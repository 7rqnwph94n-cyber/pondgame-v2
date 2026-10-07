# Architecture benchmark v03 — first massing gate

7 October 2026. Ten Blender candidates, not final production assets and not six playable housing tiers.

## Delivered

- Six housing forms: Seed Shelter, Rooted Dwelling, Mature Habitat, Symbiotic Court, Terraced Habitat, Memory Manor. An ancestral front chamber persists; later forms add shared court space, inhabited levels, shell terraces and a protected archive fan.
- General Store: broad covered goods galleries with two loading mouths. Washery: elevated raw-feed duct, descending separation basins and grit recess. Kiln: insulated conversion chamber, material/fuel throat, thermal-exchange gills and cooling comb. Digester: sealed unequal fermentation lobes, buried containment tissue and differentiated enzyme/fertiliser reservoirs.
- No shared circular foundation. Local substrate grips and building-specific containment replace the old segmented disc.
- Editable source `assets/architecture_v03/architecture_benchmark_v03.blend`, ten Y-up OBJ/MTL exports, per-model visual anchors and an inventory. Authored-normal support preserves smooth shells through the runtime loader.
- Independent Godot review script: `godot --path client -s res://tests/architecture_review.gd -- housing` or `industry`; headless `verify` checks all ten imports. Blender massing and material sheets are in `docs/art/renders/architecture_v03/`.

## Review findings and next fixed step

The massing pass removes the dominant shared plinth and makes the housing ladder substantially larger and more socially organised. These are useful prototypes, but **not yet Rich's requested finished architecture**. The current shell vocabulary is still heavily ribbed and must not become a replacement for the previous samey foundation.

1. Refine tiers 1–3 first: enclosed inhabited tissue, believable shell edges, protected brood/rest anatomy and less regularly spaced structural ribs. Utility attachments must be visibly attached, optional at founding, and legible from behind.
2. Refine tiers 4–6: mature shared spaces, supported terrace edges and a genuinely inhabited archive crown. Preserve the major silhouette differences; don't solve maturity merely with more ribs.
3. Refine the Store: replace generic bay contents with stored goods and retention structures. Washery: add screening/filter tissue and make feed, rejected grit and silica collection readable. Kiln: protect the heat core and distinguish raw input from cooled ceramic. Digester: add functional lobe seams, containment and differentiated discharge anatomy, not whimsical ornament.
4. Review rotation, neighbour occlusion and actual settlement scale before runtime binding. The gallery is a renderer test, not proof of readability in a populated city.
5. Add construction/working/blocked/dormant variants after baseline anatomy is accepted. Those states must follow domain evidence, not arbitrary animation.

The source models are roughly 2,400–14,400 triangles each at this stage; optimisation and distance treatment remain open. The six-stage domain ladder and clean-flow/waste infrastructure are proposals requested from Claude. Existing game rules are unchanged.

## Validation

- Export tests cover exactly ten candidates, finite geometry, triangulated faces, valid authored normal indices, material files, ports and housing height progression.
- All ten load through the Godot runtime OBJ reader with no import/normal errors.
- Normal Metal/Forward+ review captures are provided, not just Blender renders.
- Python regression: 186 tests pass. Godot client regression against the retained playable asset mapping: 316 assertions pass.

## Draft isolation

The earlier broad `verdant_v2` library is held as unaccepted draft work. Its proposed mapping is preserved as `assets/verdant_v2/draft_asset_map.json`; the active art-worktree presentation mapping has been restored to the previously committed assets. This benchmark deliberately does not silently adopt either draft library or substitute art for missing domain progression.
