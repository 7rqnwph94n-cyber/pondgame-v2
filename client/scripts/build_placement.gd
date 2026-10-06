extends Node3D
## Cursor preview only: no collision body and no economy command until confirmation.
const ObjLoaderScript = preload("res://scripts/obj_loader.gd")
var footprint := Vector2(7, 7)
var building := ""
var yaw := 0.0
var reason := "Choose ground"
var point := Vector3.ZERO
var has_ground := false
var _ghost: MeshInstance3D
var _footprint: MeshInstance3D
var _material: StandardMaterial3D


func configure(definition: String, style: Dictionary) -> void:
	building = definition
	_material = StandardMaterial3D.new()
	_material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	_material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_material.no_depth_test = true
	_ghost = MeshInstance3D.new()
	var asset: String = style.get("residence_tiers", {}).get("shelter", "") if definition == "shelter" else style.get("buildings", {}).get(definition, "")
	if asset != "": _ghost.mesh = ObjLoaderScript.load_mesh(style.get("asset_root", "").path_join(asset + ".obj"))
	if _ghost.mesh == null:
		var box := BoxMesh.new()
		box.size = Vector3(5, 3, 5)
		_ghost.mesh = box
		_ghost.position.y = 1.5
	footprint = WorldView.mesh_footprint(_ghost.mesh)
	_ghost.material_override = _material
	_ghost.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_ghost)
	_footprint = MeshInstance3D.new()
	var pad := BoxMesh.new()
	pad.size = Vector3(footprint.x, 0.08, footprint.y)
	_footprint.mesh = pad
	_footprint.position.y = 0.12
	_footprint.material_override = _material
	_footprint.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_footprint)
	visible = false


func update_at(camera: Camera3D, screen: Vector2, world: Node3D, over_ui: bool) -> void:
	has_ground = false
	visible = not over_ui
	if over_ui: return
	var origin := camera.project_ray_origin(screen)
	var direction := camera.project_ray_normal(screen)
	# March against the same height function used to generate the rendered terrain.
	var last_distance := 0.0
	for distance in range(0, 1001, 2):
		var sample := origin + direction * float(distance)
		if sample.y <= world.terrain.height_at(sample.x, sample.z):
			var low := last_distance
			var high := float(distance)
			for iteration in range(12):
				var middle := (low + high) * 0.5
				var probe := origin + direction * middle
				if probe.y > world.terrain.height_at(probe.x, probe.z): low = middle
				else: high = middle
			point = origin + direction * ((low + high) * 0.5)
			point.y = world.terrain.height_at(point.x, point.z) + 0.05
			has_ground = true
			break
		last_distance = float(distance)
	visible = has_ground
	reason = world.placement_reason(point, yaw, footprint) if has_ground else "Choose ground"
	position = point
	rotation.y = yaw
	_material.albedo_color = Color(0.3, 1.0, 0.55, 0.45) if reason == "" else Color(1.0, 0.22, 0.18, 0.45)


func rotate_preview(reverse: bool = false) -> void:
	yaw = wrapf(yaw + deg_to_rad(-15.0 if reverse else 15.0), -PI, PI)
