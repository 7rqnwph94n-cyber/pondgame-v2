---
id: 2026-10-05T1728Z-rich-rework-controls-and-icon-hud-after-playable-click-through
from: rich
to: [claude, codex]
status: DECISION
subject: Rework controls and icon HUD after playable click-through
refs: []
closes: []
respond_by: 
tags: [ui, controls]
branch: 
commit: 
relayed_by: codex
---

## Context

Rich reviewed the desktop click-through.

## Changed

Codex takes main.gd, hud.gd, camera_rig.gd and client interaction tests for this block.

## Decision/evidence

Rich: “controls are poor. there is no right click for menu/unit/building options, there is no zoom, and no build bar down the left side like pharaoh, the ui is far too wordy, we need icons with hover over descriptions, units not clickable at all.”

Interpretation: implement these controls now, simplify the default HUD, preserve detailed explanations behind explicit inspection.

## Action requested

Claude should avoid shared client files while Codex works. No gameplay dispatch.

## Compatibility/risk

Carriers are currently presentation-only, not simulated agents. Selection must explain this and must not invent cargo or movement orders. No bridge contract or economy changes.

## Reference

client/scripts/main.gd; client/scripts/hud.gd; client/scripts/camera_rig.gd.
