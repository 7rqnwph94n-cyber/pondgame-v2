"""Player/plan commands.

Commands are requests, never state overwrites. Each returns a structured
result; failed commands carry machine-readable reason codes. A command with
``retry_until`` (absolute seconds) or ``retry: true`` is re-attempted every
step until it succeeds or the deadline passes, which models a player who keeps
trying; the time spent waiting is reported as diagnostics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .construction import Site, salvage
from .definitions import first_instance_terms
from .morphology import ResearchProject
from .residences import Residence

if TYPE_CHECKING:  # pragma: no cover
    from .simulation import Simulation

DEFAULT_PRIORITY = 50


@dataclass
class CommandResult:
    ok: bool
    reasons: list[str] = field(default_factory=list)
    info: str = ""


@dataclass
class PendingCommand:
    index: int
    command: dict[str, Any]
    issued_at: int
    deadline: int
    attempts: int = 0
    triggered: bool = False
    last_reasons: list[str] = field(default_factory=list)
    waited: dict[str, float] = field(default_factory=dict)


def unmet_conditions(sim: "Simulation", when: dict[str, Any]) -> list[str]:
    """Plan triggers: every listed condition must hold before the command is attempted.

    - built: entity id (facility or residence) or list of ids
    - tier: [residence_id, minimum tier]
    - researched: morphology id
    - contract: [contract id, [acceptable statuses]]
    - stock: {resource: minimum units in the first district store}
    - stock_below: {resource: units}; holds while the store has fewer than that many
    - food_minutes_below / food_minutes_above: n (settlement food minutes, as the food-emergency predicate)
    - vacancies_below: {class: wp}; holds while unfilled jobs of that class total less than wp
    - free_housing_below: n (empty homes plus homes under construction hold fewer than n organisms)
    """
    unmet: list[str] = []
    built = when.get("built")
    for entity_id in ([built] if isinstance(built, str) else built or []):
        if entity_id not in sim.facilities and entity_id not in sim.residences:
            unmet.append(f"built:{entity_id}")
    if "tier" in when:
        residence_id, tier = when["tier"]
        order = sim.defs["residence_rules"]["tier_order"]
        residence = sim.residences.get(residence_id)
        if residence is None or order.index(residence.tier) < order.index(tier):
            unmet.append(f"tier:{residence_id}>={tier}")
    if "researched" in when and when["researched"] not in sim.researched:
        unmet.append(f"researched:{when['researched']}")
    if "contract" in when:
        contract_id, statuses = when["contract"]
        if sim.trade.contracts.get(contract_id) not in statuses:
            unmet.append(f"contract:{contract_id}")
    if "free_housing_below" in when:
        free = sum(r.capacity(sim.defs) - r.population for r in sim.residences.values())
        free += sum(sim.defs["residences"][sim.defs["buildings"][s.target]["residence_tier"]]["capacity"]
                    for s in sim.sites.values()
                    if s.active and s.kind == "building" and sim.defs["buildings"][s.target].get("residence_tier"))
        if free >= when["free_housing_below"]:
            unmet.append(f"free_housing:{free:.0f}>={when['free_housing_below']}")
    if "food_minutes_below" in when or "food_minutes_above" in when:
        minutes = sim.food_emergency.measure(sim)
        minutes = float("inf") if minutes is None else minutes
        if "food_minutes_below" in when and minutes >= when["food_minutes_below"]:
            unmet.append(f"food_minutes<{when['food_minutes_below']}")
        if "food_minutes_above" in when and minutes <= when["food_minutes_above"]:
            unmet.append(f"food_minutes>{when['food_minutes_above']}")
    for job_class, maximum in when.get("vacancies_below", {}).items():
        vacant = sum(a.vacancies.get(job_class, 0.0) for a in sim.allocations.values())
        if vacant >= maximum:
            unmet.append(f"vacancies:{job_class}<{maximum}")
    store = sim.store(sim.districts[0])
    for resource, minimum in when.get("stock", {}).items():
        if store.get(resource) < minimum:
            unmet.append(f"stock:{resource}>={minimum}")
    for resource, maximum in when.get("stock_below", {}).items():
        if store.get(resource) >= maximum:
            unmet.append(f"stock:{resource}<{maximum}")
    return unmet


def fail(*reasons: str) -> CommandResult:
    return CommandResult(False, list(reasons))


def _district(sim: "Simulation", cmd: dict[str, Any]) -> str | None:
    district = cmd.get("district", sim.districts[0])
    return district if district in sim.districts else None


def cmd_construct(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    building_id = cmd.get("building")
    definition = sim.defs["buildings"].get(building_id)
    if definition is None:
        return fail(f"unknown_building:{building_id}")
    if not definition.get("constructible", True):
        return fail(f"not_constructible:{building_id}")
    district = _district(sim, cmd)
    if district is None:
        return fail(f"unknown_district:{cmd.get('district')}")
    site_id = cmd.get("id")
    if not site_id and not (sim.spatial is not None and cmd.get("dry_run")):
        site_id = sim.next_id(building_id)
    if site_id and sim.id_in_use(site_id):
        return fail(f"duplicate_id:{site_id}")
    placement = None
    if sim.spatial is not None:
        # Strict roads (Rich 2026-10-06): every building has a position and joins the anchor's network.
        if cmd.get("position") is None:
            return fail("spatial:position_required")
        try:
            position = (float(cmd["position"][0]), float(cmd["position"][1]))
            yaw = float(cmd.get("yaw", 0.0))
            footprint = sim.spatial.footprint_for(building_id, cmd.get("footprint"))
        except (TypeError, ValueError, IndexError, KeyError):
            return fail("spatial:malformed_position")
        entrance, reasons = sim.spatial.validate_building(position, yaw, footprint)
        if entrance is None:
            return fail(*reasons)
        placement = (position, yaw, footprint, entrance)
        if cmd.get("dry_run"):   # v4: authoritative preview, nothing is created or paid
            return CommandResult(True, info=f"valid {building_id} placement")
    # First-instance terms apply once per settlement; a cancelled first site releases them.
    first = "first_instance" in definition and building_id not in sim.first_instance_used
    terms = first_instance_terms(definition) if first else definition
    if first:
        sim.first_instance_used[building_id] = site_id
    site = Site(
        id=site_id, kind="building", target=building_id, district=district,
        cost={k: int(v) for k, v in terms.get("cost", {}).items()},
        physical_work=float(terms["work"]), coordinator_work=0.0,
        priority=int(cmd.get("priority", DEFAULT_PRIORITY)), created_at=sim.second, order=sim.next_order(),
        terms=terms,
    )
    sim.sites[site_id] = site
    if placement is not None:
        sim.spatial.place(site_id, *placement)
    return CommandResult(True, info=f"site {site_id} placed")


def cmd_cancel(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    target = cmd.get("target")
    site = sim.sites.get(target)
    if site is None or not site.active:
        return fail(f"no_active_site:{target}")
    if site.kind == "great_work_stage":
        sim.great_work.paused = True
    # Spatial mode: the refund stays at the site as a salvage pile for carriers to collect.
    refunded = site.cancel(sim.local_store(site.id, site.district), sim.defs["construction_rules"]["cancel_refund_delivered"])
    if sim.first_instance_used.get(site.target) == site.id:
        del sim.first_instance_used[site.target]
    return CommandResult(True, info=f"refunded {refunded}")


def cmd_demolish(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    target = cmd.get("target")
    facility = sim.facilities.get(target)
    if facility is None:
        return fail(f"no_facility:{target}")
    if not facility.definition.get("constructible", True):
        return fail(f"protected_building:{target}")
    store = sim.local_store(facility.id, facility.district)
    store.put(facility.held_inputs)
    refund = salvage(facility.definition.get("cost", {}), set(sim.defs["durable_resources"]),
                     sim.defs["construction_rules"]["demolish_refund_durable"])
    store.put(refund)
    del sim.facilities[target]
    return CommandResult(True, info=f"salvaged {refund}")


def cmd_evolve(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    residence: Residence | None = sim.residences.get(cmd.get("residence"))
    if residence is None:
        return fail(f"unknown_residence:{cmd.get('residence')}")
    if residence.evolution_target:
        return fail(f"already_evolving:{residence.evolution_target}")
    target = sim.defs["residences"][residence.tier].get("next")
    if not target:
        return fail(f"no_next_tier:{residence.tier}")
    morph = sim.defs["residences"][target]["evolution"].get("requires_morphology")
    if morph and morph not in sim.researched:
        return fail(f"morphology_not_researched:{morph}")
    residence.evolution_target = target
    residence.evolution_timer = 0.0
    return CommandResult(True, info=f"{residence.id} seeking {target}")


def cmd_research(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    morph_id = cmd.get("morphology")
    morph = sim.defs["morphologies"].get(morph_id)
    if morph is None:
        return fail(f"unknown_morphology:{morph_id}")
    if morph_id in sim.researched or any(p.morphology == morph_id and p.active for p in sim.research):
        return fail(f"already_researched_or_queued:{morph_id}")
    if not sim.nursery_ids():
        return fail("no_nursery")
    project = ResearchProject(
        id=cmd.get("id") or f"research_{morph_id}", morphology=morph_id,
        cost={k: int(v) for k, v in morph["research_cost"].items()}, nursery_work=float(morph["nursery_work"]),
        priority=int(cmd.get("priority", DEFAULT_PRIORITY)), created_at=sim.second, order=sim.next_order(),
    )
    sim.research.append(project)
    return CommandResult(True, info=f"research {morph_id} queued")


def cmd_express(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    morph_id = cmd.get("morphology")
    morph = sim.defs["morphologies"].get(morph_id)
    residence = sim.residences.get(cmd.get("residence"))
    if morph is None:
        return fail(f"unknown_morphology:{morph_id}")
    if residence is None:
        return fail(f"unknown_residence:{cmd.get('residence')}")
    if morph_id not in sim.researched:
        return fail(f"morphology_not_researched:{morph_id}")
    if residence.tier not in morph["expressed_by"]:
        return fail(f"tier_cannot_express:{residence.tier}")
    current = residence.expressed.get(morph["slot"])
    if current == morph_id:
        return fail(f"already_expressed:{morph_id}")
    if current is not None:
        return fail(f"slot_occupied:{morph['slot']}={current}")
    cost = {k: int(v) for k, v in morph["express_cost"].items()}
    store = sim.store(residence.district)
    missing = [f"insufficient_goods:{r}" for r, q in cost.items() if store.get(r) < q]
    if missing:
        return fail(*missing)
    store.take(cost)
    residence.expressed[morph["slot"]] = morph_id
    residence.conversion_until = sim.second + int(sim.defs["morphology_rules"]["conversion_pause_seconds"])
    return CommandResult(True, info=f"{residence.id} expresses {morph_id}")


def cmd_set_recipe(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    facility = sim.facilities.get(cmd.get("target"))
    if facility is None:
        return fail(f"no_facility:{cmd.get('target')}")
    recipe = cmd.get("recipe")
    if recipe not in facility.definition.get("recipes", []):
        return fail(f"recipe_not_supported:{recipe}")
    if facility.cycle_remaining is not None:
        return fail("cycle_in_progress")
    facility.recipe_id = recipe
    return CommandResult(True)


def cmd_pause(sim: "Simulation", cmd: dict[str, Any], paused: bool) -> CommandResult:
    facility = sim.facilities.get(cmd.get("target"))
    if facility is None:
        return fail(f"no_facility:{cmd.get('target')}")
    facility.paused = paused
    return CommandResult(True)


def cmd_set_labour_priority(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    """Lower numbers are staffed first. Category defaults are 0..N in workforce.job_priority order.

    ``target`` may be a facility id, or one of the job categories ``builders``/``research``.
    """
    value = cmd.get("value")
    if cmd.get("target") in ("builders", "research"):
        if value is not None and not isinstance(value, int):
            return fail(f"invalid_priority:{value}")
        category = "construction" if cmd["target"] == "builders" else "research"
        if value is None:
            sim.category_priority.pop(category, None)
        else:
            sim.category_priority[category] = value
        return CommandResult(True)
    facility = sim.facilities.get(cmd.get("target"))
    if facility is None:
        return fail(f"no_facility:{cmd.get('target')}")
    value = cmd.get("value")
    if value is not None and not isinstance(value, int):
        return fail(f"invalid_priority:{value}")
    facility.labour_priority = value
    return CommandResult(True)


def _trade_open(sim: "Simulation") -> list[str]:
    needed = sim.defs["trade"].get("requires_building")
    if needed and not any(f.building_id == needed for f in sim.facilities.values()):
        return [f"trade_not_open:requires {needed}"]
    return []


def cmd_trade(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    problems = _trade_open(sim)
    if problems:
        return fail(*problems)
    sell = {k: int(v) for k, v in cmd.get("sell", {}).items()}
    buy = {k: int(v) for k, v in cmd.get("buy", {}).items()}
    ok, reasons = sim.trade.barter(sim.store(sim.districts[0]), sell, buy, sim.second, sim.season["id"], sim.next_id("caravan"))
    return CommandResult(ok, reasons, info=f"sold {sell} bought {buy}" if ok else "")


def cmd_deliver_contract(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    problems = _trade_open(sim)
    if problems:
        return fail(*problems)
    ok, reasons = sim.trade.deliver_contract(sim.store(sim.districts[0]), cmd.get("contract"), sim.second, sim.season["id"], sim.next_id("caravan"))
    return CommandResult(ok, reasons)


def cmd_decline_contract(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    ok, reasons = sim.trade.decline(cmd.get("contract"))
    return CommandResult(ok, reasons)


def cmd_begin_great_work(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    if sim.great_work.begun_at is not None:
        return fail("great_work_already_begun")
    blockers = sim.great_work_blockers()
    if blockers:
        return fail(*blockers)
    sim.begin_great_work(int(cmd.get("priority", 0)))
    return CommandResult(True, info="Memory Reef begun")


POLICIES = {"growth_nutrient_reserve", "builder_wp"}


def cmd_set_policy(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    policy = cmd.get("policy")
    if policy not in POLICIES:
        return fail(f"unknown_policy:{policy}")
    value = cmd.get("value")
    if not isinstance(value, (int, float)) or value < 0:
        return fail(f"invalid_policy_value:{value}")
    sim.policies[policy] = value
    return CommandResult(True, info=f"{policy}={value}")


HANDLERS = {
    "set_policy": cmd_set_policy,
    "set_labour_priority": cmd_set_labour_priority,
    "construct": cmd_construct,
    "cancel": cmd_cancel,
    "demolish": cmd_demolish,
    "evolve": cmd_evolve,
    "research": cmd_research,
    "express": cmd_express,
    "set_recipe": cmd_set_recipe,
    "pause": lambda sim, cmd: cmd_pause(sim, cmd, True),
    "resume": lambda sim, cmd: cmd_pause(sim, cmd, False),
    "trade": cmd_trade,
    "deliver_contract": cmd_deliver_contract,
    "decline_contract": cmd_decline_contract,
    "begin_great_work": cmd_begin_great_work,
}


def _spatial_only(handler):
    def run(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
        if sim.spatial is None:
            return fail("spatial:not_enabled")
        ok, info, reasons = handler(sim, cmd)
        return CommandResult(True, info=info) if ok else fail(*reasons)
    return run


HANDLERS["build_road"] = _spatial_only(lambda sim, cmd: sim.spatial.build_road(cmd))
HANDLERS["remove_road"] = _spatial_only(lambda sim, cmd: sim.spatial.remove_road(cmd.get("target")))


def execute(sim: "Simulation", cmd: dict[str, Any]) -> CommandResult:
    handler = HANDLERS.get(cmd.get("do"))
    if handler is None:
        return fail(f"unknown_command:{cmd.get('do')}")
    return handler(sim, cmd)
