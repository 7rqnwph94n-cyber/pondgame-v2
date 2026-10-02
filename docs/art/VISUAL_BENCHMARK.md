# Pondgame v2 — Verdant visual benchmark specification v0.1

## Purpose

Before bulk art production, prove that the old Pondlife visual identity can express the new chemistry-driven economy at normal play scale.

The benchmark is one composed basin corner containing:

- a sunlit silt clearing;
- a ledge/root boundary;
- one Photosynthetic Field;
- one Silicate Outcrop;
- one General Store;
- one Shelter Cluster;
- one Mineral Washery;
- three General carriers moving Silicate through the chain;
- Bloom and Dry seasonal presentations.

It is a visual/integration test, not a complete gameplay scene.

The implementation-ready scene envelope, coordinates, relative footprints and state-to-interface contract are defined in `SILICA_STREET_PRODUCTION_PACKAGE.md`. This document remains the visual QA specification.

## Story of the scene

Raw glassy fragments are cut from a Silicate Outcrop at the darker edge of the basin. Carriers follow a low living route to an open General Store and Mineral Washery. The Washery takes cloudy fragments through porous membranes and deposits pale Prepared Silica. A nearby Shelter Cluster and Photosynthetic Field show the contrast between inhabited/agricultural and industrial space.

The player should understand that story within five seconds at Settlement view without opening UI.

## Composition

- Central 60%: quiet silt clearing and readable movement corridor.
- Rear/left: ledge and root create a dark Silicate landmark.
- Centre: Store and Washery form a small industrial pair.
- Front/right: residence and field occupy cleaner, brighter ground.
- Boundary plants cluster around rocks; no uniform scatter.
- The industrial pair must not silhouette-merge from the default camera.
- Carriers remain visible against route and substrate at every tested yaw.

## Required assets

Use P0 entries from `VERTICAL_SLICE_ASSET_MANIFEST.md`:

- `env_basin_benchmark`;
- `patch_silicate_a`;
- `farm_photosynthetic_a`;
- `unit_general_carrier_a`;
- `res_shelter_cluster_a`;
- `proc_mineral_washery_a`;
- `store_general_a`;
- `payload_raw_silicate_a`;
- `payload_prepared_silica_a`.

Reuse candidates are listed in `ASSET_REUSE_AUDIT.md` but remain staged until approved.

## Demonstrated state sequence

The review scene must be able to play a deterministic 40-second loop:

1. Silicate Outcrop rich; Washery awaiting input.
2. Carrier receives Raw Silicate payload.
3. Carrier moves and delivers to General Store/Washery.
4. Washery input chamber fills.
5. Washery processes with visible cloudy flow and membrane motion.
6. Prepared Silica appears on output shelf.
7. Second carrier collects output.
8. Outcrop moves to worked state.
9. Scene changes from Bloom to Dry presentation.
10. Field closes/stresses, clean brightness reduces and distant motes change.

State must be driven through the presentation adapter or a temporary adapter-compatible harness—not bespoke animation timing embedded in the benchmark scene.

## Functional reads to test

At Settlement view, without labels:

- Which formation is extractable?
- Which building stores goods?
- Which building transforms goods?
- Which area is residential?
- Which area is cultivated?
- Which organism is carrying something?
- Which side is cleaner/more desirable?
- Has the season changed?

If two or more answers rely only on colour or UI, revise the silhouettes/state presentation.

## Camera matrix

Capture:

- yaw 0°, 45°, 90°, 135°, 180°, 225°, 270°, 315°;
- low, default and high pitch at default yaw;
- near, Settlement and Territory zoom;
- neutral diagnostic lighting and final lighting;
- Bloom and Dry.

Minimum contact sheet: 18 labelled views. Include a greyscale Settlement view.

## Material checks

- Shell, membrane, raw Silicate, Prepared Silica, silt, carbonate/rock and Resin-like amber must remain distinct.
- Prepared Silica must visibly derive from Raw Silicate.
- Amber activity emission cannot be confused with selection or warning.
- Translucent membranes must not disappear or sort incorrectly across views.
- No baked lighting contradicts the directional light.
- Assets look acceptable with bloom and fog disabled.

## Scale and anchor checks

- Establish one shared authoring-to-game scale.
- Confirm ground pivots with no baked world offset.
- Confirm Label, FX, input, output and payload anchors.
- Carried goods sit inside/on anatomy rather than float beside it.
- Worker contact points align with Outcrop, Store and Washery.
- Presentation bounds do not define collision automatically.
- Roof and rear faces are intentional.

## Animation checks

- Carrier does not slide during move.
- Payload changes posture or buoyancy.
- Deliver action contacts the destination.
- Washery progress has a clear beginning, middle and completion.
- Building remains mostly stable; no whole-mesh pumping.
- Field stress is slower/closed, not merely red-tinted.
- Loops have matching start/end poses.
- Unsupported actions fall back to idle safely.

## Performance scene

After visual approval, duplicate to representative density:

- 50 carriers;
- 30 buildings/processors using shared materials;
- 120 environment props;
- 12 active patch/farm state effects;
- 40 visible payloads.

Record:

- Godot version and renderer;
- hardware;
- resolution;
- average/worst frame time;
- draw calls;
- visible objects;
- VRAM/memory where available;
- effect/material features disabled during diagnosis.

Do not invent a target FPS without agreeing on target hardware. The purpose is to find dominant costs before mass production.

## Deliverables

- Blender sources and texture sources;
- GLBs and Godot presentation wrappers;
- asset-manifest records;
- deterministic review scene;
- labelled camera contact sheet;
- Bloom/Dry comparison;
- 40-second state capture if tooling permits;
- import/validation log;
- performance record;
- short QA report listing limitations;
- Rich approval or requested changes.

## Acceptance gate

Benchmark passes only when:

1. Rich approves the overall look.
2. All functional-read questions pass at Settlement view.
3. Rotation reveals no unfinished backs/roofs or unacceptable occlusion.
4. The adapter drives state without gameplay-specific art hacks.
5. Legacy and new elements share one material/scale language.
6. Godot imports without missing external dependencies.
7. Representative density identifies no unaddressed production blocker.

Until then, do not start the full processor, residence or morphology roster.
