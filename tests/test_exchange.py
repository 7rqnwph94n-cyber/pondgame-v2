"""Tests for the agent exchange (docs/exchange, tools/exchange.py)."""
from __future__ import annotations

import datetime as dt
import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("exchange", ROOT / "tools" / "exchange.py")
exchange = importlib.util.module_from_spec(spec)
sys.modules["exchange"] = exchange          # dataclasses need the module registered
spec.loader.exec_module(exchange)

BODY = "\n\n".join(f"## {s}\n\ntext" for s in exchange.REQUIRED_SECTIONS)


class RepositoryExchangeTests(unittest.TestCase):
    def test_repository_exchange_is_valid(self):
        self.assertEqual([], exchange.check())

    def test_index_is_current(self):
        self.assertEqual(exchange.build_index(), exchange.INDEX.read_text(encoding="utf-8"),
                         "INDEX.md is stale: run python3 tools/exchange.py index")

    def test_each_board_belongs_to_its_agent(self):
        for board in exchange.load_boards():
            self.assertEqual(board.agent, board.meta["agent"])

    def test_contracts_name_owner_and_consumers(self):
        for path in exchange.CONTRACTS.glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn(data["owner"], exchange.AGENTS)
            self.assertTrue(set(data["consumers"]) <= set(exchange.AGENTS))


class ExchangeMechanicsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        for sub in ("messages", "status", "contracts"):
            (self.tmp / sub).mkdir()
        self.t0 = dt.datetime(2026, 10, 2, 16, 0, tzinfo=dt.timezone.utc)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write(self, minutes, **kw):
        args = dict(sender="claude", to=["codex"], status="INFO", subject="Hello", body=BODY, refs=[], closes=[])
        args.update(kw)
        return exchange.new_message(now=self.t0 + dt.timedelta(minutes=minutes), root=self.tmp, **args)

    def test_new_message_has_valid_id_path_and_front_matter(self):
        path = self.write(0, subject="Throughput sweep: results!")
        self.assertEqual("2026-10-02T1600Z-claude-throughput-sweep-results", path.stem)
        self.assertIn("messages/2026/10-02", path.as_posix())
        self.assertEqual([], exchange.check(self.tmp))

    def test_same_minute_same_subject_gets_unique_id(self):
        first, second = self.write(0), self.write(0)
        self.assertNotEqual(first.stem, second.stem)
        self.assertEqual([], exchange.check(self.tmp))

    def test_requests_stay_open_until_closed(self):
        request = self.write(0, status="REQUEST", subject="Need fixtures")
        messages = exchange.load_messages(self.tmp / "messages")
        self.assertEqual([request.stem], [m.id for m in exchange.open_items(messages)])
        self.write(5, sender="codex", to=["claude"], status="RESOLVED", subject="Fixtures done",
                   refs=[request.stem], closes=[request.stem])
        messages = exchange.load_messages(self.tmp / "messages")
        self.assertEqual([], exchange.open_items(messages))

    def test_inbox_lists_messages_to_agent_but_not_own(self):
        self.write(0, to=["codex"], subject="For codex")
        self.write(1, sender="codex", to=["claude"], subject="For claude")
        messages = exchange.load_messages(self.tmp / "messages")
        self.assertEqual(["For codex"], [m.meta["subject"] for m in exchange.inbox("codex", messages=messages)])

    def test_check_rejects_bad_messages(self):
        bad = self.tmp / "messages" / "2026" / "10-02"
        bad.mkdir(parents=True)
        (bad / "oops.md").write_text("---\nid: oops\nfrom: someone\nto: []\nstatus: SHOUT\n---\nno sections\n", encoding="utf-8")
        errors = exchange.check(self.tmp)
        for fragment in ("bad id", "from must", "to must", "status must", "missing subject", "missing section"):
            self.assertTrue(any(fragment in e for e in errors), fragment)

    def test_relayed_decisions_require_relayed_by(self):
        self.write(0, sender="rich", to=["claude", "codex"], status="DECISION", subject="Go")
        self.assertTrue(any("relayed_by" in e for e in exchange.check(self.tmp)))

    def test_unknown_refs_are_errors_but_legacy_refs_are_allowed(self):
        self.write(0, refs=["2026-01-01T0000Z-codex-nothing"])
        self.write(1, refs=["legacy:AGENT_CHAT.md#2026-10-02T15:34Z"])
        errors = exchange.check(self.tmp)
        self.assertEqual(1, sum("unknown reference" in e for e in errors))

    def test_index_is_deterministic_and_shows_open_items(self):
        self.write(0, status="REQUEST", subject="Need a decision", to=["rich"])
        first = exchange.build_index(self.tmp)
        self.assertEqual(first, exchange.build_index(self.tmp))
        self.assertIn("Need a decision", first.split("## Recent messages")[0])


if __name__ == "__main__":
    unittest.main()
