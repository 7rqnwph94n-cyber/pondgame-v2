---
id: 2026-10-02T1613Z-claude-four-economy-decisions-needed-before-the-next-sweep
from: claude
to: [rich]
status: REQUEST
subject: Four economy decisions needed before the next sweep
refs: [legacy:AGENT_CHAT.md#2026-10-02T15:57Z]
closes: []
respond_by: Rich's next review
tags: [economy, decision]
branch: claude/milestone-a-honest-economy
commit: 
---

## Context

These are carried over from my last legacy handoff (`legacy:AGENT_CHAT.md#2026-10-02T15:57Z`), so they show as open in the index until answered.

## Changed

None.

## Decision/evidence

Throughput sweep v1: 0/288 combinations pass, and none reaches Symbiotic by 120:00. See `docs/milestone_a/THROUGHPUT_SWEEP_V1_RESULTS.md` on `claude/milestone-a-honest-economy`.

## Action requested

Rich, please decide:

1. Approve an **adaptive reference player** (a heuristic governor) before the next sweep. This is new tooling, not balance.
2. **Calendar after 90:00:** extend the Dry Phase (current assumption), or repeat the seasons?
3. **Carbonate lever:** redefine it as early payment or supply (starting Carbonate +6/+12, the neighbour buying surplus Staple/Biomass, or a lower price), since trade rate does not bind.
4. **Builder WP 2/3/4** in the next sweep?

## Compatibility/risk

No balance values change until you decide.

## Reference

`python3 -m economy.sweep economy/data/experiments/throughput_sweep_v1.json`.
