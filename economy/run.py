"""Run the honest Milestone A economy and print an evidence report.

    python3 -m economy.run                       # doc-faithful definitions
    python3 -m economy.run --overlay economy/data/experiments/probe_unblock_bootstrap.json
    python3 -m economy.run --json reports/honest_run.json
    python3 -m economy.run --bootstrap-only
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import DEFAULT_DEFINITIONS, DEFAULT_PLAN, Simulation, load_definitions, load_plan
from .engine.bootstrap import analyse, format_analysis
from .engine.definitions import is_provisional


def format_report(defs: dict, report: dict, boot: dict, top: int = 5) -> str:
    lines: list[str] = []
    meta, outcome = report["meta"], report["outcome"]
    lines.append(f"Verdant Basin honest economy — {meta['scenario']} / plan {meta['plan']} / seed {meta['seed']}")
    for overlay in meta["overlays"]:
        lines.append(f"  OVERLAY {overlay['id']}: {overlay['description']}")
    provisional = sorted(b for b, d in defs["buildings"].items() if is_provisional(d))
    if provisional:
        lines.append(f"  provisional (undocumented) building values: {', '.join(provisional)}")
    lines.append("")
    lines.append(format_analysis(boot))
    lines.append("")
    done = outcome["great_work_completed_at"]
    lines.append(f"Memory Reef: {'completed at ' + done if done else 'NOT completed'}"
                 f" — stages {outcome['great_work_stages_complete']}/3, begun {outcome['great_work_begun_at'] or 'never'}")
    lines.append(f"Final population {outcome['final_population']}; residences {outcome['final_tiers']}")
    lines.append(f"Tier first reached: {outcome['tier_first_reached']}; morphologies researched: {outcome['researched'] or 'none'}")
    lines.append("")
    lines.append(f"Top {top} bottlenecks (blocked entity-minutes; see engine/diagnostics.py for the method)")
    for rank, item in enumerate(report["bottlenecks"][:top], 1):
        evidence = "; ".join(f"{e['item']} {e['minutes']}m" for e in item["top_evidence"][:3])
        lines.append(f"  {rank}. {item['key']:40s} {item['blocked_entity_minutes']:7.1f}  ({evidence})")
    lines.append("")
    path = report["great_work_critical_path"]
    lines.append("Great Work critical path")
    if path["unlock"]:
        lines.append(f"  never unlocked; blockers at end: {', '.join(path['unlock']['current_blockers'])}")
    for stage in path["stages"]:
        if stage.get("opened_at"):
            lines.append(f"  {stage['stage']}: opened {stage['opened_at']}, materials {stage['materials_complete_at'] or 'incomplete'}"
                         f" (last {stage['last_material']}), done {stage['completed_at'] or '-'}; material waits {stage['material_wait_minutes']}")
    lines.append("")
    unbuilt = [c for c in report["construction"] if not c["commissioned_at"]]
    if unbuilt:
        lines.append("Construction sites never commissioned")
        for site in unbuilt:
            lines.append(f"  {site['id']:18s} placed {site['placed_at']} missing {site['missing'] or '-'} waits {site['wait_minutes']}")
        lines.append("")
    failed = [c for c in report["commands"]["failed"] if not str(c.get("reasons", [""])[0]).startswith("condition_never_met")]
    untriggered = len(report["commands"]["failed"]) - len(failed)
    lines.append(f"Commands: {report['commands']['succeeded']} succeeded, {len(failed)} failed, {untriggered} never triggered (prerequisite never met)")
    for entry in failed:
        lines.append(f"  #{entry['index']} {entry['do']} {entry.get('label', '')}: {', '.join(entry['reasons'])}")
    lines.append("")
    lines.append("Production by recipes: " + ", ".join(f"{k} {v}" for k, v in report["produced_by_recipes"].items()))
    lines.append(f"Trade: {report['trade']}")
    lines.append(f"Workforce: {report['workforce']}")
    lines.append(f"Population growth blocked (minutes): {report['population_growth_blocked_minutes']}")
    lines.append(f"Not yet enforced (risk): {report['risks_not_enforced']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--definitions", type=Path, default=DEFAULT_DEFINITIONS)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--overlay", type=Path, action="append", default=[])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--json", type=Path, help="write the full report (with minute snapshots) as JSON")
    parser.add_argument("--bootstrap-only", action="store_true")
    parser.add_argument("--top", type=int, default=5)
    args = parser.parse_args()

    defs = load_definitions(args.definitions, args.overlay)
    boot = analyse(defs)
    if args.bootstrap_only:
        print(format_analysis(boot))
        return 0
    report = Simulation(defs, load_plan(args.plan), seed=args.seed).run()
    report["bootstrap"] = boot
    print(format_report(defs, report, boot, args.top))
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(report, indent=1), encoding="utf-8")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
