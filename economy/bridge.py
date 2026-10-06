"""Local simulation bridge for the Godot client (ADR 0001, Rich 2026-10-02T18:11Z).

The Python domain is the only rules authority. The client connects over localhost TCP and exchanges
newline-delimited JSON. Every request carries an ``id``, and the reply echoes it. The protocol is
specified in ``docs/exchange/contracts/sim_bridge.json`` and tested in ``tests/test_bridge.py``.

    python3 -m economy.bridge [--port 47615] [--overlay PATH ...] [--governor PATH] [--seconds-per-request 600]

Requests (``op``):

- ``hello``: protocol version, scenario and a definitions summary for labels and layout.
- ``advance`` ``{seconds}``: step the fixed-step simulation, then return the player view and new events.
  Pause and speed live in the client, which decides how many simulated seconds to request.
- ``view``: the player view without advancing.
- ``command`` ``{cmd}``: issue a player command (same legality checks as plans). Returns ok and info, or reasons.
- ``inspect`` ``{target}``: why a facility, site, residence or the Great Work is (not) progressing.
- ``autoplay`` ``{enabled}``: let the reference governor act alongside the player (demonstration only).
- ``quit``: end the session.
"""
from __future__ import annotations

import argparse
import json
import socket
import sys
from pathlib import Path
from typing import Any

from .engine import Simulation, load_definitions
from .engine.definitions import read_json
from .player_view import observe

PROTOCOL = 1          # wire protocol; contract sim_bridge v4 adds fields and spatial commands only
DEFAULT_PORT = 47615
MAX_ADVANCE = 600
ROOT = Path(__file__).resolve().parents[1]


def stamp(second: int) -> str:
    return f"{second // 60:02d}:{second % 60:02d}"


class Session:
    """One running simulation and the client-facing operations on it."""

    def __init__(self, overlays: list[str] | None = None, governor: str | None = None):
        self.overlays = list(overlays or [])
        self.defs = load_definitions(overlays=self.overlays)
        self.sim = Simulation(self.defs, {"id": "client", "commands": []})
        self.governor = None
        self.governor_path = governor
        self.events_sent = 0
        self.sim.step()   # second 0: initial allocation and measurements, as in a scripted run

    # ------------------------------------------------------------------ operations
    def hello(self) -> dict[str, Any]:
        d = self.defs
        return {
            "protocol": PROTOCOL,
            "scenario": {k: d["scenario"][k] for k in ("id", "duration_seconds", "step_seconds") if k in d["scenario"]},
            "overlays": [o["id"] for o in d.get("applied_overlays", [])],
            "buildings": {b: {"category": v["category"], "jobs": v.get("jobs", {}), "cost": v.get("cost", {}),
                              "patch": v.get("patch"), "recipes": v.get("recipes", [])}
                          for b, v in sorted(d["buildings"].items())},
            "residence_tiers": d["residence_rules"]["tier_order"],
            "resources": sorted(d["resources"]) if isinstance(d["resources"], (list, dict)) else [],
            "seasons": [{"id": s["id"], "start": s["start"], "end": s["end"]} for s in d["seasons"]],
            "calendar_cycle_seconds": d["scenario"].get("calendar_cycle_seconds"),
            "autoplay_available": self.sim.spatial is None,
            **({"spatial": self.sim.spatial.hello()} if self.sim.spatial is not None else {}),
        }

    def advance(self, seconds: int) -> dict[str, Any]:
        seconds = max(0, min(int(seconds), MAX_ADVANCE))
        for _ in range(seconds):
            self.sim.step()
        return self.view()

    def view(self) -> dict[str, Any]:
        view = observe(self.sim)
        view["time"] = stamp(self.sim.second)
        view["population"] = round(sum(r.population for r in self.sim.residences.values()), 2)
        view["maintenance_upkeep"] = self.sim.upkeep.state
        view["autoplay"] = self.governor is not None
        reason, at = getattr(self.sim.diag, "growth_block_now", (None, -1))
        view["colony_blockers"] = ([_blocker("growth_blocked", "population not growing: " + GROWTH_TEXT.get(reason, reason), reason=reason)]
                                   if reason and at >= self.sim.second - 1 else [])
        for site_id, site in view["sites"].items():
            built = self.sim.sites[site_id]
            site["progress"] = round(built.physical_done / built.physical_work, 3) if built.physical_work else 0.0
            site["blockers"] = site_blockers(self.sim, built)
        for fid, facility in view["facilities"].items():
            built = self.sim.facilities[fid]
            facility["blockers"] = facility_blockers(self.sim, built)
            facility["labour_priority"] = labour_rank(self.sim, built)
            facility["labour_priority_overridden"] = built.labour_priority is not None
            recipe = self.sim.defs["recipes"].get(built.recipe_id) if built.recipe_id else None
            facility["cycle_progress"] = (None if built.cycle_remaining is None or not recipe else
                                          round(1 - built.cycle_remaining / recipe["cycle_seconds"], 3))
        for rid, residence in view["residences"].items():
            residence["blockers"] = residence_blockers(self.sim, self.sim.residences[rid])
        if self.sim.spatial is not None:
            view["spatial"] = self.sim.spatial.view()
        new_events = self.sim.events[self.events_sent:]
        self.events_sent = len(self.sim.events)
        view["events"] = new_events
        return view

    def command(self, cmd: dict[str, Any]) -> dict[str, Any]:
        if not isinstance(cmd, dict) or "do" not in cmd:
            return {"ok": False, "reasons": ["malformed_command"]}
        try:
            result = self.sim.issue(cmd, source="player")
        except (KeyError, TypeError, ValueError) as error:
            return {"ok": False, "reasons": [f"invalid_command:{error}"]}
        reply = {"ok": result.ok, "info": result.info if result.ok else "", "reasons": [] if result.ok else result.reasons}
        if result.ok and result.data is not None:
            reply["preview"] = result.data   # v5: dry-run construct preview
        return reply

    def autoplay(self, enabled: bool) -> dict[str, Any]:
        from .governor import Governor, load_governor_config
        if enabled and self.sim.spatial is not None:
            # No governor can place buildings and roads legally yet; never grant infrastructure for free.
            return {"ok": False, "autoplay": False, "reasons": ["spatial:autoplay_unavailable"]}
        if enabled and self.governor is None:
            default = "empty_start_governor_v1.json" if self.defs["starting_state"].get("founding_party") else "reference_governor_v3.json"
            path = self.governor_path or str(ROOT / "economy" / "data" / "governors" / default)
            self.governor = Governor(load_governor_config(path))
            self.sim.controllers.append(self.governor)
        elif not enabled and self.governor is not None:
            self.sim.controllers.remove(self.governor)
            self.governor = None
        return {"ok": True, "autoplay": self.governor is not None}

    def inspect(self, target: str) -> dict[str, Any]:
        return explain(self.sim, target)


# ---------------------------------------------------------------------- stall inspector
# Stable blocker codes (sim_bridge contract v2). Presentation binds icons to codes; `text` is the tooltip.
# Ordered most actionable first. `output_blocked` is reserved: storage capacity is not enforced yet.
BLOCKER_CODES = ("road_disconnected", "paused", "unstaffed", "waiting_input", "awaiting_transport", "food_emergency",
                 "morphology_missing", "environment", "patch_depleted", "output_blocked", "strained", "dormant",
                 "low_need", "missing_service", "evolution_blocked", "great_work_blocked", "growth_blocked")
GROWTH_TEXT = {"no_free_capacity": "no free housing: build a home",
               "basic_needs_unsupplied": "a home is strained or dormant",
               "growth_nutrient_unavailable": "no Growth Nutrient in store for migrants"}


def _blocker(code: str, text: str, **params: Any) -> dict[str, Any]:
    assert code in BLOCKER_CODES, code
    return {"code": code, "params": params, "text": text}


def labour_rank(sim: Simulation, f) -> int:
    """Effective staffing rank (lower is staffed first): the player override or the category default."""
    order = sim.defs["workforce"]["job_priority"]
    return f.labour_priority if f.labour_priority is not None else (order.index(f.category) if f.category in order else len(order))


def input_consumers(sim: Simulation, district: str, goods: dict, exclude: str = "") -> dict:
    """Same-store recipe competitors; held inputs are reserved, not recoverable by pause."""
    result = {}
    for good in sorted(goods):
        rows = []
        for fid, f in sorted(sim.facilities.items()):
            if fid == exclude or f.district != district or f.paused:
                continue
            recipe = sim.defs["recipes"].get(f.recipe_id, {})
            amount = recipe.get("inputs", {}).get(good, 0)
            if amount and (f.status == "running" or f.status == "no_input"):
                rows.append({"entity": fid, "building": f.building_id, "recipe": f.recipe_id,
                             "per_cycle": amount, "held": f.held_inputs.get(good, 0),
                             "state": "running" if f.status == "running" else "waiting_input",
                             "outputs": dict(recipe.get("outputs", {}))})
        if rows:
            result[good] = rows
    return result


def transport_blockers(sim: Simulation, entity_id: str, missing: dict[str, int]) -> list[dict[str, Any]]:
    """Spatial mode (v4): disconnection first; goods that are on their way or waiting at the anchor."""
    spatial = sim.spatial
    if spatial is None or entity_id not in spatial.placements:
        return []
    if not spatial.connected(entity_id):
        return [_blocker("road_disconnected", "no road connection to the supply anchor: connect the entrance to a road")]
    inbound = spatial.inbound(entity_id)
    anchor = sim.store(sim.districts[0])
    carried = {g: q for g, q in missing.items() if inbound.get(g) or anchor.get(g)}
    if not carried:
        return []
    return [_blocker("awaiting_transport", "carriers bringing " + ", ".join(f"{q} {g}" for g, q in sorted(carried.items())),
                     needs=carried, inbound={g: inbound[g] for g in sorted(inbound)})]


def _without_transportable(missing: dict[str, int], blockers: list[dict[str, Any]]) -> dict[str, int]:
    """Goods reported as awaiting transport are not also 'waiting for input'."""
    carried = next((b["params"]["needs"] for b in blockers if b["code"] == "awaiting_transport"), {})
    return {g: q for g, q in missing.items() if g not in carried}


def facility_blockers(sim: Simulation, f) -> list[dict[str, Any]]:
    out = []
    disconnected = not sim.is_connected(f.id)
    if f.paused:
        out.append(_blocker("paused", "paused by the player"))
    jobs = f.definition.get("jobs", {})
    if jobs and f.staffing < 1.0 - 1e-6 and not f.paused and not disconnected:
        rank = labour_rank(sim, f)
        text = f"staffed {f.staffing:.0%} of {', '.join(f'{n} {c}' for c, n in jobs.items())}"
        if rank > 0:
            text += f" (labour priority {rank}: raise it to staff this first)"
        out.append(_blocker("unstaffed", text, staffing=round(f.staffing, 2), jobs=dict(jobs), labour_priority=rank,
                            can_raise_priority=rank > 0))
    recipe = sim.defs["recipes"].get(f.recipe_id) if f.recipe_id else None
    store = sim.local_store(f.id, f.district).counts
    missing = {r: q - store.get(r, 0) for r, q in (recipe or {}).get("inputs", {}).items() if store.get(r, 0) < q}
    transport = transport_blockers(sim, f.id, missing if f.cycle_remaining is None and not f.paused else {})
    out = transport[:1] + out + transport[1:] if disconnected else out + transport
    missing = _without_transportable(missing, transport)
    if missing and f.cycle_remaining is None:
        out.append(_blocker("waiting_input", "needs inputs " + ", ".join(f"{q} {r}" for r, q in sorted(missing.items())),
                            goods=missing, consumers=input_consumers(sim, f.district, missing, f.id)))
    if f.status == "morphology_missing":
        out.append(_blocker("morphology_missing", f"needs morphology {f.status_detail}", morphology=f.status_detail))
    elif f.status == "environment":
        out.append(_blocker("environment", f"environment: {f.status_detail}", detail=f.status_detail))
    elif f.status == "patch_depleted":
        out.append(_blocker("patch_depleted", f"patch depleted: {f.status_detail}", patch=f.status_detail))
    return out


def site_blockers(sim: Simulation, s) -> list[dict[str, Any]]:
    out = []
    missing = s.missing()
    if sim.spatial is not None and s.id in sim.spatial.depots:
        local = sim.spatial.depots[s.id]
        need = {g: q - local.get(g) for g, q in missing.items() if q > local.get(g)}
        out += transport_blockers(sim, s.id, need)
        missing = _without_transportable(need, out)
    if missing:
        out.append(_blocker("waiting_input", ", ".join(f"waiting for {q} {r}" for r, q in sorted(missing.items())),
                            goods=dict(missing), consumers=input_consumers(sim, s.district, missing)))
    if s.state == "awaiting_labour":
        if sim.builder_state.get(s.district) == "preempted_food_emergency":
            out.append(_blocker("food_emergency", "Builders are farming: food emergency", reason=sim.food_emergency.reason))
        else:
            out.append(_blocker("unstaffed", "waiting for Builders (construction labour)", labour="builders"))
    return out


def residence_blockers(sim: Simulation, r, state: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    state = state or r.presentation_state(sim.defs, sim.services_for(r))
    out = []
    if not sim.is_connected(r.id):
        out += transport_blockers(sim, r.id, {})
    if state["condition"] in ("strained", "dormant"):
        out.append(_blocker(state["condition"], f"condition {state['condition']}"))
    for good, minutes in sorted(state["need_buffer_minutes"].items()):
        if minutes < 3:
            out.append(_blocker("low_need", f"low {good}: {minutes:.1f} min", good=good, minutes=minutes))
    local = sim.spatial is not None and sim.spatial.mode == "current"
    for service, ok in state["services_for_next_tier"].items():
        if not ok:
            if local:   # v5: local reach by lane distance
                row = sim.spatial.coverage.get(r.id, {}).get(service, {})
                provider, distance, reach = row.get("provider"), row.get("distance"), row.get("range")
                text = (f"next tier needs service: {service} (nearest {provider} is {distance:.0f} m by lane; reach {reach:.0f} m)"
                        if provider else f"next tier needs service: {service} (no active provider connected)")
                out.append(_blocker("missing_service", text, service=service, provider=provider, distance=distance, range=reach))
            else:
                out.append(_blocker("missing_service", f"next tier needs service: {service}", service=service))
    next_tier = sim.defs["residences"][r.tier].get("next")
    if next_tier and not state["evolution"] and all(state["services_for_next_tier"].values()):
        need = sim.defs["residences"][next_tier]["evolution"].get("goods", {})
        store = (sim.store(r.district) if sim.spatial is None else _evolution_reachable(sim, r)).counts
        short = {g: q - store.get(g, 0) for g, q in need.items() if store.get(g, 0) < q}
        if short:
            out.append(_blocker("waiting_input", "to evolve, needs in store: " + ", ".join(f"{q} {g}" for g, q in sorted(short.items())),
                                goods=short, purpose="evolution", consumers=input_consumers(sim, r.district, short)))
    if state["evolution"]:
        missing = {f"service:{b['params']['service']}" for b in out if b["code"] == "missing_service"}
        for b in state["evolution"]["blockers"]:
            if b in missing:
                continue   # already reported as missing_service
            out.append(_blocker("evolution_blocked", f"evolution blocked: {b}", blocker=b))
    return out


def _evolution_reachable(sim: Simulation, r):
    """Spatial mode: goods a home can draw on for evolution = its depot plus the anchor store (carriers bring them)."""
    from .engine.inventory import Inventory
    combined = Inventory(sim.defs["resources"], sim.spatial.depots[r.id].counts)
    combined.put(sim.store(r.district).counts)
    return combined


def explain(sim: Simulation, target: str) -> dict[str, Any]:
    """A player-readable answer to 'why is this not progressing?' for one entity.

    `blockers` is the ordered, structured list (contract v2); `reasons` keeps the plain text (v1).
    """
    def reply(kind: str, blockers: list[dict[str, Any]], blocked: bool, **fields: Any) -> dict[str, Any]:
        return {"ok": True, "kind": kind, "entity": target, **fields, "blocked": blocked,
                "blockers": blockers, "reasons": [b["text"] for b in blockers]}

    if target == "great_work":
        raw = sim.great_work_blockers() if sim.great_work.begun_at is None else []
        blockers = [_blocker("great_work_blocked", b, blocker=b) for b in raw]
        return reply("great_work", blockers, bool(blockers), begun=sim.great_work.begun_at is not None,
                     stage=sim.great_work.stage_index)
    if target in sim.facilities:
        f = sim.facilities[target]
        recipe = sim.defs["recipes"].get(f.recipe_id) if f.recipe_id else None
        blockers = facility_blockers(sim, f)
        if f.status not in ("running", "idle") and not blockers:   # never leave a stall unexplained
            blockers = [_blocker("environment", f"{f.status}: {f.status_detail}", detail=f"{f.status}:{f.status_detail}")]
        return reply("facility", blockers, f.status != "running", building=f.building_id, status=f.status,
                     labour_priority=labour_rank(sim, f), labour_priority_overridden=f.labour_priority is not None,
                     detail=f.status_detail, staffing=round(f.staffing, 2), recipe=f.recipe_id,
                     cycle_progress=None if f.cycle_remaining is None or not recipe else
                     round(1 - f.cycle_remaining / recipe["cycle_seconds"], 3))
    if target in sim.sites:
        s = sim.sites[target]
        waits = {k: round(v / 60, 1) for k, v in sorted(sim.diag.site_wait.get(s.id, {}).items(), key=lambda i: -i[1])}
        total = s.physical_work or 1.0
        return reply("site", site_blockers(sim, s), s.state in ("awaiting_materials", "awaiting_labour"),
                     builds=s.target, state=s.state, missing=s.missing(),
                     work_progress=round(s.physical_done / total, 3), waited_minutes=waits)
    if target in sim.residences:
        r = sim.residences[target]
        state = r.presentation_state(sim.defs, sim.services_for(r))
        blockers = residence_blockers(sim, r, state)
        defs = sim.defs["residences"]
        next_tier = defs[r.tier].get("next")
        change = None
        if next_tier:
            now, then = defs[r.tier], defs[next_tier]
            change = {now["class"]: -now["workforce"]}
            change[then["class"]] = change.get(then["class"], 0) + then["workforce"]
        ready = bool(next_tier) and not state["evolution"] and not blockers
        return reply("residence", blockers, bool(blockers), **state, next_tier=next_tier, evolution_ready=ready,
                     evolution_workforce_change=change)
    return {"ok": False, "reasons": [f"unknown_target:{target}"]}


# ---------------------------------------------------------------------- transport
def handle(session: Session, request: dict[str, Any]) -> dict[str, Any]:
    op = request.get("op")
    try:
        if op == "hello":
            reply = {"ok": True, **session.hello()}
        elif op == "advance":
            reply = {"ok": True, "view": session.advance(request.get("seconds", 1))}
        elif op == "view":
            reply = {"ok": True, "view": session.view()}
        elif op == "command":
            reply = session.command(request.get("cmd"))
        elif op == "inspect":
            reply = session.inspect(str(request.get("target", "")))
        elif op == "autoplay":
            reply = session.autoplay(bool(request.get("enabled")))
        elif op == "quit":
            reply = {"ok": True, "bye": True}
        else:
            reply = {"ok": False, "reasons": [f"unknown_op:{op}"]}
    except Exception as error:   # the client must always get a reply; the error is the diagnosis
        reply = {"ok": False, "reasons": [f"bridge_error:{type(error).__name__}:{error}"]}
    reply["id"] = request.get("id")
    reply["op"] = op
    return reply


def serve(session: Session, port: int, once: bool = True, accept_timeout: float = 120.0) -> None:
    with socket.create_server(("127.0.0.1", port)) as server:
        server.settimeout(accept_timeout)   # exit if no client ever connects (e.g. the client crashed at start)
        print(f"bridge listening on 127.0.0.1:{port}", flush=True)
        while True:
            try:
                conn, _ = server.accept()
            except socket.timeout:
                print("bridge: no client connected; exiting", flush=True)
                return
            conn.settimeout(None)
            with conn, conn.makefile("rwb") as stream:
                for raw in stream:
                    raw = raw.strip()
                    if not raw:
                        continue
                    try:
                        request = json.loads(raw)
                    except json.JSONDecodeError:
                        request = {"op": "malformed"}
                    reply = handle(session, request)
                    stream.write(json.dumps(reply, separators=(",", ":"), default=str).encode("utf-8") + b"\n")
                    stream.flush()
                    if request.get("op") == "quit":
                        return
            if once:
                return


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Local simulation bridge for the Godot client")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--overlay", action="append", default=[], help="definitions overlay (repeatable)")
    parser.add_argument("--governor", help="reference governor config used when the client enables autoplay")
    args = parser.parse_args(argv)
    serve(Session(args.overlay, args.governor), args.port)
    return 0


if __name__ == "__main__":
    sys.exit(main())
