"""Player-facing competitor diagnosis on the recorded opening, without Autoplay."""
import json
import unittest
from pathlib import Path
from economy.bridge import Session, handle, input_consumers
ROOT = Path(__file__).resolve().parents[1]

class ConsumerTests(unittest.TestCase):
    def setUp(self):
        self.s = Session([str(ROOT / "economy/data/experiments/candidate_playable_slice_v1.json")])
        plan = json.loads((ROOT / "docs/milestone_b/human_opening_2026-10-04.plan.json").read_text())
        for at, cmd in plan:
            while self.s.sim.second < at:
                self.s.advance(min(600, at - self.s.sim.second))
            self.assertTrue(self.s.command(cmd)["ok"])
        while self.s.sim.second < 2700:
            self.s.advance(min(600, 2700 - self.s.sim.second))

    def test_shelter_names_real_same_store_recipe_competitor(self):
        sites = self.s.view()["sites"]
        shelter = next(sid for sid, row in sites.items() if row["target"] == "shelter")
        reply = handle(self.s, {"op": "inspect", "target": shelter})
        blocker = next(b for b in reply["blockers"] if b["code"] == "waiting_input")
        rows = blocker["params"]["consumers"]["biomass"]
        culture = next(r for r in rows if r["building"] == "culture_bed")
        self.assertIn("staple", culture["outputs"])
        f = self.s.sim.facilities[culture["entity"]]
        self.assertEqual(f.held_inputs.get("biomass", 0), culture["held"])
        self.assertEqual(self.s.defs["recipes"][f.recipe_id]["inputs"]["biomass"], culture["per_cycle"])
        f.paused = True
        paused = handle(self.s, {"op": "inspect", "target": shelter})
        self.assertNotIn(culture["entity"], [r["entity"] for b in paused["blockers"] for r in b["params"].get("consumers", {}).get("biomass", [])])

    def test_excludes_other_store_self_and_inactive_facilities(self):
        f = next(f for f in self.s.sim.facilities.values() if f.building_id == "culture_bed")
        self.assertEqual({}, input_consumers(self.s.sim, "another_district", {"biomass": 1}))
        rows = input_consumers(self.s.sim, f.district, {"biomass": 1}, f.id)
        self.assertNotIn(f.id, [r["entity"] for r in rows.get("biomass", [])])
        f.status = "no_workforce"
        self.assertNotIn(f.id, [r["entity"] for r in input_consumers(self.s.sim, f.district, {"biomass": 1}).get("biomass", [])])
