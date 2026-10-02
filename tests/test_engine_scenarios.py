"""Scenario and cross-system tests for the honest reference economy.

The characterisation assertions (marked) pin today's evidence-backed balance
failure. When balance data changes, update them in the same commit as a
docs/AGENT_CHAT.md entry explaining the new result.
"""
from __future__ import annotations

import hashlib
import json
import unittest

from economy.engine import Simulation, load_plan
from economy.engine.bootstrap import analyse

from tests.helpers import make_defs


def run_reference(probe: bool):
    sim = Simulation(make_defs(probe=probe), load_plan())
    return sim, sim.run()


class BootstrapAnalysisTests(unittest.TestCase):
    def test_doc_faithful_definitions_contain_deadlocks(self):
        result = analyse(make_defs())
        self.assertFalse(result["viable"])
        self.assertEqual(["shelter"], result["reachable_tiers"])
        nodes = {node for cycle in result["deadlock_cycles"] for node in cycle}
        # Memory Enclave <- Memory service <- Memory Circle <- Coordinators <- Memory Enclave
        self.assertTrue({"tier:memory", "service:memory", "building:memory_circle", "class:coordinator"} <= nodes)
        # First Stable <- Growth Nutrient/Waste/Clean Flow <- Adapted workers <- Stable
        self.assertTrue({"tier:stable", "class:adapted", "good:growth_nutrient", "service:waste"} <= nodes)
        self.assertIn("service:waste", result["unreachable"]["tier:stable"])

    def test_enzyme_silica_loop_appears_behind_the_workforce_loops(self):
        result = analyse(make_defs({"starting_state": {"inventory": {"repair_enzyme": None}}}, probe=True))
        self.assertFalse(result["viable"])
        nodes = {node for cycle in result["deadlock_cycles"] for node in cycle}
        self.assertTrue({"building:silicate_pit", "good:repair_enzyme", "good:fired_ceramic", "good:prepared_silica"} <= nodes)

    def test_probe_overlay_removes_every_static_deadlock(self):
        result = analyse(make_defs(probe=True))
        self.assertTrue(result["viable"], result["unreachable"])
        self.assertEqual(["shelter", "stable", "symbiotic", "memory"], result["reachable_tiers"])


class ReferencePlanInvariantTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline_sim, cls.baseline = run_reference(probe=False)
        cls.probe_sim, cls.probe = run_reference(probe=True)

    def test_simulation_is_deterministic(self):
        def fingerprint(report):
            return hashlib.sha256(json.dumps(report, sort_keys=True, default=str).encode()).hexdigest()
        _, again = run_reference(probe=True)
        self.assertEqual(fingerprint(self.probe), fingerprint(again))

    def test_records_every_minute(self):
        self.assertEqual(91, len(self.probe["snapshots"]))
        first = self.probe["snapshots"][0]
        self.assertIn("general", first["workforce"]["core"])
        self.assertIn("store", first)

    def test_no_building_appears_without_paid_cost_and_completed_work(self):
        for sim in (self.baseline_sim, self.probe_sim):
            starting = {entry["id"] for entry in sim.defs["starting_state"]["buildings"]}
            starting |= {entry["id"] for entry in sim.defs["starting_state"]["residences"]}
            built = {entry["id"]: entry for entry in sim.diag.completed_sites}
            for entity_id in list(sim.facilities) + list(sim.residences):
                if entity_id in starting:
                    continue
                self.assertIn(entity_id, built, entity_id)
                site = sim.sites[entity_id]
                for resource, quantity in site.cost.items():
                    self.assertEqual(quantity, site.delivered.get(resource, 0), f"{entity_id} {resource}")
                self.assertIsNotNone(site.materials_complete_at)
                self.assertLessEqual(site.materials_complete_at, site.completed_at)
                self.assertGreaterEqual(site.physical_done + 1e-6, site.physical_work)

    def test_no_production_without_staffing(self):
        # Baseline: the Nutrient Washer needs Adapted workers that never exist, so no Growth Nutrient is ever made.
        self.assertNotIn("growth_nutrient", self.baseline["produced_by_recipes"])
        self.assertGreater(self.baseline_sim.diag.lost["washer_1"][("no_workforce", "staffing 0.00")], 60 * 60)

    def test_tiers_change_only_through_evolution_rules(self):
        for sim in (self.baseline_sim, self.probe_sim):
            order = sim.defs["residence_rules"]["tier_order"]
            initial = {e["id"]: e["tier"] for e in sim.defs["starting_state"]["residences"]}
            for residence in sim.residences.values():
                start_index = order.index(initial.get(residence.id, "shelter"))
                ups = sum(1 for e in sim.events if e.split(" ", 1)[1].startswith(f"{residence.id} evolved"))
                downs = sum(1 for e in sim.events if e.split(" ", 1)[1].startswith(f"{residence.id} devolved"))
                self.assertEqual(order.index(residence.tier), start_index + ups - downs, residence.id)

    def test_goods_are_whole_and_never_negative(self):
        for snapshot in self.probe["snapshots"]:
            for resource, quantity in snapshot["custody"].items():
                self.assertIsInstance(quantity, int)
                self.assertGreaterEqual(quantity, 0, resource)

    def test_report_names_at_least_three_bottlenecks_with_evidence(self):
        for report in (self.baseline, self.probe):
            self.assertGreaterEqual(len(report["bottlenecks"]), 3)
            for item in report["bottlenecks"][:3]:
                self.assertTrue(item["top_evidence"])
                self.assertGreater(item["blocked_entity_minutes"], 0)

    def test_great_work_failure_is_explained(self):
        for report in (self.baseline, self.probe):
            path = report["great_work_critical_path"]
            if report["outcome"]["great_work_completed_at"] is None and path["begun_at"] is None:
                self.assertTrue(path["unlock"]["current_blockers"])


class ReferencePlanCharacterisationTests(unittest.TestCase):
    """CHARACTERISATION: today's honest result. Update with a chat entry when balance changes."""

    @classmethod
    def setUpClass(cls):
        _, cls.baseline = run_reference(probe=False)
        _, cls.probe = run_reference(probe=True)

    def test_doc_faithful_economy_never_leaves_the_shelter_tier(self):
        self.assertIsNone(self.baseline["outcome"]["great_work_completed_at"])
        self.assertEqual(0, self.baseline["outcome"]["final_tiers"]["stable"])

    def test_probe_economy_still_cannot_reach_the_memory_reef(self):
        outcome = self.probe["outcome"]
        self.assertIsNone(outcome["great_work_completed_at"])
        self.assertEqual(0, outcome["final_tiers"]["symbiotic"])
        self.assertGreaterEqual(outcome["final_tiers"]["stable"], 1)

    def test_carbonate_is_the_top_probe_bottleneck(self):
        self.assertEqual("goods:carbonate", self.probe["bottlenecks"][0]["key"])
        keys = [item["key"] for item in self.probe["bottlenecks"][:5]]
        self.assertIn("labour:construction", keys)


if __name__ == "__main__":
    unittest.main()
