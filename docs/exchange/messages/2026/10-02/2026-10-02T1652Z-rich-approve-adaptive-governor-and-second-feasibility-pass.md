---
id: 2026-10-02T1652Z-rich-approve-adaptive-governor-and-second-feasibility-pass
from: rich
to: [claude, codex]
status: DECISION
subject: Approve adaptive governor and second feasibility pass
refs: [2026-10-02T1613Z-claude-four-economy-decisions-needed-before-the-next-sweep, legacy:AGENT_CHAT.md#2026-10-02T16:50Z]
closes: [2026-10-02T1613Z-claude-four-economy-decisions-needed-before-the-next-sweep]
respond_by: 
tags: [economy, decision]
branch: claude/milestone-a-honest-economy
commit: 5ef1c26
relayed_by: codex (legacy log), recorded by claude
---

## Context

Rich answered Claude's four economy decisions. Codex relayed the decision in the legacy log (`legacy:AGENT_CHAT.md#2026-10-02T16:50Z`, commit `5ef1c26` on `claude/milestone-a-honest-economy`) before the exchange was installed. Claude records it here so it lives in the exchange.

## Changed

None by this message.

## Decision/evidence

Rich, verbatim as relayed by Codex:

> 1. Approve an adaptive heuristic reference governor. It must react only to information and actions available to a competent player, log its decisions and remain deterministic under a fixed seed/configuration.
> 2. Repeat the seasonal calendar after 90:00 rather than extending Dry indefinitely. Preserve the authored cycle and document the wrap boundary.
> 3. Redefine early Carbonate access around earned purchasing power: allow the neighbouring settlement to buy modest quantities of Staple Culture and Biomass so a functioning opening economy can fund Carbonate imports. Do not solve this with free advanced goods, a huge starting stock or a blanket price collapse.
> 4. Include protected Builder allocations of 2, 3 and 4 WP in the next bounded sweep. Retain food-emergency pre-emption at every level.
>
> First push commit `39a8a1b`. Then implement and test the adaptive governor, repeating calendar and early export market. Run single-lever and cumulative comparisons including Builder 2/3/4, and select the least-generous package that reaches Symbiotic without a self-supplied-Gel failure, remains food/maintenance solvent and completes the Memory Reef within 100–120 minutes. Report governor decisions/build order, milestone timings, trade flows and value balance, construction utilisation, population, shortages, unpaid upkeep, blocked entity-minutes and the next dominant bottleneck. If no bounded package passes, stop and report evidence before expanding ranges.
>
> The governor is a balance instrument, not a hidden production bonus or intended final player AI. Export prices/caps require provenance and must not trivialise food security. Builder allocation remains visible and player-controllable; the governor may choose among legal settings but may not bypass the food-emergency predicate.

Claude's interpretation, labelled as such: `39a8a1b` is already on `origin` (Rich pushed it). Claude starts the governor work immediately after the exchange is installed.

## Action requested

None. Claude is executing; progress goes on `status/claude.md`.

## Compatibility/risk

As stated in the decision.

## Reference

`legacy:AGENT_CHAT.md#2026-10-02T16:50Z`; `docs/milestone_a/THROUGHPUT_SWEEP_V1_RESULTS.md`.
