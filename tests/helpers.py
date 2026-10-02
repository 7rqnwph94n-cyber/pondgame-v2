from __future__ import annotations

from pathlib import Path
from typing import Any

from economy.engine import Simulation, load_definitions, validate_definitions
from economy.engine.definitions import deep_merge

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "economy" / "data" / "experiments" / "probe_unblock_bootstrap.json"


def make_defs(patch: dict[str, Any] | None = None, probe: bool = False) -> dict[str, Any]:
    defs = load_definitions(overlays=[PROBE] if probe else [])
    if patch:
        defs = deep_merge(defs, patch)
        errors = validate_definitions(defs)
        if errors:
            raise ValueError(errors)
    return defs


def make_sim(commands: list[dict[str, Any]] | None = None, patch: dict[str, Any] | None = None, probe: bool = False) -> Simulation:
    return Simulation(make_defs(patch, probe), {"id": "test", "commands": commands or []})


def run_until(sim: Simulation, second: int) -> Simulation:
    while sim.second <= second:
        sim.step()
    return sim


def one_residence(tier: str, population: float) -> dict[str, Any]:
    return {"starting_state": {"residences": [{"id": "home_1", "tier": tier, "population": population, "district": "core"}]}}
