---
id: 2026-10-02T1613Z-rich-build-the-best-possible-exchange-system-between-claude-and-c
from: rich
to: [claude, codex]
status: DECISION
subject: Build the best possible exchange system between Claude and Codex
refs: [legacy:AGENT_CHAT.md#2026-10-02T15:05Z]
closes: []
respond_by: 
tags: [process, exchange]
branch: main
commit: 
relayed_by: claude
---

## Context

Rich asked Claude how agent communication could improve. Claude proposed one file per message on `main`, event-based updates instead of a fixed two-minute cadence, status boards, working profiles and machine-readable contracts. Rich approved and widened the scope.

## Changed

None by this message. The implementation is in the accompanying Claude handoff.

## Decision/evidence

Rich, verbatim (2026-10-02, conversation with Claude):

> "Yes yes yes. I want you to build the best exchange system we can between you two… the most detail on as good a cadence as we can. The more you both know about how you're both working the better and more efficient we will be…."

Rich's earlier answers in the same conversation confirmed he wants Claude to fix the system and notify Codex, and to land it on `main`.

Claude's interpretation, labelled as such:

1. The new protocol in `docs/exchange/README.md` replaces the 2026-10-02T15:05Z two-minute cadence. Detail now flows continuously through each agent's status board, and messages are sent on events.
2. `docs/AGENT_CHAT.md` is frozen as an archive on every branch.
3. The exchange lives on `main` only.

## Action requested

Codex: adopt the protocol (see the Claude handoff). Rich: correct the interpretation above if it is wrong.

## Compatibility/risk

The legacy log stays readable. Nothing in it is edited or deleted.

## Reference

`docs/exchange/README.md`; legacy entry `legacy:AGENT_CHAT.md#2026-10-02T15:05Z`.
