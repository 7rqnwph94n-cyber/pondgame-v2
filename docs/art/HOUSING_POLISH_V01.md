# House-only concept polish v01

Rich rejected the v02 house gallery and asked for a substantial visible improvement against the approved concept. This package replaces the thin dome study in the review fixture with four stages derived from the stronger approved v04 anatomy. It is an isolated art candidate; the live gameplay mapping is unchanged.

## Visible changes

- Enclosed, warped protective carapaces with real carved apertures and shell thickness, instead of open hemispheres.
- Recessed amber habitation organs and visible dark margins. The first native pass filled openings too completely; the final organs are smaller and deeper.
- Mineral shoulder tissue, tapered forked roots and perforated load-bearing webs. Roots were tapered again after the first close-up resembled tusks.
- Mixed cultivation cushions, blades, vascular stems, seed vesicles and substrate accretion anchored to the flanks; supply mouths remain clear.
- Distinct progression from a solitary sheltered chamber to a rooted pair, a planted court with tension canopy, and a layered memory habitat.
- Embedded 1024-pixel albedo, tangent normal and packed roughness maps. Softer shell relief, broad teal variation and restrained wax highlights separate from porous matte mineral. Transparency remains opaque for predictable distant rendering.

The generator reuses the established v04 UV, closed-shell, state-hierarchy and export authoring functions. It does not claim every component was newly sculpted. Accepted v04 and previous v02 files are preserved. A test of additional colour conversion made the native shells too dark; that conversion was removed and an exported palette range check added.

## Package

`assets/housing_polish_v01/` contains four near GLBs, four distance GLBs, companion visual anchors, source material tiles, manifest and editable Blender scene. Stage IDs are 01_seed_shelter, 02_rooted_dwelling, 04_symbiotic_court and 06_memory_manor. They are comparison stages, not a new gameplay progression contract.

Rebuild from the repository root:

```sh
Blender -b -t 4 --python-exit-code 1 --python tools/build_housing_polish_blender.py
Godot --headless --path client --script res://tests/housing_polish_review.gd -- verify
Godot --path client --script res://tests/housing_polish_review.gd -- comparison
Godot --path client --script res://tests/housing_polish_review.gd -- 3 --angle 155
```

Other modes: 0 through 3 for individual details, distance for simplified models, comparison --greyscale for silhouette/value review. Captures live in docs/art/renders/housing_polish_v01/. Comparison top row is previous v02; bottom row is polished housing. Both use the same light, camera, ground, antialiasing and ambient occlusion. The old row retains its own existing material adapter.

## Verification and limits

Native Godot/Metal captures cover all four close-ups, matched comparison, greyscale, distance meshes and a rear memory view. Import checks validate all eight models, finite normals/vertices, UV counts, embedded PBR maps, texture resolution, colour multiplier, source palette and distance silhouette bounds within five percent.

These are review meshes, not a population performance result. The largest house remains expensive even at the current distance setting; further LOD work, settlement-context inspection, colour-vision review, animation, domain footprint/docking agreement and Rich’s art judgement remain before default adoption. No industrial families were edited in this pass.
