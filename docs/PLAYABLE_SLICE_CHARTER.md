# Pondgame v2 — Silica Street playable slice charter

**Owner:** Codex, acting as project lead at Rich's request (2026-10-04).
**Status:** working production target; Rich may change it at any time.
**Reference:** [Silica Street production benchmark](art/SILICA_STREET_PRODUCTION_PACKAGE.md), [visual benchmark](art/VISUAL_BENCHMARK.md), [Verdant v0.5 review](art/EMPTY_MAP_REVIEW_V05.md), [governor sweep v4](milestone_a/GOVERNOR_SWEEP_V4_RESULTS.md).

## The decision

Finish one coherent opening district before broadening the map or adding late-era content. The player should establish food, extract Raw Silicate, carry it to storage, process it into Prepared Silica, recover from a visible production stall, and evolve a first home. Bloom-to-Dry pressure must be visible and manageable. This is the first **playable slice**, not a declaration that the whole economy or Memory Reef is balanced.

The Memory Reef's 100–120-minute ambition remains a separate economy research track. No candidate rule is silently promoted to the baseline. The latest bounded sweep found that workforce supply versus early job count is the dominant obstacle; Claude should test a narrow structural remedy and report the least intrusive result before any promotion.

## Scope gates, in order

1. **Truth and stability.** Start, pause, resume, command, inspect and save/reopen where available must run without bridge errors. Presentation may not contradict the Python player view. A site keeps its visual location when commissioned.
2. **A human can play the opening.** Without Autoplay or a written build-order script, a player can identify the next useful action, set labour priority when the Dredge is starved, understand why a site or processor is stuck, and reach a first Stable home. Preserve food solvency through the first Dry transition.
3. **The world explains the chain.** At default gameplay zoom, a five-second look distinguishes Silicate source, carrier, store, washery, field and homes. Raw and Prepared Silica have different forms. A working or blocked Washery reads in-world, with the inspector giving the exact reason. The route has a designed dry crossing; no line cuts through open water.
4. **Presentation quality.** The representative district has authored terrain transitions, vegetation masses rather than evenly spaced props, believable geology, quiet construction land and a compact idle HUD. Review normal-renderer captures with UI shown and hidden. Rich's empty-map acceptance gate remains open until he signs it off.
5. **Regression evidence.** Keep a reproducible camera/seed capture, bridge and client tests, and a short human-play log showing any confusion or softlock. Fix critical defects before adding content breadth.

## Production boundaries

- **Codex:** terrain, map/layout data, assets, placement presentation, route/crossing visuals, camera, HUD look and visual QA.
- **Claude:** simulation and bridge protocol, commands, inspector content, labour/production diagnosis and economy experiments.
- **Shared files** (`main.gd`, `hud.gd`, `world_view.gd`): announce intent in the exchange before editing, keep changes narrow, pull latest work and run both sides' tests.
- A map feature or `HarvestAnchor` is not a gameplay resource rule. Geography becomes authoritative only after a separate design decision and contract.
- New bridge fields require a versioned contract and tests; visual code must not parse English reason strings to infer a stable state.

## Next two work blocks

**Codex:** author and capture the river crossing against `BasinTerrain.CHANNEL`; keep it presentation-only. Export reusable map geometry to presentation-owned data where this does not change rules. Then review the district at normal play zoom, prioritising silhouettes and vegetation massing over more species.

**Claude:** verify bridge/commands/inspector on the latest client branch; make Dredge labour priority and stall causes legible to a human player. In parallel, test a small, bounded workforce-scale candidate rather than another broad factorial sweep. Report evidence and do not promote a rule without an explicit project decision.

## Not in this slice

Memory-tier homes, Reef completion, full spatial logistics, all chemical provinces at final quality, a complete morphology tree, and production-ready art for every building. They are real game goals, not hidden prerequisites for this first slice.
