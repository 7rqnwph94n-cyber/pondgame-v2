# Silica Street blockout kit

Generated source meshes for the first playable benchmark. Run:

```bash
python3 tools/generate_blockout_assets.py
```

The committed OBJ files use metres, +Y up and a ground pivot at the local origin. Material names match the six-family benchmark kit plus host-rock and dark-organic utility materials. Named anchors live in adjacent `.anchors.json` files because OBJ has no portable empty-node convention.

The kit contains the benchmark Silicate source and payloads, carrier, store, Washery, Shelter, Clean-Flow Node, Waste Collector and Photosynthetic Field. Four additional, silhouette-distinct assets cover the facilities present at game start: First Nursery, Maintenance Organ, Survey Organ and Culture Bed.

These are deliberately low-detail calibration assets. They establish scale, silhouette, pivots, material separation and interaction positions; they do not define collision, capacity or final topology. Convert accepted revisions to GLB after the engine camera review.
