"""Commissioned buildings and their recipe cycles.

A facility reserves its full input batch at cycle start (goods leave the store
and are held by the facility), progresses according to staffing and
environment, and places outputs in the district store at cycle completion.
Each second that a facility does not progress at nominal rate is attributed to
a cause so diagnostics can explain lost production.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .inventory import Inventory

EPS = 1e-9

# Stall/loss cause identifiers. Stable strings: the presentation adapter and
# reports consume them.
NO_INPUT = "no_input"
NO_WORKFORCE = "no_workforce"
ENVIRONMENT = "environment"
PATCH_DEPLETED = "patch_depleted"
MORPHOLOGY_MISSING = "morphology_missing"
PAUSED = "paused"
RUNNING = "running"
IDLE = "idle"


class ProductionContext(Protocol):
    def store(self, district: str) -> Inventory: ...
    def has_capability(self, district: str, morphology: str) -> bool: ...
    def record_loss(self, facility_id: str, cause: str, detail: str, seconds: float) -> None: ...
    def record_output(self, goods: dict[str, int]) -> None: ...


@dataclass
class Facility:
    id: str
    building_id: str
    district: str
    definition: dict[str, Any]
    commissioned_at: int
    order: int
    recipe_id: str | None = None
    paused: bool = False
    labour_priority: int | None = None   # player override of the category default
    staffing: float = 0.0
    research_staffing: float = 0.0
    cycle_remaining: float | None = None
    held_inputs: dict[str, int] = field(default_factory=dict)
    completed_cycles: int = 0
    status: str = IDLE
    status_detail: str = ""

    def __post_init__(self) -> None:
        if self.recipe_id is None and self.definition.get("recipes"):
            self.recipe_id = self.definition["recipes"][0]

    @property
    def category(self) -> str:
        return self.definition["category"]

    def environment_factor(self, recipe: dict[str, Any], season: dict[str, Any], ctx: ProductionContext) -> tuple[float, str]:
        factor = 1.0
        detail = ""
        season_key = recipe.get("season_factor")
        if season_key:
            factor *= float(season[season_key]) * float(recipe.get("fertility", 1.0))
            detail = f"{season['id']}:{season_key}"
        modifier = self.definition.get("morphology_modifier")
        if modifier and not ctx.has_capability(self.district, modifier["morphology"]):
            without = modifier.get("without_by_season", {}).get(season["id"], modifier["without"])
            factor *= float(without)
            detail = (detail + "; " if detail else "") + f"without {modifier['morphology']}"
        return factor, detail

    def step(self, recipes: dict[str, Any], season: dict[str, Any], env, ctx: ProductionContext, min_staffing: float, dt: float) -> None:
        if not self.recipe_id:
            return
        recipe = recipes[self.recipe_id]
        # Spatial mode: the facility's own depot; otherwise the district store.
        store = ctx.local_store(self.id, self.district) if hasattr(ctx, "local_store") else ctx.store(self.district)

        def stall(cause: str, detail: str = "") -> None:
            self.status, self.status_detail = cause, detail
            ctx.record_loss(self.id, cause, detail, dt)

        if self.paused:
            return stall(PAUSED)
        required_morph = self.definition.get("requires_morphology")
        if required_morph and not ctx.has_capability(self.district, required_morph):
            return stall(MORPHOLOGY_MISSING, required_morph)
        if self.staffing < min_staffing - EPS:
            return stall(NO_WORKFORCE, f"staffing {self.staffing:.2f}")

        factor, env_detail = self.environment_factor(recipe, season, ctx)
        if self.cycle_remaining is None:
            if factor <= EPS:
                return stall(ENVIRONMENT, env_detail)
            patch = self.definition.get("patch")
            primary_qty = sum(recipe["outputs"].values())
            if not env.available(patch, primary_qty):
                return stall(PATCH_DEPLETED, patch or "")
            inputs = recipe.get("inputs", {})
            missing = store.first_missing(inputs)
            if missing is not None:
                return stall(NO_INPUT, missing)
            store.take(inputs)
            self.held_inputs = dict(inputs)
            env.extract(patch, primary_qty)
            self.cycle_remaining = float(recipe["cycle_seconds"])

        rate = self.staffing * factor
        if rate <= EPS:
            return stall(ENVIRONMENT, env_detail)
        self.status, self.status_detail = RUNNING, ""
        if self.staffing < 1.0 - EPS:
            ctx.record_loss(self.id, NO_WORKFORCE, f"staffing {self.staffing:.2f}", (1.0 - self.staffing) * dt)
        if factor < 1.0 - EPS:
            ctx.record_loss(self.id, ENVIRONMENT, env_detail, (1.0 - factor) * self.staffing * dt)
        self.cycle_remaining -= rate * dt
        if self.cycle_remaining <= EPS:
            store.put(recipe["outputs"])
            ctx.record_output(recipe["outputs"])
            self.completed_cycles += 1
            every = int(recipe.get("byproduct_every", 0))
            if every and self.completed_cycles % every == 0:
                store.put(recipe.get("byproducts", {}))
                ctx.record_output(recipe.get("byproducts", {}))
            self.held_inputs = {}
            self.cycle_remaining = None
