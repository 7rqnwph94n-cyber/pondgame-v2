# Pondgame v2 status — 5 October 2026

## Shared source of truth

`origin/main` contains the completed economy engine, current Godot client/presentation, experiments, evidence and exchange contracts. The client work through `3d934e5` and all visual/economy ancestors are integrated. `docs/exchange/INDEX.md` and each agent's own status board record the next work; both agents must fetch/pull before edits and announce shared-file changes.

The primary Mac checkout is `pondgame-v2`; the exchange/main worktree is `pondgame-v2-codex`. The asset worktree is `pondgame-v2-assets`. Old staged changes in the main worktree were stale copies that removed newer records and the safe-commit tool; they were backed up outside the repository and restored rather than committed. No unique work was discarded. Duplicate Claude report/capture files were byte-checked against their committed canonical copies and moved to the same local backup.

## Current playable state

- Python simulation with paid construction, workforce allocation, seasonal food, residence evolution, production and reference-governor diagnostics.
- Godot client with authored Verdant basin, dry crossing, carrier presentation, distinct starting facilities, resource HUD, Staff first / Normal priority and evolution/growth explanations.
- Additive sim_bridge contract v3 (protocol 1): input competitors identify same-store recipes and allow direct inspection; waiting recipes are labelled as competing for the next batch, and pausing does not refund reserved inputs.
- Default economy: provisional `candidate_playable_slice_v1`, fewer early job slots plus Carbonate renewal 0.2/min capped at 12. Baseline v0.2 remains unchanged.
- Recorded manual-opening replay: first Stable home 25:55 and food-solvent through the first Dry season. This is prior human-play evidence and scripted reproduction, not fresh novice acceptance.

## Known limits and next work

The reference governor reaches Symbiotic at 106:29. Food remains solvent through 240 minutes, but Repair Enzyme upkeep first goes unpaid at 136:29; unpaid time totals 21.5 minutes at 180 and 54.7 at 240. No Memory homes or Reef stages occur. The [upkeep diagnosis](milestone_a/UPKEEP_DIAGNOSIS_2026-10-05.md) identifies insufficient installed Enzyme capacity: one fully staffed digester makes 0.25/min against 0.50/min demand at first Symbiotic. Extra digesters ordered at 120:00 arrive late because Biomass-starved Ceramic production delays construction. The [early capacity comparison](milestone_a/EARLY_ENZYME_CAPACITY_2026-10-05.md) found a legal 80-minute construction/one-Culture-Bed-pause strategy with Symbiotic at 115:39 and zero unpaid upkeep or food emergencies through 240 minutes. Gel shortage rises to 4.8 residence-minutes, and by 240 production merely matches upkeep demand. The strategy is research only; Autoplay/default rules are unchanged. Final visual sign-off, novice onboarding and long-game balance remain open.

## Preservation

The original `pondlife/game` prototype is clean at `73df57b` and its complete Git history is archived in `archives/pondlife-prototype-2026-10-05/prototype.bundle`, with restore instructions. The v2 development branches remain recoverable in Git history.
