extends Node3D
## Pondgame v2 client shell (Milestone B, ADR 0001).
## Loads the same definitions as the headless economy (via the Python bridge), advances the fixed-step
## simulation under client-side pause and speed controls, renders replaceable placeholder entities through
## EntityView (the presentation adapter), and explains stalls in the inspector.

const SPEEDS := [0, 1, 2, 4, 8, 16, 32]           # simulated seconds per real second
const INSPECT_INTERVAL := 0.5
const SimBridgeScript = preload("res://scripts/sim_bridge.gd")
const WorldViewScript = preload("res://scripts/world_view.gd")
const HudScript = preload("res://scripts/hud.gd")
const CameraRigScript = preload("res://scripts/camera_rig.gd")
const ObjLoaderScript = preload("res://scripts/obj_loader.gd")
const BasinTerrainScript = preload("res://scripts/basin_terrain.gd")
const CrossingViewScript = preload("res://scripts/crossing_view.gd")

var bridge: Node
var world: Node3D
var hud: CanvasLayer
var camera_rig: Node3D
var hello: Dictionary = {}
var view: Dictionary = {}
var speed_index := 1
var _accumulated := 0.0
var _advance_in_flight := false
var _selected := ""
var _inspect_timer := 0.0
var _player_ids := 0
var style: Dictionary = {}
# Capture mode (Codex import review, CI): --capture=<png> [--capture-seconds=N] [--capture-speed=S] [--autoplay]
var _capture_path := ""
var _capture_after := 0.0
var _capture_clock := 0.0
var _capture_focus := Vector2.ZERO
var _capture_zoom := 88.0
var _capture_view_override := false
var _carrier_views: Array[MeshInstance3D] = []
var _empty_settlement_start := false
var _settlement_route_ids := ""
var _follow_carrier := ""
var _context_serial := 0
var _carrier_phase := 0.0
var _carrier_route: Array[Vector3] = []
var _crossing_view: Node3D
var _environment_materials: Dictionary = {}


func _parse_capture_args() -> void:
	var startup := ConfigFile.new()
	if startup.load("res://settings.cfg") == OK:
		_empty_settlement_start = startup.get_value("presentation", "empty_settlement_start", false)
		if _empty_settlement_start: speed_index = 0
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			_capture_path = arg.get_slice("=", 1)
		elif arg.begins_with("--capture-seconds="):
			_capture_after = arg.get_slice("=", 1).to_float()
		elif arg.begins_with("--capture-speed="):
			speed_index = SPEEDS.find(arg.get_slice("=", 1).to_int())
		elif arg.begins_with("--camera-focus="):
			var pair := arg.get_slice("=", 1).split(",")
			if pair.size() == 2:
				_capture_focus = Vector2(pair[0].to_float(), pair[1].to_float())
				_capture_view_override = true
		elif arg.begins_with("--camera-zoom="):
			_capture_zoom = arg.get_slice("=", 1).to_float()
			_capture_view_override = true
		elif arg.begins_with("--select="):
			set_meta("select", arg.get_slice("=", 1))
		elif arg == "--autoplay":
			set_meta("autoplay", true)
		elif arg == "--empty-map":
			set_meta("empty_map", true)
	if speed_index < 0:
		speed_index = 1


func _ready() -> void:
	_parse_capture_args()
	style = _load_style()
	_build_environment()
	camera_rig = CameraRigScript.new()
	add_child(camera_rig)
	if _capture_path != "":
		camera_rig.set_capture_locked(true)
	if _capture_view_override:
		camera_rig.set_review_view(_capture_focus, _capture_zoom)
	if has_meta("empty_map"):
		return
	world = WorldViewScript.new()
	world.configure_terrain(_basin_terrain)
	add_child(world)
	hud = HudScript.new()
	hud.configure_style(style)
	add_child(hud)
	_build_carrier_views()
	hud.speed_selected.connect(_on_speed_selected)
	hud.zoom_requested.connect(camera_rig.zoom_by)
	camera_rig.navigation_started.connect(func(): _follow_carrier = "")
	hud.follow_requested.connect(func(id): _follow_carrier = id)
	hud.autoplay_toggled.connect(func(on): bridge.request("autoplay", {"enabled": on}, func(_r): pass))
	hud.build_requested.connect(_on_build_requested)
	hud.action_requested.connect(_on_action_requested)
	hud.inspect_requested.connect(_select)
	bridge = SimBridgeScript.new()
	_apply_settings(bridge)
	add_child(bridge)
	bridge.connected.connect(_on_connected)
	bridge.failed.connect(func(reason): hud.show_status("Bridge error: " + reason, true))
	hud.show_status("Starting the simulation…", false)
	bridge.start()


func _apply_settings(b: Node) -> void:
	var config := ConfigFile.new()
	if config.load("res://settings.cfg") == OK:
		b.python = config.get_value("bridge", "python", b.python)
		b.port = int(config.get_value("bridge", "port", b.port))
		b.overlays = PackedStringArray(config.get_value("bridge", "overlays", []))
	if OS.has_environment("POND_PYTHON"):
		b.python = OS.get_environment("POND_PYTHON")


func _load_style() -> Dictionary:
	var text := FileAccess.get_file_as_string("res://presentation/asset_map.json")
	var data = JSON.parse_string(text)
	var result: Dictionary = data if typeof(data) == TYPE_DICTIONARY else {}
	var map: Dictionary = result.get("environment", {}).get("map", {})
	var layout_path := "res://presentation/" + str(map.get("layout_file", "map_layout.json"))
	var layout_data = JSON.parse_string(FileAccess.get_file_as_string(layout_path))
	if layout_data is Dictionary:
		for key in layout_data:
			map[key] = layout_data[key]
	var root := ProjectSettings.globalize_path("res://")
	result["asset_root"] = root.path_join(result.get("asset_dir", "../assets/blockout/silica_street")).simplify_path()
	result["environment_root"] = root.path_join(result.get("environment_dir", "../assets/blockout/environment")).simplify_path()
	result["terrain_texture_root"] = root.path_join(result.get("terrain_texture_dir", "../assets/textures/terrain")).simplify_path()
	result["icon_root"] = root.path_join(result.get("icon_dir", "../assets/ui/icons")).simplify_path()
	return result


func _on_connected(reply: Dictionary) -> void:
	hello = reply
	world.configure(style, hello)
	hud.configure(hello)
	hud.show_status("", false)
	if has_meta("autoplay"):
		bridge.request("autoplay", {"enabled": true}, func(_r): pass)
	hud.show_speed(speed_index, SPEEDS[speed_index])
	bridge.request("view", {}, _on_view)
	if has_meta("select"):
		_select(str(get_meta("select")))


func _process(delta: float) -> void:
	if has_meta("empty_map"):
		if _capture_path != "":
			_capture_clock += delta
			if _capture_clock >= _capture_after:
				_capture()
		return
	if not bridge or not bridge.is_ready:
		return
	_update_carrier_views(delta)
	_accumulated += delta * SPEEDS[speed_index]
	if not _advance_in_flight and (_accumulated >= 1.0 or SPEEDS[speed_index] == 0):
		var seconds := int(min(floor(_accumulated), 600))
		if seconds > 0 or view.is_empty():
			_accumulated -= seconds
			_advance_in_flight = true
			bridge.request("advance", {"seconds": seconds}, _on_view)
	if _capture_path != "":
		_capture_clock += delta
		if _capture_clock >= _capture_after and not view.is_empty():
			_capture()
			return
	_inspect_timer -= delta
	if _selected.begins_with("carrier_"):
		hud.show_unit_inspection(_selected, speed_index != 0)
	elif _selected != "" and _inspect_timer <= 0.0:
		_inspect_timer = INSPECT_INTERVAL
		var inspecting := _selected
		bridge.request("inspect", {"target": inspecting}, func(reply):
			if _selected == inspecting: hud.show_inspection(reply))


func _on_view(reply: Dictionary) -> void:
	_advance_in_flight = false
	if not reply.get("ok", false):
		hud.show_status("Simulation error: " + str(reply.get("reasons", [])), true)
		return
	view = reply["view"]
	world.sync(view)
	if _empty_settlement_start: _refresh_settlement_route()
	if world.views.has(_selected):
		world.views[_selected].set_selected(true)
	elif _selected != "" and _selected != "great_work" and not _selected.begins_with("carrier_"):
		_select("")
	hud.show_view(view)
	_apply_season(view.get("season", "bloom"))


func _on_speed_selected(index: int) -> void:
	speed_index = clamp(index, 0, SPEEDS.size() - 1)
	_accumulated = 0.0
	hud.show_speed(speed_index, SPEEDS[speed_index])


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE:
				_on_speed_selected(0 if speed_index != 0 else 1)
			KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6:
				_on_speed_selected(event.keycode - KEY_0)
			KEY_ESCAPE:
				_select("")
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			_context_serial += 1
			_select(_pick(event.position))
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			_open_context(event.position)


func _open_context(position: Vector2) -> void:
	var id := _pick(position)
	_context_serial += 1
	var serial := _context_serial
	_select(id)
	if id == "":
		hud.show_context(position)
	elif id.begins_with("carrier_"):
		hud.show_context(position, {"kind": "carrier", "entity": id})
	elif bridge.is_ready:
		bridge.request("inspect", {"target": id}, func(reply):
			if serial == _context_serial and reply.get("ok", false):
				hud.show_context(position, reply))


func _pick(screen_position: Vector2) -> String:
	var camera: Camera3D = camera_rig.camera
	var from: Vector3 = camera.project_ray_origin(screen_position)
	var to: Vector3 = from + camera.project_ray_normal(screen_position) * 1000.0
	var query := PhysicsRayQueryParameters3D.create(from, to)
	var hit := camera.get_world_3d().direct_space_state.intersect_ray(query)
	if hit and hit.collider and hit.collider.has_meta("entity_view"):
		return hit.collider.get_meta("entity_view").entity_id
	# Building hitboxes take precedence; a visible carrier is the fallback target.
	if _carrier_route.size() < 2: return ""
	var nearest := ""
	var best := 16.0
	for carrier in _carrier_views:
		if not carrier.is_visible_in_tree() or camera.is_position_behind(carrier.global_position): continue
		var distance := camera.unproject_position(carrier.global_position + Vector3.UP).distance_to(screen_position)
		if distance < best:
			best = distance
			nearest = str(carrier.get_meta("carrier_id"))
	return nearest


func _select(entity_id: String) -> void:
	if world.views.has(_selected):
		world.views[_selected].set_selected(false)
	_follow_carrier = ""
	_selected = entity_id
	for carrier in _carrier_views:
		carrier.get_node("Selection").visible = str(carrier.get_meta("carrier_id")) == entity_id
	if world.views.has(_selected):
		world.views[_selected].set_selected(true)
	_inspect_timer = 0.0
	if _selected == "":
		hud.clear_inspection()


func _on_build_requested(building: String) -> void:
	_player_ids += 1
	var id := "%s_p%d" % [building, _player_ids]
	bridge.request("command", {"cmd": {"do": "construct", "building": building, "id": id, "priority": 30}}, func(reply):
		_on_command_reply(reply)
		if reply.get("ok", false): _select(id))


func _on_action_requested(cmd: Dictionary) -> void:
	bridge.request("command", {"cmd": cmd}, _on_command_reply)


func _on_command_reply(reply: Dictionary) -> void:
	if reply.get("ok", false):
		hud.flash(reply.get("info", "ok"), false)
		bridge.request("view", {}, _on_view)
	else:
		hud.flash("Not possible: " + ", ".join(PackedStringArray(reply.get("reasons", []))), true)


func _capture() -> void:
	var path := _capture_path
	_capture_path = ""
	if DisplayServer.get_name() == "headless":
		push_warning("Capture requested with the dummy headless renderer; run without --headless to render pixels")
		bridge.stop()
		get_tree().quit()
		return
	await RenderingServer.frame_post_draw
	var image := get_viewport().get_texture().get_image()
	if image:
		image.save_png(path)
		print("captured %s at sim %s" % [path, view.get("time", "?")])
	if bridge:
		bridge.stop()
	get_tree().quit()


# ------------------------------------------------------------------ world dressing
var _sun: DirectionalLight3D
var _env: Environment
var _ground_mat: StandardMaterial3D
var _basin_terrain: Node3D
const SEASON_TINTS := {
	"bloom": Color(0.16, 0.42, 0.36), "high_water": Color(0.10, 0.33, 0.42),
	"recession": Color(0.30, 0.38, 0.30), "dry": Color(0.42, 0.38, 0.26)}


func _build_environment() -> void:
	var map: Dictionary = style.get("environment", {}).get("map", {})
	_env = Environment.new()
	_env.background_mode = Environment.BG_COLOR
	_env.background_color = Color(0.03, 0.12, 0.14)
	_env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	_env.ambient_light_color = Color(0.55, 0.75, 0.75)
	_env.ambient_light_energy = 0.32
	_env.fog_enabled = not has_meta("empty_map")
	_env.fog_light_color = Color(0.05, 0.22, 0.25)
	_env.fog_density = 0.004
	var we := WorldEnvironment.new()
	we.environment = _env
	add_child(we)
	_sun = DirectionalLight3D.new()
	_sun.rotation_degrees = Vector3(-55, 35, 0)
	_sun.light_energy = 1.15
	_sun.shadow_enabled = true
	add_child(_sun)
	_basin_terrain = BasinTerrainScript.new()
	_basin_terrain.configure_layout(map)
	_basin_terrain.build(style.get("terrain_texture_root", ""))
	add_child(_basin_terrain)
	_build_environment_assets()
	_build_ecological_scatter()
	if not has_meta("empty_map") and not _empty_settlement_start:
		_build_presentation_routes(map)
		_load_carrier_route(map)


func _build_map_geography(map: Dictionary) -> void:
	var channel := _points_from_pairs(map.get("channel", []), 0.08)
	_add_band(channel, 18.0, Color(map.get("floodplain_colour", "#7f7958")), 0.025)
	_add_band(channel, 7.0, Color(map.get("water_colour", "#176b73")), 0.07)

	# Stable start, chemical frontiers and the distant Great Work shelf.
	_add_patch(Vector3(-18, 0.045, -8), Vector2(17, 12), Color(map.get("terrace_colour", "#596c57")), 0.7)
	_add_patch(Vector3(-31, 0.05, 20), Vector2(14, 12), Color(map.get("methane_colour", "#27343f")), 1.9)
	_add_patch(Vector3(39, 0.05, -3), Vector2(11, 18), Color(map.get("sulphur_colour", "#7d6235")), 3.1)
	_add_patch(Vector3(29, 0.04, -18), Vector2(16, 24), Color(map.get("carbonate_colour", "#9d9981")), 4.4)
	_add_patch(Vector3(-35, 0.04, -29), Vector2(13, 9), Color(map.get("carbonate_colour", "#9d9981")), 5.6)

	# Delta fingers make the downstream end read as deposition rather than a road.
	var water := Color(map.get("water_colour", "#176b73"))
	_add_band(_points_from_pairs([[22, 17], [31, 21], [43, 20]], 0.075), 3.2, water, 0.075)
	_add_band(_points_from_pairs([[22, 17], [29, 28], [40, 36]], 0.075), 3.0, water, 0.075)
	_add_band(_points_from_pairs([[25, 19], [36, 28], [47, 30]], 0.075), 2.4, water, 0.075)

	# Low, non-interactive landmark masses establish the map's long-term goals.
	_add_memory_reef(Vector3(-35, 0.35, -29))


func _build_presentation_routes(map: Dictionary) -> void:
	var crossing: Dictionary = map.get("crossing", {})
	if crossing.has("west_landing") and crossing.has("east_landing"):
		_crossing_view = CrossingViewScript.new()
		add_child(_crossing_view)
		var west: Array = crossing["west_landing"]
		var east: Array = crossing["east_landing"]
		_crossing_view.build(_basin_terrain, Vector2(float(west[0]), float(west[1])),
			Vector2(float(east[0]), float(east[1])), float(crossing.get("width", 2.8)))
	_add_ground_route(map)


func _load_carrier_route(map: Dictionary) -> void:
	_carrier_route.clear()
	var pairs: Array = map.get("carrier_route", [])
	for i in range(pairs.size() - 1):
		var a := Vector2(float(pairs[i][0]), float(pairs[i][1]))
		var b := Vector2(float(pairs[i + 1][0]), float(pairs[i + 1][1]))
		var steps := maxi(1, ceili(a.distance_to(b) / 1.4))
		for step in range(steps):
			var t := float(step) / float(steps)
			var flat := a.lerp(b, t)
			var height: float = _basin_terrain.height_at(flat.x, flat.y) + 0.32
			if _crossing_view != null and _is_bridge_segment(a, b, map):
				var west: Array = map["crossing"]["west_landing"]
				var west_point := Vector2(float(west[0]), float(west[1]))
				height = _crossing_view.height_at_fraction(t if a.distance_to(west_point) < 0.1 else 1.0 - t) + 0.32
			_carrier_route.append(Vector3(flat.x, height, flat.y))
	if not pairs.is_empty():
		var last: Array = pairs[-1]
		var flat := Vector2(float(last[0]), float(last[1]))
		_carrier_route.append(Vector3(flat.x, _basin_terrain.height_at(flat.x, flat.y) + 0.32, flat.y))


func _is_bridge_segment(a: Vector2, b: Vector2, map: Dictionary) -> bool:
	var crossing: Dictionary = map.get("crossing", {})
	if not crossing.has("west_landing") or not crossing.has("east_landing"):
		return false
	var west: Array = crossing["west_landing"]
	var east: Array = crossing["east_landing"]
	var w := Vector2(float(west[0]), float(west[1]))
	var e := Vector2(float(east[0]), float(east[1]))
	return (a.distance_to(w) < 0.1 and b.distance_to(e) < 0.1) or (a.distance_to(e) < 0.1 and b.distance_to(w) < 0.1)


func _add_ground_route(map: Dictionary) -> void:
	var pairs: Array = map.get("carrier_route", [])
	var drawn := {}
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(pairs.size() - 1):
		var a := Vector2(float(pairs[i][0]), float(pairs[i][1]))
		var b := Vector2(float(pairs[i + 1][0]), float(pairs[i + 1][1]))
		if _is_bridge_segment(a, b, map):
			continue
		var key := "%s/%s" % [str(a), str(b)]
		var reverse_key := "%s/%s" % [str(b), str(a)]
		if drawn.has(key) or drawn.has(reverse_key):
			continue
		drawn[key] = true
		var direction := (b - a).normalized()
		var side := Vector2(-direction.y, direction.x) * 0.95
		var steps := maxi(1, ceili(a.distance_to(b) / 1.4))
		for step in range(steps):
			var p := a.lerp(b, float(step) / float(steps))
			var q := a.lerp(b, float(step + 1) / float(steps))
			for flat in [p + side, q - side, q + side, p + side, p - side, q - side]:
				st.add_vertex(Vector3(flat.x, _basin_terrain.height_at(flat.x, flat.y) + 0.055, flat.y))
	st.generate_normals()
	st.set_material(_material(Color("#365f59"), 0.94))
	var route := MeshInstance3D.new()
	route.mesh = st.commit()
	route.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(route)


func _points_from_pairs(pairs: Array, height: float) -> Array[Vector3]:
	var points: Array[Vector3] = []
	for pair in pairs:
		if pair is Array and pair.size() >= 2:
			points.append(Vector3(float(pair[0]), height, float(pair[1])))
	return points


func _add_band(points: Array[Vector3], width: float, colour: Color, height: float) -> void:
	for i in range(points.size() - 1):
		var a := points[i]
		var b := points[i + 1]
		var delta := b - a
		var segment := MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(width, 0.08, delta.length() + width * 0.45)
		segment.mesh = box
		segment.position = (a + b) * 0.5
		segment.position.y = height
		segment.rotation.y = atan2(delta.x, delta.z)
		segment.material_override = _material(colour, 0.82)
		add_child(segment)


func _add_patch(center: Vector3, radii: Vector2, colour: Color, phase: float) -> void:
	var zone := MeshInstance3D.new()
	var vertices := PackedVector3Array([Vector3.ZERO])
	var normals := PackedVector3Array([Vector3.UP])
	var indices := PackedInt32Array()
	var edge_count := 18
	for i in range(edge_count):
		var angle := float(i) / float(edge_count) * TAU
		var variation := 0.88 + 0.12 * sin(angle * 3.0 + phase) + 0.06 * cos(angle * 7.0 - phase)
		vertices.append(Vector3(cos(angle) * radii.x * variation, 0, sin(angle) * radii.y * variation))
		normals.append(Vector3.UP)
	for i in range(edge_count):
		indices.append_array(PackedInt32Array([0, i + 1, (i + 1) % edge_count + 1]))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	zone.mesh = mesh
	zone.position = center
	zone.material_override = _material(colour, 0.9)
	add_child(zone)


func _add_memory_reef(center: Vector3) -> void:
	for i in range(7):
		var rib := MeshInstance3D.new()
		var prism := CylinderMesh.new()
		prism.top_radius = 0.35
		prism.bottom_radius = 0.9
		prism.height = 4.0 + float(i % 3)
		prism.radial_segments = 6
		rib.mesh = prism
		var angle := float(i) / 7.0 * TAU
		rib.position = center + Vector3(cos(angle) * 5.0, prism.height * 0.5, sin(angle) * 5.0)
		rib.rotation_degrees.z = 12.0
		rib.material_override = _material(Color("#77729c"), 0.45)
		add_child(rib)


func _add_vent_field(center: Vector3) -> void:
	for offset in [Vector3(-4, 0, -5), Vector3(2, 0, -2), Vector3(-1, 0, 5), Vector3(5, 0, 4)]:
		var vent := MeshInstance3D.new()
		var cone := CylinderMesh.new()
		cone.top_radius = 0.35
		cone.bottom_radius = 1.8
		cone.height = 4.5
		cone.radial_segments = 8
		vent.mesh = cone
		vent.position = center + offset + Vector3(0, cone.height * 0.5, 0)
		vent.material_override = _material(Color("#9b7438"), 0.75, Color("#f0a23a"))
		add_child(vent)


func _material(colour: Color, roughness: float, emission: Color = Color.BLACK) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = colour
	material.roughness = roughness
	if emission != Color.BLACK:
		material.emission_enabled = true
		material.emission = emission
		material.emission_energy_multiplier = 0.35
	return material


func _build_environment_assets() -> void:
	var root: String = style.get("environment_root", "")
	if root == "":
		return
	var environment: Dictionary = style.get("environment", {})
	var tiles: Array = environment.get("terrain_tiles", [])
	if not tiles.is_empty():
		for z in range(-5, 6):
			for x in range(-6, 7):
				var index: int = abs(x * 3 + z * 5) % tiles.size()
				_add_environment_mesh(str(tiles[index]), Vector3(x * 8, 0.015, z * 8), 0.0, 1.0)
	if has_meta("empty_map"):
		for item in environment.get("empty_features", []):
			_add_environment_item(item)
	else:
		for item in environment.get("routes", []):
			_add_environment_item(item)
		for item in environment.get("features", []):
			_add_environment_item(item)
		for item in environment.get("scenery", []):
			_add_environment_item(item)
	for item in environment.get("chemical_ecology", []):
		_add_environment_item(item)
	for item in environment.get("shore_habitat", []):
		_add_environment_item(item)


func _build_ecological_scatter() -> void:
	var root: String = style.get("environment_root", "")
	var clusters := [Vector2(-43, -32), Vector2(-18, -10), Vector2(-2, 5), Vector2(20, 12), Vector2(29, 28)]
	var mat_names := ["vegetation_mat_a", "filter_grove_a", "vegetation_mat_b", "filter_grove_b", "vegetation_mat_c"]
	# Broad mats make the bank ecology read as habitat at strategy-camera scale.
	for cluster_index in range(clusters.size()):
		var centre: Vector2 = clusters[cluster_index]
		for i in range(5):
			var asset: String = mat_names[(i + cluster_index) % mat_names.size()]
			var mesh: ArrayMesh = ObjLoaderScript.load_mesh(root.path_join(asset + ".obj"))
			if mesh == null:
				continue
			var instance := MeshInstance3D.new()
			instance.mesh = mesh
			var angle := float(i) * 2.399 + float(cluster_index) * 0.73
			var radius := 2.5 + float((i * 7) % 8) * 0.74
			var side := -1.0 if i % 2 == 0 else 1.0
			var px := centre.x + cos(angle) * radius + side * 6.2
			var pz := centre.y + sin(angle) * radius - side * 2.1
			instance.position = Vector3(px, _basin_terrain.height_at(px, pz) + 0.08, pz)
			instance.rotation_degrees.y = float((i * 67 + cluster_index * 31) % 360)
			instance.scale = Vector3.ONE * (0.82 + float(i % 3) * 0.13)
			_texture_environment_surfaces(instance)
			add_child(instance)
	# Taller individual organisms break up the mat silhouettes without becoming confetti.
	var accent_names := ["plant_fan_b", "plant_ribbon_b", "plant_branch_b", "plant_cup_a"]
	for cluster_index in range(clusters.size()):
		var centre: Vector2 = clusters[cluster_index]
		for i in range(5):
			var asset: String = accent_names[(i + cluster_index) % accent_names.size()]
			var mesh: ArrayMesh = ObjLoaderScript.load_mesh(root.path_join(asset + ".obj"))
			if mesh == null:
				continue
			var instance := MeshInstance3D.new()
			instance.mesh = mesh
			var angle := float(i) * 2.399 + float(cluster_index) * 0.61
			var side := -1.0 if i % 2 == 0 else 1.0
			var px := centre.x + cos(angle) * (4.5 + i) + side * 5.5
			var pz := centre.y + sin(angle) * (3.5 + i * 0.7) - side * 2.0
			instance.position = Vector3(px, _basin_terrain.height_at(px, pz) + 0.09, pz)
			instance.rotation_degrees.y = float((i * 79 + cluster_index * 43) % 360)
			instance.scale = Vector3.ONE * (1.15 + float(i % 3) * 0.18)
			add_child(instance)
	var rocks := ["boulder_a", "boulder_b", "boulder_c", "detail_pebbles_a"]
	for i in range(24):
		var rock_asset: String = rocks[i % rocks.size()]
		var rock_mesh: ArrayMesh = ObjLoaderScript.load_mesh(root.path_join(rock_asset + ".obj"))
		if rock_mesh == null:
			continue
		var rock_instance := MeshInstance3D.new()
		rock_instance.mesh = rock_mesh
		var rock_x := 18.0 + float((i * 17) % 65)
		var rock_z := -42.0 + float((i * 29) % 72)
		rock_instance.position = Vector3(rock_x, _basin_terrain.height_at(rock_x, rock_z) + 0.06, rock_z)
		rock_instance.rotation_degrees.y = float((i * 83) % 360)
		rock_instance.scale = Vector3.ONE * (0.8 + float(i % 6) * 0.18)
		_texture_environment_surfaces(rock_instance)
		add_child(rock_instance)


func _build_carrier_views() -> void:
	var mesh: ArrayMesh = ObjLoaderScript.load_mesh(str(style.get("asset_root", "")).path_join("unit_general_carrier_a.obj"))
	if mesh == null:
		return
	for i in range(3):
		var carrier := MeshInstance3D.new()
		carrier.mesh = mesh
		carrier.hide()
		carrier.scale = Vector3.ONE * 0.9
		carrier.set_meta("asset", "unit_general_carrier_a")
		carrier.set_meta("carrier_id", "carrier_%d" % (i + 1))
		var ring := MeshInstance3D.new()
		ring.name = "Selection"
		var mesh_ring := TorusMesh.new()
		mesh_ring.inner_radius = 1.0
		mesh_ring.outer_radius = 1.22
		ring.mesh = mesh_ring
		ring.material_override = _material(Color("#78d6dc"), 0.7, Color("#78d6dc"))
		ring.position.y = 0.2
		ring.hide()
		carrier.add_child(ring)
		carrier.set_meta("phase_offset", float(i) / 3.0)
		add_child(carrier)
		_carrier_views.append(carrier)


func _update_carrier_views(delta: float) -> void:
	if _carrier_views.is_empty(): return
	var visible_route := not view.is_empty() and _carrier_route.size() >= 2
	for carrier in _carrier_views: carrier.visible = visible_route
	if not visible_route: return
	var active := false
	for facility in view.get("facilities", {}).values():
		if facility.get("building", "") in ["silicate_pit", "mineral_washery"] and facility.get("status", "") == "running":
			active = true
			break
	var speed := 0.055 if active else 0.012
	var animation_rate := minf(sqrt(float(SPEEDS[speed_index])), 3.0)
	_carrier_phase = fmod(_carrier_phase + delta * speed * animation_rate, 1.0)
	for carrier in _carrier_views:
		var t: float = fmod(_carrier_phase + float(carrier.get_meta("phase_offset")), 1.0)
		var scaled := t * (_carrier_route.size() - 1)
		var segment: int = min(int(floor(scaled)), _carrier_route.size() - 2)
		var local_t: float = scaled - segment
		var a: Vector3 = _carrier_route[segment]
		var b: Vector3 = _carrier_route[segment + 1]
		carrier.position = a.lerp(b, local_t)
		if str(carrier.get_meta("carrier_id")) == _follow_carrier:
			camera_rig.focus_on(carrier.position)
		var direction := b - a
		if direction.length_squared() > 0.001:
			carrier.rotation.y = atan2(direction.x, direction.z)
func _add_environment_item(item: Dictionary) -> void:
	var p: Array = item.get("position", [0, 0, 0])
	var terrain_y: float = _basin_terrain.height_at(float(p[0]), float(p[2])) if _basin_terrain else 0.0
	_add_environment_mesh(
		str(item.get("asset", "")),
		Vector3(float(p[0]), float(p[1]) + terrain_y, float(p[2])),
		float(item.get("rotation_y", 0.0)),
		float(item.get("scale", 1.0)))


func _add_environment_mesh(asset: String, position: Vector3, rotation_y: float, uniform_scale: float) -> void:
	if asset == "":
		return
	var root: String = style.get("environment_root", "")
	var mesh: ArrayMesh = ObjLoaderScript.load_mesh(root.path_join(asset + ".obj"))
	if mesh == null:
		push_warning("Missing environment asset: %s" % asset)
		return
	var instance := MeshInstance3D.new()
	instance.mesh = mesh
	instance.position = position
	instance.rotation_degrees.y = rotation_y
	instance.scale = Vector3.ONE * uniform_scale
	instance.set_meta("asset", asset)
	_texture_environment_surfaces(instance)
	add_child(instance)


func _texture_environment_surfaces(instance: MeshInstance3D) -> void:
	# Texture exposed substrate in world space so vertical faces and ground share geology.
	var surface_textures := {
		"rock": "mineral", "silica_matrix": "mineral", "carbonate": "carbonate",
		"carbonate_shadow": "carbon_clay", "methane": "methane", "methane_film": "methane",
		"methane_rim": "wet", "sulphur_bed": "sulphur", "sulphur_crust": "sulphur",
		"sulphur": "sulphur", "living_green": "fertile", "living_olive": "fertile",
		"flood_silt": "wet",
	}
	for surface_index in range(instance.mesh.get_surface_count()):
		var original := instance.mesh.surface_get_material(surface_index) as StandardMaterial3D
		if original == null or not surface_textures.has(original.resource_name):
			continue
		if _environment_materials.has(original.resource_name):
			instance.set_surface_override_material(surface_index, _environment_materials[original.resource_name])
			continue
		var texture: Texture2D = _basin_terrain.material_texture(surface_textures[original.resource_name])
		if texture == null:
			continue
		var shader := Shader.new()
		shader.code = """
shader_type spatial;
render_mode cull_disabled;
uniform sampler2D ground_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform vec4 surface_tint : source_color;
varying vec3 world_position;
varying vec3 world_normal;
void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize(MODEL_NORMAL_MATRIX * NORMAL);
}
void fragment() {
	vec3 blend = pow(abs(normalize(world_normal)), vec3(4.0));
	blend /= max(0.001, blend.x + blend.y + blend.z);
	vec3 p = world_position / 8.0;
	vec3 colour = texture(ground_texture, p.zy).rgb * blend.x;
	colour += texture(ground_texture, p.xz).rgb * blend.y;
	colour += texture(ground_texture, p.xy).rgb * blend.z;
	ALBEDO = mix(colour, surface_tint.rgb, 0.16);
	ROUGHNESS = 0.92;
}
"""
		var material := ShaderMaterial.new()
		material.shader = shader
		material.set_shader_parameter("ground_texture", texture)
		material.set_shader_parameter("surface_tint", original.albedo_color)
		_environment_materials[original.resource_name] = material
		instance.set_surface_override_material(surface_index, material)


func _apply_season(season: String) -> void:
	if _ground_mat:
		_ground_mat.albedo_color = _ground_mat.albedo_color.lerp(SEASON_TINTS.get(season, SEASON_TINTS["bloom"]), 0.2)


func _refresh_settlement_route() -> void:
	# No prefabricated roads or crossing. Walkers appear only between player-built entities
	# with an entirely dry connecting segment; these are visual walks, not simulated cargo.
	var ids: Array = []
	for id in world.views:
		if world.views[id].kind != "site": ids.append(id)
	ids.sort()
	var signature := ",".join(PackedStringArray(ids))
	if signature == _settlement_route_ids: return
	_settlement_route_ids = signature
	_carrier_route.clear()
	for i in ids.size():
		for j in range(i + 1, ids.size()):
			var a: Vector3 = world.views[ids[i]].position
			var b: Vector3 = world.views[ids[j]].position
			var samples: Array[Vector3] = []
			var dry := true
			var steps := maxi(2, ceili(a.distance_to(b) / 1.0))
			for step in range(steps + 1):
				var point := a.lerp(b, float(step) / steps)
				if not _basin_terrain.has_dry_footprint_at(point.x, point.z):
					dry = false
					break
				point.y = _basin_terrain.height_at(point.x, point.z) + 0.32
				samples.append(point)
			if dry:
				_carrier_route.assign(samples)
				samples.reverse()
				_carrier_route.append_array(samples.slice(1))
				return
