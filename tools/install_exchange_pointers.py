"""One-off: point CLAUDE.md, AGENTS.md and the frozen AGENT_CHAT.md at docs/exchange (run from repo root)."""
from __future__ import annotations

from pathlib import Path

FREEZE = """> **FROZEN 2026-10-02.** This log is an archive. All new messages go to `docs/exchange/` on `main`
> (protocol: `docs/exchange/README.md`, summary: `docs/exchange/INDEX.md`). Do not append here.
> Refer to entries in this file as `legacy:AGENT_CHAT.md#<timestamp>`.

"""

CLAUDE_SECTION = """## Collaboration protocol

The exchange between Claude, Codex and Rich lives in `docs/exchange/` on `main`. `docs/exchange/README.md` is authoritative; `docs/AGENT_CHAT.md` is a frozen archive.

### At the start of every session

1. `git switch main && git pull`, then `python3 tools/exchange.py inbox --agent claude`.
2. Read this file completely, `docs/exchange/INDEX.md`, every new message addressed to you, and Codex's board (`docs/exchange/status/codex.md`) and profile (`docs/exchange/agents/codex.md`).
3. Run the relevant tests before changing behaviour.
4. Update `docs/exchange/status/claude.md` (state `active`, plan for this block).

### During and after work

- Keep `status/claude.md` current: at every major step, at least about every 15 minutes of active work, after long jobs, before each commit, and at the end of the block.
- Send event-based messages with `python3 tools/exchange.py new` for: decisions (Rich's decisions recorded verbatim as `from: rich`), blockers, contract/schema/stable-ID/adapter changes (`CONTRACT`), handoffs, and evidence that changes someone's plan. No empty heartbeats.
- Cross-agent interfaces are defined in `docs/exchange/contracts/*.json` and enforced by tests. Never define an interface only in prose.
- Exchange changes are separate `exchange:` commits on `main`; never edit `docs/exchange/` on a feature branch; never edit another agent's message, board or profile.
- Rich resolves creative disagreements. Do not silently choose on Rich's behalf when the choice materially changes the game.

"""

AGENTS_MD = """# Instructions for coding agents (Codex and others)

This repository is shared by Rich (owner), Claude (gameplay/systems) and Codex (art/presentation).

**Communication between agents uses the exchange in `docs/exchange/` on `main`.** Read `docs/exchange/README.md` first. At the start of every session:

1. `git switch main && git pull`, then `python3 tools/exchange.py inbox --agent codex`.
2. Read `docs/exchange/INDEX.md`, every new message addressed to you, and Claude's board (`docs/exchange/status/claude.md`) and profile (`docs/exchange/agents/claude.md`).
3. Update your own board, `docs/exchange/status/codex.md`, and keep it current while you work (major steps, at least about every 15 minutes of active work, before commits, at the end of the block).

Send messages with `python3 tools/exchange.py new` on events: decisions (Rich's recorded verbatim as `from: rich, relayed_by: codex`), blockers, contract changes, handoffs and new evidence. Stable gameplay IDs come from `docs/exchange/contracts/*.json`. `docs/AGENT_CHAT.md` is frozen.

Codex owns this file's Codex-specific content and may extend it; keep the exchange pointer above.
"""


def freeze_agent_chat(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "FROZEN 2026-10-02" in text:
        return
    title, _, rest = text.partition("\n")
    path.write_text(title + "\n\n" + FREEZE + rest.lstrip("\n"), encoding="utf-8")


def update_claude_md(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    start = text.index("## Collaboration protocol")
    end = text.index("## Git workflow")
    text = text[:start] + CLAUDE_SECTION + "---\n\n" + text[end:]
    text = text.replace(
        "Treat this file as standing project memory. Read it at the beginning of every session, then read the latest entries in `docs/AGENT_CHAT.md` before changing code or design data.",
        "Treat this file as standing project memory. Read it at the beginning of every session, then follow the start-of-session steps in \"Collaboration protocol\" (the exchange in `docs/exchange/`) before changing code or design data.")
    text = text.replace(
        "- Any schema/interface changes are documented in `docs/AGENT_CHAT.md`.",
        "- Any schema/interface changes are documented in `docs/exchange/` (messages, and contracts where relevant).")
    text = text.replace(
        "- `docs/AGENT_CHAT.md` contains any required cross-agent handoff;",
        "- `docs/exchange/` contains any required cross-agent handoff, contract update and a current status board;")
    text = text.replace(
        "When sources disagree, use this order and record the conflict in `docs/AGENT_CHAT.md`:",
        "When sources disagree, use this order and record the conflict in `docs/exchange/`:")
    text = text.replace(
        "Exact language-level signatures may evolve, but semantic changes require an entry in `docs/AGENT_CHAT.md` and tests.",
        "Exact language-level signatures may evolve, but semantic changes require a `CONTRACT` message in `docs/exchange/`, an updated contract file and tests.")
    path.write_text(text, encoding="utf-8")


def main() -> None:
    root = Path.cwd()
    freeze_agent_chat(root / "docs" / "AGENT_CHAT.md")
    update_claude_md(root / "CLAUDE.md")
    agents = root / "AGENTS.md"
    if agents.exists():
        text = agents.read_text(encoding="utf-8")
        if "docs/exchange" not in text:
            agents.write_text(AGENTS_MD + "\n---\n\n" + text, encoding="utf-8")
    else:
        agents.write_text(AGENTS_MD, encoding="utf-8")
    print("pointers installed")


if __name__ == "__main__":
    main()
