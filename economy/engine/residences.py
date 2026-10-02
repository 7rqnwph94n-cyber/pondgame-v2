"""Residences: need buffers, decline, evolution and workforce supply.

Residence tier only changes through this module's rules:
- evolution: a requested target tier, service gates and full need buffers must
  hold for a sustain period while one-time goods stay reserved; goods are
  consumed when the timer completes;
- devolution: unresolved shortage escalates Strain -> Dormancy -> one tier down.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .inventory import Inventory, missing_goods

EPS = 1e-9

NORMAL = "normal"
STRAINED = "strained"
DORMANT = "dormant"


@dataclass
class Residence:
    id: str
    tier: str
    district: str
    population: float
    created_at: int
    order: int
    buffers: dict[str, float] = field(default_factory=dict)
    waste_accumulator: float = 0.0
    state: str = NORMAL
    state_seconds: float = 0.0        # time spent short in the current decline state
    recovery_seconds: float = 0.0     # consecutive supplied time while declined
    emigration_rate: float = 0.0
    evolution_target: str | None = None
    evolution_reserved: dict[str, int] = field(default_factory=dict)
    evolution_timer: float = 0.0
    expressed: dict[str, str] = field(default_factory=dict)   # slot -> morphology
    conversion_until: int = -1
    short_this_step: bool = False
    unmet: dict[str, float] = field(default_factory=dict)
    last_evolution_blockers: list[str] = field(default_factory=list)

    def definition(self, defs: dict[str, Any]) -> dict[str, Any]:
        return defs["residences"][self.tier]

    def workforce(self, defs: dict[str, Any], second: int) -> tuple[str, float]:
        definition = self.definition(defs)
        if second < self.conversion_until:
            return definition["class"], 0.0
        occupancy = min(1.0, self.population / definition["capacity"])
        wp = definition["workforce"] * occupancy
        if self.state == DORMANT:
            wp *= defs["residence_rules"]["dormancy_workforce_factor"]
        return definition["class"], wp

    def capacity(self, defs: dict[str, Any]) -> int:
        return int(self.definition(defs)["capacity"])

    def buffer_capacity(self, defs: dict[str, Any], resource: str) -> float:
        rate = self.definition(defs)["per_minute"][resource]
        return rate * defs["residence_rules"]["buffer_minutes"]

    def refill(self, defs: dict[str, Any], store: Inventory) -> None:
        for resource in self.definition(defs)["per_minute"]:
            level = self.buffers.get(resource, 0.0)
            if level < self.buffer_capacity(defs, resource) - EPS and store.take_up_to(resource, 1):
                self.buffers[resource] = level + 1.0

    def consume(self, defs: dict[str, Any], store: Inventory, dt: float) -> None:
        definition = self.definition(defs)
        occupancy = min(1.0, self.population / definition["capacity"])
        self.short_this_step = False
        if occupancy <= EPS:
            return
        for resource, rate in definition["per_minute"].items():
            amount = rate * occupancy * dt / 60.0
            level = self.buffers.get(resource, 0.0)
            if level + EPS >= amount:
                self.buffers[resource] = level - amount
            else:
                self.buffers[resource] = 0.0
                self.unmet[resource] = self.unmet.get(resource, 0.0) + amount - level
                self.short_this_step = True
        self.waste_accumulator += definition.get("waste_per_minute", 0.0) * occupancy * dt / 60.0
        whole = int(self.waste_accumulator + EPS)
        if whole:
            self.waste_accumulator -= whole
            store.put({"organic_waste": whole})

    def update_decline(self, defs: dict[str, Any], dt: float, events: list[str], stamp: str) -> None:
        rules = defs["residence_rules"]
        tiers = rules["tier_order"]
        if self.short_this_step:
            self.recovery_seconds = 0.0
            if self.state == NORMAL:
                self.state, self.state_seconds = STRAINED, 0.0
                events.append(f"{stamp} {self.id} strained")
            self.state_seconds += dt
            if self.state == STRAINED and self.state_seconds >= rules["strain_seconds"]:
                self.state, self.state_seconds = DORMANT, 0.0
                events.append(f"{stamp} {self.id} dormant")
            elif self.state == DORMANT and self.state_seconds >= rules["dormancy_seconds"]:
                index = tiers.index(self.tier)
                if index > 0:
                    old = self.tier
                    self.tier = tiers[index - 1]
                    capacity = self.capacity(defs)
                    if self.population > capacity:
                        self.emigration_rate = (self.population - capacity) / rules["emigration_seconds"]
                    self.buffers = {r: min(v, self.buffer_capacity(defs, r)) for r, v in self.buffers.items() if r in self.definition(defs)["per_minute"]}
                    self.state, self.state_seconds = STRAINED, 0.0
                    events.append(f"{stamp} {self.id} devolved {old} -> {self.tier}")
                else:
                    self.state_seconds = rules["dormancy_seconds"]  # floor tier: remains dormant
        elif self.state != NORMAL:
            self.recovery_seconds += dt
            needed = rules["strain_recovery_seconds"] if self.state == STRAINED else rules["dormancy_recovery_seconds"]
            if self.recovery_seconds >= needed:
                events.append(f"{stamp} {self.id} recovered from {self.state}")
                self.state, self.state_seconds, self.recovery_seconds = NORMAL, 0.0, 0.0
        if self.emigration_rate > 0:
            capacity = self.capacity(defs)
            self.population = max(float(capacity), self.population - self.emigration_rate * dt)
            if self.population <= capacity + EPS:
                self.emigration_rate = 0.0

    def presentation_state(self, defs: dict[str, Any], services: set[str]) -> dict[str, Any]:
        """Stable, presentation-safe view (requested by Codex for residence art states)."""
        definition = self.definition(defs)
        occupancy = self.population / definition["capacity"]
        needs = {}
        for resource, rate in definition["per_minute"].items():
            per_minute = rate * max(occupancy, 1e-9)
            needs[resource] = round(self.buffers.get(resource, 0.0) / per_minute, 2)
        evolving = None
        if self.evolution_target:
            sustain = defs["residences"][self.evolution_target]["evolution"]["sustain_seconds"]
            evolving = {
                "target_tier": self.evolution_target,
                "sustain_progress": round(min(1.0, self.evolution_timer / sustain), 3),
                "goods_reserved": dict(self.evolution_reserved),
                "blockers": list(self.last_evolution_blockers),
            }
        next_tier = definition.get("next")
        required = defs["residences"][next_tier]["evolution"].get("services", []) if next_tier else []
        return {
            "tier": self.tier,
            "condition": self.state,
            "population": round(self.population, 2),
            "capacity": definition["capacity"],
            "need_buffer_minutes": needs,
            "services_for_next_tier": {s: s in services for s in required},
            "evolution": evolving,
            "expressed_morphologies": dict(self.expressed),
        }

    def buffers_supplied(self, defs: dict[str, Any]) -> bool:
        return all(self.buffers.get(resource, 0.0) > EPS for resource in self.definition(defs)["per_minute"])

    def release_reservation(self, store: Inventory) -> None:
        if self.evolution_reserved:
            store.put(self.evolution_reserved)
            self.evolution_reserved = {}

    def evolution_blockers(self, defs: dict[str, Any], services: set[str], has_morph: bool) -> list[str]:
        definition = defs["residences"][self.evolution_target]
        evolution = definition["evolution"]
        blockers = [f"service:{s}" for s in evolution.get("services", []) if s not in services]
        morph = evolution.get("requires_morphology")
        if morph and not has_morph:
            blockers.append(f"morphology:{morph}")
        if self.state != NORMAL:
            blockers.append(f"residence_state:{self.state}")
        if not self.buffers_supplied(defs):
            blockers.append("needs_unsupplied")
        return blockers

    def step_evolution(self, defs: dict[str, Any], store: Inventory, services: set[str], has_morph: bool,
                       dt: float, events: list[str], stamp: str) -> list[str]:
        """Advance a requested evolution. Returns blocking reasons (empty if progressing or done)."""
        if not self.evolution_target:
            return []
        evolution = defs["residences"][self.evolution_target]["evolution"]
        blockers = self.evolution_blockers(defs, services, has_morph)
        self.last_evolution_blockers = list(blockers)
        if blockers:
            if self.evolution_timer > 0 or self.evolution_reserved:
                events.append(f"{stamp} {self.id} evolution interrupted ({', '.join(blockers)}); reservation released")
            self.release_reservation(store)
            self.evolution_timer = 0.0
            return blockers
        goods = {k: int(v) for k, v in evolution.get("goods", {}).items()}
        if not self.evolution_reserved:
            missing = missing_goods(goods, store.counts)
            if missing:
                self.last_evolution_blockers = [f"goods:{resource}" for resource in missing]
                return self.last_evolution_blockers
            store.take(goods)
            self.evolution_reserved = dict(goods)
        self.evolution_timer += dt
        if self.evolution_timer >= evolution["sustain_seconds"]:
            old = self.tier
            self.tier = self.evolution_target
            self.evolution_target = None
            self.evolution_reserved = {}   # consumed
            self.evolution_timer = 0.0
            self.last_evolution_blockers = []
            events.append(f"{stamp} {self.id} evolved {old} -> {self.tier}")
        return []
