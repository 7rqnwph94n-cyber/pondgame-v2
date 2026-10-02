# Candidate bootstrap rules v1: results

Date: 2026-10-02 · Author: Claude · Branch: `claude/milestone-a-honest-economy`
Responds to: `docs/AGENT_CHAT.md` 2026-10-02T14:46Z (Rich via Codex, "Simulate the preferred bootstrap resolutions").

Reproduce:

```bash
python3 -m economy.run --plan economy/data/plans/verdant_reference_b.json \
    --overlay economy/data/experiments/candidate_bootstrap_rules_v1.json
python3 -m economy.sweep economy/data/experiments/candidate_bootstrap_sweep.json
python3 -m economy.sweep economy/data/experiments/candidate_lever_ladder.json
```

## Verdict

- **All eight rules are encoded and remove every static deadlock** found in Milestone A. The bootstrap analyser reports the full tier ladder reachable.
- **The Memory Reef is still not feasible in 90 minutes.**
  - Across the 96-run bounded sweep, no setting completes the Reef, and **no run reaches even one Symbiotic home**.
  - With the recommended values, the reference city gets its first Stable at **41:29** (doc target 12–18) and ends with 3 Shelters, 3 Stables and 56 population.
- **The binding constraints have moved** from structural deadlocks to throughput: workforce/population growth, Carbonate, the Artisan tier, and the length of the Memory chain.
- The candidate is **not promoted** into `verdant_v0_2.json`, as instructed.

## How each decision was encoded (`economy/data/experiments/candidate_bootstrap_rules_v1.json`)

| # | Rich's rule | Encoding |
|---|---|---|
| 1 | Basic Washer, Clean-Flow Node and Waste Collector use General labour | Washer and Clean-Flow Node jobs → General. New `waste_collector` (2 Carbonate, 1 Biomass, 10 work, 2 General; cost provisional) provides Waste alongside the Digester. Channel Separator and Digester stay Adapted. |
| 2 | First Kiln Adapted; first Detox Clinic without Composite | New generic **first-instance terms**: the first Kiln has 4 Adapted jobs (later Kilns 4 Artisans); the first Clinic costs 2 Ceramic + 1 Enzyme. Health stays a Symbiotic gate. |
| 3 | First Memory Circle uses Artisans | First-instance jobs: 3 Artisans. Later Circles need Coordinators. |
| 4 | First Silicate Pit costs no Enzyme | First-instance cost: 2 Carbonate. The Cutter keeps its Enzyme cost. |
| 5 | Inefficient pre-Mineral-Jaw cutting | Cutter no longer requires Mineral Jaw; it runs at 50% without it (same pattern as the Pit). |
| 6 | High Water slows sediment; soften the no-Burrowing penalty | High Water sediment ×0.25 (was closed); Dredge without Burrowing ×0.70 (was ×0.60). |
| 7 | Configurable Builder allocation | New Builder job: `builder_wp` workers reserved, only while a site is ready for work. Its rank is set in `job_priority` and the player can re-rank it. Candidate: 2 WP, ranked after services and before food. |
| 8 | Maintenance grace and small Enzyme reserve | Upkeep is now enforced: 1 Enzyme per 10 weight per 8 min. Unpaid upkeep suspends the Maintenance service. The grace period ends at the first Symbiotic home, and the colony starts with 1 Repair Enzyme. |

## Bounded comparison of the open numbers (96 runs)

Mean outcome for each value, averaged over all other parameters. Plan B, 90 minutes:

| Parameter | Value | Mean pop | Mean first Stable | Runs reaching Symbiotic | Mean Maintenance unpaid |
|---|---|---:|---:|---:|---:|
| High Water sediment | **0.25** / 0.5 | 46.3 / 43.5 | 37.9 / 34.7 min | 0 / 0 | 9.2 / 10.2 min |
| Dredge without Burrowing | **0.7** / 0.8 | 44.7 / 45.1 | 38.5 / 34.2 min | 0 / 0 | 9.2 / 10.3 min |
| Starting Repair Enzyme | **1** / 2 / 4 | 45.0 / 44.9 / 44.9 | 36.3 min (all) | 0 | 11.1 / 10.0 / 8.0 min |
| Builder WP | **2** / 4 | 45.1 / 44.8 | 37.1 / 35.5 min | 0 / 0 | 9.4 / 10.0 min |
| Builder rank | after food / **before food** | **32.0 / 57.8** | **never / 36.3 min** | 0 / 0 | 0 / 19.4 min |
| Upkeep grace ends at | first Stable / **first Symbiotic** | 45.5 / 44.3 | 36.3 min (both) | 0 / 0 | **19.4 / 0.0 min** |

**Recommendation.** Bold marks the recommended value. No setting is viable, so these are the least generous values that are no worse than the more generous alternatives tested. They are what the candidate overlay now uses.

- **Builder rank decides everything.** Ranked after food, builders never get workers and the city never reaches a Stable (all 48 runs).
- **The grace period must last until the first Symbiotic home.** Ending it at the first Stable leaves Maintenance unpaid for about 19 minutes, because no Enzyme producer exists yet, and that blocks evolution.
- **High Water and Dredge multipliers matter little.** The more generous values bring the first Stable 3–4 minutes earlier but change nothing downstream.
- **More starting Enzyme only helps** when the grace period ends early.

## What still blocks the Reef: cumulative lever ladder (diagnostic only)

Each step keeps every earlier step's changes. This is evidence about where the limits are, not a proposal.

| Step | Reef | First Stable | First Symbiotic | First Memory | Pop |
|---|---|---:|---:|---:|---:|
| L0 candidate rules | – | 41:29 | – | – | 56 |
| L1 +100 Carbonate | – | 31:33 | – | – | 54 |
| L2 +30 Repair Enzyme | – | 31:33 | – | – | 54 |
| L3 +40 Growth Nutrient | – | 27:28 | – | – | 76 |
| L4 +6 full Shelters (+48 pop) | – | 08:03 | – | – | 124 |
| L5 +40 Silica, Ceramic, Fibre, Resin, Biomass | – | 12:11 | – | – | 124 |
| L6 +40 Composite, Ornament, Gel; +60 Staple | **88:14** | 06:00 | 50:23 | 80:54 | 152 |
| L7 research 4× faster | 2 stages | 06:00 | 55:38 | 75:25 | 144 |
| L8 evolution sustain timers halved | 85:00 | 05:15 | 54:31 | 72:12 | 144 |

The Reef first fits inside 90 minutes only when the whole Artisan economy is free and the city starts with roughly double its population. Even then it finishes at 85–88 minutes, and results are timing-sensitive: L7 regresses even though it is strictly more generous.

What blocks it:

1. **Population and labour throughput.**
   - Growth is capped at 1 organism/min, and every Shelter costs 2 Carbonate plus builders.
   - Food and services consume the General workforce.
   - Evolving Shelters converts General workers rather than adding them (771 Adapted WP-minutes worked below class in L0).
2. **Carbonate.** Still the top bottleneck: 241 blocked entity-minutes in L0. Trade is capped at 0.5/min and pre-Jaw cutting gives 0.3/min.
3. **The Artisan tier.**
   - Symbiotic needs Health, Distribution and Gel.
   - Gel, Composite, Ornament and later Kilns all need Artisans, and only Symbiotic homes supply them.
   - The first Symbiotic home must get its Nutrient Kitchen staffed within 7 minutes or devolve. The analyser now flags this as a "self-supplied need".
4. **Length of the Memory chain.**
   - Memory Ganglion needs Gel and Ornament before 100 Nursery-work starts, which is 25 minutes at 4 WP.
   - The Circle, Enclave (4-minute sustain), unlock and three stages follow.
   - About 12 Ornaments are needed at 0.25/min per Artisan Organ.

## Engine changes made while doing this (reviewed by tests)

- First-instance building terms; the Builder allocation; maintenance upkeep with grace, payment and suspension.
- Player re-ranking of `builders` / `research` labour. Research ranked last by default had starved Mineral Jaw of Nursery workers for 66 minutes in one run.
- **Fix:** Coordinators covering lower-class jobs now count as "available" for the Great Work unlock, and a ready stage claims them first. Before this, a busy city could never begin the Reef.
- **Fix:** the free-housing plan trigger no longer breaks when a Great Work stage site exists.
- New plan triggers `stock_below` and `free_housing_below`; residence presentation state in snapshots (Codex request); the `economy.sweep` tool.
- Doc-faithful and probe characterisations are unchanged (`verdant_v0_2.json` keeps upkeep and builders off).

## Decisions needed from Rich

1. **Promotion.** Promote rules 1–8 (values above) into `verdant_v0_2.json` now as the structural baseline, or keep them as a candidate until a viable package exists? Recommendation: promote rules 1–5 and 7–8 now, because they remove proven deadlocks, and treat feasibility as a separate tuning pass.
2. **Which throughput levers to test next.** Options:
   - opening population or migration rate;
   - farm and service job sizes;
   - the Carbonate supply rate;
   - first-instance Adapted staffing for the first Kitchen/Workshop/Organ, the same pattern as the Kiln;
   - Memory Ganglion Nursery-work;
   - Reef stage costs;
   - accepting a longer first-success target than 78–88 minutes.

   The sweep tool can compare any of these within minutes.
3. **Builder default.** Should builders outrank food crews by default, or should that stay a player choice exposed in the UI? The default matters more than any number tested.
