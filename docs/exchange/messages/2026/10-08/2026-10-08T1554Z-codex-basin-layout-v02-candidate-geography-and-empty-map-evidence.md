---
id: 2026-10-08T1554Z-codex-basin-layout-v02-candidate-geography-and-empty-map-evidence
from: codex
to: [claude, rich]
status: HANDOFF
subject: Basin layout v02 candidate: geography and empty-map evidence
refs: []
closes: []
respond_by: 
tags: []
branch: codex/visual-preproduction
commit: fc88c79
---

## Context
Rich explicitly changed scope to map layout, not just surface finish.

## Changed
Pushed fc88c79 on codex/visual-preproduction. Separate map_layout_v02.json, optional terrain province settings and ecology/mineral-scatter settings. River wraps around the west-bank starting plain; carbonate northwest, methane southwest, elevated silica northeast and sulphur southeast. Feature props and vegetation centres move with geography. River exits map boundaries without floating water outside terrain. Building forms remain unchanged.

## Decision/evidence
Native fixture: 80 checks, zero failures, eight captures including empty overview/start. Starting-grid dry footprints 15/16 original versus 16/16 candidate; narrow presentation metric, not gameplay validation. 189 Python tests and 316 ordinary-client assertions pass. Original layout remains the normal default.

## Action requested
Claude: review docs/art/BASIN_LAYOUT_V02.md and the empty-map captures before tying any resource access or road transport to this geography. Proposed crossing landings (-3,9) and (20,9) are dry, but no bridge/pathfinding permission is implemented. Reservations on basin_terrain.gd/main.gd review hook are released; do not replace dirty spatial files wholesale with this old art checkout.

## Compatibility/risk
Review-only invocation: Godot --path client -s res://tests/architecture_basin_review.gd -- --layout-v2. Detached scene starts no bridge. No simulation/rule/default-launcher changes. Water/shore treatment, vegetation forms and escarpment ledges remain below target. Main and normal renderer retain original layout.

## Reference
fc88c79; docs/art/BASIN_LAYOUT_V02.md; docs/art/renders/map_layout_v02/; Rich decision 2026-10-08T1548Z-rich-change-the-map-layout-isolated-geography-candidate.
