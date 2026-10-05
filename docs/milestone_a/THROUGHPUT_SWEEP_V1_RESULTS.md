# v0.2 promotion and throughput sweep v1: results

Date: 2026-10-02 · Author: Claude · Branch: `claude/milestone-a-honest-economy`
Responds to: `docs/AGENT_CHAT.md` 2026-10-02T15:18Z (Rich via Codex, "Promote bootstrap repairs and run throughput sweep").

Reproduce:

```bash
python3 -m economy.run --plan economy/data/plans/verdant_reference_c.json        # promoted baseline, 120 min
python3 -m economy.sweep economy/data/experiments/throughput_sweep_v1.json         # 288 runs, ~6 min on 2 cores
python3 -m economy.run --overlay economy/data/experiments/legacy_doc_faithful.json  # original Milestone A failure
```

## Verdict

- **Done as instructed:**
  - Rules 1–8 are promoted into `verdant_v0_2.json` with provenance.
  - The Builder allocation is protected (2 WP, before food) and pre-empted only by an explicit, inspectable food emergency.
  - Runs extend to 120 minutes.
  - The original failure stays reproducible through `legacy_doc_faithful.json`.
- **No tested combination meets the acceptance criteria.**
  - Across 288 runs (every combination of the five levers), **no run reaches a Symbiotic home within 120 minutes**, so none can complete the Reef.
  - There is therefore **no least-generous combination to recommend**, and I have not adopted any lever.
- **The three late-game levers cannot be evaluated yet.** Artisan relief, Ganglion Nursery-work and Reef costs had exactly zero effect, because the city never reaches the stage where they act.
- **Two upstream facts block that stage:**
  1. Early Carbonate is **payment-limited, not supply-limited**, so the requested "trade throughput" lever does nothing.
  2. Once Carbonate is relieved diagnostically, **construction labour and the General workforce bind**. The scripted reference player then becomes the dominant source of variance, so its results are not trustworthy evidence about balance.

## What was promoted

| Area | v0.2 baseline now | Provenance in data |
|---|---|---|
| Rules 1–6, 8 | As in `CANDIDATE_RULES_V1_RESULTS.md`, with the least generous values (High Water sediment 0.25; no-Burrowing 0.70; 1 starting Enzyme; grace until the first Symbiotic home) | `source` strings cite "candidate rule N (promoted by Rich, AGENT_CHAT 2026-10-02T15:18Z)" |
| Rule 7 Builders | `builder_wp` 2, rank `construction` before `food` | `construction_rules.source` |
| Food emergency | Enters below 4 food-minutes or on any residence Staple shortage; exits at ≥ 8 food-minutes with no shortage (hysteresis). While active, the Builder job ranks after food crews. | `construction_rules.food_emergency` |
| Horizon | 7200 s (120 min); `first_success_target_minutes` [100, 120] | `scenario` |
| Calendar beyond 90 min | **Assumption:** Dry Phase extended to 120 min (least generous). Needs your decision; see below. | `notes` |
| Legacy | `economy/data/experiments/legacy_doc_faithful.json` reverses all of the above | Characterisation tests use it |

Food minutes = (Staple in stores + residence Staple buffers) ÷ current settlement Staple consumption per minute. The emergency state, its reason and the Builder state are in every snapshot (`food_emergency`, `builders`). Builder states:

- `protected`: reserved ahead of food;
- `preempted_food_emergency`: ranked after food, with a reason;
- `idle`: no site ready;
- `disabled`: `builder_wp` 0.

## The sweep (`throughput_sweep_v1.json`)

Levels are listed least to most generous:

| Lever | Levels |
|---|---|
| Artisan relief | off · first Kitchen / Workshop / Organ use Adapted crews (4 / 5 / 4) |
| Early Carbonate | base · trade 0.75/min (max 45) · + pre-Jaw Cutter 65% · trade 1.0/min (max 60) + Cutter 65% |
| Population | base · migration 0.75/min · 1.0/min · 0.75/min + one starting Shelter (+8 pop) |
| Ganglion Nursery-work | 100 · 75 · 50 |
| Reef stage costs | ×1.0 · ×0.85 · ×0.7 (rounded, minimum 1) |

**Acceptance criteria (encoded in the spec):**

- (a) reaches Symbiotic with no devolution;
- (b) at most 5 residence-minutes of Staple shortage and at most 1 minute of unpaid upkeep;
- (c) Reef completed by 120:00. Before 100:00 is flagged as earlier than target.

**Plan:** `verdant_reference_c.json`. It is lever-agnostic: advanced buildings are placed when their inputs flow, not when a tier is reached, so lever effects can show. Housing waits while food is short; farms are added on low food-minutes.

### Single-lever results (others at base)

| Changed lever | First Stable | Symbiotic | Pop @120 | Staple short (res-min) | Devolutions | Blocked entity-min | Top bottleneck |
|---|---:|---|---:|---:|---:|---:|---|
| none (baseline) | 21:48 | – | 52 | 54.0 | 1 | 1605 | Nutrient-for-Carbonate trade exhausted |
| Artisan relief | 21:48 | – | 52 | 54.0 | 1 | 1605 | same |
| Carbonate trade 0.75 | 21:48 | – | 52 | 54.0 | 1 | 1325 | same |
| Carbonate trade 1.0 + Cutter 65% | 21:48 | – | 52 | 54.0 | 1 | 1322 | same |
| Migration 0.75 | 21:19 | – | 52 | 55.8 | 1 | 1632 | same |
| Migration 1.0 | 21:19 | – | 48 | 57.0 | 2 | 1639 | same |
| Migration 0.75 + 1 Shelter | 41:55 | – | 40 | 0.0 | 0 | 1073 | Carbonate |
| Ganglion 75 / 50 | 21:48 | – | 52 | 54.0 | 1 | 1605 | same |
| Reef ×0.85 / ×0.7 | 21:48 | – | 52 | 54.0 | 1 | 1605 | same |

Both cumulative ladders (least and most generous step of each lever, added in your order) also never reach Symbiotic. Marginal effects: 0/288 runs reach Symbiotic and 0/288 complete the Reef.

## Why nothing moves

1. **Early Carbonate is bought with Growth Nutrient.**
   - The neighbour has stock to spare, but the colony can only pay with its 20 starting value and Growth Nutrient (max 12 sold at 8).
   - Nutrient is also what migrants and evolutions consume, and it rarely reaches a tradeable surplus.
   - Raising the neighbour's sale rate therefore removes about 280 blocked entity-minutes of waiting but changes no outcome.
   - In the baseline, the Silicate Pit and Mineral Washery (the start of the Silica → Kiln → Clinic → Symbiotic chain) wait 58 and 63 minutes for Carbonate; the first Kiln is only commissioned at 96:38.
2. **Behind Carbonate, labour binds.** In diagnostic runs adding 12–50 starting Carbonate (not a lever proposal), the chain advances but stalls on construction labour and General workers.
   - Two protected builders give about 2 work-units a minute, about 240 over 120 minutes. The plan's buildings need about 600.
   - §10.3 and §19.6 assume roughly 10 idle builders.
   - Raising builders to 4–8 speeds the early game but starves food crews and causes devolutions in several runs.
3. **The scripted player is now the weakest instrument.**
   - Small, sensible plan edits swing outcomes more than any lever. Examples: farms added only while existing crews are full; crew overrides moved below food.
   - I found and fixed two real plan defects this way. The remaining variance means a fixed, timed script cannot stand in for a competent player once several levers interact.
4. **Calendar.** Extending the Dry Phase to 120 minutes costs a lot of food. With the seasons repeating instead (Bloom from 90:00), baseline Staple shortage falls from 54 to 0.2 residence-minutes. Neither version reaches Symbiotic.

## Recommendation and decisions needed

No balance values should change on this evidence. Before the next sweep I recommend:

1. **An adaptive reference player.** Replace the timed script with a small heuristic governor that each minute:
   - keeps food above a target;
   - adds housing while food is secure;
   - pauses idle crews to free workers;
   - spends value on the current bottleneck;
   - follows the Reef dependency graph.

   It would be deterministic and testable, and it would make lever results attributable to balance rather than script luck. **This needs your go-ahead; it is new tooling, not balance.**
2. **Calendar after 90 minutes:** extend Dry, or repeat the seasons (Bloom from 90:00)?
3. **Redefine the Carbonate lever as early payment or supply** rather than trade rate. Options:
   - starting Carbonate +6/+12;
   - the neighbour also buys surplus Staple or Biomass;
   - a lower Carbonate price.
4. **Add Builder WP (2/3/4) to the next sweep.** Your fixed 2 WP becomes binding as soon as Carbonate is relieved.

## Stable IDs added (handed to Codex)

- Snapshot `builders` per district: {`state`: `protected` | `preempted_food_emergency` | `idle` | `disabled`, `wp`, `reason`}.
- Snapshot `food_emergency`: {`active`, `reason`, `food_minutes`}. Report `food_emergency`: {`episodes`, `minutes_active`}.
- `waste_collector` is now a baseline building. First-instance terms are now baseline for Kiln, Clinic, Memory Circle and Silicate Pit.
- Plan triggers `food_minutes_below`, `food_minutes_above` and `vacancies_below` (plan data only).
