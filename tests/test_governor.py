"""Tests for the repeating calendar, the early export market and the adaptive reference governor."""
from __future__ import annotations

import hashlib
import json
import unittest

from economy.engine import Simulation, load_definitions
from economy.engine.environment import Environment
from economy.governor import Governor, load_governor_config, observe, summarise_log

from tests.helpers import run_until


def governed_run(until=None):
    sim = Simulation(load_definitions(), {"id": "governor", "commands": []})
    governor = Governor(load_governor_config())
    sim.controllers.append(governor)
    report = sim.run(until=until)
    return sim, governor, report


class CalendarTests(unittest.TestCase):
    def test_calendar_wraps_to_bloom_at_90_minutes_and_deposits_recur(self):
        env = Environment(load_definitions())
        self.assertEqual("dry", env.season_at(5399)["id"])
        self.assertEqual("bloom", env.season_at(5400)["id"])
        self.assertEqual("high_water", env.season_at(5400 + 1080)["id"])
        for second in range(0, 5400 + 1081):
            env.step(second, 1.0)
        self.assertEqual(2, sum(1 for _, patch, _ in env.deposit_log if patch == "phosphate_bed"))

    def test_legacy_overlay_keeps_a_linear_calendar(self):
        from tests.helpers import make_defs
        env = Environment(make_defs())
        self.assertEqual("dry", env.season_at(5400)["id"])


class ExportMarketTests(unittest.TestCase):
    def test_partner_demand_for_staple_and_biomass_accrues_to_a_cap(self):
        sim = Simulation(load_definitions(), {"id": "t", "commands": []})
        self.assertEqual(0, sim.trade.partner_demand("staple", 0))
        self.assertEqual(2, sim.trade.partner_demand("biomass", 600))       # 0.2/min x 10 min
        self.assertEqual(20, sim.trade.partner_demand("staple", 7200))      # capped
        self.assertEqual(12, sim.trade.partner_demand("growth_nutrient", 0))  # no per_minute: whole cap at once

    def test_selling_biomass_buys_carbonate(self):
        sim = Simulation(load_definitions(), {"id": "t", "commands": [
            {"at": 900, "do": "trade", "sell": {"biomass": 2}, "buy": {"carbonate": 5}}]})
        sim.store("core").put({"biomass": 5})
        run_until(sim, 900)
        self.assertTrue(sim.command_log[-1]["ok"], sim.command_log[-1])
        self.assertEqual(2, sim.trade.sold["biomass"])
        self.assertEqual(2, sim.store("core").get("stored_value"))   # 20 + 2 x 1 (Biomass) - 5 x 4 (Carbonate)


class TimeStampTests(unittest.TestCase):
    def test_minutes_parser_handles_three_digit_minutes(self):
        from economy.sweep import _minutes
        self.assertAlmostEqual(100 + 19 / 60, _minutes("100:19"))
        self.assertAlmostEqual(5.5, _minutes("05:30"))


class GovernorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sim, cls.governor, cls.report = governed_run()

    def test_governor_is_deterministic(self):
        def digest(report, governor):
            return hashlib.sha256(json.dumps([report["outcome"], report["trade"], governor.log], sort_keys=True, default=str).encode()).hexdigest()
        _, governor, report = governed_run()
        self.assertEqual(digest(self.report, self.governor), digest(report, governor))

    def test_every_governor_action_is_a_logged_legal_command(self):
        governor_commands = [e for e in self.sim.command_log if e.get("source") == "governor"]
        self.assertEqual(len(self.governor.log), len(governor_commands))
        self.assertTrue(all("reason" in e and e["reason"] for e in self.governor.log))
        allowed = {"construct", "evolve", "research", "express", "set_recipe", "pause", "resume", "set_labour_priority",
                   "set_policy", "trade", "deliver_contract", "decline_contract", "begin_great_work"}
        self.assertTrue({e["command"]["do"] for e in self.governor.log} <= allowed)

    def test_governor_never_changes_builder_allocation_or_bypasses_the_food_emergency(self):
        for entry in self.governor.log:
            command = entry["command"]
            self.assertFalse(command["do"] == "set_policy" and command.get("policy") == "builder_wp")
            self.assertFalse(command["do"] == "set_labour_priority" and command.get("target") == "builders")
        self.assertEqual(2.0, self.sim.policies["builder_wp"])

    def test_buildings_still_come_only_from_paid_sites(self):
        starting = {e["id"] for e in self.sim.defs["starting_state"]["buildings"]}
        for facility_id in self.sim.facilities:
            if facility_id not in starting:
                site = self.sim.sites[facility_id]
                for resource, quantity in site.cost.items():
                    self.assertEqual(quantity, site.delivered.get(resource, 0))

    def test_observation_is_the_player_view(self):
        sim = Simulation(load_definitions(), {"id": "t", "commands": []})
        run_until(sim, 0)
        view = observe(sim)
        self.assertEqual({"second", "season", "next_season", "seconds_to_next_season", "store", "food_minutes", "food_emergency",
                          "workforce", "builders", "facilities", "sites", "residences", "services", "researched",
                          "research_queue", "trade", "great_work", "policies"}, set(view))

    def test_log_summary_lists_build_order(self):
        summary = summarise_log(self.governor)
        self.assertTrue(summary["build_order"])
        self.assertEqual(0, summary["failed_actions"])


if __name__ == "__main__":
    unittest.main()


class GovernorV2AndSweepV3Tests(unittest.TestCase):
    """Rich 2026-10-02T1746Z: test the four design changes; the instrument must adapt to quoted costs fairly."""

    def _run(self, defs, version="v2", until=None):
        from economy.engine.definitions import read_json
        sim = Simulation(defs, {"id": "governor", "commands": []})
        governor = Governor(read_json(f"economy/data/governors/reference_governor_{version}.json"))
        sim.controllers.append(governor)
        return sim, governor, sim.run(until=until)

    def test_governor_v2_plays_the_unchanged_rules_exactly_like_v1(self):
        _, g1, r1 = self._run(load_definitions(), "v1", until=3600)
        _, g2, r2 = self._run(load_definitions(), "v2", until=3600)
        self.assertEqual([(e["t"], e["command"]) for e in g1.log], [(e["t"], e["command"]) for e in g2.log])

    def test_carbonate_only_first_cutter_is_built_early(self):
        defs = load_definitions()
        defs["buildings"]["carbonate_cutter"]["first_instance"] = {"cost": {"carbonate": 3}}
        _, governor, _ = self._run(defs, until=900)
        built = [e for e in governor.log if e["command"].get("do") == "construct" and e["command"]["building"] == "carbonate_cutter"]
        self.assertTrue(built and built[0]["t"] < 600)

    def test_level_criteria_override_widens_the_reef_window(self):
        from economy.sweep import evaluate
        summary = {"first_symbiotic": "90:00", "symbiotic_devolutions": 0, "devolutions": 0, "staple_shortage_minutes": 0,
                   "upkeep_unpaid_minutes": 0, "reef_minutes": 140.0, "reef_completed_at": "140:00"}
        self.assertIn("reef_too_late", evaluate(summary, {"reef_window_minutes": [100, 120]}))
        self.assertEqual([], evaluate(summary, {"reef_window_minutes": [100, 150]}))
