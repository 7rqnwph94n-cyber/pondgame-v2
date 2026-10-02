"""Static bootstrap analysis of a definitions file.

Answers, without running time: starting from the initial colony, which goods
can become *renewable*, which buildings can be built and staffed, which
residence tiers, workforce classes, services and morphologies can ever be
reached? Anything unreachable is reported with its blockers, and blocker
cycles (deadlocks) are extracted as strongly connected components.

Rules used (deliberately generous so an unreachable verdict is robust):
- one-off costs (construction, evolution, research, expression) may be paid
  from finite stock: starting inventory or goods the trade partner sells;
- recurring recipe inputs must be renewable;
- a job can be filled by its own class or any higher class that is reachable;
- quantities are ignored, so finite stock is treated as unlimited. A good can
  therefore be reported reachable here yet still run out in simulation.
"""
from __future__ import annotations

from typing import Any

from .definitions import first_instance_terms


def analyse(defs: dict[str, Any]) -> dict[str, Any]:
    classes = defs["workforce"]["classes"]
    tiers_order = defs["residence_rules"]["tier_order"]
    # One instance is enough to bootstrap a chain, so first-instance terms count.
    buildings = {b: first_instance_terms(d) for b, d in defs["buildings"].items()}
    recipes = defs["recipes"]
    start = defs["starting_state"]

    stock = {r for r, q in start["inventory"].items() if q > 0}
    stock |= set(defs.get("trade", {}).get("partner_sells", {}))
    existing = {entry["building"] for entry in start["buildings"]}
    tiers = {entry["tier"] for entry in start["residences"]}
    renewable: set[str] = set()
    morphs_researched: set[str] = set()
    morphs_expressed: set[str] = set()

    def available_classes() -> set[str]:
        return {defs["residences"][t]["class"] for t in tiers}

    def staffable(definition: dict[str, Any], have: set[str]) -> list[str]:
        missing = []
        for job_class in definition.get("jobs", {}):
            index = classes.index(job_class)
            if not any(c in have for c in classes[index:]):
                missing.append(f"class:{job_class}")
        return missing

    def payable(goods: dict[str, Any]) -> list[str]:
        return [f"good:{r}" for r in goods if r not in renewable and r not in stock]

    def building_blockers(building_id: str) -> list[str]:
        definition = buildings[building_id]
        blockers: list[str] = []
        if building_id not in existing:
            if not definition.get("constructible", True):
                return ["not_constructible"]
            blockers += payable(definition.get("cost", {}))
        blockers += staffable(definition, available_classes())
        morph = definition.get("requires_morphology")
        if morph and morph not in morphs_expressed:
            blockers.append(f"morph:{morph}")
        return blockers

    def services_available() -> set[str]:
        return {
            service_id for service_id, service in defs["services"].items()
            if any(p in buildings and not building_blockers(p) for p in service["provided_by"])
        }

    def recipe_blockers(recipe_id: str) -> list[str]:
        return [f"good:{r}" for r in recipes[recipe_id].get("inputs", {}) if r not in renewable]

    def tier_blockers(tier: str) -> list[str]:
        index = tiers_order.index(tier)
        if index == 0:
            return [] if "shelter" in buildings and not payable(buildings["shelter"].get("cost", {})) else ["good:shelter_cost"]
        previous = tiers_order[index - 1]
        blockers = [] if previous in tiers else [f"tier:{previous}"]
        evolution = defs["residences"][tier].get("evolution", {})
        blockers += payable(evolution.get("goods", {}))
        have = services_available()
        blockers += [f"service:{s}" for s in evolution.get("services", []) if s not in have]
        morph = evolution.get("requires_morphology")
        if morph and morph not in morphs_expressed:
            blockers.append(f"morph:{morph}")
        return blockers

    def research_blockers(morph_id: str) -> list[str]:
        morph = defs["morphologies"][morph_id]
        nurseries = [b for b, d in buildings.items() if d.get("research_jobs") and not building_blockers(b)]
        blockers = [] if nurseries else ["building:nursery"]
        return blockers + payable(morph.get("research_cost", {}))

    def express_blockers(morph_id: str) -> list[str]:
        morph = defs["morphologies"][morph_id]
        blockers = [] if morph_id in morphs_researched else [f"research:{morph_id}"]
        blockers += payable(morph.get("express_cost", {}))
        if not any(t in tiers for t in morph["expressed_by"]):
            # Any listed tier suffices; the lowest one is the honest blocker
            # (higher tiers require it anyway), which avoids false OR-cycles.
            lowest = min(morph["expressed_by"], key=tiers_order.index)
            blockers.append(f"tier:{lowest}")
        return blockers

    changed = True
    while changed:
        changed = False
        for building_id, definition in buildings.items():
            if building_blockers(building_id):
                continue
            for recipe_id in definition.get("recipes", []):
                if not recipe_blockers(recipe_id):
                    for good in recipes[recipe_id]["outputs"]:
                        if good not in renewable:
                            renewable.add(good)
                            changed = True
                    for good in recipes[recipe_id].get("byproducts", {}):
                        if good not in renewable:
                            renewable.add(good)
                            changed = True
        for tier in tiers_order:
            if tier not in tiers and not tier_blockers(tier):
                tiers.add(tier)
                changed = True
        for morph_id in defs["morphologies"]:
            if morph_id not in morphs_researched and not research_blockers(morph_id):
                morphs_researched.add(morph_id)
                changed = True
            if morph_id not in morphs_expressed and not express_blockers(morph_id):
                morphs_expressed.add(morph_id)
                changed = True

    # ----- explain what is unreachable
    graph: dict[str, list[str]] = {}
    for good in defs["resources"]:
        if good in renewable or good == "stored_value":
            continue
        producers = [
            f"building:{b}" for b, d in buildings.items()
            if any(good in recipes[r]["outputs"] or good in recipes[r].get("byproducts", {}) for r in d.get("recipes", []))
        ]
        graph[f"good:{good}"] = producers or ["no_producer"]
    for building_id, definition in buildings.items():
        blockers = building_blockers(building_id)
        recipe_block = []
        if not blockers and definition.get("recipes"):
            if all(recipe_blockers(r) for r in definition["recipes"]):
                recipe_block = sorted({b for r in definition["recipes"] for b in recipe_blockers(r)})
        if blockers or recipe_block:
            graph[f"building:{building_id}"] = blockers + recipe_block
    for tier in tiers_order:
        if tier not in tiers:
            graph[f"tier:{tier}"] = tier_blockers(tier)
    have_classes = available_classes()
    for job_class in classes:
        if job_class not in have_classes:
            graph[f"class:{job_class}"] = [f"tier:{t}" for t, d in defs["residences"].items() if d["class"] == job_class]
    have_services = services_available()
    for service_id, service in defs["services"].items():
        if service_id not in have_services:
            graph[f"service:{service_id}"] = [f"building:{p}" for p in service["provided_by"]]
    for morph_id in defs["morphologies"]:
        if morph_id not in morphs_researched:
            graph[f"research:{morph_id}"] = research_blockers(morph_id)
        if morph_id not in morphs_expressed:
            graph[f"morph:{morph_id}"] = express_blockers(morph_id)

    cycles = [sorted(c) for c in _strongly_connected(graph) if len(c) > 1]

    # Recurring needs a tier can only get from its own (or a higher) workforce class: the first home of
    # that tier starts short and must get the producer staffed before Strain + Dormancy end in devolution.
    rules = defs["residence_rules"]
    grace = int(rules["strain_seconds"] + rules["dormancy_seconds"])
    self_supplied = []
    for tier in tiers_order[1:]:   # the starting tier is supplied by the starting colony
        tier_class = classes.index(defs["residences"][tier]["class"])
        for good in defs["residences"][tier]["per_minute"]:
            producers = [b for b, d in buildings.items()
                         if any(good in recipes[r]["outputs"] for r in d.get("recipes", []))]
            lower_staffable = [b for b in producers
                               if all(classes.index(c) < tier_class for c in buildings[b].get("jobs", {}))]
            if producers and not lower_staffable:
                self_supplied.append({"tier": tier, "need": good, "producers": producers, "grace_seconds": grace})
    stock_only = sorted(r for r in stock if r not in renewable and r != "stored_value")
    return {
        "renewable_goods": sorted(renewable),
        "stock_only_goods": stock_only,
        "reachable_tiers": [t for t in tiers_order if t in tiers],
        "reachable_classes": [c for c in classes if c in have_classes],
        "available_services": sorted(have_services),
        "researchable_morphologies": sorted(morphs_researched),
        "expressible_morphologies": sorted(morphs_expressed),
        "unreachable": {k: v for k, v in sorted(graph.items())},
        "deadlock_cycles": sorted(cycles, key=len),
        "self_supplied_needs": self_supplied,
        "viable": not graph,
    }


def _strongly_connected(graph: dict[str, list[str]]) -> list[list[str]]:
    """Tarjan's algorithm restricted to nodes present in the graph (iterative)."""
    index_of: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    result: list[list[str]] = []
    counter = 0
    for root in sorted(graph):
        if root in index_of:
            continue
        work = [(root, iter(graph.get(root, [])))]
        index_of[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, children = work[-1]
            advanced = False
            for child in children:
                if child not in graph:
                    continue
                if child not in index_of:
                    index_of[child] = low[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(graph.get(child, []))))
                    advanced = True
                    break
                if child in on_stack:
                    low[node] = min(low[node], index_of[child])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
            if low[node] == index_of[node]:
                component = []
                while True:
                    item = stack.pop()
                    on_stack.discard(item)
                    component.append(item)
                    if item == node:
                        break
                result.append(component)
    return result


def format_analysis(result: dict[str, Any]) -> str:
    lines = ["Bootstrap analysis (static, quantity-blind)"]
    lines.append(f"  viable: {result['viable']}")
    lines.append(f"  reachable tiers: {', '.join(result['reachable_tiers'])}")
    lines.append(f"  reachable workforce classes: {', '.join(result['reachable_classes'])}")
    lines.append(f"  renewable goods: {', '.join(result['renewable_goods']) or 'none'}")
    lines.append(f"  finite-stock-only goods: {', '.join(result['stock_only_goods']) or 'none'}")
    lines.append(f"  services available: {', '.join(result['available_services']) or 'none'}")
    if result["unreachable"]:
        lines.append("  unreachable (blocked by):")
        for item, blockers in result["unreachable"].items():
            lines.append(f"    {item:32s} <- {', '.join(blockers)}")
    for item in result.get("self_supplied_needs", []):
        lines.append(f"  self-supplied need: first {item['tier']} home needs {item['need']}, made only by its own class "
                     f"({', '.join(item['producers'])}); {item['grace_seconds']} s before devolution")
    for i, cycle in enumerate(result["deadlock_cycles"], 1):
        lines.append(f"  deadlock cycle {i} ({len(cycle)} nodes): {', '.join(cycle)}")
    return "\n".join(lines)
