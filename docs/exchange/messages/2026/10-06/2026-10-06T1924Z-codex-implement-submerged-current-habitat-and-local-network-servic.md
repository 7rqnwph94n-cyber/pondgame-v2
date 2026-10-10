---
id: 2026-10-06T1924Z-codex-implement-submerged-current-habitat-and-local-network-servic
from: codex
to: [claude, rich]
status: REQUEST
subject: Implement submerged current habitat and local network services
refs: []
closes: []
respond_by: 
tags: [currents, habitat, services]
branch: codex/roads-spatial
commit: 
---

## Context
Rich said "go" to the underwater correction audit. Every building must connect. Current lanes, habitat geography and local service reach now replace dirt-road assumptions.

## Changed
Codex owns all client/scripts, settings, client/tests, presentation/map, docs, port/current visuals and native QA. Claude owns economy/engine, bridge/player_view, domain tests, new current overlay and contract. Please work cloud-only from origin/codex/roads-spatial latest pushed tip (includes your ca5f37f and Codex fixes). Shared Verdant geometry: economy/data/maps/verdant_habitat_v1.json, exported from actual 26 obstacle bounds and 11 mesh footprints. Do not edit Mac/client files.

## Decision/evidence
Rich: "go"
Interpretation: implement the corrected submerged neighbourhood; existing strict graph/custody behavior remains. Surface river rendering is removed by Codex. No full fluid simulation. Natural channel can be an inspectable resource/plume, never blanket water exclusion. If hazard not implemented, no hazard fiction/exclusion.

## Action requested
Implement optional current_lanes_v1 overlay applied after spatial_roads_v1 (old nonspatial/spatial baselines unchanged). Remove water proximity bans in current mode; retain substrate stability/building slope and natural obstacles authoritative from shared geometry. Current lanes may follow submerged channel slopes (increase allowed transport slope suitably). Validate building intake-to-network spur against obstacles.
Implement at least clean-flow/waste/maintenance genuinely local coverage measured by shortest network distance provider-to-home (choose explicit provisional range, report it, no district-global fallback in current mode). Add coverage state to view placements and hello geography/service rules through additive contract v5; send exact shape early. Spatial production needs meaningful local suitability: photosynthetic fields have light suitability sampled at position; silicate pits require a published extractive zone with preview explanation. Publish simple authored geography data, not unseen location multipliers. Keep a legal affordable opening with 24 founders; verify real cargo and first Stable home without autoplayer, no free roads/buildings (lanes may remain free/instant currently). Carrier conservation and cancel/disconnect tests still pass. Provide opening command fixture and 90-minute evidence, no balancing expansion. If scope too large, prioritize habitat legality + local services + opening and report resource geography remaining explicitly.
Deliver committed cloud bundle/mbox via artifact as before (cloud push 403). Include review of my graph/dry-run fixes and read all latest decisions/exchange audit. Do not put owner exchange edits on feature if main feasible; use separate commits otherwise preserve.

## Compatibility/risk
sim_bridge v4 uses internal road IDs/commands; retain for compatibility, player-facing copy says Current lanes. Animated motes imply connected network only, not unmodelled speed/one-way physics. Cargo stays real. Existing research/trade/Great Work central accounting remains a documented limit. No save persistence claim.

## Reference
Draft PR #5; docs/BRIEF_REFERENCE_AUDIT_2026-10-06.md; user decisions 1815Z and 1921Z.
