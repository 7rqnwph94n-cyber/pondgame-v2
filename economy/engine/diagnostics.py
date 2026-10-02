"""Observability: every stall is attributed to a cause, and causes are ranked.

Bottleneck keys share one vocabulary across sources so different symptoms of
the same root cause add up:

- ``goods:<resource>``      material/input/need unavailable
- ``workforce:<class>``     jobs of that class unfilled
- ``labour:<kind>``         construction, coordinator or nursery work unavailable
- ``service:<id>``          evolution blocked by a missing service
- ``morphology:<id>``       a capability not yet expressed
- ``environment:<detail>``  season/patch access/adaptation penalty
- ``patch:<id>``            finite deposit exhausted
- other prefixes come from command reason codes (e.g. ``great_work_unlock``)

The unit is blocked entity-seconds: one second of one site, residence
evolution, research project, retrying command or facility not progressing.
"""
from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .simulation import Simulation

EPS = 1e-9


def _fmt(second: int | None) -> str | None:
    return None if second is None else f"{second // 60:02d}:{second % 60:02d}"


def bottleneck_key(source: str, reason: str, context: dict[str, Any] | None = None) -> str | None:
    head, _, tail = reason.partition(":")
    if head == "paused":
        return None  # a deliberate player choice, not a bottleneck
    if source == "loss":
        if head == "no_input":
            return f"goods:{tail}"
        if head == "no_workforce":
            return f"workforce:{(context or {}).get('job_class', '?')}"
        if head == "environment":
            return f"environment:{tail}"
        if head == "morphology_missing":
            return f"morphology:{tail}"
        if head == "patch_depleted":
            return f"patch:{tail}"
        return f"production:{head}"
    if head in ("awaiting_materials", "goods", "insufficient_goods"):
        return f"goods:{tail}"
    if head == "awaiting_labour":
        return "labour:construction"
    if head == "awaiting_coordinators":
        return "labour:coordinator"
    if head == "awaiting_nursery_work":
        return "labour:nursery"
    if head in ("service", "morphology"):
        return reason
    if head == "morphology_not_researched":
        return f"morphology:{tail}"
    if head in ("residence_state", "needs_unsupplied"):
        return "needs:residence_supply"
    if head.startswith("needs_"):
        return f"great_work_unlock:{head[6:]}"
    if head.startswith("partner_"):
        return f"trade:{head}:{tail}"
    return f"{source}:{head}"


class Diagnostics:
    def __init__(self, sim: "Simulation"):
        self.sim = sim
        self.lost: dict[str, dict[tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))
        self.site_wait: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.evolution_wait: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.research_wait: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.shortage_seconds: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self.growth_block: dict[str, float] = defaultdict(float)
        self.births = 0
        self.produced: dict[str, int] = {}
        self.below_class_wp_minutes: dict[str, float] = defaultdict(float)
        self.vacancy_wp_minutes: dict[str, float] = defaultdict(float)
        self.idle_construction_wp = 0.0      # WP-minutes of construction labour with nothing to build
        self.snapshots: list[dict[str, Any]] = []
        self.maintenance_weight_seconds = 0.0
        self.peak_store_units = 0
        self.store_over_capacity_seconds = 0.0
        self.tier_first_reached: dict[str, int] = {}
        self.completed_sites: list[dict[str, Any]] = []

    # ------------------------------------------------------------ recording
    def record_loss(self, facility_id: str, cause: str, detail: str, seconds: float) -> None:
        self.lost[facility_id][(cause, detail)] += seconds

    def record_site_wait(self, site, reasons: list[str]) -> None:
        for reason in reasons:
            self.site_wait[site.id][reason] += self.sim.dt

    def record_site_complete(self, site) -> None:
        self.completed_sites.append({
            "id": site.id, "kind": site.kind, "target": site.target, "created_at": site.created_at,
            "materials_complete_at": site.materials_complete_at, "last_material": site.last_material,
            "completed_at": site.completed_at,
        })

    def record_evolution_wait(self, residence_id: str, reasons: list[str]) -> None:
        for reason in reasons:
            self.evolution_wait[residence_id][reason] += self.sim.dt

    def record_research_wait(self, project, reasons: list[str]) -> None:
        for reason in reasons:
            self.research_wait[project.id][reason] += self.sim.dt

    def record_shortage(self, residence) -> None:
        for resource in self.sim.defs["residences"][residence.tier]["per_minute"]:
            if residence.buffers.get(resource, 0.0) <= EPS:
                self.shortage_seconds[residence.id][resource] += self.sim.dt

    def record_growth_block(self, reason: str) -> None:
        self.growth_block[reason] += self.sim.dt

    def maintenance_weight(self) -> float:
        sim = self.sim
        weight = sum(f.definition.get("maintenance_weight", 0.0) for f in sim.facilities.values())
        weight += sum(sim.defs["buildings"]["shelter"].get("maintenance_weight", 1.0) for _ in sim.residences.values())
        if sim.great_work.site_id and sim.great_work.site_id in sim.sites:
            weight += 3.0
        return weight

    def record_step(self) -> None:
        sim = self.sim
        self.maintenance_weight_seconds += self.maintenance_weight() * sim.dt
        for residence in sim.residences.values():
            self.tier_first_reached.setdefault(residence.tier, sim.second)
        for allocation in sim.allocations.values():
            for job_class, wp in allocation.below_class.items():
                self.below_class_wp_minutes[job_class] += wp * sim.dt / 60.0
            for job_class, wp in allocation.vacancies.items():
                self.vacancy_wp_minutes[job_class] += wp * sim.dt / 60.0
        for district in sim.districts:
            units = sim.store(district).total_units(exclude=("stored_value",))
            self.peak_store_units = max(self.peak_store_units, units)
            capacity = sum(f.definition.get("storage_capacity", 0) for f in sim.facilities.values() if f.district == district)
            if units > capacity:
                self.store_over_capacity_seconds += sim.dt
        if sim.second % 60 == 0:
            self.snapshots.append(self.snapshot())

    def snapshot(self) -> dict[str, Any]:
        sim = self.sim
        workforce = {}
        for district, allocation in sim.allocations.items():
            supply = sim.workforce_supply(district)
            workforce[district] = {
                job_class: {
                    "supply": round(supply[job_class], 2),
                    "employed": round(allocation.employed[job_class], 2),
                    "job_demand": round(allocation.demand[job_class], 2),
                    "vacancies": round(allocation.vacancies[job_class], 2),
                    "unassigned": round(allocation.remaining[job_class], 2),
                    "working_below_class": round(allocation.below_class[job_class], 2),
                }
                for job_class in sim.defs["workforce"]["classes"]
            }
        return {
            "minute": sim.second // 60,
            "season": sim.season["id"],
            "store": {d: s.nonzero() for d, s in sim.stores.items()},
            "custody": {k: v for k, v in sorted(sim.custody().items()) if v},
            "workforce": workforce,
            "population": round(sum(r.population for r in sim.residences.values()), 2),
            "residences": {r.id: r.presentation_state(sim.defs, sim.services.get(r.district, set()))
                           for r in sim.residences.values()},
            "maintenance_upkeep": sim.upkeep.state,
            "builders_wp": {d: round(v, 2) for d, v in sim.builder_wp.items()},
            "services": {d: sorted(s) for d, s in sim.services.items()},
            "facilities": {f.id: {"status": f.status, "detail": f.status_detail, "staffing": round(f.staffing, 2)}
                           for f in sim.facilities.values() if f.recipe_id},
            "sites": {s.id: {"target": s.target, "state": s.state, "missing": s.missing()}
                      for s in sim.sites.values() if s.active},
            "great_work_stage": sim.great_work.stage_index,
            "patch_reserves": {k: (None if v is None else round(v, 2)) for k, v in sim.env.reserves.items()},
        }

    # ------------------------------------------------------------- reporting
    def _job_class(self, facility_id: str) -> str:
        facility = self.sim.facilities.get(facility_id)
        if facility is None:
            return "?"
        return next(iter(facility.definition.get("jobs", {"?": 0})))

    def lost_production(self) -> dict[str, Any]:
        sim = self.sim
        by_building: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        values = sim.defs["trade"]["base_values"]
        total_value: dict[str, float] = defaultdict(float)
        for facility_id, causes in self.lost.items():
            facility = sim.facilities.get(facility_id)
            if facility is None or not facility.recipe_id:
                continue
            recipe = sim.defs["recipes"][facility.recipe_id]
            per_second = {r: q / recipe["cycle_seconds"] for r, q in recipe["outputs"].items()}
            for (cause, detail), seconds in causes.items():
                label = f"{cause}:{detail}" if detail and cause in ("no_input", "morphology_missing", "patch_depleted") else cause
                units = sum(rate * seconds for rate in per_second.values())
                by_building[facility.building_id][label] += units
                total_value[label] += sum(rate * seconds * values.get(r, 0) for r, rate in per_second.items())
        return {
            "units_by_building": {b: {c: round(u, 2) for c, u in sorted(v.items(), key=lambda i: -i[1])}
                                  for b, v in sorted(by_building.items())},
            "value_by_cause": {c: round(v, 1) for c, v in sorted(total_value.items(), key=lambda i: -i[1])},
        }

    def bottlenecks(self) -> list[dict[str, Any]]:
        totals: dict[str, float] = defaultdict(float)
        evidence: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))

        def add(key: str | None, item: str, seconds: float) -> None:
            if key is None or seconds <= EPS:
                return
            totals[key] += seconds
            evidence[key][item] += seconds

        for site_id, reasons in self.site_wait.items():
            for reason, seconds in reasons.items():
                add(bottleneck_key("site", reason), f"site {site_id}", seconds)
        for residence_id, reasons in self.evolution_wait.items():
            for reason, seconds in reasons.items():
                add(bottleneck_key("evolution", reason), f"evolution {residence_id}", seconds)
        for project_id, reasons in self.research_wait.items():
            for reason, seconds in reasons.items():
                add(bottleneck_key("research", reason), f"research {project_id}", seconds)
        for entry in self.sim.command_log:
            for reason, seconds in entry.get("waited", {}).items():
                add(bottleneck_key("command", reason), f"command #{entry['index']} {entry['do']}", seconds)
        add("goods:repair_enzyme", "maintenance upkeep unpaid (service suspended)", self.sim.upkeep.unpaid_seconds)
        for residence_id, goods in self.shortage_seconds.items():
            for resource, seconds in goods.items():
                add(f"goods:{resource}", f"residence {residence_id} need", seconds)
        for facility_id, causes in self.lost.items():
            for (cause, detail), seconds in causes.items():
                reason = f"{cause}:{detail}"
                add(bottleneck_key("loss", reason, {"job_class": self._job_class(facility_id)}), f"facility {facility_id}", seconds)
        ranked = sorted(totals.items(), key=lambda item: -item[1])
        return [
            {
                "key": key,
                "blocked_entity_minutes": round(seconds / 60.0, 1),
                "top_evidence": [
                    {"item": item, "minutes": round(s / 60.0, 1)}
                    for item, s in sorted(evidence[key].items(), key=lambda i: -i[1])[:5]
                ],
            }
            for key, seconds in ranked
        ]

    def critical_path(self) -> dict[str, Any]:
        sim = self.sim
        gw = sim.great_work
        stages = []
        for stage in sim.defs["great_work"]["stages"]:
            site_id = f"{sim.defs['great_work']['id']}_{stage['id']}"
            site = sim.sites.get(site_id)
            if site is None:
                stages.append({"stage": stage["id"], "opened_at": None})
                continue
            waits = self.site_wait.get(site_id, {})
            stages.append({
                "stage": stage["id"],
                "opened_at": _fmt(site.created_at),
                "materials_complete_at": _fmt(site.materials_complete_at),
                "last_material": site.last_material,
                "completed_at": _fmt(site.completed_at),
                "missing_now": site.missing() if site.active else {},
                "material_wait_minutes": {r.split(":", 1)[1]: round(s / 60, 1) for r, s in waits.items() if r.startswith("awaiting_materials")},
                "labour_wait_minutes": {r: round(s / 60, 1) for r, s in waits.items() if not r.startswith("awaiting_materials")},
                "physical_done": round(site.physical_done, 1),
                "coordinator_done": round(site.coordinator_done, 1),
            })
        begin = [e for e in sim.command_log if e["do"] == "begin_great_work"]
        pending = [p for p in sim.pending if p.command["do"] == "begin_great_work"]
        unlock = None
        if gw.begun_at is None:
            unlock = {
                "current_blockers": sim.great_work_blockers(),
                "waited_minutes": {r: round(s / 60, 1) for e in begin for r, s in e.get("waited", {}).items()}
                | {r: round(s / 60, 1) for p in pending for r, s in p.waited.items()},
            }
        return {"begun_at": _fmt(gw.begun_at), "completed_at": _fmt(gw.completed_at), "stages": stages, "unlock": unlock}

    def build_report(self) -> dict[str, Any]:
        sim = self.sim
        upkeep_demand = self.maintenance_weight_seconds / (10.0 * 8.0 * 60.0)
        enzyme_made = sum(
            f.completed_cycles * sim.defs["recipes"][f.recipe_id]["outputs"].get("repair_enzyme", 0)
            for f in sim.facilities.values() if f.recipe_id
        )
        sites = []
        for site in sim.sites.values():
            if site.kind != "building":
                continue
            sites.append({
                "id": site.id, "building": site.target, "placed_at": _fmt(site.created_at),
                "materials_complete_at": _fmt(site.materials_complete_at), "commissioned_at": _fmt(site.completed_at),
                "state": site.state, "missing": site.missing() if site.active else {},
                "work_progress": f"{site.physical_done:.1f}/{site.physical_work:.0f}",
                "wait_minutes": {r: round(s / 60, 1) for r, s in self.site_wait.get(site.id, {}).items()},
            })
        residences = {
            r.id: {
                "tier": r.tier, "population": round(r.population, 2), "state": r.state,
                "evolving_to": r.evolution_target, "expressed": dict(r.expressed),
                "evolution_wait_minutes": {k: round(v / 60, 1) for k, v in self.evolution_wait.get(r.id, {}).items()},
                "shortage_minutes": {k: round(v / 60, 1) for k, v in self.shortage_seconds.get(r.id, {}).items()},
                "unmet_units": {k: round(v, 2) for k, v in r.unmet.items()},
            }
            for r in sim.residences.values()
        }
        research = [
            {"morphology": p.morphology, "queued_at": _fmt(p.created_at), "materials_complete_at": _fmt(p.materials_complete_at),
             "completed_at": _fmt(p.completed_at), "missing": p.missing() if p.active else {},
             "wait_minutes": {k: round(v / 60, 1) for k, v in self.research_wait.get(p.id, {}).items()}}
            for p in sim.research
        ]
        failed = [e for e in sim.command_log if not e["ok"]]
        delayed = [e for e in sim.command_log if e["ok"] and e["executed_at"] != e["issued_at"]]
        return {
            "meta": {
                "scenario": sim.defs["scenario"]["id"],
                "overlays": sim.defs.get("applied_overlays", []),
                "plan": sim.plan.get("id"),
                "seed": sim.seed,
                "duration_seconds": sim.duration,
            },
            "outcome": {
                "great_work_completed_at": _fmt(sim.great_work.completed_at),
                "great_work_completed_seconds": sim.great_work.completed_at,
                "great_work_stages_complete": sim.great_work.stage_index,
                "great_work_begun_at": _fmt(sim.great_work.begun_at),
                "final_population": round(sum(r.population for r in sim.residences.values()), 2),
                "final_tiers": {t: sum(1 for r in sim.residences.values() if r.tier == t) for t in sim.defs["residence_rules"]["tier_order"]},
                "tier_first_reached": {t: _fmt(s) for t, s in self.tier_first_reached.items()},
                "researched": {m: _fmt(s) for m, s in sim.researched.items()},
                "births": self.births,
            },
            "bottlenecks": self.bottlenecks()[:12],
            "great_work_critical_path": self.critical_path(),
            "commands": {
                "failed": failed,
                "delayed": [{"index": e["index"], "do": e["do"], "label": e["label"], "issued_at": _fmt(e["issued_at"]),
                             "executed_at": _fmt(e["executed_at"]), "waited_minutes": {k: round(v / 60, 1) for k, v in e["waited"].items()}}
                            for e in delayed],
                "succeeded": sum(1 for e in sim.command_log if e["ok"]),
            },
            "construction": sites,
            "residences": residences,
            "research": research,
            "lost_production": self.lost_production(),
            "workforce": {
                "vacancy_wp_minutes": {k: round(v, 1) for k, v in self.vacancy_wp_minutes.items() if v > EPS},
                "working_below_class_wp_minutes": {k: round(v, 1) for k, v in self.below_class_wp_minutes.items() if v > EPS},
            },
            "population_growth_blocked_minutes": {k: round(v / 60, 1) for k, v in self.growth_block.items()},
            "maintenance_upkeep": {
                "enforced": sim.upkeep.enforced,
                "state": sim.upkeep.state,
                "grace_ended_at": _fmt(sim.upkeep.grace_ended_at),
                "enzyme_paid": sim.upkeep.paid,
                "unpaid_minutes": round(sim.upkeep.unpaid_seconds / 60, 1),
            },
            "risks_not_enforced": {
                "maintenance_enzyme_demand": round(upkeep_demand, 1),
                "repair_enzyme_produced": enzyme_made,
                "peak_store_units": self.peak_store_units,
                "store_over_capacity_minutes": round(self.store_over_capacity_seconds / 60, 1),
                "idle_construction_wp_minutes": round(self.idle_construction_wp, 1),
            },
            "produced_by_recipes": dict(sorted(self.produced.items())),
            "final_store": {d: s.nonzero() for d, s in sim.stores.items()},
            "patch_reserves": {k: (None if v is None else round(v, 2)) for k, v in sim.env.reserves.items()},
            "trade": {"sold": dict(sim.trade.sold), "bought": dict(sim.trade.bought), "contracts": dict(sim.trade.contracts)},
            "events": sim.events,
            "snapshots": self.snapshots,
        }
