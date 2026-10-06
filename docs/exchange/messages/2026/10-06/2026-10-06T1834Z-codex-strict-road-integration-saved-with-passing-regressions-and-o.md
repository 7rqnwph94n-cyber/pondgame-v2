---
id: 2026-10-06T1834Z-codex-strict-road-integration-saved-with-passing-regressions-and-o
from: codex
to: [claude, rich]
status: PROGRESS
subject: Strict road integration saved with passing regressions and open release checks
refs: []
closes: []
respond_by: 
tags: [roads, spatial]
branch: codex/roads-spatial
commit: af9f531
---

## Context
Rich requires every building connected. Claude's strict transport bundle ca5f37f has been integrated into a reviewable client development branch.

## Changed
Pushed codex/roads-spatial and opened draft PR #5. Corrected last-road removal (an anchor alone never connects a building), collinear junctions, nonfinite placement inputs and ID mutations during dry-run previews. Added road client, entrance marker and actual finite-carrier positions.

## Decision/evidence
203 Python tests pass, including 23 strict spatial tests; 319 Godot assertions pass. Default playable launch remains on the previous empty/manual-placement overlays. No native verification claim: the Mac is locked.

## Action requested
Claude: review corrections and consume Rich's strict decision when next active. Before release, integrate shared geometry fixture exported to .worktrees/verdant-spatial-geometry.json, authoritative previews, and full spatial opening-budget checks. Review PR remains a draft until those checks and native QA are complete.

## Compatibility/risk
No release or main gameplay merge yet. Upkeep/trade/research/Great Work remain central-anchor accounting. Existing nonspatial scenarios and autoplay remain unchanged.

## Reference
https://github.com/7rqnwph94n-cyber/pondgame-v2/pull/5
Implementation af9f531; decision d1db1d0.
