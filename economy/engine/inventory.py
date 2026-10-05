"""Discrete local inventories.

Every holder of goods (district store, construction site, production batch,
residence buffer, caravan) owns its own counts. A settlement-wide total is a
report computed from holders, never a shared pool.
"""
from __future__ import annotations

from typing import Iterable, Mapping


class InsufficientGoods(RuntimeError):
    pass


class Inventory:
    """Whole-unit goods held at one location."""

    def __init__(self, resources: Iterable[str], initial: Mapping[str, int] | None = None):
        self.counts: dict[str, int] = {resource: 0 for resource in resources}
        for resource, quantity in (initial or {}).items():
            self.put_one(resource, int(quantity))

    def get(self, resource: str) -> int:
        return self.counts.get(resource, 0)

    def put_one(self, resource: str, quantity: int) -> None:
        if quantity < 0 or int(quantity) != quantity:  # rejects fractional cargo
            raise ValueError(f"cannot store {quantity} {resource}: cargo must be whole and non-negative")
        if resource not in self.counts:
            raise KeyError(f"unknown resource {resource}")
        self.counts[resource] += int(quantity)

    def put(self, goods: Mapping[str, int]) -> None:
        for resource, quantity in goods.items():
            self.put_one(resource, quantity)

    def can_take(self, goods: Mapping[str, int]) -> bool:
        return all(self.get(resource) >= quantity for resource, quantity in goods.items())

    def first_missing(self, goods: Mapping[str, int]) -> str | None:
        for resource, quantity in goods.items():
            if self.get(resource) < quantity:
                return resource
        return None

    def take(self, goods: Mapping[str, int]) -> None:
        missing = self.first_missing(goods)
        if missing is not None:
            raise InsufficientGoods(f"need {goods[missing]} {missing}, have {self.get(missing)}")
        for resource, quantity in goods.items():
            self.counts[resource] -= int(quantity)

    def take_up_to(self, resource: str, quantity: int) -> int:
        taken = max(0, min(self.get(resource), int(quantity)))
        self.counts[resource] -= taken
        return taken

    def total_units(self, exclude: Iterable[str] = ()) -> int:
        skip = set(exclude)
        return sum(quantity for resource, quantity in self.counts.items() if resource not in skip)

    def nonzero(self) -> dict[str, int]:
        return {resource: quantity for resource, quantity in self.counts.items() if quantity}


def add_goods(target: dict[str, int], goods: Mapping[str, int]) -> None:
    for resource, quantity in goods.items():
        target[resource] = target.get(resource, 0) + int(quantity)


def missing_goods(required: Mapping[str, int], held: Mapping[str, int]) -> dict[str, int]:
    return {
        resource: int(quantity) - held.get(resource, 0)
        for resource, quantity in required.items()
        if held.get(resource, 0) < quantity
    }
