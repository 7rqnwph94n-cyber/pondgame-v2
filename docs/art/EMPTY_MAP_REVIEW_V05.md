# Verdant riverbank habitat — v0.5

Reviewed captures: [empty map](../milestone_b/captures/verdant_empty_map_v17_bank_habitat.png), [habitat close-up](../milestone_b/captures/verdant_bank_habitat_detail_v04.png), [playable view](../milestone_b/captures/verdant_playable_v19_dry_placement.png).

Status: a stronger representative habitat and a cleaner playable composition; Rich's empty-map visual acceptance gate remains open. This is still blockout-quality art, not a Pharaoh-level finished landscape.

## Delivered

- Three new biomass-bower silhouettes with layered, upward growth and distinct heights; each has a reserved `HarvestAnchor` without changing the simulation economy.
- Stranded fibres and mineral grains at the bank, short depositional/erosion marks that follow the terrain, a subtly variable water width, and finer downstream flow lines.
- The habitat appears in both empty-map and playable scenes. Wet sediment is now textured alongside the other province materials.
- Locked camera-focus and zoom capture options make subsequent visual comparisons reproducible.
- The playable HUD starts compact. Build (`B`) and Log (`L`) reveal their panels when needed, leaving the map visible by default.
- Client-only settlement slots now test a whole dry building footprint, avoid other slots and follow ground elevation. Domain legality, yields and stable IDs are untouched.

## Honest remaining gaps

- At normal zoom, vegetation needs more mass, richer colour hierarchy and less radial symmetry. The water and bank are clearer, but still simplified.
- The carrier route is an old presentation polyline and cuts across the new water course. It needs an authored crossing or a route rework before the playable view can be considered convincing.
- Chemical provinces outside the riverbank do not yet share this habitat's density. Terrain-to-asset transitions, construction landmarks and distant silhouettes need a dedicated pass.
- `HarvestAnchor` is not an implemented resource interaction. Resource placement and map geography have not yet become gameplay constraints.

## Verification

- 11 environment/asset-map Python tests passed; 212 Godot client assertions passed.
- Normal Metal renderer produced the three reviewed screenshots without shader or script errors.
