"""Provisional slice overlay (Rich 2026-10-04T1039Z) and the patch reserve_cap it relies on."""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from economy.engine import load_definitions
from economy.engine.definitions import validate_definitions
from economy.engine.environment import Environment
from economy.sweep import parameter_levels

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "economy" / "data" / "experiments"
SLICE = EXP / "candidate_playable_slice_v1.json"


class ReserveCapTests(unittest.TestCase):
    def _env(self, cap):
        defs = load_definitions()
        defs["patches"]["surface"] = {"reserve": 5, "renewal_per_minute": 6.0, **({"reserve_cap": cap} if cap else {})}
        return Environment(defs)

    def test_renewal_stops_at_the_cap(self):
        env = self._env(8)
        for second in range(600):
            env.step(second, 1.0)
        self.assertAlmostEqual(8.0, env.reserves["surface"])

    def test_without_a_cap_renewal_is_unchanged(self):
        env = self._env(None)
        for second in range(60):
            env.step(second, 1.0)
        self.assertAlmostEqual(11.0, env.reserves["surface"], places=6)

    def test_extraction_below_the_cap_renews_back_to_it(self):
        env = self._env(8)
        env.reserves["surface"] = 2.0
        for second in range(30):
            env.step(second, 1.0)
        self.assertAlmostEqual(5.0, env.reserves["surface"], places=6)

    def test_validation(self):
        defs = load_definitions()
        defs["patches"]["surface_test"] = {"reserve": 10, "reserve_cap": 5}
        self.assertTrue(any("below its starting reserve" in e for e in validate_definitions(defs)))
        defs["patches"]["surface_test"] = {"renewable": True, "reserve_cap": 5}
        self.assertTrue(any("needs a finite reserve" in e for e in validate_definitions(defs)))


class SliceOverlayTests(unittest.TestCase):
    def test_overlay_is_exactly_playable_plus_l3_plus_capped_renewal(self):
        """Guard against drift: the slice overlay must equal its documented composition."""
        def apply(defs, sets):
            for path, value in sets.items():
                keys = path.split(".")
                target = defs
                for key in keys[:-1]:
                    target = target.setdefault(key, {})
                target[keys[-1]] = copy.deepcopy(value)
        expected = load_definitions(overlays=[EXP / "candidate_playable_v1.json"])
        ws = json.loads((EXP / "workforce_scale_v1_playable.json").read_text(encoding="utf-8"))
        l3 = next(l for l in parameter_levels(ws["parameters"][0]) if l["label"] == "L3_+food_-1")["set"]
        apply(expected, l3)
        apply(expected, {"patches.surface_carbonate.renewal_per_minute": 0.2, "patches.surface_carbonate.reserve_cap": 12})
        actual = load_definitions(overlays=[SLICE])
        for section in ("buildings", "recipes", "morphologies", "construction_rules", "population", "residences"):
            self.assertEqual(expected[section], actual[section], section)
        for key in ("reserve", "renewal_per_minute", "reserve_cap"):
            self.assertEqual(expected["patches"]["surface_carbonate"][key], actual["patches"]["surface_carbonate"][key])

    def test_baseline_is_untouched(self):
        base = load_definitions()
        self.assertNotIn("surface_carbonate", base["patches"])
        self.assertEqual({"general": 3}, base["buildings"]["sediment_dredge"]["jobs"])
        self.assertNotIn("reserve_cap", json.dumps(base["patches"]))

    def test_overlay_states_it_is_provisional_and_the_reef_limit(self):
        meta = json.loads(SLICE.read_text(encoding="utf-8"))
        self.assertIn("PROVISIONAL", meta["status"])
        self.assertIn("Reef is NOT reachable", meta["status"])


class ClientLaunchTests(unittest.TestCase):
    def test_client_launches_the_provisional_slice_overlay(self):
        import configparser
        import json as _json
        cfg = configparser.ConfigParser()
        cfg.read(ROOT / "client" / "settings.cfg", encoding="utf-8")
        overlays = _json.loads(cfg["bridge"]["overlays"])
        self.assertEqual(["economy/data/experiments/candidate_playable_slice_v1.json",
                          "economy/data/experiments/empty_settlement_start_v1.json",
                          "economy/data/experiments/spatial_roads_v1.json",
                          "economy/data/experiments/current_lanes_v1.json"], overlays)
        from economy.bridge import Session, handle
        hello = handle(Session([str(ROOT / o) for o in overlays]), {"id": 1, "op": "hello"})
        self.assertEqual(["candidate_playable_slice_v1", "empty_settlement_start_v1",
                          "spatial_roads_v1", "current_lanes_v1"], hello["overlays"])
        self.assertEqual("current", hello["spatial"]["mode"])
        self.assertFalse(hello["autoplay_available"])
        self.assertEqual("true", cfg["presentation"]["submerged"])
