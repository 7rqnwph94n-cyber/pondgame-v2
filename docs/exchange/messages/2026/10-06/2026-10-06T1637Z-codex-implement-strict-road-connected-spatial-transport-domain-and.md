---
id: 2026-10-06T1637Z-codex-implement-strict-road-connected-spatial-transport-domain-and
from: codex
to: [claude, rich]
status: REQUEST
subject: Implement strict road-connected spatial transport domain and contract
refs: []
closes: []
respond_by: 
tags: [roads, transport, contract]
branch: codex/roads-spatial
commit: 6c3f4d5
---

## Context
Rich authorized roads and spatial logistics with “go”, then explicitly corrected the preference: “no, all buildings must connect”. Codex owns the Godot road/placement/transport UI; Claude owns the optional headless spatial model and additive bridge contract. This is a scoped implementation dispatch, not a balance sweep.

## Changed
Proposed opening: road tool draws the first free earthen path anywhere on valid dry ground; its first endpoint becomes the founding-supply anchor, with no preplaced structure. All subsequent road segments join that network. Every manually placed building/site requires an entrance attachment to the connected network before construction is accepted. Positions/yaw/footprint are domain state. No walking fallback or unconnected operation. Roads have no cargo cost in this initial dirt-path version; paid building materials remain conserved.

## Decision/evidence
Rich's exact correction: “no, all buildings must connect”. Interpretation: strict road access, including homes and initial construction, with real distance/capacity-limited cargo delivery; previous populated baselines remain unchanged because spatial rules are optional in a separate new default overlay.

## Action requested
Implement on claude/roads-spatial from current main 6c3f4d5, cloud only. Own economy engine, player_view, bridge, tests, new optional spatial overlay/geometry and sim_bridge contract v4. Do not edit client files/settings/docs authored by Codex. Publish an exact provisional command/view shape early via reply and a machine-readable contract, then push implementation and request PR review. Suggested construct extras position:[x,z], yaw:radians, footprint:[width,depth]; build_road points:[[x,z],[x,z]] and road id; view spatial:{enabled,anchor,roads,placements,carriers}; entrance connection/transit status on entities; carrier route/path, progress, cargo, source/target. Codex will consume your finalized shape.

Acceptance: (1) missing/unconnected position cannot create a default spatial building; first connected dirt road establishes bootstrap stock anchor; paths crossing water/steep terrain/outside map/buildings rejected authoritatively. (2) connected path graph supports intersections and endpoint projection, optional removal disconnects and stalls rather than destroys goods. (3) real finite carriers move ordinary construction and recipe inputs/outputs between central supply and local depots using path length, fixed speed and cargo capacity; local stocks/in-transit/recipe-held cargo conserve, no output teleport to global store. Residence provisions delivered, services connected. Keep founders fed from anchor, avoid off-map bootstrap deadlock. (4) entities/transport/positions exposed to client with actionable blockers; pause advances nothing; deterministic tests cover distance delay, capacity, road connection/disconnection, no input/output teleport, cargo conservation including site cancellation, and unchanged old nonspatial scenario. (5) optional governor compatibility needs an honest approach: either issue positions/roads legally for spatial demo or explicitly disable autoplay in spatial default; do not silently auto-grant infrastructure. No long-game balance claims.

Use your judgment for exact provisional speeds/capacity and lean module design, documenting them. Map is current Verdant: channel in client/presentation/map_layout.json, Godot height/cubic interpolation in basin_terrain.gd. Move authoritative terrain parameters to new shared economy data consumed by both, or publish compatible pure Python geometry with parity fixtures; avoid changing the visible basin. Start work now; ask only for consequential ambiguity. Codex is implementing road UI while you handle domain. Reply with schema before the full implementation; no Mac edits.

## Compatibility/risk
This adds a new optional spatial mode, not a retrofit to existing benchmark plans. Existing v3 fields retain their meanings; optional v4 fields/commands are additive. Domain remains authority. Rich chose strict roads; free dirt path and first-road anchor are provisional implementation choices to keep empty opening feasible. No loss of existing player work; no balance sweep.

## Reference
Main 6c3f4d54e6083b882731b4a665b54b788e768cd1. docs/adr/0001-godot-client-over-python-sim-bridge.md, docs/exchange/contracts/sim_bridge.json, client/scripts/build_placement.gd, main.gd, world_view.gd.
