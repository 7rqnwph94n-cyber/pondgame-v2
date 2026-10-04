---
id: 2026-10-04T1029Z-claude-carbonate-workforce-v1-l3-carbonate-renewal-meets-every-crit
from: claude
to: [codex]
status: HANDOFF
subject: Carbonate+workforce v1: L3 + Carbonate renewal meets every criterion except the Reef; nothing promoted
refs: [2026-10-04T1026Z-rich-test-carbonate-supply-and-workforce-or-evolution-levers]
closes: []
respond_by: 
tags: [economy]
branch: claude/milestone-b-client-shell
commit: b553643
---

## Context

The bounded experiment Rich asked for with "1 and 3" (Codex 1026Z): a Carbonate source plus modest population and evolution levers, separately and in small combinations with L3, at most eight candidates.

## Changed

`b553643` on `claude/milestone-b-client-shell`:
- spec `economy/data/experiments/carbonate_workforce_v1.json`;
- runner `tools/run_lever_experiment.py` (it refuses more than 8 candidates);
- report `docs/milestone_a/CARBONATE_WORKFORCE_V1_RESULTS.md`.

No baseline or engine change.

## Decision/evidence

**Levers** (all on the playable package):
- **C:** surface Carbonate renews at 0.2/min. Carbonate precipitates slowly in the calcifying shallows; this is the existing renewal mechanic the Anoxic Basin uses, not a stock injection. 0.2/min is below a full gleaning crew's yield.
- **P:** migration 0.5 → 0.75/min.
- **E:** a Stable home needs 1 Growth Nutrient instead of 2.

**Runs:** 8 candidates (C, P, E, L3+C, L3+C+P, L3+C+E, C+P+E, L3+C+P+E). The controls (v0.2, playable) and the anchor (playable+L3) were re-run in the same harness. The results reproduce identically on the Mac's Python 3.10.

**Results: 0 of 8 pass the full criteria, but two fail only on the Reef.**

**L3 + C:**
- Symbiotic at 106:29 and held.
- Repair Enzyme upkeep paid: 6 units, 0 minutes unpaid.
- Food solvent, no devolution.
- Carbonate produced rises from 34 to 59, and Carbonate drops out of the top three bottlenecks.

**L3 + C + P:** the same pattern, with Symbiotic at 110:09 and population 108.

**What didn't work:**
- C, P and E alone, or C+P+E without L3, never reach Symbiotic. Carbonate stays binding and General vacancies stay above 120 WP-minutes: gleaners and crews are understaffed.
- Adding E (L3+C+E, or all four) brings Symbiotic forward to 81–84 minutes, but then leaves upkeep unpaid for 13.7–15.1 minutes, like the L3 anchor (12.7). Enzyme supply must arrive before Symbiotic.

**Unchanged:**
- No run reaches Memory or opens the Reef. The remaining bottlenecks are no Mineral Jaw, Fired Ceramic and dry-season farms.
- Food is solvent everywhere and there are no devolutions anywhere.

**Least intrusive candidate meeting every slice-relevant criterion: L3 + C** (two levers). It fails only the Reef, which the charter places outside this slice.

**Caveats:**
- Upkeep solvency is observed for only about 14 minutes after Symbiotic.
- Patch renewal in the engine is uncapped, so an unharvested surface reserve would keep growing. It needs a cap before any adoption.

## Action requested

**Codex:** put the next decision to Rich as multiple choice:
- (a) adopt L3 + C as the provisional playable economy for the slice (still a candidate overlay; renewal cap added first);
- (b) first test L3 + C over a longer horizon, to confirm upkeep solvency after Symbiotic;
- (c) no change.

Nothing is promoted until he answers.

## Compatibility/risk

Everything lives in experiment overlays. `candidate_playable_v1` and the v0.2 baseline are untouched. The bridge and the client are unaffected.

## Reference

`b553643`; the 1026Z Rich DECISION; `docs/milestone_a/WORKFORCE_SCALE_V1_RESULTS.md`; `docs/PLAYABLE_SLICE_CHARTER.md`.
