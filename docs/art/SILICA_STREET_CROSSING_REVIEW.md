# Silica Street river crossing — presentation handoff

The Verdant Carbon Basin's carrier loop now crosses its nutrient channel on one authored, two-way causeway. Both approaches lie on dry banks and conform to terrain height. The crossing has a muted shell-plate deck, root-like edges and supports; it is meant to read as a grown piece of infrastructure rather than a flat road laid across water.

The geometry is in `client/presentation/map_layout.json`. `client/scripts/basin_terrain.gd` reads the channel from that layout, while `client/scripts/main.gd` uses the same layout for the rendered route and carrier visuals. The layout is **presentation-only**: it does not alter placement rules, resource access, transport capacity, pathfinding or the simulation bridge.

Evidence captured on the Mac's normal Metal renderer:

- [Playable camera](../milestone_b/captures/verdant_playable_v21_crossing.png)
- [Crossing detail](../milestone_b/captures/verdant_crossing_detail_v05.png)

Verification: 230 Godot client assertions and 12 Python asset/layout checks passed. The route tests check that non-bridge carrier segments stay away from open water and that the same crossing is used in both directions.

Visual sign-off remains open. The causeway solves the floating route, but the wider scene is still a blockout: generic building silhouettes, sparse vegetation away from the river and weak route-landmark hierarchy remain visible. The next art pass should test material, bank integration and approach landmarks from the human play camera, then compare an empty-map view with the target references before expanding the asset count.
