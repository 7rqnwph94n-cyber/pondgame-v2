# Empty Verdant map — acceptance review v0.1

**Capture:** [`../milestone_b/captures/verdant_empty_map_v06.png`](../milestone_b/captures/verdant_empty_map_v06.png)
**Verdict:** **FAIL — 4/10. Buildings remain excluded.**

## Passed

- Continuous environment fills the entire viewport; the playfield no longer reads as a floating board.
- Orthographic high-oblique camera produces a stable city-builder composition.
- Water occupies a lowered channel and the channel follows a smooth meander.
- Wet-bank colour transitions are continuous rather than raw polygon seams.
- Terrain, water and ecological dressing are reviewable without HUD, labels or simulation buildings through `--empty-map`.

## Failed

- Ground still lacks a convincing atlas of sediment, terrace, mineral and biological surface textures.
- Macro colour differences are too weak and washed out; chemistry cannot yet be read at a glance.
- Vegetation follows the channel but remains distributed too evenly and uses insufficient family variation.
- The right-hand rise lacks authored cliff faces, strata and embedded silica.
- No convincing flood debris, shoreline growth succession, shallow-water detail or water motion exists.
- Rocks are isolated scatter props rather than geological formations.
- There are not yet four readable resource families.

## Next required pass

1. Terrain texture atlas and splat/vertex blending.
2. Authored cliff-face and strata system integrated with elevation.
3. Three ecological scatter zones: wet bank, fertile shelf and sparse upland.
4. Embedded silica, methane and sulphur geology with depletion-ready silhouettes.
5. Water depth gradient, slow surface motion and shoreline detail.
6. Repeat the empty-map screenshot test. Required score remains 7/10.
