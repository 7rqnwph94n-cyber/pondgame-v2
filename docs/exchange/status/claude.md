---
agent: claude
updated: 2026-10-02T18:32Z
state: waiting
current_task: Milestone B client shell delivered (Godot 4.3 over the Python bridge); waiting for Rich to push and play, and for Codex's import review
branch: claude/milestone-b-client-shell
head_commit: 70f9b7a
waiting_on: Rich, who must push three branches and try the client; Codex, for import review and adoption of sim_bridge v1
---

## Now

- The **client shell runs** (`70f9b7a` on `claude/milestone-b-client-shell`). It has:
  - Codex's blockouts at runtime;
  - pause and speed controls (1–32×);
  - a build list;
  - a stall inspector with actions;
  - Autoplay.
- Captures are in `docs/milestone_b/captures/`.
- Contract `sim_bridge` v1 is published (1832Z CONTRACT). ADR 0001 is in `docs/adr/`.

## Next

1. Fix whatever Rich hits on first run on his Mac (Python path, Godot 4.3 import).
2. Fold in Codex's import-review fixes through `client/presentation/asset_map.json` and `EntityView`.
3. Economy: once Rich chooses a population or job-scale fix (1809Z HANDOFF), the Reef can become reachable.
4. Then spatial placement and logistics: positions become domain state (ADR 0001, point 7).

## Blocked on / waiting for

- Rich: push `main`, `claude/milestone-a-honest-economy` and `claude/milestone-b-client-shell`, then open `client/project.godot` in Godot 4.3.
- Codex: import review at the shell camera; adopt `sim_bridge` v1; use `tools/exchange.py commit` (1804Z REQUEST).

## Assumptions I'm making about the other agent's work

- Codex's blockouts stay at `assets/blockout/silica_street/<asset>.obj` with `silica_street_blockout.mtl`, in metres, +Y up and ground pivot. The client reads them at runtime.
- Codex owns `client/presentation/asset_map.json` (presentation data only).

## Recently finished

- 70f9b7a: Milestone B client shell, `economy/bridge.py`, `economy/player_view.py`, ADR 0001, bridge and client tests.
- 16455ef: `candidate_playable_v1`, governor v3 and sweep v4.
- 04d8deb and 1448433: safe exchange commit, and repair of the stale-worktree reverts.

## Questions for Rich

- Not blocking: choose a population or job-scale fix for the Reef (1809Z HANDOFF).
