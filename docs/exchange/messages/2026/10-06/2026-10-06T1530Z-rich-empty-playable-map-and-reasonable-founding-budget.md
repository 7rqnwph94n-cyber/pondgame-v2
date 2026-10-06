---
id: 2026-10-06T1530Z-rich-empty-playable-map-and-reasonable-founding-budget
from: rich
to: [claude, codex]
status: DECISION
subject: Empty playable map and reasonable founding budget
refs: []
closes: []
respond_by: 
tags: [opening, budget]
branch: 
commit: 
relayed_by: codex
---

## Context

Rich rejects a ready-built settlement as the play start.

## Changed

Codex takes engine/simulation.py, engine/definitions.py, new empty-start overlay and client startup/settings for this block.

## Decision/evidence

Rich: “MAP MUST BE EMPTY AT START OF PLAY WITH A REASONABLE BUDGET TO START.”

Interpretation: no prebuilt homes, facilities, sites, roads, crossing or visible carriers. Preserve natural terrain/resources. Add costed initial materials/provisions/currency and an off-map founding party so normal paid construction can bootstrap the first homes. Founders land in built shelters, with food/workforce accounted; make First Nursery buildable in this scenario. Existing accepted slice overlay and baseline remain unchanged.

## Action requested

Claude: avoid shared engine/client files while Codex implements; review the resulting opening and bootstrap budget when handed off.

## Compatibility/risk

New optional founding-party definitions path and separate client overlay. No wire/schema change is needed: displayed population continues to mean housed population, and workforce already includes current available labour.

## Reference

client/settings.cfg; economy/engine/simulation.py; economy/data/experiments.
