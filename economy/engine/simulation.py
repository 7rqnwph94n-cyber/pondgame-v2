"""Deterministic fixed-step orchestrator for the honest headless economy.

One step is ``scenario.step_seconds`` of game time. Processing order per step
follows the dispatch priorities in the slice economy (§12.5):

1. environment (season deposits, patch renewal);
2. queued commands;
3. workforce allocation;
4. residence needs (refill, consume), decline and evolution;
5. construction and research material delivery, then labour;
6. production cycles;
7. trade arrivals;
8. population growth;
9. Great Work bookkeeping and diagnostics.
"""
from __future__ import annotations

import random
from typing import Any

from . import commands as command_module
from .construction import AWAITING_LABOUR, COMPLETE, IN_PROGRESS, Site
from .diagnostics import Diagnostics
from .environment import Environment
from .inventory import Inventory, add_goods
from .morphology import ResearchProject, capability
from .production import Facility
from .residences import NORMAL, Residence
from .trade import TradeState
from .workforce import Job, allocate

EPS = 1e-9


GRACE = "grace"
PAID = "paid"
UNPAID = "unpaid"
NOT_ENFORCED = "not_enforced"


class UpkeepState:
    """Maintenance upkeep (§13): Repair Enzyme per maintenance weight per minute.

    During the onboarding grace period nothing is charged. Afterwards a debt
    accrues each second; whole Enzyme units are paid from the store. While a
    unit is owed and unavailable, the Maintenance service is switched off
    (which blocks residence evolution). Debt is capped at one unit so
    resupply restores the service immediately rather than demanding back-pay.
    """

    def __init__(self, defs: dict[str, Any]):
        self.rules = defs.get("maintenance_upkeep", {})
        self.enforced = bool(self.rules.get("enforced", False))
        self.service = self.rules.get("service", "maintenance")
        self.state = GRACE if self.enforced else NOT_ENFORCED
        self.grace_ended_at: int | None = None
        self.debt = 0.0
        self.paid = 0
        self.unpaid_seconds = 0.0

    def _grace_over(self, sim: "Simulation") -> bool:
        tier = self.rules.get("grace_until_tier")
        if tier:
            order = sim.defs["residence_rules"]["tier_order"]
            if any(order.index(r.tier) >= order.index(tier) for r in sim.residences.values()):
                return True
        building = self.rules.get("grace_until_building")
        if building and any(f.building_id == building for f in sim.facilities.values()):
            return True
        limit = self.rules.get("grace_max_seconds")
        return limit is not None and sim.second >= int(limit)

    def step(self, sim: "Simulation") -> None:
        if not self.enforced:
            return
        if self.state == GRACE:
            if not self._grace_over(sim):
                return
            self.grace_ended_at = sim.second
            self.state = PAID
            sim.events.append(f"{stamp(sim.second)} maintenance upkeep begins")
        providers = sim.defs["services"][self.service]["provided_by"]
        if not any(f.building_id in providers and not f.paused for f in sim.facilities.values()):
            return
        rate = float(self.rules.get("enzyme_per_weight_per_minute", 1.0 / 80.0))
        self.debt = min(1.0, self.debt + sim.diag.maintenance_weight() * rate * sim.dt / 60.0)
        store = sim.store(sim.districts[0])
        if self.debt + EPS >= 1.0:
            if store.take_up_to("repair_enzyme", 1):
                self.debt -= 1.0
                self.paid += 1
                if self.state == UNPAID:
                    sim.events.append(f"{stamp(sim.second)} maintenance upkeep restored")
                self.state = PAID
            else:
                if self.state != UNPAID:
                    sim.events.append(f"{stamp(sim.second)} maintenance upkeep UNPAID: service suspended")
                self.state = UNPAID
                self.unpaid_seconds += sim.dt


# Builder allocation states (presentation/UI-facing, stable IDs)
BUILDERS_DISABLED = "disabled"
BUILDERS_IDLE = "idle"
BUILDERS_PROTECTED = "protected"
BUILDERS_PREEMPTED = "preempted_food_emergency"


class FoodEmergency:
    """Explicit food-emergency predicate (Rich, AGENT_CHAT 2026-10-02T15:18Z).

    Food minutes = (food held in stores + residence need buffers) / settlement consumption per minute.
    The emergency starts when food minutes fall below ``enter_below_minutes`` or (optionally) any residence
    runs short of the food good; it ends only when food minutes reach ``exit_above_minutes`` with no
    residence short (hysteresis, so the Builder allocation does not flicker).
    """

    def __init__(self, defs: dict[str, Any]):
        self.rules = defs.get("construction_rules", {}).get("food_emergency")
        self.active = False
        self.reason = ""
        self.food_minutes: float | None = None
        self.since: int | None = None
        self.seconds_active = 0.0
        self.episodes = 0

    def measure(self, sim: "Simulation") -> float | None:
        """Current settlement food minutes (None when nobody eats the food good)."""
        good = (self.rules or {}).get("good", "staple")
        held = sum(store.get(good) for store in sim.stores.values())
        held += sum(r.buffers.get(good, 0.0) for r in sim.residences.values())
        demand = 0.0
        for residence in sim.residences.values():
            definition = residence.definition(sim.defs)
            rate = definition["per_minute"].get(good, 0.0)
            demand += rate * min(1.0, residence.population / definition["capacity"])
        return held / demand if demand > EPS else None

    def update(self, sim: "Simulation") -> None:
        if not self.rules:
            return
        good = self.rules["good"]
        self.food_minutes = self.measure(sim)
        short = self.rules.get("enter_on_residence_shortage", True) and any(
            r.short_this_step and r.buffers.get(good, 0.0) <= EPS and good in r.definition(sim.defs)["per_minute"]
            for r in sim.residences.values())
        minutes = float("inf") if self.food_minutes is None else self.food_minutes
        if not self.active:
            if short or minutes < self.rules["enter_below_minutes"]:
                self.active, self.since = True, sim.second
                self.episodes += 1
                self.reason = (f"{good} shortage in a residence" if short
                               else f"{good} {minutes:.1f} min < {self.rules['enter_below_minutes']} min")
                sim.events.append(f"{stamp(sim.second)} FOOD EMERGENCY: builders pre-empted ({self.reason})")
        elif not short and minutes >= self.rules["exit_above_minutes"]:
            self.active, self.reason = False, ""
            sim.events.append(f"{stamp(sim.second)} food emergency over: builder allocation restored")
        if self.active:
            self.seconds_active += sim.dt


class GreatWorkState:
    def __init__(self) -> None:
        self.begun_at: int | None = None
        self.stage_index = 0
        self.site_id: str | None = None
        self.completed_at: int | None = None
        self.paused = False
        self.priority = 0


def stamp(second: int) -> str:
    return f"{second // 60:02d}:{second % 60:02d}"


class Simulation:
    def __init__(self, defs: dict[str, Any], plan: dict[str, Any] | None = None, seed: int | None = None):
        self.defs = defs
        self.plan = plan or {"id": "empty", "commands": []}
        scenario = defs["scenario"]
        self.seed = scenario.get("seed", 0) if seed is None else seed
        self.rng = random.Random(self.seed)  # reserved for stochastic rules; none are active in Milestone A
        self.dt = float(scenario.get("step_seconds", 1))
        self.duration = int(scenario["duration_seconds"])
        self.districts: list[str] = list(scenario["districts"])
        self.second = 0
        self.season = defs["seasons"][0]
        self.stores = {district: Inventory(defs["resources"]) for district in self.districts}
        self.env = Environment(defs)
        self.facilities: dict[str, Facility] = {}
        self.residences: dict[str, Residence] = {}
        self.sites: dict[str, Site] = {}
        self.research: list[ResearchProject] = []
        self.researched: dict[str, int] = {}
        self.trade = TradeState(defs)
        self.great_work = GreatWorkState()
        self.events: list[str] = []
        self.services: dict[str, set[str]] = {d: set() for d in self.districts}
        self.allocations: dict[str, Any] = {}
        self.construction_pool: dict[str, float] = {d: 0.0 for d in self.districts}
        self.coordinator_pool: dict[str, float] = {d: 0.0 for d in self.districts}
        rules = defs.get("construction_rules", {})
        self.policies: dict[str, float] = {
            "growth_nutrient_reserve": float(defs["population"]["nutrient_reserve"]),
            "builder_wp": float(rules.get("builder_wp", 0.0)),
        }
        self.first_instance_used: dict[str, str] = {}
        self.category_priority: dict[str, int] = {}   # player overrides for "construction"/"research" job ranks
        self.builder_wp: dict[str, float] = {d: 0.0 for d in self.districts}
        self.upkeep = UpkeepState(defs)
        self.food_emergency = FoodEmergency(defs)
        self.builder_state: dict[str, str] = {d: BUILDERS_DISABLED for d in self.districts}
        self.growth_progress = 0.0
        self.nutrient_credit = 0.0
        self.food_positive_since: int | None = 0
        self._order = 0
        self._id_counters: dict[str, int] = {}
        self.pending: list[command_module.PendingCommand] = []
        self.command_log: list[dict[str, Any]] = []
        self._queued = sorted(enumerate(self.plan.get("commands", [])), key=lambda item: (item[1]["at"], item[0]))
        self.diag = Diagnostics(self)
        self._load_starting_state()

    # ------------------------------------------------------------------ setup
    def next_order(self) -> int:
        self._order += 1
        return self._order

    def next_id(self, prefix: str) -> str:
        while True:
            self._id_counters[prefix] = self._id_counters.get(prefix, 0) + 1
            candidate = f"{prefix}_{self._id_counters[prefix]}"
            if not self.id_in_use(candidate):
                return candidate

    def id_in_use(self, entity_id: str) -> bool:
        return entity_id in self.facilities or entity_id in self.residences or entity_id in self.sites

    def store(self, district: str) -> Inventory:
        return self.stores[district]

    def _load_starting_state(self) -> None:
        start = self.defs["starting_state"]
        self.stores[self.districts[0]].put({k: int(v) for k, v in start["inventory"].items()})
        for entry in start["buildings"]:
            self._commission_facility(entry["id"], entry["building"], entry.get("district", self.districts[0]))
        for entry in start["residences"]:
            self.residences[entry["id"]] = Residence(
                id=entry["id"], tier=entry["tier"], district=entry.get("district", self.districts[0]),
                population=float(entry["population"]), created_at=0, order=self.next_order(),
            )

    def _commission_facility(self, facility_id: str, building_id: str, district: str, terms: dict[str, Any] | None = None) -> None:
        definition = terms or self.defs["buildings"][building_id]
        if definition.get("residence_tier"):
            self.residences[facility_id] = Residence(
                id=facility_id, tier=definition["residence_tier"], district=district,
                population=0.0, created_at=self.second, order=self.next_order(),
            )
        else:
            self.facilities[facility_id] = Facility(
                id=facility_id, building_id=building_id, district=district, definition=definition,
                commissioned_at=self.second, order=self.next_order(),
            )

    # --------------------------------------------------------------- queries
    def nursery_ids(self) -> list[str]:
        return [f.id for f in self.facilities.values() if f.definition.get("research_jobs")]

    def has_capability(self, district: str, morphology: str) -> bool:
        return capability(self.residences.values(), self.defs, district, morphology, self.second)

    def record_loss(self, facility_id: str, cause: str, detail: str, seconds: float) -> None:
        self.diag.record_loss(facility_id, cause, detail, seconds)

    def record_output(self, goods: dict[str, int]) -> None:
        for resource, quantity in goods.items():
            self.diag.produced[resource] = self.diag.produced.get(resource, 0) + int(quantity)

    def workforce_supply(self, district: str) -> dict[str, float]:
        supply = {c: 0.0 for c in self.defs["workforce"]["classes"]}
        for residence in self.residences.values():
            if residence.district == district:
                job_class, wp = residence.workforce(self.defs, self.second)
                supply[job_class] += wp
        return supply

    def active_research(self) -> ResearchProject | None:
        candidates = [p for p in self.research if p.active]
        return min(candidates, key=lambda p: (p.priority, p.order)) if candidates else None

    def great_work_blockers(self) -> list[str]:
        unlock = self.defs["great_work"]["unlock"]
        blockers = []
        if not any(r.tier == unlock["residence_tier"] for r in self.residences.values()):
            blockers.append(f"needs_residence:{unlock['residence_tier']}")
        min_staff = self.defs["workforce"]["min_staffing_fraction"]
        if not any(f.building_id == unlock["service_building"] and f.staffing >= min_staff for f in self.facilities.values()):
            blockers.append(f"needs_active_service:{unlock['service_building']}")
        coordinator_class = self.defs["workforce"]["great_work_coordinator_class"]
        # Coordinators covering lower-class vacancies can be recalled, so they count as available.
        available = sum(
            a.remaining.get(coordinator_class, 0.0) + a.below_class.get(coordinator_class, 0.0)
            for a in self.allocations.values())
        if available + EPS < unlock["coordinator_wp"]:
            blockers.append(f"needs_coordinator_wp:{available:.1f}/{unlock['coordinator_wp']}")
        status = self.trade.contracts.get(unlock["contract_resolved"])
        if status not in ("completed", "declined"):
            blockers.append(f"needs_contract_resolved:{unlock['contract_resolved']}={status}")
        positive = 0 if self.food_positive_since is None else self.second - self.food_positive_since
        if positive < unlock["food_positive_seconds"]:
            blockers.append(f"needs_food_reserve:{positive}/{unlock['food_positive_seconds']}s")
        return blockers

    def begin_great_work(self, priority: int) -> None:
        self.great_work.begun_at = self.second
        self.great_work.priority = priority
        self._open_great_work_stage()

    def _open_great_work_stage(self) -> None:
        stage = self.defs["great_work"]["stages"][self.great_work.stage_index]
        site_id = f"{self.defs['great_work']['id']}_{stage['id']}"
        self.sites[site_id] = Site(
            id=site_id, kind="great_work_stage", target=stage["id"], district=self.districts[0],
            cost={k: int(v) for k, v in stage["cost"].items()}, physical_work=float(stage["physical_work"]),
            coordinator_work=float(stage["coordinator_work"]), priority=self.great_work.priority,
            created_at=self.second, order=self.next_order(),
        )
        self.great_work.site_id = site_id
        self.events.append(f"{stamp(self.second)} Great Work stage {stage['id']} opened")

    # ------------------------------------------------------------------ steps
    def _process_commands(self) -> None:
        while self._queued and self._queued[0][1]["at"] <= self.second:
            index, cmd = self._queued.pop(0)
            if cmd.get("retry"):
                deadline = self.duration
            else:
                deadline = int(cmd.get("retry_until", cmd["at"]))
            self.pending.append(command_module.PendingCommand(index, cmd, self.second, deadline))
        still_pending = []
        for pending in self.pending:
            when = pending.command.get("when")
            if when and not pending.triggered:
                if command_module.unmet_conditions(self, when):
                    still_pending.append(pending)
                    continue
                pending.triggered = True
                pending.issued_at = self.second
                if not pending.command.get("retry"):
                    window = int(pending.command.get("retry_until", pending.command["at"])) - int(pending.command["at"])
                    pending.deadline = self.second + max(0, window)
            pending.attempts += 1
            result = command_module.execute(self, pending.command)
            if result.ok:
                self.command_log.append({
                    "index": pending.index, "do": pending.command["do"], "issued_at": pending.issued_at,
                    "executed_at": self.second, "ok": True, "info": result.info,
                    "label": pending.command.get("label", ""), "waited": dict(pending.waited),
                })
                self.events.append(f"{stamp(self.second)} {pending.command['do']} ok: {result.info}")
                continue
            pending.last_reasons = result.reasons
            if self.second < pending.deadline:
                for reason in result.reasons:
                    pending.waited[reason] = pending.waited.get(reason, 0.0) + self.dt
                still_pending.append(pending)
                continue
            self.command_log.append({
                "index": pending.index, "do": pending.command["do"], "issued_at": pending.issued_at,
                "executed_at": None, "failed_at": self.second, "ok": False, "reasons": result.reasons,
                "label": pending.command.get("label", ""), "waited": dict(pending.waited),
            })
            self.events.append(f"{stamp(self.second)} {pending.command['do']} FAILED: {', '.join(result.reasons)}")
        self.pending = still_pending

    def _allocate_workforce(self) -> None:
        workforce = self.defs["workforce"]
        priorities = {category: i for i, category in enumerate(workforce["job_priority"])}
        priorities.update(self.category_priority)
        research = self.active_research()
        research_ready = research is not None and research.materials_complete_at is not None
        for district in self.districts:
            jobs: list[Job] = []
            for facility in self.facilities.values():
                if facility.district != district or facility.paused:
                    continue
                rank = priorities.get(facility.category, len(priorities)) if facility.labour_priority is None else facility.labour_priority
                for job_class, required in facility.definition.get("jobs", {}).items():
                    jobs.append(Job(f"{facility.id}:{job_class}", facility.id, job_class, float(required), rank, facility.order))
                if research_ready:
                    for job_class, required in facility.definition.get("research_jobs", {}).items():
                        jobs.append(Job(f"{facility.id}#research:{job_class}", facility.id, job_class, float(required),
                                        priorities["research"], facility.order))
            coordinator_class = workforce["great_work_coordinator_class"]
            gw_need = self._great_work_coordinator_demand(district)
            if gw_need > EPS:
                jobs.append(Job(f"great_work@{district}", f"great_work@{district}", coordinator_class, gw_need,
                                priorities.get("great_work", -1), -2))
            builder_need = self._builder_demand(district)
            if builder_need > EPS:
                rules = self.defs.get("construction_rules", {})
                rank = priorities.get("construction", len(priorities))
                if self.food_emergency.active:
                    # Pre-empted: food crews are staffed first; builders keep only what is left over.
                    rank = max(rank, priorities.get("food", rank)) + 0.5
                    self.builder_state[district] = BUILDERS_PREEMPTED
                else:
                    self.builder_state[district] = BUILDERS_PROTECTED
            else:
                self.builder_state[district] = BUILDERS_DISABLED if self.policies.get("builder_wp", 0.0) <= EPS else BUILDERS_IDLE
            if builder_need > EPS:
                jobs.append(Job(f"builders@{district}", f"builders@{district}", rules.get("builder_class", "general"),
                                builder_need, rank, -1))
            allocation = allocate(self.workforce_supply(district), jobs, workforce["classes"], workforce["substitution_efficiency"])
            self.allocations[district] = allocation
            for facility in self.facilities.values():
                if facility.district != district:
                    continue
                facility.staffing = _weighted(allocation.staffing, facility, "jobs", ":")
                facility.research_staffing = _weighted(allocation.staffing, facility, "research_jobs", "#research:") if research_ready else 0.0
            self.builder_wp[district] = builder_need * allocation.staffing.get(f"builders@{district}", 0.0)
            self.construction_pool[district] = self.builder_wp[district] + sum(
                allocation.remaining[c] for c in workforce["construction_classes"])
            self.coordinator_pool[district] = gw_need * allocation.staffing.get(f"great_work@{district}", 0.0) + \
                allocation.remaining[coordinator_class]
            min_staff = workforce["min_staffing_fraction"]
            self.services[district] = {
                service_id for service_id, service in self.defs["services"].items()
                if any(f.district == district and f.building_id in service["provided_by"] and not f.paused and f.staffing >= min_staff
                       for f in self.facilities.values())
            }
            if self.upkeep.state == UNPAID:
                self.services[district].discard(self.upkeep.service)

    def _great_work_coordinator_demand(self, district: str) -> float:
        """While a stage is ready for Coordinator work, every Coordinator is claimed for it (top priority)."""
        site = self.sites.get(self.great_work.site_id) if self.great_work.site_id else None
        if (site is None or site.district != district or self.great_work.paused or site.materials_complete_at is None
                or site.coordinator_remaining() <= EPS):
            return 0.0
        return self.workforce_supply(district)[self.defs["workforce"]["great_work_coordinator_class"]]

    def _builder_demand(self, district: str) -> float:
        """Builders are reserved only while a site in this district is ready for physical work."""
        wanted = self.policies.get("builder_wp", 0.0)
        if wanted <= EPS:
            return 0.0
        ready = any(s.active and s.district == district and s.materials_complete_at is not None and s.physical_remaining() > EPS
                    and not (s.kind == "great_work_stage" and self.great_work.paused) for s in self.sites.values())
        return wanted if ready else 0.0

    def _residences_step(self) -> None:
        for residence in self.residences.values():
            residence.refill(self.defs, self.store(residence.district))
        for residence in self.residences.values():
            store = self.store(residence.district)
            residence.consume(self.defs, store, self.dt)
            if residence.short_this_step:
                self.diag.record_shortage(residence)
            residence.update_decline(self.defs, self.dt, self.events, stamp(self.second))
            if residence.evolution_target:
                morph = self.defs["residences"][residence.evolution_target]["evolution"].get("requires_morphology")
                has_morph = morph is None or (morph in residence.expressed.values() and self.second >= residence.conversion_until)
                blockers = residence.step_evolution(self.defs, store, self.services[residence.district], has_morph,
                                                    self.dt, self.events, stamp(self.second))
                self.diag.record_evolution_wait(residence.id, blockers)

    def _construction_step(self) -> None:
        active_sites = sorted((s for s in self.sites.values() if s.active), key=lambda s: (s.priority, s.order))
        claims: list[tuple[int, int, Any]] = [(s.priority, s.order, s) for s in active_sites]
        claims += [(p.priority, p.order, p) for p in self.research if p.active]
        for _, _, claimant in sorted(claims, key=lambda c: (c[0], c[1])):
            district = getattr(claimant, "district", self.districts[0])
            claimant.deliver_from(self.store(district), self.second)
        physical = dict(self.construction_pool)
        coordinator = dict(self.coordinator_pool)
        for site in active_sites:
            if site.kind == "great_work_stage" and self.great_work.paused:
                self.diag.record_site_wait(site, ["paused"])
                continue
            used_p, used_c = site.apply_labour(physical[site.district], coordinator[site.district], self.dt)
            physical[site.district] -= used_p
            coordinator[site.district] -= used_c
            self.diag.record_site_wait(site, site.wait_reason(used_p > EPS, used_c > EPS))
            if site.materials_complete_at is not None and used_p > EPS and site.physical_remaining() > EPS:
                # Trickle labour: progressing, but below a nominal crew. Weighted so that a site
                # crawling at 0.5 WP is reported almost as blocked as one with no labour at all.
                crew = float(self.defs["construction_rules"].get("diagnostic_nominal_crew_wp", 4.0))
                shortfall = max(0.0, 1.0 - used_p / crew)
                if shortfall > EPS:
                    self.diag.site_wait[site.id]["awaiting_labour"] += shortfall * self.dt
            if site.materials_complete_at is not None:
                site.state = IN_PROGRESS if (used_p > EPS or used_c > EPS) else AWAITING_LABOUR
            if site.is_built():
                site.state = COMPLETE
                site.completed_at = self.second
                self.diag.record_site_complete(site)
                if site.kind == "building":
                    self._commission_facility(site.id, site.target, site.district, site.terms)
                    self.events.append(f"{stamp(self.second)} commissioned {site.id} ({site.target})")
                else:
                    self._complete_great_work_stage(site)
        self.diag.idle_construction_wp += sum(physical.values()) * self.dt / 60.0

    def _complete_great_work_stage(self, site: Site) -> None:
        stages = self.defs["great_work"]["stages"]
        self.events.append(f"{stamp(self.second)} Great Work stage {site.target} complete")
        self.great_work.stage_index += 1
        if self.great_work.stage_index >= len(stages):
            self.great_work.completed_at = self.second
            self.great_work.site_id = None
            self.events.append(f"{stamp(self.second)} MEMORY REEF COMPLETE")
        else:
            self._open_great_work_stage()

    def _research_step(self) -> None:
        project = self.active_research()
        if project is None:
            return
        worked = False
        if project.materials_complete_at is not None:
            for facility in self.facilities.values():
                if facility.research_staffing > EPS:
                    wp = sum(facility.definition["research_jobs"].values()) * facility.research_staffing
                    project.work_done += wp * self.dt / 60.0
                    worked = True
        self.diag.record_research_wait(project, project.wait_reasons(worked))
        if project.work_done + EPS >= project.nursery_work:
            project.completed_at = self.second
            self.researched[project.morphology] = self.second
            self.events.append(f"{stamp(self.second)} morphology {project.morphology} researched")

    def _production_step(self) -> None:
        recipes = self.defs["recipes"]
        min_staff = self.defs["workforce"]["min_staffing_fraction"]
        for facility in list(self.facilities.values()):
            facility.step(recipes, self.season, self.env, self, min_staff, self.dt)

    def _population_step(self) -> None:
        rules = self.defs["population"]
        free = [r for r in sorted(self.residences.values(), key=lambda r: r.order)
                if r.population + 1.0 <= r.capacity(self.defs) + EPS and r.emigration_rate == 0.0]
        if not free:
            self.diag.record_growth_block("no_free_capacity")
            return
        if any(r.state != NORMAL for r in self.residences.values()):
            self.diag.record_growth_block("basic_needs_unsupplied")
            return
        rate = float(rules["migration_per_minute"])
        nursery = [f for f in self.facilities.values() if f.building_id == rules["nursery_building"]]
        if any(f.staffing >= self.defs["workforce"]["min_staffing_fraction"] for f in nursery):
            rate += float(rules["nursery_per_minute"])
        self.growth_progress = min(1.0, self.growth_progress + rate * self.dt / 60.0)
        if self.growth_progress + EPS < 1.0:
            return
        per = float(rules["nutrient_per_organism"])
        target = free[0]
        store = self.store(target.district)
        if self.nutrient_credit + EPS < per:
            if store.get("growth_nutrient") > int(self.policies["growth_nutrient_reserve"]):
                store.take({"growth_nutrient": 1})
                self.nutrient_credit += 1.0
            else:
                self.diag.record_growth_block("growth_nutrient_unavailable")
                return
        self.nutrient_credit -= per
        self.growth_progress -= 1.0
        target.population += 1.0
        self.diag.births += 1

    def _bookkeeping(self) -> None:
        food = self.defs["great_work"]["unlock"]["food_good"]
        if sum(store.get(food) for store in self.stores.values()) > 0:
            if self.food_positive_since is None:
                self.food_positive_since = self.second
        else:
            self.food_positive_since = None

    def step(self) -> None:
        self.season = self.env.season_at(self.second)
        self.env.step(self.second, self.dt)
        self._process_commands()
        self.upkeep.step(self)
        self.food_emergency.update(self)
        self._allocate_workforce()
        self._residences_step()
        self._construction_step()
        self._research_step()
        self._production_step()
        self.trade.step(self.store(self.districts[0]), self.second, self.events, stamp(self.second))
        self._population_step()
        self._bookkeeping()
        self.diag.record_step()
        self.second += int(self.dt)

    def run(self, until: int | None = None):
        end = self.duration if until is None else until
        while self.second <= end:
            self.step()
        for pending in self.pending:
            untriggered = bool(pending.command.get("when")) and not pending.triggered
            reasons = ["condition_never_met:" + ",".join(command_module.unmet_conditions(self, pending.command["when"]))] if untriggered else pending.last_reasons
            self.command_log.append({
                "index": pending.index, "do": pending.command["do"], "issued_at": pending.issued_at,
                "executed_at": None, "failed_at": None, "ok": False, "reasons": reasons,
                "label": pending.command.get("label", ""), "waited": dict(pending.waited), "still_pending": True,
            })
        return self.diag.build_report()

    # ------------------------------------------------------------ reporting
    def custody(self) -> dict[str, int]:
        """Every whole cargo unit in the settlement, wherever it is held."""
        totals: dict[str, int] = {}
        for store in self.stores.values():
            add_goods(totals, store.counts)
        for site in self.sites.values():
            if site.active:
                add_goods(totals, site.delivered)
        for project in self.research:
            if project.active:
                add_goods(totals, project.delivered)
        for facility in self.facilities.values():
            add_goods(totals, facility.held_inputs)
        for residence in self.residences.values():
            add_goods(totals, residence.evolution_reserved)
        add_goods(totals, self.trade.in_transit())
        return totals


def _weighted(staffing: dict[str, float], facility: Facility, key: str, separator: str) -> float:
    jobs = facility.definition.get(key, {})
    total = sum(jobs.values())
    if not total:
        return 1.0 if key == "jobs" else 0.0
    return sum(staffing.get(f"{facility.id}{separator}{c}", 0.0) * r for c, r in jobs.items()) / total
