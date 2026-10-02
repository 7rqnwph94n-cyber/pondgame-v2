# Pondgame v2 — Verdant visual art bible v0.1

**Status:** Vertical-slice production direction

**Owner:** Codex visual track; Rich approves benchmark direction

**Scope:** Verdant Basin only

## Visual thesis

Pondgame is a miniature alien civilisation grown from living glass, coral, shell, mineral and cultivated membrane. Its world should feel beautiful, damp, deep and biologically purposeful—not like human machinery covered in coral decoration.

At a glance the player should see three nested ideas:

1. a substantial underwater landscape shaped by flow, sediment and chemistry;
2. a legible city with residential, agricultural, industrial and civic districts;
3. close-up organisms and structures whose materials reveal how they live and work.

The emotional target is **wonder through comprehensible strangeness**. The player should want to inspect unfamiliar forms, then understand them from silhouette, material flow and animation.

## Relationship to the former Pondlife style

Preserve:

- deep teal shells, green growth, amber organs and pale mint highlights;
- rounded buds, branching lobes, opening cups and living-rib structures;
- jewel-like eyes and small luminous internal organs;
- selective translucent membranes;
- clustered environmental composition around substantial terrain anchors;
- fully rounded assets built for free camera rotation;
- organic construction revealed through additive growth stages.

Change:

- replace the generic unit/building roster with forms derived from actual Verdant economic functions;
- make inputs, transformation and output visible on processors;
- make chemical patches geographical formations rather than coloured pickups;
- reserve faction variation until one complete Verdant civilisation works;
- reduce decorative surface noise and prioritise district-scale readability;
- distinguish raw, prepared and refined states physically.

## The four readability distances

### Territory view

The player reads district mass, terrain, seasonal waterline, major routes, hazards and the Memory Reef. Individual detail disappears. Colour and silhouette must carry meaning.

### Settlement view

The normal play view. The player reads residence tier, building family, active/inactive state, resource patch type, goods movement and major service coverage.

### Building view

The player reads inputs, moving parts, stored output, construction stage, stress and maintenance. Material transitions must be visible.

### Organism view

The player reads morphology, payload, health and personality. This is where eyes, membranes and articulated work behaviour earn their budget.

Every asset is approved first at Settlement view. Close-up beauty cannot rescue a weak gameplay silhouette.

## Shape language

### Verdant civilisation

- Primary forms: rounded shells, leaf-shaped plates, cups, vesicles and branching ribs.
- Secondary forms: mineral inclusions, porous filters, woven lattices and translucent seams.
- Direction: growth radiates outward from a protected core.
- Balance: asymmetry should feel grown, while functional openings remain unmistakable.
- Avoid: rectangular factory boxes, human doors/windows, decorative pipes without biological logic and arbitrary spikes.

### Functional shape cues

| Function | Required cue |
|---|---|
| Storage | Open or translucent chambers with visible contents |
| Filtering | Repeated porous surfaces across a clear flow direction |
| Cultivation | Ordered living beds connected to substrate and tending access |
| Crushing/washing | Feed throat, progressive chambers and separated discharge |
| Heating/firing | Insulated chamber, hot inner core and cooled output shelf |
| Weaving/composite | Tensioned strands crossing around a forming body |
| Residence | Protected inhabited cavity, brood/light signs and readable tier growth |
| Civic/memory | Radial gathering form, repeated encoded marks and calm pulse rhythm |
| Logistics | Clear through-route, loading cups and directional flow |

## Material families

Use a small shared library so a large city remains coherent and economical.

| Material | Look | Uses | Motion/state cue |
|---|---|---|---|
| Living shell | Deep teal, semi-gloss, subtle growth bands | bodies, residences, durable organs | small breathing expansion |
| Soft growth | green, waxy, low roughness variation | farms, fresh construction, service tissues | unfurling and current response |
| Membrane | pale mint, thin and selectively translucent | filters, sacs, fins, canopies | tension, fill and gentle flutter |
| Amber organ | warm focal emission under opaque covering | activity, health, cognition | pulse tied to work cycle |
| Carbonate | chalk/cream, porous, matte | reef, bulk construction | chips and layered accretion |
| Silica | cool blue-green, translucent only at edges | prepared mineral, glassy reinforcement | glints and rigid fracture |
| Ceramic | pale stone with darker fired rim | heat-resistant structure | warm-to-cool process gradient |
| Fibre | muted green/tan strands | routes, lattices, composite | tension and weave motion |
| Resin | honey/amber, viscous then glossy solid | seals, composite and ornaments | flowing-to-cured state |
| Pigment | saturated coral/violet accents | culture, identity, trade goods | restrained shimmer, never neon flood |

Transparency is exceptional. Start opaque and add translucent surfaces only when they explain filtering, fluid level or fragile tissue. Overlapping transparency must survive Godot sorting and distant zoom.

## Palette hierarchy

Core Verdant starting swatches:

- deep teal shell `#174B50`;
- leaf green growth `#75B96B`;
- amber organ `#FFC05A`;
- pale mint membrane `#C3EDC2`;
- carbonate chalk `#D9D5BE`;
- silica cyan `#8CE0DE`;
- silt brown `#615D4E`;
- pigment coral `#EF7967`;
- memory violet `#77729C`.

Rules:

- Terrain is lower saturation and value contrast than interactables.
- Raw-resource identity uses material and form first, colour second.
- Amber emission means living activity, not selection.
- Ownership, selection, warning and accessibility colours remain separate UI channels.
- Reserve the brightest coral/violet for cultural goods and Memory structures.
- Test all production assets in greyscale and common colour-vision simulations.

## Chemical geography

Resources appear as environmental processes, not loot piles.

| Patch | Environmental read | State changes |
|---|---|---|
| Sunlit shelf | broad bright shallow, rippled substrate, anchored crop beds | light intensity and seasonal waterline |
| Phosphate sediment | dark fertile laminae and pale granular inclusions | dredge scars; sealed during High Water; fresh deposition |
| Nutrient channel | suspended motes concentrated by visible flow | density and direction change by season |
| Silicate outcrop | rigid glassy seams emerging through silt | removable facets and exhausted scar |
| Carbonate reef | chalky porous shelves and layered living crust | cut faces and slow edge regrowth only where designed |
| Anoxic basin | still dark pocket, oily iridescence, sparse stressed life | expanding dark boundary and gas release in Dry Phase |
| Pigment shallows | subtle coloured microbial film, not a neon pool | cultivated saturation and contamination bleaching |
| Clean-flow spring | clear rising current, pale filter fauna and clean substrate | contracted reach during Dry Phase |

Patch boundaries should be readable but irregular. Avoid rings, hex decals and uniform circular deposits unless shown only in an optional management lens.

## Goods states

Every vertical-slice good needs four representations where relevant:

1. environmental/raw source;
2. carried payload;
3. stored bundle;
4. processed output.

Goods share material identity across representations. Prepared Silica remains recognisably derived from Raw Silicate; Habitat Composite visibly contains fibre, cured resin and silica rather than becoming a generic purple crate.

Payloads use simplified silhouettes and one material slot. Storage may instance the same payload mesh in bins or chambers.

## Architecture and districts

### Residential

Low, broad, protected and socially clustered. New tiers add chambers, cultivated gardens, service connections and encoded decoration without replacing the original structure. Occupied homes show small internal lights and inhabitants, not constant large animation.

### Agricultural

Ordered repetition adapted to irregular terrain. Field modules should expose cultivation method and seasonal condition. Farms are living landscapes, not square plots.

### Industrial

More rigid, open and process-readable. Inputs arrive on one side, move through visible chambers and leave as distinct output. Vibration, turbidity, heat or waste visually justify reduced residential desirability.

### Logistics

Low-profile routes and nodes preserve sightlines. Goods must be visible entering, waiting and leaving. Direction is encoded through ribs, fronds and current ribbons rather than painted arrows.

### Civic

Calmer rhythm, stronger radial symmetry and cultural pigment. Civic forms should feel collectively inhabited rather than industrially efficient.

### Memory Reef

The settlement landmark. It grows from chalk foundation bed to woven living lattice to a crown of encoded silica/resin surfaces. Each stage must read from Territory view and visibly embody materials delivered by the economy.

## Organisms and morphology

The first carrier/generic worker is a rounded organism with paired collecting cups, visible cargo abdomen and clear forward direction. It is not the final answer for every caste.

Morphologies must change action silhouette:

| Morphology | Visible change |
|---|---|
| Burrowing Limb | broad digging paddles and grounded stance |
| Filter Crown | radial porous fan held into current |
| Mineral Jaw | reinforced cutting plates with silica edge |
| Detox Sac | paired darker processing sacs and warning-colour valves |
| Vascular Carrier | enlarged payload vessels and stronger transport ribs |
| Memory Ganglion | protected luminous neural crown with signalling tendrils |

Do not communicate morphology only through icons or colour. Caste variants may share a base rig where anatomy permits.

## Animation language

- Idle: low-amplitude breathing or internal circulation.
- Move: body-propelled motion with clear acceleration and stop; no sliding mesh.
- Work: contact with the target and material response.
- Carry: payload mass changes pose or buoyancy.
- Build: repeated placement/growth action directed at the construction site.
- Stress: reduced amplitude, protected posture and irregular pulse.
- Dormancy: closed form, dim core and minimal movement.
- Evolution: additive unfurling/accretion, not a flash-and-swap.

Whole-model pulsing and bobbing are not substitutes for authored action. Keep locomotion in place; gameplay controls position.

## Environment composition

- Keep approximately two-thirds of central construction ground visually quiet.
- Cluster detail around a large terrain anchor, smaller supporting forms and planted transitions.
- Use substantial ledges, roots and shelves to create chemical/geographical districts.
- Avoid evenly scattered props.
- Tall forms belong at boundaries and landmarks where camera occlusion is manageable.
- Interactive patches remain visually stronger than decorative versions of similar material.
- Seasonal change should affect waterline, motes, crop posture, sediment exposure and distant colour—not merely apply a fullscreen tint.

## Lighting and atmosphere

- Cool broad underwater fill with one soft directional source.
- Local amber activity emission and very restrained cultural pigment light.
- Contact shadows and grounded geometry are mandatory before bloom/fog polish.
- Caustics move slowly and at low contrast.
- Distance becomes darker, cooler and less saturated.
- Interactive silhouettes retain contrast through fog.
- Validate a neutral diagnostic-lighting mode so post-processing cannot hide weak materials.

## Camera and technical review

Review every hero asset at:

- eight yaw angles at 45-degree increments;
- low, default and high pitch;
- near, settlement and territory zoom;
- neutral and final lighting;
- idle and relevant active state;
- colour and greyscale.

Buildings require designed roofs and backs. Fine alpha planes may supplement plants but cannot form dominant scenery silhouettes.

## UI and icon direction

- Icons use simplified material silhouettes on dark desaturated backgrounds.
- Resource family is encoded by outer frame shape; exact good by central silhouette.
- Avoid chemistry-lab clip art, human tools and literal factory symbols.
- Production-chain arrows and status colours belong to UI, not baked textures.
- Portraits should be rendered from accepted models after benchmark approval.

## Hard avoids

- generic sci-fi metal panels;
- Earth-industrial machinery disguised with vines;
- glowing everything;
- transparent overlapping jelly geometry everywhere;
- dense coral clutter across buildable ground;
- faction identity through recolour alone;
- resources that differ only by hue;
- whole-building scale pulses;
- high-frequency texture noise invisible at play distance;
- programmer art becoming a permanent collision or silhouette contract;
- asset production for post-slice worlds before the Verdant benchmark passes.

## Approval gate

No asset family enters bulk production until a representative benchmark passes:

1. Settlement-view functional read.
2. Camera rotation and roof/back review.
3. Process/state animation driven through the adapter.
4. Mixed-scene contrast and occlusion.
5. Godot import with stable paths and no external dependencies.
6. Recorded performance in a representative density scene.
7. Rich's explicit visual approval.

## Approved progression reference

The same-species visual progression across Early Settlement, Mature Industry and Memory/Planetary thresholds is recorded in `docs/art/concepts/VERDANT_ERA_PROGRESSION.md`. Those boards extend the art direction without expanding the current implementation scope.

Residence growth, branching morphology and map-development rules are recorded in `docs/art/concepts/VERDANT_EVOLUTION_STORYBOARDS.md`. Those spreads establish additive world-readable progression and do not define balance values.
