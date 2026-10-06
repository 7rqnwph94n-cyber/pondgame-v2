extends Node3D
## Drawn roads are authoritative domain segments; the preview never changes simulation state.
const PlacementScript = preload("res://scripts/build_placement.gd")
var roads: Dictionary = {}
var terrain: Node3D
var world: Node3D
var active := false
var has_start := false
var start := Vector3.ZERO
var point := Vector3.ZERO
var has_ground := false
var reason := ""
var width := 2.0
var snap_radius := 2.0
var attach_distance := 3.0
var water_margin := 6.5
var max_grade := 0.35
var min_segment := 1.0
var _signature := ""
var _road_mesh: MeshInstance3D
var _preview: MeshInstance3D
var _marker: MeshInstance3D
var _anchor_marker: MeshInstance3D
var _preview_signature := ""
var current_medium := false
var _flow_material: ShaderMaterial
var _organs: Node3D
var _intakes: Node3D
var _ports: MeshInstance3D
var _port_signature := ""


func configure(view_world: Node3D) -> void:
	world = view_world
	_organs = Node3D.new()
	add_child(_organs)
	_intakes = Node3D.new()
	add_child(_intakes)
	_ports = MeshInstance3D.new()
	add_child(_ports)
	terrain = world.terrain
	_road_mesh = MeshInstance3D.new()
	add_child(_road_mesh)
	_preview = MeshInstance3D.new()
	_preview.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(_preview)
	_marker = MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.5
	sphere.height = 1.0
	_marker.mesh = sphere
	_marker.material_override = _material(Color(0.3, 1, 0.55, 0.75), true)
	_marker.hide()
	add_child(_marker)
	_anchor_marker = MeshInstance3D.new()
	var ring := TorusMesh.new()
	ring.inner_radius = 1.1
	ring.outer_radius = 1.45
	_anchor_marker.mesh = ring
	_anchor_marker.material_override = _material(Color("#e1c477"), true)
	_anchor_marker.hide()
	add_child(_anchor_marker)


func sync(spatial: Dictionary) -> void:
	var next: Dictionary = spatial.get("roads", {})
	var signature := JSON.stringify(next)
	if signature != _signature:
		_signature = signature
		roads = next
		var strips: Array = []
		for road in roads.values():
			var points: Array = road.get("points", []) if road is Dictionary else road
			for i in range(points.size() - 1): strips.append([_point(points[i]), _point(points[i + 1])])
		_road_mesh.mesh = _strips_mesh(strips, Color("#69d9bc") if current_medium else Color("#586751"), false)
		_rebuild_organs()
	_sync_ports(spatial.get("placements", {}))
	if _flow_material: _flow_material.set_shader_parameter("clock", float(spatial.get("second", 0)))
	var anchor_data = spatial.get("anchor")
	var anchor = anchor_data.get("position") if anchor_data is Dictionary else anchor_data
	_anchor_marker.visible = anchor is Array and anchor.size() >= 2
	if _anchor_marker.visible: _anchor_marker.position = _point(anchor) + Vector3.UP * 0.12


func begin() -> void:
	active = true
	has_start = false
	_preview_signature = ""


func finish() -> void:
	active = false
	has_start = false
	_preview.hide()
	_marker.hide()


func _point(pair: Array) -> Vector3:
	var x := float(pair[0])
	var z := float(pair[1])
	return Vector3(x, terrain.height_at(x, z) + (0.85 if current_medium else 0.08), z)


func nearest(flat: Vector2) -> Dictionary:
	var best := INF
	var result := {}
	for id in roads:
		var road = roads[id]
		var points: Array = road.get("points", []) if road is Dictionary else road
		for i in range(points.size() - 1):
			var a := Vector2(float(points[i][0]), float(points[i][1]))
			var b := Vector2(float(points[i+1][0]), float(points[i+1][1]))
			var ab := b - a
			if ab.length_squared() <= 0.001: continue
			var candidate := a + ab * clampf((flat - a).dot(ab) / ab.length_squared(), 0, 1)
			var distance := flat.distance_to(candidate)
			if distance < best:
				best = distance
				result = {"point": candidate, "distance": best, "id": id}
	return result


func update_at(camera: Camera3D, screen: Vector2, over_ui: bool) -> void:
	if not active: return
	var ground := PlacementScript.ground_at(camera, screen, terrain)
	has_ground = ground.get("hit", false) and not over_ui
	_preview.visible = has_ground and has_start
	_marker.visible = has_ground
	if not has_ground:
		reason = "Choose ground"
		return
	point = ground["point"]
	var close := nearest(Vector2(point.x, point.z))
	if not close.is_empty() and close["distance"] <= snap_radius:
		point = _point([close["point"].x, close["point"].y])
	_marker.position = point + Vector3.UP * 0.4
	if has_start:
		reason = segment_reason(start, point)
	else:
		reason = ground_reason(point)
		if reason == "" and not roads.is_empty() and (close.is_empty() or close["distance"] > snap_radius):
			reason = "Start on an existing road"
	var colour := Color(0.3, 1, 0.55, 0.6) if reason == "" else Color(1, 0.2, 0.15, 0.6)
	_marker.material_override.albedo_color = colour
	var signature := "%s/%s/%s" % [str(start), str(point), reason]
	if has_start and signature != _preview_signature:
		_preview_signature = signature
		_preview.mesh = _strips_mesh([[start, point]], colour, true)


func ground_reason(candidate: Vector3) -> String:
	if absf(candidate.x) > BasinTerrain.SIZE / 2 - width or absf(candidate.z) > BasinTerrain.SIZE / 2 - width:
		return "Outside the map"
	if not current_medium and terrain.channel_distance_at(Vector2(candidate.x, candidate.z)) < water_margin:
		return "Road cannot cross water"
	for obstacle in world.obstacles:
		var flat := Vector3(candidate.x, obstacle.get_center().y, candidate.z)
		if obstacle.grow(width / 2).has_point(flat): return "Road blocked by natural feature"
	for id in world._slots:
		var local: Vector3 = (candidate - world._slots[id]).rotated(Vector3.UP, -world._rotations.get(id, 0.0))
		var footprint: Vector2 = world._footprints.get(id, Vector2(7, 7))
		if absf(local.x) < footprint.x / 2 + width / 2 and absf(local.z) < footprint.y / 2 + width / 2:
			return "Road overlaps a building or site"
	return ""


func segment_reason(a: Vector3, b: Vector3) -> String:
	var length := Vector2(a.x, a.z).distance_to(Vector2(b.x, b.z))
	if length < min_segment: return "Road is too short"
	if length > 120: return "Use shorter road sections"
	var steps := ceili(length)
	var previous := a
	for i in range(steps + 1):
		var candidate := a.lerp(b, float(i) / steps)
		candidate.y = terrain.height_at(candidate.x, candidate.z)
		var blocked := ground_reason(candidate)
		if blocked != "": return blocked
		if i > 0 and absf(candidate.y - previous.y) / (length / steps) > max_grade:
			return "Road slope too steep"
		previous = candidate
	return ""


func _strips_mesh(strips: Array, colour: Color, overlay: bool) -> ArrayMesh:
	if strips.is_empty(): return null
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for strip in strips:
		var a: Vector3 = strip[0]
		var b: Vector3 = strip[1]
		var flat := Vector2(b.x - a.x, b.z - a.z)
		var side := Vector2(-flat.y, flat.x).normalized() * width / 2
		var steps := maxi(1, ceili(flat.length()))
		for i in range(steps):
			var p := Vector2(a.x, a.z).lerp(Vector2(b.x, b.z), float(i) / steps)
			var q := Vector2(a.x, a.z).lerp(Vector2(b.x, b.z), float(i + 1) / steps)
			var vertices := [p + side, q - side, q + side, p + side, p - side, q - side]
			var uvs := [Vector2(float(i), 1), Vector2(float(i+1), 0), Vector2(float(i+1), 1), Vector2(float(i), 1), Vector2(float(i), 0), Vector2(float(i+1), 0)]
			for n in vertices.size():
				var vertex: Vector2 = vertices[n]
				st.set_uv(uvs[n])
				st.add_vertex(Vector3(vertex.x, terrain.height_at(vertex.x, vertex.y) + (0.85 if current_medium and not overlay else 0.15), vertex.y))
	st.generate_normals()
	st.set_material(_current_material() if current_medium and not overlay else _material(colour, overlay))
	return st.commit()


func _material(colour: Color, overlay: bool) -> StandardMaterial3D:
	var result := StandardMaterial3D.new()
	result.albedo_color = colour
	result.roughness = 0.97
	if overlay:
		result.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		result.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		result.no_depth_test = true
	return result


func configure_rules(rules: Dictionary) -> void:
	snap_radius = float(rules.get("snap_distance", 2))
	attach_distance = float(rules.get("attach_distance", 3))
	water_margin = float(rules.get("road_water_margin", 6.5))
	max_grade = float(rules.get("road_max_grade", 0.35))
	min_segment = float(rules.get("min_segment_m", 1))


func connection_reason(centre: Vector3, yaw: float, footprint: Vector2) -> String:
	if roads.is_empty(): return "Grow a current lane first (T)"
	# Entrance lies on the local +Z face, one metre outside the footprint.
	var entrance := centre + Vector3(0, 0, footprint.y / 2 + 1).rotated(Vector3.UP, yaw)
	var close := nearest(Vector2(entrance.x, entrance.z))
	if close.is_empty() or close["distance"] > attach_distance:
		return "Intake must meet a current lane · R rotate"
	return ""


func footprint_overlaps_road(centre: Vector3, yaw: float, footprint: Vector2) -> bool:
	for road in roads.values():
		var points: Array = road.get("points", []) if road is Dictionary else road
		for i in range(points.size() - 1):
			var a := _point(points[i])
			var b := _point(points[i+1])
			var steps := maxi(1, ceili(Vector2(a.x, a.z).distance_to(Vector2(b.x, b.z)) * 2))
			for n in range(steps + 1):
				var local := (a.lerp(b, float(n) / steps) - centre).rotated(Vector3.UP, -yaw)
				if absf(local.x) < footprint.x / 2 + width / 2 and absf(local.z) < footprint.y / 2 + width / 2: return true
	return false


func pick(camera: Camera3D, screen: Vector2) -> String:
	var best := 7.0
	var result := ""
	for id in roads:
		var road = roads[id]
		var points: Array = road.get("points", []) if road is Dictionary else road
		for i in range(points.size() - 1):
			var a := camera.unproject_position(_point(points[i]))
			var b := camera.unproject_position(_point(points[i+1]))
			var ab := b - a
			if ab.length_squared() < 0.001: continue
			var distance := screen.distance_to(a + ab * clampf((screen - a).dot(ab) / ab.length_squared(), 0, 1))
			if distance < best:
				best = distance
				result = id
	return result


func set_validation(value: String) -> void:
	reason = value
	var colour := Color(0.3, 1, 0.55, 0.6) if reason == "" else Color(1, 0.2, 0.15, 0.6)
	_marker.material_override.albedo_color = colour
	var signature := "%s/%s/%s" % [str(start), str(point), reason]
	if has_start and signature != _preview_signature:
		_preview_signature = signature
		_preview.mesh = _strips_mesh([[start, point]], colour, true)


func _current_material() -> ShaderMaterial:
	if _flow_material != null: return _flow_material
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never;
uniform float clock = 0.0;
void fragment() {
	float edge = pow(max(0.0, 1.0 - abs(UV.y * 2.0 - 1.0)), 2.0);
	float side = UV.y < 0.5 ? 1.0 : -1.0;
	float bead = pow(max(0.0, sin(UV.x * 3.0 - clock * side * 1.7)), 18.0);
	float strands = pow(max(0.0, cos((UV.y - 0.5) * 19.0)), 8.0);
	ALBEDO = mix(vec3(0.12, 0.49, 0.42), vec3(0.58, 0.94, 0.78), bead);
	EMISSION = ALBEDO * bead * 0.55;
	ALPHA = edge * (0.055 + strands * 0.12 + bead * 0.55);
}
"""
	_flow_material = ShaderMaterial.new()
	_flow_material.shader = shader
	return _flow_material


func _rebuild_organs() -> void:
	for child in _organs.get_children(): child.queue_free()
	if not current_medium: return
	var seen := {}
	for road in roads.values():
		var points: Array = road.get("points", [])
		for pair in points:
			var key := str(pair)
			if seen.has(key): continue
			seen[key] = true
			_add_organ(_point(pair), 0.6)


func _add_organ(point_at: Vector3, radius: float) -> void:
	var organ := Node3D.new()
	organ.position = point_at
	_organs.add_child(organ)
	for i in range(5):
		var lobe := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = radius * 0.42
		sphere.height = radius * 1.6
		lobe.mesh = sphere
		lobe.position = Vector3(cos(i * TAU / 5) * radius, -0.32, sin(i * TAU / 5) * radius)
		lobe.rotation.z = 0.25
		var material := _material(Color("#3c967e"), false)
		material.roughness = 0.32
		material.emission_enabled = true
		material.emission = Color("#356c59")
		material.emission_energy_multiplier = 0.25
		lobe.material_override = material
		organ.add_child(lobe)


func _sync_ports(placements: Dictionary) -> void:
	var strips: Array = []
	var ports: Array = []
	for placement in placements.values():
		if placement.get("kind") != "pile" and placement.get("entrance") is Array:
			ports.append({"point": _point(placement["entrance"]), "connected": placement.get("connected", false)})
		if placement.get("kind") == "pile" or not placement.get("connected", false): continue
		var attach = placement.get("attach")
		var entrance = placement.get("entrance")
		if attach is Array and entrance is Array: strips.append([_point(attach), _point(entrance)])
	var signature := str(strips) + str(ports)
	if signature == _port_signature: return
	_port_signature = signature
	for child in _intakes.get_children(): child.queue_free()
	for port in ports:
		var cup := MeshInstance3D.new()
		var ring := TorusMesh.new()
		ring.inner_radius = 0.3
		ring.outer_radius = 0.65
		cup.mesh = ring
		cup.position = port["point"]
		cup.material_override = _material(Color("#73d6b2") if port["connected"] else Color("#f39863"), false)
		_intakes.add_child(cup)
	_ports.mesh = _strips_mesh(strips, Color("#69d9bc"), false)
