---
id: 2026-10-05T1754Z-codex-icon-build-rail-and-player-controls-integrated-after-indepen
from: codex
to: [claude, rich]
status: HANDOFF
subject: Icon build rail and player controls integrated after independent review
refs: []
closes: []
respond_by: 
tags: [ui, controls, sync]
branch: 
commit: 37adb0e
---

## Context

Rich rejected the first click-through’s controls and wordy UI; see the 1728Z decision.

## Changed

37adb0e integrates the controls/UI pass on main: persistent left category build rail, single-click construction with hover costs/workforce, compact icon resource strip plus full-stock grid, short inspector with expandable details, contextual building/site/home/carrier/ground right-click menus, zoom buttons/wheel/pinch/Shift-trackpad scroll, two-finger trackpad pan, Alt-scroll or Q/E rotation, selected-carrier ring and Inspect/Follow. New construction is selected automatically.

## Decision/evidence

Native Mac QA verified category catalogue, zoom, building menu, carrier selection/ring and Inspect/Follow menu, hover descriptions, construction inspector and resource grid. Final Godot client suite passes 281 assertions. Claude independently reproduced the first branch’s 273 assertions and found toolbar focus consuming Space, carrier click theft and missing context-evolution workforce warning. All three are fixed with regression coverage. Buildings win overlapping clicks, hidden/unconfigured carriers are excluded, and the Evolve menu names its workforce change. High-speed carrier animation is capped and manual pan cancels Follow.

## Action requested

Claude: read 37adb0e and sync actual cloud main to this final handoff commit. Acknowledge clean exact SHA; no new gameplay block or board commit requested. Rich: restart Play Pondlife normally to load the final review corrections. Existing click-through is left to Rich’s control.

## Compatibility/risk

No economy/default/bridge contract edits. Carriers remain visual, without cargo or individual orders. Construction uses district placement. The opening remains a provisional slice and later-game balance/Memory Reef remain open.

## Reference

client/README.md; docs/PROJECT_STATUS.md; client/tests/run_tests.gd.
