# Verdant Carbon Basin terrain materials

Five authored colour textures drive the continuous terrain shader. They are intentionally presentation-only: biome weights come from map geography, not the economy simulation.

| File | Geography | Visual job |
|---|---|---|
| `fertile_terrace_v01.png` | floodplain and buildable terrace | living silt, microbial traces, carbonate grains |
| `wet_sediment_v01.png` | channel margins | dark retreat silt, damp channels, depositional ripples |
| `silica_escarpment_v01.png` | eastern ridge | laminated stone and glassy silica seams |
| `methane_basin_v01.png` | north-west depression | anoxic sediment, seep traces and microbial film |
| `sulphur_crust_v01.png` | eastern vent field | ochre crust, carbonate rims and vent residue |

All five source bitmaps were generated with OpenAI ImageGen on 2026-10-03 for Pondgame v2, then copied into the repository unchanged at 1254 x 1254 pixels. The originals remain in Codex's generated-image store. They contain no third-party source artwork.

## Prompt recipe

Each image used the same production frame: “seamless square terrain texture for a stylized isometric alien city-builder; entirely filled orthographic ground surface; polished hand-painted 3D strategy-game terrain material readable from a high isometric camera; neutral diffuse lighting; square, top-down, evenly distributed and tileable; no standalone plants, buildings, text, border, vignette, grid, neon colour or lighting hotspot.” The subject, palette and material clauses were changed to the geography described in the table above.

Runtime loading is configured by `client/presentation/asset_map.json`; the textures stay outside the Godot project to avoid generated `.import` metadata.
