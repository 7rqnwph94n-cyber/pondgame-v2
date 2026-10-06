---
id: 2026-10-06T1815Z-rich-every-building-must-connect-to-the-supply-road-network
from: rich
to: [claude, codex]
status: DECISION
subject: Every building must connect to the supply road network
refs: []
closes: []
respond_by: 
tags: [roads, spatial]
branch: codex/roads-spatial
commit: 
relayed_by: codex
---

## Context
Rich corrected the proposed transport policy during the roads implementation.

## Changed
All buildings require connection to the same supply road network. There is no foot-transport exception.

## Decision/evidence
Rich: "no, all buildings must connect"

Codex interpretation: placement requires a connected entrance; removing the connection blocks fresh deliveries, construction, staffing and services. An isolated supply anchor does not count as a road.

## Action requested
Claude: retain this strict rule in the domain. Codex has received your bundle and is integrating the client. Codex is correcting the last-road-removal loophole and collinear junction handling in economy/engine/spatial.py and adding regression tests; please avoid simultaneous edits to those files. Natural obstacle parity and full integration review remain open.

## Compatibility/risk
The original nonspatial baseline remains available. Current feature is in development and has not replaced the playable main build. Native review is temporarily blocked because the Mac is locked.

## Reference
claude/roads-spatial at ca5f37f; codex/roads-spatial integration branch.
