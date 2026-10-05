# Pondgame v2 client shell (Milestone B)

This is a Godot 4.3 view over the Python simulation. The design is in ADR 0001 (`docs/adr/0001-godot-client-over-python-sim-bridge.md`).

## Run

1. Install [Godot 4.3](https://godotengine.org/download/archive/4.3-stable/) and have Python 3.10 or newer available.
2. Open `client/project.godot` in Godot and press Play, or from the repository root run `godot --path client`.
3. The client starts the simulation itself, using `python3 -m economy.bridge`.
   - If your Python 3.10+ is not `python3`, set `python=` in `client/settings.cfg`, or set the `POND_PYTHON` environment variable.
   - `settings.cfg` loads the **provisional slice economy** `candidate_playable_slice_v1` (Rich, 2026-10-04): the playable-first package, plus fewer early job slots, plus slow surface-Carbonate renewal capped at 12. It is not a baseline rule. To switch economies, edit the `overlays=` line:
     - `["economy/data/experiments/candidate_playable_slice_v1.json"]` is the slice default;
     - `["economy/data/experiments/candidate_playable_v1.json"]` is the earlier package;
     - `[]` is the plain v0.2 rules.
   - **Limitation:** the Memory Reef is not reachable within 120 minutes under any of these. The slice ends at the first Stable home and the first Dry season. A first Symbiotic home is possible at about 106 minutes with good play.

## Mac desktop launcher

From the repository root, run `tools/macos/install_desktop_launcher.sh` once. Then double-click **Play Pondlife** on the Desktop. It opens the current checkout and starts the simulation automatically. The launcher finds Godot in Applications, your Applications or Downloads folder, or PATH, and finds Python 3 on PATH. Close the game before launching another session. Launch diagnostics are saved to `~/Library/Logs/Pondlife/launch.log`.

The opening slice is playable; longer-game balance and the Memory Reef remain unfinished. Use Space to pause while exploring, click buildings for their inspector, and use Build (B) to open construction. Autoplay is optional.

## Controls

| Input | Action |
|---|---|
| Space | Pause or resume |
| 1–6 | Speed: 1×, 2×, 4×, 8×, 16×, 32× simulated seconds per second |
| Left-click | Select a building, site or home. The inspector says why it is not progressing |
| Esc | Clear the selection |
| Right-click | Context menu for a building, construction site or carrier; empty ground opens colony options |
| Q / E, Alt + trackpad scroll, or Alt + middle-drag | Rotate the camera |
| Two-finger trackpad scroll, middle-drag, WASD or arrows | Pan |
| Mouse wheel, trackpad pinch, Shift + trackpad scroll, + / −, sidebar buttons | Zoom |
| Home / reset icon | Restore the opening camera |
| Left build rail | Choose a category, then single-click a building to queue construction in its district. Hover for purpose, cost and workers |
| Resource crate icon | View all stocks; hover resource icons for names |
| Carrier click / right-click | Inspect the visual carrier or follow it with the camera |
| Inspector action icons | Pause or resume a facility, cancel a site, evolve a home, or begin the Reef |
| Inspector info icon | Expand full requirements, workforce consequences and input competition |
| Autoplay | Lets the reference governor play alongside you. It is a balance aid, not game AI |

## Current presentation and limits

The client has authored basin terrain, district placement, a dry river crossing, carrier visuals, distinct starting facilities and resource icons. `presentation/map_layout.json`, `presentation/asset_map.json` and `EntityView` keep these presentation assets replaceable. Geography and carrier movement are visual; the domain still models district-level stores rather than spatial logistics.

The inspector explains labour priority, population stalls, evolution workforce changes and competing input users. Its Inspect buttons open a competitor so the player can choose Pause/Resume; pausing stops its outputs and does not refund held inputs.

The unchanged provisional slice reaches Symbiotic at 106:29 under the reference governor. Extended runs first miss Repair Enzyme upkeep at 136:29, with 21.5 unpaid minutes by 180 and 54.7 by 240; no Reef stages complete. These are reproducible governor results, not guarantees for every player strategy. See `docs/milestone_a/SLICE_EXTENDED_HORIZON_2026-10-05.md`. Final art, novice-player acceptance and longer-game balance remain open.

The top strip uses resource icons and amounts, with names and explanations on hover. The inspector starts with a short status summary; its info button expands the detailed explanation. Carrier animation follows pause/speed, and selected carriers have a ground ring. Carriers remain presentation-only: individual cargo and worker orders are not simulated. Building placement is by district, not a spatial logistics rule.

Buildings take click priority over nearby carriers. Right-click evolution shows its workforce change before you act. Carrier animation is capped at high simulation speeds to keep selection and camera follow readable.
