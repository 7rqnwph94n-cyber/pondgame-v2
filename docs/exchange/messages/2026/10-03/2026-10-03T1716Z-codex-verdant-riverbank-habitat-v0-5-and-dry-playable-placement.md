---
id: 2026-10-03T1716Z-codex-verdant-riverbank-habitat-v0-5-and-dry-playable-placement
from: codex
to: [claude, rich]
status: HANDOFF
subject: Verdant riverbank habitat v0.5 and dry playable placement
refs: []
closes: []
respond_by:
tags: [art, map, client]
branch: claude/milestone-b-client-shell
commit: d8c867a
---

## Context

Rich asked for more work on the map after the v14 diversity pass. The current objective remains Pharaoh-like geographic and resource readability, with the empty-map visual gate open.

## Changed

Pushed `d8c867a` on `claude/milestone-b-client-shell` (the shared PR #2 branch): three biomass-bower variants with reserved `HarvestAnchor`, river debris, conforming sediment marks, narrower flow filaments and a subtly variable channel width. The playable HUD now starts compact with Build/Log toggles. Presentation-only building slots avoid a full river footprint and follow ground elevation.

## Decision/evidence

Reviewed captures and candid limits are in `docs/art/EMPTY_MAP_REVIEW_V05.md`. 11 Python asset/reference tests and 212 Godot assertions pass. This is improved blockout art, not a claim that the Pharaoh reference gate has passed.

## Action requested

Claude: please pull or inspect this commit before touching the shared Godot client. The old `carrier_route` presentation polyline visibly crosses the newly rendered channel; when you next integrate routes/transport, please coordinate an authored crossing or revised route against `BasinTerrain.CHANNEL`. No economy rule or resource access change is requested by this handoff.

## Compatibility/risk

No domain IDs, state contract, yields or legality rules changed. `WorldView.configure_terrain()` is called by the client to place visual entities only. Bower `HarvestAnchor` is not an implemented gathering interaction. Old route line remains visually inconsistent.

## Reference

Feature commit `d8c867a`; `docs/art/EMPTY_MAP_REVIEW_V05.md`; captures `verdant_empty_map_v17_bank_habitat.png`, `verdant_bank_habitat_detail_v04.png`, `verdant_playable_v19_dry_placement.png`.
