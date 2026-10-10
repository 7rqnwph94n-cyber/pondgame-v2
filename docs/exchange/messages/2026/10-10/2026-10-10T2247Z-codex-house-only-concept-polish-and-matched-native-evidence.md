---
id: 2026-10-10T2247Z-codex-house-only-concept-polish-and-matched-native-evidence
from: codex
to: [claude, rich]
status: HANDOFF
subject: House-only concept polish and matched native evidence
refs: []
closes: []
respond_by: 
tags: []
branch: codex/visual-preproduction
commit: 21245ae
---

## Context

Rich requested a substantial house-only improvement after rejecting v02.

## Changed

21245ae adds isolated housing_polish_v01: four stages derived from approved v04 anatomy, 1024 embedded PBR maps, recessed organs, tapered forked roots, mixed planted tissue and brood details. Preserves previous v02 and accepted v04 sources. Generator and native review fixture included; no industrial/shared client/default edits.

## Decision/evidence

512 native checks pass on all eight near/distance files, including finite geometry/normals, UV counts, embedded PBR/resolution, vertex tint, source teal palette and distance silhouette bounds. Eight Metal captures: matched before/after, four individual details, grey comparison, LOD comparison and rear memory. First close-up findings corrected: oversized organ fill and tusk-like root ends. Additional colour-conversion experiment reverted after PNG inspection; final palette check passes. Raw/review source geometry counts: 26060/52094/89676/140080 near; 10942/21873/37659/58830 distance.

## Action requested

Awareness; no gameplay mapping promotion requested. Independent review needed before any code/main adoption. Rich’s visual judgement remains authoritative.

## Compatibility/risk

Highest stage remains expensive; population performance, further LODs, placement/docking agreements, animation, settlement-context and colour-vision review remain. No new economic tiers or implemented services implied by comparison stages. PR5/native manual gate unchanged; user settlement preserved.

## Reference

Branch codex/visual-preproduction, 21245ae. docs/art/HOUSING_POLISH_V01.md and docs/art/renders/housing_polish_v01/comparison.png (old top, polished bottom). Source assets/housing_polish_v01/housing_polish_v01.blend.
