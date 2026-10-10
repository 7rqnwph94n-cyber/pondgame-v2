---
id: 2026-10-07T1747Z-codex-texture-only-architecture-milestone-native-surfaces-verified
from: codex
to: [claude, rich]
status: HANDOFF
subject: Texture-only architecture milestone; native surfaces verified
refs: [2026-10-07T1732Z-rich-architecture-forms-accepted-refine-textures-only]
closes: []
respond_by: 
tags: []
branch: codex/visual-preproduction
commit: f254cc6
---

## Context

Rich accepted the architecture form direction and requested texture refinement only. This block is complete for surface review, not default adoption.

## Changed

Art branch milestone f254cc6: all twelve surface families now have deterministic tileable 512px albedo, height-derived normals and packed roughness. Softer shell accretion, porous carbonate, fired ceramic, fine tissue fibres and restrained resin/silica highlights. Chamber UVs are continuously wrapped, removing the kiln's quadrant patches. Fast material-only Blender refresh tool added; same material source as full generator.

## Decision/evidence

189 Python tests, 316 original-client assertions and 2,826 architecture checks pass. Native near/distance roughness presence, green-channel use, variation, resolution and nonmetallic channels validated. Final native camera reel repeated: three close-ups, family sheets, eight yaws, three pitches/zooms, greyscale, construction/state fixtures. 100-instance art fixture: median 9.341ms, p95 16.744ms, 642 draws, 5,430,372 primitives; not a whole-game performance claim. Draws/primitives unchanged versus 330e202. Every manifest entry and anchor file is unchanged. Source positions/forms were not edited; regenerated LOD simplification vertices are not claimed byte-identical after UV changes.

## Action requested

Claude: retain domain/bridge ownership; no material-source edits needed. Do not default-enable the kit or overwrite shared client files. Existing requests for six-tier progression, local utility/transport and building-local stock bindings remain open. Rich judges the new surfaces next.

## Compatibility/risk

Review-only in isolated codex/visual-preproduction. No gameplay/default mapping/runtime integration changes this block. More texture memory/package size; repeat the authoritative mixed-settlement gate before release. Shared procedural tiles still fall short of bespoke per-building painting; no concept-parity claim. Small support pieces still use box UVs. Spatial checkout left untouched.

## Reference

f254cc6; docs/art/ARCHITECTURE_V04_READINESS.md; tools/refine_architecture_surfaces_blender.py; docs/art/renders/architecture_v04/godot_detail.png, godot_kiln_detail.png and godot_digester_detail.png. Rich's exact decision is recorded in the referenced exchange message.
