"""Tests for the mechanics added for Rich's candidate bootstrap rules (AGENT_CHAT 2026-10-02T14:46Z)."""
from __future__ import annotations

import unittest

from economy.engine import Simulation, load_definitions, load_plan
from economy.engine.bootstrap import analyse
from economy.engine.simulation import GRACE, NOT_ENFORCED, PAID, UNPAID
from economy.sweep import marginal_effects, set_path

from tests.helpers import ROOT, make_defs, run_until

CANDIDATE = ROOT / "economy" / "data" / "experiments" / "candidate_bootstrap_rules_v1.json"
PLAN_B = ROOT / "economy" / "data" / "plans" / "verdant_reference_b.json"


def candidate_defs(patch=None):
    from economy.engine.definitions import deep_merge
    defs = load_definitions(overlays=[CANDIDATE])
    return deep_merge(defs, patch) if patch else defs


def sim_with(commands, patch=None):
    return Simulation(candidate_defs(patch), {"id": "test", "commands": commands})


class FirstInstanceTests(unittest.TestCase):
    PATCH = {"starting_state": {"inventory": {"carbonate": 20, "prepared_silica": 10}}}

    def test_first_kiln_uses_adapted_crew_and_later_kilns_need_artisans(self):
        sim = sim_with([
            {"at": 0, "do": "construct", "building": "ceramic_kiln", "id": "kiln_1"},
            {"at": 0, "do": "construct", "building": "ceramic_kiln", "id": "kiln_2"},
        ], self.PATCH)
        run_until(sim, 2000)
        self.assertEqual({"adapted": 4}, sim.facilities["kiln_1"].definition["jobs"])
        self.assertEqual({"artisan": 4}, sim.facilities["kiln_2"].definition["jobs"])

    def test_first_pit_costs_no_enzyme_and_cancel_releases_the_terms(self):
        sim = sim_with([
            {"at": 0, "do": "construct", "building": "silicate_pit", "id": "pit_1"},
            {"at": 1, "do": "cancel", "target": "pit_1"},
            {"at": 2, "do": "construct", "building": "silicate_pit", "id": "pit_2"},
            {"at": 3, "do": "construct", "building": "silicate_pit", "id": "pit_3"},
        ], self.PATCH)
        run_until(sim, 3)
        self.assertEqual({"carbonate": 2}, sim.sites["pit_1"].cost)
        self.assertEqual({"carbonate": 2}, sim.sites["pit_2"].cost)
        self.assertEqual({"carbonate": 2, "repair_enzyme": 1}, sim.sites["pit_3"].cost)


class PreJawCuttingTests(unittest.TestCase):
    def test_cutter_runs_at_half_rate_without_mineral_jaw(self):
        patch = {"starting_state": {"inventory": {"prepared_silica": 4, "repair_enzyme": 2},
                                    "residences": [{"id": "home_1", "tier": "shelter", "population": 8, "district": "core"},
                                                   {"id": "home_2", "tier": "shelter", "population": 8, "district": "core"},
                                                   {"id": "home_3", "tier": "stable", "population": 12, "district": "core"}]}}
        sim = sim_with([{"at": 0, "do": "construct", "building": "carbonate_cutter", "id": "cutter_1"}], patch)
        while "cutter_1" not in sim.facilities:
            sim.step()
        carbonate = sim.store("core").get("carbonate")
        run_until(sim, sim.second + 195)   # 100 s cycle at 50 % = 200 s
        self.assertEqual(carbonate, sim.store("core").get("carbonate"))
        run_until(sim, sim.second + 10)
        self.assertEqual(carbonate + 1, sim.store("core").get("carbonate"))


class BuilderTests(unittest.TestCase):
    def test_builders_claim_workers_only_while_a_site_is_ready(self):
        sim = sim_with([{"at": 60, "do": "construct", "building": "culture_bed", "id": "bed_2"}])
        run_until(sim, 30)
        self.assertEqual(0.0, sim.builder_wp["core"])
        run_until(sim, 61)
        self.assertAlmostEqual(2.0, sim.builder_wp["core"])
        run_until(sim, 400)
        self.assertIn("bed_2", sim.facilities)
        self.assertEqual(0.0, sim.builder_wp["core"])

    def test_builders_outrank_extraction_crews(self):
        # 18 General: institutions 6 + builders 2 + food 9 leaves 1 for the 3-worker dredge.
        commands = [{"at": 0, "do": "construct", "building": "sediment_dredge", "id": "dredge_1"},
                    {"at": 0, "do": "construct", "building": "nutrient_washer", "id": "washer_1"},
                    {"at": 400, "do": "construct", "building": "culture_bed", "id": "bed_2"}]
        sim = sim_with(commands)
        run_until(sim, 401)
        self.assertAlmostEqual(2.0, sim.builder_wp["core"])
        self.assertTrue(all(f.staffing == 1.0 for f in sim.facilities.values() if f.category == "food"))
        self.assertLess(sim.facilities["dredge_1"].staffing, 0.5)

    def test_player_can_rerank_builders_and_research(self):
        sim = sim_with([{"at": 0, "do": "set_labour_priority", "target": "builders", "value": 9},
                        {"at": 0, "do": "set_labour_priority", "target": "research", "value": 0}])
        run_until(sim, 0)
        self.assertEqual({"construction": 9, "research": 0}, sim.category_priority)


class MaintenanceUpkeepTests(unittest.TestCase):
    def test_baseline_does_not_enforce_upkeep(self):
        sim = Simulation(make_defs(), {"id": "t", "commands": []})
        run_until(sim, 10)
        self.assertEqual(NOT_ENFORCED, sim.upkeep.state)

    def test_grace_then_payment_then_suspension(self):
        sim = sim_with([], {"maintenance_upkeep": {"grace_until_tier": None, "grace_max_seconds": 60},
                            "starting_state": {"inventory": {"repair_enzyme": 1}}})
        run_until(sim, 59)
        self.assertEqual(GRACE, sim.upkeep.state)
        self.assertEqual(1, sim.store("core").get("repair_enzyme"))
        run_until(sim, 60 + 8 * 60)          # weight ~9 -> ~0.11 Enzyme/min -> first unit within ~9 min
        self.assertIn(sim.upkeep.state, (PAID, UNPAID))
        while sim.upkeep.state != UNPAID and sim.second < 3000:
            sim.step()
        self.assertEqual(UNPAID, sim.upkeep.state)
        self.assertEqual(1, sim.upkeep.paid)
        self.assertNotIn("maintenance", sim.services["core"])
        sim.store("core").put({"repair_enzyme": 1})
        sim.step()
        sim.step()
        self.assertEqual(PAID, sim.upkeep.state)
        self.assertIn("maintenance", sim.services["core"])


class GreatWorkCoordinatorTests(unittest.TestCase):
    def test_coordinators_covering_lower_jobs_still_count_and_are_claimed(self):
        patch = {"starting_state": {
            "inventory": {"carbonate": 40, "fired_ceramic": 30, "habitat_composite": 30, "repair_enzyme": 10,
                          "pigment_ornament": 10, "staple": 200, "balanced_gel": 200},
            "residences": [{"id": "home_1", "tier": "memory", "population": 20, "district": "core"}]}}
        sim = Simulation(make_defs(patch), {"id": "t", "commands": []})
        run_until(sim, 5)
        allocation = sim.allocations["core"]
        self.assertGreater(allocation.below_class["coordinator"], 0)       # covering General jobs
        self.assertNotIn(True, [b.startswith("needs_coordinator_wp") for b in sim.great_work_blockers()])
        sim.begin_great_work(0)
        while sim.great_work.stage_index < 1 and sim.second < 5400:
            sim.step()
        while sim.second < 5400 and sim.great_work.completed_at is None:
            sim.step()
            site = sim.sites.get(sim.great_work.site_id or "")
            if site and site.materials_complete_at is not None and site.coordinator_remaining() > 0:
                self.assertGreater(sim.coordinator_pool["core"], 10)    # claimed ahead of lower jobs
                break


class PlanTriggerTests(unittest.TestCase):
    def test_stock_below_and_free_housing_triggers(self):
        sim = sim_with([
            {"at": 0, "do": "construct", "building": "shelter", "id": "home_4", "when": {"free_housing_below": 3}},
            {"at": 0, "do": "pause", "target": "field_1", "when": {"stock_below": {"staple": 5}}},
        ])
        run_until(sim, 5)
        self.assertIn("home_4", sim.sites)
        self.assertFalse(sim.facilities["field_1"].paused)

    def test_free_housing_ignores_great_work_sites(self):
        sim = Simulation(make_defs({"starting_state": {"inventory": {"carbonate": 20, "fired_ceramic": 10}}}),
                         {"id": "t", "commands": [{"at": 2, "do": "construct", "building": "shelter", "id": "home_4",
                                                   "when": {"free_housing_below": 3}}]})
        run_until(sim, 0)
        sim.begin_great_work(0)
        run_until(sim, 3)
        self.assertIn("home_4", sim.sites)


class ResidencePresentationTests(unittest.TestCase):
    def test_snapshot_exposes_art_facing_residence_state(self):
        sim = sim_with([{"at": 0, "do": "evolve", "residence": "home_1"}])
        run_until(sim, 60)
        state = sim.diag.snapshots[-1]["residences"]["home_1"]
        for key in ("tier", "condition", "need_buffer_minutes", "services_for_next_tier", "evolution", "expressed_morphologies"):
            self.assertIn(key, state)
        self.assertEqual("stable", state["evolution"]["target_tier"])
        self.assertIn("service:waste", state["evolution"]["blockers"])
        self.assertFalse(state["services_for_next_tier"]["waste"])


class CandidateBootstrapTests(unittest.TestCase):
    def test_candidate_rules_remove_every_static_deadlock(self):
        result = analyse(candidate_defs())
        self.assertTrue(result["viable"], result["unreachable"])

    def test_first_symbiotic_gel_is_flagged_as_self_supplied(self):
        needs = analyse(candidate_defs())["self_supplied_needs"]
        self.assertEqual([("symbiotic", "balanced_gel")], [(n["tier"], n["need"]) for n in needs])


class SweepToolTests(unittest.TestCase):
    def test_set_path_handles_list_indices(self):
        defs = candidate_defs()
        set_path(defs, "seasons.1.sediment", 0.9)
        self.assertEqual(0.9, defs["seasons"][1]["sediment"])

    def test_marginal_effects_average_over_other_parameters(self):
        runs = [{"setting": {"a": a, "b": b}, "final_population": 10 * a + b, "first_stable": "10:00",
                 "first_symbiotic": None, "upkeep_unpaid_minutes": 0} for a in (1, 2) for b in (0, 2)]
        effects = marginal_effects(runs)
        self.assertEqual(11.0, effects["a"][1]["mean_final_population"])
        self.assertEqual(21.0, effects["a"][2]["mean_final_population"])


class CandidateCharacterisationTests(unittest.TestCase):
    """CHARACTERISATION of candidate_bootstrap_rules_v1 + plan B. Update with a chat entry when rules change."""

    @classmethod
    def setUpClass(cls):
        cls.report = Simulation(candidate_defs(), load_plan(PLAN_B)).run()

    def test_first_stable_happens_but_no_symbiotic_or_reef(self):
        outcome = self.report["outcome"]
        self.assertIsNotNone(outcome["tier_first_reached"].get("stable"))
        self.assertNotIn("symbiotic", outcome["tier_first_reached"])
        self.assertIsNone(outcome["great_work_completed_at"])

    def test_carbonate_still_leads_the_bottlenecks(self):
        keys = [b["key"] for b in self.report["bottlenecks"][:3]]
        self.assertEqual("goods:carbonate", keys[0])
        self.assertIn("workforce:general", keys)

    def test_upkeep_grace_lasts_until_symbiotic(self):
        self.assertEqual(GRACE, self.report["maintenance_upkeep"]["state"])
        self.assertEqual(0.0, self.report["maintenance_upkeep"]["unpaid_minutes"])


if __name__ == "__main__":
    unittest.main()
