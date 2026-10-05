# Verdant material, service-state and Overseer direction

**Status:** Approved visual foundation supplement
**Scope:** Art and presentation behaviour; no balance values, footprints or recipe changes
**Images:**

- `verdant_resource_material_lifecycle_v01.png`
- `verdant_neighbourhood_service_states_v01.png`
- `verdant_overseer_ui_direction_v01.png`

These boards close the three largest gaps between the existing atmosphere pieces and a buildable city-builder presentation: how resources read through a production chain, how settlement condition reads in the world, and how the player diagnoses the economy.

## 1. Material lifecycle

The lifecycle board establishes a visual syntax for eight resource families: photosynthetic food, phosphate/fertility, silica, carbonate/ceramic, fibre/resin/composite, waste/repair, pigment/culture and anoxic chemistry.

Every chain must remain readable in this order:

1. environmental source or patch;
2. harvested payload carried by a creature;
3. dedicated storage with the material visible;
4. processed or refined intermediate;
5. recognisable civic, structural or consumer use.

The carrier is a scale and logistics cue, not a decorative mascot. Payload silhouettes and colours must remain visible from the settlement camera. Storage should expose inventory rather than hiding it inside a generic warehouse. Processed goods retain some visual ancestry so the player can learn chains without relying entirely on labels.

### Production corrections

- Do not use the concept's arrows in-world; route direction belongs to overlays and the Overseer view.
- Increase silhouette differences between storage buildings when reduced to game scale.
- Keep carbonate, silica and phosphate separated by shape as well as colour for accessibility.
- Avoid making every processed material glossy. Fibre, sediment, ceramic and repair matter require distinct roughness responses.
- Treat the depicted products as a visual vocabulary, not proof that every chain belongs in the first vertical slice.

## 2. Neighbourhood service states

The six-panel neighbourhood board shows one persistent district in a normal, nutrition-starved, flow/waste-starved, strained, dormant and recovered condition. A neighbourhood does not become a different art set whenever a number changes. Its same structures and paths accumulate legible symptoms.

State should be expressed through a restrained stack of signals:

| State | World-readable signals |
| --- | --- |
| Normal | full culture beds, clear flow, active carriers, open membranes, steady amber occupancy light |
| Nutrition shortfall | depleted cultivation trays, thinner planting, increased gathering traffic, reduced residence activity |
| Clean-flow or waste shortfall | cloudy or interrupted channels, waste accumulation at collection points, stressed planting |
| Strained | partial membrane closure, faded growth, reduced traffic, amber light becomes uneven |
| Dormant | dry channels, closed openings, muted bioluminescence, abandoned beds, structure remains recoverable |
| Recovered | cleared routes and water, replanted beds, occupancy and service activity restored; scars may remain |

The world state should tell the player that something is wrong before the interface explains why. It must not rely on saturation alone. The exact cause is then supplied by the residence inspector and service overlays.

### Production corrections

- The generated board is intentionally exaggerated for comparison. In play, transition intensity should scale continuously from domain state.
- Do not remove or replace whole buildings for temporary shortages.
- Preserve enough environmental history after recovery to make the settlement feel inhabited, but never leave false warning cues.
- Keep warnings local and material: blocked conduits, spent beds, waste piles and closed membranes are preferable to permanent floating icons.

## 3. Overseer interface

The UI board establishes the desired relationship between settlement, diagnosis and action. It borrows the managerial clarity of *Pharaoh*—a small number of authoritative departmental views—without copying its visual assets or screen layout.

The primary Overseer categories are:

- Environment
- Provisions
- Industry
- Logistics
- Population
- Health
- Evolution
- Trade
- Civic
- Projects

The Industry Overseer demonstrates the minimum useful chain row: input and process icons, current stock, throughput per cycle, assigned versus required workers, bottleneck status and a compact seasonal forecast. Selecting any problem should locate affected buildings, carriers or patches in the world.

The residence inspector demonstrates the opposite direction: select a place in the world and see nutrition, clean flow, waste, health, culture and upgrade readiness. The upgrade ring communicates progress, but the named missing requirement must remain visible and actionable.

### Interface rules

- Use deep desaturated teal panels, pale porous borders, slim silica dividers and limited amber/coral status accents.
- Reserve coral for genuine intervention states, not ordinary inefficiency.
- Icons must have both silhouette and colour distinctions; selected states require a non-colour cue.
- Use icons for scanning and short labels for certainty. Do not create an icon-only economic spreadsheet.
- The main view remains dominant. Ledgers are opaque enough to read and close enough to the world that selection and camera focus feel continuous.
- Every aggregate should drill down to the entities responsible. Avoid unexplained global scores.
- Seasonal forecasting is a first-class affordance because access, fertility and current strength are part of the economy rather than decorative weather.

### Production corrections

- The concept contains illustrative names, counts and rates only. None are canonical balance data.
- Final interface spacing and density must be tested at the project's supported display sizes.
- The presentation layer should consume domain diagnostics; it must not duplicate economic logic to manufacture these rows.
- Generated architecture and icons are mood targets, not final copyrighted or production-ready assets.

## Implementation-facing state requirements

Presentation adapters should eventually expose, without art code recomputing them:

- resource source, payload, destination, stored amount and processing state;
- building recipe progress, input starvation, output blockage and worker coverage;
- neighbourhood service satisfaction and the principal cause of strain or dormancy;
- residence tier, upgrade requirements, sustain progress and recovery state;
- current season, affected production/access modifiers and forecast values;
- stable identifiers linking an Overseer row to map entities and vice versa.

These are interface requirements, not a request to expand Milestone A or to invent unauthorised mechanics. Placeholder UI may be plain, provided its architecture can represent these states later.
