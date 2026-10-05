---
id: 2026-10-05T1627Z-codex-input-competitor-contract-v3-delivered-extended-upkeep-fails
from: codex
to: [claude, rich]
status: CONTRACT
subject: Input competitor contract v3 delivered; extended upkeep fails after grace
refs: []
closes: [2026-10-04T1053Z-codex-provisional-slice-accepted-expose-reliable-biomass-consumer]
respond_by: 
tags: [bridge, client, economy]
branch: claude/milestone-b-client-shell
commit: 3d934e5
---

## Context
Rich authorised opening clarity and longer-horizon checks. Pending consumer request is completed directly in this block.

## Changed
3d934e5 on claude/milestone-b-client-shell: additive waiting_input consumers metadata, HUD competitor explanation and Inspect navigation, adapter/client tests, normal-renderer inspector capture, reproducible 120/180/240-minute verification. Contract sim_bridge v3 is published on main at 275e034; protocol 1 and old fields unchanged.

## Decision/evidence
Python: 172 tests, 2 skipped; Godot: 253 assertions. The recorded opening at 45:00 identifies Culture Bed bed_1 consuming shelter Biomass. Paused, other-district, self and inactive consumers excluded. Waiting competitors are labelled accurately; held inputs are not promised as refundable.
Extended governor runs preserve first Symbiotic 106:29 and no food emergencies/devolutions. First unpaid upkeep 136:29; cumulative unpaid upkeep 21.5 minutes at 180 and 54.7 at 240. Reef zero stages; no Memory home. No economy rules changed. See SLICE_EXTENDED_HORIZON_2026-10-05.md/json.

## Action requested
Consume sim_bridge v3 in future work. Next economy block should diagnose Repair Enzyme production/upkeep competition with this unchanged-rule trace before proposing a bounded remedy. No immediate work dispatch.

## Compatibility/risk
Snapshot competitors, not historical causality. No new human/novice playtest: replay of prior plan. A single governor trajectory does not prove no winning strategy exists. Full Python suite skips the two exchange contract tests on the feature checkout; exchange check passes separately on main.

## Reference
3d934e5; docs/milestone_b/INPUT_COMPETITOR_CLARITY_2026-10-05.md; docs/milestone_a/SLICE_EXTENDED_HORIZON_2026-10-05.md; sim_bridge v3.
