# Map reference gap audit — Pharaoh / Age of Empires III–IV

**Status:** replacement-map acceptance standard
**Date:** 2026-10-03
**Owner:** Codex visual track
**Current comparison capture:** [`../milestone_b/captures/verdant_carbon_basin_assets_v02.png`](../milestone_b/captures/verdant_carbon_basin_assets_v02.png)

## Verdict

The current Carbon Basin is not visually comparable to even an empty or newly started map from the reference games. It communicates a schematic arrangement, but it does not yet render a continuous, believable environment. Further decorative OBJ placement on the existing plane is rejected as the primary solution.

## Reference set

### Pharaoh: A New Era

1. Early Nile map: <https://cdn.alza.cz/Foto/ImgGalery/Image/pharaoh-a-new-era-recenze-pocatky.jpg>
2. River map in the mission editor: <https://images.steamusercontent.com/ugc/2018225171764795203/CC0C3FE3650B85BCEEEFA8B703915AEA7CF714AB/>
3. Early settlement and immigrants: <https://storage.oyungezer.com.tr/ogz-public/images/haberler/2023/02/Pharaoh/p1.jpg>

### Age of Empires III: Definitive Edition

1. Exploration-age clearing: <https://forums.ageofempires.com/uploads/default/original/3X/8/0/8010db51ebed22bd8611eefad086253e6a095735.jpeg>
2. Early hunt and wood line: <https://cdn.ageofempires.com/aoe-forums/original/3X/f/c/fc25854005c0d453624821349584446b5a3eeaf8.jpeg>
3. Wide starting-terrain view: <https://forums.ageofempires.com/uploads/default/original/3X/9/9/990b688811e1932378adcc8d7f49440ed2e51adb.jpeg>

### Age of Empires IV

1. Resource-bearing terrain: <https://forums.ageofempires.com/uploads/default/original/3X/b/5/b559dbe4a6f345ea8ebd0e42d8250ca6b20f276e.jpeg>
2. Forest biome: <https://forums.ageofempires.com/uploads/default/optimized/3X/f/4/f4de002ce90cedfefd53dcb5807ec64ca4ddea7e_2_1024x576.jpeg>
3. Official coastal biome preview: <https://pbs.twimg.com/media/HFkblViW8AAqw1W.jpg>

Supporting design sources:

- Pharaoh Mission Editor terrain rules: <https://cdn.akamai.steamstatic.com/steam/apps/1351080/manuals/Mission_Editor_Guide_EN.pdf?t=1696860281>
- AoE III custom-map terrain skins: <https://support.ageofempires.com/hc/en-us/articles/8478444858388-Custom-Maps-Guide>
- AoE IV generated-map layout: <https://support.ageofempires.com/hc/en-us/articles/4869788243220-Introduction-to-Generated-Maps>

## Measured comparison

These are manual estimates from the screenshots at their published framing, rounded to avoid false precision. They are visual-production measurements, not claims about internal engine data.

| Measure | Pharaoh sample range | AoE III sample range | AoE IV sample range | Pondgame current | Gap |
|---|---:|---:|---:|---:|---:|
| Gameplay viewport occupied by continuous world | 98–100% | 98–100% | 98–100% | ~78%; visible void surrounds board | 20–22 percentage points |
| Visibly distinct terrain/ground materials | 5–7 | 6–9 | 7–11 | 4–5 mostly flat colours | 2–7 materials |
| Major landform layers readable in one frame | 3–5 | 4–7 | 5–8 | 2–3 | approximately half |
| Soft/organic terrain transitions | 90–100% of boundaries | 85–100% | 90–100% | ~10%; most are hard polygon edges | 75–90 percentage points |
| Screen occupied by clearly repeated identical modules | under 5% | under 8% | under 8% | ~20–25% around banks/cliffs | 3–5× too much |
| Environmental scale cues visible | 8–20+ | 20–50+ | 20–50+ | 6–10, many too small to read | 2–5× too few |
| Readable natural-resource families in frame | 3–6 | 4–7 | 4–8 | 2–3 ambiguous families | roughly half |
| Meaningful height/elevation bands | 2–4 | 3–6 | 4–7 | 1–2 | 2–5 bands missing |
| UI occlusion of world at idle | ~12–20% | ~18–25% | ~15–23% | ~30–35% | 10–20 percentage points too high |
| Empty-map presentation readiness | 8/10 | 8/10 | 9/10 | 2/10 | 6–7 points |

## Where the references succeed

### 1. The world continues beyond the camera

The reference maps fill the entire view. Cropping implies a larger territory. Pondgame exposes the rectangular play surface and the void around it, making the world read as a model table.

### 2. Terrain is a layered surface, not coloured zoning

Pharaoh combines desert, fertile bank, floodplain, water, rock, vegetation and small variations within each surface. AoE combines macro biome colour with grass, soil, paths, rocks, plants, decals, height and shadows. Pondgame currently uses large single-colour polygons to represent chemistry.

### 3. Boundaries carry the environmental story

Pharaoh's most informative area is the Nile edge: water, reeds, wet soil, fertile green and dry sand transition in sequence. AoE resource areas similarly blend trees, undergrowth, rocks and worn ground. Pondgame jumps directly from teal strip to flat bank without a convincing wet edge, deposition line or plant succession.

### 4. Repetition is distributed and disguised

The reference games repeat assets, but rotate, scale, cluster and interleave them with terrain variation. Pondgame places identical bank masses and cliff rows at equal intervals, making the construction method visible before the geography.

### 5. Empty space is authored

Reference buildable land contains low-frequency colour breakup, sparse stones, grass, tracks, wildlife and shadow. Pondgame's empty space is a uniform material. It reads as missing content rather than deliberate construction room.

### 6. Resources have contextual silhouettes

Forests are wood because they form wood lines; mines emerge from geology; Pharaoh farms occupy fertile floodplain. Pondgame's silica and chemical zones are isolated props on coloured patches, with weak integration between source and landform.

## Replacement-map acceptance gates

The next empty Verdant map must pass every gate before buildings are reintroduced.

| Gate | Pass condition |
|---|---|
| World coverage | At least 98% of the gameplay viewport contains rendered environment; no board edge or void at default camera and permitted pan limits |
| Terrain vocabulary | Minimum 7 readable surface families: deep channel, wet bank, fertile silt, stable terrace, dry/mineral ground, escarpment and one hazardous chemistry |
| Transition coverage | At least 90% of biome boundaries use a blended or physically layered transition; no raw polygon seams |
| Elevation | Minimum 4 readable height bands: channel bed, floodplain, build terrace and ridge/cliff |
| Repetition | No identical module may appear more than 3 times consecutively without rotation, scale, variant or occluding breakup |
| Environmental cues | Minimum 24 readable scale cues in a 1600×900 reference frame, clustered rather than evenly scattered |
| Resource readability | At least 4 resource families identifiable without labels or overlays in a five-second test |
| Quiet buildable land | 55–70% of the visible playable land remains construction-readable while still showing material texture |
| UI budget | Idle UI covers no more than 20% of the world view; build catalogue is collapsed by default |
| Screenshot test | The empty map must earn at least 7/10 against the reference rubric from Rich before buildings return |

## Fix plan

### Phase 0 — stop compounding the wrong system

- Preserve the current prototype as evidence but disable its terrain dressing in the default presentation.
- Stop producing standalone decorative OBJ modules until the base terrain renderer passes.
- Keep economy and presentation adapters intact.

### Phase 1 — replace the board

- Use a terrain mesh or chunked grid large enough that camera limits never reveal its boundary.
- Adopt a fixed orthographic/high-oblique gameplay camera and define its legal pan/zoom envelope first.
- Sculpt four elevation bands and a genuine lowered channel bed.
- Add skirts or surrounding terrain so the map never floats in void.

### Phase 2 — material and transition system

- Build a compact terrain material atlas for channel, wet sediment, fertile silt, terrace, mineral ridge, methane contamination and sulphur crust.
- Blend materials through vertex weights or splat masks.
- Add macro variation, small normal/roughness breakup and low-frequency tint variation; avoid a single flat colour per biome.
- Give the water its own surface, depth colour and shoreline intersection treatment.

### Phase 3 — environmental grammar

- Author wet-edge, flood-debris, terrace-edge, cliff-foot and hazard-boundary scatter rules.
- Use clustered MultiMesh variants with deterministic rotation, scale and density.
- Add at least three variants for every frequently repeated bank, rock and plant family.
- Make fertile vegetation density follow channel distance and elevation.

### Phase 4 — resources and navigation

- Embed silica into an exposed ridge face rather than standing crystals on a black box.
- Make methane visible through dead substrate, membrane films and sparse adapted life.
- Make sulphur emerge from vent geology with deposits down-current.
- Add wildlife/carrier-scale organisms to establish size before settlement construction.
- Validate that four resource families read with the HUD hidden.

### Phase 5 — UI and screenshot review

- Collapse build and event panels by default.
- Keep only the top resource strip and compact minimap visible at idle.
- Produce matched 1600×900 screenshots at default zoom: empty Pharaoh reference, empty AoE reference and empty Verdant map.
- Score the Verdant screenshot against every acceptance gate. Do not reintroduce buildings until it passes.

## Required next deliverable

One empty, playable Verdant Basin map with no buildings, labels or debug overlays. The screenshot must show finished terrain, embedded water, blended banks, elevation, resource-bearing geology, ecological scatter and no visible world boundary.
