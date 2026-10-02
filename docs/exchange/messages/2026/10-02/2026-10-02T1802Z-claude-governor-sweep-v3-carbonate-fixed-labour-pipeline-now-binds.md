---
id: 2026-10-02T1802Z-claude-governor-sweep-v3-carbonate-fixed-labour-pipeline-now-binds
from: claude
to: [rich, codex]
status: REQUEST
subject: Governor sweep v3: Carbonate fixed, labour pipeline now binds; no package passes
refs: [2026-10-02T1746Z-rich-test-all-four-design-changes-in-governor-sweep-v3]
closes: []
respond_by: 
tags: [economy, balance]
branch: claude/milestone-a-honest-economy
commit: 0119aec
---

## Context

Governor sweep v3, per Rich's 1746Z DECISION: all four design changes plus Builder WP, 243 runs, with reference governor v2.

## Changed

- Governor v2 adds two player-visible adaptations: it builds an early Carbonate-only Cutter, and researches Mineral Jaw as soon as the goods are in stock. A test checks that it plays identically to v1 on unchanged rules.
- Sweep levels can override acceptance criteria, so the horizon lever widens the Reef window.
- Report: `docs/milestone_a/GOVERNOR_SWEEP_V3_RESULTS.md`, commit 0119aec. All 115 tests pass on the Mac.

## Decision/evidence

**No bounded package passes: 0 of 243 runs.** No run opens a Reef stage or reaches Memory, even at 180 minutes. I stopped and did not expand any range.

The Carbonate change works:

- 151 runs reach Symbiotic (62%, against 19% in v2);
- earliest Symbiotic 104:19;
- earliest Stable 33:21;
- 32 runs fail only on the Reef.

By lever:

- The Carbonate-only first Cutter is the decisive lever.
- Pit and Cutter at 3 Adapted helps.
- Builder 3 WP is best.
- An earlier Mineral Jaw does not help (still gated by Silica; Nutrient-only research starves migration).
- A longer horizon reaches Symbiotic but never the Reef.

The next dominant bottleneck is the workforce class pipeline. In the best run, only 2–3 homes evolve to Stable in 180 minutes (12 Shelter, 2 Stable, 1 Symbiotic), and Adapted vacancies reach 576 WP-minutes. After Symbiotic, Repair Enzyme upkeep goes unpaid (35 minutes), and Jaw competes with upkeep for Enzyme.

Instrument note: the first v3 run had a governor priority bug (the early Cutter was starved of Carbonate). I fixed it, re-ran the whole sweep, and only the corrected results are reported.

## Action requested

**Rich:** choose the next step:

1. promote the Carbonate-only first Cutter;
2. faster Stable evolution or more Adapted labour;
3. Repair Enzyme upkeep relief;
4. reconsider the first-success target: Symbiotic, stable and solvent by about 110 minutes as the Milestone A gate, with the Reef as a longer-game goal.

**Codex:** nothing.

## Compatibility/risk

No contract change.

## Reference

`docs/milestone_a/GOVERNOR_SWEEP_V3_RESULTS.md` on `claude/milestone-a-honest-economy`, commit 0119aec. Decision: 2026-10-02T1746Z-rich-test-all-four-design-changes-in-governor-sweep-v3.
