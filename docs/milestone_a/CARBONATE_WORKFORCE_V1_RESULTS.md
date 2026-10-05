# Carbonate and workforce v1

**Request:** Rich chose "1 and 3" at 2026-10-04T1026Z (relayed by Codex): Carbonate supply together with modest population and evolution levers.

**Spec:** `economy/data/experiments/carbonate_workforce_v1.json`. **Runner:** `python3 tools/run_lever_experiment.py <spec>`, which refuses more than 8 candidates.

**Setup:**
- Reference governor v3; 120-minute horizon; v2 acceptance criteria.
- 8 new candidate runs, all on the playable package. Two controls and the L3 anchor are re-run in the same harness.
- **Nothing is promoted.** Repair Enzyme relief is deliberately not a lever; unpaid upkeep is reported as a failure.

## Levers, and why each is plausible

| Lever | Change | Rationale |
|---|---|---|
| **L3** | Fewer early job slots: crews of 3–4 lose one slot; outputs unchanged | From workforce scale v1 (the anchor) |
| **C**: Carbonate source | `surface_carbonate` renews at 0.2/min | Carbonate precipitates slowly in the calcifying shallows. The Anoxic Basin already renews this way; no new rule or stock injection is needed. 0.2/min is below what a full gleaning crew extracts, so it slows exhaustion rather than gifting stock. *Note:* the engine's patch renewal is uncapped. Unharvested surface Carbonate would keep accumulating, so a cap is a review item if C goes further. |
| **P**: population supply | Migration 0.5 → 0.75 per minute (+50%) | The value tested in governor sweep v2. Migrants still need Growth Nutrient and free housing. |
| **E**: evolution cost | A Stable home needs 1 Growth Nutrient instead of 2 | Services and the 90-second sustain are unchanged. |

## Results

Abbreviations: Carbonate made / bought = produced / bought over 120 minutes; Surface left = surface Carbonate remaining at 120:00; Enzyme paid / unpaid = units paid / minutes unpaid; G/A vacancy = General / Adapted vacancy, in WP-minutes.

| Run | Stable | Symbiotic | Homes S/St/Sy | Pop | Carbonate made / bought | Surface left | Enzyme paid / unpaid | Gel short | G/A vacancy | Fails |
|---|---|---|---|---|---|---|---|---|---|---|
| control: v0.2 | 24:06 | – | 8/3/0 | 97 | 9 / 30 | 0 | 0 / 0 | 0 | 54 / 6 | no Symbiotic, Reef |
| control: playable | 24:29 | – | 7/4/0 | 88 | 26 / 20 | 0 | 0 / 0 | 0 | 158 / 65 | no Symbiotic, Reef |
| anchor: playable + L3 | 21:39 | 83:59 | 9/1/1 | 92 | 34 / 13 | 0 | 11 / **12.7** | 3.0 | 15 / 154 | maintenance, Reef |
| C | 24:29 | – | 8/3/0 | 96 | 37 / 20 | 12 | 0 / 0 | 0 | 161 / 61 | no Symbiotic, Reef |
| P | 24:29 | – | 7/4/0 | 92 | 28 / 18 | 0 | 0 / 0 | 0 | 153 / 59 | no Symbiotic, Reef |
| E | 20:50 | – | 8/3/0 | 98 | 30 / 19 | 0 | 0 / 0 | 0 | 166 / 67 | no Symbiotic, Reef |
| **L3 + C** | 21:39 | **106:29** | 6/3/1 | 92 | **59** / 12 | 7 | 6 / **0** | 3.0 | 31 / 55 | **Reef only** |
| **L3 + C + P** | 21:39 | **110:09** | 10/2/1 | **108** | **61** / 12 | 7 | 5 / **0** | 3.0 | 33 / 57 | **Reef only** |
| L3 + C + E | 18:09 | 81:39 | 9/2/1 | 108 | 51 / 11 | 7 | 11 / 15.1 | 3.0 | 70 / 42 | maintenance, Reef |
| C + P + E | 20:10 | – | 10/3/0 | 108 | 45 / 20 | 11 | 0 / 0 | 0 | 127 / 58 | no Symbiotic, Reef |
| L3 + C + P + E | 18:04 | 83:59 | 7/2/1 | 89 | 51 / 15 | 7 | 11 / 13.7 | 3.0 | 15 / 77 | maintenance, Reef |

The table omits the columns that were identical everywhere: no run reaches Memory or opens a Reef stage, every run is food-solvent (no Staple shortage or food emergency), there are no devolutions, and Repair Enzyme upkeep is unpaid only in the three runs that reach Symbiotic before about 85 minutes.

## Findings

1. **Carbonate and fewer slots only work together.**
   - **C alone** keeps the surface reserve alive, with 12 units left at 120:00, but General vacancies stay high (161 WP-minutes) and the gleaners are understaffed. Carbonate remains the top bottleneck.
   - **L3 alone** staffs the crews but exhausts the surface reserve.
   - **Together (L3 + C)**, Carbonate production rises from 34 to 59, the Carbonate bottleneck drops out of the top three, and General vacancies fall to 31.
2. **L3 + C is the first package in any sweep that meets every criterion except the Reef.**
   - Symbiotic at 106:29, then held: no Gel devolution, upkeep **paid** (6 Enzyme, 0 unpaid minutes), food solvent.
   - **L3 + C + P** behaves the same, with population 108 and Symbiotic at 110:09.
   - *Caveat:* both reach Symbiotic late, so upkeep solvency is observed for only about 10–14 minutes after the grace period ends.
3. **Cheaper evolution (E) brings Symbiotic too early for the Enzyme supply.**
   - L3 + C + E reaches Symbiotic at 81:39 but then leaves upkeep unpaid for 15.1 minutes, as the L3 anchor does.
   - Enzyme supply, which comes from waste digestion, has to arrive before Symbiotic, not merely exist eventually.
4. **P (more migration) adds people without unlocking anything on its own.**
5. The bottlenecks that remain after L3 + C are **no Mineral Jaw, Fired Ceramic and dry-season farms**. The Reef (Memory-tier home, Memory Circle, 8 Coordinator WP) is not reachable within 120 minutes in any run.

## Least intrusive result

**L3 + C** (two levers) is the least intrusive candidate meeting every slice-relevant criterion: Symbiotic held, food and maintenance solvent, no devolution. It fails only the Reef, which the slice charter places outside this slice.

It is a candidate, not a recommendation to promote. For Rich (via Codex), as multiple choice:
- (a) adopt L3 + C as the provisional playable economy for the slice, still a candidate overlay with the uncapped renewal reviewed;
- (b) test L3 + C over a longer horizon, to see whether upkeep solvency holds after Symbiotic;
- (c) keep everything as it is.

## Reproduce

```
python3 tools/run_lever_experiment.py economy/data/experiments/carbonate_workforce_v1.json
```

11 runs, about 9 seconds on 2 cores.
