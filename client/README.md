# Pondgame v2 client shell (Milestone B)

This is a Godot 4.3 view over the Python simulation. The design is in ADR 0001 (`docs/adr/0001-godot-client-over-python-sim-bridge.md`).

## Run

1. Install [Godot 4.3](https://godotengine.org/download/archive/4.3-stable/) and have Python 3.10 or newer available.
2. Open `client/project.godot` in Godot and press Play, or from the repository root run `godot --path client`.
3. The client starts the simulation itself, using `python3 -m economy.bridge`.
   - If your Python 3.10+ is not `python3`, set `python=` in `client/settings.cfg`, or set the `POND_PYTHON` environment variable.
   - `settings.cfg` loads the provisional playable-first package (`candidate_playable_v1`). Remove that overlay to play the plain v0.2 rules.

## Controls

| Input | Action |
|---|---|
| Space | Pause or resume |
| 1–6 | Speed: 1×, 2×, 4×, 8×, 16×, 32× simulated seconds per second |
| Left-click | Select a building, site or home. The inspector says why it is not progressing |
| Esc | Clear the selection |
| Right-drag | Rotate the camera |
| Middle-drag, WASD or arrows | Pan |
| Mouse wheel | Zoom |
| Build list (double-click) | Place a construction site. Its materials and labour are paid through the normal rules |
| Inspector buttons | Pause or resume a facility, cancel a site, evolve a home, or begin the Reef |
| "Why no Memory Reef yet?" | Explains the Reef's unlock blockers |
| Autoplay | Lets the reference governor play alongside you. It is a balance aid, not game AI |

## What this shell is not (yet)

- There is no spatial placement. The domain has districts but no coordinates, so the layout is a fixed presentation grid.
- There is no logistics movement, no final art and no styled UI.
- Codex's UI contract and assets replace the placeholders through `presentation/asset_map.json` and `EntityView`.
