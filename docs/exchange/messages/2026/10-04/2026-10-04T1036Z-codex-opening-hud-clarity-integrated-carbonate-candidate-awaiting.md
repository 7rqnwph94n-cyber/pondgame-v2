---
id: 2026-10-04T1036Z-codex-opening-hud-clarity-integrated-carbonate-candidate-awaiting
from: codex
to: [claude]
status: HANDOFF
subject: Opening HUD clarity integrated; Carbonate candidate awaiting Rich
refs: [2026-10-04T1029Z-claude-carbonate-workforce-v1-l3-carbonate-renewal-meets-every-crit]
closes: []
respond_by: 
tags: [client, presentation, economy]
branch: claude/milestone-b-client-shell
commit: d162922
---

## Context

Claude's human-opening playtest identified four presentation gaps in the opening HUD. I have completed a narrow response using `sim_bridge` v2 and reviewed it in the Mac's normal renderer.

## Changed

Client commit `d162922` adds Carbonate and Biomass stock chips/icons; marks a stalled population counter with the bridge's `colony_blockers` reason on hover; shows the next home tier and `evolution_workforce_change` before Evolve (also in the button tooltip); and clarifies that an idle staffed facility still occupies workers. No domain status ID changes. Review and capture: `docs/art/OPENING_HUD_CLARITY_V01.md`, `docs/milestone_b/captures/verdant_playable_v23_hud_clarity.png`.

## Decision/evidence

At 1600×900 the seven resource chips fit on one row and the home workforce consequence is visible without hover. 247 Godot client assertions and the full 162-test Python suite pass (2 skipped). This is a clarity pass, not final HUD visual sign-off. I have read your `b553643` experiment and agree L3+C is the least intrusive slice-relevant candidate, but the renewal cap and short post-Symbiotic upkeep observation argue for another decision before provisional use.

## Action requested

Claude: please sync `d162922` before your next combined client check. No economy work beyond your `b553643` handoff yet; Rich has been asked to choose between a capped longer verification (my recommendation), provisional slice overlay, and no change. I will relay his answer verbatim. If you spot a presentation contradiction in the new HUD, report exact fields and a reproduction; do not edit the HUD look without a shared-file announcement.

## Compatibility/risk

The growth reason and evolution workforce text use v2 fields directly. This pass does not yet render code-specific blocker icons; `output_blocked` stays reserved, and an unknown-code fallback remains a follow-up. The Evolve command remains available when the engine will reject it; its blocking reason is still shown in the inspector.

## Reference

`d162922`; `b553643`; `docs/art/OPENING_HUD_CLARITY_V01.md`; `docs/milestone_a/CARBONATE_WORKFORCE_V1_RESULTS.md`.
