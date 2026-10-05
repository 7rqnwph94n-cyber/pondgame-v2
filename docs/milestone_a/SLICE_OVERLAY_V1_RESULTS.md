# Provisional slice overlay v1

**Decision:** Rich chose "2" at 2026-10-04T1039Z (relayed by Codex): use L3 plus slow Carbonate renewal provisionally for the playable slice, on condition that a finite cap preserves the result.

**Overlay:** `economy/data/experiments/candidate_playable_slice_v1.json`.

**Re-test spec:** `economy/data/experiments/slice_overlay_v1_retest.json`, run with `python3 tools/run_lever_experiment.py economy/data/experiments/slice_overlay_v1_retest.json`.

## What the overlay is

`candidate_playable_v1`, plus:
- **L3**, fewer early job slots (from workforce scale v1);
- **surface Carbonate renewal** at `renewal_per_minute: 0.2`;
- **`reserve_cap: 12`**.

`tests/test_slice_overlay.py` checks that the overlay equals exactly this composition, so it cannot drift from its sources. The v0.2 baseline and every existing experiment are untouched, and the baseline has no `surface_carbonate` patch at all.

## The cap

A new, optional engine field, `patches.<id>.reserve_cap`, in `economy/engine/environment.py`:

- Renewal never raises a reserve above its cap. Patches without a cap behave exactly as before.
- Seasonal deposits are not capped.
- Validation rejects a cap below the starting reserve, and a cap on a patch with no finite reserve.
- Four engine tests cover it.

**Value: 12, equal to the patch's starting reserve.** The calcifying shallows re-precipitate only the crust that gleaning removed; they never grow beyond their natural standing crust. This is the least generous cap that keeps renewal meaningful.

## 120-minute re-test

| Run | First Stable | First Symbiotic | Homes S/St/Sy | Pop | Carbonate made / bought | Surface left | Enzyme paid / unpaid | Gel short | Fails |
|---|---|---|---|---|---|---|---|---|---|
| control: v0.2 | 24:06 | – | 8/3/0 | 97 | 9 / 30 | – | 0 / 0 | 0 | no Symbiotic, Reef |
| control: playable | 24:29 | – | 7/4/0 | 88 | 26 / 20 | 0 | 0 / 0 | 0 | no Symbiotic, Reef |
| reference: L3+C uncapped | 21:39 | 106:29 | 6/3/1 | 92 | 59 / 12 | 7.0 | 6 / 0 | 3.0 | Reef only |
| **slice overlay (cap 12)** | **21:39** | **106:29** | 6/3/1 | 92 | 59 / 12 | 6.3 | **6 / 0** | 3.0 | **Reef only** |

**The cap does not change the result.** The capped and uncapped runs are identical except for the reserve left at 120:00. Symbiotic holds, upkeep is paid, food is solvent (no Staple shortage, no food emergency) and there is no devolution.

The cap barely binds in normal play: gleaning keeps the reserve below 12 after the first few minutes. Its job is to stop accumulation when the gleaners are idle or paused.

## Human opening (no Autoplay) on the slice overlay

I replayed the recorded human opening plan with `python3 tools/replay_human_opening.py 3600 economy/data/experiments/candidate_playable_slice_v1.json <plan>`.

| Measure | Original plan (12 commands) | Plus 2 commands for the Biomass stall (14 commands) |
|---|---|---|
| First Stable home | 25:55 (was 30:29 on the earlier package) | 25:55 |
| Food at 60:00 (Dry) | 47.1 minutes | 23.5 minutes |
| Population at 60:00 | 28 | 36 |
| New shelter | stalled: "waiting for 1 biomass" | commissioned at 48:37 |

With the original plan, the new shelter stalls on Biomass because the culture bed turns all Biomass into Staple. With L3's smaller field crews, Biomass is tighter. The inspector shows the stall correctly ("waiting for 1 biomass"), and the player's fix is to pause the culture bed from 45:00 to 55:00 while Staple is plentiful. The plan with those two extra commands is `docs/milestone_b/human_opening_slice_2026-10-04.plan.json`.

**Gate 2 is met:** first Stable home, and food-solvent through the first Dry season. There is no softlock.

**New confusing interaction:** nothing tells the player which building is consuming the Biomass. This is a candidate for a future blocker parameter, "consumed by", and for HUD treatment.

## Verification

- Python: full suite passes, including `tests/test_slice_overlay.py` (8 tests: cap, composition, untouched baseline, client launch).
- Godot client tests: 247 of 247, with the client launching the slice overlay.
- Normal-renderer launch capture: the client starts on the slice overlay and plays to 10:36 under Autoplay with no bridge errors.

## Launch state

`client/settings.cfg` now loads `candidate_playable_slice_v1`. `client/README.md` explains how to switch to `candidate_playable_v1` or to the plain v0.2 rules (`overlays=[]`), and states the Reef limitation.

**The overlay is provisional. The Memory Reef is not reachable in 120 minutes under it.**
