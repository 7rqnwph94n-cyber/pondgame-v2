"""The local simulation bridge used by the Godot client (ADR 0001)."""
from __future__ import annotations

import json
import socket
import threading
import time
import unittest
from pathlib import Path

from economy.bridge import MAX_ADVANCE, PROTOCOL, Session, handle, serve

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "exchange" / "contracts" / "sim_bridge.json"


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.s = Session()

    def test_hello_describes_protocol_and_definitions(self):
        reply = handle(self.s, {"id": 1, "op": "hello"})
        self.assertTrue(reply["ok"])
        self.assertEqual(PROTOCOL, reply["protocol"])
        self.assertEqual(1, reply["id"])
        self.assertIn("sediment_dredge", reply["buildings"])
        self.assertEqual(["shelter", "stable", "symbiotic", "memory"], reply["residence_tiers"])

    def test_advance_steps_fixed_seconds_and_is_capped(self):
        view = handle(self.s, {"id": 1, "op": "advance", "seconds": 90})["view"]
        self.assertEqual(91, view["second"])     # the session starts after the second-0 step
        view = handle(self.s, {"id": 2, "op": "advance", "seconds": 10_000})["view"]
        self.assertEqual(91 + MAX_ADVANCE, view["second"])

    def test_advance_zero_is_a_pause(self):
        before = handle(self.s, {"id": 1, "op": "view"})["view"]["second"]
        after = handle(self.s, {"id": 2, "op": "advance", "seconds": 0})["view"]["second"]
        self.assertEqual(before, after)

    def test_player_commands_obey_the_rules(self):
        ok = handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "sediment_dredge", "id": "d1"}})
        self.assertTrue(ok["ok"])
        bad = handle(self.s, {"id": 2, "op": "command", "cmd": {"do": "construct", "building": "no_such_building", "id": "x"}})
        self.assertFalse(bad["ok"])
        self.assertTrue(bad["reasons"])
        malformed = handle(self.s, {"id": 3, "op": "command", "cmd": "build"})
        self.assertEqual(["malformed_command"], malformed["reasons"])

    def test_no_building_appears_without_its_site_being_paid_and_built(self):
        handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "sediment_dredge", "id": "d1"}})
        view = handle(self.s, {"id": 2, "op": "view"})["view"]
        self.assertIn("d1", view["sites"])
        self.assertNotIn("d1", view["facilities"])

    def test_events_are_delivered_once(self):
        handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "sediment_dredge", "id": "d1"}})
        first = handle(self.s, {"id": 2, "op": "view"})["view"]["events"]
        second = handle(self.s, {"id": 3, "op": "view"})["view"]["events"]
        self.assertTrue(any("d1" in e for e in first))
        self.assertEqual([], second)

    def test_inspector_explains_entities(self):
        handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "ceramic_kiln", "id": "k1"}})
        site = handle(self.s, {"id": 2, "op": "inspect", "target": "k1"})
        self.assertEqual("site", site["kind"])
        self.assertEqual("k1", site["entity"])
        self.assertEqual(2, site["id"])                   # the request id is never shadowed
        self.assertTrue(site["blocked"])
        self.assertTrue(any("waiting for" in r for r in site["reasons"]))
        home = handle(self.s, {"id": 3, "op": "inspect", "target": "home_1"})
        self.assertEqual("residence", home["kind"])
        self.assertIn("next tier needs service", " ".join(home["reasons"]))
        reef = handle(self.s, {"id": 4, "op": "inspect", "target": "great_work"})
        self.assertIn("needs_residence:memory", reef["reasons"])
        self.assertFalse(handle(self.s, {"id": 5, "op": "inspect", "target": "nope"})["ok"])

    def test_autoplay_toggles_the_reference_governor(self):
        self.assertTrue(handle(self.s, {"id": 1, "op": "autoplay", "enabled": True})["autoplay"])
        view = handle(self.s, {"id": 2, "op": "advance", "seconds": 60})["view"]
        self.assertTrue(view["autoplay"])
        self.assertTrue(any("[governor]" in e for e in view["events"]))
        self.assertFalse(handle(self.s, {"id": 3, "op": "autoplay", "enabled": False})["autoplay"])

    def test_bridge_is_deterministic(self):
        def run():
            s = Session()
            handle(s, {"id": 1, "op": "autoplay", "enabled": True})
            return json.dumps(handle(s, {"id": 2, "op": "advance", "seconds": 600})["view"], sort_keys=True, default=str)
        self.assertEqual(run(), run())

    def test_unknown_ops_and_errors_still_reply(self):
        self.assertEqual(["unknown_op:bogus"], handle(self.s, {"id": 1, "op": "bogus"})["reasons"])
        reply = handle(self.s, {"id": 2, "op": "advance", "seconds": "lots"})
        self.assertFalse(reply["ok"])
        self.assertTrue(reply["reasons"][0].startswith("bridge_error:"))


class TransportTests(unittest.TestCase):
    def test_json_lines_over_tcp(self):
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", 0))
            port = probe.getsockname()[1]
        thread = threading.Thread(target=serve, args=(Session(), port), daemon=True)
        thread.start()
        for _ in range(100):
            try:
                conn = socket.create_connection(("127.0.0.1", port), timeout=5)
                break
            except OSError:
                time.sleep(0.05)
        with conn, conn.makefile("rwb") as stream:
            for i, request in enumerate([{"op": "hello"}, {"op": "advance", "seconds": 5}, {"op": "quit"}]):
                stream.write(json.dumps({"id": i, **request}).encode() + b"\n")
                stream.flush()
                reply = json.loads(stream.readline())
                self.assertEqual(i, reply["id"])
                self.assertTrue(reply["ok"])
        thread.join(timeout=5)
        self.assertFalse(thread.is_alive())


@unittest.skipUnless(CONTRACT.exists(), "sim_bridge contract not present on this branch")
class BridgeContractTests(unittest.TestCase):
    def test_contract_matches_the_bridge(self):
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(PROTOCOL, contract["protocol"])
        s = Session()
        for op, spec in contract["ops"].items():
            request = {"id": 1, "op": op, **spec.get("example", {})}
            if op == "quit":
                continue
            reply = handle(s, request)
            self.assertTrue(reply["ok"], (op, reply))
            fields = reply["view"] if "view" in reply else reply
            for field in spec.get("reply_fields", []):
                self.assertIn(field, fields, (op, field))


if __name__ == "__main__":
    unittest.main()


class BlockerCodeTests(unittest.TestCase):
    """sim_bridge contract v2: ordered, structured blockers with stable codes (Codex binds icons to codes)."""

    def setUp(self):
        from economy.bridge import BLOCKER_CODES
        self.codes = set(BLOCKER_CODES)
        self.s = Session()

    def _all_blockers(self, view):
        for kind in ("facilities", "sites", "residences"):
            for entity in view[kind].values():
                yield from entity["blockers"]

    def test_view_entities_carry_valid_structured_blockers(self):
        handle(self.s, {"id": 1, "op": "autoplay", "enabled": True})
        view = handle(self.s, {"id": 2, "op": "advance", "seconds": 600})["view"]
        seen = list(self._all_blockers(view))
        self.assertTrue(seen)
        for b in seen:
            self.assertIn(b["code"], self.codes)
            self.assertIsInstance(b["params"], dict)
            self.assertTrue(b["text"])

    def test_paused_and_unstaffed_and_waiting_input(self):
        handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "ceramic_kiln", "id": "k1"}})
        site = handle(self.s, {"id": 2, "op": "inspect", "target": "k1"})
        self.assertIn(site["blockers"][0]["code"], ("waiting_input", "unstaffed"))
        survey = handle(self.s, {"id": 3, "op": "inspect", "target": "survey_1"})
        handle(self.s, {"id": 4, "op": "command", "cmd": {"do": "pause", "target": "survey_1"}})
        paused = handle(self.s, {"id": 5, "op": "inspect", "target": "survey_1"})
        self.assertEqual("paused", paused["blockers"][0]["code"])          # most actionable first
        self.assertEqual([b["text"] for b in paused["blockers"]], paused["reasons"])   # v1 text kept

    def test_waiting_input_lists_missing_goods(self):
        handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "ceramic_kiln", "id": "k1"}})
        handle(self.s, {"id": 2, "op": "command", "cmd": {"do": "construct", "building": "ceramic_kiln", "id": "k2"}})
        reply = handle(self.s, {"id": 3, "op": "inspect", "target": "k2"})
        waiting = [b for b in reply["blockers"] if b["code"] == "waiting_input"]
        self.assertTrue(waiting and waiting[0]["params"]["goods"])

    def test_residence_services_are_not_reported_twice(self):
        handle(self.s, {"id": 1, "op": "command", "cmd": {"do": "evolve", "residence": "home_1"}})
        view = handle(self.s, {"id": 2, "op": "advance", "seconds": 30})["view"]
        texts = [b["text"] for b in view["residences"]["home_1"]["blockers"]]
        self.assertEqual(len(texts), len(set(texts)))
        self.assertFalse(any(b["code"] == "evolution_blocked" and b["params"]["blocker"].startswith("service:")
                             for b in view["residences"]["home_1"]["blockers"]))

    def test_reef_blockers_are_coded(self):
        reply = handle(self.s, {"id": 1, "op": "inspect", "target": "great_work"})
        self.assertTrue(all(b["code"] == "great_work_blocked" for b in reply["blockers"]))


class LabourPriorityLegibilityTests(unittest.TestCase):
    """Charter gate 2: a player can see and fix a starved Dredge through labour priority."""

    def test_view_and_inspector_expose_labour_priority_and_raising_it_staffs_first(self):
        s = Session(["economy/data/experiments/candidate_playable_v1.json"])
        handle(s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": "sediment_dredge", "id": "d1"}})
        view = handle(s, {"id": 2, "op": "advance", "seconds": 200})["view"]
        self.assertIn("d1", view["facilities"])
        self.assertIn("labour_priority", view["facilities"]["d1"])
        self.assertFalse(view["facilities"]["d1"]["labour_priority_overridden"])
        ok = handle(s, {"id": 3, "op": "command", "cmd": {"do": "set_labour_priority", "target": "d1", "value": 0}})
        self.assertTrue(ok["ok"])
        reply = handle(s, {"id": 4, "op": "inspect", "target": "d1"})
        self.assertEqual(0, reply["labour_priority"])
        self.assertTrue(reply["labour_priority_overridden"])
        unstaffed = [b for b in reply["blockers"] if b["code"] == "unstaffed"]
        self.assertTrue(all(not b["params"]["can_raise_priority"] for b in unstaffed))


class HumanOpeningFindingsTests(unittest.TestCase):
    """Fixes for confusions found in the 2026-10-04 human opening (no Autoplay)."""

    def test_home_says_what_evolution_needs_and_what_it_costs_in_workers(self):
        s = Session()
        for building, sid in (("waste_collector", "w"), ("clean_flow_node", "c")):
            handle(s, {"id": 1, "op": "command", "cmd": {"do": "construct", "building": building, "id": sid}})
        handle(s, {"id": 2, "op": "advance", "seconds": 400})
        home = handle(s, {"id": 3, "op": "inspect", "target": "home_1"})
        needs = [b for b in home["blockers"] if b["code"] == "waiting_input" and b["params"].get("purpose") == "evolution"]
        self.assertTrue(needs and "growth_nutrient" in needs[0]["params"]["goods"])
        self.assertEqual("stable", home["next_tier"])
        self.assertEqual({"general": -6, "adapted": 8}, home["evolution_workforce_change"])
        self.assertFalse(home["evolution_ready"])

    def test_colony_says_why_population_is_not_growing(self):
        s = Session()
        view = handle(s, {"id": 1, "op": "advance", "seconds": 120})["view"]
        self.assertIn("colony_blockers", view)
        for b in view["colony_blockers"]:
            self.assertEqual("growth_blocked", b["code"])
            self.assertIn(b["params"]["reason"], ("no_free_capacity", "basic_needs_unsupplied", "growth_nutrient_unavailable"))


@unittest.skipUnless(CONTRACT.exists(), "sim_bridge contract not present on this branch")
class BlockerContractTests(unittest.TestCase):
    def test_contract_codes_match_the_bridge(self):
        from economy.bridge import BLOCKER_CODES
        contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        self.assertGreaterEqual(contract["version"], 2)
        self.assertEqual(set(BLOCKER_CODES), set(contract["blockers"]["codes"]))
