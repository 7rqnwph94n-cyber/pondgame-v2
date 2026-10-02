"""Bounded parameter comparisons and cumulative lever ladders over definitions.

    python3 -m economy.sweep <spec.json> [--json reports/sweep.json] [--workers N] [--top N]

Sweep spec
----------
``plan``, optional ``base_overlays``, ``parameters`` and optional ``criteria``/``ladders``.

Each parameter lists levels from LEAST to MOST generous, in one of two forms:

- simple: ``{"name", "path" | "paths", "values", "labels"?}``. Every path gets the level's value.
- levels: ``{"name", "levels": [{"label", "set"?: {path: value}, "append"?: {path: [items]},
  "scale"?: {path: factor}}]}``. ``scale`` multiplies every number in the dict at ``path``,
  rounding to whole units and never below 1.

Paths are dotted, and list indices are allowed (``seasons.1.sediment``). Every combination is
simulated. Generosity is the sum of level indices. A run *passes* when it meets ``criteria``;
without criteria it passes when the Memory Reef completes. The recommendation is the passing run
with the lowest generosity. Single-lever runs (all other levers at their base level) and
``ladders`` (cumulative steps naming a level per lever) are reported so causality stays visible.

A spec with a top-level ``ladder`` list runs the older diagnostic ladder format (see
``run_ladder``).
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


# ---------------------------------------------------------------- definitions editing
def _walk(defs: dict[str, Any], path: str):
    keys = [int(k) if k.isdigit() else k for k in path.split(".")]
    target = defs
    for key in keys[:-1]:
        target = target[key]
    return target, keys[-1]


def set_path(defs: dict[str, Any], path: str, value: Any) -> None:
    target, key = _walk(defs, path)
    target[key] = deepcopy(value)


def append_path(defs: dict[str, Any], path: str, items: list[Any]) -> None:
    target, key = _walk(defs, path)
    target[key].extend(deepcopy(items))


def scale_path(defs: dict[str, Any], path: str, factor: float) -> None:
    target, key = _walk(defs, path)
    goods = target[key]
    for name, quantity in goods.items():
        goods[name] = max(1, int(quantity * factor + 0.5))


def parameter_levels(parameter: dict[str, Any]) -> list[dict[str, Any]]:
    if "levels" in parameter:
        return parameter["levels"]
    labels = parameter.get("labels", parameter["values"])
    paths = parameter.get("paths", [parameter.get("path")])
    return [{"label": label, "set": {path: value for path in paths}} for value, label in zip(parameter["values"], labels)]


def apply_level(defs: dict[str, Any], level: dict[str, Any]) -> None:
    for path, value in level.get("set", {}).items():
        set_path(defs, path, value)
    for path, items in level.get("append", {}).items():
        append_path(defs, path, items)
    for path, factor in level.get("scale", {}).items():
        scale_path(defs, path, factor)


# ---------------------------------------------------------------- outcome summary
def _minutes(stamp: str | None) -> float | None:
    return None if stamp is None else int(stamp[:2]) + int(stamp[3:]) / 60


def progress(report: dict[str, Any]) -> tuple:
    outcome = report["outcome"]
    reached = outcome["tier_first_reached"]
    best = max((TIERS.index(t) for t in reached), default=0)
    first_best = _minutes(reached.get(TIERS[best])) or 999.0
    done = outcome["great_work_completed_seconds"]
    return (1 if done is not None else 0, -(done or 0), outcome["great_work_stages_complete"], best, -first_best,
            outcome["final_population"])


def summarise(report: dict[str, Any]) -> dict[str, Any]:
    outcome = report["outcome"]
    events = report.get("events", [])
    shortage = {"staple": 0.0, "balanced_gel": 0.0}
    for residence in report["residences"].values():
        for good in shortage:
            shortage[good] += residence["shortage_minutes"].get(good, 0.0)
    return {
        "reef_completed_at": outcome["great_work_completed_at"],
        "reef_minutes": None if outcome["great_work_completed_seconds"] is None else round(outcome["great_work_completed_seconds"] / 60, 1),
        "stages": outcome["great_work_stages_complete"],
        "first_stable": outcome["tier_first_reached"].get("stable"),
        "first_symbiotic": outcome["tier_first_reached"].get("symbiotic"),
        "first_memory": outcome["tier_first_reached"].get("memory"),
        "final_tiers": outcome["final_tiers"],
        "final_population": outcome["final_population"],
        "devolutions": sum(1 for e in events if " devolved " in e),
        "symbiotic_devolutions": sum(1 for e in events if "devolved symbiotic" in e),
        "staple_shortage_minutes": round(shortage["staple"], 1),
        "gel_shortage_minutes": round(shortage["balanced_gel"], 1),
        "food_emergency_minutes": report.get("food_emergency", {}).get("minutes_active", 0.0),
        "upkeep_unpaid_minutes": report["maintenance_upkeep"]["unpaid_minutes"],
        "blocked_entity_minutes": report.get("blocked_entity_minutes_total"),
        "top_bottlenecks": [b["key"] for b in report["bottlenecks"][:3]],
    }


def evaluate(summary: dict[str, Any], criteria: dict[str, Any] | None) -> list[str]:
    """Return failed criteria (empty list = pass)."""
    if not criteria:
        return [] if summary["reef_completed_at"] else ["reef_not_completed"]
    failures = []
    if criteria.get("require_symbiotic") and not summary["first_symbiotic"]:
        failures.append("no_symbiotic")
    if summary["symbiotic_devolutions"] > criteria.get("max_symbiotic_devolutions", 0):
        failures.append("symbiotic_devolved(gel)")
    if summary["devolutions"] > criteria.get("max_devolutions", 0):
        failures.append("devolution")
    if summary["staple_shortage_minutes"] > criteria.get("max_staple_shortage_minutes", 0):
        failures.append("food_not_solvent")
    if summary["upkeep_unpaid_minutes"] > criteria.get("max_unpaid_minutes", 0):
        failures.append("maintenance_not_solvent")
    window = criteria.get("reef_window_minutes")
    if summary["reef_minutes"] is None:
        failures.append("reef_not_completed")
    elif window and summary["reef_minutes"] > window[1]:
        failures.append("reef_too_late")
    return failures


# ---------------------------------------------------------------- running
def _run_one(job: tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[int], dict[str, Any] | None]) -> dict[str, Any]:
    defs, plan, setting, combo, criteria = job
    errors = validate_definitions(defs)
    if errors:
        raise ValueError(errors)
    report = Simulation(defs, plan).run()
    summary = summarise(report)
    failures = evaluate(summary, criteria)
    window = (criteria or {}).get("reef_window_minutes")
    early = bool(window and summary["reef_minutes"] is not None and summary["reef_minutes"] < window[0])
    return {"setting": setting, "levels": combo, "generosity": sum(combo), "progress": progress(report),
            "passes": not failures, "failures": failures, "earlier_than_target": early, **summary}


def run_sweep(spec: dict[str, Any], workers: int | None = None) -> dict[str, Any]:
    base = load_definitions(overlays=spec.get("base_overlays", []))
    plan = load_plan(spec["plan"])
    parameters = spec["parameters"]
    criteria = spec.get("criteria")
    levels = [parameter_levels(p) for p in parameters]
    jobs = []
    for combo in itertools.product(*[range(len(l)) for l in levels]):
        defs = deepcopy(base)
        setting = {}
        for parameter, options, index in zip(parameters, levels, combo):
            apply_level(defs, options[index])
            setting[parameter["name"]] = options[index]["label"]
        jobs.append((defs, plan, setting, list(combo), criteria))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        runs = list(pool.map(_run_one, jobs))   # order preserved -> deterministic output
    passing = [r for r in runs if r["passes"]]
    if passing:
        best = min(passing, key=lambda r: (r["generosity"], -(r["reef_minutes"] or 0)))
        verdict = "pass"
    else:
        best = max(runs, key=lambda r: (r["progress"], -r["generosity"]))
        verdict = "no tested setting meets the criteria"
    by_levels = {tuple(r["levels"]): r for r in runs}
    singles = [r for r in runs if sum(1 for i in r["levels"] if i) <= 1]
    ladders = []
    for ladder in spec.get("ladders", []):
        steps = []
        current = [0] * len(parameters)
        names = [p["name"] for p in parameters]
        for step in ladder["steps"]:
            for name, label in step.items():
                index = names.index(name)
                current[index] = [l["label"] for l in levels[index]].index(label)
            steps.append(by_levels[tuple(current)])
        ladders.append({"name": ladder["name"], "steps": steps})
    ranked = sorted(runs, key=lambda r: (not r["passes"], r["generosity"] if r["passes"] else 0, [-x for x in r["progress"]]))
    return {"id": spec["id"], "plan": spec["plan"], "criteria": criteria, "verdict": verdict, "recommendation": best,
            "passing_count": len(passing), "viable_count": len(passing), "singles": singles, "ladders": ladders,
            "marginal_effects": marginal_effects(runs), "runs": ranked}


def marginal_effects(runs: list[dict[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    """Mean outcome for each value of each parameter, averaged over all other parameters."""
    effects: dict[str, dict[str, dict[str, Any]]] = {}
    for name in runs[0]["setting"]:
        effects[name] = {}
        for value in sorted({json.dumps(r["setting"][name]) for r in runs}):
            group = [r for r in runs if json.dumps(r["setting"][name]) == value]
            stable = [m for m in (_minutes(r["first_stable"]) for r in group) if m is not None]
            reef = [r["reef_minutes"] for r in group if r.get("reef_minutes") is not None]
            effects[name][json.loads(value) if not value.startswith("[") else value] = {
                "runs": len(group),
                "mean_final_population": round(sum(r["final_population"] for r in group) / len(group), 1),
                "mean_first_stable_minute": round(sum(stable) / len(stable), 1) if stable else None,
                "runs_reaching_symbiotic": sum(1 for r in group if r["first_symbiotic"]),
                "runs_completing_reef": len(reef),
                "mean_reef_minute": round(sum(reef) / len(reef), 1) if reef else None,
                "mean_upkeep_unpaid_minutes": round(sum(r["upkeep_unpaid_minutes"] for r in group) / len(group), 1),
            }
    return effects


def run_ladder(spec: dict[str, Any]) -> dict[str, Any]:
    """Cumulative diagnostic levers: each step keeps every earlier step's changes (never a proposal)."""
    defs = load_definitions(overlays=spec.get("base_overlays", []))
    plan = load_plan(spec["plan"])
    steps = []
    for step in spec["ladder"]:
        apply_level(defs, step)
        errors = validate_definitions(defs)
        if errors:
            raise ValueError(errors)
        report = Simulation(deepcopy(defs), plan).run()
        steps.append({"step": step["name"], **summarise(report)})
    return {"id": spec["id"], "plan": spec["plan"], "steps": steps}


# ---------------------------------------------------------------- formatting
def _row(run: dict[str, Any]) -> str:
    return " | ".join(str(x) for x in (
        run["reef_completed_at"] or "-", run["stages"], run["first_stable"] or "-", run["first_symbiotic"] or "-",
        run["first_memory"] or "-", run["final_population"], run["upkeep_unpaid_minutes"], run["staple_shortage_minutes"],
        run["devolutions"], run["blocked_entity_minutes"], ", ".join(run["top_bottlenecks"])))


ROW_HEADER = "reef | stages | stable | symb | memory | pop | unpaid | staple short | devolutions | blocked | top bottlenecks"


def format_ladder(result: dict[str, Any]) -> str:
    lines = [f"Lever ladder {result['id']} (cumulative; plan {result['plan']})", "step | " + ROW_HEADER]
    for s in result["steps"]:
        lines.append(f"{s['step']} | {_row(s)}")
    return "\n".join(lines)


def format_sweep(result: dict[str, Any], top: int = 12) -> str:
    lines = [f"Sweep {result['id']} ({len(result['runs'])} runs, plan {result['plan']})",
             f"Verdict: {result['verdict']}; passing runs: {result['passing_count']}"]
    rec = result["recommendation"]
    if result["passing_count"]:
        lines.append(f"Recommended (least generous passing): {rec['setting']} -> Reef {rec['reef_completed_at']}")
    else:
        lines.append(f"Best-progress run (nothing passes, so no recommendation): {rec['setting']}")
    names = list(result["runs"][0]["setting"])
    lines += ["", "Single-lever runs (all other levers at base)", "setting | " + ROW_HEADER]
    for run in result["singles"]:
        changed = {n: run["setting"][n] for n, i in zip(names, run["levels"]) if i} or "base"
        lines.append(f"{changed} | {_row(run)}")
    for ladder in result["ladders"]:
        lines += ["", f"Cumulative: {ladder['name']}", "setting | " + ROW_HEADER]
        for run in ladder["steps"]:
            changed = {n: run["setting"][n] for n, i in zip(names, run["levels"]) if i} or "base"
            lines.append(f"{changed} | {_row(run)}")
    lines += ["", "Marginal effects (mean over all other parameters)"]
    for name, values in result["marginal_effects"].items():
        cells = "; ".join(f"{v}: pop {e['mean_final_population']}, symbiotic {e['runs_reaching_symbiotic']}/{e['runs']}, "
                          f"reef {e['runs_completing_reef']}/{e['runs']} (mean {e['mean_reef_minute']})"
                          for v, e in values.items())
        lines.append(f"  {name}: {cells}")
    lines += ["", f"Top {top} runs (passing first, least generous first)", "setting | gen | pass | " + ROW_HEADER]
    for run in result["runs"][:top]:
        lines.append(f"{run['setting']} | {run['generosity']} | {'PASS' if run['passes'] else ','.join(run['failures'])} | {_row(run)}")
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
