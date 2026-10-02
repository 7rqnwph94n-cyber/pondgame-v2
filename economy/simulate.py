from __future__ import annotations

import argparse
from dataclasses import asdict
from pathlib import Path
import json

from .model import EconomySimulation, load_config, validate_config, workforce_at


DEFAULT_CONFIG = Path(__file__).parent / "data" / "verdant_v0_1.json"


def format_time(seconds: int | None) -> str:
    if seconds is None:
        return "not completed"
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def print_report(config: dict, result) -> None:
    final_residences = result.snapshots[-1]["residences"]
    workforce = workforce_at(config, final_residences)
    print("Verdant Basin reference economy")
    print(f"Duration: {result.duration_seconds // 60} minutes")
    print(f"Great Work: {format_time(result.great_work_completed_at)}")
    print(f"Great Work stages complete: {result.great_work_stage_index}/3")
    print(f"Final residences: {final_residences}")
    print(f"Nominal workforce: {workforce}")
    print()
    print("Final strategic inventory")
    strategic = [
        "staple", "growth_nutrient", "balanced_gel", "carbonate",
        "prepared_silica", "fired_ceramic", "woven_fibre", "cured_resin",
        "habitat_composite", "repair_enzyme", "pigment_ornament"
    ]
    for resource in strategic:
        print(f"  {resource:22s} {result.inventory[resource]:8.2f}")
    print()
    if result.shortages:
        print("Unmet recurring/event demand")
        for resource, quantity in sorted(result.shortages.items()):
            print(f"  {resource:22s} {quantity:8.2f}")
    else:
        print("Unmet recurring/event demand: none")
    print()
    print("Completed production cycles")
    for recipe, cycles in sorted(result.completed_cycles.items()):
        print(f"  {recipe:22s} {cycles:5d}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Pondgame v2 Verdant economy reference plan")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--json", type=Path, help="write the complete result as JSON")
    args = parser.parse_args()

    config = load_config(args.config)
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 2

    result = EconomySimulation(config).run()
    print_report(config, result)
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(asdict(result), indent=2), encoding="utf-8")
        print(f"\nWrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

