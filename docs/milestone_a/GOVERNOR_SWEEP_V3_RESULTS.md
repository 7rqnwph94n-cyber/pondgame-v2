# Governor sweep v3: results

Run on 2026-10-02 for Rich's decision of 17:46Z (`exchange: 2026-10-02T1746Z-rich-test-all-four-design-changes-in-governor-sweep-v3`): test all four design changes.

Spec: `economy/data/experiments/governor_sweep_v3.json`. Governor: `economy/data/governors/reference_governor_v2.json`. 243 runs. Acceptance criteria are as in v2, except that the Reef window widens with the horizon.

## Verdict

**No bounded package passes: 0 of 243 runs.** No run opens a Reef stage or reaches Memory tier, even with 180 minutes. Per the standing instruction, I have stopped and have not expanded any range.

The Carbonate change did work. It moves the bottleneck from Carbonate to labour and upkeep:

| | Sweep v2 (324 runs) | Sweep v3 (243 runs) |
|---|---|---|
| Runs reaching Symbiotic | 63 (19%) | 151 (62%) |
| Earliest Symbiotic | 110:29 | 104:19 |
| Symbiotic without Gel devolution | 45 | 123 |
| Runs failing only on the Reef | 0 | 32 |
| Earliest first Stable | 41:54 | 33:21 |

## Levers (least to most generous) and marginal effects

Each figure is the number of runs reaching Symbiotic, out of 81.

| Lever | Levels → runs reaching Symbiotic | Read |
|---|---|---|
| Carbonate bootstrap | off 24; **first Cutter costs 3 Carbonate only: 60**; plus partner supply 0.8/min, cap 40: 67 | **The decisive lever.** The extra partner supply adds little: purchasing power, not partner stock, limits buying. |
| Mineral Jaw research | off 55; no Enzyme 53; Nutrient only 43 | **No help.** Without Enzyme it is still gated by Silica. Nutrient-only research spends Growth Nutrient that migrants need. |
| Adapted demand | off 36; **Pit and Cutter use 3 Adapted: 61**; plus a General-staffed Washery 54 | Helps. |
| Horizon (Reef window) | 120: 38; 150: 56; 180: 57 | More time reaches Symbiotic but never the Reef. At 180 minutes, unpaid upkeep and dry-season food failures appear. |
| Builder WP | 2: 34; **3: 71**; 4: 46 | 3 is best again. |

Least-generous runs that fail **only** on the Reef:

- Builder 3 with the Carbonate-only first Cutter: Stable 37:19, Symbiotic 110:29, population 92, all solvent.
- With Builder 4 instead: Symbiotic 108:59.

These runs end soon after Symbiotic, so their solvency covers only a few minutes after the upkeep grace period ends.

## Instrument note: a governor bug, found and fixed

Governor v2 adds two player-visible adaptations, so the rule variants are judged fairly:

1. It builds the first Carbonate Cutter early when its quoted cost is Carbonate only.
2. It researches Mineral Jaw as soon as the goods are in stock.

On unchanged rules it plays exactly like v1. A test checks this.

The first v3 run placed the early Cutter at the lowest material priority (40). Homes and gates then took the Carbonate first, and the Cutter waited 53 minutes. That made the bootstrap look harmful (Stable at 70 minutes). I raised its priority to 18, ahead of the rest of the build order, and re-ran the whole sweep. All figures in this report come from the corrected run.

## Best-progress run, in detail

Builder 3, Carbonate bootstrap with supply, General-staffed Washery, 180-minute horizon.

**Milestones**
- First Stable 38:59; Symbiotic 104:19.
- Population at the end: 132.
- **Homes at 180:00: 12 Shelter, 2 Stable, 1 Symbiotic.** Only three Shelter→Stable evolutions happen in 180 minutes (38:59, 83:09, 101:19).

**Upkeep:** the grace period ends at 104:20. After that, 20 Repair Enzyme are paid and upkeep is unpaid for 35 minutes. The Enzyme supply (one Waste Digester) cannot cover upkeep once grace ends.

**Workforce**
- Adapted vacancies: 576 WP-minutes.
- Posts filled below class: Adapted 445 WP-minutes, Artisan 387.
- General vacancies: 151 WP-minutes. So there is no General surplus to evolve into Adapted.

**Mineral Jaw:** never researched. In this run Jaw is "off", and every Enzyme goes to construction and upkeep. The Pit and Cutter ran at 50% for 125 blocked minutes.

**Reef unlock blockers at 180:00:**
- no Memory-tier home;
- no Memory Circle;
- 0 of 8 Coordinator WP.

None of them is close.

**Blocked entity-minutes**

| Cause | Minutes |
|---|---|
| Adapted workforce | 183 |
| Dry-season farms | 145 |
| Without Mineral Jaw | 125 |
| Carbonate | 88 (was 130–135 in v2) |
| Cured Resin (Composite Workshop) | 61 |

**Trade:** sold Staple 16, Biomass 16 and Growth Nutrient 3; bought Carbonate 23. Carbonate production rose from 11 to 27–32 over the first 120 minutes.

## The next dominant bottleneck

**The workforce class pipeline.** The colony grows in Shelter homes, but too few homes evolve, so Adapted labour never catches up with the extraction and processing jobs. Three things follow:

- Symbiotic arrives late.
- Memory is out of reach.
- After Symbiotic, the Repair Enzyme upkeep cannot be paid.

The three remaining locks are labour class, Enzyme upkeep and Mineral Jaw. They are linked: Jaw would raise output per Adapted worker, but its Enzyme cost competes with upkeep.

## Options for Rich (not tested; each is a rule change)

1. **Promote the Carbonate-only first Cutter.** It is the one lever with a large, clean effect.
2. **Faster Stable evolution or more Adapted labour**, for example:
   - cheaper Stable needs;
   - Shelter workers filling Adapted posts at better efficiency;
   - more housing capacity per home.
3. **Enzyme upkeep relief**, for example:
   - lower upkeep at the first Symbiotic homes;
   - a second Enzyme source before Symbiotic.
4. **Reconsider the first-success target.** Make "Symbiotic, stable and solvent by about 110 minutes" the Milestone A gate, and treat the Reef as a longer-game goal.

## Reproduce

```
python3 -m economy.sweep economy/data/experiments/governor_sweep_v3.json
```

About 8 minutes on 2 cores. The output is deterministic.
