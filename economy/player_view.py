"""The player view: everything a player can see on the HUD, inspectors, calendar and trade screen.

Shared by the reference governor (which may act only on this) and the Godot client bridge.
"""
from __future__ import annotations

from typing import Any


def observe(sim) -> dict[str, Any]:
    """Player-visible state only (what the HUD, inspectors, Overseers, calendar and trade screen show)."""
    defs = sim.defs
    district = sim.districts[0]
    allocation = sim.allocations.get(district)
    supply = sim.workforce_supply(district)
    workforce = {
        c: {
            "supply": supply[c],
            "demand": allocation.demand[c] if allocation else 0.0,
            "vacancies": allocation.vacancies[c] if allocation else 0.0,
            "unassigned": allocation.remaining[c] if allocation else supply[c],
            "below_class": allocation.below_class[c] if allocation else 0.0,
        }
        for c in defs["workforce"]["classes"]
    }
    calendar_second = sim.env.calendar_second(sim.second)
    season = sim.env.season_at(sim.second)
    upcoming = [s for s in defs["seasons"] if s["start"] > calendar_second]
    following = upcoming[0] if upcoming else defs["seasons"][0]
    seconds_to_next = (following["start"] if upcoming else int(sim.env.cycle or season["end"])) - calendar_second
    trade = sim.trade
    return {
        "second": sim.second,
        "season": season["id"],
        "next_season": following["id"],
        "seconds_to_next_season": seconds_to_next,
        "store": dict(sim.store(district).counts),
        "food_minutes": sim.food_emergency.measure(sim),
        "food_emergency": sim.food_emergency.active,
        "workforce": workforce,
        "builders": sim.builder_state.get(district),
        "facilities": {
            f.id: {"building": f.building_id, "category": f.category, "status": f.status, "detail": f.status_detail,
                   "staffing": f.staffing, "paused": f.paused, "recipe": f.recipe_id, "cycle_active": f.cycle_remaining is not None,
                   "jobs": dict(f.definition.get("jobs", {})), "recipes": list(f.definition.get("recipes", []))}
            for f in sim.facilities.values()
        },
        "sites": {s.id: {"target": s.target, "kind": s.kind, "state": s.state, "missing": s.missing()}
                  for s in sim.sites.values() if s.active},
        "residences": {r.id: {**r.presentation_state(defs, sim.services_for(r)), "order": r.order}
                       for r in sim.residences.values()},
        "services": sorted(sim.services.get(district, set())),
        "researched": sorted(sim.researched),
        "research_queue": [p.morphology for p in sim.research if p.active],
        "trade": {
            "open": any(f.building_id == defs["trade"].get("requires_building") for f in sim.facilities.values()),
            "partner_stock": {r: trade.partner_stock(r, sim.second) for r in defs["trade"]["partner_sells"]},
            "partner_demand": {r: trade.partner_demand(r, sim.second) for r in defs["trade"]["partner_buys"]},
            "buy_price": {r: trade.buy_price(r) for r in defs["trade"]["partner_sells"]},
            "sell_price": {r: float(v["price"]) for r, v in defs["trade"]["partner_buys"].items()},
            "caravans_out": sum(1 for c in trade.caravans if not c.arrived),
            "contracts": dict(trade.contracts),
        },
        "great_work": {"begun": sim.great_work.begun_at is not None, "stage": sim.great_work.stage_index,
                       "blockers": sim.great_work_blockers() if sim.great_work.begun_at is None else []},
        "policies": dict(sim.policies),
    }
