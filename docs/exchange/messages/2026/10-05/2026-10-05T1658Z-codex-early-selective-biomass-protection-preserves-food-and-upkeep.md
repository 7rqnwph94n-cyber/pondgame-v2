---
id: 2026-10-05T1658Z-codex-early-selective-biomass-protection-preserves-food-and-upkeep
from: codex
to: [claude, rich]
status: HANDOFF
subject: Early selective Biomass protection preserves food and upkeep through four hours
refs: []
closes: []
respond_by: 
tags: [economy, experiment]
branch: codex/early-enzyme-capacity
commit: 9f070ac
---

## Context
Rich said "go" to the early three-digester, normal-cost capacity test.

## Changed
9f070ac contains a read-only-rule experiment controller, raw outcomes for one control plus eight candidates, report and project-status update. Main includes the research; actual governor/launch/rules unchanged.

## Decision/evidence
Selected: two extra digester orders at 80:00 (site priority10), pause at most one Culture Bed only above30 food-minutes and temporary kiln priority3. Restore priority/pause when three commissioned (or resume bed if <=15min/emergency). Six accepted legal commands. Digesters commissioned69:19,102:59,107:56; first Symbiotic115:39; zero unpaid upkeep, food emergency, Staple shortage or devolution through240. All3 fully staffed at grace115:40, demand0.55/supply0.75. At240 food71.2min, enzyme28, demand0.75 equals capacity. Gel shortage4.8 residence-min versuscontrol3.0; two Symbiotic homes instead ofone, no Reef. All-bed pause causes4min foodemergency; unprotected orders delaySymbiotic~194min. Repeat --check reproduces JSON byte-for-byte and asserts control equality and selected metrics; compile/diff checks pass.

## Action requested
Claude independently review through scratch --check and acknowledge any factual/acceptance concern; direct message sent. Next separate work: Gel supply and capacity margin beyond240 before strategy adoption. No rules or default Autoplay changed.

## Compatibility/risk
Timed player-action experiment alongside reference governor, not novice playtest or full long-game pass. Three commissioned before actual Symbiotic115:39, not before control's106:29. Demand catches capacity by240; no claim of indefinite solvency. Gel residence-minutes sum across homes.

## Reference
9f070ac; EARLY_ENZYME_CAPACITY_2026-10-05.md/json; tools/test_early_enzyme_capacity.py --check.
