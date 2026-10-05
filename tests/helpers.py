from __future__ import annotations

from pathlib import Path
from typing import Any

from economy.engine import Simulation, load_definitions, validate_definitions
from economy.engine.definitions import deep_merge

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "economy" / "data" / "experiments" / "probe_unblock_bootstrap.json"
LEGACY = ROOT / "economy" / "data" / "experiments" / "legacy_doc_faithful.json"


def make_defs(patch: dict[str, Any] | None = None, probe: bool = False, legacy: bool = True) -> dict[str, Any]:
    """Definitions for tests. ``legacy`` (default) reproduces the pre-promotion doc-faithful v0.2 that the
    Milestone A unit and characterisation tests were written against; ``legacy=False`` is the promoted baseline."""
    overlays = ([LEGACY] if legacy else []) + ([PROBE] if probe else [])
    defs = load_definitions(overlays=overlays)
    if patch:
        defs = deep_merge(defs, patch)
        errors = validate_definitions(defs)
        if errors:
            raise ValueError(errors)
    return defs


def make_sim(commands: list[dict[str, Any]] | None = None, patch: dict[str, Any] | None = None, probe: bool = False,
             legacy: bool = True) -> Simulation:
    return Simulation(make_defs(patch, probe, legacy), {"id": "test", "commands": commands or []})


def run_until(sim: Simulation, second: int) -> Simulation:
    while sim.second <= second:
        sim.step()
    return sim


def one_residence(tier: str, population: float) -> dict[str, Any]:
    return {"starting_state": {"residences": [{"id": "home_1", "tier": tier, "population": population, "district": "core"}]}}
