# Pondgame v2 — Verdant vertical-slice asset manifest v0.1

**Status values:** `briefed`, `candidate`, `in-production`, `review`, `accepted`, `retired`.

**Priority:** P0 benchmark, P1 slice-critical, P2 polish/variation.

No path below is a claim that the file exists. Canonical runtime paths are assigned only after acceptance.

The playable arrangement, provisional scale targets, scenario reel and interface bindings for the P0 set are defined in `SILICA_STREET_PRODUCTION_PACKAGE.md`.

## Manifest contract

Each production asset records:

- stable visual ID and linked gameplay definition ID;
- category and priority;
- source and exported paths;
- reuse origin where relevant;
- scale, bounds and pivot;
- material slots and texture sizes;
- animation/state list;
- named anchors;
- triangle/draw-call targets;
- provenance;
- review status and known limitations.

Art metadata must not contain gameplay costs, capacity, collision or recipe balance.

## P0 visual benchmark

Directional concept: `docs/art/concepts/verdant_benchmark_concept_v01.png`. Its production interpretation and required corrections are recorded in `docs/art/concepts/VERDANT_BENCHMARK_CONCEPT_V01_REVIEW.md`.

| Visual ID | Gameplay link | Asset | Disposition | Required states |
|---|---|---|---|---|
| `env_basin_benchmark` | benchmark map corner | Silt clearing, ledge, root and patch boundaries | Kitbash legacy environment | Bloom, Dry |
| `patch_silicate_a` | `raw_silicate` source | Glassy outcrop with removable facets | Kitbash mineral geometry | rich, worked, depleted |
| `farm_photosynthetic_a` | `photosynthetic_field` | Ordered membrane field | Kitbash algae | growing, active, dry-stressed |
| `unit_general_carrier_a` | General workforce | Verdant carrier organism | Adapt Gatherer | idle, move, carry, deliver, stressed |
| `res_shelter_cluster_a` | `shelter` | First-tier residence | Adapt Biofilm Shelter | construction 0–1, occupied, strained, dormant |
| `proc_mineral_washery_a` | `mineral_washery` | Flow-through silica washer | New/kitbash Silt Filter | idle, awaiting input, active, blocked output |
| `store_general_a` | General Store | Open typed storage chambers | Adapt Storage Pit | empty, partial, full, loading |
| `payload_raw_silicate_a` | `raw_silicate` | Sharp glassy fragments | Kitbash | carried/stored |
| `payload_prepared_silica_a` | `prepared_silica` | Sorted pale granules/ingots | Adapt legacy Silica | carried/stored/output |

## Terrain and environment — P1

| Visual ID | Asset | Variants/states | Reuse |
|---|---|---|---|
| `terrain_silt` | Blendable basin silt | clean, fertile, contaminated | Adapt |
| `terrain_sand` | Pale shallow substrate | wet/dry | Reuse |
| `terrain_rock` | Exposed shelf material | wet/dry | Reuse |
| `terrain_gravel` | Transition material | clean/disturbed | Reuse |
| `ledge_set_a` | Modular shelves | 8 modules | Reuse |
| `boulder_set_a` | Terrain anchors | 6 forms | Reuse |
| `root_set_a` | Root landmarks | 4 forms | Reuse |
| `plant_background_set_a` | Quiet ecological framing | 12 forms | Adapt |
| `detail_ground_set_a` | Ripples, grit, stains, scars | 6+ motifs | Adapt |
| `water_atmosphere_verdant` | Fog, caustics, shafts, motes | four seasons | Adapt |

## Chemical patches — P1

| Visual ID | Gameplay link | Required presentation |
|---|---|---|
| `patch_phosphate_a` | Phosphate Sediment | layered bed, dredge scar, High Water cover, fresh deposition |
| `patch_nutrient_channel_a` | Suspended Nutrient | directional motes, seasonal density, filter placement guides |
| `patch_silicate_a` | Raw Silicate | rich/worked/depleted facets |
| `patch_carbonate_a` | Carbonate | porous reef, cut face and contested landmark presence |
| `patch_anoxic_a` | Anoxic Organics | dark boundary, gas/film cue, Dry expansion and hazard state |
| `patch_pigment_a` | Raw Pigment | subtle culture film, healthy/cultivated/bleached states |
| `landmark_clean_spring_a` | Clean Flow | rising clear current and contracted Dry radius cue |

## Farms — P1

| Visual ID | Gameplay link | Required presentation |
|---|---|---|
| `farm_photosynthetic_a` | Photosynthetic Field | 4–8 modular beds; fertility and Dry stress |
| `farm_fibre_a` | Fibre Garden | long tensioned fronds; harvested and recovering |
| `farm_resin_a` | Resin Grove | secretion cups; raw resin fill level |
| `farm_pigment_a` | Pigment Bed | shallow microbial panels; clean-flow sensitivity |

## Extraction and processing — P1

| Visual ID | Gameplay link | Process read |
|---|---|---|
| `extract_sediment_dredge_a` | Sediment Dredge | paddles lift layered sediment into payload cups |
| `extract_filter_crown_a` | Filter Crown | fan spans visible current and concentrates particles |
| `extract_silicate_pit_a` | Silicate Pit | cutting organism/fixture removes hard facets |
| `extract_carbonate_cutter_a` | Carbonate Cutter | broad brace and mineral jaw contact |
| `extract_anoxic_pump_a` | Anoxic Pump | sealed intake, dark feed and detox exhaust |
| `proc_nutrient_washer_a` | Nutrient Washer | dirty sediment to pale nutrient and sludge |
| `proc_channel_separator_a` | Channel Separator | flow concentration into nutrient bundles |
| `proc_culture_bed_a` | Culture Bed | biomass inoculation to staple culture |
| `proc_nutrient_kitchen_a` | Nutrient Kitchen | two inputs blended into four gel vessels |
| `proc_mineral_washery_a` | Mineral Washery | facets washed/sorted to silica output |
| `proc_ceramic_kiln_a` | Ceramic Kiln | fuel sac, insulated heat core and cooling shelf |
| `proc_retting_pool_a` | Retting Pool | raw fronds separate into aligned fibres |
| `proc_resin_curing_a` | Resin Curing Organ | viscous amber fill becomes glossy solid |
| `proc_composite_a` | Composite Workshop | fibre/resin/silica visibly interlace |
| `proc_waste_digester_a` | Waste Digester | dark waste to enzyme and fertiliser outputs |
| `proc_enzyme_culture_a` | Emergency Enzyme Culture | staple/fuel conversion with high metabolic pulse |
| `proc_artisan_a` | Artisan Organ | resin and pigment form ornament |

All processors require `idle`, `awaiting_input`, `active`, `output_blocked`, `unstaffed`, `strained/disrepair` presentation through shared material/state systems where possible.

## Logistics — P1

| Visual ID | Gameplay link | Requirements |
|---|---|---|
| `unit_general_carrier_a` | General carrier | payload anchor and capacity read |
| `unit_vascular_carrier_a` | Vascular morphology | larger vessels and transport ribs |
| `store_general_a` | General Store | typed visible stock |
| `store_living_a` | Living-Goods Store | protected moist chambers |
| `store_hazard_a` | Hazard Store | sealed dark containment |
| `node_distribution_a` | Distribution Node | loading cups and local-service pulse |
| `node_transfer_a` | Transfer Node | directional handoff |
| `route_flow_channel_a` | Flow Channel | modular low ribs and current ribbon |
| `trade_landing_a` | Trade Landing | larger loading fan and route marker |

## Residences and services — P1

| Visual ID | Gameplay link | Growth/state requirements |
|---|---|---|
| `res_shelter_cluster_a` | Shelter Cluster | foundation; occupied/strained/dormant |
| `res_stable_habitat_a` | Stable Habitat | additive chamber, service connections |
| `res_symbiotic_a` | Symbiotic Neighbourhood | gardens, shared chambers, artisan cues |
| `res_memory_enclave_a` | Memory Enclave | encoded crown and cultural pigment |
| `service_nursery_a` | First Nursery | brood, adaptation work and paused state |
| `service_maintenance_a` | Maintenance Organ | repair payload and service dispatch |
| `service_clean_flow_a` | Clean-Flow Node | flow connection and contamination state |
| `service_detox_a` | Detox Clinic | intake, detox sacs and recovery pulse |
| `service_memory_circle_a` | Memory Circle | radial gathering and encoded surface |

## Morphologies — P1

Morphology may be implemented as compatible body variants or validated attachments. Each must alter silhouette.

| Visual ID | Gameplay link | Required cue |
|---|---|---|
| `morph_burrowing_a` | Burrowing Limb | broad paddles and grounded posture |
| `morph_filter_a` | Filter Crown | radial porous fan |
| `morph_mineral_jaw_a` | Mineral Jaw | reinforced silica-edged cutter |
| `morph_detox_a` | Detox Sac | paired dark sacs and valves |
| `morph_vascular_a` | Vascular Carrier | enlarged payload system |
| `morph_memory_a` | Memory Ganglion | luminous protected neural crown |

## Memory Reef — P1 hero asset

| Stage | Visual requirement |
|---|---|
| Site | cleared circular bed, delivery zones and shared Coral Scaffold language |
| Foundation | broad carbonate rings and embedded ceramic ribs |
| Living Lattice | rising fibre/resin lattice with active construction movement |
| Archive Crown | silica/pigment encoded surfaces and calm civilisational pulse |

Required anchors: bulk delivery, specialist delivery, physical work, coordinator work, label, camera focus and FX.

## UI assets — P1/P2

- 22 goods icons matching data IDs;
- 4 workforce-class icons;
- 6 morphology icons;
- 6 service icons;
- 4 season icons;
- need/strain/dormancy/disrepair status icons;
- production-state family symbols;
- construction and Great Work stage symbols;
- portraits rendered only from accepted organism/building assets.

## Shared anchors and state naming

Preferred anchors:

```text
LabelAnchor
FXAnchor
InputAnchor_<resource-or-slot>
OutputAnchor_<resource-or-slot>
PayloadAnchor
WorkerAnchor_<n>
ServiceAnchor
CameraAnchor
```

Preferred actions/states:

```text
idle
move
carry_move
deliver
work
build
strained
dormant
spawn
despawn
```

Adapter semantics remain authoritative in `CLAUDE.md`; this manifest does not redefine gameplay.

## Production batches

1. **Benchmark:** the nine P0 assets in one review scene.
2. **Environment and patches:** terrain library, seasons and seven chemical landmarks.
3. **Opening economy:** carrier, first residence, store, field, culture, sediment and nutrient chain.
4. **Materials economy:** silica, carbonate, fibre, resin and processors.
5. **Population/services:** residence ladder, nursery and civic services.
6. **Morphology:** six visible caste changes.
7. **Trade and Great Work:** Trade Landing, cargo presentation and Memory Reef.
8. **UI/polish:** accepted-model portraits, icons, LODs and performance pass.

## Generated blockout source

The first P0 blockout batch is generated by `tools/generate_blockout_assets.py` into `assets/blockout/silica_street/`. OBJ is the temporary interchange format because it imports without a modelling dependency; adjacent anchor JSON preserves engine-facing contact points. These files remain `candidate` until an in-engine camera/import review, after which accepted revisions should be converted to GLB presentation assets.
