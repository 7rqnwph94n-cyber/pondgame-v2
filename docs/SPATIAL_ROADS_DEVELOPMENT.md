# Connected current transport

Rich required “no, all buildings must connect”, then corrected the land-world presentation: “i need roads that dont look like roads. Current streams? we are in a liquid medium at this point, so the river is redundant unless it is a hazard”.

The original optional `spatial_roads_v1` remains available as a legacy comparison. The default now adds `current_lanes_v1`, replacing dirt paths with suspended biological current lanes and removing the blanket water/bank exclusion. There is no implemented river hazard, so the surface river presentation is removed. All buildings require one connected intake network; the first lane establishes the supplies anchor. Curves are baked into the actual transport path. Lane drawing is free for the bounded opening.

Shared geometry exports actual rock AABB bounds and minimum building envelopes. The domain converts exported minima to centres; parity tests check every obstacle. Current previews run non-mutating domain commands, show actual intake spurs and reject crossings through obstacles/buildings. Buildings cannot obstruct an existing intake branch. Pausing a provider removes its local coverage.

Six carriers transport construction goods, recipe inputs/outputs and home provisions with finite capacity and real network distances. Cargo and salvage stay in custody when disconnected. Suspended ribbons, cargo bundles, intake ports and growth follow simulation state, including pause. Local services use published reach; habitat light scales field output and silicate pits require the published exposure.

The [client guide](../client/README.md) describes controls and bounded opening evidence. The [charter](PLAYABLE_SLICE_CHARTER.md) records remaining acceptance. This is the first functional submerged neighbourhood; anchor-based logistics, central upkeep/trade/research/Great Work accounting, save/load, fluid hazards and final art remain limitations.
