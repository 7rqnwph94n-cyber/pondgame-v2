# Verdant map diversity pass — v0.4

Capture: [v14 ecological diversity](../milestone_b/captures/verdant_empty_map_v14_ecological_diversity.png).

Status: awaiting Rich's visual review; the empty-map acceptance gate remains open. No new numeric score is assigned by this pass.

## Added

- Seven authored land materials, including a mauve carbon-clay construction terrace and a pale carbonate shelf.
- Two branching river filter groves and four chemical organism families: methane bladders, sulphur feeders, silica lichens and carbonate tubes.
- Secondary silica shelves, methane craters and sulphur crusts alongside the primary formations.
- A carbonate formation provides a fourth geological resource silhouette. This is presentation evidence, not a new gameplay extraction rule.
- Exposed rock, crust and microbial substrate now share textured world-space materials with their surrounding geography. Materials are cached and shared by instances.
- Wet bank variation is blended directly into the terrain. The raised shoreline overlay was removed after its triangles visibly cut across the terrain.

## Observed limits

The provinces are more distinct, and the props sit more comfortably in their materials. At the current camera scale, organism detail remains small and several broad mat shapes remain rounded and repetitive. Water still has too little visible structure in a still frame. The carbonate province is partly cropped at the default framing; it needs a separate inspection before four-resource readability is considered passed.

## Next deliverable

Finish one representative riverbank habitat at the default gameplay camera before scaling the treatment across the map. It should contain varied vegetation heights, convincing eroded and deposited edges, shallow water detail, and an embedded harvestable resource with a clear silhouette. Keep the established map topology and the quiet construction terrace. Use the finished habitat as the quality standard for the other chemical provinces.

## Validation

- 11 asset/reference tests passed.
- 23 Godot client tests passed.
- Normal Metal rendering produced the v14 screenshot without shader or script errors.
- Economy rules and state contracts are unchanged.
