extends SceneTree
## Headless client tests. Run from the repository root:
##   godot --headless --path client --import          (once, registers class names)
##   godot --headless --path client -s res://tests/run_tests.gd
## Exit code 0 = all passed. The integration test launches the real Python bridge (python3 on PATH or POND_PYTHON).

var failures := PackedStringArray()
var passed := 0
var completed := PackedStringArray()
const TESTS := ["obj_loader", "layout", "crossing", "staff_first", "opening_hud", "player_controls", "empty_start_presentation", "placement", "current_habitat", "bridge"]
const CrossingViewScript = preload("res://scripts/crossing_view.gd")


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
	test_crossing_is_the_only_water_route()
	await test_inspector_staff_first_action()
	await test_opening_hud_legibility()
	await test_player_controls()
	test_empty_start_presentation()
	await test_manual_placement()
	test_current_habitat()
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


func test_crossing_is_the_only_water_route() -> void:
	var data = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/map_layout.json"))
	check(data is Dictionary, "presentation map layout parses")
	if not data is Dictionary:
		return
	var terrain := BasinTerrain.new()
	terrain.configure_layout(data)
	terrain.build()
	var crossing: Dictionary = data["crossing"]
	var west := Vector2(float(crossing["west_landing"][0]), float(crossing["west_landing"][1]))
	var east := Vector2(float(crossing["east_landing"][0]), float(crossing["east_landing"][1]))
	check(terrain.channel_distance_at(west) >= 7.0 and terrain.channel_distance_at(east) >= 7.0,
		"crossing landings are on dry banks (%.1f, %.1f m from centre)" % [
			terrain.channel_distance_at(west), terrain.channel_distance_at(east)])
	var crossings := 0
	var pairs: Array = data["carrier_route"]
	for i in range(pairs.size() - 1):
		var a := Vector2(float(pairs[i][0]), float(pairs[i][1]))
		var b := Vector2(float(pairs[i + 1][0]), float(pairs[i + 1][1]))
		var bridge_segment: bool = (a == west and b == east) or (a == east and b == west)
		if bridge_segment:
			crossings += 1
			continue
		var dry := true
		for step in range(21):
			if terrain.channel_distance_at(a.lerp(b, float(step) / 20.0)) < 6.0:
				dry = false
				break
		check(dry, "carrier route segment %d stays out of open water" % i)
	check(crossings == 2, "carriers cross the same authored bridge in both directions")
	check(terrain.channel_distance_at(west.lerp(east, 0.5)) < 5.2, "bridge spans the channel")
	var bridge := CrossingViewScript.new()
	bridge.build(terrain, west, east, float(crossing["width"]))
	check(bridge.height_at_fraction(0.5) > -1.45, "bridge deck clears water surface")
	bridge.free()
	terrain.free()
	completed.append("crossing")


func _action_buttons(hud) -> Dictionary:
	var found := {}
	for b in hud._actions.get_children():
		if not b.is_queued_for_deletion():
			found[b.get_meta("action_label", b.text)] = b
	return found


func test_inspector_staff_first_action() -> void:
	var hud = preload("res://scripts/hud.gd").new()
	root.add_child(hud)
	await process_frame
	var sent := []
	hud.action_requested.connect(func(cmd): sent.append(cmd))
	var starved := {"ok": true, "kind": "facility", "entity": "dredge_1", "building": "sediment_dredge", "status": "running",
		"staffing": 0.33, "labour_priority": 5, "labour_priority_overridden": false,
		"blockers": [{"code": "unstaffed", "params": {"staffing": 0.33, "jobs": {"general": 3}, "labour_priority": 5,
			"can_raise_priority": true}, "text": "staffed 33% of 3 general"}], "reasons": ["staffed 33% of 3 general"]}
	hud.show_inspection(starved)
	var buttons := _action_buttons(hud)
	check(buttons.has("Staff first"), "a starved facility offers Staff first")
	check(not buttons.has("Normal priority"), "no reset offered before an override")
	if buttons.has("Staff first"):
		buttons["Staff first"].pressed.emit()
	check(sent.size() == 1 and sent[0].get("do") == "set_labour_priority" and sent[0].get("target") == "dredge_1"
		and sent[0].get("value") == hud.STAFF_FIRST_RANK, "Staff first sends set_labour_priority %s" % str(sent))
	var raised := starved.duplicate(true)
	raised["labour_priority"] = 3
	raised["labour_priority_overridden"] = true
	raised["blockers"] = []
	raised["reasons"] = []
	hud.show_inspection(raised)
	buttons = _action_buttons(hud)
	check(buttons.has("Normal priority") and not buttons.has("Staff first"), "after the override the inspector offers a reset instead")
	if buttons.has("Normal priority"):
		buttons["Normal priority"].pressed.emit()
	check(sent.size() == 2 and sent[1].get("value") == null, "Normal priority clears the override")
	hud.queue_free()
	completed.append("staff_first")


func test_opening_hud_legibility() -> void:
	var hud = preload("res://scripts/hud.gd").new()
	root.add_child(hud)
	await process_frame
	hud.show_view({"time": "05:00", "season": "bloom", "next_season": "dry", "seconds_to_next_season": 300,
		"population": 24, "food_minutes": 20.0, "builders": "idle", "maintenance_upkeep": "grace",
		"store": {"carbonate": 7, "biomass": 5, "staple": 8},
		"colony_blockers": [{"code": "growth_blocked", "params": {"reason": "no_free_capacity"},
			"text": "no free housing: build a home"}]})
	check(hud._headline_values.has("carbonate") and hud._headline_values["carbonate"].text.contains("7"),
		"Carbonate stock is visible in the opening strip")
	check(hud._headline_values.has("biomass") and hud._headline_values["biomass"].text.contains("5"),
		"Biomass stock is visible in the opening strip")
	check(hud._colony.text.contains("24 !") and hud._colony.tooltip_text.contains("no free housing"),
		"population chip identifies a growth stall and explains it on hover")
	var home := {"ok": true, "kind": "residence", "entity": "home_1", "tier": "shelter", "condition": "normal",
		"population": 8, "capacity": 8, "next_tier": "stable", "services_for_next_tier": {},
		"evolution_workforce_change": {"general": -6, "adapted": 8}, "reasons": []}
	hud.show_inspection(home)
	check(hud._inspector_body.text.contains("-6 General") and hud._inspector_body.text.contains("+8 Adapted"),
		"home inspector warns of the workforce class change before Evolve")
	var buttons := _action_buttons(hud)
	check(buttons.has("Evolve") and buttons["Evolve"].tooltip_text.contains("-6 General"),
		"Evolve action repeats the workforce consequence on hover")
	var service := {"ok": true, "kind": "facility", "entity": "maintenance_1", "building": "maintenance_organ",
		"status": "idle", "staffing": 1.0, "reasons": []}
	hud.show_inspection(service)
	check(hud._inspector_body.text.contains("workers assigned"),
		"idle facility explains that it still occupies workers")
	var competing := {"ok": true, "kind": "site", "entity": "shelter_new", "builds": "shelter",
		"state": "awaiting_materials", "reasons": ["waiting for 1 biomass"], "blockers": [
		{"code": "waiting_input", "params": {"goods": {"biomass": 1}, "consumers": {"biomass": [
		{"entity": "culture_1", "building": "culture_bed", "state": "waiting_input", "per_cycle": 1,
		"held": 0, "outputs": {"staple": 2}}]}}}]}
	hud.show_inspection(competing)
	await process_frame
	check(hud._inspector_body.text.to_lower().contains("culture bed also uses biomass"), "stall identifies the competing recipe")
	check(hud._inspector_body.text.contains("waiting for inputs too"), "waiting competitor is not presented as consuming now")
	check(hud._inspector_body.text.contains("check food reserves"), "pause advice explains food trade-off")
	var selected := {"id": ""}
	hud.inspect_requested.connect(func(id): selected["id"] = id)
	buttons = _action_buttons(hud)
	check(buttons.has("Inspect culture_1"), "consumer can be inspected directly")
	if buttons.has("Inspect culture_1"):
		buttons["Inspect culture_1"].pressed.emit()
	check(selected["id"] == "culture_1", "consumer navigation selects its stable id")
	competing["blockers"][0]["params"]["consumers"] = {}
	hud.show_inspection(competing)
	await process_frame
	check(not _action_buttons(hud).has("Inspect culture_1"), "consumer action disappears after competition ends")
	hud.queue_free()
	completed.append("opening_hud")


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


func test_player_controls() -> void:
	var hud = preload("res://scripts/hud.gd").new()
	root.add_child(hud)
	await process_frame
	hud.configure({"resources": ["biomass", "fired_ceramic"], "buildings": {
		"culture_bed": {"category": "food", "cost": {"biomass": 2}, "jobs": {"general": 3}},
		"shelter": {"category": "residence", "cost": {"biomass": 1}}}})
	var speeds: Array = []
	hud.speed_selected.connect(func(index): speeds.append(index))
	hud._speed_buttons[0].button_pressed = true
	hud._speed_buttons[0].pressed.emit()
	hud._speed_buttons[0].button_pressed = false
	hud._speed_buttons[0].pressed.emit()
	check(speeds == [0, 1], "pause icon toggles both pause and resume")
	check(hud._category_buttons.size() == 8, "eight persistent build categories are available")
	hud.open_build_category("food")
	await process_frame
	var sent: Array = []
	hud.build_requested.connect(func(id): sent.append(id))
	var buttons: Array = hud._catalogue.get_children()
	check(buttons.size() == 1 and buttons[0].get_meta("building") == "culture_bed", "food catalogue excludes homes")
	check(buttons[0].tooltip_text.contains("2 biomass") and buttons[0].tooltip_text.contains("3 General"), "build tooltip includes cost and workforce")
	buttons[0].pressed.emit()
	check(sent == ["culture_bed"] and not hud._build_panel.visible, "single click chooses building and closes catalogue")
	hud.show_context(Vector2.ZERO, {"kind": "facility", "entity": "bed", "building": "culture_bed", "status": "running", "blockers": []})
	check(hud._context_commands.size() == 2 and hud._context_commands[1].get("do") == "pause", "running context offers pause without invalid priority override")
	hud.show_context(Vector2.ZERO, {"kind": "facility", "entity": "bed", "status": "paused"})
	check(hud._context_commands[1].get("do") == "resume", "paused context offers resume")
	hud.show_context(Vector2.ZERO, {"kind": "site", "entity": "site"})
	check(hud._context_commands[1].get("do") == "cancel", "construction context offers cancel")
	hud.show_context(Vector2.ZERO, {"kind": "residence", "entity": "home", "next_tier": "stable", "evolution_workforce_change": {"general": -6, "adapted": 8}})
	check(hud._context_commands[1].get("do") == "evolve", "home context offers evolution")
	check(hud._context.get_item_text(1).contains("-6 General"), "context evolution exposes workforce consequence before click")
	hud.show_context(Vector2.ZERO, {"kind": "carrier", "entity": "carrier_1"})
	check(hud._context_commands[1].get("ui") == "follow", "carrier context offers camera follow rather than fake orders")
	hud._context.hide()
	hud.show_unit_inspection("carrier_1", false)
	check(hud._summary.text.contains("Paused") and hud._inspector_body.text.contains("not simulated"), "carrier inspection explains paused state and domain limits")
	check(not hud._inspector_body.visible, "long inspector explanations are collapsed by default")
	var rig = preload("res://scripts/camera_rig.gd").new()
	root.add_child(rig)
	await process_frame
	var wheel := InputEventMouseButton.new()
	wheel.button_index = MOUSE_BUTTON_WHEEL_UP
	wheel.pressed = true
	rig._unhandled_input(wheel)
	check(rig.camera.size < 88, "mouse wheel zooms inward")
	var pan := InputEventPanGesture.new()
	pan.delta = Vector2(0, -2)
	var before: float = rig.camera.size
	var focus_before: Vector3 = rig._focus
	rig._unhandled_input(pan)
	check(rig._focus != focus_before and rig.camera.size == before, "two-finger trackpad scroll pans the map")
	pan.shift_pressed = true
	rig._unhandled_input(pan)
	check(rig.camera.size < before, "Shift-trackpad scroll zooms inward")
	pan.shift_pressed = false
	pan.alt_pressed = true
	var yaw_before: float = rig._yaw
	rig._unhandled_input(pan)
	check(rig._yaw != yaw_before, "Alt-trackpad scroll rotates")
	var pinch := InputEventMagnifyGesture.new()
	pinch.factor = 1.5
	before = rig.camera.size
	rig._unhandled_input(pinch)
	check(rig.camera.size < before, "trackpad pinch zooms inward")
	rig.zoom_by(0.001)
	check(rig.camera.size == 24, "zoom clamps close range")
	rig.zoom_by(1000)
	check(rig.camera.size == 150, "zoom clamps overview range")
	rig.reset_view()
	check(rig.camera.size == 88, "camera reset restores opening zoom")
	var main = preload("res://scripts/main.gd").new()
	main.camera_rig = rig
	var carrier := MeshInstance3D.new()
	carrier.set_meta("carrier_id", "carrier_1")
	carrier.set_meta("phase_offset", 0.0)
	root.add_child(carrier)
	main._carrier_views.append(carrier)
	main._carrier_route.assign([Vector3.ZERO, Vector3(10, 0, 0)])
	var target: Vector2 = rig.camera.unproject_position(carrier.global_position + Vector3.UP)
	check(main._pick(target) == "carrier_1", "carrier screen target is clickable at overview zoom")
	carrier.hide()
	check(main._pick(target) == "", "hidden carriers cannot take clicks")
	carrier.show()
	main._carrier_route.clear()
	check(main._pick(target) == "", "unconfigured route has no clickable carriers")
	main._carrier_route.assign([Vector3.ZERO, Vector3(10, 0, 0)])
	var building = preload("res://scripts/entity_view.gd").new()
	building.setup("residence", {})
	building.entity_id = "home_hit"
	root.add_child(building)
	await physics_frame
	check(main._pick(target) == "home_hit", "building hit wins over nearby carrier")
	building.free()
	main.view = {"facilities": {}}
	main.speed_index = 0
	main._update_carrier_views(1.0)
	check(main._carrier_phase == 0.0, "pause also freezes carrier route animation")
	main.speed_index = 6
	main._update_carrier_views(1.0)
	check(main._carrier_phase < 0.05, "carrier animation stays readable at 32x")
	main.free()
	carrier.queue_free()
	rig.queue_free()
	hud.queue_free()
	completed.append("player_controls")


func test_empty_start_presentation() -> void:
	var main = preload("res://scripts/main.gd").new()
	main._parse_capture_args()
	check(main._empty_settlement_start and main.speed_index == 0, "playable default starts empty and paused")
	main.style = _style()
	main._build_environment()
	check(main._crossing_view == null and main._carrier_route.is_empty(), "empty opening contains no prebuilt crossing or authored carrier route")
	main._build_carrier_views()
	check(main._carrier_views.size() == 6, "carrier visuals remain available for a later player settlement")
	for carrier in main._carrier_views:
		check(not carrier.visible, "no carrier is visible on the empty starting map")
	main._spatial_enabled = true
	main.view = {"spatial": {"carriers": {"carrier_1": {"position": [-40, 0], "state": "to_target", "distance": 5, "path": [[-45, 0], [-25, 0]], "cargo": {"carbonate": 4}}}}}
	main._update_carrier_views(1)
	check(main._carrier_views[0].visible and is_equal_approx(main._carrier_views[0].position.x, -40), "spatial carrier uses authoritative cargo position without an authored route")
	var stationary: Vector3 = main._carrier_views[0].position
	main._update_carrier_views(30)
	check(main._carrier_views[0].position == stationary, "spatial carrier cannot animate ahead of paused domain state")
	check(not main._carrier_views[1].visible, "carrier without a domain position stays off map")
	main.free()
	completed.append("empty_start_presentation")


class PlacementMainHarness extends "res://scripts/main.gd":
	func _ready() -> void: pass
	func _process(_delta: float) -> void: pass


class PlacementBridgeHarness extends Node:
	var is_ready := true
	var commands: Array = []
	var succeed := true
	func request(method: String, params: Dictionary, callback: Callable = Callable()) -> void:
		if method == "command":
			commands.append(params["cmd"])
			if callback.is_valid(): callback.call({"ok": succeed, "reasons": ["test rejection"] if not succeed else []})


func test_manual_placement() -> void:
	var terrain := BasinTerrain.new()
	terrain.build()
	var world := WorldView.new()
	world.configure(_style(), {"buildings": {"culture_bed": {"category": "food"}}})
	world.configure_terrain(terrain)
	root.add_child(world)
	var point := Vector3(-25, terrain.height_at(-25, -32) + 0.05, -32)
	check(world.placement_reason(point, 0) == "", "clear dry ground accepts a manual footprint")
	check(world.placement_reason(Vector3(140, 0, 0), 0) == "Outside the map", "placement rejects outside terrain bounds")
	check(world.placement_reason(Vector3(-4, 0, 5), 0) == "Too close to water", "placement rejects water and channel margins")
	check(world.placement_reason(Vector3(18, 0, -30), 0) == "Ground too steep", "placement rejects steep escarpment")
	world.reserve_placement("paid_home", point, PI / 4)
	check(world.placement_reason(point + Vector3(5, 0, 0), 0).begins_with("Overlaps"), "rotated footprints block overlapping neighbours")
	check(world.placement_reason(point + Vector3(0, 0, -12), 0) == "", "separate footprint remains placeable")
	world.sync({"sites": {"paid_home": {"kind": "building", "target": "shelter"}}})
	check(world.views["paid_home"].position == point and is_equal_approx(world.views["paid_home"].rotation.y, PI / 4), "site uses player position and rotation")
	world.sync({"residences": {"paid_home": {"tier": "shelter"}}})
	check(world.views["paid_home"].position == point and is_equal_approx(world.views["paid_home"].rotation.y, PI / 4), "commissioned home retains placement")
	world.sync({"residences": {"paid_home": {"tier": "stable"}}})
	check(world.views["paid_home"].position == point and is_equal_approx(world.views["paid_home"].rotation.y, PI / 4), "evolution retains placement")
	world.sync({})
	check(not world._slots.has("paid_home") and world.placement_reason(point, 0) == "", "cancelled or removed site releases footprint")
	world.obstacles.append(AABB(point - Vector3(1, 0, 1), Vector3(2, 2, 2)))
	check(world.placement_reason(point, 0).begins_with("Blocked by rocks"), "natural obstacles block construction")
	world.obstacles.clear()
	var rig := CameraRig.new()
	root.add_child(rig)
	var hud := Hud.new()
	root.add_child(hud)
	var bridge := PlacementBridgeHarness.new()
	var main := PlacementMainHarness.new()
	root.add_child(main)
	main.world = world
	main.camera_rig = rig
	main.hud = hud
	main.bridge = bridge
	main.style = _style()
	await process_frame
	var cursor := InputEventMouseMotion.new()
	cursor.position = rig.camera.unproject_position(point)
	main._input(cursor)
	check(main._placement_screen == cursor.position, "placement tracks event coordinates rather than a stale OS cursor")
	main._on_build_requested("shelter")
	check(bridge.commands.is_empty() and world.views.is_empty(), "choosing a building creates no site and spends no resources")
	check(main._placement.get_children().size() == 3, "preview contains only ghost, footprint and entrance marker, without collision bodies")
	main._placement.rotate_preview()
	check(is_equal_approx(main._placement.yaw, deg_to_rad(15)), "R rotates preview by fifteen degrees")
	main._placement.rotate_preview(true)
	check(is_zero_approx(main._placement.yaw), "Shift-R rotates in reverse")
	main._cancel_placement()
	check(main._placement == null and bridge.commands.is_empty(), "cancel discards preview without a construction command")
	main._on_build_requested("shelter")
	main._confirm_placement(rig.camera.unproject_position(Vector3(-4, terrain.height_at(-4, 5), 5)))
	check(bridge.commands.is_empty() and main._placement != null, "invalid water click cannot submit construction")
	var screen := rig.camera.unproject_position(point)
	main._placement.update_at(rig.camera, screen, world, false)
	check(main._placement.has_ground and main._placement.point.distance_to(point) < 0.15, "cursor ray meets actual terrain height")
	main._placement.update_at(rig.camera, screen, world, true)
	check(not main._placement.visible, "preview hides over HUD controls")
	bridge.succeed = false
	main._confirm_placement(screen)
	check(bridge.commands.size() == 1 and world._slots.is_empty() and main._placement != null, "economy rejection releases reservation and retains preview")
	bridge.succeed = true
	main._confirm_placement(screen)
	check(bridge.commands.size() == 2 and main._placement == null, "valid confirmation issues exactly one ordinary construct command")
	var id: String = bridge.commands[-1]["id"]
	check(world._slots[id].distance_to(point) < 0.15, "confirmed location is reserved before bridge view arrives")
	world.sync({"sites": {id: {"kind": "building", "target": "shelter"}}})
	check(world.views[id].position.distance_to(point) < 0.15, "bridge site appears at confirmed cursor location")
	main.free()
	bridge.free()
	hud.free()
	rig.free()
	world.free()
	terrain.free()
	completed.append("placement")


class CurrentTerrainHarness extends Node3D:
	var submerged := true
	func height_at(_x: float, _z: float) -> float: return 0.0
	func channel_distance_at(_point: Vector2) -> float: return 0.0

class PreviewBridgeHarness extends Node:
	var is_ready := true
	var callbacks: Array[Callable] = []
	var commands: Array = []
	func request(_method: String, payload: Dictionary, callback: Callable) -> void:
		commands.append(payload["cmd"])
		callbacks.append(callback)

func test_current_habitat() -> void:
	var terrain := CurrentTerrainHarness.new()
	var world := WorldView.new()
	world.configure_terrain(terrain)
	var lane = preload("res://scripts/road_view.gd").new()
	lane.configure(world)
	lane.current_medium = true
	lane.sync({"second": 10, "roads": {"r": {"points": [[0,0],[10,0]], "length": 10}}, "placements": {"h": {"kind": "residence", "connected": true, "attach": [5,0], "entrance": [5,-1]}}})
	lane.start = Vector3.ZERO
	lane.point = Vector3(30,0,0)
	var curve: Array = lane.draw_points()
	check(curve.size() > 2 and curve[0] == [0.0,0.0] and curve[-1] == [30.0,0.0], "current curve keeps exact connected endpoints")
	check(float(curve[curve.size()/2][1]) > 0, "current planning has a natural bend rather than a ground-road strip")
	lane.straight = true
	check(lane.draw_points().size() == 2, "straight modifier preserves explicit player control")
	check(lane._road_mesh.mesh.surface_get_material(0) is ShaderMaterial, "current lanes use suspended flow shader rather than opaque dirt")
	check(lane._organs.get_child_count() == 2, "current endpoints grow biological junction organs")
	check(lane._intakes.get_child_count() == 1 and lane._ports.mesh != null, "connected building has a visible intake and branch")
	check(lane.ground_reason(Vector3(20,0,20)) == "", "current lane permits ordinary liquid habitat without blanket channel exclusion")
	check(lane.connection_reason(Vector3(5,0,-5), 0, Vector2(7,7)) == "", "building intake can meet current lane")
	var phase = lane._flow_material.get_shader_parameter("clock")
	lane.sync({"second": 10, "roads": lane.roads, "placements": {}})
	check(lane._flow_material.get_shader_parameter("clock") == phase, "current motion uses simulation time and remains still on pause")
	var habitat = preload("res://scripts/habitat_view.gd").new()
	habitat.configure(terrain, {"light": {"dark_height": -2.5,"full_height":1}, "extraction_zones":[{"center":[20,0],"radius":8}]})
	check(not habitat.overlay.visible and habitat.deposits.get_child_count() == 7, "published mineral exposure is visible while suitability overlay stays optional")
	habitat.toggle()
	check(habitat.overlay.visible, "habitat view exposes published suitability")
	check(habitat.in_zone(Vector2(20,0), {"center":[20,0],"radius":8}) and not habitat.in_zone(Vector2(30,0), {"center":[20,0],"radius":8}), "exposure overlay obeys published bounds")
	var main := PlacementMainHarness.new()
	var bridge := PreviewBridgeHarness.new()
	main.bridge = bridge
	main._preview_last_sent = -1000
	var a := {"do":"construct","building":"shelter","position":[0,0]}
	check(main._validate_preview(a) != "", "unverified preview cannot appear valid")
	check(bridge.commands[0].get("dry_run", false), "preview validates without placing or spending")
	main._preview_last_sent = -1000
	var b := {"do":"construct","building":"shelter","position":[10,0]}
	main._validate_preview(b)
	bridge.callbacks[0].call({"ok":true})
	check(not main._preview_ready, "late reply for old cursor location cannot approve a new placement")
	bridge.callbacks[1].call({"ok":false,"reasons":["spatial:not_connected"]})
	check(main._validate_preview(b).contains("connected current network"), "authoritative disconnection remains blocked in preview")
	var home := EntityView.new()
	home.setup("residence", _style())
	home.set_entity_identity("grown", "stable")
	check(home.uses_asset() == "res_shelter_cluster_a" and home._body.get_child_count() == 3, "evolved home retains organic shelter and adds visible living chambers")
	home.free()
	main.free()
	bridge.free()
	habitat.free()
	lane.free()
	world.free()
	terrain.free()
	completed.append("current_habitat")
