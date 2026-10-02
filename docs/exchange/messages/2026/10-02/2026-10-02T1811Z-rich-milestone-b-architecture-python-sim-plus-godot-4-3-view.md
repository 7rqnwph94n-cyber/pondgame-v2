---
id: 2026-10-02T1811Z-rich-milestone-b-architecture-python-sim-plus-godot-4-3-view
from: rich
to: [claude, codex]
status: DECISION
subject: Milestone B architecture: Python sim plus Godot 4.3 view
refs: [2026-10-02T1742Z-rich-prioritise-playable-silica-street-after-targeted-structural]
closes: []
respond_by: 
tags: [architecture, milestone-b]
branch: 
commit: 
relayed_by: claude
---

## Context

Milestone B start. Claude asked Rich two architecture questions in the Claude conversation, as multiple choice.

## Changed

Nothing yet. ADR 0001 will record this.

## Decision/evidence

Rich's selections, verbatim labels:

1. "How should Godot run the game rules?" → **"Python sim + Godot view (Recommended)"**. Option text: "Godot launches the existing Python simulation as a local process and talks JSON both ways: snapshots in, commands out. There is one source of truth and it's the fastest route to playable. Shipping later means bundling Python, or porting once the rules settle."
2. "Which Godot version?" → **"Godot 4.3 (Recommended)"**.

## Action requested

Claude:
- write ADR 0001 (Godot client over a local Python simulation bridge);
- publish the bridge protocol as a contract;
- build the smallest client shell (load definitions, advance the simulation, placeholder entities through the presentation adapter, pause and speed, one stall inspector).

Codex: target Godot 4.3 for any presentation scenes or wrappers.

## Compatibility/risk

The Python domain stays the only rules authority; Godot holds no gameplay rules. Shipping will later need bundled Python or a port, to be decided once the rules settle.

## Reference

CLAUDE.md, Milestone B. 2026-10-02T1742Z-rich-prioritise-playable-silica-street-after-targeted-structural.
