# Strict road transport — integration in progress

Rich's requirement: “no, all buildings must connect”.

The optional `spatial_roads_v1.json` overlay follows the slice and empty-start overlays. It requires a player road before construction and a connected entrance for every building. Removing its route blocks deliveries, construction, workforce and services. The first road establishes the supply anchor; an anchor without a road does not connect buildings. Roads are currently free instant dirt paths.

Six carriers move finite loads between the supply anchor and building depots. Construction, production inputs/outputs and household provisions use delivered goods. Cargo and salvage remain in custody when connections are removed. Carrier meshes display domain positions and stop when simulation time stops. Upkeep, trade, research and Great Work accounting remain at the central anchor.

The client has a road icon and T shortcut: click a start, then successive endpoints; right-click/Escape finishes. Building entrances are marked on placement ghosts. R rotates them toward roads. Right-click a road to inspect or remove it.

This overlay is not the default playable launch yet. Remaining release checks: authoritative preview integration; shared natural-obstacle/mesh footprint data; full spatial opening/budget acceptance; native click-through; independent review. The client geometry exporter is `client/tools/export_spatial_geometry.gd`.

Regression evidence: 203 Python tests and 319 Godot client assertions. Native QA is temporarily unavailable while the Mac is locked. These counts cover the implemented domain and existing client regression; they do not establish full spatial opening balance.
