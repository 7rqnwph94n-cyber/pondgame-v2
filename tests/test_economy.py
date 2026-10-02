from pathlib import Path
import unittest

from economy.model import EconomySimulation, load_config, validate_config, workforce_at


CONFIG_PATH = Path(__file__).parents[1] / "economy" / "data" / "verdant_v0_1.json"


class EconomyConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(CONFIG_PATH)

    def test_config_is_internally_consistent(self):
        self.assertEqual([], validate_config(self.config))

    def test_seasons_cover_the_scenario_without_gaps(self):
        seasons = self.config["seasons"]
        self.assertEqual(0, seasons[0]["start"])
        for left, right in zip(seasons, seasons[1:]):
            self.assertEqual(left["end"], right["start"])
        self.assertGreater(seasons[-1]["end"], self.config["scenario"]["duration_seconds"])

    def test_great_work_totals_match_design_document(self):
        totals = {}
        for stage in self.config["great_work"]["stages"]:
            for resource, quantity in stage["cost"].items():
                totals[resource] = totals.get(resource, 0) + quantity
        self.assertEqual(30, totals["carbonate"])
        self.assertEqual(24, totals["fired_ceramic"])
        self.assertEqual(24, totals["habitat_composite"])
        self.assertEqual(8, totals["repair_enzyme"])
        self.assertEqual(6, totals["pigment_ornament"])

    def test_reference_residences_provide_all_workforce_classes(self):
        residences = self.config["reference_plan"]["residence_events"][-1]["set"]
        workforce = workforce_at(self.config, residences)
        self.assertEqual({"general", "adapted", "artisan", "coordinator"}, set(workforce))
        self.assertGreaterEqual(workforce["general"], 20)
        self.assertGreaterEqual(workforce["coordinator"], 6)


class ReferenceSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config(CONFIG_PATH)
        cls.result = EconomySimulation(cls.config).run()

    def test_inventory_never_goes_negative(self):
        for resource, minimum in self.result.minimum_inventory.items():
            self.assertGreaterEqual(minimum, -1e-6, resource)

    def test_simulation_records_each_minute(self):
        expected = self.config["scenario"]["duration_seconds"] // 60 + 1
        self.assertEqual(expected, len(self.result.snapshots))

    def test_core_production_chains_operate(self):
        for recipe in (
            "culture_bed", "nutrient_washer", "ceramic_kiln",
            "composite_workshop", "waste_digester", "artisan_organ"
        ):
            self.assertGreater(self.result.completed_cycles.get(recipe, 0), 0, recipe)

    def test_great_work_completes_in_target_window(self):
        self.assertIsNotNone(self.result.great_work_completed_at)
        self.assertGreaterEqual(self.result.great_work_completed_at, 78 * 60)
        self.assertLessEqual(self.result.great_work_completed_at, 88 * 60)

    def test_food_shortage_is_small_or_zero(self):
        self.assertLessEqual(self.result.shortages.get("staple", 0.0), 2.0)
        self.assertLessEqual(self.result.shortages.get("balanced_gel", 0.0), 1.0)

    def test_reference_plan_pays_all_planned_investments(self):
        non_food_shortages = {
            resource: quantity
            for resource, quantity in self.result.shortages.items()
            if resource not in {"staple", "balanced_gel", "pigment_ornament"}
        }
        self.assertEqual({}, non_food_shortages)


if __name__ == "__main__":
    unittest.main()
