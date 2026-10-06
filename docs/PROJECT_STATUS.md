# Pondgame v2 status — 6 October 2026

## Shared source of truth

`origin/main` contains the completed economy engine, current Godot client/presentation, experiments, evidence and exchange contracts. The client work through `3d934e5` and all visual/economy ancestors are integrated. `docs/exchange/INDEX.md` and each agent's own status board record the next work; both agents must fetch/pull before edits and announce shared-file changes.

The primary Mac checkout is `pondgame-v2`; the exchange/main worktree is `pondgame-v2-codex`. The asset worktree is `pondgame-v2-assets`. Old staged changes in the main worktree were stale copies that removed newer records and the safe-commit tool; they were backed up outside the repository and restored rather than committed. No unique work was discarded. Duplicate Claude report/capture files were byte-checked against their committed canonical copies and moved to the same local backup.

## Current playable state

- Python simulation with paid construction, workforce allocation, seasonal food, residence evolution, production and reference-governor diagnostics.
- Godot client with an empty Verdant basin at launch, player-built facilities and subsequent carrier presentation, resource HUD, Staff first / Normal priority and evolution/growth explanations.
- Additive sim_bridge contract v3 (protocol 1): input competitors identify same-store recipes and allow direct inspection; waiting recipes are labelled as competing for the next batch, and pausing does not refund reserved inputs.
- Default economy: provisional `candidate_playable_slice_v1` followed by `empty_settlement_start_v1`, fewer early job slots plus Carbonate renewal 0.2/min capped at 12. Baseline v0.2 remains unchanged.
- Earlier populated-slice manual-opening replay: first Stable home 25:55 and food-solvent through the first Dry season. This is prior human-play evidence and scripted reproduction, not fresh novice acceptance.

## Known limits and next work

In the earlier populated slice, the reference governor reaches Symbiotic at 106:29. Food remains solvent through 240 minutes, but Repair Enzyme upkeep first goes unpaid at 136:29; unpaid time totals 21.5 minutes at 180 and 54.7 at 240. No Memory homes or Reef stages occur. The [upkeep diagnosis](milestone_a/UPKEEP_DIAGNOSIS_2026-10-05.md) identifies insufficient installed Enzyme capacity: one fully staffed digester makes 0.25/min against 0.50/min demand at first Symbiotic. Extra digesters ordered at 120:00 arrive late because Biomass-starved Ceramic production delays construction. The [early capacity comparison](milestone_a/EARLY_ENZYME_CAPACITY_2026-10-05.md) found a legal 80-minute construction/one-Culture-Bed-pause strategy with Symbiotic at 115:39 and zero unpaid upkeep or food emergencies through 240 minutes. Gel shortage rises to 4.8 residence-minutes, and by 240 production merely matches upkeep demand. The strategy is research only; Autoplay/default rules are unchanged. Final visual sign-off, novice onboarding and long-game balance remain open.

## Preservation

The original `pondlife/game` prototype is clean at `73df57b` and its complete Git history is archived in `archives/pondlife-prototype-2026-10-05/prototype.bundle`, with restore instructions. The v2 development branches remain recoverable in Git history.

## Player controls review, 2026-10-05

Rich’s first click-through rejected the hidden build catalogue, wordy HUD, camera controls and unselectable carriers. The new client has a persistent left icon build rail, category flyouts with single-click construction and cost/workforce hover help, a compact icon resource strip and full-stock panel, a short inspector with expandable details, and building/site/home right-click actions. Zoom supports buttons, wheel, trackpad pinch/Shift-scroll and +/−; Home resets the camera. Trackpad scroll pans; Q/E, Alt-scroll or Alt-middle-drag rotate, freeing right-click for options. Carriers can be selected, highlighted, inspected and followed; they freeze with pause and manual panning cancels follow. Construction auto-selects its new site.

Native Mac QA verified the build rail, resource strip, hover help, zoom button, building context menu, carrier selection/Inspect/Follow and the construction inspector. Automated client tests cover zoom inputs and bounds, menu actions, single-click build requests, compact inspection and carrier picking/pause. Carriers remain visual representations with no simulated cargo or individual orders; construction still uses district placement. Economy, bridge contracts and provisional launch defaults are unchanged.

Claude independently reproduced the first controls branch’s 273 assertions and reviewed selection/action paths. His review identified toolbar focus consuming Space (fixed), carrier click priority and missing workforce warning on context evolution. All are corrected, with regression coverage. His trackpad and high-speed animation observations are also incorporated.

Final controls regression suite: 281 Godot assertions pass on the Mac.

## Empty founding start, 2026-10-06

Rich requested an empty map and a reasonable starting budget. The default now starts paused with no homes, facilities, sites, roads, bridge or carriers. Twenty-four founders wait off-map, provide 18 General workforce and consume actual Staple provisions until housed. Starter supplies and 50 trade credit support paid construction; no buildings are granted. The original populated overlay and v0.2 baseline remain separate. See [budget and opening evidence](milestone_a/EMPTY_START_2026-10-06.md).

The tested opening builds three homes and eight basic facilities within ten minutes, stays food-solvent through ninety minutes, and a separate opening reaches a Stable home within forty minutes. These are bounded opening checks, not long-game balance acceptance. All 180 Python tests and 288 Godot assertions pass. Native Mac launch confirms the empty paused basin and exact starting inventory.

## Manual placement, 2026-10-06

Rich rejected automatic slots after comparing with Manor Lords. Build icons now activate a translucent cursor preview, green/red footprint and short rejection reason. R / Shift-R rotates in 15-degree increments; left-click confirms paid construction; right-click / Escape cancels the preview without cost. Water, map bounds, steep terrain, rocks, buildings and sites block placement. Chosen positions and orientations remain through construction and evolution. Autoplay retains fallback slots; manual locations are presentation-owned for the running session, with no save/load or spatial resource/service/transport rules yet. Road drawing and flexible plots are subsequent work.

Validation: 180 Python tests and 313 Godot assertions pass. Native Mac QA verified green cursor preview, rotation, red water rejection without resource spending, right-click cancellation and paid shelter commissioning at the selected location.
