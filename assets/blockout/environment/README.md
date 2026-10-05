# Silica Street environment blockouts

Generate with:

```bash
python3 tools/generate_environment_blockouts.py
```

The kit supplies seamless-edge 8 m terrain tiles, modular ledges, three boulder silhouettes, one root landmark, low flow-route modules, seven quiet plant silhouettes and three ground-detail modules. The Carbon Basin extension adds channel banks, a cultivated floodplain shelf, a silica escarpment, methane seep membranes, sulphur vents and depositional delta islands. The riverbank habitat adds three canopy/stature variants of a biomass bower and stranded-bank debris. All assets use metres and +Y up. Route and modular landmark snap points are stored in adjacent anchor JSON files; each bower also exposes a `HarvestAnchor` for a future harvest interaction.

These are camera, placement and navigation-calibration assets. They do not define terrain collision, route capacity or resource access. The bower's harvest anchor is visual preparation, not an economy rule or an active harvest command.
