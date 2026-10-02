from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


EPSILON = 1e-9


@dataclass
class RunningCycle:
    remaining: float = 0.0
    completed: int = 0


@dataclass
class GreatWorkState:
    stage_index: int = 0
    materials_paid: bool = False
    physical_work_remaining: float = 0.0
    coordinator_work_remaining: float = 0.0
    completed_at: int | None = None


@dataclass
class SimulationResult:
    duration_seconds: int
    inventory: dict[str, float]
    minimum_inventory: dict[str, float]
    shortages: dict[str, float]
    completed_cycles: dict[str, int]
    great_work_completed_at: int | None
    great_work_stage_index: int
    snapshots: list[dict[str, Any]] = field(default_factory=list)
    event_log: list[str] = field(default_factory=list)

    @property
    def completed(self) -> bool:
        return self.great_work_completed_at is not None


def load_config(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    resources = set(config.get("resources", []))
    if not resources:
        errors.append("resources list is empty")

    for recipe_id, recipe in config.get("recipes", {}).items():
        if recipe.get("cycle_seconds", 0) <= 0:
            errors.append(f"{recipe_id}: cycle_seconds must be positive")
        for direction in ("inputs", "outputs", "byproducts"):
            for resource, quantity in recipe.get(direction, {}).items():
                if resource not in resources:
                    errors.append(f"{recipe_id}: unknown {direction} resource {resource}")
                if quantity <= 0:
                    errors.append(f"{recipe_id}: {direction} quantity for {resource} must be positive")

    seasons = config.get("seasons", [])
    expected_start = 0
    for season in seasons:
        if season["start"] != expected_start:
            errors.append(f"season {season['id']}: expected start {expected_start}, got {season['start']}")
        if season["end"] <= season["start"]:
            errors.append(f"season {season['id']}: end must follow start")
        expected_start = season["end"]
    if seasons and seasons[-1]["end"] <= config["scenario"]["duration_seconds"]:
        errors.append("seasons do not cover the full scenario")

    for residence_id, residence in config.get("residences", {}).items():
        for resource in residence.get("per_minute", {}):
            if resource not in resources:
                errors.append(f"{residence_id}: unknown consumption resource {resource}")

    for stage in config.get("great_work", {}).get("stages", []):
        for resource in stage.get("cost", {}):
            if resource not in resources:
                errors.append(f"great work {stage['id']}: unknown resource {resource}")

    return errors


class EconomySimulation:
    def __init__(self, config: dict[str, Any]):
        errors = validate_config(config)
        if errors:
            raise ValueError("Invalid economy config:\n" + "\n".join(errors))
        self.config = config
        self.inventory = {resource: 0.0 for resource in config["resources"]}
        self.inventory.update({key: float(value) for key, value in config["scenario"]["starting_inventory"].items()})
        self.minimum_inventory = dict(self.inventory)
        self.shortages = {resource: 0.0 for resource in config["resources"]}
        self.facilities: dict[str, int] = {}
        self.residences: dict[str, int] = {}
        self.cycles: dict[tuple[str, int], RunningCycle] = {}
        self.great_work = GreatWorkState()
        self.event_log: list[str] = []
        self.snapshots: list[dict[str, Any]] = []

    def season_at(self, second: int) -> dict[str, Any]:
        for season in self.config["seasons"]:
            if season["start"] <= second < season["end"]:
                return season
        return self.config["seasons"][-1]

    def _can_pay(self, cost: dict[str, float]) -> bool:
        return all(self.inventory.get(resource, 0.0) + EPSILON >= quantity for resource, quantity in cost.items())

    def _pay(self, cost: dict[str, float]) -> None:
        for resource, quantity in cost.items():
            self.inventory[resource] -= quantity

    def _add(self, goods: dict[str, float]) -> None:
        for resource, quantity in goods.items():
            self.inventory[resource] += quantity

    def _apply_events(self, second: int) -> None:
        plan = self.config["reference_plan"]
        for event in plan["facility_events"]:
            if event["at"] == second:
                self.facilities.update({key: int(value) for key, value in event["set"].items()})
                self.event_log.append(f"{second // 60:02d}:{second % 60:02d} facilities {event['set']}")
        for event in plan["residence_events"]:
            if event["at"] == second:
                self.residences = {key: int(value) for key, value in event["set"].items()}
                self.event_log.append(f"{second // 60:02d}:{second % 60:02d} residences {event['set']}")
        for event in plan["inventory_events"]:
            if event["at"] != second:
                continue
            additions = event.get("add", {})
            removals = event.get("remove", {})
            self._add(additions)
            if removals:
                if self._can_pay(removals):
                    self._pay(removals)
                else:
                    for resource, quantity in removals.items():
                        available = max(0.0, self.inventory[resource])
                        paid = min(available, quantity)
                        self.inventory[resource] -= paid
                        self.shortages[resource] += quantity - paid
            self.event_log.append(f"{second // 60:02d}:{second % 60:02d} {event['label']}")

    def _effective_cycle_seconds(self, recipe: dict[str, Any], season: dict[str, Any]) -> float | None:
        factor_name = recipe.get("season_factor")
        if not factor_name:
            return float(recipe["cycle_seconds"])
        multiplier = float(season[factor_name]) * float(recipe.get("fertility", 1.0))
        if multiplier <= 0:
            return None
        return float(recipe["cycle_seconds"]) / multiplier

    def _run_facilities(self, season: dict[str, Any]) -> None:
        recipes = self.config["recipes"]
        active_keys: set[tuple[str, int]] = set()
        for recipe_id, count in self.facilities.items():
            recipe = recipes[recipe_id]
            for index in range(count):
                key = (recipe_id, index)
                active_keys.add(key)
                cycle = self.cycles.setdefault(key, RunningCycle())
                if cycle.remaining > 0:
                    cycle.remaining -= 1.0
                    if cycle.remaining <= EPSILON:
                        self._add(recipe.get("outputs", {}))
                        cycle.completed += 1
                        every = int(recipe.get("byproduct_every", 0))
                        if every and cycle.completed % every == 0:
                            self._add(recipe.get("byproducts", {}))
                    continue

                effective = self._effective_cycle_seconds(recipe, season)
                if effective is None:
                    continue
                inputs = recipe.get("inputs", {})
                if self._can_pay(inputs):
                    self._pay(inputs)
                    cycle.remaining = effective

        for key in list(self.cycles):
            if key not in active_keys and self.cycles[key].remaining <= 0:
                del self.cycles[key]

    def _consume_residences(self) -> None:
        per_second: dict[str, float] = {}
        waste_per_second = 0.0
        for residence_id, count in self.residences.items():
            definition = self.config["residences"][residence_id]
            for resource, rate in definition.get("per_minute", {}).items():
                per_second[resource] = per_second.get(resource, 0.0) + count * float(rate) / 60.0
            waste_per_second += count * float(definition.get("waste_per_minute", 0.0)) / 60.0

        for resource, demand in per_second.items():
            paid = min(max(0.0, self.inventory[resource]), demand)
            self.inventory[resource] -= paid
            self.shortages[resource] += demand - paid
        self.inventory["organic_waste"] += waste_per_second

    def _run_great_work(self, second: int) -> None:
        state = self.great_work
        plan = self.config["reference_plan"]
        stages = self.config["great_work"]["stages"]
        if second < plan["great_work_start"] or state.completed_at is not None:
            return
        if state.stage_index >= len(stages):
            state.completed_at = second
            return

        stage = stages[state.stage_index]
        if not state.materials_paid:
            if not self._can_pay(stage["cost"]):
                return
            self._pay(stage["cost"])
            state.materials_paid = True
            state.physical_work_remaining = float(stage["physical_work"])
            state.coordinator_work_remaining = float(stage["coordinator_work"])
            self.event_log.append(f"{second // 60:02d}:{second % 60:02d} Great Work stage {stage['id']} funded")

        state.physical_work_remaining = max(
            0.0, state.physical_work_remaining - plan["physical_workforce"] / 60.0
        )
        state.coordinator_work_remaining = max(
            0.0, state.coordinator_work_remaining - plan["coordinator_workforce"] / 60.0
        )
        if state.physical_work_remaining <= EPSILON and state.coordinator_work_remaining <= EPSILON:
            self.event_log.append(f"{second // 60:02d}:{second % 60:02d} Great Work stage {stage['id']} complete")
            state.stage_index += 1
            state.materials_paid = False
            if state.stage_index >= len(stages):
                state.completed_at = second

    def _record_snapshot(self, second: int) -> None:
        if second % 60 != 0:
            return
        self.snapshots.append(
            {
                "minute": second // 60,
                "season": self.season_at(second)["id"],
                "inventory": {key: round(value, 3) for key, value in self.inventory.items()},
                "facilities": dict(self.facilities),
                "residences": dict(self.residences),
                "great_work_stage": self.great_work.stage_index,
            }
        )

    def run(self) -> SimulationResult:
        duration = int(self.config["scenario"]["duration_seconds"])
        for second in range(duration + 1):
            self._apply_events(second)
            season = self.season_at(second)
            self._run_facilities(season)
            self._consume_residences()
            self._run_great_work(second)
            for resource, value in self.inventory.items():
                self.minimum_inventory[resource] = min(self.minimum_inventory[resource], value)
            self._record_snapshot(second)

        completed_cycles: dict[str, int] = {}
        for (recipe_id, _), cycle in self.cycles.items():
            completed_cycles[recipe_id] = completed_cycles.get(recipe_id, 0) + cycle.completed
        return SimulationResult(
            duration_seconds=duration,
            inventory=dict(self.inventory),
            minimum_inventory=dict(self.minimum_inventory),
            shortages={key: value for key, value in self.shortages.items() if value > 0.001},
            completed_cycles=completed_cycles,
            great_work_completed_at=self.great_work.completed_at,
            great_work_stage_index=self.great_work.stage_index,
            snapshots=list(self.snapshots),
            event_log=list(self.event_log),
        )


def workforce_at(config: dict[str, Any], residences: dict[str, int]) -> dict[str, int]:
    result: dict[str, int] = {}
    for residence_id, count in residences.items():
        definition = config["residences"][residence_id]
        workforce_class = definition["class"]
        result[workforce_class] = result.get(workforce_class, 0) + count * int(definition["workforce"])
    return result

