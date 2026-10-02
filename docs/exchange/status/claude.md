---
agent: claude
updated: 2026-10-02T18:09Z
state: active
current_task: Milestone B start (Rich 17:42Z item 6) — ADR and smallest Godot client shell for the playable Silica Street slice
branch: claude/milestone-a-honest-economy
head_commit: 16455ef
waiting_on: Rich, who must push main and the branch; a population or job-scale decision is needed for the Reef but does not block
---

## Now

- Milestone A balance passes are finished.
  - Sweep v3: 0 of 243 pass.
  - Sweep v4 (narrow 17:42Z package): 0 of 9 pass.
  - Carbonate is solved. Labour supply against job count now binds (see 1809Z HANDOFF).
- Starting Milestone B:
  1. a Godot client ADR;
  2. a client shell that loads the same definitions;
  3. headless simulation stepping, placeholder entities through the presentation adapter, pause and speed controls, and one "why stalled" inspector.

## Next

1. ADR: `docs/adr/0001-godot-client.md`. How the Python domain and the Godot client share rules and data.
2. Client shell on `claude/milestone-b-client-shell`.
3. Silica Street early loop using Codex's ten OBJ blockouts as replaceable wrappers.

## Blocked on / waiting for

- Rich: push `main` and `claude/milestone-a-honest-economy`.
- Godot is not available in my Mac VM. I will try a headless Godot in my workspace for tests; Rich will run the editor locally.

## Assumptions I'm making about the other agent's work

- Codex treats `presentation_states.json` v1 as authoritative, with no `restoring` Builder state.
- Codex's ten Silica Street OBJ blockouts on `codex/visual-preproduction` (`4eac599`) are replaceable calibration geometry with no gameplay values.
- Codex commits exchange changes with `tools/exchange.py commit` (1804Z REQUEST).

## Recently finished

- 16455ef: candidate_playable_v1, governor v3, sweep v4 and its report.
- 0119aec: governor v2, sweep v3 and its report.
- 04d8deb and 1448433: safe exchange commit command, and repair of the stale-worktree reverts.

## Questions for Rich

- Not blocking: choose a population or job-scale fix so the Reef becomes reachable. Options are in the 1809Z HANDOFF.
