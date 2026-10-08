# Basin layout v02 — geography candidate

Rich explicitly requested "no, change the map layout." This replaces the planned surface-only pass. Building forms stay frozen.

## Composition

The river now runs from outside the northwest map boundary, curves around a broad west-bank settlement plain, then exits beyond the southeast boundary. It no longer cuts through the centre of that plain. Resource geography, feature props, habitat groups and loose mineral scatter move together rather than leaving the old scenery on a new river.

| Region | Centre (x,z) | Intended settlement decision |
|---|---|---|
| Carbon-clay starting plain | -28,9 | Room for housing, stores and a deliberate road network |
| Carbonate shelf | -59,-38 | Northwest extraction frontier, separate from the starting plain |
| Methane depression | -60,43 | Southwest chemical habitat; not generic fertile land |
| Silica escarpment | roughly 48,-30 | Elevated northeast mineral district across the river |
| Sulphur province | 57,20 | Separate southeast industrial frontier |

The proposed crossing joins (-3,9) and (20,9). Both landings pass the dry-footprint check. The empty review does not build a bridge or imply that carriers can cross. Its route is an approach proposal, not an implemented pathfinding contract.

## Implementation boundary

`client/presentation/map_layout_v02.json` is a separate candidate. The ordinary client still loads the original layout. Optional terrain geography and ecology/scatter settings retain old defaults; no simulation, resource yield, placement permission, transport, camera or building-form changes.

Run the native review from this art checkout:

```sh
Godot --path client -s res://tests/architecture_basin_review.gd -- --layout-v2
```

The detached scene never starts the simulation bridge. It captures two empty-map views plus six architecture-context views in `docs/art/renders/map_layout_v02/`. Buildings are paused, unknown inventories hidden, and sites remain presentation-only.

## Acceptance and remaining gaps

The fixture passes 80 checks: sixteen full-footprint starting sites, the original-layout sample comparison, silica relief, dry crossing landings, model loading, dry/clear review sites and group framing. The sample improves from 15/16 to 16/16 dry sites; that narrow metric is not proof of overall gameplay quality. 189 Python tests and 316 ordinary-client assertions pass. The water shader clips the off-map river controls at the terrain boundary instead of drawing floating extensions.

This is a first geography candidate, not a finished map. River width is still comparatively uniform; banks and water surfaces remain weak. Vegetation is more intentionally located but the old plant meshes still look thin and repetitive. The escarpment needs authored ledges rather than a broad smooth rise. Crossing geometry, legal resource patches and network routing still need coordinated gameplay implementation. Empty-map visual sign-off remains open.
