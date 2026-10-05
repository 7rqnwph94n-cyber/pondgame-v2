"""Unchanged provisional rules under the reference governor at 120/180/240 minutes."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from economy.engine.definitions import load_definitions, read_json
from economy.sweep import simulate, summarise
from economy.governor import summarise_log


def main():
    rows = []
    for minutes in (120, 180, 240):
        defs = load_definitions(overlays=[ROOT / "economy/data/experiments/candidate_playable_slice_v1.json"])
        defs["scenario"]["duration_seconds"] = minutes * 60
        sim, report, governor = simulate(defs, {"id": "extended_slice", "commands": []},
                                        read_json(ROOT / "economy/data/governors/reference_governor_v3.json"))
        row = {"horizon_minutes": minutes, **summarise(report),
               "enzyme_paid": report["maintenance_upkeep"]["enzyme_paid"],
               "surface_carbonate_left": sim.env.reserves.get("surface_carbonate"),
               "governor_failed_actions": summarise_log(governor)["failed_actions"],
               "events": report.get("events", [])}
        rows.append(row)
        print(json.dumps(row), flush=True)
    (ROOT / "docs/milestone_a/SLICE_EXTENDED_HORIZON_2026-10-05.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    main()
