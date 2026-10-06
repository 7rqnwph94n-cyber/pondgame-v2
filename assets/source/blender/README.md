# Submerged current organ kit — Blender source

`submerged_current_organs_v01.blend` is the editable Blender 5.2 source for three candidate visual assets:

| Asset | Intended use | Orientation |
|---|---|---|
| `node_current_junction_a` | Controlled-current network junction | Four mouths at ±X, ±Z |
| `node_building_intake_a` | Visible building-to-network intake | Mouth points along +X |
| `node_transfer_fan_a` | Storage/transfer handoff landmark | Two mouths at ±X; three visible cargo cups |

Run `tools/generate_current_organs_blender.py` in Blender background mode to regenerate the OBJ/MTL files in `assets/blockout/environment/` and the contact sheet in `docs/art/renders/`. The scene is Z-up; export is metres, Y-up. Adjacent anchor JSON gives attachment points for future integration. The meshes have no collision or logistics authority.

These are camera-scale candidates, not accepted final models. They intentionally reserve distinct silhouettes for junction, ordinary intake and transfer. Before runtime adoption, test them in the latest submerged map, check node/port attachment under rotation and zoom, and compare against the art bible. In particular, the pale collars may still read too mechanical and should be softened in a later modelling pass if Rich agrees.
