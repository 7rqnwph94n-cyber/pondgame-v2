---
agent: claude
updated: 2026-10-10T12:00Z
state: idle
current_task: Reviewed Codex's final current-habitat integration (codex/roads-spatial 6fdc454) read-only in the cloud. No blockers; one should-fix in the client preview refresh. Awaiting merge, native QA and the next dispatch.
branch: claude/current-habitat
head_commit: 89f29b6
waiting_on: Codex merge of codex/roads-spatial after native QA; Rich's launch review
---

## Now

- **Reviewed `6fdc454` read-only in a cloud scratch copy** (no Mac edits):
  - Python suite passes (223 tests); Godot client 337 of 337 assertions.
  - `tools/verify_current_opening.py --check` reproduces the core opening evidence unchanged.
  - The mineral opening (`--plan economy/data/plans/current_mineral_opening_v1.json --evidence tests/fixtures/current_mineral_opening_evidence.json --check`) reproduces: 19 Raw Silicate and 26 Prepared Silica produced in 90 minutes, all sites paid, no food emergency or devolution, first Stable 11:38.
  - `tools/test_early_enzyme_capacity.py --check` still reproduces byte-for-byte.
- **Geometry correction agreed:** exported obstacle `position` is the AABB minimum, so the loader's `min + size/2` centre is right, and the new test pins it to the source file. Protecting existing intake spurs from new footprints, and rebuilding attachments after each current-mode placement, are sound.
- **Launch configuration agreed:** four overlays (slice, empty start, spatial roads, current lanes) and `submerged=true`; autoplay refused in this mode.
- **Should-fix before Rich's QA (client):** the one-second stationary preview refresh clears the last result, so the ghost turns red with "Checking connection…" once a second and a click during that window is refused. Keep showing the previous result while the refresh is in flight.

## Next

- When dispatched: remaining resource geography (Carbonate and others), a plume/hazard role for the old channel only if Rich wants one, and moving research/trade/upkeep/Great Work off the central store.

## Blocked on / waiting for

- Codex: merge after native QA; next dispatch.

## Assumptions I'm making about the other agent's work

- `sim_bridge` v5 is additive to v4 and protocol 1; lanes keep the v4 road commands and ids.
- Service ranges (40/40/50/45 m), lane grade 0.7 and the light model (dark -1.0, full 1.2, minimum 0.35) are provisional, not balanced.
- No save persistence for roads, lanes or placements.

## Recently finished

- `89f29b6` (merged): current-habitat mode, local lane-distance services, light and extraction-zone suitability, dry-run previews, opening fixture and 90-minute evidence, `sim_bridge` v5.
- `ca5f37f` (merged): strict road-connected spatial transport, `sim_bridge` v4.
- Reviews: empty start (PR #3), manual placement (PR #4), player controls, client current rendering (`1f667c2`) and the final integration (`6fdc454`).

## Questions for Rich

- None.
