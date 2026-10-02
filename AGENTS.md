# Instructions for coding agents (Codex and others)

This repository is shared by Rich (owner), Claude (gameplay/systems) and Codex (art/presentation).

**Communication between agents uses the exchange in `docs/exchange/` on `main`.** Read `docs/exchange/README.md` first. At the start of every session:

1. `git switch main && git pull`, then `python3 tools/exchange.py inbox --agent codex`.
2. Read `docs/exchange/INDEX.md`, every new message addressed to you, and Claude's board (`docs/exchange/status/claude.md`) and profile (`docs/exchange/agents/claude.md`).
3. Update your own board, `docs/exchange/status/codex.md`, and keep it current while you work (major steps, at least about every 15 minutes of active work, before commits, at the end of the block).

Send messages with `python3 tools/exchange.py new` on events: decisions (Rich's recorded verbatim as `from: rich, relayed_by: codex`), blockers, contract changes, handoffs and new evidence. Stable gameplay IDs come from `docs/exchange/contracts/*.json`. `docs/AGENT_CHAT.md` is frozen.

Codex owns this file's Codex-specific content and may extend it; keep the exchange pointer above.
