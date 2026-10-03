# Verdant Carbon Basin — vertical-slice map grammar v0.1

**Status:** implementation target for the first playable presentation map  
**Owner:** Codex visual track  
**Concept:** [`concepts/verdant_carbon_basin_map_v01.png`](concepts/verdant_carbon_basin_map_v01.png)

## Purpose

The Carbon Basin replaces the undifferentiated test plane. It proves that geography can explain the economy before procedural generation is attempted. The concept establishes composition and district relationships; it is not a literal asset or architecture blueprint.

## Design inheritance

- **Pharaoh:** one dominant environmental process; fertility follows water; extraction belongs to cliffs; settlement occupies constrained safe ground; routes and seasonal change make the map legible.
- **Age of Empires:** a viable sheltered start, an accessible expansion belt and valuable frontier resources beyond spatial pressure.
- **Anno:** locally incomplete fertility and mineral access create regional specialisation and increasingly long transport chains.

No layout, building or interface is to be copied. These are spatial design principles.

## Territory structure

| Region | Location and silhouette | Economic purpose | Pressure |
|---|---|---|---|
| Nutrient channel | Broad S-curve from north-west to south-east | Clean flow, filtering, transport and early food | Seasonal reach and crossings |
| Carbon floodplain | Quiet pale shelf wrapped around the central channel | Staple cultivation and biomass | Flood timing; contaminated downstream edge |
| Starting terrace | Raised stable oval at the inside bend | Housing, store and first services | Finite desirable land |
| Silicate escarpment | Tall cyan/cream ridge on the north-east boundary | Raw Silicate and later mineral chains | Long haul; extraction scars |
| Processing saddle | Stable ground between terrace and ridge | Washery, ceramic and composite industry | Waste and habitat-quality cost |
| Methane seep | Dark iridescent low basin in the south-west | Alternative energy/biology branch | Toxicity and difficult construction |
| Sulphur frontier | Warm vent field beyond the eastern pass | Catalysts and late chemistry | Hazard, distance and specialist morphology |
| Detritus delta | Branching depositional fingers in the south-east | Biomass recovery and fertile renewal | Shifting channels and accumulation |
| Memory shelf | Distant carbonate platform beyond the headwater | Great Work and territory landmark | Long-term material demand |

## Resource placement rules

1. Resources occur because of flow, geology or biology—never as evenly scattered pickups.
2. Every start receives nearby staple fertility, basic structural material and clean flow.
3. Improved deposits lie outside the settlement terrace and require a logistics decision.
4. Rare resources occupy memorable landmarks or chemical boundaries.
5. The richest reactions occur where two patches meet, but those boundaries carry risk.
6. Depletion changes the terrain silhouette: cut faces, dredge scars, drained membranes or exhausted vents.

## Settlement grammar

- Residences cluster around a calm service loop on the starting terrace.
- Cultivation follows the floodplain contour rather than a square field grid.
- Extractors touch the resource formation they work.
- Processing occupies the route between extraction and storage, downstream from housing.
- Storage and transfer organs sit at junctions.
- Civic structures terminate sightlines and form neighbourhood centres.
- Permanent floating labels are forbidden at settlement view. Selection, construction and alerts may reveal labels.

## Camera and readability

- Default camera: fixed high-oblique city-builder view, approximately 35° yaw and 55–60° pitch.
- The channel, ridge and district masses must read before individual buildings.
- Terrain remains lower contrast than interactables.
- Central buildable ground stays quiet; ecological detail clusters at boundaries.
- Territory view uses chemical overlays; normal play relies primarily on terrain and morphology.

## Implementation boundary

`client/presentation/asset_map.json` owns map dressing, district centres and presentation paths. These values do not alter simulation recipes, yields, travel times or legality. Gameplay geography becomes authoritative only through a future versioned contract owned by the simulation track.

## Concept corrections

The concept accidentally introduces a few crane-like silhouettes and pale conventional roofs. Production architecture must instead follow the existing living-shell, membrane, ceramic and glass language. Retain its geography, density, routes and district hierarchy—not those human-industrial details.

## Generation record

- Mode: built-in image generation.
- Use case: `stylized-concept`.
- Output: `concepts/verdant_carbon_basin_map_v01.png`.
- No source image was supplied.

## Research references

- *Pharaoh: A New Era Mission Editor Guide*: terrain, floodplain fertility, climate, rock and entry/exit composition — <https://cdn.akamai.steamstatic.com/steam/apps/1351080/manuals/Mission_Editor_Guide_EN.pdf?t=1696860281>
- *Age of Empires IV — Introduction to Generated Maps*: biome, resource and spawn-rule separation — <https://support.ageofempires.com/hc/en-us/articles/4869788243220-Introduction-to-Generated-Maps>
- *Age of Empires IV — Season Three resource pass*: safe, divided and widened contested distributions — <https://www.ageofempires.com/news/age_of_empires_iv_update_24916_season3/>
- *Anno Union — Treasures of the soil*: island fertility and mineral limits as production-chain pressure — <https://www.anno-union.com/devblog-treasures-of-the-soil/>
- *Anno Union — Your own trading empire*: specialisation and transport between regions — <https://www.anno-union.com/devblog-your-own-trading-empire/>
