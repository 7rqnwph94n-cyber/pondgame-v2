"""Unit tests for individual Milestone A systems."""
from __future__ import annotations

import unittest

from economy.engine.environment import Environment
from economy.engine.inventory import InsufficientGoods, Inventory
from economy.engine.production import Facility
from economy.engine.residences import DORMANT, NORMAL, STRAINED, Residence
from economy.engine.workforce import Job, allocate

from tests.helpers import make_defs, make_sim, one_residence, run_until

CLASSES = ["general", "adapted", "artisan", "coordinator"]
EFF = [1.0, 0.85, 0.65, 0.50]


class InventoryTests(unittest.TestCase):
    def test_goods_are_whole_units(self):
        store = Inventory(["carbonate"])
        with self.assertRaises(ValueError):
            store.put({"carbonate": 0.5})

    def test_cannot_take_more_than_held(self):
        store = Inventory(["carbonate"], {"carbonate": 2})
        with self.assertRaises(InsufficientGoods):
            store.take({"carbonate": 3})
        self.assertEqual(2, store.get("carbonate"))
        self.assertEqual(2, store.take_up_to("carbonate", 5))
        self.assertEqual(0, store.get("carbonate"))


class WorkforceTests(unittest.TestCase):
    def test_same_class_fills_first_and_reports_unassigned(self):
        result = allocate({"general": 10}, [Job("a:general", "a", "general", 3, 0, 0)], CLASSES, EFF)
        self.assertAlmostEqual(1.0, result.staffing["a:general"])
        self.assertAlmostEqual(7.0, result.remaining["general"])

    def test_higher_class_substitutes_at_penalty(self):
        result = allocate({"adapted": 10}, [Job("a:general", "a", "general", 3, 0, 0)], CLASSES, EFF)
        self.assertAlmostEqual(1.0, result.staffing["a:general"])
        self.assertAlmostEqual(10 - 3 / 0.85, result.remaining["adapted"])
        self.assertAlmostEqual(3 / 0.85, result.below_class["adapted"])

    def test_lower_class_never_fills_higher_job(self):
        result = allocate({"general": 50}, [Job("k:artisan", "k", "artisan", 4, 0, 0)], CLASSES, EFF)
        self.assertEqual(0.0, result.staffing["k:artisan"])
        self.assertAlmostEqual(4.0, result.vacancies["artisan"])
        self.assertAlmostEqual(50.0, result.remaining["general"])

    def test_priority_order_decides_who_is_understaffed(self):
        jobs = [Job("late:general", "late", "general", 3, 5, 0), Job("early:general", "early", "general", 3, 1, 1)]
        result = allocate({"general": 4}, jobs, CLASSES, EFF)
        self.assertAlmostEqual(1.0, result.staffing["early:general"])
        self.assertAlmostEqual(1 / 3, result.staffing["late:general"])


class FakeContext:
    def __init__(self, store, capabilities=()):
        self._store = store
        self.capabilities = set(capabilities)
        self.losses: dict[str, float] = {}
        self.outputs: dict[str, int] = {}

    def store(self, district):
        return self._store

    def has_capability(self, district, morphology):
        return morphology in self.capabilities

    def record_loss(self, facility_id, cause, detail, seconds):
        self.losses[cause] = self.losses.get(cause, 0.0) + seconds

    def record_output(self, goods):
        for resource, quantity in goods.items():
            self.outputs[resource] = self.outputs.get(resource, 0) + quantity


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.defs = make_defs()
        self.season = self.defs["seasons"][2]  # recession: sediment open
        self.env = Environment(self.defs)

    def facility(self, building_id, staffing=1.0):
        facility = Facility(building_id, building_id, "core", self.defs["buildings"][building_id], 0, 0)
        facility.staffing = staffing
        return facility

    def run_facility(self, facility, ctx, seconds, season=None):
        for _ in range(seconds):
            facility.step(self.defs["recipes"], season or self.season, self.env, ctx, 0.25, 1.0)

    def test_inputs_reserved_at_cycle_start_and_outputs_at_completion(self):
        store = Inventory(self.defs["resources"], {"biomass": 1})
        ctx = FakeContext(store)
        bed = self.facility("culture_bed")
        self.run_facility(bed, ctx, 1)
        self.assertEqual(0, store.get("biomass"))
        self.assertEqual({"biomass": 1}, bed.held_inputs)
        self.run_facility(bed, ctx, 58)
        self.assertEqual(0, store.get("staple"))
        self.run_facility(bed, ctx, 1)
        self.assertEqual(1, store.get("staple"))

    def test_no_workforce_means_no_production(self):
        store = Inventory(self.defs["resources"], {"biomass": 5})
        ctx = FakeContext(store)
        bed = self.facility("culture_bed", staffing=0.2)
        self.run_facility(bed, ctx, 300)
        self.assertEqual(5, store.get("biomass"))
        self.assertEqual(0, store.get("staple"))
        self.assertEqual("no_workforce", bed.status)

    def test_understaffing_slows_production_proportionally(self):
        store = Inventory(self.defs["resources"], {"biomass": 5})
        ctx = FakeContext(store)
        bed = self.facility("culture_bed", staffing=0.5)
        self.run_facility(bed, ctx, 119)
        self.assertEqual(0, store.get("staple"))
        self.run_facility(bed, ctx, 1)
        self.assertEqual(1, store.get("staple"))
        self.assertAlmostEqual(60.0, ctx.losses["no_workforce"], delta=1.0)

    def test_seasonal_closure_stalls_with_environment_reason(self):
        store = Inventory(self.defs["resources"])
        ctx = FakeContext(store)
        dredge = self.facility("sediment_dredge")
        high_water = self.defs["seasons"][1]
        self.run_facility(dredge, ctx, 300, season=high_water)
        self.assertEqual(0, store.get("phosphate_sediment"))
        self.assertEqual("environment", dredge.status)

    def test_finite_patch_depletes(self):
        self.env.reserves["phosphate_bed"] = 1.0
        store = Inventory(self.defs["resources"])
        ctx = FakeContext(store, {"burrowing_limb"})
        dredge = self.facility("sediment_dredge")
        self.run_facility(dredge, ctx, 1000)
        self.assertEqual(1, store.get("phosphate_sediment"))
        self.assertEqual("patch_depleted", dredge.status)

    def test_required_morphology_gates_building(self):
        store = Inventory(self.defs["resources"])
        cutter = self.facility("carbonate_cutter")
        self.run_facility(cutter, FakeContext(store), 300)
        self.assertEqual(0, store.get("carbonate"))
        self.assertEqual("morphology_missing", cutter.status)
        self.run_facility(cutter, FakeContext(store, {"mineral_jaw"}), 100)
        self.assertEqual(1, store.get("carbonate"))

    def test_missing_adaptation_applies_penalty(self):
        store = Inventory(self.defs["resources"])
        dredge = self.facility("sediment_dredge")
        # recession sediment 1.35 x 0.60 without Burrowing Limb = 0.81 -> 120 / 0.81 = 148.1 s
        self.run_facility(dredge, FakeContext(store), 148)
        self.assertEqual(0, store.get("phosphate_sediment"))
        self.run_facility(dredge, FakeContext(store), 1)
        self.assertEqual(1, store.get("phosphate_sediment"))


class EnvironmentTests(unittest.TestCase):
    def test_high_water_deposits_phosphate_and_anoxic_basin_seeps(self):
        env = Environment(make_defs())
        for second in range(0, 1081):
            env.step(second, 1.0)
        self.assertAlmostEqual(180.0, env.reserves["phosphate_bed"])
        self.assertAlmostEqual(80 + 0.08 * 1081 / 60, env.reserves["anoxic_basin"])
        self.assertIsNone(env.reserves["sunlit_shelf"])
        self.assertEqual("high_water", env.season_at(1080)["id"])


class ConstructionTests(unittest.TestCase):
    def test_building_commissions_only_after_materials_and_work(self):
        sim = make_sim([{"at": 0, "do": "construct", "building": "culture_bed", "id": "bed_2"}])
        run_until(sim, 0)
        self.assertEqual(5, sim.store("core").get("carbonate"))   # delivered to the site at once
        self.assertNotIn("bed_2", sim.facilities)
        run_until(sim, 60)
        self.assertNotIn("bed_2", sim.facilities)                  # 8 work at 6 free WP = 80 s
        run_until(sim, 90)
        self.assertIn("bed_2", sim.facilities)

    def test_site_waits_for_missing_materials_and_explains_why(self):
        sim = make_sim([{"at": 0, "do": "construct", "building": "trade_landing", "id": "landing_1"}])
        run_until(sim, 600)
        self.assertNotIn("landing_1", sim.facilities)
        waits = sim.diag.site_wait["landing_1"]
        self.assertGreater(waits["awaiting_materials:fired_ceramic"], 590)
        self.assertGreater(waits["awaiting_materials:habitat_composite"], 590)

    def test_cancel_refunds_ninety_percent_of_delivered_rounded_down(self):
        sim = make_sim([
            {"at": 0, "do": "construct", "building": "ceramic_kiln", "id": "kiln_1"},
            {"at": 1, "do": "cancel", "target": "kiln_1"},
        ])
        run_until(sim, 2)
        self.assertEqual(6 - 4 + 3, sim.store("core").get("carbonate"))
        self.assertEqual(2 - 2 + 1, sim.store("core").get("prepared_silica"))
        self.assertNotIn("kiln_1", sim.facilities)

    def test_demolish_salvages_durable_materials(self):
        sim = make_sim([
            {"at": 0, "do": "construct", "building": "ceramic_kiln", "id": "kiln_1"},
            {"at": 400, "do": "demolish", "target": "kiln_1"},
        ])
        run_until(sim, 399)
        self.assertIn("kiln_1", sim.facilities)
        carbonate_before = sim.store("core").get("carbonate")
        run_until(sim, 400)
        self.assertNotIn("kiln_1", sim.facilities)
        self.assertEqual(carbonate_before + 2, sim.store("core").get("carbonate"))   # floor(4 x 0.6)

    def test_starting_buildings_cannot_be_demolished(self):
        sim = make_sim([{"at": 0, "do": "demolish", "target": "nursery_1"}])
        run_until(sim, 0)
        self.assertEqual(["protected_building:nursery_1"], sim.command_log[0]["reasons"])


class ResidenceStateTests(unittest.TestCase):
    def setUp(self):
        self.defs = make_defs()

    def test_strain_dormancy_devolution_chain(self):
        home = Residence("h", "stable", "core", 12.0, 0, 0)
        events: list[str] = []
        home.short_this_step = True
        home.update_decline(self.defs, 1.0, events, "t")
        self.assertEqual(STRAINED, home.state)
        for _ in range(180):
            home.update_decline(self.defs, 1.0, events, "t")
        self.assertEqual(DORMANT, home.state)
        self.assertEqual(("adapted", 4.0), home.workforce(self.defs, 0))   # 50 % while dormant
        for _ in range(240):
            home.update_decline(self.defs, 1.0, events, "t")
        self.assertEqual("shelter", home.tier)
        self.assertEqual("general", home.workforce(self.defs, 0)[0])
        self.assertTrue(any("devolved stable -> shelter" in e for e in events))
        for _ in range(200):
            home.update_decline(self.defs, 1.0, events, "t")
        self.assertAlmostEqual(8.0, home.population)   # excess population emigrated

    def test_resupply_clears_strain_after_sixty_seconds(self):
        home = Residence("h", "shelter", "core", 8.0, 0, 0)
        home.short_this_step = True
        home.update_decline(self.defs, 1.0, [], "t")
        home.short_this_step = False
        for _ in range(59):
            home.update_decline(self.defs, 1.0, [], "t")
        self.assertEqual(STRAINED, home.state)
        home.update_decline(self.defs, 1.0, [], "t")
        self.assertEqual(NORMAL, home.state)

    def test_lowest_tier_never_devolves(self):
        home = Residence("h", "shelter", "core", 8.0, 0, 0)
        home.short_this_step = True
        for _ in range(2000):
            home.update_decline(self.defs, 1.0, [], "t")
        self.assertEqual("shelter", home.tier)
        self.assertEqual(DORMANT, home.state)


class ResidenceSimulationTests(unittest.TestCase):
    PATCH = {"starting_state": {"inventory": {"growth_nutrient": 2, "carbonate": 10, "biomass": 6}}}

    def services_commands(self):
        return [
            {"at": 0, "do": "construct", "building": "waste_collector", "id": "collector_1", "priority": 1},
            {"at": 0, "do": "construct", "building": "clean_flow_node", "id": "clean_flow_1", "priority": 2},
        ]

    def test_needs_buffers_draw_whole_units_from_the_store(self):
        sim = make_sim([{"at": 0, "do": "pause", "target": "bed_1"}])
        run_until(sim, 0)
        self.assertEqual(8 - 3, sim.store("core").get("staple"))
        for residence in sim.residences.values():
            self.assertAlmostEqual(1.0, residence.buffers["staple"], delta=0.01)

    def test_starvation_strains_then_makes_residences_dormant(self):
        sim = make_sim([{"at": 0, "do": "pause", "target": "bed_1"}], patch={"starting_state": {"inventory": {"staple": None}}})
        run_until(sim, 400)
        self.assertTrue(all(r.state == DORMANT for r in sim.residences.values()))
        self.assertAlmostEqual(9.0, sim.workforce_supply("core")["general"])

    def test_evolution_needs_services_sustain_and_goods(self):
        sim = make_sim(self.services_commands() + [{"at": 0, "do": "evolve", "residence": "home_1"}], patch=self.PATCH, probe=True)
        run_until(sim, 60)
        self.assertEqual("shelter", sim.residences["home_1"].tier)
        self.assertGreater(sim.diag.evolution_wait["home_1"]["service:clean_flow"], 0)
        while sim.residences["home_1"].evolution_timer == 0 and sim.second < 1200:
            sim.step()
        started = sim.second
        self.assertEqual({"growth_nutrient": 2}, sim.residences["home_1"].evolution_reserved)
        self.assertEqual(0, sim.store("core").get("growth_nutrient"))
        run_until(sim, started + 85)
        self.assertEqual("shelter", sim.residences["home_1"].tier)
        run_until(sim, started + 95)
        home = sim.residences["home_1"]
        self.assertEqual("stable", home.tier)
        self.assertEqual({}, home.evolution_reserved)
        self.assertEqual("adapted", home.workforce(sim.defs, sim.second)[0])

    def test_interrupted_evolution_releases_reservation(self):
        sim = make_sim(self.services_commands() + [{"at": 0, "do": "evolve", "residence": "home_1"}], patch=self.PATCH, probe=True)
        while sim.residences["home_1"].evolution_timer == 0 and sim.second < 1200:
            sim.step()
        sim.facilities["clean_flow_1"].paused = True
        sim.step()
        sim.step()
        self.assertEqual({}, sim.residences["home_1"].evolution_reserved)
        self.assertEqual(2, sim.store("core").get("growth_nutrient"))
        self.assertEqual(0.0, sim.residences["home_1"].evolution_timer)

    def test_memory_enclave_requires_researched_ganglion(self):
        sim = make_sim([{"at": 0, "do": "evolve", "residence": "home_1"}], patch=one_residence("symbiotic", 16))
        run_until(sim, 0)
        self.assertEqual(["morphology_not_researched:memory_ganglion"], sim.command_log[0]["reasons"])

    def test_population_grows_into_empty_homes_and_costs_nutrient(self):
        sim = make_sim([{"at": 0, "do": "construct", "building": "shelter", "id": "home_4"}],
                       patch={"starting_state": {"inventory": {"growth_nutrient": 7}}})
        run_until(sim, 6 * 60)
        self.assertGreaterEqual(sim.residences["home_4"].population, 4)
        # 4 GN reserve policy: growth stops once 4 remain; each unit funds four organisms.
        self.assertGreaterEqual(sim.store("core").get("growth_nutrient"), 4)


class MorphologyTests(unittest.TestCase):
    PATCH = {
        "starting_state": {
            "inventory": {"growth_nutrient": 10, "prepared_silica": 10, "repair_enzyme": 5, "staple": 30},
            "residences": [
                {"id": "home_1", "tier": "shelter", "population": 8, "district": "core"},
                {"id": "home_2", "tier": "shelter", "population": 8, "district": "core"},
                {"id": "home_3", "tier": "stable", "population": 12, "district": "core"},
            ],
        }
    }

    def test_research_takes_goods_and_nursery_work_then_express_pauses_workforce(self):
        sim = make_sim([
            {"at": 0, "do": "research", "morphology": "mineral_jaw"},
            {"at": 0, "do": "express", "morphology": "mineral_jaw", "residence": "home_3", "retry": True},
        ], patch=self.PATCH)
        run_until(sim, 10)
        self.assertEqual(6, sim.store("core").get("growth_nutrient"))
        self.assertNotIn("mineral_jaw", sim.researched)
        run_until(sim, 15 * 60 + 5)            # 60 work at 4 WP/min
        self.assertIn("mineral_jaw", sim.researched)
        expressed_at = next(e["executed_at"] for e in sim.command_log if e["do"] == "express")
        self.assertEqual(0.0, sim.residences["home_3"].workforce(sim.defs, expressed_at + 10)[1])
        self.assertFalse(sim.has_capability("core", "mineral_jaw"))
        run_until(sim, expressed_at + 91)
        self.assertTrue(sim.has_capability("core", "mineral_jaw"))
        self.assertEqual(8.0, sim.residences["home_3"].workforce(sim.defs, sim.second)[1])

    def test_express_rejects_wrong_tier(self):
        sim = make_sim([
            {"at": 0, "do": "research", "morphology": "mineral_jaw"},
            {"at": 0, "do": "express", "morphology": "mineral_jaw", "residence": "home_1", "when": {"researched": "mineral_jaw"}},
        ], patch=self.PATCH)
        run_until(sim, 20 * 60)
        failure = next(e for e in sim.command_log if e["do"] == "express")
        self.assertEqual(["tier_cannot_express:shelter"], failure["reasons"])


class TradeTests(unittest.TestCase):
    def test_purchase_arrives_after_round_trip(self):
        sim = make_sim([{"at": 600, "do": "trade", "buy": {"carbonate": 5}}])
        run_until(sim, 600)
        self.assertEqual(0, sim.store("core").get("stored_value"))
        self.assertEqual(6, sim.store("core").get("carbonate"))
        run_until(sim, 839)
        self.assertEqual(6, sim.store("core").get("carbonate"))
        run_until(sim, 840)
        self.assertEqual(11, sim.store("core").get("carbonate"))

    def test_partner_stock_accrues_over_time(self):
        sim = make_sim([{"at": 0, "do": "trade", "buy": {"carbonate": 1}}])
        run_until(sim, 0)
        self.assertEqual(["partner_stock_insufficient:carbonate"], sim.command_log[0]["reasons"])

    def test_barter_cannot_overdraw_value(self):
        sim = make_sim([{"at": 720, "do": "trade", "buy": {"carbonate": 6}}])
        run_until(sim, 720)
        self.assertTrue(sim.command_log[0]["reasons"][0].startswith("insufficient_value"))

    def test_contract_reward_and_price_change(self):
        sim = make_sim([{"at": 60, "do": "deliver_contract", "contract": "fertile_exchange"}],
                       patch={"starting_state": {"inventory": {"growth_nutrient": 8}}})
        run_until(sim, 60)
        self.assertEqual(0, sim.store("core").get("growth_nutrient"))
        run_until(sim, 300)
        self.assertEqual(18, sim.store("core").get("carbonate"))
        self.assertEqual("completed", sim.trade.contracts["fertile_exchange"])
        self.assertAlmostEqual(4 * 0.85, sim.trade.buy_price("carbonate"))


class CommandTests(unittest.TestCase):
    def test_unknown_command_fails_with_reason(self):
        sim = make_sim([{"at": 0, "do": "teleport"}])
        run_until(sim, 0)
        self.assertEqual(["unknown_command:teleport"], sim.command_log[0]["reasons"])

    def test_retry_records_waiting_time(self):
        sim = make_sim([{"at": 0, "do": "trade", "buy": {"carbonate": 2}, "retry": True}])
        run_until(sim, 300)
        entry = sim.command_log[0]
        self.assertTrue(entry["ok"])
        self.assertEqual(240, entry["executed_at"])
        self.assertAlmostEqual(240, entry["waited"]["partner_stock_insufficient:carbonate"])

    def test_when_trigger_delays_attempt(self):
        sim = make_sim([
            {"at": 0, "do": "construct", "building": "culture_bed", "id": "bed_2"},
            {"at": 0, "do": "pause", "target": "bed_2", "when": {"built": "bed_2"}},
        ])
        run_until(sim, 200)
        self.assertTrue(sim.facilities["bed_2"].paused)
        self.assertEqual({}, sim.command_log[-1]["waited"])

    def test_great_work_refuses_to_begin_with_named_blockers(self):
        sim = make_sim([{"at": 0, "do": "begin_great_work"}])
        run_until(sim, 0)
        reasons = sim.command_log[0]["reasons"]
        self.assertIn("needs_residence:memory", reasons)
        self.assertIn("needs_active_service:memory_circle", reasons)
        self.assertTrue(any(r.startswith("needs_contract_resolved") for r in reasons))


class GreatWorkStageTests(unittest.TestCase):
    def test_stages_open_in_order_and_need_materials_then_labour(self):
        patch = {
            "starting_state": {
                "inventory": {"carbonate": 40, "fired_ceramic": 30, "habitat_composite": 30, "repair_enzyme": 10,
                              "pigment_ornament": 10, "staple": 200, "balanced_gel": 200},
                "residences": [
                    {"id": "home_1", "tier": "shelter", "population": 8, "district": "core"},
                    {"id": "home_2", "tier": "shelter", "population": 8, "district": "core"},
                    {"id": "home_3", "tier": "shelter", "population": 8, "district": "core"},
                    {"id": "home_4", "tier": "memory", "population": 20, "district": "core"},
                ],
            }
        }
        sim = make_sim(patch=patch)
        run_until(sim, 0)
        sim.begin_great_work(0)
        run_until(sim, 1)
        self.assertEqual(24, sim.store("core").get("fired_ceramic"))    # only stage I's 6 Ceramic delivered
        while sim.great_work.completed_at is None and sim.second < 5400:
            sim.step()
        self.assertIsNotNone(sim.great_work.completed_at)
        path = sim.diag.critical_path()
        opened = [s["opened_at"] for s in path["stages"]]
        self.assertEqual(sorted(opened), opened)
        # 6 free General build 115 physical work; 12 Coordinators build 60 coordinator work.
        self.assertGreaterEqual(sim.great_work.completed_at, int(115 / 6 * 60))


if __name__ == "__main__":
    unittest.main()
