"""Seasons and resource patches."""
from __future__ import annotations

from typing import Any


class Environment:
    """Seasons and patches.

    If ``scenario.calendar_cycle_seconds`` is set, the authored season list (which must cover exactly one
    cycle) repeats: at each multiple of the cycle the calendar wraps back to the first season, and seasonal
    deposits recur each cycle. Without it, the last season simply continues.
    """

    def __init__(self, defs: dict[str, Any]):
        self.seasons = defs["seasons"]
        self.cycle = defs.get("scenario", {}).get("calendar_cycle_seconds")
        self.patch_defs = defs.get("patches", {})
        # None marks a renewable patch with no finite reserve.
        self.reserves: dict[str, float | None] = {
            patch_id: (None if patch.get("renewable") else float(patch["reserve"]))
            for patch_id, patch in self.patch_defs.items()
        }
        self.deposit_log: list[tuple[int, str, float]] = []

    def calendar_second(self, second: int) -> int:
        return second % int(self.cycle) if self.cycle else second

    def cycle_index(self, second: int) -> int:
        return second // int(self.cycle) if self.cycle else 0

    def season_at(self, second: int) -> dict[str, Any]:
        second = self.calendar_second(second)
        for season in self.seasons:
            if season["start"] <= second < season["end"]:
                return season
        return self.seasons[-1]

    def step(self, second: int, dt: float) -> None:
        local = self.calendar_second(second)
        for season in self.seasons:
            if season["start"] == local:
                for patch_id, patch in self.patch_defs.items():
                    amount = patch.get("season_deposits", {}).get(season["id"])
                    if amount and self.reserves[patch_id] is not None:
                        self.reserves[patch_id] += float(amount)
                        self.deposit_log.append((second, patch_id, float(amount)))
        for patch_id, patch in self.patch_defs.items():
            renewal = patch.get("renewal_per_minute")
            if renewal and self.reserves[patch_id] is not None:
                self.reserves[patch_id] += float(renewal) * dt / 60.0

    def available(self, patch_id: str | None, quantity: float) -> bool:
        if patch_id is None:
            return True
        reserve = self.reserves[patch_id]
        return reserve is None or reserve + 1e-9 >= quantity

    def extract(self, patch_id: str | None, quantity: float) -> None:
        if patch_id is None or self.reserves[patch_id] is None:
            return
        self.reserves[patch_id] -= quantity
