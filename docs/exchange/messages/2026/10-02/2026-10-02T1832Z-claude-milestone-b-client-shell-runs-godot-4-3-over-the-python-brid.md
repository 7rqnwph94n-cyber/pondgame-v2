---
id: 2026-10-02T1832Z-claude-milestone-b-client-shell-runs-godot-4-3-over-the-python-brid
from: claude
to: [rich, codex]
status: HANDOFF
subject: Milestone B client shell runs: Godot 4.3 over the Python bridge, Codex blockouts in
refs: [2026-10-02T1811Z-rich-milestone-b-architecture-python-sim-plus-godot-4-3-view]
closes: []
respond_by: 
tags: [milestone-b, playable]
branch: claude/milestone-b-client-shell
commit: 70f9b7a
---

## Context

Milestone B, following Rich's 17:42Z item 6 and the 18:11Z architecture decision. This is the smallest playable shell for the Silica Street early loop.

## Changed

Branch `claude/milestone-b-client-shell` (`70f9b7a`; it includes a merge of `codex/visual-preproduction` for the blockout kit):

- `client/`: a Godot 4.3 project. It has:
  - a camera rig;
  - a HUD with clock, season, colony line, speed buttons (pause, 1–32×) and Autoplay;
  - the store;
  - a build list;
  - an event log;
  - a stall inspector with actions;
  - one `EntityView` per domain entity.
- Codex's OBJ blockouts are read at runtime: shelters, store, Washery, clean-flow node, waste collector, farm, and the pit/patch asset. Anything unmapped uses a category placeholder.
- `economy/bridge.py` and `economy/player_view.py` (the governor's view, now shared).
- Defaults load the provisional `candidate_playable_v1` package.
- Captures: `docs/milestone_b/captures/shell_autoplay_31m56.png` and `shell_inspector_silicate_pit.png`, rendered with Godot 4.3 via OpenGL in my workspace.
- Tests:
  - Python: the full suite passes on the Mac (Python 3.10), bridge tests included.
  - Godot headless client tests: 23 of 23 pass in my workspace against the real bridge. They cover OBJ loading of all mapped blockouts, deterministic layout, the protocol round trip, one view per entity, shelters and store using Codex's assets, and the Reef inspector.

## Decision/evidence

The CLAUDE.md Milestone B list is met:
- the client loads the same definitions;
- it advances the headless simulation;
- it renders replaceable placeholders through the adapter;
- it has pause and speed;
- one inspector explains stalls.

Not yet: spatial placement (the domain has no coordinates), logistics movement, final UI styling and final art.

## Action requested

**Rich**, when you can:
1. Push `main`, `claude/milestone-a-honest-economy` and `claude/milestone-b-client-shell`.
2. Open `client/project.godot` in Godot 4.3 and press Play. If your Python 3.10+ is not `python3`, set it in `client/settings.cfg`.

**Codex:** import review. The captures are in the repository, and you can make your own with:
`godot --path client -- --capture=out.png --capture-seconds=40 --capture-speed=32 --autoplay [--select=<id>]`.
Please report assets that fail readability at the shell camera (75–90 m, pitch about −55°). `client/presentation/asset_map.json` is yours to edit.

## Compatibility/risk

- The Python sim is a child process, so players need Python 3.10+ until shipping is decided (ADR 0001).
- Under the headless dummy renderer, Godot prints harmless "Parameter m is null" mesh warnings.
- The provisional economy package will change.

## Reference

`docs/adr/0001-godot-client-over-python-sim-bridge.md`, `client/README.md`, the CONTRACT message for `sim_bridge` v1 sent at the same time, and `2026-10-02T1811Z-rich-milestone-b-architecture-python-sim-plus-godot-4-3-view`.
