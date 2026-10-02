"""Construction sites: material delivery, labour and commissioning.

Lifecycle: awaiting_materials -> awaiting_labour/in_progress -> complete.
A site may be cancelled at any time; delivered materials are refunded at the
configured rate (whole units, rounded down). Great Work stages are ordinary
sites with an additional Coordinator-work requirement.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from typing import Any

from .inventory import Inventory, missing_goods

EPS = 1e-9

AWAITING_MATERIALS = "awaiting_materials"
AWAITING_LABOUR = "awaiting_labour"
AWAITING_COORDINATORS = "awaiting_coordinators"
IN_PROGRESS = "in_progress"
COMPLETE = "complete"
CANCELLED = "cancelled"


@dataclass
class Site:
    id: str
    kind: str                 # "building" | "great_work_stage"
    target: str               # building definition id or great-work stage id
    district: str
    cost: dict[str, int]
    physical_work: float
    coordinator_work: float
    priority: int
    created_at: int
    order: int
    delivered: dict[str, int] = field(default_factory=dict)
    physical_done: float = 0.0
    coordinator_done: float = 0.0
    state: str = AWAITING_MATERIALS
    materials_complete_at: int | None = None
    last_material: str | None = None
    completed_at: int | None = None
    blocked_seconds: dict[str, float] = field(default_factory=dict)
    terms: dict[str, Any] | None = None   # effective building definition (first-instance terms applied)

    @property
    def active(self) -> bool:
        return self.state not in (COMPLETE, CANCELLED)

    def missing(self) -> dict[str, int]:
        return missing_goods(self.cost, self.delivered)

    def deliver_from(self, store: Inventory, second: int) -> None:
        if not self.active or self.materials_complete_at is not None:
            return
        for resource, quantity in self.missing().items():
            taken = store.take_up_to(resource, quantity)
            if taken:
                self.delivered[resource] = self.delivered.get(resource, 0) + taken
                self.last_material = resource
        if not self.missing():
            self.materials_complete_at = second
            self.state = AWAITING_LABOUR

    def physical_remaining(self) -> float:
        return max(0.0, self.physical_work - self.physical_done)

    def coordinator_remaining(self) -> float:
        return max(0.0, self.coordinator_work - self.coordinator_done)

    def apply_labour(self, physical_wp: float, coordinator_wp: float, dt: float) -> tuple[float, float]:
        """Apply labour (WP); return WP actually consumed (physical, coordinator)."""
        used_physical = used_coord = 0.0
        if self.materials_complete_at is None:
            return 0.0, 0.0
        need = self.physical_remaining()
        if need > EPS and physical_wp > EPS:
            work = min(need, physical_wp * dt / 60.0)
            self.physical_done += work
            used_physical = work * 60.0 / dt
        need = self.coordinator_remaining()
        if need > EPS and coordinator_wp > EPS:
            work = min(need, coordinator_wp * dt / 60.0)
            self.coordinator_done += work
            used_coord = work * 60.0 / dt
        return used_physical, used_coord

    def is_built(self) -> bool:
        return (
            self.materials_complete_at is not None
            and self.physical_remaining() <= EPS
            and self.coordinator_remaining() <= EPS
        )

    def wait_reason(self, physical_progress: bool, coordinator_progress: bool) -> list[str]:
        """Explain why the site did not progress this step (empty when it did)."""
        if self.materials_complete_at is None:
            return [f"{AWAITING_MATERIALS}:{resource}" for resource in self.missing()]
        reasons = []
        if self.physical_remaining() > EPS and not physical_progress:
            reasons.append(AWAITING_LABOUR)
        if self.coordinator_remaining() > EPS and not coordinator_progress:
            reasons.append(AWAITING_COORDINATORS)
        return reasons

    def cancel(self, store: Inventory, refund_rate: float) -> dict[str, int]:
        refunded = {resource: int(floor(quantity * refund_rate + EPS)) for resource, quantity in self.delivered.items()}
        refunded = {resource: quantity for resource, quantity in refunded.items() if quantity}
        store.put(refunded)
        self.delivered = {}
        self.state = CANCELLED
        return refunded


def salvage(cost: dict[str, Any], durable: set[str], rate: float) -> dict[str, int]:
    result = {
        resource: int(floor(int(quantity) * rate + EPS))
        for resource, quantity in cost.items()
        if resource in durable
    }
    return {resource: quantity for resource, quantity in result.items() if quantity}
