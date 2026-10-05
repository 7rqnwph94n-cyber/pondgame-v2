---
id: 2026-10-05T1622Z-rich-improve-opening-clarity-and-verify-longer-slice-horizon
from: rich
to: [claude, codex]
status: DECISION
subject: Improve opening clarity and verify longer slice horizon
refs: []
closes: []
respond_by: 
tags: [client, bridge, economy]
branch: 
commit: 
relayed_by: codex
---

## Context
Rich asked for status, then said "do it" to improving opening clarity and testing beyond 120 minutes.

## Changed
Starting a narrow HUD and bridge-adapter pass on hud.gd and economy/bridge.py.

## Decision/evidence
Rich verbatim: "do it". Interpretation: finish consumer diagnosis and longer-horizon verification.

## Action requested
Avoid overlapping these files during this block; no work required from Claude.

## Compatibility/risk
Additive versioned consumer metadata only; unchanged economy rules.

## Reference
141db45 and the pending consumer-diagnosis request.
