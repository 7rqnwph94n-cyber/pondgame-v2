# Pondgame v2 client shell (Milestone B)

This is a Godot 4.3 view over the Python simulation. The design is in ADR 0001 (`docs/adr/0001-godot-client-over-python-sim-bridge.md`).

## Run

1. Install [Godot 4.3](https://godotengine.org/download/archive/4.3-stable/) and have Python 3.10 or newer available.
2. Open `client/project.godot` in Godot and press Play, or from the repository root run `godot --path client`.
3. The client starts the simulation itself, using `python3 -m economy.bridge`.
   - If your Python 3.10+ is not `python3`, set `python=` in `client/settings.cfg`, or set the `POND_PYTHON` environment variable.
   - `settings.cfg` loads the **provisional slice economy** `candidate_playable_slice_v1` (Rich, 2026-10-04): the playable-first package, plus fewer early job slots, plus slow surface-Carbonate renewal capped at 12. It is not a baseline rule. To switch economies, edit the `overlays=` line:
     - `["economy/data/experiments/candidate_playable_slice_v1.json", "economy/data/experiments/empty_settlement_start_v1.json"]` is the empty founding default;
     - `["economy/data/experiments/candidate_playable_slice_v1.json"]` reproduces the earlier populated slice benchmark;
     - `["economy/data/experiments/candidate_playable_v1.json"]` is the earlier package;
     - `[]` is the plain v0.2 rules.
   - **Limitation:** longer-game balance and the Memory Reef are unfinished. The earlier populated slice benchmark reaches Symbiotic around 106 minutes but does not reach the Reef within 120 minutes; those timings do not describe the new empty founding start.

## Mac desktop launcher

From the repository root, run `tools/macos/install_desktop_launcher.sh` once. Then double-click **Play Pondlife** on the Desktop. It opens the current checkout and starts the simulation automatically. The launcher finds Godot in Applications, your Applications or Downloads folder, or PATH, and finds Python 3 on PATH. Close the game before launching another session. Launch diagnostics are saved to `~/Library/Logs/Pondlife/launch.log`.

The opening slice is playable; longer-game balance and the Memory Reef remain unfinished. Use Space to pause while exploring, click buildings for their inspector, and use Build (B) to open construction. Autoplay is optional.

## Empty founding start

Play starts paused on an empty basin: no homes, facilities, sites, roads, crossing or visible carriers. Choose Homes on the left rail and build shelters, then press Space to start time. A 24-person founding crew waits off-map, pays for food from your provisions, supplies the first construction labour and moves into the homes you build.

Starting supplies: 30 Carbonate, 16 Prepared Silica, 24 Biomass, 8 Raw Silicate, 40 Staple food, 16 Growth Nutrient, 4 Repair Enzyme and 50 trade credits. Construction spends materials; credits are for trade. This covers three homes, food production and the basic services with reserves. First Nursery is now buildable. Optional Autoplay constructs the foundation legally.

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
| Autoplay | Lets the reference governor play alongside you. It is a balance aid, not game AI |

## Current presentation and limits

The client has authored basin terrain, manual building placement, subsequent carrier visuals and resource icons. The earlier populated benchmark also retains its authored river crossing and starting facilities. `presentation/map_layout.json`, `presentation/asset_map.json` and `EntityView` keep these presentation assets replaceable. Geography and carrier movement are visual; the domain still models district-level stores rather than spatial logistics.

The inspector explains labour priority, population stalls, evolution workforce changes and competing input users. Its Inspect buttons open a competitor so the player can choose Pause/Resume; pausing stops its outputs and does not refund held inputs.

The earlier populated benchmark (original slice overlay only) reaches Symbiotic at 106:29 under the reference governor. Extended runs first miss Repair Enzyme upkeep at 136:29, with 21.5 unpaid minutes by 180 and 54.7 by 240; no Reef stages complete. These are reproducible governor results, not guarantees for every player strategy. See `docs/milestone_a/SLICE_EXTENDED_HORIZON_2026-10-05.md`. Final art, novice-player acceptance and longer-game balance remain open.

The top strip uses resource icons and amounts, with names and explanations on hover. The inspector starts with a short status summary; its info button expands the detailed explanation. Carrier animation follows pause/speed, and selected carriers have a ground ring. Carriers remain presentation-only: individual cargo and worker orders are not simulated. Manual placements retain their location and rotation through construction and evolution during the running session. Geography still does not change district-level economy access or travel times; spatial logistics and save/load are not implemented.

Buildings take click priority over nearby carriers. Right-click evolution shows its workforce change before you act. Carrier animation is capped at high simulation speeds to keep selection and camera follow readable.

Placement: green means valid, red means blocked, with a short reason at the bottom. Footprints cover the current building mesh, with at least a 7m square and clearance between neighbours. Water margins, steep terrain, map bounds, rocks and selected natural features block placement. Camera navigation remains available while placing. Canceling a preview spends nothing; canceling a confirmed site uses the economy's normal salvage rules. Autoplay still uses automatic presentation slots. Road drawing, road snapping and flexible field plots are future work.
