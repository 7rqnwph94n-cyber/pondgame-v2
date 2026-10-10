# Pondlife art direction — v0.1

30 September 2026. User-confirmed direction: freely rotating camera, fantastical underwater world, three factions sharing the implemented role/building roster. This document is a production brief, not a claim that new models or faction mechanics exist.

## Visual thesis

A miniature civilisation grown from living glass, coral, shell and mineral, set within a substantial underwater landscape. Preserve the artstyle sheets' jewel eyes, translucent-looking membranes, teal shell surfaces and luminous internal organs. Translate the sheets into fully rounded designs with convincing backs, sides and undersides where visible. Use the supplied gameplay references for terrain mass, planted composition, open ground and depth; create original forms rather than reproduce their specific assets.

The sheets are concept references. Their busy surface detail, front-facing compositions and painted backgrounds are not a production specification. Simplify small detail into readable colour masses. Build glossy opaque shells with selectively translucent membranes; avoid making every organism an overlapping stack of transparent surfaces.

## Faction grammar

| Faction | Shape | Surface | Proposed palette | Motion |
|---|---|---|---|---|
| The Verdant Bloom | Rounded buds, branching lobes, opening cups | Smooth membranes, living coral, soft mineral inclusions | Deep teal #174B50, leaf green #75B96B, amber #FFC05A, pale mint #C3EDC2 | Swell, unfurl, gently pulse |
| The Strata Wardens | Broad bases, layered plates, blunt facets, reinforced ribs | Sedimentary shells, matte stone, polished silica seams | Blue slate #304556, mineral violet #77729C, ice cyan #8CE0DE, chalk #D5DFD8 | Deliberate weight shifts and controlled plate movement |
| The Driftpack | Swept fins, hooked ribs, segmented tapered shells | Cured chitin, flexible membranes, worn ridges | Deep plum #382E4C, coral #EF7967, sea blue #398A9C, restrained lime #C8DD73 | Fin ripples, quick banking, trailing feelers |

Palette values are starting swatches, to be judged under the game lighting. Reserve the brightest colours for small focal points. Faction colour occupies large enough areas to read at zoom, while ownership/selection colours remain separate channels. Distinguish factions through anatomy as well as hue, and test in greyscale.

Shared functional cues survive all faction treatments: a Gatherer has collecting cups; a Forager has a larger cargo abdomen; a Scout is long and narrow. Bloom expresses collecting cups as buds, Strata as plated scoops and Driftpack as swept chitin baskets. Building roles likewise share a readable function, not an identical recoloured mesh.

User-proposed mechanics: Bloom favours economy/regrowth and cheap early construction; Strata favours durability/fortification at slower economic pace; Driftpack favours movement and current use. Exact multipliers, combat and raiding implementation remain Claude's gameplay responsibility. Art does not change balance values.

## Environment composition

Establish a legible ground plane, then place substantial ledges and boulders, then plant in clusters around those forms. Preserve generous open clearings for settlement and movement. As a benchmark composition starting point, keep roughly two-thirds of the central playable ground visually quiet and concentrate detail around boundaries and landmarks. This is a composition target, not a gameplay obstacle rule.

Avoid evenly distributing every prop. Use a large anchor rock, smaller supporting rocks, a planted transition and a clean edge into the clearing. Assemble varied habitats from reusable parts. Tall props need useful silhouettes from all sides and must not repeatedly hide units when the camera rotates.

Rock Pool uses compact exposed ledges, sand pockets and bright cup gardens. Pond uses broad silt shelves, roots and taller frond masses. Darkness and saturation fall into the distance; interactive objects retain contrast. Neutral terrain should not look claimed by a faction.

Lighting establishes volume: broad cool underwater fill, soft directional illumination and local emission accents. Caustics should animate gently across surfaces without becoming the dominant pattern. Bloom, fog, particles and shafts support the models; they cannot substitute for terrain geometry or contact shadows. Review first without post-processing, then with the intended effects.

## Readability and camera

The current camera supports 360-degree yaw, pitch from 20 to 85 degrees and orthographic size 200–1600 (default 720). Test eight yaw angles, low/default/high pitch and near/default/far zoom. At default zoom a player should identify faction and role from silhouette and a few colour masses. At maximum zoom-out, units must at least retain clear presence and ownership; detailed role information can rely on UI.

No camera-facing scenery cards for dominant forms. Fine plant fronds may use carefully arranged geometry/alpha-cutout planes if they survive rotation. Buildings require intentional roof designs because high camera angles expose them. Use short and broad forms around paths, reserving tall landmarks for places where occlusion is manageable.

## Production responsibilities

Codex: art direction, concepts, modelling/material pipeline, library organisation, visual QA and explicit asset handoffs. Claude: game logic, faction balance, spawning, navigation, resource state wiring and visual-adapter integration. User: visual direction decisions at benchmark milestones.

Use Blender source files plus exported GLB assets and Godot presentation scenes. Blender.app is present locally; its automation/export pipeline has not yet been exercised for this work. Image generation may support concepts and textures, but generated pictures are not finished 3D assets. Organic topology, rigging and animation need direct validation, and complex units may need additional modelling iteration. Quality is judged in-engine, not inferred from concept art.

Immediate next production milestone: the environment benchmark defined in ASSET_INVENTORY.md. Create one coherent playable corner before mass production. The full target is both biome kits and all three faction treatments of the shared roster. Lake, River, Sea and spacefaring assets remain future scope, with reusable visual grammar rather than speculative production now.
