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

PROTOCOL = 1
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
            "autoplay_available": True,
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
        for site_id, site in view["sites"].items():
            built = self.sim.sites[site_id]
            site["progress"] = round(built.physical_done / built.physical_work, 3) if built.physical_work else 0.0
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
        return {"ok": result.ok, "info": result.info if result.ok else "", "reasons": [] if result.ok else result.reasons}

    def autoplay(self, enabled: bool) -> dict[str, Any]:
        from .governor import Governor, load_governor_config
        if enabled and self.governor is None:
            path = self.governor_path or str(ROOT / "economy" / "data" / "governors" / "reference_governor_v3.json")
            self.governor = Governor(load_governor_config(path))
            self.sim.controllers.append(self.governor)
        elif not enabled and self.governor is not None:
            self.sim.controllers.remove(self.governor)
            self.governor = None
        return {"ok": True, "autoplay": self.governor is not None}

    def inspect(self, target: str) -> dict[str, Any]:
        return explain(self.sim, target)


# ---------------------------------------------------------------------- stall inspector
def explain(sim: Simulation, target: str) -> dict[str, Any]:
    """A player-readable answer to 'why is this not progressing?' for one entity."""
    if target == "great_work":
        blockers = sim.great_work_blockers() if sim.great_work.begun_at is None else []
        return {"ok": True, "kind": "great_work", "entity": target, "begun": sim.great_work.begun_at is not None,
                "stage": sim.great_work.stage_index, "blocked": bool(blockers), "reasons": blockers}
    if target in sim.facilities:
        f = sim.facilities[target]
        reasons = []
        if f.paused:
            reasons.append("paused by the player")
        if f.status not in ("running",) and f.status_detail:
            reasons.append(f"{f.status}: {f.status_detail}")
        elif f.status not in ("running",):
            reasons.append(f.status)
        recipe = sim.defs["recipes"].get(f.recipe_id) if f.recipe_id else None
        store = sim.store(f.district).counts
        missing_inputs = {r: q - store.get(r, 0) for r, q in (recipe or {}).get("inputs", {}).items() if store.get(r, 0) < q}
        if missing_inputs and f.cycle_remaining is None:
            reasons.append("needs inputs " + ", ".join(f"{q} {r}" for r, q in sorted(missing_inputs.items())))
        jobs = f.definition.get("jobs", {})
        if jobs and f.staffing < 1.0 - 1e-6:
            reasons.append(f"staffed {f.staffing:.0%} of {', '.join(f'{n} {c}' for c, n in jobs.items())}")
        return {"ok": True, "kind": "facility", "entity": target, "building": f.building_id, "status": f.status,
                "detail": f.status_detail, "staffing": round(f.staffing, 2), "recipe": f.recipe_id,
                "cycle_progress": None if f.cycle_remaining is None or not recipe else
                round(1 - f.cycle_remaining / recipe["cycle_seconds"], 3),
                "blocked": f.status != "running", "reasons": reasons}
    if target in sim.sites:
        s = sim.sites[target]
        missing = s.missing()
        reasons = [f"waiting for {q} {r}" for r, q in sorted(missing.items())]
        if s.state == "awaiting_labour":
            reasons.append("waiting for Builders (construction labour)")
        waits = {k: round(v / 60, 1) for k, v in sorted(sim.diag.site_wait.get(s.id, {}).items(), key=lambda i: -i[1])}
        total = s.physical_work or 1.0
        return {"ok": True, "kind": "site", "entity": target, "builds": s.target, "state": s.state, "missing": missing,
                "work_progress": round(s.physical_done / total, 3), "waited_minutes": waits,
                "blocked": s.state in ("awaiting_materials", "awaiting_labour"), "reasons": reasons}
    if target in sim.residences:
        r = sim.residences[target]
        state = r.presentation_state(sim.defs, sim.services.get(r.district, set()))
        reasons = []
        if state["condition"] != "normal":
            reasons.append(f"condition {state['condition']}")
        low = {g: m for g, m in state["need_buffer_minutes"].items() if m < 3}
        if low:
            reasons.append("low needs: " + ", ".join(f"{g} {m:.1f} min" for g, m in sorted(low.items())))
        missing_services = [s for s, ok in state["services_for_next_tier"].items() if not ok]
        if missing_services:
            reasons.append("next tier needs services: " + ", ".join(missing_services))
        if state["evolution"] and state["evolution"]["blockers"]:
            reasons.append("evolution blocked: " + ", ".join(state["evolution"]["blockers"]))
        return {"ok": True, "kind": "residence", "entity": target, **state, "blocked": bool(reasons), "reasons": reasons}
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
