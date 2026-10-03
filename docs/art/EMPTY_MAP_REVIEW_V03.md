# Empty Verdant map — acceptance review v0.3

**Capture:** [`../milestone_b/captures/verdant_empty_map_v12_authored_terrain.png`](../milestone_b/captures/verdant_empty_map_v12_authored_terrain.png)
**Verdict:** **FAIL — 6.7/10. Buildings remain excluded.**

## Material and ecology pass

- Five authored 1254 px terrain materials now blend continuously from geographic weights: fertile terrace, wet sediment, silica escarpment, methane basin and sulphur crust.
- The procedural colour wash is gone. Quiet buildable land retains low- and mid-frequency surface evidence without becoming prop-filled.
- The river has a separate irregular wet-bank layer, smoother spline sampling, shallow-edge colour and two flow frequencies.
- Five bank habitats now use broad microbial/filter mats with three variants plus taller silhouette accents. The ecology reads as clustered biomass rather than a line of evenly spaced props.
- Silica is a laminated shelf with exposed seams; methane is a low film and dome field; sulphur sits on a crust bed with shorter vent chimneys.
- Resource formations were reduced in scale so the geological province carries the resource story rather than a giant icon prop.

## Remaining shortfall

- The resource meshes are improved blockouts, not final authored geology. Their geometry and flat OBJ materials still lag behind the terrain below them.
- Bank mats establish mass, but the three variants repeat too visibly and their broad leaves need finer perimeter breakup.
- The shoreline band remains too coherent in several bends. It needs shallow shelves, retreat lines, debris and intermittent gaps rather than one continuous dark margin.
- Water flow reads at runtime but the still capture remains too uniform through its centre.
- A fourth harvestable resource family is not yet unmistakable without labels. Fertile biomass is present but does not yet advertise a distinct gatherable silhouette.

## Gate status

| Gate | Status |
|---|---|
| World coverage | Pass |
| Seven readable surface families | Pass |
| 90% blended/physically layered boundaries | Provisional pass |
| Four elevation bands | Provisional pass |
| Repetition limit | Provisional pass |
| 24 readable environmental cues | Pass |
| Four label-free resource families | Fail |
| 55–70% quiet buildable land | Pass |
| Empty-map score at least 7/10 | Fail — 6.7 |

## Next visual pass

1. Replace the three resource blockouts with final geological silhouettes and triplanar material breakup.
2. Add two finer bank-mat families, sparse chemistry-specific organisms and eroded edges to the broad mats.
3. Break the continuous shoreline into wet shelves, carbonate retreat lines, deposited debris and exposed mud pockets.
4. Give the fertile floodplain one unmistakable harvestable biomass formation, bringing label-free resource readability to four families.
5. Produce a matched v0.4 capture and rescore before any building is restored.
