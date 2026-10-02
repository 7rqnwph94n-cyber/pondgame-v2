# Silica Street — playable production benchmark v0.1

**Status:** Ready for implementation planning  
**Owner:** Codex visual track with Claude domain-state integration  
**Purpose:** Turn the approved Verdant direction into one small, playable, measurable city block before broad asset production.

Production turnarounds and their binding corrections are reviewed in `concepts/SILICA_STREET_TURNAROUND_REVIEW.md`.

The benchmark UI hierarchy and bindings are defined in `SILICA_STREET_UI_CONTRACT.md`. Shelter and service production corrections are recorded in `concepts/SILICA_STREET_SERVICE_TURNAROUND_REVIEW.md`.

Silica Street is not a vertical-slice content checklist in miniature. It is the minimum scene capable of proving that extraction, transport, storage, processing, construction, residence services, seasonal presentation and economic diagnosis all belong to the same game.

## Success statement

At ordinary settlement zoom, a new player should be able to watch the district for five seconds and identify:

- where Raw Silicate originates;
- which organism is moving it;
- where it is waiting;
- where it becomes Prepared Silica;
- whether the processor is operating or blocked;
- whether the nearby residences are healthy or deteriorating.

Opening the inspector or Industry Overseer should then explain the exact cause without contradicting what the world shows.

## Benchmark boundary

### Included

- one authored basin block;
- one Silicate patch and extraction contact zone;
- one route spine with a branch to storage and processing;
- one General Store;
- one Mineral Washery;
- two Shelter clusters;
- one Photosynthetic Field;
- one Clean-Flow Node;
- one basic Waste Collector;
- three General carriers and both Silicate payload forms;
- construction ghost and 0/25/50/75/100% build presentation for one structure;
- Bloom and Dry environmental presentations;
- building inspector, service overlay and compact Industry Overseer prototype.

### Explicitly excluded

- full free-build mode;
- the complete resource roster;
- final pathfinding or balance;
- residence tiers above Shelter;
- morphology selection;
- trade, the Memory Reef and advanced civic buildings;
- production-ready vegetation variety beyond the benchmark kit.

## Spatial specification

Use **1 authoring unit = 1 metre** for export and engine placement. These dimensions establish relative readability, not gameplay collision or final build-grid rules.

### Scene envelope

- Authored block: 48 × 32 m.
- Calm central movement corridor: at least 4 m clear width.
- Default Settlement view: approximately 42 × 24 m visible.
- Quiet border: 2–4 m of terrain dressing around interactable silhouettes.
- No interactable object may be hidden entirely behind another from the default camera.

### Layout coordinates

Origin is the centre of the block; +X runs east and +Z runs north.

| Element | Centre | Presentation footprint | Orientation and purpose |
| --- | ---: | ---: | --- |
| Silicate Outcrop | (-16, +8) | 7 × 6 m | Dark rear-left landmark; worked face points southeast |
| Extraction contact zone | (-12, +5) | 3 × 3 m | Keeps workers visible against the patch |
| General Store | (-3, +4) | 6 × 5 m | Open stock chambers face south/southeast |
| Mineral Washery | (+6, +5) | 8 × 6 m | Dirty intake west; pale output east |
| Clean-Flow Node | (+11, +9) | 3 × 3 m | Feeds washery and visibly clears its channel |
| Waste Collector | (+10, -1) | 4 × 4 m | Downstream of industry; distinct dark collection cups |
| Shelter Cluster A | (+7, -9) | 7 × 6 m | Clean residential foreground with service connections visible |
| Shelter Cluster B | (+15, -8) | 7 × 6 m | Enables neighbourhood comparison and service falloff |
| Photosynthetic Field | (-5, -9) | 9 × 6 m | Broad low silhouette; keeps foreground agriculture readable |

The main route enters at (-20, +2), passes the Outcrop contact, Store and Washery, then bends south between agriculture and residences. The route is a low-edged surface treatment; it must never resemble a raised railway or obscure carrier feet/contact anatomy.

## Camera and scale contract

Initial camera calibration target:

- orthographic projection;
- yaw 45°;
- pitch 38° downward;
- default view centred near (0, 0, 0);
- near zoom frames one processor plus adjacent route;
- Settlement zoom frames the 42 × 24 m working block;
- Territory zoom preserves patch, industrial and residential colour-value groups but does not promise unit-state readability.

The first engine review must test eight 45° yaw increments. If the world camera will not rotate in normal play, rear and roof review still remains mandatory for asset quality and future camera events.

### Screen-space targets at 1920 × 1080

- General carrier length at Settlement zoom: 38–52 px.
- Small payload silhouette: no dimension below 8 px.
- Building state-changing feature: at least 14 px across.
- Service warning marker, when enabled: 22–28 px and never the only state cue.
- Main stock/resource icon: 24 px minimum.

These are calibration targets. Record actual captures before locking mesh detail or texture density.

## Asset contracts

### `patch_silicate_a`

- Bounds target: 7 × 6 × 3.5 m.
- Three authored depletion presentations: `rich`, `worked`, `depleted`.
- Use 5–7 large removable/readable facets, not dozens of shards.
- Raw Silicate is translucent blue-grey with dark host rock; Prepared Silica becomes paler and more regular.
- Required anchors: `WorkerAnchor_1`, `WorkerAnchor_2`, `PayloadAnchor`, `LabelAnchor`, `FXAnchor`.

### `unit_general_carrier_a`

- Length target: 1.3 m; loaded silhouette grows vertically or laterally by at least 15%.
- Avoid a conventional crab: use a buoyant central mantle, four principal contact limbs and two dedicated cargo membranes.
- Required actions: `idle`, `move`, `carry_move`, `collect`, `deliver`, `work`, `strained`.
- Payload must sit within authored anatomy at `PayloadAnchor`, with separate offsets for raw fragments and prepared bundles.
- Colour/emission cannot be the only loaded-state cue.

### `store_general_a`

- Bounds target: 6 × 5 × 3 m.
- At least three open typed chambers; contents visible from default and opposite yaw.
- Fill presentations: `empty`, `partial`, `full`, `loading`.
- Storage silhouette must remain lower and broader than the Washery.
- Required anchors: typed `InputAnchor_*`, `WorkerAnchor_1`, `LabelAnchor`, `CameraAnchor`.

### `proc_mineral_washery_a`

- Bounds target: 8 × 6 × 4.5 m.
- Three-stage process silhouette: dark/dirty intake cup, translucent moving wash membrane, pale ordered output shelf.
- States: `idle`, `awaiting_input`, `active`, `output_blocked`, `unstaffed`, `strained`.
- Whole-building pulsing is prohibited; only flow, membrane tension, valves and local amber organs animate.
- Required anchors: `InputAnchor_raw_silicate`, `OutputAnchor_prepared_silica`, two `WorkerAnchor_*`, `ServiceAnchor`, `LabelAnchor`, `FXAnchor`, `CameraAnchor`.

### `res_shelter_cluster_a`

- Bounds target: 7 × 6 × 3.8 m.
- Construction presentations: foundation, frame, sealed chamber, occupied finish plus optional continuous growth mask.
- Runtime conditions consume Claude's `normal`, `strained`, `dormant` values.
- World cues must follow `VERDANT_MATERIAL_SERVICE_UI.md`: occupancy light regularity, membrane openness, local growth, channel condition and activity.
- Upgrade readiness is interface-only in this benchmark; do not morph into a Stable model yet.

### Service and farm props

- Clean-Flow Node target: 3 × 3 × 2.5 m with visibly clear upstream/downstream ribbon.
- Waste Collector target: 4 × 4 × 2.5 m with contained dark payload and no toxic-green shorthand.
- Photosynthetic Field target: 9 × 6 m assembled from 2–3 m bed modules; Dry stress changes posture and density, not only hue.

## Material kit

The benchmark should use no more than six principal material families:

| Family | Read | Notes |
| --- | --- | --- |
| Carbonate lattice | chalky warm off-white, porous | structural frame; low gloss |
| Living shell | deep teal-blue | broad calm masses; subtle wet response |
| Membrane | pale blue-green translucent | sparing; verify sorting from all yaws |
| Silicate | cool cyan/blue-grey crystalline | raw irregular, prepared ordered |
| Active organ | restrained amber | life/process cue, never universal trim |
| Silt/organic matter | muted sand through dark brown-black | separates clean terrain, waste and host rock by roughness |

Coral is a warning/accent colour and does not belong in the base material kit. Fine filigree from concept art becomes normal/roughness breakup or a few large structural ribs.

## Domain-to-presentation mapping

Art consumes state; it does not infer or calculate it.

| Domain/presentation field | World response | Interface response |
| --- | --- | --- |
| patch richness/depletion | facet set and worked scar | remaining-stock bar/value |
| carrier payload ID/amount | attached payload mesh and loaded posture | selected-unit cargo row |
| processor input starvation | empty intake, slack membrane | `AWAITING INPUT`, missing resource |
| processor active/progress | local flow and staged material | progress and throughput |
| processor output blockage | filled output shelf, stopped outlet | `OUTPUT BLOCKED`, destination/stock cause |
| worker assigned/required | visible worker anchors occupied | assigned/required fraction |
| residence `condition` | normal/strained/dormant material and activity set | condition label and principal blocker |
| `need_buffer_minutes` | no direct numerical visual | buffer time beside each need |
| `services_for_next_tier` | optional local service overlay | met/missing service rows |
| evolution blockers/progress | no tier swap in benchmark | readiness ring, sustain and blockers |
| upkeep state | local disrepair layer when unpaid | `not_enforced`, `grace`, `paid`, `unpaid` with reason |
| season/current | field posture, motes, channel strength | season strip, duration and affected outputs |

Stable IDs must link every inspector/Overseer row back to one or more selectable map entities. UI must never recreate production or service rules.

## Required scenario reel

An adapter-compatible deterministic harness should expose six selectable scenarios:

1. **Healthy flow:** carriers complete the full chain; residences normal.
2. **Input starvation:** Raw Silicate absent; Washery awaits input.
3. **Output blockage:** Prepared Silica shelf and Store allocation are full.
4. **Worker shortage:** Washery unstaffed while other district activity continues.
5. **Service failure:** flow or waste service removed; residences progress normal → strained → dormant using domain timing.
6. **Recovery and Dry transition:** service restored, residue cleared, activity returns, then Dry changes farm and environment presentation.

Scenario controls change authoritative harness inputs or snapshots. They may not directly toggle arbitrary meshes in production scenes.

## Minimal interface package

### Main HUD

- current season and time-to-transition;
- selected headline stocks: Raw Silicate, Prepared Silica, food and Repair Enzyme;
- population/free workforce and protected Builder allocation;
- one compact alert stack prioritised by severity.

### Building inspector

- name, state and staffing;
- recipe input, progress and output;
- current throughput and principal blocker;
- maintenance state;
- locate suppliers and destinations.

### Residence inspector

- tier and condition;
- population/capacity;
- need buffers and service satisfaction;
- evolution target, sustain progress and named blockers;
- expressed morphologies, even if none are available in the benchmark.

### Industry Overseer

One Silica row is sufficient for the benchmark. It must show source → carrier → store/process → output, stock, throughput, assigned/required workers, bottleneck and seasonal forecast. Selecting a node focuses or highlights matching entities in the world.

## Parallel work split

### Claude / implementation track

- keep state identifiers stable and provide fixture snapshots for the six scenarios;
- create or preserve adapter boundaries for selection, process and residence state;
- ensure Builder protection/food-emergency reason is representable;
- expose map-entity links for drill-down;
- use primitives/placeholders until visual assets pass import review.

### Codex / visual track

- author production turnarounds for carrier, Outcrop, Store and Washery;
- establish the six-material test kit;
- prepare scale dummies and anchor diagrams;
- audit legacy terrain/vegetation candidates against the scene;
- provide icon silhouettes and inspector/Overseer wireframes;
- review engine captures at the camera matrix before approving detail.

## Acceptance gate

Silica Street passes only when:

1. the resource story passes the five-second read at Settlement zoom;
2. every scenario produces coherent world and UI feedback from the same state;
3. raw and prepared Silica remain distinct in colour-blind/greyscale inspection;
4. Store, Washery, residence and field silhouettes remain distinct through the yaw matrix;
5. carrier payload and building process remain readable at the screen-space targets;
6. assets import at metre scale with correct pivots and named anchors;
7. the representative density test identifies no unaddressed material, transparency or animation blocker;
8. Rich approves an in-engine capture, not only a concept render.

Only after this gate should the project manufacture the broader processor, residence and morphology roster.
