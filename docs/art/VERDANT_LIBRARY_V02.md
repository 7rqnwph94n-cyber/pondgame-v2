# Verdant v02 candidate library

This is an opt-in art library on `codex/visual-preproduction`, not the default playable asset mapping. It preserves the pre-existing candidate geometry and adds a Godot material review. Architecture v04 remains a separate approved-form study.

## Contents and provenance

129 meshes: 73 settlement and 56 environment assets, 306,764 triangles in total. The largest individual mesh has 9,776 triangles. The manifest records each asset’s source, bounds, count and candidate status. Companion OBJ/MTL/anchor files and the Blender authoring scene are included.

The library covers four home tiers, facility candidates, portable goods, seven carrier morphologies, construction and Reef stages, meadow variants and mineral depletion. Some facility ideas are speculative; presence in the library does not add a gameplay building or change a stable gameplay ID.

## Material pass

`assets/verdant_v2/materials/biological_surface.gdshader` uses local-position procedural variation: shell growth bands, porous carbonate/ceramic, restrained silica highlights, waxy tissue and resin. Tiny normal perturbations add surface relief without changing geometry. It uses no bitmap textures, emission, transparency or animation. This shader is separate from the Blender materials and is not baked into the source scene.

`client/scripts/verdant_surface_material.gd` applies the shader only in the review fixture. The default loader, asset mapping and gameplay presentation are unchanged. The generator now writes its proposed mapping to `assets/verdant_v2/draft_asset_map.json` rather than overwriting the live mapping.

## Reproduce and inspect

Run from the repository root using Godot 4.7.1:

```sh
godot --headless --path client --script res://tests/verdant_library_review.gd -- verify
godot --path client --script res://tests/verdant_library_review.gd -- residence
godot --path client --script res://tests/verdant_library_review.gd -- industry --greyscale
godot --path client --script res://tests/verdant_library_review.gd -- residence --plain
```

Other modes: `carriers`, `goods`, `ecology`, `reef`. Captures are written under `docs/art/renders/library_v02/`. Plain and surface captures use identical camera and lighting. Greyscale captures use Godot saturation adjustment.

The verifier checks every mesh import, finite vertices, valid normals, companion files and applied shader material. Native Metal captures also exercise shader compilation. All 129 imports passed; residence, industry, carriers, goods, ecology and Reef captures completed. Residence and industry greyscale views are included.

The Blender generator is `tools/build_verdant_library_blender.py`. It requires Blender and regenerates the authoring scene, exported candidate library and contact sheets; the shader is maintained separately. The generator was syntax-checked during this pass; the existing full library was imported and rendered rather than regenerated.

## Findings and remaining work

Shells and mineral ribs separate in greyscale, and home tiers gain visible silhouette complexity. Surface variation improves the flat diffuse baseline, but these remain prototype assets. Repeated dome forms need further review in a settlement context.

Several raw/refined goods still share a silhouette: carbonate/ceramic, fibre/woven fibre and resin/cured resin depend heavily on colour. They need distinct shapes before gameplay adoption. Meadow variants need submerged terrain context and density checks. No colour-vision simulation, in-game population GPU benchmark, collision/placement footprint validation, animation or live default integration is claimed by this gallery pass.
