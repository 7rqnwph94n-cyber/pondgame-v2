extends SceneTree
## Headless client tests. Run from the repository root:
##   godot --headless --path client --import          (once, registers class names)
##   godot --headless --path client -s res://tests/run_tests.gd
## Exit code 0 = all passed. The integration test launches the real Python bridge (python3 on PATH or POND_PYTHON).

var failures := PackedStringArray()
var passed := 0
var completed := PackedStringArray()
const TESTS := ["obj_loader", "layout", "bridge"]


func _initialize() -> void:
	_run()


func check(condition: bool, message: String) -> void:
	if condition:
		passed += 1
	else:
		failures.append(message)
		printerr("FAIL: " + message)


func _style() -> Dictionary:
	var data = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/asset_map.json"))
	data["asset_root"] = ProjectSettings.globalize_path("res://").path_join(data["asset_dir"]).simplify_path()
	return data


func _run() -> void:
	test_obj_loader()
	test_layout_is_deterministic_and_stable()
	await test_bridge_round_trip()
	for t in TESTS:
		check(t in completed, "test %s ran to completion (a script error stops a test silently)" % t)
	print("client tests: %d passed, %d failed" % [passed, failures.size()])
	quit(0 if failures.is_empty() else 1)


func test_obj_loader() -> void:
	var style := _style()
	var assets: Array = style["buildings"].values() + style["residence_tiers"].values()
	for asset in assets:
		var path: String = style["asset_root"].path_join(asset + ".obj")
		var mesh := ObjLoader.load_mesh(path)
		var stats: Dictionary = ObjLoader.stats.get(path, {})
		check(mesh != null and stats.get("triangles", 0) > 0 and stats.get("materials", 0) > 0,
			"blockout %s loads as a mesh (%s)" % [asset, str(stats)])
	check(ObjLoader.load_mesh("/no/such/file.obj") == null, "missing OBJ returns null (placeholder fallback)")
	completed.append("obj_loader")


func test_layout_is_deterministic_and_stable() -> void:
	var a := WorldView.new()
	var b := WorldView.new()
	for id in ["x1", "x2", "x3"]:
		check(a.slot_for(id, "food") == b.slot_for(id, "food"), "layout is deterministic for " + id)
	check(a.slot_for("x1", "processing") == a.slot_for("x1", "food"), "an entity keeps its slot")
	check(a.slot_for("x2", "food") != a.slot_for("x3", "food"), "entities in a band do not overlap")
	var terrain := BasinTerrain.new()
	terrain.build()
	var land_view := WorldView.new()
	land_view.configure(_style(), {})
	land_view.configure_terrain(terrain)
	var placed: Array[Vector3] = []
	for band in ["residence", "food", "service", "logistics", "processing", "extraction"]:
		for n in range(3):
			var slot := land_view.slot_for("%s_%d" % [band, n], band)
			check(terrain.has_dry_footprint_at(slot.x, slot.z), "%s slot has dry building footprint" % band)
			check(absf(slot.y - terrain.height_at(slot.x, slot.z)) < 0.1, "%s slot follows terrain" % band)
			for previous in placed:
				check(Vector2(slot.x, slot.z).distance_to(Vector2(previous.x, previous.z)) >= 8.0,
					"%s slot clears existing buildings" % band)
			placed.append(slot)
	land_view.free()
	terrain.free()
	a.free()
	b.free()
	completed.append("layout")


func test_bridge_round_trip() -> void:
	var bridge := SimBridge.new()
	bridge.port = 47000 + randi() % 2000
	if OS.has_environment("POND_PYTHON"):
		bridge.python = OS.get_environment("POND_PYTHON")
	root.add_child(bridge)
	var state := {"hello": {}, "view": {}, "inspect": {}, "failed": ""}
	bridge.connected.connect(func(h): state["hello"] = h)
	bridge.failed.connect(func(r): state["failed"] = r)
	bridge.start()
	var waited := 0.0
	while state["hello"].is_empty() and state["failed"] == "" and waited < 20.0:
		await create_timer(0.05).timeout
		waited += 0.05
	check(state["failed"] == "", "bridge starts and connects (%s)" % state["failed"])
	check(int(state["hello"].get("protocol", -1)) == SimBridge.PROTOCOL, "protocol %d agreed" % SimBridge.PROTOCOL)
	if state["hello"].is_empty():
		bridge.stop()
		return
	bridge.request("autoplay", {"enabled": true})
	bridge.request("advance", {"seconds": 300}, func(r): state["view"] = r.get("view", {}))
	waited = 0.0
	while state["view"].is_empty() and waited < 20.0:
		await create_timer(0.05).timeout
		waited += 0.05
	var view: Dictionary = state["view"]
	check(int(view.get("second", 0)) == 301, "advance steps the fixed-step simulation (second %s)" % str(view.get("second")))
	var world := WorldView.new()
	root.add_child(world)
	world.configure(_style(), state["hello"])
	world.sync(view)
	var expected: int = view.get("facilities", {}).size() + view.get("residences", {}).size()
	for s in view.get("sites", {}).values():
		if s.get("kind") == "building":
			expected += 1
	check(world.views.size() == expected and expected > 0, "one view per entity (%d of %d)" % [world.views.size(), expected])
	check(world.views.has("home_1") and world.views["home_1"].uses_asset() == "res_shelter_cluster_a", "shelters use Codex's blockout")
	check(world.views.has("store_1") and world.views["store_1"].uses_asset() == "store_general_a", "the store uses Codex's blockout")
	bridge.request("inspect", {"target": "great_work"}, func(r): state["inspect"] = r)
	waited = 0.0
	while state["inspect"].is_empty() and waited < 10.0:
		await create_timer(0.05).timeout
		waited += 0.05
	check(state["inspect"].get("kind", "") == "great_work" and not state["inspect"].get("reasons", []).is_empty(),
		"the inspector explains why the Reef is blocked")
	bridge.stop()
	world.queue_free()
	completed.append("bridge")
