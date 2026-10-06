"""Loading, overlaying and validating economy definitions.

Definitions are plain JSON dictionaries keyed by stable string IDs. Overlays are
deep-merged on top of a base file so experiments never edit the accepted data.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable
import json

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_DEFINITIONS = DATA_DIR / "verdant_v0_2.json"
DEFAULT_PLAN = DATA_DIR / "plans" / "verdant_reference_a.json"


def read_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    """Return base updated by overlay. Dicts merge recursively; other values replace.

    A value of ``null`` in the overlay deletes the key.
    """
    result = deepcopy(base)
    for key, value in overlay.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_definitions(path: str | Path = DEFAULT_DEFINITIONS, overlays: Iterable[str | Path] = ()) -> dict[str, Any]:
    defs = read_json(path)
    applied = []
    for overlay_path in overlays:
        overlay = read_json(overlay_path)
        applied.append({"id": overlay.get("id", str(overlay_path)), "description": overlay.get("description", "")})
        defs = deep_merge(defs, overlay.get("patch", {}))
    defs["applied_overlays"] = applied
    errors = validate_definitions(defs)
    if errors:
        raise ValueError("Invalid economy definitions:\n" + "\n".join(errors))
    return defs


def load_plan(path: str | Path = DEFAULT_PLAN) -> dict[str, Any]:
    return read_json(path)


def _check_goods(errors: list[str], resources: set[str], owner: str, goods: dict[str, Any] | None) -> None:
    for resource, quantity in (goods or {}).items():
        if resource not in resources:
            errors.append(f"{owner}: unknown resource {resource}")
        elif not isinstance(quantity, (int, float)) or quantity <= 0:
            errors.append(f"{owner}: quantity for {resource} must be positive")


def validate_definitions(defs: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    resources = set(defs.get("resources", []))
    if not resources:
        errors.append("resources list is empty")
    classes = defs["workforce"]["classes"]
    if len(defs["workforce"]["substitution_efficiency"]) != len(classes):
        errors.append("workforce.substitution_efficiency must have one value per class")

    for recipe_id, recipe in defs.get("recipes", {}).items():
        if recipe.get("cycle_seconds", 0) <= 0:
            errors.append(f"recipe {recipe_id}: cycle_seconds must be positive")
        for direction in ("inputs", "outputs", "byproducts"):
            _check_goods(errors, resources, f"recipe {recipe_id} {direction}", recipe.get(direction))
        if not recipe.get("outputs"):
            errors.append(f"recipe {recipe_id}: has no outputs")
        factor = recipe.get("season_factor")
        if factor and any(factor not in season for season in defs["seasons"]):
            errors.append(f"recipe {recipe_id}: season factor {factor} missing from a season")
        for good in recipe.get("inputs", {}).values():
            if int(good) != good:
                errors.append(f"recipe {recipe_id}: inputs must be whole cargo units")

    party = defs.get("starting_state", {}).get("founding_party", {})
    if party:
        if party.get("tier") not in defs.get("residences", {}):
            errors.append("founding_party: unknown residence tier")
        if not isinstance(party.get("population"), int) or party["population"] <= 0:
            errors.append("founding_party: population must be a positive integer")
    services = defs.get("services", {})
    buildings = defs.get("buildings", {})
    for building_id, building in buildings.items():
        owner = f"building {building_id}"
        _check_goods(errors, resources, f"{owner} cost", building.get("cost"))
        first = building.get("first_instance")
        if first is not None:
            if "cost" in first:
                _check_goods(errors, resources, f"{owner} first_instance cost", first["cost"])
            for job_class in first.get("jobs", {}):
                if job_class not in classes:
                    errors.append(f"{owner}: first_instance unknown workforce class {job_class}")
        if building.get("constructible", True) and "work" not in building:
            errors.append(f"{owner}: constructible building needs work")
        for job_class in list(building.get("jobs", {})) + list(building.get("research_jobs", {})):
            if job_class not in classes:
                errors.append(f"{owner}: unknown workforce class {job_class}")
        for recipe_id in building.get("recipes", []):
            if recipe_id not in defs["recipes"]:
                errors.append(f"{owner}: unknown recipe {recipe_id}")
        if building.get("patch") and building["patch"] not in defs.get("patches", {}):
            errors.append(f"{owner}: unknown patch {building['patch']}")
        for key in ("requires_morphology",):
            if building.get(key) and building[key] not in defs["morphologies"]:
                errors.append(f"{owner}: unknown morphology {building[key]}")
        modifier = building.get("morphology_modifier")
        if modifier and modifier["morphology"] not in defs["morphologies"]:
            errors.append(f"{owner}: unknown morphology {modifier['morphology']}")
        if building.get("residence_tier") and building["residence_tier"] not in defs["residences"]:
            errors.append(f"{owner}: unknown residence tier")
        if "source" not in building:
            errors.append(f"{owner}: missing source/provenance")

    for service_id, service in services.items():
        for provider in service["provided_by"]:
            if provider not in buildings:
                errors.append(f"service {service_id}: unknown provider {provider}")

    tiers = defs["residence_rules"]["tier_order"]
    upkeep = defs.get("maintenance_upkeep", {})
    if upkeep.get("grace_until_tier") and upkeep["grace_until_tier"] not in tiers:
        errors.append("maintenance_upkeep: unknown grace_until_tier")
    if upkeep.get("service") and upkeep["service"] not in services:
        errors.append("maintenance_upkeep: unknown service")
    builder_class = defs.get("construction_rules", {}).get("builder_class")
    if builder_class and builder_class not in classes:
        errors.append("construction_rules: unknown builder_class")
    for residence_id, residence in defs["residences"].items():
        if residence_id not in tiers:
            errors.append(f"residence {residence_id}: missing from tier_order")
        if residence["class"] not in classes:
            errors.append(f"residence {residence_id}: unknown class")
        _check_goods(errors, resources, f"residence {residence_id} needs", residence.get("per_minute"))
        nxt = residence.get("next")
        if nxt and nxt not in defs["residences"]:
            errors.append(f"residence {residence_id}: unknown next tier {nxt}")
        evolution = residence.get("evolution")
        if evolution:
            _check_goods(errors, resources, f"residence {residence_id} evolution", evolution.get("goods"))
            for service_id in evolution.get("services", []):
                if service_id not in services:
                    errors.append(f"residence {residence_id}: unknown service {service_id}")
            morph = evolution.get("requires_morphology")
            if morph and morph not in defs["morphologies"]:
                errors.append(f"residence {residence_id}: unknown morphology {morph}")

    for morph_id, morph in defs.get("morphologies", {}).items():
        _check_goods(errors, resources, f"morphology {morph_id} research", morph.get("research_cost"))
        _check_goods(errors, resources, f"morphology {morph_id} express", morph.get("express_cost"))
        for tier in morph.get("expressed_by", []):
            if tier not in defs["residences"]:
                errors.append(f"morphology {morph_id}: unknown tier {tier}")

    trade = defs.get("trade", {})
    for table in ("partner_sells", "partner_buys"):
        for resource in trade.get(table, {}):
            if resource not in resources:
                errors.append(f"trade {table}: unknown resource {resource}")
    for contract_id, contract in trade.get("contracts", {}).items():
        _check_goods(errors, resources, f"contract {contract_id} deliver", contract.get("deliver"))
        _check_goods(errors, resources, f"contract {contract_id} reward", contract.get("reward"))

    for stage in defs["great_work"]["stages"]:
        _check_goods(errors, resources, f"great work stage {stage['id']}", stage["cost"])

    expected = 0
    for season in defs["seasons"]:
        if season["start"] != expected:
            errors.append(f"season {season['id']}: expected start {expected}")
        expected = season["end"]
    cycle = defs["scenario"].get("calendar_cycle_seconds")
    if cycle:
        if defs["seasons"][-1]["end"] != cycle:
            errors.append("calendar_cycle_seconds must equal the end of the last season")
    elif defs["seasons"][-1]["end"] <= defs["scenario"]["duration_seconds"]:
        errors.append("seasons do not cover the full scenario")

    for patch_id, patch in defs.get("patches", {}).items():
        if patch.get("reserve_cap") is not None:
            if patch.get("renewable"):
                errors.append(f"patch {patch_id}: reserve_cap needs a finite reserve")
            elif float(patch["reserve_cap"]) < float(patch.get("reserve", 0)):
                errors.append(f"patch {patch_id}: reserve_cap {patch['reserve_cap']} is below its starting reserve")
        for season_id in patch.get("season_deposits", {}):
            if season_id not in {s["id"] for s in defs["seasons"]}:
                errors.append(f"patch {patch_id}: unknown deposit season {season_id}")

    start = defs["starting_state"]
    _check_goods(errors, resources, "starting inventory", start["inventory"])
    seen: set[str] = set()
    for entry in start["buildings"] + start["residences"]:
        if entry["id"] in seen:
            errors.append(f"starting state: duplicate id {entry['id']}")
        seen.add(entry["id"])
    for entry in start["buildings"]:
        if entry["building"] not in buildings:
            errors.append(f"starting state: unknown building {entry['building']}")
    for entry in start["residences"]:
        if entry["tier"] not in defs["residences"]:
            errors.append(f"starting state: unknown residence tier {entry['tier']}")
    return errors


def first_instance_terms(definition: dict[str, Any]) -> dict[str, Any]:
    """Definition used by the first instance of a building: ``first_instance.cost``/``jobs`` replace the defaults."""
    override = definition.get("first_instance")
    if not override:
        return definition
    terms = {k: v for k, v in definition.items() if k != "first_instance"}
    for key in ("cost", "jobs"):
        if key in override:
            terms[key] = deepcopy(override[key])
    terms["first_instance_applied"] = True
    return terms


def is_provisional(entry: dict[str, Any]) -> bool:
    return "provisional" in str(entry.get("source", ""))
