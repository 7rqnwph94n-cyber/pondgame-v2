---
id: 2026-10-07T1643Z-codex-refined-ten-building-v04-milestone-native-evidence-and-remai
from: codex
to: [claude, rich]
status: HANDOFF
subject: Refined ten-building v04 milestone: native evidence and remaining concept gates
refs: [2026-10-07T1530Z-codex-propose-six-tier-progression-and-bounded-clean-flow-waste-in, 2026-10-07T1609Z-codex-announce-isolated-textured-architecture-adapter-and-opt-in-e]
closes: []
respond_by: 
tags: [art, architecture, contract]
branch: 
commit: 
---

## Context

Rich requested repeated refinement of the fixed ten-building benchmark to game readiness and concept quality. Refined milestone a4403f7 is on codex/visual-preproduction, in the isolated pondgame-v2-assets checkout. It is NOT accepted production art or default adoption.

## Changed

Delivered: six housing visual stages, Store/Washery/Kiln/Digester, editable compressed Blender source, 20 self-contained textured near/distance GLBs, visual anchors/manifest, construction phases, dormant closures, typed input/output chambers, explicit recipe-phase soft tissue deformation, and native orbit/pitch/zoom/greyscale/state/density captures. Multiple reviews corrected open anatomy, twisting collars, canopy intersections, rear Store access, protruding light organs, excessive gloss and LOD state loss. Other asset families remain on hold.

## Decision/evidence

Verification: 188 Python tests, 316 original-client assertions and 564 architecture checks pass. Final 100-instance native Forward+ fixture: 8.646ms median / 16.596ms p95, 598 draws, 4,868,384 primitives. This is not whole-game performance certification. See docs/art/ARCHITECTURE_V04_READINESS.md and docs/art/renders/architecture_v04/godot_*.png.

## Compatibility/risk

The adapter is opt-in through POND_ARCHITECTURE_V04=1 in THIS art checkout, or architecture_review in a fixture style. Default mappings remain original. Existing shelter/stable/symbiotic/memory bind visual stages 1/2/4/6. Stages 3/5 remain unbound; capacities, needs, costs and recipes unchanged.

Presentation edits: new architecture_loader.gd, architecture_visual.gd and presentation/architecture_v04.json; small changes to entity_view.gd, world_view.gd and build_placement.gd. No main/bridge/economy edits. This checkout's shared client files predate the spatial work: do not replace newer whole files or blindly cherry-pick over the dirty spatial checkout. Shared-file reservation for this block released; reconcile scoped changes after announcing ownership.

## Action requested

Next for Claude when dispatched: answer the existing 15:30Z six-tier/utility proposal request. Also propose the smallest versioned bridge extension for known building-local resource counts and explicit recipe progress, without deriving local stock from global totals. The art API set_chamber_stocks accepts actual resource IDs and known counts; absent IDs hide their groups. set_recipe_state changes deformation only on supplied phase, never elapsed wall time. Local stocks/phase remain an integration gate, not implemented domain support. Visual anchors remain non-authoritative until a docking agreement. Do not introduce new mandatory utility costs before Rich's routing choice.

Next for Codex: sculpted asymmetry and cultivation integrated into walls/terraces. Repeated round apertures, thin supports, geometric canopy triangles and planter-like beds are still below the richer concepts. Then review an authoritative mixed settlement with real carriers, states and inventory. Passing tests does not settle artistic parity; Rich visual acceptance remains open. No new Claude reply received during this block.

## Reference

Art branch a4403f7; docs/art/ARCHITECTURE_PRODUCTION_PLAN.md; docs/art/ARCHITECTURE_V04_READINESS.md. Prior requests and shared-file announcement are listed in the message refs.
