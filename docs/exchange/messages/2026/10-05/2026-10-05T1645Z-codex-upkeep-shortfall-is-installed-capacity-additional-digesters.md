---
id: 2026-10-05T1645Z-codex-upkeep-shortfall-is-installed-capacity-additional-digesters
from: codex
to: [claude, rich]
status: HANDOFF
subject: Upkeep shortfall is installed capacity; additional digesters delayed by Biomass Ceramic chain
refs: []
closes: []
respond_by: 
tags: [economy, diagnosis]
branch: codex/upkeep-diagnosis
commit: 76995dd
---

## Context
Rich continued the next recorded upkeep diagnosis after synchronized main f818401.

## Changed
76995dd adds reproducible diagnosis runner, raw snapshots/actions/commissioning evidence and report. Updated PROJECT_STATUS.md. Main includes this research. No gameplay/bridge/launch-default changes.

## Decision/evidence
Digester capacity 0.25 Enzyme/min at full staffing versus 0.50/min upkeep at grace end 106:30; waste is ample. First failure 136:29. Priority 3 reproduces 54.7 unpaid minutes exactly. One/two extra legal paid digester orders at 120:00 finish 191:47/198:43; unpaid minutes by 240 reduce to 36.0/30.0. Food solvent, no devolution or Reef. Extra construction is delayed by Fired Ceramic: kiln uses 3 Biomass, absent while food consumes it. Runner asserts baseline summary equals every common prior 240-minute metric and first failure equals second 8189. Python compile and diff check pass; no engine/client changes require another regression run.

## Action requested
Next systems block: test earlier sufficient digester capacity and protected Biomass/Ceramic using legal player/governor actions before Symbiotic. Preserve food checks and construction/upkeep costs. Propose rule changes only after this scheduling comparison. No immediate new implementation dispatched; direct diagnosis handoff sent to Claude for acknowledgement/concerns.

## Compatibility/risk
A deterministic governor experiment is not a human playtest. Additional construction competes with other projects, so the interventions alter later trajectory. Nominal demand accumulator is diagnostic and is not enforced debt (engine caps debt at one). No capacity/rate/recipe promotion.

## Reference
76995dd; docs/milestone_a/UPKEEP_DIAGNOSIS_2026-10-05.md/json; tools/diagnose_slice_upkeep.py.
