#!/usr/bin/env python3
"""Agent exchange: the shared, conflict-free channel between Claude, Codex and Rich.

Standard library only (Python 3.10+). Run from the repository root.

    python3 tools/exchange.py new --from claude --to codex,rich --status HANDOFF \\
        --subject "Throughput sweep results" --body-file /tmp/body.md [--refs ID ...] [--closes ID ...] \\
        [--respond-by "next work block"] [--tags economy,contract]
    python3 tools/exchange.py inbox --agent codex [--since ID]   # what is new / open for an agent
    python3 tools/exchange.py index                             # regenerate docs/exchange/INDEX.md
    python3 tools/exchange.py check                             # validate everything (CI/tests use this)

Every message is its own file under docs/exchange/messages/YYYY/MM-DD/, so two agents never edit the
same file. Each agent overwrites only its own status board under docs/exchange/status/. INDEX.md is
generated and deterministic: if it ever conflicts in a merge, regenerate it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCHANGE = ROOT / "docs" / "exchange"
MESSAGES = EXCHANGE / "messages"
STATUS = EXCHANGE / "status"
CONTRACTS = EXCHANGE / "contracts"
INDEX = EXCHANGE / "INDEX.md"

AGENTS = ("claude", "codex", "rich")
STATUSES = ("INFO", "PROGRESS", "REQUEST", "DECISION", "HANDOFF", "BLOCKED", "RESOLVED", "CONTRACT")
OPENING = ("REQUEST", "BLOCKED")          # open until a later message lists the id in `closes`
REQUIRED_SECTIONS = ("Context", "Changed", "Decision/evidence", "Action requested", "Compatibility/risk", "Reference")
ID_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{4}Z-(claude|codex|rich)-[a-z0-9-]+$")
FRONT_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)


@dataclass
class Message:
    path: Path
    meta: dict
    body: str

    @property
    def id(self) -> str:
        return self.meta.get("id", "")

    @property
    def time(self) -> str:
        return self.id[:16]

    def wants_response_from(self, agent: str) -> bool:
        return agent in self.meta.get("to", []) and self.meta.get("status") in OPENING


@dataclass
class Board:
    agent: str
    meta: dict
    body: str
    errors: list[str] = field(default_factory=list)


# ------------------------------------------------------------------ parsing
def _parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [item.strip().strip("'\"") for item in inner.split(",") if item.strip()] if inner else []
    if raw.lower() in ("true", "false"):
        return raw.lower() == "true"
    return raw.strip("'\"")


def parse_front_matter(text: str) -> tuple[dict, str]:
    match = FRONT_RE.match(text)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = _parse_value(value)
    return meta, text[match.end():]


def load_messages(root: Path = MESSAGES) -> list[Message]:
    messages = []
    for path in sorted(root.rglob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        for key in ("to", "refs", "closes", "tags"):
            value = meta.get(key, [])
            meta[key] = value if isinstance(value, list) else [value]
        messages.append(Message(path, meta, body))
    return sorted(messages, key=lambda m: (m.time, m.id))


def load_boards(root: Path = STATUS) -> list[Board]:
    boards = []
    for path in sorted(root.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        boards.append(Board(path.stem, meta, body))
    return boards


# ------------------------------------------------------------------ validation
def check(root: Path = EXCHANGE) -> list[str]:
    errors: list[str] = []
    messages = load_messages(root / "messages")
    ids = [m.id for m in messages]
    known = set(ids)
    for duplicate in sorted({i for i in ids if ids.count(i) > 1}):
        errors.append(f"duplicate message id {duplicate}")
    for m in messages:
        where = m.path.relative_to(root)
        if not ID_RE.match(m.id):
            errors.append(f"{where}: bad id {m.id!r} (expected YYYY-MM-DDTHHMMZ-<agent>-<slug>)")
        if m.path.stem != m.id:
            errors.append(f"{where}: file name must equal id")
        if m.meta.get("from") not in AGENTS:
            errors.append(f"{where}: from must be one of {AGENTS}")
        if m.id and m.meta.get("from") and f"-{m.meta.get('from')}-" not in m.id:
            errors.append(f"{where}: id agent does not match from")
        if m.meta.get("from") == "rich" and not m.meta.get("relayed_by"):
            errors.append(f"{where}: messages from rich must name relayed_by")
        if not m.meta["to"] or any(t not in AGENTS for t in m.meta["to"]):
            errors.append(f"{where}: to must list agents from {AGENTS}")
        if m.meta.get("status") not in STATUSES:
            errors.append(f"{where}: status must be one of {STATUSES}")
        if not m.meta.get("subject"):
            errors.append(f"{where}: missing subject")
        for ref in m.meta["refs"] + m.meta["closes"]:
            if ref not in known and not ref.startswith("legacy:"):
                errors.append(f"{where}: unknown reference {ref}")
        if m.meta.get("status") != "PROGRESS":
            for section in REQUIRED_SECTIONS:
                if f"## {section}" not in m.body:
                    errors.append(f"{where}: missing section '## {section}'")
        expected_dir = f"{m.id[:4]}/{m.id[5:10]}"
        if m.id and expected_dir not in m.path.as_posix():
            errors.append(f"{where}: should live under messages/{expected_dir}/")
    for board in load_boards(root / "status"):
        if board.meta.get("agent") != board.agent:
            errors.append(f"status/{board.agent}.md: agent field must be {board.agent!r}")
        for key in ("updated", "state", "current_task"):
            if key not in board.meta:
                errors.append(f"status/{board.agent}.md: missing {key}")
    for contract in sorted((root / "contracts").glob("*.json")):
        try:
            data = json.loads(contract.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"contracts/{contract.name}: invalid JSON ({exc})")
            continue
        for key in ("id", "version", "owner", "consumers"):
            if key not in data:
                errors.append(f"contracts/{contract.name}: missing {key}")
    return errors


# ------------------------------------------------------------------ queries
def open_items(messages: list[Message]) -> list[Message]:
    closed = {ref for m in messages for ref in m.meta["closes"]}
    return [m for m in messages if m.meta.get("status") in OPENING and m.id not in closed]


def age(message: Message, now: dt.datetime) -> str:
    try:
        sent = dt.datetime.strptime(message.time, "%Y-%m-%dT%H%MZ").replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return "?"
    minutes = int((now - sent).total_seconds() // 60)
    return f"{minutes // 60}h{minutes % 60:02d}m" if minutes >= 60 else f"{minutes}m"


def inbox(agent: str, since: str | None = None, messages: list[Message] | None = None) -> list[Message]:
    messages = load_messages() if messages is None else messages
    fresh = [m for m in messages if agent in m.meta["to"] and m.meta.get("from") != agent and (since is None or m.id > since)]
    return fresh


# ------------------------------------------------------------------ index
def build_index(root: Path = EXCHANGE, now: dt.datetime | None = None) -> str:
    """Deterministic for a given repository state (no wall clock unless asked for ages)."""
    messages = load_messages(root / "messages")
    boards = load_boards(root / "status")
    lines = [
        "# Exchange index",
        "",
        "_Generated by `python3 tools/exchange.py index`. Do not edit by hand; regenerate after a merge conflict._",
        "",
        "## Agent status boards",
        "",
        "| Agent | State | Current task | Branch | Updated | Waiting on |",
        "|---|---|---|---|---|---|",
    ]
    for board in boards:
        m = board.meta
        lines.append(f"| [{board.agent}](status/{board.agent}.md) | {m.get('state', '?')} | {m.get('current_task', '')} | "
                     f"`{m.get('branch', '')}` | {m.get('updated', '')} | {m.get('waiting_on', '') or '–'} |")
    lines += ["", "## Open requests and blockers", ""]
    items = open_items(messages)
    if items:
        lines += ["| Since | From → To | Status | Subject | Respond by |", "|---|---|---|---|---|"]
        for m in items:
            rel = m.path.relative_to(root).as_posix()
            lines.append(f"| {m.time} | {m.meta['from']} → {', '.join(m.meta['to'])} | **{m.meta['status']}** | "
                         f"[{m.meta['subject']}]({rel}) | {m.meta.get('respond_by', '') or '–'} |")
    else:
        lines.append("None.")
    lines += ["", "## Recent messages (newest first)", "", "| Time (UTC) | From → To | Status | Subject |", "|---|---|---|---|"]
    for m in list(reversed(messages))[:40]:
        rel = m.path.relative_to(root).as_posix()
        lines.append(f"| {m.time} | {m.meta['from']} → {', '.join(m.meta['to'])} | {m.meta['status']} | [{m.meta['subject']}]({rel}) |")
    contracts = sorted((root / "contracts").glob("*.json"))
    lines += ["", "## Contracts", ""]
    for contract in contracts:
        data = json.loads(contract.read_text(encoding="utf-8"))
        lines.append(f"- [`{contract.name}`](contracts/{contract.name}) v{data.get('version')} — owner {data.get('owner')}, "
                     f"consumers {', '.join(data.get('consumers', []))}")
    lines += ["", f"Messages: {len(messages)}. Legacy log: `docs/AGENT_CHAT.md` (frozen).", ""]
    return "\n".join(lines)


# ------------------------------------------------------------------ writing
def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:60].rstrip("-") or "message"


def new_message(sender: str, to: list[str], status: str, subject: str, body: str, refs: list[str], closes: list[str],
                respond_by: str = "", tags: list[str] | None = None, relayed_by: str = "", branch: str = "",
                commit: str = "", now: dt.datetime | None = None, root: Path = EXCHANGE) -> Path:
    now = now or dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H%MZ")
    base = f"{stamp}-{sender}-{slugify(subject)}"
    folder = root / "messages" / now.strftime("%Y") / now.strftime("%m-%d")
    folder.mkdir(parents=True, exist_ok=True)
    message_id, n = base, 2
    while (folder / f"{message_id}.md").exists():
        message_id, n = f"{base}-{n}", n + 1
    meta = [
        "---",
        f"id: {message_id}",
        f"from: {sender}",
        f"to: [{', '.join(to)}]",
        f"status: {status}",
        f"subject: {subject}",
        f"refs: [{', '.join(refs)}]",
        f"closes: [{', '.join(closes)}]",
        f"respond_by: {respond_by}",
        f"tags: [{', '.join(tags or [])}]",
        f"branch: {branch}",
        f"commit: {commit}",
    ]
    if relayed_by:
        meta.append(f"relayed_by: {relayed_by}")
    meta.append("---")
    path = folder / f"{message_id}.md"
    path.write_text("\n".join(meta) + "\n\n" + body.strip() + "\n", encoding="utf-8")
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p_new = sub.add_parser("new", help="write a new message")
    p_new.add_argument("--from", dest="sender", required=True, choices=AGENTS)
    p_new.add_argument("--to", required=True, help="comma-separated: claude,codex,rich")
    p_new.add_argument("--status", required=True, choices=STATUSES)
    p_new.add_argument("--subject", required=True)
    p_new.add_argument("--body-file", type=Path, help="markdown body; default stdin")
    p_new.add_argument("--refs", nargs="*", default=[])
    p_new.add_argument("--closes", nargs="*", default=[])
    p_new.add_argument("--respond-by", default="")
    p_new.add_argument("--tags", default="")
    p_new.add_argument("--relayed-by", default="")
    p_new.add_argument("--branch", default="")
    p_new.add_argument("--commit", default="")
    p_inbox = sub.add_parser("inbox", help="messages addressed to an agent, plus its open items")
    p_inbox.add_argument("--agent", required=True, choices=AGENTS)
    p_inbox.add_argument("--since", help="only messages with id greater than this")
    sub.add_parser("index", help="regenerate docs/exchange/INDEX.md")
    sub.add_parser("check", help="validate messages, boards and contracts")
    args = parser.parse_args(argv)

    if args.command == "new":
        body = args.body_file.read_text(encoding="utf-8") if args.body_file else sys.stdin.read()
        to = [t.strip() for t in args.to.split(",") if t.strip()]
        tags = [t.strip() for t in args.tags.split(",") if t.strip()]
        path = new_message(args.sender, to, args.status, args.subject, body, args.refs, args.closes,
                           args.respond_by, tags, args.relayed_by, args.branch, args.commit)
        errors = check()
        INDEX.write_text(build_index(), encoding="utf-8")
        print(path.relative_to(ROOT))
        for error in errors:
            print(f"WARNING: {error}", file=sys.stderr)
        return 1 if errors else 0
    if args.command == "inbox":
        messages = load_messages()
        now = dt.datetime.now(dt.timezone.utc)
        fresh = inbox(args.agent, args.since, messages)
        print(f"Inbox for {args.agent}: {len(fresh)} message(s){' since ' + args.since if args.since else ''}")
        for m in fresh:
            print(f"  {m.id}  [{m.meta['status']}] {m.meta['subject']}  ({m.path.relative_to(ROOT)})")
        owed = [m for m in open_items(messages) if args.agent in m.meta["to"]]
        print(f"Open items awaiting {args.agent}: {len(owed)}")
        for m in owed:
            print(f"  {m.id}  [{m.meta['status']}] {m.meta['subject']}  age {age(m, now)}  respond by: {m.meta.get('respond_by') or '–'}")
        mine = [m for m in open_items(messages) if m.meta.get("from") == args.agent]
        print(f"Open items raised by {args.agent}: {len(mine)}")
        for m in mine:
            print(f"  {m.id}  [{m.meta['status']}] {m.meta['subject']}  age {age(m, now)}")
        for board in load_boards():
            if board.agent != args.agent:
                print(f"{board.agent} status ({board.meta.get('updated', '?')}): {board.meta.get('state', '?')} — {board.meta.get('current_task', '')}")
        return 0
    if args.command == "index":
        INDEX.write_text(build_index(), encoding="utf-8")
        print(INDEX.relative_to(ROOT))
        return 0
    if args.command == "check":
        errors = check()
        stale = INDEX.exists() and INDEX.read_text(encoding="utf-8") != build_index()
        if stale:
            errors.append("INDEX.md is stale: run `python3 tools/exchange.py index`")
        for error in errors:
            print(f"ERROR: {error}")
        print("exchange OK" if not errors else f"{len(errors)} problem(s)")
        return 1 if errors else 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
