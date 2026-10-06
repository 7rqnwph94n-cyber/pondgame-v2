"""Strict road-connected spatial transport (Rich 2026-10-06: "no, all buildings must connect").

Acceptance from the Codex 1637Z request: authoritative roads and placement, a first-road supply anchor,
finite carriers moving every construction, recipe and household good over road distance, conservation,
disconnection stalls without loss, and an unchanged non-spatial game.
"""
import json
import math
import unittest
from pathlib import Path

from economy.bridge import Session, facility_blockers, handle
from economy.engine import Simulation, load_definitions
from economy.engine.spatial import Terrain, rects_overlap, segment_hits_rect

ROOT = Path(__file__).resolve().parents[1]
BASE = ['economy/data/experiments/candidate_playable_slice_v1.json',
        'economy/data/experiments/empty_settlement_start_v1.json']
SPATIAL = BASE + ['economy/data/experiments/spatial_roads_v1.json']
TRANSPORTED = ("carbonate", "biomass", "prepared_silica", "raw_silicate")

# A dry stretch of the settlement terrace west of the channel.
MAIN_ROAD = [[-45, 0], [-25, 0]]


def make_sim(work=None, **rules):
    defs = load_definitions(overlays=[ROOT / o for o in SPATIAL])
    defs["spatial"].update(rules)
    if work is not None:
        for building in defs["buildings"].values():
            if "work" in building:
                building["work"] = work
    sim = Simulation(defs, {"id": "test", "commands": []})
    sim.step()
    return sim


def issue(sim, cmd):
    return sim.issue(cmd, source="test")


def run(sim, seconds):
    for _ in range(seconds):
        sim.step()


def custody(sim, goods=TRANSPORTED):
    totals = sim.custody()
    return {g: totals.get(g, 0) for g in goods}


class TerrainParityTests(unittest.TestCase):
    def test_python_terrain_matches_godot_basin(self):
        rows = json.loads((ROOT / "tests/fixtures/terrain_parity.json").read_text())["rows"]
        layout = json.loads((ROOT / "client/presentation/map_layout.json").read_text())
        terrain = Terrain(layout["channel"])
        self.assertGreater(len(rows), 1000)
        for x, z, height, channel in rows:
            self.assertAlmostEqual(terrain.height(x, z), height, delta=1e-3)
            self.assertAlmostEqual(terrain.channel_distance(x, z), channel, delta=1e-3)

    def test_footprint_geometry(self):
        self.assertTrue(rects_overlap((0, 0), 0, (7, 7), (6, 0), 0, (7, 7)))
        self.assertFalse(rects_overlap((0, 0), 0, (7, 7), (8, 0), 0, (7, 7)))
        self.assertTrue(rects_overlap((0, 0), math.pi / 4, (7, 7), (7.5, 0), 0, (7, 7)))   # rotated corner reaches
        self.assertTrue(segment_hits_rect((-10, 0), (10, 0), (0, 0), 0.3, (4, 4)))
        self.assertFalse(segment_hits_rect((-10, 5), (10, 5), (0, 0), 0, (4, 4)))


class RoadAndPlacementTests(unittest.TestCase):
    def test_empty_start_has_no_anchor_and_buildings_need_a_road(self):
        sim = make_sim()
        self.assertIsNone(sim.spatial.anchor)
        self.assertEqual(issue(sim, {"do": "construct", "building": "shelter"}).reasons, ["spatial:position_required"])
        r = issue(sim, {"do": "construct", "building": "shelter", "position": [-40, -5]})
        self.assertEqual(r.reasons, ["spatial:no_road_network"])
        self.assertFalse(sim.sites)

    def test_removing_last_road_disconnects_buildings_even_at_anchor(self):
        sim = make_sim()
        self.assertTrue(issue(sim, {"do": "build_road", "id": "r", "points": MAIN_ROAD}).ok)
        self.assertTrue(issue(sim, {"do": "construct", "id": "h", "building": "shelter", "position": [-45, -5]}).ok)
        self.assertTrue(sim.spatial.connected("h"))
        self.assertTrue(issue(sim, {"do": "remove_road", "target": "r"}).ok)
        self.assertFalse(sim.spatial.connected("h"))
        self.assertIsNone(sim.spatial._route_to((-45, -0.5)))
        result = issue(sim, {"do": "construct", "id": "other", "building": "shelter", "position": [-45, 5], "yaw": math.pi})
        self.assertEqual(result.reasons, ["spatial:not_connected"])

    def test_collinear_road_extension_has_a_shared_junction(self):
        sim = make_sim()
        self.assertTrue(issue(sim, {"do": "build_road", "points": MAIN_ROAD}).ok)
        self.assertTrue(issue(sim, {"do": "build_road", "points": [[-35, 0], [-15, 0]]}).ok)
        self.assertIn((-15.0, 0.0), sim.spatial.dist)
        route = sim.spatial._route_to((-16, -1))
        self.assertIsNotNone(route)
        self.assertAlmostEqual(route[1], 29.0)

    def test_nonfinite_building_coordinates_reject_without_creation(self):
        for field, value in (("position", [math.nan, -5]), ("position", [math.inf, -5]), ("yaw", math.inf)):
            with self.subTest(field=field, value=value):
                sim = make_sim()
                issue(sim, {"do": "build_road", "points": MAIN_ROAD})
                cmd = {"do": "construct", "id": "h", "building": "shelter", "position": [-40, -5]}
                cmd[field] = value
                self.assertEqual(issue(sim, cmd).reasons, ["spatial:malformed_position"])
                self.assertFalse(sim.sites)

    def test_first_road_sets_the_anchor_and_later_roads_must_join(self):
        sim = make_sim()
        self.assertTrue(issue(sim, {"do": "build_road", "id": "r1", "points": MAIN_ROAD}).ok)
        self.assertEqual(sim.spatial.anchor, (-45.0, 0.0))
        far = issue(sim, {"do": "build_road", "points": [[-60, 30], [-50, 30]]})
        self.assertEqual(far.reasons, ["spatial:road_not_joined"])
        joined = issue(sim, {"do": "build_road", "id": "r2", "points": [[-35, 1.5], [-35, 15]]})
        self.assertTrue(joined.ok, joined.reasons)
        self.assertEqual(sim.spatial.roads["r2"][0], (-35.0, 0.0))          # endpoint projected onto r1
        self.assertIn((-35.0, 0.0), sim.spatial.nodes.values())             # T-junction node

    def test_authoritative_road_rejections(self):
        sim = make_sim()
        self.assertEqual(issue(sim, {"do": "build_road", "points": [[-30, -10], [-10, -10]]}).reasons, ["spatial:water"])
        self.assertEqual(issue(sim, {"do": "build_road", "points": [[120, 0], [135, 0]]}).reasons, ["spatial:outside_map"])
        self.assertEqual(issue(sim, {"do": "build_road", "points": [[0, -40], [30, -40]]}).reasons, ["spatial:too_steep"])
        self.assertEqual(issue(sim, {"do": "build_road", "points": [[0, 0], [0.5, 0]]}).reasons, ["spatial:segment_too_short"])
        self.assertEqual(issue(sim, {"do": "build_road", "points": [[0, 0]]}).reasons, ["spatial:road_points_2_to_32"])
        self.assertIsNone(sim.spatial.anchor)
        self.assertTrue(issue(sim, {"do": "build_road", "points": MAIN_ROAD}).ok)
        self.assertTrue(issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]}).ok)
        through = issue(sim, {"do": "build_road", "points": [[-40.5, 0], [-40.5, -12]]})
        self.assertEqual(through.reasons, ["spatial:overlaps_building:h"])

    def test_crossing_roads_form_a_junction(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        self.assertTrue(issue(sim, {"do": "build_road", "points": [[-25, 0], [-25, 20], [-40, 20]]}).ok)
        # Crosses the U at x=-32 without sharing an endpoint, starting from the main road.
        self.assertTrue(issue(sim, {"do": "build_road", "points": [[-32, 0], [-32, 25]]}).ok)
        self.assertIn((-32.0, 20.0), {(round(x, 3), round(z, 3)) for x, z in sim.spatial.nodes.values()})
        # A home by the far end of the U is reached through the crossing, not round the long way.
        self.assertTrue(issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-38, 15],
                                    "yaw": 0.0}).ok)
        route = sim.spatial.placements["h"].route_length
        self.assertLess(route, 13 + 20 + 6 + 2)    # anchor->(-32,0)->(-32,20)->(-38,20)->entrance

    def test_dry_run_previews_without_creating(self):
        sim = make_sim()
        r = issue(sim, {"do": "build_road", "points": MAIN_ROAD, "dry_run": True})
        self.assertTrue(r.ok)
        self.assertEqual(r.info, "valid road [[-45.0,0.0],[-25.0,0.0]]")
        self.assertIsNone(sim.spatial.anchor)
        self.assertEqual(sim.spatial._road_counter, 0)
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        r = issue(sim, {"do": "build_road", "points": [[-35, 1.5], [-35, 15]], "dry_run": True})
        self.assertEqual(r.info, "valid road [[-35.0,0.0],[-35.0,15.0]]")       # snapped endpoint
        self.assertTrue(issue(sim, {"do": "construct", "building": "shelter", "position": [-40, -5], "dry_run": True}).ok)
        self.assertFalse(sim.sites)
        self.assertEqual(sim._id_counters, {})
        self.assertEqual(sim.spatial._road_counter, 1)
        self.assertEqual(len(sim.spatial.roads), 1)

    def test_building_rejections(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        cases = {
            "spatial:not_connected": {"position": [-55, 25]},
            "spatial:water": {"position": [-15, -10]},
            "spatial:overlaps_road": {"position": [-40, 1]},
        }
        for reason, extra in cases.items():
            r = issue(sim, {"do": "construct", "building": "shelter", **extra})
            self.assertEqual(r.reasons, [reason], extra)
        self.assertTrue(issue(sim, {"do": "construct", "building": "shelter", "id": "a", "position": [-40, -5]}).ok)
        r = issue(sim, {"do": "construct", "building": "shelter", "position": [-36, -5]})
        self.assertEqual(r.reasons, ["spatial:overlaps_building:a"])
        placement = sim.spatial.placements["a"]
        self.assertEqual((placement.position, placement.yaw, placement.footprint), ((-40.0, -5.0), 0.0, (7.0, 7.0)))
        self.assertEqual(placement.entrance, (-40.0, -0.5))

    def test_positions_survive_commissioning(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5], "yaw": 0.25})
        run(sim, 600)
        self.assertIn("h", sim.residences)
        self.assertEqual(sim.spatial.kind("h"), "residence")
        self.assertEqual(sim.spatial.placements["h"].yaw, 0.25)


class TransportTests(unittest.TestCase):
    def test_materials_travel_by_road_and_distance_costs_time(self):
        sim = make_sim()
        issue(sim, {"do": "build_road", "points": [[-45, 0], [-45, 40]]})
        issue(sim, {"do": "construct", "building": "culture_bed", "id": "near", "position": [-40.5, 5], "yaw": -math.pi / 2})
        issue(sim, {"do": "construct", "building": "culture_bed", "id": "far", "position": [-40.5, 35], "yaw": -math.pi / 2})
        near, far = sim.spatial.placements["near"], sim.spatial.placements["far"]
        self.assertLess(near.route_length, far.route_length)
        run(sim, 2)
        self.assertFalse(sim.sites["near"].delivered)          # nothing teleported to the site
        self.assertTrue(sim.spatial.inbound("near"))
        run(sim, 60)
        speed = sim.spatial.rules["carrier_speed_mps"]
        n, f = sim.sites["near"].materials_complete_at, sim.sites["far"].materials_complete_at
        self.assertIsNotNone(n)
        self.assertIsNotNone(f)
        self.assertGreaterEqual(f - n, int((far.route_length - near.route_length) / speed) - 2)

    def test_carrier_capacity_limits_each_trip(self):
        sim = make_sim(carrier_capacity=1, carriers=1)
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        issue(sim, {"do": "construct", "building": "general_store", "id": "store", "position": [-40, -5]})   # 3 + 1 units
        trips, loads = 0, []
        last = None
        for _ in range(240):
            sim.step()
            c = sim.spatial.carriers[0]
            if c.job == "deliver" and last != "deliver":
                trips += 1
                loads.append(sum(c.cargo.values()))
            last = c.job
        self.assertEqual(trips, 4)
        self.assertTrue(all(load == 1 for load in loads))
        self.assertIsNotNone(sim.sites["store"].materials_complete_at)

    def test_outputs_stay_local_until_collected(self):
        sim = make_sim(work=1)
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        for i, x in enumerate((-40, -30)):
            issue(sim, {"do": "construct", "building": "shelter", "id": f"h{i}", "position": [x, -5]})
        issue(sim, {"do": "construct", "building": "shelter", "id": "h2", "position": [-40, 5], "yaw": math.pi})
        issue(sim, {"do": "construct", "building": "photosynthetic_field", "id": "field", "position": [-30, 5], "yaw": math.pi})
        anchor = sim.store("core")
        produced_before = sim.diag.produced.get("biomass", 0)
        arrivals = 0
        for _ in range(900):
            before = anchor.get("biomass")
            carrying = sum(c.cargo.get("biomass", 0) for c in sim.spatial.carriers if c.state == "to_anchor")
            sim.step()
            gained = anchor.get("biomass") - before
            if gained > 0:
                arrivals += 1
                # every unit that appears at the anchor was on a returning carrier
                self.assertLessEqual(gained, carrying)
        self.assertGreater(sim.diag.produced.get("biomass", 0), produced_before)
        self.assertGreater(arrivals, 0)

    def test_homes_are_provisioned_by_carriers(self):
        sim = make_sim(work=1)
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]})
        run(sim, 120)
        self.assertEqual(sim.residences["h"].population, 8)
        self.assertGreater(sim.spatial.depots["h"].get("staple") + sim.residences["h"].buffers.get("staple", 0), 0)
        self.assertFalse(sim.residences["h"].short_this_step)

    def test_transport_conserves_cargo_including_cancellation(self):
        sim = make_sim(work=10**6)   # sites never finish: only transport moves goods
        issue(sim, {"do": "build_road", "points": MAIN_ROAD})
        issue(sim, {"do": "construct", "building": "general_store", "id": "a", "position": [-40, -5]})
        issue(sim, {"do": "construct", "building": "waste_collector", "id": "b", "position": [-30, -5]})
        start = custody(sim)
        for _ in range(120):
            sim.step()
            self.assertEqual(custody(sim), start)
        delivered = dict(sim.sites["a"].delivered)
        self.assertTrue(delivered)
        issue(sim, {"do": "cancel", "target": "a"})
        self.assertEqual(sim.spatial.kind("a"), "pile")
        lost = {g: q - int(q * 0.9 + 1e-9) for g, q in delivered.items()}
        expected = {g: start[g] - lost.get(g, 0) for g in start}
        self.assertEqual(custody(sim), expected)
        for _ in range(300):
            sim.step()
            self.assertEqual(custody(sim), expected)
        self.assertNotIn("a", sim.spatial.placements)          # salvage collected, pile cleared

    def test_disconnection_stalls_and_preserves_goods(self):
        sim = make_sim(work=1)
        issue(sim, {"do": "build_road", "id": "trunk", "points": MAIN_ROAD})
        issue(sim, {"do": "build_road", "id": "spur", "points": [[-30, 0], [-30, 20]]})
        issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]})
        issue(sim, {"do": "construct", "building": "culture_bed", "id": "bed", "position": [-25.5, 15], "yaw": -math.pi / 2})
        run(sim, 300)
        self.assertIn("bed", sim.facilities)
        self.assertTrue(issue(sim, {"do": "remove_road", "target": "spur"}).ok)
        self.assertFalse(sim.spatial.connected("bed"))
        run(sim, 60)   # carriers already on the spur finish their leg; no new trips start
        self.assertFalse(sim.spatial.inbound("bed"))
        self.assertFalse(any(c.target == "bed" for c in sim.spatial.carriers))
        held = sim.spatial.depots["bed"].nonzero()
        total = sim.custody()
        run(sim, 120)
        self.assertEqual(sim.facilities["bed"].staffing, 0.0)
        self.assertEqual(sim.spatial.depots["bed"].nonzero(), held)          # stalled, nothing lost or taken
        self.assertEqual(facility_blockers(sim, sim.facilities["bed"])[0]["code"], "road_disconnected")
        self.assertTrue(issue(sim, {"do": "build_road", "points": [[-30, 0], [-30, 20]]}).ok)
        self.assertTrue(sim.spatial.connected("bed"))

    def test_disconnected_home_neither_works_nor_takes_founders(self):
        sim = make_sim(work=1)
        issue(sim, {"do": "build_road", "id": "trunk", "points": MAIN_ROAD})
        issue(sim, {"do": "build_road", "id": "spur", "points": [[-30, 0], [-30, 20]]})
        issue(sim, {"do": "construct", "building": "shelter", "id": "h", "position": [-25.5, 15], "yaw": -math.pi / 2})
        issue(sim, {"do": "remove_road", "target": "spur"})
        run(sim, 120)
        self.assertNotIn("h", sim.residences)                 # disconnected site gets no labour or goods
        self.assertEqual(sim.spatial.depots["h"].nonzero(), {})


class BridgeSpatialTests(unittest.TestCase):
    def test_hello_view_and_disabled_autoplay(self):
        s = Session([str(ROOT / o) for o in SPATIAL])
        hello = handle(s, {"id": 1, "op": "hello"})
        self.assertTrue(hello["spatial"]["enabled"])
        self.assertFalse(hello["autoplay_available"])
        self.assertEqual(hello["spatial"]["rules"]["carriers"], 6)
        auto = handle(s, {"id": 2, "op": "autoplay", "enabled": True})
        self.assertEqual((auto["ok"], auto["reasons"]), (False, ["spatial:autoplay_unavailable"]))
        self.assertTrue(s.command({"do": "build_road", "id": "r", "points": MAIN_ROAD})["ok"])
        self.assertTrue(s.command({"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]})["ok"])
        view = s.advance(3)
        spatial = view["spatial"]
        self.assertEqual(spatial["anchor"], {"position": [-45.0, 0.0]})
        self.assertEqual(spatial["roads"]["r"]["length"], 20.0)
        p = spatial["placements"]["h"]
        self.assertEqual(set(p), {"kind", "position", "yaw", "footprint", "entrance", "attach", "connected",
                                  "route_length", "local", "inbound"})
        self.assertTrue(p["connected"])
        moving = [c for c in spatial["carriers"].values() if c["state"] != "idle"]
        self.assertTrue(moving)
        self.assertEqual(set(moving[0]), {"state", "job", "source", "target", "cargo", "path", "length", "distance",
                                          "progress", "position"})
        codes = [b["code"] for b in view["sites"]["h"]["blockers"]]
        self.assertIn("awaiting_transport", codes)
        json.dumps(view)

    def test_pause_advances_nothing(self):
        s = Session([str(ROOT / o) for o in SPATIAL])
        s.command({"do": "build_road", "points": MAIN_ROAD})
        s.command({"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]})
        before = s.advance(2)["spatial"]
        self.assertEqual(s.advance(0)["spatial"], before)

    def test_deterministic(self):
        def play():
            s = Session([str(ROOT / o) for o in SPATIAL])
            s.command({"do": "build_road", "points": MAIN_ROAD})
            s.command({"do": "construct", "building": "shelter", "id": "h", "position": [-40, -5]})
            s.command({"do": "construct", "building": "photosynthetic_field", "id": "f", "position": [-30, -5]})
            return [s.advance(60)["spatial"] for _ in range(5)]
        self.assertEqual(play(), play())

    def test_non_spatial_game_is_unchanged(self):
        s = Session([str(ROOT / o) for o in BASE])
        self.assertNotIn("spatial", handle(s, {"id": 1, "op": "hello"}))
        self.assertNotIn("spatial", s.view())
        self.assertIsNone(s.sim.spatial)
        self.assertTrue(s.command({"do": "construct", "building": "shelter", "id": "h"})["ok"])
        self.assertEqual(s.command({"do": "build_road", "points": MAIN_ROAD})["reasons"], ["spatial:not_enabled"])


if __name__ == "__main__":
    unittest.main()
