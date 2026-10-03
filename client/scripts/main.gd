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
var _carrier_views: Array[MeshInstance3D] = []
var _carrier_phase := 0.0
const CARRIER_ROUTE := [
	Vector3(-14, 0.25, 2), Vector3(-8, 0.25, 2), Vector3(-4, 0.25, 2),
	Vector3(0, 0.25, 2), Vector3(4, 0.25, 2), Vector3(4, 0.25, 10)]


func _parse_capture_args() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--capture="):
			_capture_path = arg.get_slice("=", 1)
		elif arg.begins_with("--capture-seconds="):
			_capture_after = arg.get_slice("=", 1).to_float()
		elif arg.begins_with("--capture-speed="):
			speed_index = SPEEDS.find(arg.get_slice("=", 1).to_int())
		elif arg.begins_with("--select="):
			set_meta("select", arg.get_slice("=", 1))
		elif arg == "--autoplay":
			set_meta("autoplay", true)
	if speed_index < 0:
		speed_index = 1


func _ready() -> void:
	_parse_capture_args()
	style = _load_style()
	_build_environment()
	camera_rig = CameraRigScript.new()
	add_child(camera_rig)
	world = WorldViewScript.new()
	add_child(world)
	hud = HudScript.new()
	hud.configure_style(style)
	add_child(hud)
	_build_carrier_views()
	hud.speed_selected.connect(_on_speed_selected)
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
	var root := ProjectSettings.globalize_path("res://")
	result["asset_root"] = root.path_join(result.get("asset_dir", "../assets/blockout/silica_street")).simplify_path()
	result["environment_root"] = root.path_join(result.get("environment_dir", "../assets/blockout/environment")).simplify_path()
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
	if _selected != "" and _inspect_timer <= 0.0:
		_inspect_timer = INSPECT_INTERVAL
		bridge.request("inspect", {"target": _selected}, hud.show_inspection)


func _on_view(reply: Dictionary) -> void:
	_advance_in_flight = false
	if not reply.get("ok", false):
		hud.show_status("Simulation error: " + str(reply.get("reasons", [])), true)
		return
	view = reply["view"]
	world.sync(view)
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
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		_select(_pick(event.position))


func _pick(screen_position: Vector2) -> String:
	var camera: Camera3D = camera_rig.camera
	var from: Vector3 = camera.project_ray_origin(screen_position)
	var to: Vector3 = from + camera.project_ray_normal(screen_position) * 1000.0
	var query := PhysicsRayQueryParameters3D.create(from, to)
	var hit := get_world_3d().direct_space_state.intersect_ray(query)
	if hit and hit.collider and hit.collider.has_meta("entity_view"):
		return hit.collider.get_meta("entity_view").entity_id
	return ""


func _select(entity_id: String) -> void:
	if world.views.has(_selected):
		world.views[_selected].set_selected(false)
	_selected = entity_id
	if world.views.has(_selected):
		world.views[_selected].set_selected(true)
	_inspect_timer = 0.0
	if _selected == "":
		hud.clear_inspection()


func _on_build_requested(building: String) -> void:
	_player_ids += 1
	var id := "%s_p%d" % [building, _player_ids]
	bridge.request("command", {"cmd": {"do": "construct", "building": building, "id": id, "priority": 30}}, _on_command_reply)


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
	bridge.stop()
	get_tree().quit()


# ------------------------------------------------------------------ world dressing
var _sun: DirectionalLight3D
var _env: Environment
var _ground_mat: StandardMaterial3D
const SEASON_TINTS := {
	"bloom": Color(0.16, 0.42, 0.36), "high_water": Color(0.10, 0.33, 0.42),
	"recession": Color(0.30, 0.38, 0.30), "dry": Color(0.42, 0.38, 0.26)}


func _build_environment() -> void:
	_env = Environment.new()
	_env.background_mode = Environment.BG_COLOR
	_env.background_color = Color(0.03, 0.12, 0.14)
	_env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	_env.ambient_light_color = Color(0.55, 0.75, 0.75)
	_env.ambient_light_energy = 0.6
	_env.fog_enabled = true
	_env.fog_light_color = Color(0.05, 0.22, 0.25)
	_env.fog_density = 0.004
	var we := WorldEnvironment.new()
	we.environment = _env
	add_child(we)
	_sun = DirectionalLight3D.new()
	_sun.rotation_degrees = Vector3(-55, 35, 0)
	_sun.shadow_enabled = true
	add_child(_sun)
	var ground := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(260, 260)
	ground.mesh = plane
	_ground_mat = StandardMaterial3D.new()
	_ground_mat.albedo_color = SEASON_TINTS["bloom"]
	ground.material_override = _ground_mat
	add_child(ground)
	_build_environment_assets()


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
	for item in environment.get("routes", []):
		_add_environment_item(item)
	for item in environment.get("scenery", []):
		_add_environment_item(item)


func _build_carrier_views() -> void:
	var mesh: ArrayMesh = ObjLoaderScript.load_mesh(str(style.get("asset_root", "")).path_join("unit_general_carrier_a.obj"))
	if mesh == null:
		return
	for i in range(3):
		var carrier := MeshInstance3D.new()
		carrier.mesh = mesh
		carrier.scale = Vector3.ONE * 0.9
		carrier.set_meta("asset", "unit_general_carrier_a")
		carrier.set_meta("phase_offset", float(i) / 3.0)
		add_child(carrier)
		_carrier_views.append(carrier)


func _update_carrier_views(delta: float) -> void:
	if _carrier_views.is_empty() or view.is_empty():
		return
	var active := false
	for facility in view.get("facilities", {}).values():
		if facility.get("building", "") in ["silicate_pit", "mineral_washery"] and facility.get("status", "") == "running":
			active = true
			break
	var speed := 0.055 if active else 0.012
	_carrier_phase = fmod(_carrier_phase + delta * speed, 1.0)
	for carrier in _carrier_views:
		var t: float = fmod(_carrier_phase + float(carrier.get_meta("phase_offset")), 1.0)
		var scaled := t * (CARRIER_ROUTE.size() - 1)
		var segment: int = min(int(floor(scaled)), CARRIER_ROUTE.size() - 2)
		var local_t: float = scaled - segment
		var a: Vector3 = CARRIER_ROUTE[segment]
		var b: Vector3 = CARRIER_ROUTE[segment + 1]
		carrier.position = a.lerp(b, local_t)
		var direction := b - a
		if direction.length_squared() > 0.001:
			carrier.rotation.y = atan2(direction.x, direction.z)
func _add_environment_item(item: Dictionary) -> void:
	var p: Array = item.get("position", [0, 0, 0])
	_add_environment_mesh(
		str(item.get("asset", "")),
		Vector3(float(p[0]), float(p[1]), float(p[2])),
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
	add_child(instance)


func _apply_season(season: String) -> void:
	_ground_mat.albedo_color = _ground_mat.albedo_color.lerp(SEASON_TINTS.get(season, SEASON_TINTS["bloom"]), 0.2)
