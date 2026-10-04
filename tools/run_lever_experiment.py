"""Run a small named-lever experiment (controls plus at most eight candidates) with detailed metrics.

    python3 tools/run_lever_experiment.py economy/data/experiments/carbonate_workforce_v1.json [--json out.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from economy.engine.definitions import load_definitions, read_json  # noqa: E402
from economy.sweep import apply_level, evaluate, parameter_levels, simulate, summarise  # noqa: E402

MAX_CANDIDATES = 8


def lever_set(spec: dict, name: str) -> dict:
    lever = spec["levers"][name]
    if "set" in lever:
        return {"set": lever["set"]}
    source = read_json(ROOT / lever["from_spec"])
    for parameter in source["parameters"]:
        for level in parameter_levels(parameter):
            if level["label"] == lever["level"]:
                return level
    raise KeyError(name)


def run(job: tuple) -> dict:
    spec, label, overlays, levers, criteria = job
    defs = load_definitions(overlays=[ROOT / o for o in overlays])
    for name in levers:
        apply_level(defs, lever_set(spec, name))
    sim, report, governor = simulate(defs, {"id": "governor", "commands": []}, read_json(ROOT / spec["governor"]))
    s = summarise(report)
    produced = report["produced_by_recipes"]
    carbonate_made = sum(v for k, v in produced.items() if k == "carbonate") if isinstance(produced.get("carbonate"), int) else produced.get("carbonate", 0)
    upkeep = report["maintenance_upkeep"]
    wf = report["workforce"]
    return {
        "label": label, "levers": levers, "failures": evaluate(s, criteria), **{k: s[k] for k in (
            "first_stable", "first_symbiotic", "first_memory", "reef_completed_at", "stages", "final_tiers", "final_population",
            "staple_shortage_minutes", "gel_shortage_minutes", "food_emergency_minutes", "devolutions", "upkeep_unpaid_minutes",
            "trade_bought", "idle_construction_wp_minutes", "blocked_entity_minutes", "top_bottlenecks")},
        "carbonate_produced": carbonate_made,
        "surface_carbonate_left": round(sim.env.reserves.get("surface_carbonate") or 0.0, 1),
        "enzyme_paid": upkeep.get("enzyme_paid"), "upkeep_state": upkeep.get("state"),
        "vacancy_wp_minutes": wf.get("vacancy_wp_minutes"), "below_class_wp_minutes": wf.get("working_below_class_wp_minutes"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("spec")
    parser.add_argument("--json")
    args = parser.parse_args()
    spec = read_json(ROOT / args.spec)
    if len(spec["candidates"]) > MAX_CANDIDATES:
        raise SystemExit(f"bounded experiment: at most {MAX_CANDIDATES} candidates")
    criteria = read_json(ROOT / spec["criteria_from"])["criteria"]
    jobs = [(spec, c["label"], c["base_overlays"], c["levers"], criteria) for c in spec["controls"]]
    jobs += [(spec, c["label"], spec["candidate_base_overlays"], c["levers"], criteria) for c in spec["candidates"]]
    with ProcessPoolExecutor() as pool:
        rows = list(pool.map(run, jobs))
    for r in rows:
        print(json.dumps(r, default=str))
    if args.json:
        Path(args.json).write_text(json.dumps(rows, indent=1, default=str), encoding="utf-8")
    passing = [r for r in rows[len(spec["controls"]):] if not r["failures"]]
    print(f"passing candidates: {len(passing)} of {len(spec['candidates'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
