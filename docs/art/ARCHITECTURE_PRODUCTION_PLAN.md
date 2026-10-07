# Verdant architecture production plan

Owner: Codex. Scope agreed with Rich, 7 October 2026: six housing tiers, General Store, Mineral Washery, Ceramic Kiln and Waste Digester. This replaces the broad procedural-library production approach. Other new model families stay on hold until these ten establish convincing architecture.

## Fixed sequence and completion gates

1. **Function and massing:** define anatomy, substrate contact, occupied/working volume, inputs, outputs, carrier access and service attachment. Produce all ten as silhouette prototypes in Blender. No shared circular plinth.
2. **Silhouette review:** compare all ten in monochrome at settlement zoom. A building must be identifiable by its main structure; housing stages must change mass, vertical organisation and social character. Reject repeated dome-plus-decoration designs.
3. **Housing refinement:** finish tiers 1–3, then 4–6. Each keeps an identifiable ancestral chamber while making a substantial architectural transformation. Growth stays within an agreed placement footprint; increased height must not hide transport ports.
4. **Functional refinement:** finish Store → Washery → Kiln → Digester. Show actual recipe inputs, transformation and output. No Earth factory boxes or unexplained decorative tubing.
5. **Integration:** export Y-up textured glTF with authored normals, materials, near/distance meshes and visual anchors; retain the previous OBJ fallback and add a separate Godot architecture review scene. Bind existing gameplay definitions to accepted art. Coordinate the six-tier gameplay ladder with Claude before changing capacities, needs, evolution costs or workforce classes.
6. **State pass:** construction growth, empty/full storage, idle/working/blocked processor cues and housing dormancy. Animation must follow simulation state.
7. **Acceptance:** inspect normal-renderer screenshots, orbit views, carrier approach and neighbouring footprints. Record Rich's visual review and any remaining issues. Expand the library only after the ten-model benchmark is accepted.

The current broad `verdant_v2` set is a draft archive, not a completed production milestone. Original assets remain available for comparison and rollback. UI and terrain texture work are outside this architecture block.

## Six housing designs

These are proposed names for six genuine progression tiers. The current engine has only Shelter, Stable, Symbiotic and Memory; two additional gameplay steps require Claude's implementation and balance work. Art prototype completion must not be reported as six playable tiers.

| Tier | Working name | Architectural transformation | Living function |
|---|---|---|---|
| 1 | Seed Shelter | Small partly buried crescent shell; one inhabited opening; exposed anchoring tissue | Protection and basic feeding |
| 2 | Rooted Dwelling | Long double-chamber mantle with grown ribs and a clear vestibule; reinforced substrate contact | Separate brood/rest space and controlled intake |
| 3 | Mature Habitat | Several unequal chambers around a protected central circulation organ; a higher spine replaces the low mantle | Dependable services and productive household |
| 4 | Symbiotic Court | Horseshoe neighbourhood around a cultivated shared court; overhead membrane supported by living arches | Shared nutrition, partner organisms and neighbourhood life |
| 5 | Terraced Habitat | Two-level inhabited mass; broad overlapping shell plates, circulation trunk and cultivated terraces | Collective services and specialist households |
| 6 | Memory Manor | Three-level estate with an integrated archive crown, encoded mineral lattice and multiple occupied chambers | Coordination, culture and retained collective memory |

No tier uses crystals or leaves alone to signal advancement. The ancestral chamber remains recognisable. Tiers differ in scale, height, roofline, cavity arrangement, shared space and material maturity. Population/capacity numbers are deliberately absent from this art plan.

## Four functional buildings

| Building | Primary silhouette | Visible process | Substrate contact |
|---|---|---|---|
| General Store | Broad open storage galleries under a protective asymmetric shell; low and accessible | Two loading mouths; typed goods retained in partitioned chambers; room for a carrier to approach | Separate mineral feet and low anchoring tissue |
| Mineral Washery | Tall feed head descending through three separation basins; strong one-way vertical process | Coarse silicate inlet, cleaning/separation chambers, sediment rejection and clean silica collection | Mineral buttresses beneath elevated process chambers |
| Ceramic Kiln | Thick insulated mineral mantle around a compact high-temperature core; low loading throat and thermal-exchange crown | Prepared silica plus anoxic-organic/biomass feed, enclosed conversion, cooled ceramic output rack | Broad load-bearing mineral roots, no disc plinth |
| Waste Digester | Sealed unequal fermentation lobes joined around a sheltered intake | Organic waste inlet; contained digestion; small enzyme outlet and broad fertiliser discharge | Buried containment belly with short anchoring supports |

## Connection decision

Rich permits additional infrastructure (7 October: "we can add additional infrastructure to suite"). This supersedes the earlier art-plan restriction against an additional utility network; it does not approve specific new operating costs or dependencies.

**Recommended model, pending Rich's routing choice: carrier currents for discrete goods, plus one grown utility trunk containing two physically isolated channels—clean-flow supply and contained waste return.** One player routing action, two distinct simulated services. Cargo carriers must never masquerade as continuous fluid delivery. Clean and dirty channels must never visibly mix. Local service reach remains appropriate for maintenance, health and culture, rather than routing everything through the trunk.

Supporting infrastructure candidates: a Filter Organ producing clean flow from the ambient medium, utility branches/terminations, and a collector feeding the Digester. Audit existing clean-flow and waste service buildings before adding new duplicate producers. Start with connectivity and bounded service reach; pressure, pumps, leaks and electrical networks are outside the first architecture milestone. The choice between a shared trunk, independently routed lines and service-organ coverage remains open.

| Building | Carrier access | Proposed infrastructure/service connection | Representation |
|---|---|---|---|
| All homes | Supply receiving port; waste cargo pickup remains a fallback proposal | Reserve isolated clean-flow inlet and contained waste-return outlet. Tier 1 must remain viable before utilities exist; later tier requirements need balancing | Protected paired utility sockets, separate from the carrier mouth; disconnected sockets visibly dormant |
| Store | At least two separate loading bays | Transport/storage only; living-goods preservation is a separate store design | Clearly accessible goods galleries and loading mouths |
| Washery | Raw feed port and clean silica collection port | Candidate clean-flow consumer and dirty-effluent return; current recipe has neither dependency. Sediment is separated, not silently dissolved into the waste network | Descending separation basins, recirculation gills, isolated utility sockets and grit collection recess |
| Kiln | Separate material/fuel input and cooled-product pickup | Delivered metabolic fuel; maintenance. No electricity or continuous external heat line | Enclosed fuel sac, insulation and thermal exchange gills |
| Digester | Contained solid-waste inlet and separate enzyme/fertiliser pickup | Candidate waste-return destination with clean-flow process inlet. Claude must specify whether fluid feed yields existing organic_waste or a distinct feed; never consume both for the same waste | Sealed receiving belly, paired utility sockets and separated product reservoirs |

`CarrierInput`, `CarrierOutput`, `WastePickup`, `CleanFlowIn`, `WasteReturnOut`, `WasteReturnIn` (Digester), `ServiceAttachment`, `WorkAnchor`, `LabelAnchor` and `CameraAnchor` are visual anchors. They become authoritative docking points only through a versioned domain/bridge agreement. No decorative animation may claim cargo or service activity without simulation evidence. Existing recipes and progression remain unchanged until Claude's dependency proposal is accepted and tested.

### Infrastructure acceptance gates

- A disconnected facility reports the specific missing service; cargo inventory alone does not imply utility access.
- Waste production, transfer, digestion and recovered products conserve their defined units; no infinite feed or duplicate carrier/network feed.
- Filter construction and starting housing do not depend on utilities they are required to create. Verify a playable empty-map opening.
- Six housing tiers must have genuine needs and benefits, not two extra decorative meshes. Show progression and upkeep evidence before replacing the current four-stage ladder.
- Utility geometry and ports are separate from foundations; this must not reintroduce the rejected circular plinth.

## Work ownership

Codex owns models, export, material treatment, attachment geometry, presentation binding and visual review. Claude owns the six-tier domain progression, service dependencies and authoritative cargo docking. Shared client edits are announced in the exchange. The active spatial checkout contains other work; the architecture batch is built in `pondgame-v2-assets`.

## Current status

All ten now have v04 closed anatomy, textured materials, refined apertures/supports, typed cargo groups, construction layers and near/distance exports. Repeated native-camera reviews corrected rear inventory visibility, canopy intersections, twisting collars, protruding light organs and excessive shell gloss. See `ARCHITECTURE_V04_READINESS.md` for tests and the remaining acceptance gates.

Rich's follow-up ("this is good. make it all better.") keeps the same benchmark in refinement. Stronger coherent chamber warp, unequal apertures, carbonate shoulders, side/rear flared roots, integrated cultivation mats, elongated terrace beds, curved tension membranes and floor-connected supports address the next structural pass. Washery/Digester gain linked process anatomy, without decorative industrial flora.

The opt-in adapter is isolated on the art branch; normal game mappings and economy rules remain unchanged. The next art gate is judging the refined asymmetry and cultivation against the concepts, followed by an authoritative mixed-settlement review. The clean cream terraces and repeated chamber arrangements still warrant scrutiny; technical QA does not waive artistic judgement. Two of six visual housing stages remain unbound to gameplay. Final visual acceptance and domain/stock integration remain open. No further building families start before this benchmark is accepted.
