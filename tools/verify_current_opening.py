"""Play the current-habitat opening fixture for 90 minutes and record what happened.

    python3 tools/verify_current_opening.py [--check]

Every command in economy/data/plans/current_opening_v1.json goes through the bridge exactly as a player's
would. The evidence (tests/fixtures/current_opening_evidence.json) records costs paid, carrier trips, 10-minute
snapshots and the first Stable home. --check verifies the committed evidence without rewriting it.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from economy.bridge import Session   # noqa: E402

PLAN = ROOT / "economy/data/plans/current_opening_v1.json"
EVIDENCE = ROOT / "tests/fixtures/current_opening_evidence.json"


def play(plan_path=PLAN) -> dict:
    plan = json.loads(plan_path.read_text())
    s = Session([str(ROOT / o) for o in plan["overlays"]])
    queue = sorted(plan["commands"], key=lambda c: c["at"])
    results, snapshots, trips, first_stable = [], [], {"deliver": 0, "collect": 0}, None
    start_store = dict(s.sim.store("core").counts)
    last_jobs = {c.id: None for c in s.sim.spatial.carriers}
    for second in range(plan["duration_seconds"] + 1):
        while queue and queue[0]["at"] <= s.sim.second:
            cmd = queue.pop(0)["cmd"]
            r = s.command(cmd)
            results.append({"at": s.sim.second, "do": cmd["do"], "id": cmd.get("id", cmd.get("residence")),
                            "ok": r["ok"], "info": r["info"], "reasons": r["reasons"]})
        s.sim.step()
        for c in s.sim.spatial.carriers:
            if c.job in trips and c.job != last_jobs[c.id] and c.state == "to_target":
                trips[c.job] += 1
            last_jobs[c.id] = c.job
        if first_stable is None and any(r.tier == "stable" for r in s.sim.residences.values()):
            first_stable = s.sim.second
        if s.sim.second % 600 == 0:
            v = s.view()
            snapshots.append({
                "time": v["time"], "population": v["population"], "food_minutes": round(v["food_minutes"] or 0, 2),
                "food_emergency": v["food_emergency"], "sites": sorted(v["sites"]), "facilities": len(v["facilities"]),
                "tiers": {rid: r["tier"] for rid, r in sorted(v["residences"].items())},
                "anchor_store": {k: q for k, q in sorted(v["store"].items()) if q},
                "carriers_moving": sum(1 for c in v["spatial"]["carriers"].values() if c["state"] != "idle"),
            })
    sim = s.sim
    paid = {}
    for site in sim.sites.values():
        for good, q in site.cost.items():
            paid[good] = paid.get(good, 0) + q
    v = s.view()
    evidence = {
        "plan": plan["id"], "results": results, "construction_paid": dict(sorted(paid.items())),
        "all_sites_paid_in_full": all(site.delivered == site.cost or site.materials_complete_at is not None
                                      for site in sim.sites.values()),
        "carrier_trips": trips, "first_stable_second": first_stable,
        "founders_remaining": sim.founders_remaining,
        "food_emergency_seconds": sim.food_emergency.seconds_active,
        "devolutions": sum(1 for e in sim.events if "devolved" in e),
        "start_store": {k: q for k, q in sorted(start_store.items()) if q},
        "coverage_home_1": {svc: row for svc, row in sorted(v["spatial"]["placements"]["home_1"]["coverage"].items())},
        "snapshots": snapshots,
    }

    if plan_path != PLAN:
        evidence["produced"] = dict(sorted(sim.diag.produced.items()))
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--plan", type=Path, default=PLAN)
    parser.add_argument("--evidence", type=Path, default=EVIDENCE)
    args = parser.parse_args()
    content = json.dumps(play(args.plan), indent=1, sort_keys=True) + "\n"
    if args.check:
        assert args.evidence.read_text() == content, "committed evidence differs from reproduction"
        print("current opening evidence reproduces")
    else:
        args.evidence.write_text(content)
        print(f"wrote {args.evidence.resolve().relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
