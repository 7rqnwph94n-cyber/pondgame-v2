---
id: 2026-10-04T1007Z-codex-starting-facilities-now-have-distinct-playable-silhouettes
from: codex
to: [claude]
status: HANDOFF
subject: Starting facilities now have distinct playable silhouettes
refs: [2026-10-04T0933Z-codex-authored-crossing-and-route-layout-ready-for-integration]
closes: []
respond_by: 
tags: [client, presentation, assets]
branch: claude/milestone-b-client-shell
commit: a3f9cae
---

## Context

At the default opening camera, four facilities present at simulation second zero were rendered as identical placeholder cones because their building IDs had no presentation asset mapping. This obscured the starting district before any player action.

## Changed

Client commit `a3f9cae` adds silhouette-distinct blockout assets and mappings for `first_nursery`, `maintenance_organ`, `survey_organ` and `culture_bed`. These are generated from `tools/generate_blockout_assets.py` and selected by `client/presentation/asset_map.json`. `docs/art/STARTING_FACILITY_READABILITY_V01.md` records the review.

## Decision/evidence

The updated normal-renderer capture is `docs/milestone_b/captures/verdant_playable_v22_starting_facilities.png`. The four no longer read as one generic cone, though the Nursery and Maintenance Organ need stronger value separation at normal zoom. The bridge/client suite passes 234 Godot assertions and 13 Python asset/layout tests.

## Action requested

Claude: sync `a3f9cae` for your next client-camera capture. These are presentation-only assets; their anchors do not imply new rules. Your manual-opening/blocker test and bounded workforce experiment remain the priority. Please include any visual ambiguity you encounter in the handoff.

## Compatibility/risk

No economy definitions, jobs, recipes, build costs, bridge fields or placement legality changed. We are still short of the five-second production-chain acceptance gate and Rich's visual sign-off.

## Reference

`a3f9cae`; `docs/art/STARTING_FACILITY_READABILITY_V01.md`.
