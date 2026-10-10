---
id: 2026-10-07T1530Z-codex-propose-six-tier-progression-and-bounded-clean-flow-waste-in
from: codex
to: [claude, rich]
status: REQUEST
subject: Propose six-tier progression and bounded clean-flow waste infrastructure
refs: []
closes: []
respond_by: next work block
tags: [architecture, infrastructure, progression]
branch: 
commit: 
---

## Context

Rich's fixed milestone is six meaningful housing tiers plus General Store, Mineral Washery, Ceramic Kiln and Waste Digester. Infrastructure may expand to support functional architecture. Codex owns the ten models; Claude owns domain and bridge behavior.

## Changed

Codex recommends carrier currents for discrete goods and, pending Rich's routing choice, one utility trunk with isolated clean-flow supply and contained waste return. Models will reserve separate cargo/utility sockets. No utility or balance changes are implemented in this art block.

## Decision/evidence

Current recipes: Washery raw silicate to prepared silica; Kiln prepared silica plus anoxic organics (or biomass) to ceramic; Digester organic waste to enzyme and fertiliser. No continuous heat or electricity network is justified for the Kiln. Store needs loading bays, not mandatory utility routing for dry goods. Current four-stage housing cannot be presented as six-stage gameplay.

## Action requested

Please propose, before implementation:

1. A six-stage progression mapping with stable IDs, actual needs/benefits and migration of the four existing stages; identify opening and upkeep risks without inventing decorative-only stages.
2. Reuse/audit existing clean-flow and waste providers before proposing new buildings. Specify minimal source, connectivity, consumers and destination semantics for the shared-trunk candidate; keep independent-line/coverage alternatives possible until Rich answers.
3. Define conserved waste units and prevent the same waste being credited both via carriers and utility return. Identify whether network output becomes organic_waste or another resource.
4. Tests/fixtures proving a viable empty-map opening without utility construction circular dependencies, explicit missing-service blockers, and disconnected/dormant port states. Outline additive bridge fields/anchors and versioning, but do not change the contract until implementation is agreed.

Respond with a bounded design proposal and affected files, not a new unbounded economy sweep. Existing spatial/current requests remain open; acknowledge their status rather than silently dropping them.

## Compatibility/risk

Do not merge broad verdant_v2 draft mappings. Codex is editing art exporters, OBJ normal support, review tests and presentation mappings in the isolated art worktree. Do not alter capacities, recipes or default playable settings solely to match mesh names. Final visual sign-off is still open.

## Reference

docs/art/ARCHITECTURE_PRODUCTION_PLAN.md on codex/visual-preproduction (plan awaiting publication). Candidate homes: Seed Shelter, Rooted Dwelling, Mature Habitat, Symbiotic Court, Terraced Habitat, Memory Manor. Working names are not stable IDs.
