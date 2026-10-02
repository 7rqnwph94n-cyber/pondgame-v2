"""Barter with the neighbouring settlement.

Goods sent leave the store at departure. Purchased goods and contract rewards
arrive physically when the caravan returns. Stored value is an ordinary good.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import floor
from typing import Any

from .inventory import Inventory


@dataclass
class Caravan:
    id: str
    departed_at: int
    arrives_at: int
    sent: dict[str, int]
    returning: dict[str, int]
    contract: str | None = None
    arrived: bool = False


@dataclass
class TradeState:
    defs: dict[str, Any]
    bought: dict[str, int] = field(default_factory=dict)
    sold: dict[str, int] = field(default_factory=dict)
    price_multipliers: dict[str, float] = field(default_factory=dict)
    contracts: dict[str, str] = field(default_factory=dict)   # id -> open|in_transit|completed|declined
    caravans: list[Caravan] = field(default_factory=list)

    def __post_init__(self) -> None:
        for contract_id in self.defs["trade"].get("contracts", {}):
            self.contracts.setdefault(contract_id, "open")

    @property
    def table(self) -> dict[str, Any]:
        return self.defs["trade"]

    def round_trip(self, season_id: str) -> int:
        return int(self.table["round_trip_seconds"] + self.table.get("season_extra_seconds", {}).get(season_id, 0))

    def partner_stock(self, resource: str, second: int) -> int:
        offer = self.table["partner_sells"].get(resource)
        if not offer:
            return 0
        accrued = min(float(offer["max"]), float(offer["per_minute"]) * second / 60.0)
        return max(0, int(floor(accrued + 1e-9)) - self.bought.get(resource, 0))

    def partner_demand(self, resource: str, second: int) -> int:
        """Units the partner will still buy now. Demand with ``per_minute`` accrues over time up to ``max``."""
        demand = self.table["partner_buys"].get(resource)
        if not demand:
            return 0
        cap = float(demand["max"])
        if demand.get("per_minute"):
            cap = min(cap, float(demand["per_minute"]) * second / 60.0)
        return max(0, int(floor(cap + 1e-9)) - self.sold.get(resource, 0))

    def buy_price(self, resource: str) -> float:
        return float(self.table["base_values"][resource]) * self.price_multipliers.get(resource, 1.0)

    def quote(self, sell: dict[str, int], buy: dict[str, int], second: int) -> tuple[float, float, list[str]]:
        problems: list[str] = []
        income = 0.0
        for resource, quantity in sell.items():
            demand = self.table["partner_buys"].get(resource)
            if not demand:
                problems.append(f"partner_does_not_buy:{resource}")
                continue
            if quantity > self.partner_demand(resource, second):
                problems.append(f"partner_demand_exhausted:{resource}")
            income += quantity * float(demand["price"])
        cost = 0.0
        for resource, quantity in buy.items():
            if resource not in self.table["partner_sells"]:
                problems.append(f"partner_does_not_sell:{resource}")
                continue
            if self.partner_stock(resource, second) < quantity:
                problems.append(f"partner_stock_insufficient:{resource}")
            cost += quantity * self.buy_price(resource)
        return income, cost, problems

    def barter(self, store: Inventory, sell: dict[str, int], buy: dict[str, int], second: int, season_id: str, caravan_id: str) -> tuple[bool, list[str]]:
        income, cost, problems = self.quote(sell, buy, second)
        missing = [f"insufficient_goods:{r}" for r, q in sell.items() if store.get(r) < q]
        problems += missing
        balance = store.get("stored_value") + income - cost
        if balance < -1e-9:
            problems.append(f"insufficient_value:short {-balance:.1f}")
        if problems:
            return False, problems
        store.take(sell)
        # Value settles at departure; fractional value from price modifiers is rounded against the player.
        net = income - cost
        if net >= 0:
            store.put({"stored_value": int(floor(net + 1e-9))})
        else:
            store.take({"stored_value": int(-floor(net + 1e-9))})
        for resource, quantity in sell.items():
            self.sold[resource] = self.sold.get(resource, 0) + quantity
        for resource, quantity in buy.items():
            self.bought[resource] = self.bought.get(resource, 0) + quantity
        self.caravans.append(Caravan(caravan_id, second, second + self.round_trip(season_id), dict(sell), dict(buy)))
        return True, []

    def deliver_contract(self, store: Inventory, contract_id: str, second: int, season_id: str, caravan_id: str) -> tuple[bool, list[str]]:
        contract = self.table["contracts"].get(contract_id)
        if contract is None:
            return False, [f"unknown_contract:{contract_id}"]
        if self.contracts[contract_id] != "open":
            return False, [f"contract_not_open:{self.contracts[contract_id]}"]
        trip = self.round_trip(season_id)
        deadline = contract.get("deadline")
        if deadline is not None and second + trip // 2 > deadline:
            return False, ["contract_deadline_passed"]
        deliver = {k: int(v) for k, v in contract["deliver"].items()}
        missing = [f"insufficient_goods:{r}" for r, q in deliver.items() if store.get(r) < q]
        if missing:
            return False, missing
        store.take(deliver)
        self.contracts[contract_id] = "in_transit"
        reward = {k: int(v) for k, v in contract.get("reward", {}).items()}
        self.caravans.append(Caravan(caravan_id, second, second + trip, deliver, reward, contract=contract_id))
        return True, []

    def decline(self, contract_id: str) -> tuple[bool, list[str]]:
        if self.contracts.get(contract_id) != "open":
            return False, [f"contract_not_open:{self.contracts.get(contract_id)}"]
        self.contracts[contract_id] = "declined"
        return True, []

    def step(self, store: Inventory, second: int, events: list[str], stamp: str) -> None:
        for caravan in self.caravans:
            if caravan.arrived or caravan.arrives_at > second:
                continue
            store.put(caravan.returning)
            caravan.arrived = True
            if caravan.contract:
                self.contracts[caravan.contract] = "completed"
                for resource, multiplier in self.table["contracts"][caravan.contract].get("price_multipliers", {}).items():
                    self.price_multipliers[resource] = self.price_multipliers.get(resource, 1.0) * multiplier
            events.append(f"{stamp} caravan {caravan.id} returned with {caravan.returning}")

    def in_transit(self) -> dict[str, int]:
        totals: dict[str, int] = {}
        for caravan in self.caravans:
            if not caravan.arrived:
                for resource, quantity in caravan.returning.items():
                    totals[resource] = totals.get(resource, 0) + quantity
        return totals
