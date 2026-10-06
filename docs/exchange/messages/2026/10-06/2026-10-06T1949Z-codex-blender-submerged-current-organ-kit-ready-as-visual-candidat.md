---
id: 2026-10-06T1949Z-codex-blender-submerged-current-organ-kit-ready-as-visual-candidat
from: codex
to: [claude]
status: HANDOFF
subject: Blender submerged current organ kit ready as visual candidates
refs: []
closes: []
respond_by: 
tags: [art, transport, underwater]
branch: codex/visual-preproduction
commit: a753324
---

## Context

Rich asked Codex to use Blender for more assets, based on the repository's current needs. The current design correction needs a submerged controlled-current neighbourhood with visible biological junctions, building intake ports and transfer points; these are gaps identified in the brief audit. I worked in the separate `codex/visual-preproduction` worktree, without touching Claude's current-mode domain branch or playable main.

## Changed

Commit `a753324` adds three candidate presentation assets: `node_current_junction_a`, `node_building_intake_a`, `node_transfer_fan_a`. The Blender 5.2 source is `assets/source/blender/submerged_current_organs_v01.blend`; a reproducible script regenerates OBJ/MTL exports in `assets/blockout/environment/` and a contact sheet at `docs/art/renders/submerged_current_organs_v01.png`. Each asset has a Y-up anchor file. No gameplay or bridge files changed.

## Decision/evidence

All three export under 3,000 triangles and use the runtime loader's existing OBJ/MTL format. Eight focused asset/environment tests pass; the full Python suite passes 183 tests. The source was inspected in Blender's isometric contact sheet. This is a camera-scale candidate, not final art or a current-network implementation. The mouth rims are legible but may read too engineered until viewed in the live submerged map.

## Action requested

Claude: no rule change needed. When your current-mode bridge/domain work is ready, coordinate with Codex on exact port data and geometry. Do not infer connectivity or capacity from these meshes or anchors. Codex will place and judge the kit in a native camera pass after integrating the current branch.

## Compatibility/risk

The OBJ loader is unchanged. Assets are not referenced by the playable map yet, so they cannot alter simulation or visuals until explicitly integrated. The transfer cups are visual payload sockets, not storage balances. Source `.blend` and rendered sheet are intentionally included for editability and review.

## Reference

`a753324` on `codex/visual-preproduction`; `docs/BRIEF_REFERENCE_AUDIT_2026-10-06.md`; Rich's 2026-10-06 request for Blender assets.
