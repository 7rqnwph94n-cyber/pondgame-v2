# Governor sweep v2: results

Run on 2026-10-02 for Rich's decision of 16:50Z (`exchange: 2026-10-02T1652Z-rich-approve-adaptive-governor-and-second-feasibility-pass`).

Spec: `economy/data/experiments/governor_sweep_v2.json`. Governor: `economy/data/governors/reference_governor_v1.json`. 324 runs, 120-minute horizon, same acceptance criteria as `throughput_sweep_v1`.

## Verdict

**No bounded package passes: 0 of 324 runs.** Per Rich's instruction, I have stopped here and have not expanded any range.

- No run completes the Reef, or even begins it.
- Only 63 of 324 runs reach Symbiotic, all of them late (110–117 min).
- Most of those 63 devolve within minutes: the Gel supply cannot hold, and upkeep goes unpaid once the grace period ends.
- Food stays solvent in every run (0 Staple-shortage minutes; the food emergency never fires).

## What changed for this pass

| Change | Where |
|---|---|
| The season calendar repeats every 90:00 (calendar-local time drives seasons and deposits; the linear calendar remains available) | `environment.py`, `verdant_v0_2.json` (`calendar_cycle_seconds: 5400`) |
| The neighbour buys Staple (price 2) and Biomass (price 1), accruing per minute up to a cap | `trade.py` (`partner_demand`), `verdant_v0_2.json`. Swept: small 0.2/min, cap 20; modest 0.35/35; larger 0.5/50 |
| Adaptive reference governor | `economy/governor.py` |
| Protected Builders at 2, 3 or 4 WP, with food-emergency pre-emption kept | sweep lever `builder_wp` |

The governor:

- sees only the player view (`observe()`);
- acts through `sim.issue()`, so every command is legal and logged with its rule and reason;
- is deterministic, which is tested;
- never changes Builder allocation and never touches the food-emergency predicate, which is also tested.

In every run reported here it issued 0 failed commands.

## Marginal effects (mean over all other levers)

| Lever | Levels → runs reaching Symbiotic | Note |
|---|---|---|
| Builder WP | 2 → 18/108; **3 → 36/108**; 4 → 9/108 | 3 is the sweet spot. At 4 WP, General workers are pulled off production and Adapted vacancies rise. |
| Export market | small 18; modest 18; larger 27 (of 108) | Helps a little; demand caps sales. |
| Artisan relief | off 54/162; on 9/162 | **Hurts.** It moves Adapted workers into Artisan jobs while Adapted is already the scarce class. |
| Migration | base 27/162; 0.75 → 36/162 | Population rises by about 7. Small help. |
| Ganglion work | no effect | Never reached |
| Reef cost | no effect | Never reached |

## Three detailed runs

| | Baseline (all least generous) | Best progress (modest export, migration 0.75, Builder 2) | Builder 3 alone |
|---|---|---|---|
| First Stable | 43:44 | 43:39 | 41:54 |
| First Symbiotic | – | 110:29, then devolves | 117:29 (still Symbiotic at 120) |
| Final population | 92 | 95 | 84 |
| Tiers at 120:00 (Shelter/Stable/Symbiotic) | 7 / 3 / 0 | 8 / 3 / 0 | 6 / 2 / 1 |
| Staple shortage / food emergency | 0 / 0 | 0 / 0 | 0 / 0 |
| Gel shortage (min) | 0 | 7.0 | 2.5 |
| Unpaid upkeep (min) | 0 (grace never ended) | 1.3 | 0 |
| Blocked entity-minutes | 437 | 498 | 452 |
| Idle construction WP-minutes | 516 | 258 | 114 |
| Mineral Jaw | queued 116:50, not researched | never queued | never queued |
| Governor decisions (failed) | 99 (0) | 84 (0) | 83 (0) |

### Governor decisions by rule (baseline)

| Rule | Decisions |
|---|---|
| idle_crews | 42 |
| trade | 21 |
| build_order | 18 |
| housing | 8 |
| evolution | 3 |
| opening | 2 |
| food | 2 |
| contracts | 1 |
| kiln_fuel | 1 |
| morphology | 1 |

Most decisions pause or resume stalled facilities, and most of the rest trade.

### Build order and construction (baseline)

| Site | Placed | Commissioned | Main wait |
|---|---|---|---|
| Sediment dredge | 00:00 | 02:34 | |
| Nutrient washer | 00:10 | 13:01 | Carbonate 5.8 min |
| Photosynthetic field | 02:40 | 04:09 | |
| Waste collector | 02:50 | 18:01 | Carbonate 7.2 min |
| Clean-flow node | 17:10 | 21:57 | |
| **Silicate pit** | 18:10 | **69:16** | **Carbonate 46.4 min** |
| Shelter (home_6) | 38:10 | 66:55 | Carbonate 26.4 min |
| Culture bed | 53:10 | 65:25 | Carbonate 11.3 min |
| Mineral washery | 69:20 | 73:53 | |
| Carbonate cutter | 74:00 | 80:51 | Prepared Silica 5.3 min |
| Ceramic kiln | 74:10 | 89:20 | Prepared Silica 13.1 min |
| Waste digester | 89:30 | 102:46 | Fired Ceramic 10.8 min |
| Detox clinic | 102:50 | 110:00 | Ceramic, Repair Enzyme |
| Nutrient kitchen | 110:10 | not finished | Fired Ceramic |

Between 18:10 and 69:16 the economy builds almost nothing except housing and a culture bed. Every site in that window is waiting for Carbonate.

### Trade flows and value balance

Values use the base prices from §15: Carbonate 4, Biomass 1, Staple 2, Growth Nutrient 8 (partner price).

| Run | Sold | Value sold | Bought | Value bought |
|---|---|---|---|---|
| Baseline | Biomass 20, Staple 14, Growth Nutrient 5 | 88 | Carbonate 27 | 108 |
| Best | Biomass 28, Staple 16, Growth Nutrient 5 | 100 | Carbonate 30 | 120 |
| Builder 3 | Biomass 16, Staple 16, Growth Nutrient 6 | 96 | Carbonate 29 | 116 |

The new export market works as specified: it is modest, gives no free advanced goods, and doesn't collapse prices.

At the small level, though, it earns only about 0.6 stored value per minute. That buys roughly 0.15 Carbonate a minute. The baseline produced 209 Biomass and sold only 20 of it; demand, not supply, is the cap.

The *Fertile Exchange* contract (Carbonate reward) is declined in every run. In the baseline that happens at 53:10, because 8 Growth Nutrient is not in stock by the 55:00 deadline. The governor's opening sets the Nutrient reserve to 0 so migrants can use it, and that choice spends the Nutrient the contract would need.

## The dominant bottleneck: a Carbonate and Mineral Jaw lock

The sweep's three levers cannot reach this. It is structural:

1. **Carbonate only comes from trade until about 80 minutes.**
   - The Carbonate cutter needs Prepared Silica.
   - Prepared Silica needs the Washery, which needs the Pit.
   - The Pit, the Washery and every shelter also cost Carbonate.
   - So the opening has to buy, at about 0.15/min, the Carbonate that unlocks Carbonate. In the baseline, the Pit alone waited 46 minutes for its 2 Carbonate while shelters competed for the same stock.
2. **Mineral Jaw is locked behind Repair Enzyme.** Jaw's research cost includes 1 Repair Enzyme. Enzyme comes from the Waste Digester (Carbonate 3, Fired Ceramic 2), which needs the Kiln, which needs Prepared Silica. Until then the Pit and the Cutter both run at 50% (`environment:without mineral_jaw`, 45–53 blocked minutes). Enzyme arrives after 100 minutes, so Jaw is never researched in time.
3. **The Adapted class is short.**
   - The Pit, Cutter, Washery, Kiln, Retting pool and Resin curing all compete for Adapted workers.
   - Adapted vacancies reach 135–145 WP-minutes in the Builder-3 and best runs.
   - Adapted posts are filled below class for 170 WP-minutes.
   - This is why artisan relief and 4-WP Builders hurt.

Blocked entity-minutes (baseline, 437 in total):

| Cause | Minutes |
|---|---|
| Carbonate | 130 |
| Without Mineral Jaw | 45 |
| Dry-season farms | 27 |
| Fired Ceramic | 26 |

In the Builder-3 and best runs, Adapted workforce is the third cause, at 37–41 minutes.

## Caveat on the instrument

The governor is a heuristic. A better player could do somewhat better. For example, it could hold shelters back so the Pit gets the first Carbonate, or open the Washery earlier.

I don't think that would close the gap. The best runs still finish the Cutter around 77–81 minutes and Jaw is unreachable, so the Reef (Memory-tier homes plus three stages) is out of reach by a wide margin, not a few minutes. I have not tuned the governor further, because tuning it towards a pass would turn the instrument into the lever.

## Options for Rich (not tested; each changes design rules)

1. **Ease the Carbonate bootstrap.** For example:
   - a first-instance Carbonate cutter costing Carbonate only;
   - a higher early partner Carbonate rate;
   - an opening stock of Carbonate.
2. **Unlock Mineral Jaw earlier.** For example:
   - research without Repair Enzyme;
   - an early Enzyme source (the `emergency_enzyme` recipe exists but needs Anoxic Organics).
3. **Relieve Adapted demand.** For example:
   - fewer Adapted jobs on the Pit or Cutter;
   - a General-class option on the Washery.
4. **Accept a longer horizon** for the Reef, beyond 120 minutes.

Each is a material balance or design change, so it is Rich's call. Once Rich picks which to try, the existing sweep tool can test it.

## Reproduce

```
python3 -m economy.sweep economy/data/experiments/governor_sweep_v2.json
```

About 6 minutes on 2 cores. The output is deterministic.
