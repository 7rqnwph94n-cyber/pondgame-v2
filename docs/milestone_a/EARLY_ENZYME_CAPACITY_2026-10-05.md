# Early Enzyme capacity scheduling — 5 October 2026

**Promising legal strategy found, not adopted as a default:** order two additional digesters at 80:00, protect Biomass by temporarily pausing at most one Culture Bed above a 30-minute food buffer, and temporarily staff the Ceramic Kiln first. All three digesters are commissioned before Symbiotic; unpaid upkeep and food emergency time are both zero through 240:00.

Reproduce with `python3 tools/test_early_enzyme_capacity.py --check`. This runs one control plus eight bounded candidates and verifies committed JSON byte for byte. The control summary is asserted equal to the prior upkeep diagnosis. No economy definitions, recipes, rates, workforce rules, launch defaults or production governor config were changed.

## Comparison

Capacity time is when the 10-second plan first observes three commissioned digesters, not the exact commissioning event.

| Candidate | Three observed | First Symbiotic | Unpaid upkeep min | Food emergency min | Gel shortage residence-min |
|---|---|---|---:|---:|---:|
| reference | — | 106:29 | 54.7 | 0.0 | 3.0 |
| 60 min: orders only | 103:10 | 193:39 | 0.0 | 0.0 | 3.0 |
| 60 min: protect Biomass above 30 food minutes | 103:10 | 193:39 | 0.0 | 0.0 | 3.0 |
| 80 min: protect Biomass above 30 food minutes | 107:50 | 115:39 | 0.0 | 4.0 | 4.8 |
| 60 min: protect Biomass above 45 food minutes | 103:10 | 193:39 | 0.0 | 0.0 | 3.0 |
| 70 min: orders only | 103:10 | 193:39 | 0.0 | 0.0 | 3.0 |
| 80 min: orders only | 111:50 | 193:49 | 0.0 | 0.0 | 3.0 |
| 80 min: protect Biomass above 45 food minutes | 111:50 | 193:49 | 0.0 | 0.0 | 3.0 |
| 80 min: protect above 30 food minutes; pause at most one bed | 108:00 | 115:39 | 0.0 | 0.0 | 4.8 |

All runs have zero Staple shortage and zero devolution. None reaches Memory or a Reef stage. The 60-minute 30/45-buffer and 80-minute 45-buffer candidates never activate protection: they execute only the two construction orders, so their duplicate outcomes are expected and not independent evidence for protection efficacy.

## Selected strategy: six legal player actions

- 80:00: order `early_digester_1` and `early_digester_2`, normal costs and construction, site priority 10.
- 96:30: food buffer exceeds 30 minutes; pause only `bed_1` to let Biomass feed Ceramic production, and set `ceramic_kiln_1` to labour priority 3.
- 108:00: three digesters observed commissioned; restore normal kiln priority and resume `bed_1`.

The controller would resume food production if food falls to 15 minutes or a food emergency appears. It reads only `observe(sim)` for decisions and uses legal `Simulation.issue(source='player')` commands. It runs after the unmodified reference governor on its 10-second cadence. There is no injected inventory, free construction or hidden staffing bonus.

Exact commissioning: original 69:19, additional 102:59 and **107:56**. First Symbiotic is **115:39**, 9:10 later than the control. Grace ends at 115:40, with all three digesters fully staffed and running: combined supply **0.75 Enzyme/min**, actual upkeep demand **0.55/min** including the added capacity and resulting colony. Enzyme stock is 13 and food buffer 28.3 minutes at that point.

At 240:00 there are two Symbiotic homes, population 152, food buffer 71.2 minutes and Enzyme stock 28. All three digesters remain fully staffed. Maintenance weight has grown to 60, so demand is now **0.75/min**, exactly matching nominal production; it has no spare capacity for further growth. The existing reserve may mask future shortages. Do not claim indefinite solvency.

## Limits and acceptance

Pausing all Culture Beds at the same 30-minute threshold causes 4.0 minutes of food emergency. Pausing only one preserves food in this trajectory. Ordering extra capacity earlier without protection avoids upkeep but delays Symbiotic to about 194 minutes; no rule change is required to explain these differences.

The selected trajectory improves upkeep and retains Symbiotic within 120 minutes, but cumulative Gel shortage rises from 3.0 to 4.8 residence-minutes, alongside a second Symbiotic home. Residence-minutes add shortage across homes; this is not 4.8 elapsed minutes of colony-wide shortage. No home devolves, but the Gel supply trade-off remains open. This is not a full long-game/ Reef pass.

The plan is a timed simulated strategy alongside the governor, not a new human opening or demonstrated novice onboarding. It has not been wired into Autoplay or the client's launch. Next systems review should check Gel supply and capacity margin beyond four hours before adopting any governor strategy. Baseline rules remain unchanged.
