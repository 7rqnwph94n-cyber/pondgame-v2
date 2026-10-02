"""Bounded parameter comparison over definitions.

    python3 -m economy.sweep economy/data/experiments/candidate_bootstrap_sweep.json [--json reports/sweep.json]

The sweep file names a plan, base overlays and parameters. Each parameter has
a dotted ``path`` into the definitions (list indices allowed) and ``values``
listed from LEAST to MOST generous. Every combination is simulated. A run is
viable when the Memory Reef completes within the scenario. The recommendation
is the viable combination with the lowest total generosity rank; if none is
viable, the runs are ranked by progress instead.
"""
from __future__ import annotations

import argparse
import itertools
import json
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
from typing import Any

from .engine import Simulation, load_definitions, load_plan, validate_definitions

TIERS = ["shelter", "stable", "symbiotic", "memory"]


def set_path(defs: dict[str, Any], path: str, value: Any) -> None:
    keys = [int(k) if k.isdigit() else k for k in path.split(".")]
    target = defs
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = deepcopy(value)


def progress(report: dict[str, Any]) -> tuple:
    outcome = report["outcome"]
    reached = outcome["tier_first_reached"]
    best = max((TIERS.index(t) for t in reached), default=0)
    first_best = reached.get(TIERS[best], "99:99")
    minutes = int(first_best[:2]) * 60 + int(first_best[3:]) if first_best else 9999
    done = outcome["great_work_completed_seconds"]
    return (
        1 if done is not None else 0,
        -(done or 0),
        outcome["great_work_stages_complete"],
        best,
        -minutes,
        outcome["final_population"],
    )


def summarise(report: dict[str, Any]) -> dict[str, Any]:
    outcome = report["outcome"]
    return {
        "reef_completed_at": outcome["great_work_completed_at"],
        "stages": outcome["great_work_stages_complete"],
        "first_stable": outcome["tier_first_reached"].get("stable"),
        "first_symbiotic": outcome["tier_first_reached"].get("symbiotic"),
        "first_memory": outcome["tier_first_reached"].get("memory"),
        "final_tiers": outcome["final_tiers"],
        "final_population": outcome["final_population"],
        "upkeep_unpaid_minutes": report["maintenance_upkeep"]["unpaid_minutes"],
        "top_bottlenecks": [b["key"] for b in report["bottlenecks"][:3]],
    }


def _run_one(job: tuple[dict[str, Any], dict[str, Any], dict[str, Any], int]) -> dict[str, Any]:
    defs, plan, setting, generosity = job
    errors = validate_definitions(defs)
    if errors:
        raise ValueError(errors)
    report = Simulation(defs, plan).run()
    return {"setting": setting, "generosity": generosity, "progress": progress(report), **summarise(report)}


def run_sweep(spec: dict[str, Any], workers: int | None = None) -> dict[str, Any]:
    base = load_definitions(overlays=spec.get("base_overlays", []))
    plan = load_plan(spec["plan"])
    parameters = spec["parameters"]
    jobs = []
    for combo in itertools.product(*[range(len(p["values"])) for p in parameters]):
        defs = deepcopy(base)
        setting = {}
        for parameter, index in zip(parameters, combo):
            value = parameter["values"][index]
            for path in parameter.get("paths", [parameter.get("path")]):
                set_path(defs, path, value)
            setting[parameter["name"]] = parameter.get("labels", parameter["values"])[index]
        jobs.append((defs, plan, setting, sum(combo)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        runs = list(pool.map(_run_one, jobs))   # order preserved -> deterministic output
    viable = [r for r in runs if r["reef_completed_at"] is not None]
    if viable:
        best = min(viable, key=lambda r: (r["generosity"], [-x for x in r["progress"]]))
        verdict = "viable"
    else:
        best = max(runs, key=lambda r: (r["progress"], -r["generosity"]))
        verdict = "no tested setting completes the Memory Reef"
    ranked = sorted(runs, key=lambda r: ([-x for x in r["progress"]], r["generosity"]))
    return {"id": spec["id"], "plan": spec["plan"], "verdict": verdict, "recommendation": best,
            "viable_count": len(viable), "marginal_effects": marginal_effects(runs), "runs": ranked}


def _minutes(stamp: str | None) -> float | None:
    return None if stamp is None else int(stamp[:2]) + int(stamp[3:]) / 60


def marginal_effects(runs: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Mean outcome for each value of each parameter, averaged over all other parameters."""
    effects: dict[str, dict[str, dict[str, Any]]] = {}
    for name in runs[0]["setting"]:
        effects[name] = {}
        for value in sorted({json.dumps(r["setting"][name]) for r in runs}):
            group = [r for r in runs if json.dumps(r["setting"][name]) == value]
            stable = [m for m in (_minutes(r["first_stable"]) for r in group) if m is not None]
            effects[name][json.loads(value) if not value.startswith("[") else value] = {
                "runs": len(group),
                "mean_final_population": round(sum(r["final_population"] for r in group) / len(group), 1),
                "mean_first_stable_minute": round(sum(stable) / len(stable), 1) if stable else None,
                "runs_reaching_symbiotic": sum(1 for r in group if r["first_symbiotic"]),
                "mean_upkeep_unpaid_minutes": round(sum(r["upkeep_unpaid_minutes"] for r in group) / len(group), 1),
            }
    return effects


def run_ladder(spec: dict[str, Any]) -> dict[str, Any]:
    """Cumulative levers: each step keeps every earlier step's changes (diagnostic, never a proposal)."""
    defs = load_definitions(overlays=spec.get("base_overlays", []))
    plan = load_plan(spec["plan"])
    steps = []
    for step in spec["ladder"]:
        for path, value in step.get("set", {}).items():
            set_path(defs, path, value)
        for path, items in step.get("append", {}).items():
            keys = [int(k) if k.isdigit() else k for k in path.split(".")]
            target = defs
            for key in keys:
                target = target[key]
            target.extend(deepcopy(items))
        errors = validate_definitions(defs)
        if errors:
            raise ValueError(errors)
        report = Simulation(deepcopy(defs), plan).run()
        steps.append({"step": step["name"], **summarise(report)})
    return {"id": spec["id"], "plan": spec["plan"], "steps": steps}


def format_ladder(result: dict[str, Any]) -> str:
    lines = [f"Lever ladder {result['id']} (cumulative; plan {result['plan']})",
             "step | reef | stages | stable | symbiotic | memory | pop | top bottlenecks"]
    for s in result["steps"]:
        lines.append(" | ".join(str(x) for x in (s["step"], s["reef_completed_at"] or "-", s["stages"], s["first_stable"] or "-",
                                                  s["first_symbiotic"] or "-", s["first_memory"] or "-", s["final_population"],
                                                  ", ".join(s["top_bottlenecks"]))))
    return "\n".join(lines)


def format_sweep(result: dict[str, Any], top: int = 12) -> str:
    lines = [f"Sweep {result['id']} ({len(result['runs'])} runs, plan {result['plan']})",
             f"Verdict: {result['verdict']}; viable runs: {result['viable_count']}"]
    rec = result["recommendation"]
    if result["viable_count"]:
        lines.append(f"Recommended (least generous viable): {rec['setting']}")
    else:
        lines.append(f"Best-progress run (nothing viable, so no recommendation): {rec['setting']}")
    lines.append("")
    lines.append("Marginal effects (mean over all other parameters)")
    for name, values in result["marginal_effects"].items():
        cells = "; ".join(f"{v}: pop {e['mean_final_population']}, stable {e['mean_first_stable_minute']}m, "
                          f"symbiotic runs {e['runs_reaching_symbiotic']}, unpaid {e['mean_upkeep_unpaid_minutes']}m"
                          for v, e in values.items())
        lines.append(f"  {name}: {cells}")
    lines.append("")
    names = list(result["runs"][0]["setting"])
    header = " | ".join(names) + " | gen | reef | stable | symb | memory | pop | unpaid | top bottlenecks"
    lines.append(header)
    for run in result["runs"][:top]:
        cells = [str(run["setting"][n]) for n in names]
        cells += [str(run["generosity"]), str(run["reef_completed_at"] or "-"), str(run["first_stable"] or "-"),
                  str(run["first_symbiotic"] or "-"), str(run["first_memory"] or "-"), str(run["final_population"]),
                  str(run["upkeep_unpaid_minutes"]), ", ".join(run["top_bottlenecks"])]
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--top", type=int, default=12)
    parser.add_argument("--workers", type=int, help="parallel processes (default: CPU count)")
    args = parser.parse_args()
    spec = json.loads(args.spec.read_text(encoding="utf-8"))
    if "ladder" in spec:
        result = run_ladder(spec)
        print(format_ladder(result))
    else:
        result = run_sweep(spec, args.workers)
        print(format_sweep(result, args.top))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=1), encoding="utf-8")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
