# Governor sweep v4: narrow acceptance pass for the playable-first package

Run on 2026-10-02 for Rich's decision of 17:42Z (`exchange: 2026-10-02T1742Z-rich-prioritise-playable-silica-street-after-targeted-structural`, relayed by Codex; Rich's words: "lets get this playable").

| Item | File |
|---|---|
| Package | `economy/data/experiments/candidate_playable_v1.json` (a candidate, not promoted) |
| Spec | `economy/data/experiments/governor_sweep_v4.json` (9 runs) |
| Governor | `economy/data/governors/reference_governor_v3.json` |

## Package (the four targeted repairs)

1. **Surface Carbonate gleaning.**
   - New stable IDs: patch `surface_carbonate`, building `carbonate_gleaning_site`, recipe `carbonate_gleaning`.
   - Staffed by 2 General workers and costs 2 Biomass (no Carbonate).
   - Slow and finite: rate 0.25, 0.33 or 0.5 per minute at full crew; reserve 12, 20 or 30. These two are the only swept values.
2. **Mineral Jaw research without Repair Enzyme.** It still costs 4 Growth Nutrient and 3 Prepared Silica.
3. **The first Mineral Washery uses 3 General workers.** Later Washeries stay Adapted.
4. **Protected Builders at 3 WP**, with food-emergency pre-emption unchanged.

No other lever was reopened. The horizon is 120 minutes and the acceptance criteria are as in v2.

## Verdict

**No setting passes: 0 of 9 runs.** No run reaches Symbiotic.

- The package does bring the first Stable home forward to **24:29**, against 43:44 on the v0.2 baseline.
- Population reaches 88–103.
- Food and maintenance stay solvent, with no devolution.

The least-generous gleaning setting that does best is 0.33/min with a reserve of 20: population 103 and 42 Carbonate produced by 120:00.

## Instrument note: labour priority added in governor v3

On the first pass the package froze population at 24 in every run.

- The two new General job sites (the gleaners and the first Washery) took General workers ahead of the Sediment Dredge.
- With the Dredge unstaffed, no Growth Nutrient was made, so no migrants arrived. Growth was blocked for 118 minutes.

Governor v3 therefore gives the Dredge and the Nutrient Washer a player-visible labour priority of 3, equal to construction. A player would do the same. All results above use this setting.

Without that setting, the package is a trap for players who don't manage labour. That is worth knowing for UI and onboarding.

## Remaining structural blocker: the class pipeline (unchanged since v3)

Best run (0.33/min, reserve 20):

**Evolution is slow.** Shelter→Stable evolutions happen at 24:29, then 79:09 and 96:29. At 120:00 there are 9 Shelter and 3 Stable homes.

**Labour is short in both classes.**
- General vacancies: 163 WP-minutes.
- Adapted vacancies: 101 WP-minutes.
- Adapted posts filled below class: 306 WP-minutes.

The governor evolves a home only when there are General workers to spare, and there almost never are. Evolving a home turns General workers into Adapted ones, which empties General posts. The colony does not have enough people for its job count.

**The Symbiotic gates arrive too late.** The Distribution node is commissioned at 95:01 and the Detox Clinic at 100:33. Mineral Jaw is researched at 98:20; it is gated by Prepared Silica, which first goes to the Cutter and the Kiln.

Blocked entity-minutes:

| Cause | Minutes |
|---|---|
| Carbonate | 65 |
| General workforce | 55 |
| Construction labour | 55 |
| Without Mineral Jaw | 45 |
| Dry-season farms | 43 |
| Prepared Silica | 35 |

## What this means

- The Carbonate lock is solved by either route: gleaning, or the Carbonate-only first Cutter from sweep v3.
- **The binding constraint is now labour supply against job count.** Population growth (Growth Nutrient and housing) cannot feed both a General base and an Adapted class quickly enough to reach Symbiotic gates, Memory and the Reef within 120 minutes.
- Any further fix is a design choice about population or job scale, so it is Rich's call. Examples:
  - faster migration or larger homes;
  - fewer job slots per early building;
  - cheaper evolution;
  - a later Reef target.

Per the 17:42Z decision, I am not starting another factorial tuning exercise. The next step is the playable Silica Street slice (Milestone B), built on the honest economy plus this candidate package, which stays marked provisional.
