# Workforce scale v1: fewer early job slots

**Request:** Rich chose "1", fewer early job slots, at 2026-10-04T0952Z (relayed by Codex).

**Specs:** `economy/data/experiments/workforce_scale_v1_baseline.json` and `workforce_scale_v1_playable.json`.

**Setup:**
- Reference governor v3; 120-minute horizon; v2 acceptance criteria.
- 8 runs: four levels on each of two bases.
- Candidate only. **Nothing is promoted.**

## What was varied

Each level removes one job slot from early crews of 3–4. Recipe outputs and cycle times are unchanged, so the same work needs fewer people, and every crew stays at 2 or more. The levels are cumulative, least intrusive first:

| Level | Change |
|---|---|
| **L1: extraction −1** | Sediment Dredge 3→2 General; Silicate Pit 4→3 and Carbonate Cutter 4→3 Adapted |
| **L2: + processing −1** | Mineral Washery 3→2 (the first Washery stays General, 3→2); Retting, Resin Curing and Waste Digester 3→2; first Kiln 4→3 |
| **L3: + food −1** | Nutrient Washer, Photosynthetic Field, Culture Bed, Fibre Garden and Resin Grove 3→2 General |

The two bases are the untouched v0.2 rules ("baseline") and the client's provisional playable package (`candidate_playable_v1`, "playable").

## Results

| Base | Level | First Stable | First Symbiotic | Homes at 120:00 (Shelter/Stable/Symbiotic) | Population | Food | Unpaid upkeep | Top bottlenecks |
|---|---|---|---|---|---|---|---|---|
| baseline | none | 24:06 | – | 8/3/0 | 97 | solvent | 0 | Carbonate, dry farms, no Mineral Jaw |
| baseline | L1 | 23:59 | – | 8/3/0 | 96 | solvent | 0 | Carbonate, no Mineral Jaw, dry farms |
| baseline | L2 | 23:59 | – | 8/3/0 | 92 | solvent | 0 | Carbonate, no Mineral Jaw, dry farms |
| baseline | L3 | 20:49 | – | 8/3/0 | 96 | solvent | 0 | Carbonate, no Mineral Jaw, Fired Ceramic |
| playable | none | 24:29 | – | 7/4/0 | 88 | solvent | 0 | Carbonate, General workforce, Biomass |
| playable | L1 | 24:29 | – | 9/3/0 | 108 | solvent | 0 | Carbonate, construction labour, no Mineral Jaw |
| playable | L2 | 24:29 | – | 8/3/0 | 94 | solvent | 0 | Carbonate, no Mineral Jaw, General workforce |
| playable | **L3** | **21:39** | **83:59** | 9/1/1 | 92 | solvent (3.0 min Gel shortage) | **12.7 min** | no Mineral Jaw, Adapted workforce, surface Carbonate exhausted |

**Nothing passes: 0 of 8 runs.** No run opens the Reef.

- Food stays solvent in every run: no Staple shortage and no food emergency.
- There are no devolutions.

## What it shows

1. **Fewer slots relieve the labour shortage, but Carbonate takes over again.** On the playable base, the General-workforce bottleneck drops out of the top three at L1 (it reappears third at L2), and Carbonate is the main block at every level except L3. Freed workers have nothing to build with.
2. **Only the full cut (L3) on the playable base reaches Symbiotic.** It does so at 83:59, the earliest of any run so far (sweeps v2–v4 never got before 104:19). But the Symbiotic home then cannot pay its Repair Enzyme upkeep (12.7 minutes unpaid), and the 12-unit gleaning reserve runs dry. These are the same two follow-on blockers as sweep v3, reached about 20 minutes sooner.
3. **On the untouched v0.2 baseline, fewer slots don't move Symbiotic at all.** Without the playable package's Carbonate bootstrap and Jaw-without-Enzyme rule, Carbonate is binding throughout.
4. **Instrument note.** With governor v3, the v0.2 baseline reaches first Stable at 24:06, against 43:44 with governor v1. The difference is v3's labour-priority rule, which staffs the Dredge and Washer first. Earlier sweep reports used v1 and v2, so their Stable times aren't directly comparable with these.

## Least intrusive result

No level passes. The **least intrusive level that changes the outcome is L3 on the playable base**. It brings Symbiotic forward by about 20 minutes, but it leaves the long game blocked by Carbonate and Enzyme supply rather than labour.

Fewer job slots is necessary but not sufficient. For Rich, via Codex, the follow-up choices would be:

- **(a)** add a second, renewable Carbonate source in the opening, for example a larger gleaning reserve or slow regrowth;
- **(b)** relieve Repair Enzyme upkeep at the first Symbiotic home;
- **(c)** combine L3 with one of the other workforce directions (more people, or cheaper evolution);
- **(d)** treat the Reef as beyond the 120-minute slice, which the charter already does.

None of these is tested or promoted here.

## Reproduce

```
python3 -m economy.sweep economy/data/experiments/workforce_scale_v1_baseline.json
python3 -m economy.sweep economy/data/experiments/workforce_scale_v1_playable.json
```

Each takes about 15 seconds.
