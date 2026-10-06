---
id: 2026-10-06T1621Z-codex-reviewed-empty-start-and-manual-building-placement-integrate
from: codex
to: [claude, rich]
status: HANDOFF
subject: Reviewed empty start and manual building placement integrated
refs: []
closes: []
respond_by: 
tags: [client, placement, review]
branch: main
commit: b7db12d
---

## Context

Rich rejected automatic placement and authorized manual placement after the Manor Lords comparison. Empty-start PR #3 merged at 3d1ae08 after Claude independently passed 180 Python tests and 288 Godot assertions, verified founder food/workforce conservation and reproduced the old benchmark unchanged.

## Changed

Manual placement PR #4 merged at b7db12d (implementation d243678). Selecting a building picks up a translucent cursor preview without an economy command. R / Shift-R rotates; left-click valid ground confirms paid construction; right-click / Escape cancels without spending. Mesh-sized footprints reject water margins, map bounds, slopes, rocks/natural features and buildings/sites. Reserved positions and rotation survive construction and evolution. Cursor follows input events rather than stale OS mouse coordinates.

## Decision/evidence

Validation: 180 Python tests and 313 Godot assertions pass. Native Mac click-through verifies green ghost, rotation, red water/no-spend, right cancellation and paid shelter commissioning at the chosen position. Claude independently reproduced 313 assertions and found no blockers in reservation, reply ordering, rejection cleanup, removal, paused placement or camera navigation. No economy or bridge wire change in placement.

## Compatibility/risk

Limitations retained: positions are presentation-owned for the current session; no spatial logistics/save-load, road drawing/snapping or flexible plots yet. Autoplay fallback placement uses older dry-ground/centre-spacing rules and may overlap large manually placed buildings or natural obstacles. A lost bridge command reply can leave placement pending until restart. Footprint updates for future larger residence-tier meshes remain to implement. Empty-start founder count is off-wire, provisions can run out if player never builds food/homes, and presentation empty-start flag remains a separate setting from overlays. These are known follow-ups; Claude did not begin balance work.

## Action requested

All Mac worktrees will be fast-forwarded to the final main handoff; Claude should fetch/pull final main and acknowledge clean state without new board commits or balance work.

## Reference

https://github.com/7rqnwph94n-cyber/pondgame-v2/pull/3

https://github.com/7rqnwph94n-cyber/pondgame-v2/pull/4
