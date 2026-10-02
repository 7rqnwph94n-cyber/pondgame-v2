---
id: 2026-10-02T1741Z-claude-governor-sweep-v2-no-bounded-package-passes-design-decision
from: claude
to: [rich, codex]
status: REQUEST
subject: Governor sweep v2: no bounded package passes; design decision needed
refs: [2026-10-02T1652Z-rich-approve-adaptive-governor-and-second-feasibility-pass]
closes: []
respond_by: 
tags: [economy, balance]
branch: claude/milestone-a-honest-economy
commit: 6a5f5e1
---

## Context

Second feasibility pass that Rich approved at 16:50Z. The adaptive reference governor played all 324 runs over the five bounded levers. The calendar now repeats every 90:00, and the neighbour buys Staple and Biomass.

## Changed

- `economy/governor.py`: the reference governor. It uses only the player view, logs every decision, is deterministic, and never touches Builders or the food-emergency predicate.
- The engine's `issue()` and the controller hook.
- The repeating calendar and partner demand.
- Governor sweep v2 and its report.

All 115 tests pass on the Mac's Python 3.10.

## Decision/evidence

**No bounded package passes: 0 of 324 runs.** As instructed, I stopped and did not expand any range.

- No run begins the Reef.
- 63 runs reach Symbiotic, all at 110–117 minutes, and most then devolve on Gel.
- Food is solvent in every run.
- Builders at 3 WP do best: 36 of 108 runs reach Symbiotic, against 18 at 2 WP and 9 at 4 WP.
- Artisan relief hurts: 9 of 162 runs with it on, 54 with it off.
- Ganglion work and Reef cost have no effect, because those stages are never reached.

The dominant lock is structural:

1. The opening has to buy, at about 0.15/min, the Carbonate that unlocks Carbonate production. In the baseline the Silicate Pit waited 46 minutes for its Carbonate.
2. Mineral Jaw needs Repair Enzyme, which only arrives after 100 minutes via the Waste Digester, so the Pit and the Cutter run at 50%.
3. Adapted workers are the scarce class.

## Action requested

**Rich:** choose which design change to test next:

1. ease the Carbonate bootstrap;
2. unlock Mineral Jaw earlier;
3. reduce demand for Adapted workers;
4. lengthen the horizon beyond 120 minutes.

**Codex:** nothing. Milestone B fixtures wait on the economy decision.

## Compatibility/risk

No contract change. The repeating calendar, partner demand and the command `source` field do not affect `presentation_states.json` v1.

## Reference

`docs/milestone_a/GOVERNOR_SWEEP_V2_RESULTS.md` on `claude/milestone-a-honest-economy`, commit 6a5f5e1.
