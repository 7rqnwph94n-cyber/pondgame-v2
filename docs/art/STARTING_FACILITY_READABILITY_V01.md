# Starting-facility silhouettes — v0.1

The default opening view previously rendered First Nursery, Maintenance Organ, Survey Organ and Culture Bed as the same category placeholders. Those four buildings are present at simulation second zero, so the repeated cones made the starting settlement hard to parse before any player action.

This blockout pass supplies distinct meshes in the established Verdant material family:

- First Nursery: a sheltered radial brood bowl with pale canopy ribs.
- Maintenance Organ: a low three-armed repair node with a protected enzyme core.
- Survey Organ: a narrow branching sensor mast, deliberately taller than its neighbours.
- Culture Bed: three compact fermentation troughs, contrasting with the broad Photosynthetic Field.

The source is `tools/generate_blockout_assets.py`; `client/presentation/asset_map.json` selects the meshes. The change is presentation-only. It does not add jobs, recipes, capacity, build options or map constraints.

[Default playable-camera capture](../milestone_b/captures/verdant_playable_v22_starting_facilities.png)

At ordinary zoom the four no longer read as the same cone, but the scene is still blockout-quality. The Nursery and Maintenance Organ need stronger value separation from nearby shelters, and the Industry chain itself still needs a deliberate five-second read test with active extraction and processing. Rich's visual acceptance remains open.
