# Pondlife: brief and reference comparison

6 October 2026. Codex review prompted by Rich's rejection of terrestrial roads and the redundant river. This is a design/code audit of the playable main build and draft PR #5, not a fresh native playtest. The Mac is locked. Proposed mechanics below are labelled as recommendations; they are not implemented features.

## What we were asked to build

The earliest [full-scope brief](design/ORIGINAL_FULL_SCOPE.md) establishes biology as the technology tree, underwater scale and an organic-to-industrial civilisation. The [2 October Chemical Civilisation GDD](design/CHEMICAL_CIVILISATION_GDD.md) explicitly supersedes the original economy and fixed-era implementation assumptions. Its sections 2–4 make Pharaoh-style settlement relationships the central experience. Section 2 already permits a road to be a controlled current; section 26 includes a nutrient-bearing flow channel and an anoxic basin.

The [art direction](design/ART_DIRECTION.md) requires a fantastical underwater world, rounded living structures and biological motion. Our [art bible](art/ART_BIBLE.md) explicitly calls for transport direction through fronds and current ribbons.

The inherited requirement is not a medieval or Egyptian settlement placed on an underwater backdrop. Chemistry, transport, services and biological growth must determine the settlement's form and make it readable in motion. Rich's later requirement that every building connect overrides the older GDD's preference against universal access requirements.

## Direct comparison

The comparison uses the original [Pharaoh manual](https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/564530/manuals/Pharaoh_-_manual.pdf?t=1481822384), the [Manor Lords developer overview](https://manorlords.com/) and the [official building reference](https://wiki.hoodedhorse.com/Manor_Lords/Buildings/en). We borrow design relationships, not their earthly materials or exact access rules.

| Experience | Pharaoh | Manor Lords | Pondlife now / material gap |
|---|---|---|---|
| Reading the map | Fertility, water and deposits explain settlement choices. | Landscape and routes influence organic settlement form. | Landforms exist, but most production opportunities are not tied to the player's actual building coordinates. Scenic resource identity is ahead of gameplay geography. |
| Planning a settlement | Housing, routes, distribution and civic access form neighbourhoods. | Free placement, rotation and snapping support deliberate layouts. | Manual preview and rotation exist; coherent plots, useful snapping and coverage feedback remain incomplete. The draft's road frontage is terrestrial. |
| Watching it work | Citizens and goods distribution communicate city activity. | Ploughing, industry and other contextual work make the economy tangible. | Playable-main carriers remain presentation traffic. Draft #5 adds real finite cargo, but routes through one founding supply anchor; specialised storage and distributed transfers are not proven. |
| Evolving homes | Goods, services and neighbourhood desirability drive housing improvement. | Building and settlement development sits within the town's economy. | Goods/services and evolution exist, but services are district-wide flags; even draft connectivity does not implement finite reach. Local pollution/desirability does not yet organise neighbourhoods. |
| Inspecting a failure | Right-click housing reveals needs and stored goods; management overlays explain systems. | Placement tools and buildings support managing a spatial town. | Icons, context actions and blockers improved. We still need clear in-world connection, coverage, cargo and missing-input feedback to explain a problem without reading paragraphs. |
| Believing the setting | Architecture, people, terrain and seasonal economy support ancient Egypt. | Construction, landscape and work support a medieval settlement. | Organic blockouts coexist with dry-land legality, a surface-style river, dirt-road strips and walking-route assumptions. These contradict the liquid-medium premise. |

The shortfall is a weak relationship between map, settlement layout and daily life. More buildings or more test counts will not close it. The engine is useful groundwork; it has not yet produced the intended city-building experience.

## Where we drifted

The [slice charter](PLAYABLE_SLICE_CHARTER.md) narrowed work to one opening chain, explicitly deferred full spatial logistics, and required a dry river crossing. Those choices made a testable prototype, but also embedded land-based assumptions and postponed relationships central to the brief. I treated successive technical repairs as milestones toward a playable city without applying the original experience criteria strongly enough.

Code evidence: `Facility.environment_factor` uses season/recipe fertility rather than a sampled field at its world position. `Simulation.services` aggregates eligible providers by district; `services_for` adds a connectivity gate in the draft but no network-distance coverage. Draft `SpatialState._ground_ok` rejects proximity to the channel as water. `road_view.gd` renders ground strips. Draft carrier dispatch is anchored to a common depot. These are specific implementation gaps, not claims that there is no functioning economy.

## Correct transport direction

**User requirement:** all buildings remain connected. The network's fiction and visual treatment must belong to a liquid world.

**Recommendation:** player-grown controlled-current lanes, maintained by living ciliated tissue or small flow organs. Organisms stabilise a local transport corridor within the surrounding liquid. That explains why uncontrolled open-water movement does not substitute for a connected civic network.

- Draw flexible curves with clear junction snapping; present a restrained ribbon of moving suspended motes above the substrate, supported by occasional biological nodes. No paved surface, kerbs, dirt strip or terrestrial bridge.
- Buildings join through a visible intake/transfer organ. Show an actual branch to the network rather than merely accepting proximity. Preview both connection and habitat suitability.
- Carriers swim or glide with visibly different empty/loaded states. They carry real goods into local depots. Flow decoration never implies cargo movement that the simulation has not performed.
- All homes, farms, processors, storage and civic organs require the connected network. Broken connections receive one clear warning and cease new deliveries/operation according to the existing strict policy.
- Keep bidirectional travel until directional flow, return routes and speed differences are explicitly modelled. We must not imply one-way currents or extra throughput through animation alone.
- Prototype this with a graph, spline rendering and authored habitat fields. Full fluid dynamics are unnecessary.

The existing graph/custody work is reusable. The dirt rendering, 'dry ground' vocabulary and channel-as-water exclusion should not be promoted unchanged.

## What the river should become

A liquid medium does not contain an ordinary surface river with dry banks. A submerged flow corridor can still be useful, but it must have a different state from its surroundings.

**Recommendation:** replace the surface river with a submerged nutrient plume or turbulent flow boundary. It could provide valuable filtering feedstock while excessive shear or contamination makes ordinary settlement unsafe. The map must visibly distinguish calm habitat from that flow, and inspection must report the actual benefit and hazard. Calm water is valid habitat; a hazardous current is conditionally restricted. The current blanket 'too close to water' rule is inappropriate.

If we cannot implement an inspectable environmental role in the slice, remove the decorative river and its placement exclusion. Do not invent a hazard merely to justify scenery. Natural resource currents and player-controlled transport lanes should have distinct visual languages.

## Next deliverable and acceptance

Build one coherent submerged neighbourhood before adding breadth: a calm founding patch, an informative resource gradient, connected living transport lanes, one cultivation → processor → local storage → home chain, and one genuinely local civic service. Keep the empty start and paid construction budget.

Acceptance is a normal-speed human click-through:

1. A new player can identify suitable founding habitat and the transport tool without a written build order.
2. A connection preview is truthful; every building has a visible connected port; disconnected placement is rejected.
3. A player can follow one load from source through processing/storage to its destination, and pause freezes actual transport.
4. Moving a provider or industry changes service coverage, travel time or local habitat quality for an explicit reason.
5. The player fixes a visible delivery/service shortage and witnesses a home physically grow because its needs are met.
6. A seasonal/environmental change visibly affects useful geography and leaves a recovery route.
7. At ordinary zoom, Rich recognises an underwater living civilisation. No debug inspector or technical explanation is needed to establish the setting.

PR #5 remains a draft. Do not release the terrestrial-road implementation while this design correction is unresolved. Regression tests protect correctness; they do not substitute for these experience gates.
