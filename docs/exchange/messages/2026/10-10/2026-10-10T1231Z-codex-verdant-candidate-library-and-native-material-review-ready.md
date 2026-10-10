---
id: 2026-10-10T1231Z-codex-verdant-candidate-library-and-native-material-review-ready
from: codex
to: [claude, rich]
status: HANDOFF
subject: Verdant candidate library and native material review ready
refs: []
closes: []
respond_by: 
tags: []
branch: codex/visual-preproduction
commit: 9e7806b
---

## Context

Rich said "ok continue on the assets". Continued the existing 129-mesh candidate library on the art branch.

## Changed

Commit 9e7806b preserves the OBJ/MTL/anchor library and Blender source; adds candidate-only biological surface shader and material adapter, native review fixture and galleries, documentation at docs/art/VERDANT_LIBRARY_V02.md. Generator now writes a draft asset map without replacing live defaults.

## Decision/evidence

129 meshes, 306,764 triangles, largest individual mesh 9,776 triangles. All imports pass finite vertex/normal, companion file and shader material checks. Native Metal captures for homes, processors, carriers, goods, ecology and Reef compile the shader; homes/processors also have greyscale and identical-lighting plain baselines. Generator syntax passes; full generation was not rerun. Shell/mineral contrast remains readable in greyscale. Raw/refined goods still need distinct silhouettes.

## Action requested

Consume this handoff for awareness. Before eventual main adoption, independently review the candidate material adapter, shader and generator mapping isolation. No default asset promotion requested in this block.

## Compatibility/risk

No gameplay, bridge, default asset mapping or shared loader edits. Accepted v04 forms remain separate. No animation, collision footprint, colour-vision or live population performance claim. PR5 remains draft pending native manual QA; current user settlement preserved.

## Reference

Branch codex/visual-preproduction, commit 9e7806b. Manifest assets/verdant_v2/manifest.json; documentation and native captures under docs/art/.
