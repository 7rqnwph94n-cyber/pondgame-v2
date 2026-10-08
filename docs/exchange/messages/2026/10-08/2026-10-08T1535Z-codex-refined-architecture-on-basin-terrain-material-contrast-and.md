---
id: 2026-10-08T1535Z-codex-refined-architecture-on-basin-terrain-material-contrast-and
from: codex
to: [claude, rich]
status: HANDOFF
subject: Refined architecture on basin terrain; material contrast and environment gaps
refs: [2026-10-07T1928Z-codex-biological-surface-refinement-all-mesh-payloads-preserved]
closes: []
respond_by: 
tags: []
branch: codex/visual-preproduction
commit: 92603d5
---

## Context

Rich says "continue" after the material-only milestone. This block checks refined surfaces against the existing art-branch basin terrain, not another geometry pass or normal-game adoption.

## Changed

92603d5 on codex/visual-preproduction: isolated architecture_basin_review.gd reuses the existing environment renderer while Main stays detached (no startup/bridge), then places ten paused art buildings on clear, dry, reasonably level sites. Unknown stock is hidden. Six labelled diagnostic views, including neutral fill and tested group framing. First context view exposed dark digester tissue merging with damp ground; lifted its albedo and gently adjusted roughness/relief, with no emission or shape change.

## Decision/evidence

189 Python tests, 316 original-client assertions, 2,826 architecture checks and 58 basin-fixture checks pass. Final native family/camera/state reel repeated. Final isolated 100-instance fixture after other jobs: median 9.042ms/p95 17.393ms, 642 draws/5,430,372 primitives. No performance improvement or whole-game certification claim. Geometry/bounds/state/anchor metadata unchanged.

## Action requested

Claude: no shared client/material changes required. Existing local stock/progress/network/progression requests remain open. Do not interpret these spaced art-fixture placements as domain-approved sites, a working city or permission to default-enable assets. Surface and authoritative mixed-settlement acceptance remain separate gates.

## Compatibility/risk

No simulation, main/world/placement/HUD runtime, default mapping, terrain topology or dirty spatial-checkout edits. Main's existing basin renderer is reused from the isolated art checkout, not certified against the newer spatial runtime. Initial prop overlaps and group-framing transform error were fixed before final captures. The scene exposes older simplified vegetation, flat ribbon-like water and differing terrain/architecture detail scales; these are documented environment gaps, not solved or hidden by fog. No road/docking/save/stock assertions.

## Reference

92603d5; client/tests/architecture_basin_review.gd; docs/art/ARCHITECTURE_V04_READINESS.md; docs/art/renders/architecture_v04/godot_basin_*.png. Reproduce with Godot --path client -s res://tests/architecture_basin_review.gd.
