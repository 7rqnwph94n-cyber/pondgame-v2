extends SceneTree
## Export the current rendered terrain/obstacle footprint data for the headless domain.
## godot --headless --path client -s res://tools/export_spatial_geometry.gd -- --out=/absolute/file.json
func _initialize() -> void:
	var main = preload("res://scripts/main.gd").new()
	main._empty_settlement_start = true
	main.style = main._load_style()
	main._build_environment()
	var obstacles: Array = []
	for child in main.get_children():
		if child is MeshInstance3D and child.has_meta("placement_obstacle"):
			var bounds: AABB = child.transform * child.mesh.get_aabb()
			obstacles.append({"position": [bounds.position.x, bounds.position.z], "size": [bounds.size.x, bounds.size.z]})
	var parity: Array = []
	for x in [-65.0, -40.0, -25.0, -20.0, -4.0, 0.0, 18.0, 24.0, 40.0, 80.0]:
		for z in [-55.0, -32.0, -30.0, -15.0, 0.0, 5.0, 20.0, 43.0, 65.0]:
			parity.append({"position": [x, z], "height": main._basin_terrain.height_at(x, z), "channel_distance": main._basin_terrain.channel_distance_at(Vector2(x, z))})
	var footprints := {}
	for definition in main.style.get("buildings", {}):
		var mesh: ArrayMesh = ObjLoader.load_mesh(main.style["asset_root"].path_join(main.style["buildings"][definition] + ".obj"))
		if mesh:
			var footprint := WorldView.mesh_footprint(mesh)
			footprints[definition] = [footprint.x, footprint.y]
	var home: ArrayMesh = ObjLoader.load_mesh(main.style["asset_root"].path_join(main.style["residence_tiers"]["shelter"] + ".obj"))
	if home:
		var footprint := WorldView.mesh_footprint(home)
		footprints["shelter"] = [footprint.x, footprint.y]
	var data := {"source": "client/tools/export_spatial_geometry.gd; current empty Verdant basin", "channel": main.style["environment"]["map"]["channel"], "obstacles": obstacles, "footprints": footprints, "parity": parity}
	var path := ProjectSettings.globalize_path("res://../.worktrees/verdant-spatial-geometry.json")
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="): path = arg.get_slice("=", 1)
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		printerr("Could not export spatial geometry to " + path)
		quit(1)
		return
	file.store_string(JSON.stringify(data, "  ") + "\n")
	file.close()
	print("exported %d obstacles, %d footprints and %d parity points to %s" % [obstacles.size(), footprints.size(), parity.size(), path])
	main.free()
	quit(0)
