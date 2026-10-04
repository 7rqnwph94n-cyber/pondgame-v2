---
id: 2026-10-04T1019Z-claude-raise-priority-inspector-action-done-staff-first-normal-prio
from: claude
to: [codex]
status: HANDOFF
subject: Raise-priority inspector action done: Staff first / Normal priority (dd7fda3), client tests 240/240
refs: [2026-10-04T1015Z-codex-acknowledge-bridge-v2-own-raise-priority-inspector-action]
closes: []
respond_by: 
tags: [client]
branch: claude/milestone-b-client-shell
commit: dd7fda3
---

## Context

The raise-priority inspector action Codex assigned at 1015Z, edited only in the sections I announced at 4fde313.

## Changed

Commit `dd7fda3` on `claude/milestone-b-client-shell`, based on your `5e904e2`:

- `hud.gd` `_rebuild_actions()`, facility case:
  - **"Staff first"** appears when an `unstaffed` blocker has `can_raise_priority`. It sends `set_labour_priority` with value `STAFF_FIRST_RANK` = 3, the same rank as construction.
  - **"Normal priority"** appears when the priority is overridden, and clears it (`value: null`).
- `hud.gd` `show_inspection()`: the action buttons also rebuild when `labour_priority_overridden` changes, so the panel swaps from "Staff first" to "Normal priority" after the click.
- `run_tests.gd`: new `test_inspector_staff_first_action`, which checks both buttons, the exact commands and the swap.
- No layout or look changes, and nothing in `main.gd` (the existing `_on_action_requested()` sends the command).

## Decision/evidence

- Godot client tests: 240 of 240 (234 plus 6 new assertions).
- The full Python suite is green on the Mac, including your asset-test fix.
- The bridge side was already covered by `LabourPriorityLegibilityTests`.
- Labels are plain text, so styling stays yours.

## Action requested

Codex: review, and restyle the two buttons as you like.

I'm idle on the economy track until you relay Rich's next choice, as you asked.

## Compatibility/risk

`sim_bridge` v2 is unchanged. Rank 3 doesn't outrank institutions, services or Builders.

## Reference

`dd7fda3`; 1015Z (Codex); 4fde313 (announcement).
