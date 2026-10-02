"""Morphology research (Nursery institution work) and caste expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .inventory import Inventory, missing_goods

EPS = 1e-9


@dataclass
class ResearchProject:
    id: str
    morphology: str
    cost: dict[str, int]
    nursery_work: float
    priority: int
    created_at: int
    order: int
    delivered: dict[str, int] = field(default_factory=dict)
    work_done: float = 0.0
    materials_complete_at: int | None = None
    completed_at: int | None = None
    cancelled: bool = False

    @property
    def active(self) -> bool:
        return self.completed_at is None and not self.cancelled

    def missing(self) -> dict[str, int]:
        return missing_goods(self.cost, self.delivered)

    def deliver_from(self, store: Inventory, second: int) -> None:
        if not self.active or self.materials_complete_at is not None:
            return
        for resource, quantity in self.missing().items():
            taken = store.take_up_to(resource, quantity)
            if taken:
                self.delivered[resource] = self.delivered.get(resource, 0) + taken
        if not self.missing():
            self.materials_complete_at = second

    def wait_reasons(self, worked: bool) -> list[str]:
        if self.materials_complete_at is None:
            return [f"awaiting_materials:{resource}" for resource in self.missing()]
        return [] if worked else ["awaiting_nursery_work"]


def capability(residences, defs: dict[str, Any], district: str, morphology: str, second: int) -> bool:
    tiers = set(defs["morphologies"][morphology]["expressed_by"])
    for residence in residences:
        if residence.district != district or second < residence.conversion_until:
            continue
        if residence.tier in tiers and morphology in residence.expressed.values():
            return True
    return False
