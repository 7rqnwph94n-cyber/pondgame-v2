---
id: 2026-10-04T1048Z-claude-slice-overlay-live-l3-carbonate-renewal-capped-at-12-retest
from: claude
to: [codex]
status: HANDOFF
subject: Slice overlay live: L3 + Carbonate renewal capped at 12; retest unchanged (Symbiotic 106:29, upkeep paid); client launches it
refs: [2026-10-04T1039Z-rich-use-l3-and-carbonate-renewal-provisionally-for-the-playable]
closes: []
respond_by: 
tags: [economy, client]
branch: claude/milestone-b-client-shell
commit: 141db45
---

## Context

The integration brief that came with Rich's 1039Z "2" (relayed by Codex at `cf9ed32`), as announced at `9848e7b`.

## Changed

`141db45` on `claude/milestone-b-client-shell`, based on your `d162922`:

- **Engine:** a new optional field, `patches.<id>.reserve_cap` (`economy/engine/environment.py`). Renewal never raises a reserve above its cap; patches without a cap are unchanged and seasonal deposits are not capped. `definitions.py` rejects a cap below the starting reserve, or a cap on a patch with no finite reserve.
- **Overlay:** `economy/data/experiments/candidate_playable_slice_v1.json` = `candidate_playable_v1` + L3 + `surface_carbonate.renewal_per_minute: 0.2` + **`reserve_cap: 12`**. A test guards against drift from its sources. The v0.2 baseline and all existing experiments are untouched.
- **Client launch:**
  - `client/settings.cfg` now loads `candidate_playable_slice_v1` (overlay line and comment only).
  - `client/README.md` explains how to switch to `candidate_playable_v1` or plain v0.2 (`overlays=[]`), and states the Reef limitation.
  - No HUD, map or presentation files changed.
- **Report:** `docs/milestone_a/SLICE_OVERLAY_V1_RESULTS.md`.
- **Retest spec:** `slice_overlay_v1_retest.json`.
- **Replay tool:** now takes an overlay and a plan.

## Decision/evidence

**Exact cap: 12, equal to the patch's starting reserve.** The calcifying shallows re-precipitate only the crust that gleaning removed; they never exceed their natural standing crust. This is the least generous cap that keeps renewal meaningful.

**120-minute retest:** the capped overlay is identical to uncapped L3+C. Results for the slice overlay:

| Measure | Result |
|---|---|
| First Stable | 21:39 |
| First Symbiotic | 106:29, held |
| Homes at 120:00 (Shelter/Stable/Symbiotic) | 6/3/1 |
| Population | 92 |
| Carbonate | 59 made, 12 bought |
| Surface Carbonate left | 6.3 (7.0 uncapped) |
| Repair Enzyme upkeep | 6 paid, 0 minutes unpaid |
| Food | solvent (no Staple shortage, no food emergency) |
| Gel shortage | 3.0 minutes |
| Devolutions | none |
| Fails | only the Reef |

The controls reproduce: v0.2 Stable 24:06, playable package 24:29, neither reaching Symbiotic. **The cap does not break the result.** It barely binds in play; its job is to stop accumulation while gleaners are idle.

**Human opening without Autoplay** on the overlay:
- First Stable at 25:55, versus 30:29 on the earlier package.
- With 14 commands: food 23.5 minutes at 60:00 in Dry, population 36, no softlock. Gate 2 is met.
- **New confusing interaction (45:00, inspector on the shelter site `home_p1`):** "waiting for 1 biomass". With L3's smaller field crews, the culture bed converts all Biomass into Staple; the player fixes it by pausing the bed from 45:00 to 55:00. Nothing tells the player which building is eating the Biomass. A candidate fix is a "consumed by" parameter on `waiting_input` (a bridge change I can propose) plus HUD treatment.

**Tests:**
- Full Python suite green on the Mac (Python 3.10), including 8 new tests in `tests/test_slice_overlay.py`: cap, composition, untouched baseline, client launch.
- Godot client tests: 247 of 247 in my workspace on `d162922` plus these changes.
- A normal-renderer launch capture starts on the slice overlay and plays with no bridge errors.

## Action requested

**Codex:** review. Optionally tell Rich the slice now launches on the provisional overlay. Then choose whether you want the "consumed by" blocker parameter (a `sim_bridge` v3 additive change) for the Biomass confusion.

## Compatibility/risk

This is a provisional slice overlay, not a baseline rule. **The Memory Reef is not reachable in 120 minutes under it.** Post-Symbiotic upkeep solvency is still observed for only about 14 minutes. `reserve_cap` is an additive, optional engine field.

## Reference

`141db45`; 1039Z (Rich via Codex); `9848e7b` (announcement); `b553643`; `docs/milestone_a/SLICE_OVERLAY_V1_RESULTS.md`.
