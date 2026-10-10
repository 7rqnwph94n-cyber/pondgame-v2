# Pondgame v2 client shell (Milestone B)

This is a Godot 4.3 view over the Python simulation. The design is in ADR 0001 (`docs/adr/0001-godot-client-over-python-sim-bridge.md`).

## Run

1. Install [Godot 4.3](https://godotengine.org/download/archive/4.3-stable/) and have Python 3.10 or newer available.
2. Open `client/project.godot` in Godot and press Play, or from the repository root run `godot --path client`.
3. The client starts the simulation itself, using `python3 -m economy.bridge`.
   - If your Python 3.10+ is not `python3`, set `python=` in `client/settings.cfg`, or set the `POND_PYTHON` environment variable.
   - `settings.cfg` loads the **provisional slice economy** `candidate_playable_slice_v1` (Rich, 2026-10-04): the playable-first package, plus fewer early job slots, plus slow surface-Carbonate renewal capped at 12. It is not a baseline rule. To switch economies, edit the `overlays=` line:
     - `["economy/data/experiments/candidate_playable_slice_v1.json", "economy/data/experiments/empty_settlement_start_v1.json", "economy/data/experiments/spatial_roads_v1.json", "economy/data/experiments/current_lanes_v1.json"]` is the submerged founding default;
     - `["economy/data/experiments/candidate_playable_slice_v1.json"]` reproduces the earlier populated slice benchmark;
     - `["economy/data/experiments/candidate_playable_v1.json"]` is the earlier package;
     - `[]` is the plain v0.2 rules.
   - **Limitation:** longer-game balance and the Memory Reef are unfinished. The earlier populated slice benchmark reaches Symbiotic around 106 minutes but does not reach the Reef within 120 minutes; those timings do not describe the new empty founding start.

## Mac desktop launcher

From the repository root, run `tools/macos/install_desktop_launcher.sh` once. Then double-click **Play Pondlife** on the Desktop. It opens the current checkout and starts the simulation automatically. The launcher finds Godot in Applications, your Applications or Downloads folder, or PATH, and finds Python 3 on PATH. Close the game before launching another session. Launch diagnostics are saved to `~/Library/Logs/Pondlife/launch.log`.

The opening slice is playable; longer-game balance and the Memory Reef remain unfinished. Use Space to pause while exploring, click buildings for their inspector, and use Build (B) to open construction. Autoplay is disabled in the current spatial mode.

## Empty founding start

Play starts paused on an empty basin: no homes, facilities, sites, roads, crossing or visible carriers. Grow the first current lane with T: click its start, then successive ends; right-click finishes. This establishes the supplies anchor. Choose Homes on the left rail, rotate their intake toward the lane with R, and click when the ghost is green. Press Space to start time. A 24-person founding crew waits off-map, pays for food from your provisions, supplies the first construction labour and moves into the homes you build.

Starting supplies: 30 Carbonate, 16 Prepared Silica, 24 Biomass, 8 Raw Silicate, 40 Staple food, 16 Growth Nutrient, 4 Repair Enzyme and 50 trade credits. Construction spends materials; credits are for trade. This covers three homes, food production and the basic services with reserves. First Nursery is now buildable. Every building needs the same connected current network; no off-network exceptions.

The client applies `empty_settlement_start_v1.json` after the original slice overlay; the earlier populated benchmark remains reproducible with only the original overlay. See `docs/milestone_a/EMPTY_START_2026-10-06.md`.

## Controls

| Input | Action |
|---|---|
| Space | Pause or resume |
| 1–6 | Speed: 1×, 2×, 4×, 8×, 16×, 32× simulated seconds per second |
| Left-click | Select a building, site or home. The inspector says why it is not progressing |
| Esc | Clear the selection |
| Right-click | Cancel an active placement preview; otherwise context menu for a building, construction site or carrier; empty ground opens colony options |
| Q / E, Alt + trackpad scroll, or Alt + middle-drag | Rotate the camera |
| Two-finger trackpad scroll, middle-drag, WASD or arrows | Pan |
| Mouse wheel, trackpad pinch, Shift + trackpad scroll, + / −, sidebar buttons | Zoom |
| Home / reset icon | Restore the opening camera |
| Left build rail | Choose a category, then click a building to pick up its placement preview. Click valid ground to confirm; R / Shift-R rotates; right-click / Escape cancels. Hover for purpose, cost and workers |
| Resource crate icon | View all stocks; hover resource icons for names |
| Carrier click / right-click | Inspect the visual carrier or follow it with the camera |
| Inspector action icons | Pause or resume a facility, cancel a site, evolve a home, or begin the Reef |
| Inspector info icon | Expand full requirements, workforce consequences and input competition |
| T / current icon | Grow curving current lanes. Click start and successive ends; Shift makes a straight segment; right-click finishes. Right-click an existing lane to inspect/remove |
| H / habitat icon | Show local light and silica exposures; crop productivity depends on light, extraction needs an exposure |
| Autoplay | Disabled in spatial mode; available only in the older non-spatial benchmarks |

## Current presentation and limits

The default habitat is entirely submerged. Suspended current ribbons replace dirt paths; the surface river and dry-bank decorations are removed. Currents carry particles, join biological intake ports and freeze when paused. They are controlled logistics lanes, not a full fluid simulation. Existing terrain relief affects light and usable substrate; rock bounds and building footprints are shared with the rules engine.

Six simulated carriers move finite cargo along the actual network. Construction, production inputs/outputs and home provisions occupy local depots and spend travel time. Loaded meshes show resource bundles; inspectors show cargo and delivery state. Cut a lane and its buildings lose transport, labour and services; held goods remain in custody. Clean flow, waste and maintenance reach homes by network distance. Placement previews show actual intake branches, light suitability and local coverage before committing.

Construction grows from actual work progress. Evolved homes gain organic chambers within their reserved footprint. Placement stays through construction and evolution in the running session. Save/load, freeform fields, specialized warehouse logistics, fluid hazards, final art and novice-player acceptance remain unfinished. Upkeep, trade, research and Great Work accounting still use the supply anchor. Longer-game balance and the Memory Reef remain open.

The reproducible opening builds ten paid buildings, houses all 24 founders and reaches a Stable home at 11:38 with no food emergency or devolution through 90 minutes. The mineral extension adds a pit and washery, produces 19 Raw Silicate and 26 Prepared Silica through real transport, and remains food-solvent. These are ordinary-command fixtures, not human playthroughs or guarantees for arbitrary layouts:

```bash
python3 tools/verify_current_opening.py --check
python3 tools/verify_current_opening.py --check --plan economy/data/plans/current_mineral_opening_v1.json --evidence tests/fixtures/current_mineral_opening_evidence.json
```

Earlier non-spatial overlay benchmarks remain reproducible. Set `submerged=false` when deliberately reviewing the old terrestrial presentation.
