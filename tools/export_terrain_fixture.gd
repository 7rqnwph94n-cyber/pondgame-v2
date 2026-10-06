extends SceneTree
## Regenerates tests/fixtures/terrain_parity.json: Godot BasinTerrain heights and channel distances
## on a fixed grid, which the Python rules port (economy/engine/spatial.py Terrain) must match.
## Godot only runs scripts inside the project, so copy it in, run it, and remove the copy:
##   cp tools/export_terrain_fixture.gd client/_export_terrain_fixture.gd
##   godot --headless --path client -s _export_terrain_fixture.gd -- "$PWD/tests/fixtures/terrain_parity.json"
##   rm client/_export_terrain_fixture.gd
func _init() -> void:
	var out: String = OS.get_cmdline_user_args()[0]
	var terrain := BasinTerrain.new()
	terrain.configure_layout(JSON.parse_string(FileAccess.get_file_as_string("res://presentation/map_layout.json")))
	terrain._smooth_channel = terrain._sample_channel()
	var rows := []
	for x in range(-128, 129, 8):
		for z in range(-128, 129, 8):
			var fx := float(x) + 0.37
			var fz := float(z) - 0.61
			rows.append([fx, fz, terrain.height_at(fx, fz), terrain.channel_distance_at(Vector2(fx, fz))])
	var file := FileAccess.open(out, FileAccess.WRITE)
	file.store_string(JSON.stringify({"source": "client/scripts/basin_terrain.gd via tools/export_terrain_fixture.gd", "rows": rows}))
	file.close()
	terrain.free()
	quit()
