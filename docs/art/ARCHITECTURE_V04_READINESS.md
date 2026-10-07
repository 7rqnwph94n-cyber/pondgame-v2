# Verdant architecture v04 — refinement and readiness

This package replaces the v03 roof-only massing candidates for further review. It is **review-only**: technically integrated in the isolated art branch, not Rich-approved production art and not a six-tier economy implementation.

## Concept-led refinement log

| Review finding | Implemented correction |
|---|---|
| Open roofs did not describe inhabited anatomy | Closed protective chambers with recessed organs, real shell thickness and authored apertures |
| Repeated pale ribs were replacing the rejected shared foundation | Building-specific perforated carbonate support tissue, local root contacts and differentiated social spaces |
| Colours and smooth normals alone could not reproduce the concepts' material language | Embedded albedo/normal textures, material roughness, restrained resin seams and opaque membrane fallback in glTF |
| Angular aperture cuts and twisting collars failed close-up inspection | Boolean-cut openings and parallel-transported continuous collar geometry |
| Strong micro-normal noise looked like damaged shell | Lower-frequency/subtle albedo variation and reduced shell-normal strength |
| Sharp glossy highlights made native close-ups look like polished toys | Raised shell roughness and reduced clearcoat; resin and light organs also use softer highlights |
| Store read like a house and concealed its inventory at the rear | No household light apertures; three typed through-galleries with front/rear goods access |
| Washery lacked a clear transformation | Dirty inlet, porous support spine, screened middle chamber, soft transfer tissue, clean granular silica outlet and separate grit recess |
| Kiln resembled a residence with decorative fins | Opaque insulated ceramic mantle, internal warm aperture, delivered silica/fuel and cooled hollow ceramic output |
| Digester looked like whimsical lobes | Contained dark fermentation anatomy, pressure seams, sealed transfer tissue and distinct enzyme/fertiliser reservoirs |
| Membranes intersected inhabited chambers | Lifted tension supports and canopy clearances; grown beds gain visible cultivated tissue |
| Rich's six tiers were only names | Six authored visual stages with retained ancestor; tier 3/5 explicitly unbound pending domain design |
| Close-up detail risked settlement cost | Separate distance meshes at approximately 42% of near geometry, cached runtime scenes and zoom hysteresis |
| Idle/paused/blocked presentation could invent production | Work deformation changes only on explicit recipe progress; no whole-building pulse or wall-clock production animation |

## Package and reproduction

- Editable compressed source: `assets/architecture_v04/verdant_architecture_v04.blend`.
- Ten near and ten distance `.glb` files. Textures are embedded in each runtime file; the PNG source tiles remain alongside them.
- `manifest.json`: paths, geometry/surface counts, Y-up bounds, state groups and construction phases.
- Per-model `.anchors.json`: cargo, utilities, work, camera and label attachments. Anchors are visual and **not authoritative docking contracts**.
- Generator: `tools/build_architecture_refined_blender.py`. Blender command: `Blender -b -t 4 --python-exit-code 1 --python tools/build_architecture_refined_blender.py`. `-- --export-only` regenerates source/runtime data without renders; `-- --quick-review` produces faster family sheets.
- Native review: `Godot --path client -s res://tests/architecture_refined_review.gd -- housing` (also `industry`, `orbit`, `pitch`, `zoom`, `greyscale`, `states`, `construction`, `density`; headless `verify`).
- Review-only game opt-in: launch **this art checkout** with `POND_ARCHITECTURE_V04=1 Godot --path client`. This does not edit saved settings. Do not set this on the normal desktop launcher yet.

## Actual runtime behavior

`architecture_loader.gd` loads self-contained glTF files and caches scenes. `architecture_visual.gd` owns construction-layer visibility, dormant pore closures, explicitly supplied stock groups and local soft transfer deformation. Textures/materials are not modified globally when instances change state.

The opt-in plugs into EntityView and matching placement ghosts. Hierarchical bounds retain the established minimum seven-metre visual footprint. The default OBJ mapping is unchanged, and unrelated building families continue to use their existing assets. Typed cargo groups use actual resource IDs; `set_chamber_stocks` accepts known building-local counts and displays presence only (not exact visual unit counts). A silica-filled gallery does not imply that food or carbonate are present. Unknown stocks remain hidden through LOD/state changes.

`shelter`, `stable`, `symbiotic`, `memory` bind to visual stages 1, 2, 4, 6 respectively. Stages 3 and 5 remain art-only, explicitly listed in `client/presentation/architecture_v04.json`; no capacity, need or evolution cost has changed.

Known stock is deliberately not inferred from a district/global inventory. The live bridge currently does not expose every building-local typed chamber fill or per-frame recipe phase to this component; production shows those groups empty rather than inventing goods. Filled state review images are labelled fixtures, not a gameplay stock trace. Claude's domain/bridge ownership must resolve these bindings before normal release.

## Acceptance gates still open

Passing import tests or a density fixture is not a visual quality judgement. The concepts have substantially richer sculpted asymmetry, blended planted edges and authored material transitions than these procedurally composed candidates. This refinement is progress toward that benchmark, not a declaration of parity.

Before normal adoption:

1. Rich's visual review against the approved residence/Store/Washery concepts.
2. More sculpted carapace/terrace asymmetry and fewer generic perfect lobes if the present silhouettes are still judged too toy-like. Flora should integrate into structure, not merely resemble pot plants.
3. A mixed, populated, authoritative settlement review with selected/blocked/dormant neighbours and carriers docking to actual domain-approved ports.
4. Building-local typed inventory and recipe-progress bindings, with no duplicate/global-stock display.
5. Claude's six-tier progression and utility dependency proposal, accepted and tested separately from art.
6. Reconcile the isolated opt-in changes with the newer spatial client. Do not overwrite Rich's dirty active checkout or replace whole shared files blindly.

Refinement remains restricted to these ten assets. Other families remain on hold.

## Verification evidence, 7 October 2026

- Python regression: 188 tests pass, including self-contained GLB/texture/normal/UV/near-distance manifest validation.
- Existing default-client regression: 316 assertions pass. Review-only architecture checks: 564 pass, zero errors, including explicit recipe-phase preservation across distance-mesh swaps.
- Native Godot 4.7.1 Metal Forward+ on this Mac: eight yaw captures, pitches 20/38/65 degrees, three zooms, greyscale, close-up, construction and explicit-stock/state fixtures. Current native captures are `docs/art/renders/architecture_v04/godot_*.png`; Blender detail renders are earlier iteration evidence, not final camera acceptance.
- Final density fixture after Blender/Python work completed: 100 instances, 8.646ms median / 16.596ms p95, 598 draw calls, 4,868,384 rendered primitives. This is a timed art fixture, not whole-game frame-rate certification; see `density_report.json`. Repeat on the final authoritative settlement before setting a release budget.
- Close-up assessment: the tier ladder and industrial functions are clearer, but repeated round apertures, thin supports, geometric canopy triangles and discrete planter-like beds remain below the sculpted, integrated concept standard. No concept-parity claim or Rich approval is recorded.
