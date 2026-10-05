"""Tests for Rich's bootstrap rules, promoted into the v0.2 baseline (AGENT_CHAT 2026-10-02T14:46Z, 15:18Z)."""
from __future__ import annotations

import unittest

from economy.engine import Simulation, load_definitions, load_plan
from economy.engine.bootstrap import analyse
from economy.engine.simulation import GRACE, NOT_ENFORCED, PAID, UNPAID
from economy.sweep import apply_level, evaluate, marginal_effects, set_path

from tests.helpers import ROOT, make_defs, run_until

PLAN_B = ROOT / "economy" / "data" / "plans" / "verdant_reference_b.json"


def candidate_defs(patch=None):
    """The promoted v0.2 baseline (formerly candidate_bootstrap_rules_v1)."""
    from economy.engine.definitions import deep_merge
    defs = load_definitions()
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


class FoodEmergencyTests(unittest.TestCase):
    def test_emergency_preempts_builders_then_restores_them(self):
        from economy.engine.simulation import BUILDERS_PREEMPTED, BUILDERS_PROTECTED
        # Food production stops; a construction site becomes ready just as food runs low.
        sim = sim_with([
            {"at": 0, "do": "pause", "target": "bed_1"},
            {"at": 1000, "do": "construct", "building": "ceramic_kiln", "id": "kiln_1"},   # placed once food has run low
        ], {"starting_state": {"inventory": {"staple": 12, "prepared_silica": 2}}})
        while sim.builder_state["core"] != BUILDERS_PREEMPTED and sim.second < 3000:
            sim.step()
        self.assertEqual(BUILDERS_PREEMPTED, sim.builder_state["core"])
        self.assertTrue(sim.food_emergency.active)
        self.assertIn("staple", sim.food_emergency.reason)
        self.assertIn("kiln_1", sim.sites)
        snapshot_state = sim.diag.snapshot()["builders"]["core"]
        self.assertEqual(BUILDERS_PREEMPTED, snapshot_state["state"])
        self.assertTrue(snapshot_state["reason"])
        # Resupply: emergency ends only above the exit threshold (hysteresis), then builders are protected again.
        sim.facilities["bed_1"].paused = False
        sim.store("core").put({"staple": 40})
        run_until(sim, sim.second + 3)
        self.assertFalse(sim.food_emergency.active)
        self.assertEqual(BUILDERS_PROTECTED, sim.builder_state["core"])
        self.assertEqual(1, sim.food_emergency.episodes)

    def test_hysteresis_requires_exit_threshold(self):
        sim = sim_with([], {"starting_state": {"inventory": {"staple": None}}})
        sim.food_emergency.rules = dict(sim.food_emergency.rules, enter_below_minutes=4, exit_above_minutes=8)
        run_until(sim, 1)
        self.assertTrue(sim.food_emergency.active)        # ~1 min of buffered food
        sim.store("core").put({"staple": 3})              # ~5 min of food: above enter, below exit
        sim.step()
        self.assertTrue(sim.food_emergency.active)


class MaintenanceUpkeepTests(unittest.TestCase):
    def test_baseline_does_not_enforce_upkeep(self):
        sim = Simulation(make_defs(), {"id": "t", "commands": []})   # legacy doc-faithful
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
    def test_candidate_overlay_is_a_no_op_on_the_promoted_baseline(self):
        from economy.engine.definitions import deep_merge, read_json
        overlay = read_json(ROOT / "economy" / "data" / "experiments" / "candidate_bootstrap_rules_v1.json")
        base = load_definitions()
        merged = deep_merge(base, overlay["patch"])
        for key in ("seasons", "services", "construction_rules", "maintenance_upkeep", "starting_state", "workforce"):
            self.assertEqual(base[key], merged[key], key)
        for building in ("nutrient_washer", "clean_flow_node", "ceramic_kiln", "silicate_pit", "carbonate_cutter"):
            for key in ("jobs", "first_instance", "morphology_modifier", "requires_morphology", "cost"):
                self.assertEqual(base["buildings"][building].get(key), merged["buildings"][building].get(key), (building, key))

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
                 "first_symbiotic": None, "upkeep_unpaid_minutes": 0, "reef_minutes": None} for a in (1, 2) for b in (0, 2)]
        effects = marginal_effects(runs)
        self.assertEqual(11.0, effects["a"][1]["mean_final_population"])
        self.assertEqual(21.0, effects["a"][2]["mean_final_population"])


class SweepLevelTests(unittest.TestCase):
    def test_level_set_append_and_scale(self):
        defs = candidate_defs()
        apply_level(defs, {"set": {"population.migration_per_minute": 0.75},
                           "append": {"starting_state.residences": [{"id": "home_0", "tier": "shelter", "population": 8, "district": "core"}]},
                           "scale": {"great_work.stages.2.cost": 0.7}})
        self.assertEqual(0.75, defs["population"]["migration_per_minute"])
        self.assertEqual("home_0", defs["starting_state"]["residences"][-1]["id"])
        self.assertEqual({"carbonate": 4, "fired_ceramic": 7, "habitat_composite": 10, "repair_enzyme": 6, "pigment_ornament": 4},
                         defs["great_work"]["stages"][2]["cost"])

    def test_acceptance_criteria(self):
        criteria = {"require_symbiotic": True, "max_devolutions": 0, "max_staple_shortage_minutes": 5,
                    "max_unpaid_minutes": 1, "reef_window_minutes": [100, 120]}
        good = {"first_symbiotic": "50:00", "symbiotic_devolutions": 0, "devolutions": 0, "staple_shortage_minutes": 2,
                "upkeep_unpaid_minutes": 0, "reef_minutes": 112.0, "reef_completed_at": "112:00"}
        self.assertEqual([], evaluate(good, criteria))
        self.assertEqual(["reef_too_late"], evaluate(dict(good, reef_minutes=121.0), criteria))
        self.assertEqual(["food_not_solvent"], evaluate(dict(good, staple_shortage_minutes=9), criteria))
        self.assertIn("reef_not_completed", evaluate(dict(good, reef_minutes=None, reef_completed_at=None), criteria))


class BaselineCharacterisationTests(unittest.TestCase):
    """CHARACTERISATION of the promoted v0.2 baseline + plan B (120 min). Update with a chat entry when rules change."""

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
        self.assertIn("labour:construction", keys)

    def test_upkeep_grace_lasts_until_symbiotic(self):
        self.assertEqual(GRACE, self.report["maintenance_upkeep"]["state"])
        self.assertEqual(0.0, self.report["maintenance_upkeep"]["unpaid_minutes"])


class ThroughputSweepTests(unittest.TestCase):
    PLAN_C = ROOT / "economy" / "data" / "plans" / "verdant_reference_c.json"
    SPEC = ROOT / "economy" / "data" / "experiments" / "throughput_sweep_v1.json"

    def test_every_sweep_level_produces_valid_definitions(self):
        import json
        from economy.engine import validate_definitions
        from economy.sweep import parameter_levels
        spec = json.loads(self.SPEC.read_text(encoding="utf-8"))
        for parameter in spec["parameters"]:
            for level in parameter_levels(parameter):
                defs = candidate_defs()
                apply_level(defs, level)
                self.assertEqual([], validate_definitions(defs), (parameter["name"], level["label"]))

    def test_food_minutes_trigger(self):
        sim = sim_with([{"at": 0, "do": "pause", "target": "field_1", "when": {"food_minutes_below": 100}},
                        {"at": 0, "do": "pause", "target": "bed_1", "when": {"food_minutes_above": 100}}])
        run_until(sim, 2)
        self.assertTrue(sim.facilities["field_1"].paused)
        self.assertFalse(sim.facilities["bed_1"].paused)

    def test_plan_c_characterisation_120_minutes(self):
        """CHARACTERISATION (2026-10-02): plan C on the promoted baseline reaches Stable but not Symbiotic."""
        report = Simulation(candidate_defs(), load_plan(self.PLAN_C)).run()
        self.assertEqual(7200, report["meta"]["duration_seconds"])
        self.assertIn("stable", report["outcome"]["tier_first_reached"])
        self.assertNotIn("symbiotic", report["outcome"]["tier_first_reached"])
        self.assertIsNone(report["outcome"]["great_work_completed_at"])


if __name__ == "__main__":
    unittest.main()
