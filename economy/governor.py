"""Adaptive reference governor: a deterministic, heuristic "competent player" used as a balance instrument.

Rich, AGENT_CHAT/exchange 2026-10-02T16:50Z: the governor "must react only to information and actions available
to a competent player, log its decisions and remain deterministic under a fixed seed/configuration". It is a
measuring instrument, not a production bonus and not the intended final player AI.

Boundaries enforced here:
- **Information:** every decision is made from ``observe(sim)``, a player view built from what the UI exposes
  (stores, facility/site/residence states, workforce summary, food minutes, calendar forecast, trade screen,
  research and Great Work status). The governor never reads engine internals directly.
- **Actions:** only legal player commands, issued through ``Simulation.issue`` (same checks as plan commands).
  It cannot bypass the food-emergency predicate and never changes the Builder allocation size.
- **Determinism:** fixed decision interval, ordered rules, sorted iteration, no randomness.

Configuration (``economy/data/governors/*.json``) holds thresholds and the build order, so the instrument's
behaviour is reviewable data, not hidden code.
"""
from __future__ import annotations

import json
from math import floor
from pathlib import Path
from typing import Any

from .engine.definitions import first_instance_terms, read_json

DEFAULT_GOVERNOR = Path(__file__).resolve().parent / "data" / "governors" / "reference_governor_v1.json"
FOOD_BUILDINGS = ("photosynthetic_field", "culture_bed")
STALL_STATES = ("no_input", "environment", "patch_depleted")


def load_governor_config(path: str | Path = DEFAULT_GOVERNOR) -> dict[str, Any]:
    return read_json(path)


# ---------------------------------------------------------------------------------------------- observation
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
        "residences": {r.id: {**r.presentation_state(defs, sim.services.get(r.district, set())), "order": r.order}
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


# ---------------------------------------------------------------------------------------------- governor
class Governor:
    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.interval = int(config.get("decision_interval_seconds", 10))
        self.log: list[dict[str, Any]] = []
        self.paused_by_me: dict[str, str] = {}      # facility id -> reason
        self.stalled_since: dict[str, int] = {}
        self.crisis_priority = False
        self.ranked_farms: set[str] = set()
        self.next_trade_at = 0
        self.started = False
        self._ids: dict[str, int] = {}

    # -------------------------------------------------------------- plumbing
    def _issue(self, sim, rule: str, cmd: dict[str, Any], reason: str) -> bool:
        result = sim.issue(cmd, source="governor")
        self.log.append({"t": sim.second, "rule": rule, "command": cmd, "reason": reason, "ok": result.ok,
                         "result": result.info if result.ok else result.reasons})
        return result.ok

    def _new_id(self, building: str, view: dict[str, Any]) -> str:
        existing = set(view["facilities"]) | set(view["sites"]) | set(view["residences"])
        n = self._ids.get(building, 0)
        while True:
            n += 1
            candidate = f"{building}_{n}"
            if candidate not in existing:
                self._ids[building] = n
                return candidate

    @staticmethod
    def _count(view: dict[str, Any], building: str) -> int:
        built = sum(1 for f in view["facilities"].values() if f["building"] == building)
        pending = sum(1 for s in view["sites"].values() if s["target"] == building and s["kind"] == "building")
        if building == "shelter":
            built = sum(1 for r in view["residences"].values())
        return built + pending

    @staticmethod
    def _built(view: dict[str, Any], building: str) -> int:
        if building == "shelter":
            return len(view["residences"])
        return sum(1 for f in view["facilities"].values() if f["building"] == building)

    def _consumption_per_minute(self, sim, view: dict[str, Any], good: str) -> float:
        total = 0.0
        for r in view["residences"].values():
            rate = sim.defs["residences"][r["tier"]]["per_minute"].get(good, 0.0)
            total += rate * min(1.0, r["population"] / r["capacity"])
        return total

    # -------------------------------------------------------------- main loop
    def act(self, sim) -> None:
        if sim.second % self.interval != 0:
            return
        view = observe(sim)
        if not self.started:
            self._opening(sim, view)
            self.started = True
            view = observe(sim)
        budget = int(self.config.get("max_actions_per_decision", 4))
        for rule in (self._food, self._idle_crews, self._housing, self._evolution, self._morphology,
                     self._build_order, self._kiln_fuel, self._trade, self._contracts, self._great_work):
            if budget <= 0:
                break
            budget -= rule(sim, view)
            if budget < int(self.config.get("max_actions_per_decision", 4)):
                view = observe(sim)

    def _opening(self, sim, view) -> None:
        for cmd, reason in (
            ({"do": "set_policy", "policy": "growth_nutrient_reserve", "value": self.config["growth_nutrient_reserve"]},
             "migrants may use Nutrient down to the configured reserve"),
        ):
            self._issue(sim, "opening", cmd, reason)
        for fid in self.config.get("pause_at_start", []):
            if fid in view["facilities"]:
                self._issue(sim, "opening", {"do": "pause", "target": fid}, "job finished at start (survey); frees a worker")

    # -------------------------------------------------------------- rules (each returns actions taken)
    def _food(self, sim, view) -> int:
        cfg = self.config["food"]
        minutes = view["food_minutes"] if view["food_minutes"] is not None else 99.0
        actions = 0
        # Forecast: entering a low-farm season soon raises the target.
        target = cfg["target_minutes"]
        farm_next = next(s for s in sim.defs["seasons"] if s["id"] == view["next_season"])["farm"]
        if view["seconds_to_next_season"] < cfg["forecast_seconds"] and farm_next < 0.8:
            target = cfg["target_minutes_before_lean_season"]
        fields = self._count(view, "photosynthetic_field")
        beds = self._count(view, "culture_bed")
        farm_sites = [s for s in view["sites"].values() if s["target"] in FOOD_BUILDINGS]
        food_vacancy = any(f["category"] == "food" and f["staffing"] < 0.99 and not f["paused"] and f["building"] in FOOD_BUILDINGS
                           for f in view["facilities"].values())
        if minutes < target and not farm_sites and not food_vacancy:
            building = "culture_bed" if beds < fields else "photosynthetic_field"
            if self._issue(sim, "food", {"do": "construct", "building": building, "id": self._new_id(building, view),
                                         "priority": cfg["site_priority"]},
                           f"food {minutes:.1f} min < target {target} (fields {fields}, beds {beds})"):
                actions += 1
        # Crisis: food crews outrank services and logistics until food recovers (a legal labour-priority setting).
        if minutes < cfg["crisis_minutes"]:
            self.crisis_priority = True
        elif minutes >= cfg["recovered_minutes"] and self.crisis_priority:
            self.crisis_priority = False
            for fid in sorted(self.ranked_farms):
                self._issue(sim, "food", {"do": "set_labour_priority", "target": fid, "value": None},
                            f"food recovered {minutes:.1f} min: default labour order")
            self.ranked_farms.clear()
            actions += 1
        if self.crisis_priority:
            for fid, f in sorted(view["facilities"].items()):
                if f["building"] in FOOD_BUILDINGS and fid not in self.ranked_farms:
                    if self._issue(sim, "food", {"do": "set_labour_priority", "target": fid, "value": 0},
                                   f"food crisis {minutes:.1f} min < {cfg['crisis_minutes']}: farms staffed first"):
                        self.ranked_farms.add(fid)
                        actions += 1
        return actions

    def _idle_crews(self, sim, view) -> int:
        cfg = self.config["idle_crews"]
        actions = 0
        protected = set(cfg.get("never_pause", []))
        for fid, f in sorted(view["facilities"].items()):
            if not f["recipes"] or f["building"] in protected:
                continue
            if fid in self.paused_by_me:
                if self._can_work(sim, view, f):
                    if self._issue(sim, "idle_crews", {"do": "resume", "target": fid}, f"inputs/conditions available again ({self.paused_by_me[fid]})"):
                        del self.paused_by_me[fid]
                        self.stalled_since.pop(fid, None)
                        actions += 1
                continue
            if f["paused"] or f["cycle_active"]:
                self.stalled_since.pop(fid, None)
                continue
            if f["status"] in STALL_STATES and f["staffing"] > 0:
                since = self.stalled_since.setdefault(fid, view["second"])
                if view["second"] - since >= cfg["pause_after_seconds"] and not self._can_work(sim, view, f):
                    reason = f"{f['status']} {f['detail']} for {view['second'] - since}s: release crew"
                    if self._issue(sim, "idle_crews", {"do": "pause", "target": fid}, reason):
                        self.paused_by_me[fid] = f"{f['status']} {f['detail']}".strip()
                        actions += 1
            else:
                self.stalled_since.pop(fid, None)
        return actions

    def _can_work(self, sim, view, f) -> bool:
        recipe = sim.defs["recipes"][f["recipe"]]
        season = sim.defs["seasons"][[s["id"] for s in sim.defs["seasons"]].index(view["season"])]
        factor = recipe.get("season_factor")
        if factor and season[factor] <= 0:
            return False
        if f["status"] == "patch_depleted":
            return False
        return all(view["store"].get(r, 0) >= q for r, q in recipe.get("inputs", {}).items())

    def _housing(self, sim, view) -> int:
        cfg = self.config["housing"]
        free = sum(r["capacity"] - r["population"] for r in view["residences"].values())
        shelter_sites = [s for s in view["sites"].values() if s["target"] == "shelter"]
        free += 8 * len(shelter_sites)
        minutes = view["food_minutes"] if view["food_minutes"] is not None else 99.0
        if free < cfg["min_free_capacity"] and not shelter_sites and minutes >= cfg["min_food_minutes"] \
                and len(view["residences"]) < cfg["max_residences"]:
            if self._issue(sim, "housing", {"do": "construct", "building": "shelter", "id": self._new_id("home", view),
                                            "priority": cfg["site_priority"]},
                           f"free housing {free:.0f} < {cfg['min_free_capacity']} and food {minutes:.1f} min"):
                return 1
        return 0

    def _evolution(self, sim, view) -> int:
        cfg = self.config["evolution"]
        if any(r["evolution"] for r in view["residences"].values()):
            return 0
        wf = view["workforce"]
        tiers = sim.defs["residence_rules"]["tier_order"]
        by_tier = {t: sorted((r for r in view["residences"].items() if r[1]["tier"] == t),
                             key=lambda item: (-item[1]["population"], item[1]["order"])) for t in tiers}
        counts = {t: len(by_tier[t]) for t in tiers}
        general_surplus = wf["general"]["supply"] - wf["general"]["demand"]
        adapted_surplus = wf["adapted"]["supply"] - wf["adapted"]["demand"]
        built = lambda b: self._built(view, b)
        candidates = []
        # Shelter -> Stable: Adapted work is waiting and the General workforce can spare a home.
        if (counts["stable"] < cfg["max_stable"] and by_tier["shelter"]
                and (wf["adapted"]["vacancies"] >= cfg["adapted_vacancy_trigger"] or counts["stable"] < cfg["min_stable"])
                and general_surplus >= cfg["general_surplus_required"] and counts["shelter"] > cfg["min_shelters"]):
            candidates.append(("shelter", "Adapted jobs waiting and General surplus available"))
        # Stable -> Symbiotic: Artisan work exists (or is about to), Gel can flow, Adapted can spare a home.
        if (counts["symbiotic"] < cfg["max_symbiotic"] and by_tier["stable"]
                and built("nutrient_kitchen") and built("detox_clinic") and built("distribution_node")
                and (wf["artisan"]["vacancies"] >= cfg["artisan_vacancy_trigger"] or counts["symbiotic"] == 0)
                and adapted_surplus >= cfg["adapted_surplus_required"]):
            candidates.append(("stable", "Artisan jobs waiting; Kitchen, Clinic and Distribution ready"))
        # Symbiotic -> Memory: Ganglion expressed and a Circle staffed.
        if counts["memory"] < cfg["max_memory"] and "memory_ganglion" in view["researched"] and built("memory_circle"):
            for rid, r in by_tier["symbiotic"]:
                if "memory_ganglion" in r["expressed_morphologies"].values():
                    return 1 if self._issue(sim, "evolution", {"do": "evolve", "residence": rid}, "Ganglion expressed and Memory Circle built") else 0
        for tier, reason in candidates:
            # Do not evolve homes that express an extraction morphology the city relies on.
            for rid, r in by_tier[tier]:
                if tier == "stable" and "extraction" in r["expressed_morphologies"]:
                    continue
                if r["population"] < r["capacity"] * cfg["min_occupancy"]:
                    continue
                if self._issue(sim, "evolution", {"do": "evolve", "residence": rid}, reason):
                    return 1
                break
        return 0

    def _morphology(self, sim, view) -> int:
        actions = 0
        for step in self.config["morphologies"]:
            morph = step["morphology"]
            if morph not in view["researched"] and morph not in view["research_queue"]:
                if all(self._built(view, b) for b in step.get("after_built", [])) and \
                        all(view["store"].get(r, 0) >= q for r, q in sim.defs["morphologies"][morph]["research_cost"].items()):
                    if self._issue(sim, "morphology", {"do": "research", "morphology": morph, "priority": 5},
                                   "research goods in stock and prerequisites built"):
                        actions += 1
            elif morph in view["researched"]:
                tiers = sim.defs["morphologies"][morph]["expressed_by"]
                expressed = [rid for rid, r in view["residences"].items() if morph in r["expressed_morphologies"].values() and r["tier"] in tiers]
                if len(expressed) < step.get("express_count", 1):
                    slot = sim.defs["morphologies"][morph]["slot"]
                    cost = sim.defs["morphologies"][morph]["express_cost"]
                    if all(view["store"].get(r, 0) >= q for r, q in cost.items()):
                        # Prefer homes of the right tier that are not being evolved and have the slot free.
                        options = sorted((rid for rid, r in view["residences"].items()
                                          if r["tier"] in tiers and slot not in r["expressed_morphologies"] and not r["evolution"]),
                                         key=lambda rid: -view["residences"][rid]["order"])
                        if options and self._issue(sim, "morphology", {"do": "express", "morphology": morph, "residence": options[0]},
                                                   f"{morph} researched; express on a home that stays {tiers[0]}"):
                            actions += 1
            if morph not in view["researched"]:
                break   # research one at a time, in order
        return actions

    def _next_cost(self, sim, view, building: str) -> dict[str, int]:
        """The cost the player is quoted for the next instance (first-instance terms while unused)."""
        definition = sim.defs["buildings"][building]
        if "first_instance" in definition and self._count(view, building) == 0:
            return first_instance_terms(definition).get("cost", {})
        return definition.get("cost", {})

    def _build_order(self, sim, view) -> int:
        cfg = self.config["build"]
        open_sites = [s for s in view["sites"].values() if s["kind"] == "building" and s["target"] not in ("shelter",) + FOOD_BUILDINGS]
        if len(open_sites) >= cfg["max_open_sites"]:
            return 0
        for step in self.config["build_order"]:
            building = step["building"]
            if self._count(view, building) >= step.get("count", 1):
                continue
            if "early_if_cost_only" in step:
                # Opportunistic step: take it only while the quoted cost uses nothing outside the listed goods.
                if not set(self._next_cost(sim, view, building)) <= set(step["early_if_cost_only"]):
                    continue
            if not all(self._built(view, b) >= 1 for b in step.get("after_built", [])):
                return 0
            if step.get("after_researched") and step["after_researched"] not in view["researched"]:
                return 0
            jobs = sim.defs["buildings"][building].get("jobs", {})
            for job_class in jobs:
                if view["workforce"][job_class]["vacancies"] > cfg["max_vacancies_before_new_jobs"] and not step.get("ignore_labour"):
                    return 0   # wait: staff what exists before adding jobs (housing/evolution rules address the shortage)
            label = step.get("why", "next in build order")
            return 1 if self._issue(sim, "build_order", {"do": "construct", "building": building,
                                                         "id": self._new_id(building, view), "priority": step.get("priority", 40)}, label) else 0
        return 0

    def _kiln_fuel(self, sim, view) -> int:
        actions = 0
        for fid, f in sorted(view["facilities"].items()):
            if f["building"] != "ceramic_kiln" or f["cycle_active"]:
                continue
            want = "ceramic_kiln" if view["store"].get("anoxic_organics", 0) >= 1 else "ceramic_kiln_biofuel"
            if f["recipe"] != want and self._issue(sim, "kiln_fuel", {"do": "set_recipe", "target": fid, "recipe": want},
                                                   "Anoxic Organics available" if want == "ceramic_kiln" else "no Anoxic Organics: biomass fuel"):
                actions += 1
        return actions

    def _carbonate_need(self, sim, view) -> int:
        missing = sum(s["missing"].get("carbonate", 0) for s in view["sites"].values())
        for step in self.config["build_order"]:
            if self._count(view, step["building"]) < step.get("count", 1):
                if "early_if_cost_only" in step and not set(self._next_cost(sim, view, step["building"])) <= set(step["early_if_cost_only"]):
                    continue
                missing += self._next_cost(sim, view, step["building"]).get("carbonate", 0)
                break
        if view["great_work"]["begun"]:
            missing += 4
        return max(0, missing - view["store"].get("carbonate", 0))

    def _trade(self, sim, view) -> int:
        cfg = self.config["trade"]
        if view["second"] < self.next_trade_at or not view["trade"]["open"]:
            return 0
        self.next_trade_at = view["second"] + cfg["interval_seconds"]
        need = self._carbonate_need(sim, view)
        stock = view["trade"]["partner_stock"].get("carbonate", 0)
        want = min(need, stock, cfg["max_carbonate_per_trade"])
        if want <= 0:
            return 0
        price = view["trade"]["buy_price"]["carbonate"]
        cost = want * price
        funds = view["store"].get("stored_value", 0)
        sell: dict[str, int] = {}
        minutes = view["food_minutes"] if view["food_minutes"] is not None else 99.0
        staple_per_minute = self._consumption_per_minute(sim, view, "staple")
        surpluses = []
        # Biomass is sold first (cheapest to replace); Staple only while food is comfortably secure.
        if minutes >= cfg["sell_food_above_minutes"] or cfg.get("sell_biomass_regardless_of_food"):
            surpluses.append(("biomass", view["store"].get("biomass", 0) - cfg["biomass_reserve_units"]))
        if minutes >= cfg["sell_food_above_minutes"]:
            keep = int(cfg["staple_reserve_minutes"] * staple_per_minute) + cfg["staple_reserve_units"]
            surpluses.append(("staple", view["store"].get("staple", 0) - keep))
        surpluses.append(("growth_nutrient", view["store"].get("growth_nutrient", 0) - cfg["growth_nutrient_reserve_units"]))
        surpluses.append(("prepared_silica", view["store"].get("prepared_silica", 0) - cfg["silica_reserve_units"]))
        for good, surplus in surpluses:
            if funds >= cost:
                break
            price_in = view["trade"]["sell_price"].get(good)
            demand = view["trade"]["partner_demand"].get(good, 0)
            if not price_in or surplus <= 0 or demand <= 0:
                continue
            qty = min(surplus, demand, int((cost - funds + price_in - 1e-9) // price_in) + 1)
            if qty > 0:
                sell[good] = qty
                funds += qty * price_in
        if funds < cost:
            want = int(floor(funds / price + 1e-9))
            if want <= 0:
                return 0
        reason = (f"Carbonate short by {need}; buying {want} at {price:.2f}; paying with "
                  f"{sell or 'stored value'} (food {minutes:.1f} min)")
        return 1 if self._issue(sim, "trade", {"do": "trade", "sell": sell, "buy": {"carbonate": want}}, reason) else 0

    def _contracts(self, sim, view) -> int:
        cfg = self.config["contracts"]
        status = view["trade"]["contracts"].get("fertile_exchange")
        if status != "open" or not view["trade"]["open"]:
            return 0
        deadline = sim.defs["trade"]["contracts"]["fertile_exchange"].get("deadline", 0)
        if view["store"].get("growth_nutrient", 0) >= 8 + cfg["fertile_exchange_keep_nutrient"] and view["second"] + 120 <= deadline:
            return 1 if self._issue(sim, "contracts", {"do": "deliver_contract", "contract": "fertile_exchange"},
                                    "8 Nutrient spare: deliver for 12 Carbonate and a lower price") else 0
        if view["second"] + 120 > deadline:
            return 1 if self._issue(sim, "contracts", {"do": "decline_contract", "contract": "fertile_exchange"},
                                    "cannot deliver before the deadline; resolve it so the Reef can unlock") else 0
        return 0

    def _great_work(self, sim, view) -> int:
        if view["great_work"]["begun"] or view["great_work"]["blockers"]:
            return 0
        return 1 if self._issue(sim, "great_work", {"do": "begin_great_work", "priority": 5}, "all unlock conditions met") else 0


def attach(sim, config: dict[str, Any] | None = None) -> Governor:
    governor = Governor(config or load_governor_config())
    sim.controllers.append(governor)
    return governor


def summarise_log(governor: Governor) -> dict[str, Any]:
    by_rule: dict[str, int] = {}
    for entry in governor.log:
        if entry["ok"]:
            by_rule[entry["rule"]] = by_rule.get(entry["rule"], 0) + 1
    build_order = [f"{entry['t'] // 60:02d}:{entry['t'] % 60:02d} {entry['command'].get('building')} ({entry['rule']})"
                   for entry in governor.log if entry["ok"] and entry["command"]["do"] == "construct"]
    return {"actions_by_rule": by_rule, "build_order": build_order,
            "failed_actions": sum(1 for e in governor.log if not e["ok"]), "decisions": len(governor.log)}
