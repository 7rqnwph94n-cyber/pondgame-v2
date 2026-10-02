"""The engine must match docs/exchange/contracts/presentation_states.json (consumed by Codex)."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from economy.engine import Simulation, load_definitions, load_plan
from economy.engine import construction as C, production as P, residences as R, simulation as S

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "exchange" / "contracts" / "presentation_states.json"


@unittest.skipUnless(CONTRACT.exists(), "exchange contract not present on this branch")
class PresentationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.report = Simulation(load_definitions(), load_plan(ROOT / "economy" / "data" / "plans" / "verdant_reference_c.json")).run()

    def test_enums_match_engine_constants(self):
        enums = self.contract["enums"]
        self.assertEqual(enums["facility_status"], [P.RUNNING, P.IDLE, P.NO_INPUT, P.NO_WORKFORCE, P.ENVIRONMENT,
                                                    P.PATCH_DEPLETED, P.MORPHOLOGY_MISSING, P.PAUSED])
        self.assertEqual(enums["construction_site_state"], [C.AWAITING_MATERIALS, C.AWAITING_LABOUR, C.IN_PROGRESS, C.COMPLETE, C.CANCELLED])
        self.assertEqual(enums["residence_condition"], [R.NORMAL, R.STRAINED, R.DORMANT])
        self.assertEqual(enums["builder_state"], [S.BUILDERS_PROTECTED, S.BUILDERS_PREEMPTED, S.BUILDERS_IDLE, S.BUILDERS_DISABLED])
        self.assertEqual(enums["maintenance_upkeep_state"], [S.NOT_ENFORCED, S.GRACE, S.PAID, S.UNPAID])
        self.assertEqual(enums["residence_tier"], load_definitions()["residence_rules"]["tier_order"])

    def test_snapshots_expose_contract_fields_and_only_contract_values(self):
        fields = self.contract["snapshot_fields"]
        enums = self.contract["enums"]
        for snapshot in self.report["snapshots"]:
            for residence in snapshot["residences"].values():
                self.assertEqual(set(fields["residences.<id>"]), set(residence))
                self.assertIn(residence["condition"], enums["residence_condition"])
                self.assertIn(residence["tier"], enums["residence_tier"])
                if residence["evolution"]:
                    self.assertEqual(set(fields["residences.<id>.evolution"]), set(residence["evolution"]))
            for facility in snapshot["facilities"].values():
                self.assertEqual(set(fields["facilities.<id>"]), set(facility))
                self.assertIn(facility["status"], enums["facility_status"])
            for site in snapshot["sites"].values():
                self.assertEqual(set(fields["sites.<id>"]), set(site))
                self.assertIn(site["state"], enums["construction_site_state"])
            for builders in snapshot["builders"].values():
                self.assertEqual(set(fields["builders.<district>"]), set(builders))
                self.assertIn(builders["state"], enums["builder_state"])
            self.assertEqual(set(fields["food_emergency"]), set(snapshot["food_emergency"]))
            self.assertIn(snapshot["maintenance_upkeep"], enums["maintenance_upkeep_state"])


if __name__ == "__main__":
    unittest.main()
