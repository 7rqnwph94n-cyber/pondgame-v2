# Pondgame v2 — legacy asset reuse audit v0.1

**Source reviewed:** `../art_exports/benchmark`, `../art_exports/biomes_v02`, `../art_exports/evolution_v03` and the former art-direction documents.  
**Classification:** REUSE, ADAPT, KITBASH, RETIRE or HOLD.

This is a design/production audit, not an import approval. Every reused file must still pass provenance, Godot import, scale, material and camera checks inside v2.

## Reuse principles

- Reuse visual labour, not obsolete gameplay assumptions.
- Preserve source files and manifests; do not copy anonymous GLBs without provenance.
- Import assets through a v2 staging directory before accepting canonical paths.
- Gameplay IDs in v2 determine presentation mapping; legacy registry IDs do not.
- Do not bring old Godot scripts or gameplay collision with presentation scenes.
- Prefer a consistent revised material pass over a mixed old/new city.

## Summary

| Family | Disposition | Expected reuse |
|---|---|---:|
| Terrain tiles/materials | REUSE/ADAPT | 80–90% |
| Ledges and boulders | REUSE | 90% |
| Roots and environment props | REUSE | 80–90% |
| Plants and ground details | REUSE/ADAPT | 70–85% |
| Habitat assemblies | KITBASH | 60–75% |
| Ambient fauna | REUSE | 80% |
| Symbionts | HOLD/ADAPT | 60–80% |
| Algae/mineral/detritus resources | KITBASH/RETIRE AS IDs | 30–60% |
| Verdant Gatherer | ADAPT | 50–70% |
| Biofilm Shelter evolution | ADAPT | 60–80% |
| Other legacy buildings | KITBASH/HOLD | 25–60% |
| Old UI icons | RETIRE/KITBASH | 10–30% |
| Legacy shaders/effects | ADAPT | 40–70% |

## Environment library

### REUSE after import validation

- Six boulders: strong neutral anchors; preserve asymmetry and finished backs.
- Eight ledge modules: useful terrain grammar for basin shelves and patch boundaries.
- Four root forms: useful Pond/clean-flow landmarks.
- Four pebble clusters: retain as low-contrast detail only.
- Three ambient fauna: retain at low contrast after material harmonisation.
- Silt, sand, gravel and rock ground materials: retain as base substrate library.

### ADAPT

- Plant families: adjust palette hierarchy so cultivated crops and resource patches are unmistakable beside decoration.
- Ground details: mineral seam and algae stain can support chemical storytelling, but cannot stand alone as interactive resource visuals.
- Terrain materials: expose parameters for wetness, seasonal waterline, contamination and patch blending.

### KITBASH

- Existing Rock Pool/Pond assemblies: harvest compositions and modules for Verdant basin landmarks; rebuild layouts around v2 economic geography.
- Root Glade and Frond Meadow: potential clean-flow and sunlit-shelf anchors.
- Mineral Shelf: basis for Silicate Outcrop, with new glassy facets and depletion stages.
- Detritus Hollow: basis for anoxic basin boundary, with new fluid/gas cues.

## Resource assets

### Legacy algae

**Disposition:** KITBASH.

Use geometry variants as raw material for Photosynthetic Field and decorative biomass. Remove the assumption that “algae” is the universal food node. Add planted order, fertility state and seasonal posture.

### Legacy minerals

**Disposition:** KITBASH.

Chunk-removal logic and arrangements are useful. Split visual language into Silicate Outcrop and Carbonate Reef; do not retain a generic Minerals resource.

### Legacy detritus

**Disposition:** RETIRE as a primary resource ID; KITBASH visually.

Flake/pod shapes may appear in organic waste, anoxic deposits and sediment detail. The former catch-all Detritus economy must not return.

### Silica and chitin payloads

**Disposition:** ADAPT/HOLD.

Silica can seed Prepared Silica payload and storage. Chitin is outside the first Verdant slice unless selected later as a substitute material; do not import it as required content.

## Organisms

### Verdant Gatherer

**Disposition:** ADAPT as the general carrier foundation.

Retain rounded body, collecting cups, Verdant material language and existing clip experiments. Required changes:

- stronger forward read;
- payload vessels sized for visible cargo;
- adapter-compatible action names;
- morphology attachment zones;
- removal of legacy role assumptions;
- revised scale test against v2 map and logistics distances.

It should become a shared body foundation for General labour, not the permanent appearance of every caste.

### Unfinished former roster

**Disposition:** HOLD.

Do not produce the old 11 roles × 3 factions. Revisit individual concepts only when a v2 morphology or occupation needs them.

## Buildings

### Biofilm Shelter and evolution additions

**Disposition:** ADAPT.

Strong candidate for Shelter Cluster → Stable Habitat → Symbiotic Neighbourhood foundations. Rework requirements:

- visibly occupied cavities;
- service connection anchors;
- waste/need state cues;
- stage additions aligned to v2 residence tiers;
- no dependency on the old population-training function;
- Memory Enclave requires a new cultural crown.

### Storage Pit / Sorting Hollow

**Disposition:** ADAPT.

Use as General Store foundation if stored goods can appear as typed payload instances. It requires loading cups, carrier access and acceptance-state visuals.

### Silt Filter

**Disposition:** KITBASH into Filter Crown or Nutrient Washer.

The old stepped basins are useful, but the v2 version must show flow direction and separated output.

### Current Channel / Weir

**Disposition:** ADAPT.

Useful foundation for Flow Channel and Clean-Flow Node. Remove old combat/slow assumptions. Preserve unobstructed route read.

### Nutrient Spring

**Disposition:** KITBASH.

Potential Clean-Flow Spring landmark or service structure, not a passive magical resource generator.

### Mineral Refinery

**Disposition:** KITBASH into Mineral Washery or Ceramic Kiln.

Separate washing and firing functions. Do not ask one mesh to represent both recipes.

### Coral Scaffold

**Disposition:** ADAPT.

Good construction-site and Great Work staging vocabulary. May become shared scaffolding pieces rather than one economic building.

### Spawning Pool

**Disposition:** ADAPT into First Nursery.

Strong functional match. Add morphology conversion state, visible brood and safe dormant state.

### Defensive buildings and old capstones

**Disposition:** HOLD.

Reef Wall, Crystal Bastion and other defence-first assets are not slice requirements. Their geometry may later support hazard protection.

## Symbionts

**Disposition:** HOLD/ADAPT.

The four models and idle/content/stressed state work are valuable, but the new economy must decide whether symbionts are services, morphology enablers, crops or population needs. Import only after their mechanics exist.

## Shaders and effects

### ADAPT

- underwater ground blending;
- light shafts;
- restrained caustics;
- selection/feedback ring ideas;
- bubble and ambient-fauna fields;
- vignette only if it survives UI/readability review.

Do not copy fixed numeric fog/light values from the old orthographic rig. Recalibrate against the v2 camera and world scale.

## Import pipeline

1. Copy selected source and export candidates into an external staging batch.
2. Verify provenance and manifests.
3. Import into a v2 art sandbox, not gameplay scenes.
4. Calibrate one shared world scale and ground convention.
5. Apply revised material library.
6. Validate rotation, pitch, zoom, states and performance.
7. Classify accepted assets in the v2 manifest.
8. Only then move them to canonical paths.

## Immediate reuse batch

Bring forward only what the first benchmark needs:

- silt material;
- one rock material;
- three boulders;
- ledge straight, corner and ramp;
- one root arch;
- three plant forms;
- Verdant Gatherer foundation;
- Biofilm Shelter foundation;
- Storage Pit foundation;
- mineral facet geometry for Silicate;
- algae geometry for Photosynthetic Field;
- restrained caustic/light-shaft support.

Everything else stays outside the v2 runtime until demanded by a tested mechanic.

