"""Optional spatial transport domain (Rich 2026-10-06: "no, all buildings must connect").

Enabled only by definitions with ``spatial.enabled`` (overlay ``spatial_roads_v1``); every other
scenario is untouched. The model, in metres on the client's x/z plane:

* Roads are player-drawn polylines. The first road may start anywhere valid; its first point becomes
  the *anchor*, the founding supply store (the district store). Every later road must join the
  anchor's network with an endpoint within ``snap_distance``; joined endpoints are projected onto the
  network and crossings become junctions. Roads are free, instant dirt paths in this version.
* Every building has a domain-owned position, yaw and footprint, and an entrance on its local +Z face.
  It may only be placed with its entrance within ``attach_distance`` of the anchor's network.
* Every placed building has its own local depot. Sites build only from delivered goods, recipes use
  and fill their own depot, homes refill from theirs. Nothing teleports to or from the anchor.
* A finite pool of carriers runs hub-and-spoke trips over the shortest road route: deliveries out,
  collections (outputs, household waste, salvage) back, and returns empty. Distance costs time.
* A building whose entrance no longer reaches the anchor is disconnected: no jobs, services,
  migrants or new trips. A carrier already travelling finishes its current leg on the path it
  started, so cargo is never lost.

Provisional, documented numbers live in ``economy/data/experiments/spatial_roads_v1.json``.
"""
from __future__ import annotations

import heapq
import json
import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Iterable

from .inventory import Inventory, add_goods

ROOT = Path(__file__).resolve().parents[2]
EPS = 1e-9
JOIN_TOL = 1e-3          # metres: points closer than this are the same junction
KEY_DIGITS = 3

Point = tuple[float, float]


# ---------------------------------------------------------------------- terrain (parity with Godot)
def _smoothstep(edge0: float, edge1: float, x: float) -> float:
    if abs(edge0 - edge1) < 1e-12:
        return edge0
    s = min(1.0, max(0.0, (x - edge0) / (edge1 - edge0)))
    return s * s * (3.0 - 2.0 * s)


def _cubic(a: float, b: float, pre: float, post: float, t: float) -> float:
    # Godot Math::cubic_interpolate (Catmull-Rom), as used by Vector2.cubic_interpolate.
    return 0.5 * ((a * 2.0) + (-pre + b) * t + (2.0 * pre - 5.0 * a + 4.0 * b - post) * t * t
                  + (-pre + 3.0 * a - 3.0 * b + post) * t * t * t)


class Terrain:
    """Python port of client/scripts/basin_terrain.gd height_at() and channel distance.

    The client is the visual authority for the basin; this port is the rules authority and is held to
    it by a Godot-generated parity fixture (tests/fixtures/terrain_parity.json).
    """
    SIZE = 260.0

    def __init__(self, channel: Iterable[Iterable[float]]):
        points = [(float(p[0]), float(p[1])) for p in channel]
        smooth: list[Point] = []
        for i in range(len(points) - 1):
            before, start = points[max(0, i - 1)], points[i]
            finish, after = points[i + 1], points[min(len(points) - 1, i + 2)]
            for step in range(12):
                t = step / 12.0
                smooth.append((_cubic(start[0], finish[0], before[0], after[0], t),
                               _cubic(start[1], finish[1], before[1], after[1], t)))
        smooth.append(points[-1])
        self.channel = smooth

    def channel_distance(self, x: float, z: float) -> float:
        nearest = math.inf
        for a, b in zip(self.channel, self.channel[1:]):
            nearest = min(nearest, math.dist((x, z), project(a, b, (x, z))[0]))
        return nearest

    def height(self, x: float, z: float) -> float:
        d = self.channel_distance(x, z)
        h = math.sin(x * 0.17) * 0.16 + math.cos(z * 0.13) * 0.12 + math.sin((x + z) * 0.07) * 0.2
        if d < 6.2:
            h -= 2.7 * (1.0 - _smoothstep(0.0, 6.2, d))
        elif d < 17.0:
            h -= 0.45 * (1.0 - _smoothstep(6.2, 17.0, d))
        ridge = _smoothstep(13.0, 24.0, x) * (1.0 - _smoothstep(-34.0, 10.0, z))
        h += ridge * 10.5
        h += ridge * (math.sin(z * 0.22) * 0.7 + math.cos(x * 0.31) * 0.35)
        h += math.exp(-((x + 19.0) / 19.0) ** 2 - ((z + 6.0) / 14.0) ** 2) * 1.1
        h -= math.exp(-((x + 36.0) / 15.0) ** 2 - ((z - 21.0) / 13.0) ** 2) * 1.2
        return h


# ---------------------------------------------------------------------- geometry
def project(a: Point, b: Point, p: Point) -> tuple[Point, float]:
    """Closest point on segment ab to p, and its parameter t in [0, 1]."""
    ax, az = b[0] - a[0], b[1] - a[1]
    length2 = ax * ax + az * az
    t = 0.0 if length2 <= EPS else min(1.0, max(0.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * az) / length2))
    return (a[0] + ax * t, a[1] + az * t), t


def rotate(lx: float, lz: float, yaw: float) -> Point:
    """Godot Vector3(lx, 0, lz).rotated(Vector3.UP, yaw), on the x/z plane."""
    c, s = math.cos(yaw), math.sin(yaw)
    return (lx * c + lz * s, -lx * s + lz * c)


def rect_axes(yaw: float) -> tuple[Point, Point]:
    return rotate(1.0, 0.0, yaw), rotate(0.0, 1.0, yaw)


def rects_overlap(a: Point, yaw_a: float, size_a: Point, b: Point, yaw_b: float, size_b: Point,
                  clearance: float = 0.3) -> bool:
    """Separating-axis test for two rotated footprints (same rule as the client's world_view.gd)."""
    ax, az = rect_axes(yaw_a)
    bx, bz = rect_axes(yaw_b)
    d = (b[0] - a[0], b[1] - a[1])
    dot = lambda u, v: u[0] * v[0] + u[1] * v[1]
    for axis in (ax, az, bx, bz):
        extent = (size_a[0] / 2 * abs(dot(axis, ax)) + size_a[1] / 2 * abs(dot(axis, az))
                  + size_b[0] / 2 * abs(dot(axis, bx)) + size_b[1] / 2 * abs(dot(axis, bz)) + clearance)
        if abs(dot(d, axis)) >= extent:
            return False
    return True


def segment_hits_rect(p: Point, q: Point, centre: Point, yaw: float, size: Point) -> bool:
    """Does segment pq enter the rotated rectangle? (Liang-Barsky in the rectangle's frame.)"""
    ax, az = rect_axes(yaw)
    def local(point: Point) -> Point:
        dx, dz = point[0] - centre[0], point[1] - centre[1]
        return (dx * ax[0] + dz * ax[1], dx * az[0] + dz * az[1])
    (x0, z0), (x1, z1) = local(p), local(q)
    hw, hd = size[0] / 2, size[1] / 2
    t0, t1 = 0.0, 1.0
    for edge_p, edge_q in ((-(x1 - x0), x0 + hw), (x1 - x0, hw - x0), (-(z1 - z0), z0 + hd), (z1 - z0, hd - z0)):
        if abs(edge_p) < EPS:
            if edge_q < 0:
                return False
            continue
        r = edge_q / edge_p
        if edge_p < 0:
            t0 = max(t0, r)
        else:
            t1 = min(t1, r)
        if t0 > t1:
            return False
    return True


def segment_intersection(a: Point, b: Point, c: Point, d: Point) -> tuple[float, float] | None:
    """Parameters (t on ab, u on cd) where two non-parallel segments cross, if they do."""
    r = (b[0] - a[0], b[1] - a[1])
    s = (d[0] - c[0], d[1] - c[1])
    denom = r[0] * s[1] - r[1] * s[0]
    if abs(denom) < EPS:
        return None
    qp = (c[0] - a[0], c[1] - a[1])
    t = (qp[0] * s[1] - qp[1] * s[0]) / denom
    u = (qp[0] * r[1] - qp[1] * r[0]) / denom
    tol_t = JOIN_TOL / max(math.hypot(*r), EPS)
    tol_u = JOIN_TOL / max(math.hypot(*s), EPS)
    if -tol_t <= t <= 1 + tol_t and -tol_u <= u <= 1 + tol_u:
        return min(1.0, max(0.0, t)), min(1.0, max(0.0, u))
    return None


def polyline_length(points: list[Point]) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def point_along(points: list[Point], distance: float) -> Point:
    if not points:
        return (0.0, 0.0)
    for a, b in zip(points, points[1:]):
        step = math.dist(a, b)
        if distance <= step + EPS:
            t = 0.0 if step <= EPS else max(0.0, distance) / step
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        distance -= step
    return points[-1]


def _key(p: Point) -> tuple[float, float]:
    return (round(p[0], KEY_DIGITS), round(p[1], KEY_DIGITS))


def _pt(p: Iterable[float]) -> Point:
    x, z = (float(v) for v in p)
    if not (math.isfinite(x) and math.isfinite(z)):
        raise ValueError("non-finite coordinate")
    return (x, z)


def _r(p: Point) -> list[float]:
    return [round(p[0], 3), round(p[1], 3)]


# ---------------------------------------------------------------------- state
@dataclass
class Placement:
    id: str
    position: Point
    yaw: float
    footprint: Point
    entrance: Point
    order: int
    attach: Point | None = None
    path: list[Point] = field(default_factory=list)     # anchor -> entrance along roads
    route_length: float | None = None

    @property
    def connected(self) -> bool:
        return self.route_length is not None


@dataclass
class Carrier:
    id: str
    state: str = "idle"          # idle | to_target | to_anchor
    job: str | None = None       # deliver | collect | return
    target: str = "anchor"
    cargo: dict[str, int] = field(default_factory=dict)
    path: list[Point] = field(default_factory=list)
    length: float = 0.0
    distance: float = 0.0


class SpatialState:
    def __init__(self, sim: Any):
        self.sim = sim
        self.rules: dict[str, Any] = dict(sim.defs["spatial"])
        channel = self.rules.get("channel")
        if channel is None:   # one source of truth with the client's visible basin
            channel = json.loads((ROOT / self.rules["channel_source"]).read_text(encoding="utf-8"))["channel"]
        self.terrain = Terrain(channel)
        self.anchor: Point | None = None
        self.roads: dict[str, list[Point]] = {}
        self.placements: dict[str, Placement] = {}
        self.depots: dict[str, Inventory] = {}
        self.carriers = [Carrier(f"carrier_{i + 1}") for i in range(int(self.rules["carriers"]))]
        self._road_counter = 0
        self._rebuild()

    # ------------------------------------------------------------ network
    def _rebuild(self) -> None:
        segments: list[tuple[Point, Point]] = []
        for rid in sorted(self.roads):
            pts = self.roads[rid]
            segments += [(a, b) for a, b in zip(pts, pts[1:]) if math.dist(a, b) > EPS]
        cuts: list[set[float]] = [{0.0, 1.0} for _ in segments]
        for i in range(len(segments)):
            for j in range(i + 1, len(segments)):
                hit = segment_intersection(*segments[i], *segments[j])
                if hit:
                    cuts[i].add(hit[0])
                    cuts[j].add(hit[1])
            if self.anchor is not None:
                q, t = project(*segments[i], self.anchor)
                if math.dist(q, self.anchor) < JOIN_TOL:
                    cuts[i].add(t)
        self.nodes: dict[tuple[float, float], Point] = {}
        self.edges: dict[tuple[float, float], list[tuple[tuple[float, float], float]]] = {}
        self.pieces: list[tuple[Point, Point]] = []
        for (a, b), ts in zip(segments, cuts):
            pts = [(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t) for t in sorted(ts)]
            for p, q in zip(pts, pts[1:]):
                kp, kq = _key(p), _key(q)
                if kp == kq:
                    continue
                self.nodes.setdefault(kp, p)
                self.nodes.setdefault(kq, q)
                length = math.dist(p, q)
                self.edges.setdefault(kp, []).append((kq, length))
                self.edges.setdefault(kq, []).append((kp, length))
                self.pieces.append((self.nodes[kp], self.nodes[kq]))
        # Shortest distance from the anchor to every reachable junction.
        self.dist: dict[tuple[float, float], float] = {}
        self.prev: dict[tuple[float, float], tuple[float, float] | None] = {}
        if self.anchor is not None:
            start = _key(self.anchor)
            self.nodes.setdefault(start, self.anchor)
            heap = [(0.0, start)]
            self.dist[start], self.prev[start] = 0.0, None
            while heap:
                d, k = heapq.heappop(heap)
                if d > self.dist[k] + EPS:
                    continue
                for nk, length in sorted(self.edges.get(k, [])):
                    nd = d + length
                    if nd + EPS < self.dist.get(nk, math.inf):
                        self.dist[nk], self.prev[nk] = nd, k
                        heapq.heappush(heap, (nd, nk))
        for placement in self.placements.values():
            self._attach(placement)

    def _node_path(self, key: tuple[float, float]) -> list[Point]:
        out = []
        while key is not None:
            out.append(self.nodes[key])
            key = self.prev[key]
        return out[::-1]

    def _connected_pieces(self) -> list[tuple[Point, Point]]:
        return [(a, b) for a, b in self.pieces if _key(a) in self.dist and _key(b) in self.dist]

    def _nearest_network_point(self, p: Point, connected_only: bool = True) -> tuple[Point, float] | None:
        best = None
        pieces = self._connected_pieces() if connected_only else self.pieces
        for a, b in pieces:
            q, _ = project(a, b, p)
            d = math.dist(p, q)
            if best is None or d < best[1] - EPS:
                best = (q, d)
        if self.anchor is not None and (best is None or math.dist(p, self.anchor) < best[1] - EPS):
            best = (self.anchor, math.dist(p, self.anchor))
        return best

    def _route_to(self, point: Point) -> tuple[list[Point], float, Point] | None:
        """Shortest road route from the anchor to the nearest attachable network point."""
        limit = float(self.rules["attach_distance"])
        best = None
        candidates: list[tuple[Point, Point]] = self._connected_pieces()
        for a, b in candidates:
            q, _ = project(a, b, point)
            gap = math.dist(q, point)
            if gap > limit + EPS:
                continue
            for end in (a, b):
                total = self.dist[_key(end)] + math.dist(end, q)
                if best is None or (gap, total) < (best[0], best[1]):
                    best = (gap, total, q, end)
        if self.anchor is not None and math.dist(point, self.anchor) <= limit + EPS and not candidates:
            return [self.anchor], 0.0, self.anchor
        if best is None:
            return None
        gap, total, q, end = best
        path = self._node_path(_key(end))
        if math.dist(path[-1], q) > EPS:
            path.append(q)
        return path, total, q

    def _attach(self, placement: Placement) -> None:
        route = self._route_to(placement.entrance)
        if route is None:
            placement.attach, placement.path, placement.route_length = None, [], None
            return
        path, length, q = route
        if math.dist(path[-1], placement.entrance) > EPS:
            path = path + [placement.entrance]
        placement.attach = q
        placement.path = path
        placement.route_length = polyline_length(path)

    def connected(self, entity_id: str) -> bool:
        placement = self.placements.get(entity_id)
        return placement is not None and placement.connected

    # ------------------------------------------------------------ validation
    def _ground_ok(self, points: list[Point], water_margin: float) -> str | None:
        half = Terrain.SIZE / 2 - 1
        for x, z in points:
            if abs(x) > half or abs(z) > half:
                return "spatial:outside_map"
            if self.terrain.channel_distance(x, z) < water_margin:
                return "spatial:water"
        return None

    def _blocking_rects(self) -> list[Placement]:
        return [p for pid, p in sorted(self.placements.items()) if self.kind(pid) != "pile"]

    def validate_road(self, raw_points: Any) -> tuple[list[Point] | None, list[str]]:
        rules = self.rules
        if not isinstance(raw_points, list) or not 2 <= len(raw_points) <= int(rules["max_road_points"]):
            return None, [f"spatial:road_points_2_to_{rules['max_road_points']}"]
        try:
            points = [_pt(p) for p in raw_points]
        except (TypeError, ValueError):
            return None, ["spatial:malformed_points"]
        if self.anchor is not None:
            snap = float(rules["snap_distance"])
            joined = False
            for index in (0, len(points) - 1):
                near = self._nearest_network_point(points[index], connected_only=True)
                if near and near[1] <= snap + EPS:
                    points[index] = near[0]
                    joined = True
            if not joined:
                return None, ["spatial:road_not_joined"]
        for a, b in zip(points, points[1:]):
            if math.dist(a, b) < float(rules["min_segment_m"]) - EPS:
                return None, ["spatial:segment_too_short"]
        for a, b in zip(points, points[1:]):
            length = math.dist(a, b)
            steps = max(1, math.ceil(length / 1.0))
            samples = [(a[0] + (b[0] - a[0]) * i / steps, a[1] + (b[1] - a[1]) * i / steps) for i in range(steps + 1)]
            ground = self._ground_ok(samples, float(rules["road_water_margin"]))
            if ground:
                return None, [ground]
            heights = [self.terrain.height(x, z) for x, z in samples]
            spacing = length / steps
            if any(abs(h1 - h0) / spacing > float(rules["road_max_grade"]) + EPS for h0, h1 in zip(heights, heights[1:])):
                return None, ["spatial:too_steep"]
            for p in self._blocking_rects():
                if segment_hits_rect(a, b, p.position, p.yaw, p.footprint):
                    return None, [f"spatial:overlaps_building:{p.id}"]
        return points, []

    def footprint_for(self, building_id: str, raw: Any) -> Point:
        default = self.rules["footprints"].get(building_id, self.rules["default_footprint"])
        w, d = float(default[0]), float(default[1])
        if raw is not None:
            rw, rd = _pt(raw)
            w, d = max(w, min(rw, 40.0)), max(d, min(rd, 40.0))
        return (w, d)

    def validate_building(self, position: Point, yaw: float, footprint: Point) -> tuple[Point | None, list[str]]:
        w, d = footprint
        samples = [(position[0], position[1])]
        local = [(x * w / 2, z * d / 2) for x in (-1.0, -0.5, 0.0, 0.5, 1.0) for z in (-1.0, -0.5, 0.0, 0.5, 1.0)]
        samples += [(position[0] + rotate(lx, lz, yaw)[0], position[1] + rotate(lx, lz, yaw)[1]) for lx, lz in local]
        ground = self._ground_ok(samples, float(self.rules["building_water_margin"]))
        if ground:
            return None, [ground]
        heights = [self.terrain.height(x, z) for x, z in samples]
        if max(heights) - min(heights) > float(self.rules["building_max_rise"]) + EPS:
            return None, ["spatial:too_steep"]
        for p in self._blocking_rects():
            if rects_overlap(position, yaw, footprint, p.position, p.yaw, p.footprint):
                return None, [f"spatial:overlaps_building:{p.id}"]
        for a, b in self.pieces:
            if segment_hits_rect(a, b, position, yaw, footprint):
                return None, ["spatial:overlaps_road"]
        offset = rotate(0.0, d / 2 + float(self.rules["entrance_offset"]), yaw)
        entrance = (position[0] + offset[0], position[1] + offset[1])
        if self.anchor is None:
            return None, ["spatial:no_road_network"]
        if self._route_to(entrance) is None:
            return None, ["spatial:not_connected"]
        return entrance, []

    # ------------------------------------------------------------ commands
    def build_road(self, cmd: dict[str, Any]) -> tuple[bool, str, list[str]]:
        road_id = cmd.get("id")
        if road_id is None:
            while True:
                self._road_counter += 1
                road_id = f"road_{self._road_counter}"
                if road_id not in self.roads:
                    break
        road_id = str(road_id)
        if road_id in self.roads:
            return False, "", [f"duplicate_id:{road_id}"]
        points, reasons = self.validate_road(cmd.get("points"))
        if points is None:
            return False, "", reasons
        if cmd.get("dry_run"):   # v4: authoritative preview; info carries the snapped points
            return True, "valid road " + json.dumps([_r(p) for p in points], separators=(",", ":")), []
        if self.anchor is None:
            self.anchor = points[0]
        self.roads[road_id] = points
        self._rebuild()
        return True, f"{road_id} {polyline_length(points):.1f} m", []

    def remove_road(self, road_id: Any) -> tuple[bool, str, list[str]]:
        if road_id not in self.roads:
            return False, "", [f"spatial:unknown_road:{road_id}"]
        del self.roads[road_id]
        self._rebuild()
        return True, f"{road_id} removed", []

    def place(self, entity_id: str, position: Point, yaw: float, footprint: Point, entrance: Point) -> None:
        placement = Placement(entity_id, position, yaw, footprint, entrance, order=self.sim.next_order())
        self._attach(placement)
        self.placements[entity_id] = placement
        self.depots[entity_id] = Inventory(self.sim.defs["resources"])

    # ------------------------------------------------------------ demand
    def kind(self, entity_id: str) -> str:
        sim = self.sim
        if entity_id in sim.facilities:
            return "facility"
        if entity_id in sim.residences:
            return "residence"
        site = sim.sites.get(entity_id)
        if site is not None and site.active:
            return "site"
        return "pile"

    def targets(self, entity_id: str) -> dict[str, int]:
        """Goods this entity wants held in its local depot."""
        sim = self.sim
        if entity_id in sim.facilities:
            f = sim.facilities[entity_id]
            if f.paused or not f.recipe_id:
                return {}
            inputs = sim.defs["recipes"][f.recipe_id].get("inputs", {})
            cycles = int(self.rules["input_cycles_stocked"])
            return {g: int(q) * cycles for g, q in inputs.items()}
        if entity_id in sim.residences:
            r = sim.residences[entity_id]
            want: dict[str, int] = {}
            if r.population > EPS:
                minutes = float(self.rules["residence_stock_minutes"])
                for good, rate in r.definition(sim.defs)["per_minute"].items():
                    want[good] = max(1, math.ceil(rate * minutes - EPS))
            if r.evolution_target and not r.evolution_reserved:
                goods = sim.defs["residences"][r.evolution_target]["evolution"].get("goods", {})
                for good, q in goods.items():
                    want[good] = want.get(good, 0) + int(q)
            return want
        site = sim.sites.get(entity_id)
        if site is not None and site.active and site.materials_complete_at is None:
            return site.missing()
        return {}

    def collectable(self, entity_id: str) -> dict[str, int]:
        sim = self.sim
        depot = self.depots[entity_id]
        kind = self.kind(entity_id)
        if kind == "site":
            return {}
        keep: set[str] = set(self.targets(entity_id))
        if kind == "residence":
            r = sim.residences[entity_id]
            keep |= set(r.definition(sim.defs)["per_minute"])
            if r.evolution_target:
                keep |= set(sim.defs["residences"][r.evolution_target]["evolution"].get("goods", {}))
        elif kind == "facility":
            f = sim.facilities[entity_id]
            if f.recipe_id:
                keep |= set(sim.defs["recipes"][f.recipe_id].get("inputs", {}))
        return {g: q for g, q in sorted(depot.counts.items()) if q and g not in keep}

    def inbound(self, entity_id: str) -> dict[str, int]:
        out: dict[str, int] = {}
        for c in self.carriers:
            if c.target == entity_id and c.job == "deliver":
                add_goods(out, c.cargo)
        return out

    def shortfall(self, entity_id: str, include_inbound: bool = True) -> dict[str, int]:
        depot = self.depots[entity_id]
        inbound = self.inbound(entity_id) if include_inbound else {}
        out = {}
        for good, want in sorted(self.targets(entity_id).items()):
            short = want - depot.get(good) - inbound.get(good, 0)
            if short > 0:
                out[good] = short
        return out

    # ------------------------------------------------------------ carriers
    def step(self, dt: float) -> None:
        speed = float(self.rules["carrier_speed_mps"])
        for c in self.carriers:
            if c.state == "idle":
                continue
            c.distance = min(c.length, c.distance + speed * dt)
            if c.distance >= c.length - EPS:
                self._arrive(c)
        self._dispatch()
        for pid in sorted(self.placements):
            if (self.kind(pid) == "pile" and not self.depots[pid].nonzero()
                    and not any(c.target == pid for c in self.carriers)):
                del self.placements[pid]
                del self.depots[pid]

    def _send(self, c: Carrier, state: str, job: str, target: str, path: list[Point]) -> None:
        c.state, c.job, c.target = state, job, target
        c.path = list(path)
        c.length = polyline_length(c.path)
        c.distance = 0.0

    def _arrive(self, c: Carrier) -> None:
        anchor_store = self.sim.store(self.sim.districts[0])
        if c.state == "to_target":
            depot = self.depots[c.target]
            if c.job == "deliver":
                depot.put(c.cargo)
                c.cargo = {}
            else:   # collect: load what is collectable now
                room = int(self.rules["carrier_capacity"])
                for good, q in self.collectable(c.target).items():
                    take = depot.take_up_to(good, min(q, room))
                    if take:
                        c.cargo[good] = c.cargo.get(good, 0) + take
                        room -= take
                    if room <= 0:
                        break
            job = "collect" if c.cargo else "return"
            self._send(c, "to_anchor", job, c.target, c.path[::-1])
        else:
            anchor_store.put(c.cargo)
            c.cargo = {}
            c.state, c.job, c.target, c.path, c.length, c.distance = "idle", None, "anchor", [], 0.0, 0.0

    def _dispatch(self) -> None:
        idle = [c for c in self.carriers if c.state == "idle"]
        if not idle or self.anchor is None:
            return
        sim = self.sim
        anchor_store = sim.store(sim.districts[0])
        capacity = int(self.rules["carrier_capacity"])

        def rank(pid: str) -> tuple:
            kind = self.kind(pid)
            if kind == "residence":
                return (0, 0, self.placements[pid].order)
            if kind == "site":
                site = sim.sites[pid]
                return (1, site.priority, site.order)
            return (2, 0, self.placements[pid].order)

        connected = sorted((pid for pid, p in self.placements.items() if p.connected), key=rank)
        for pid in connected:
            while idle:
                short = self.shortfall(pid)
                load: dict[str, int] = {}
                room = capacity
                for good, q in short.items():
                    take = min(q, anchor_store.get(good), room)
                    if take > 0:
                        load[good] = take
                        room -= take
                    if room <= 0:
                        break
                if not load:
                    break
                anchor_store.take(load)
                c = idle.pop(0)
                c.cargo = load
                self._send(c, "to_target", "deliver", pid, self.placements[pid].path)
        for pid in connected:
            if not idle:
                return
            if any(c.target == pid and c.job == "collect" for c in self.carriers):
                continue
            if sum(self.collectable(pid).values()) >= 1:
                self._send(idle.pop(0), "to_target", "collect", pid, self.placements[pid].path)

    # ------------------------------------------------------------ reporting
    def custody(self) -> dict[str, int]:
        totals: dict[str, int] = {}
        for depot in self.depots.values():
            add_goods(totals, depot.counts)
        for c in self.carriers:
            add_goods(totals, c.cargo)
        return totals

    def held(self, good: str) -> int:
        return sum(d.get(good) for d in self.depots.values()) + sum(c.cargo.get(good, 0) for c in self.carriers)

    def hello(self) -> dict[str, Any]:
        keys = ("carriers", "carrier_capacity", "carrier_speed_mps", "snap_distance", "attach_distance",
                "entrance_offset", "min_segment_m", "max_road_points", "road_water_margin", "road_max_grade",
                "building_water_margin", "building_max_rise", "default_footprint", "input_cycles_stocked",
                "residence_stock_minutes")
        rules = {k: self.rules[k] for k in keys}
        rules["map_half_extent"] = Terrain.SIZE / 2 - 1
        return {"enabled": True, "version": 1, "rules": rules, "footprints": dict(self.rules["footprints"])}

    def view(self) -> dict[str, Any]:
        placements = {}
        for pid, p in sorted(self.placements.items()):
            placements[pid] = {
                "kind": self.kind(pid), "position": _r(p.position), "yaw": round(p.yaw, 4),
                "footprint": [round(p.footprint[0], 3), round(p.footprint[1], 3)], "entrance": _r(p.entrance),
                "attach": _r(p.attach) if p.attach else None, "connected": p.connected,
                "route_length": None if p.route_length is None else round(p.route_length, 2),
                "local": self.depots[pid].nonzero(), "inbound": self.inbound(pid),
            }
        carriers = {}
        for c in self.carriers:
            moving = c.state != "idle"
            position = point_along(c.path, c.distance) if moving else self.anchor
            carriers[c.id] = {
                "state": c.state, "job": c.job,
                "source": "anchor" if c.state == "to_target" else (c.target if moving else "anchor"),
                "target": c.target if c.state == "to_target" else "anchor",
                "cargo": dict(c.cargo), "path": [_r(p) for p in c.path], "length": round(c.length, 2),
                "distance": round(c.distance, 2), "progress": round(c.distance / c.length, 4) if c.length > EPS else 0.0,
                "position": _r(position) if position else None,
            }
        return {
            "enabled": True,
            "anchor": {"position": _r(self.anchor)} if self.anchor else None,
            "roads": {rid: {"points": [_r(p) for p in pts], "length": round(polyline_length(pts), 2)}
                      for rid, pts in sorted(self.roads.items())},
            "placements": placements,
            "carriers": carriers,
        }
