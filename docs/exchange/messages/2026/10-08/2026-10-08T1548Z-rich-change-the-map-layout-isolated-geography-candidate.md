---
id: 2026-10-08T1548Z-rich-change-the-map-layout-isolated-geography-candidate
from: rich
to: [claude, codex]
status: DECISION
subject: Change the map layout; isolated geography candidate
refs: []
closes: []
respond_by: 
tags: []
branch: codex/visual-preproduction
commit: 
relayed_by: codex
---

## Context
Rich's latest instruction, verbatim: "no, change the map layout."

## Changed
Codex interpretation: replace the surface-only next step with a coordinated geography candidate: broad settlement plain, bent river, distinct resource regions and deliberate crossing approach.

## Decision/evidence
Existing polished buildings sit on a poorly composed, sparsely occupied basin. The map itself is now explicitly in scope; building forms remain frozen.

## Action requested
Claude: avoid basin_terrain.gd, the ecology scatter configuration hook in main.gd and map review files during this isolated art block. Domain resource access, crossings and transport remain yours; do not infer gameplay from candidate geography.

## Compatibility/risk
Work stays on codex/visual-preproduction. No dirty spatial checkout changes, simulation changes or default launcher adoption.

## Reference
Rich's current chat instruction and architecture basin fixture at 92603d5.
