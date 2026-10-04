class_name CrossingView
extends Node3D
## A presentation-only living causeway across the nutrient channel.
## Its landings and width come from map_layout.json; it grants no transport access in the domain.

var _terrain: Node3D
var _start := Vector2.ZERO
var _finish := Vector2.ZERO
var _width := 2.8
var _crown_height := 0.0


func build(terrain: Node3D, start: Vector2, finish: Vector2, width: float) -> void:
	_terrain = terrain
	_start = start
	_finish = finish
	_width = width
	_crown_height = maxf(terrain.height_at(start.x, start.y), terrain.height_at(finish.x, finish.y)) + 0.55
	_add_deck()
	_add_edge_roots()
	_add_supports()


func height_at_fraction(t: float) -> float:
	var bank_start: float = _terrain.height_at(_start.x, _start.y) + 0.08
	var bank_finish: float = _terrain.height_at(_finish.x, _finish.y) + 0.08
	if t < 0.20:
		return lerpf(bank_start, _crown_height, smoothstep(0.0, 0.20, t))
	if t > 0.80:
		return lerpf(_crown_height, bank_finish, smoothstep(0.80, 1.0, t))
	return _crown_height


func _point(t: float, lateral: float, lift: float = 0.0) -> Vector3:
	var flat := _start.lerp(_finish, t)
	var tangent := (_finish - _start).normalized()
	var side := Vector2(-tangent.y, tangent.x)
	return Vector3(flat.x + side.x * lateral, height_at_fraction(t) + lift, flat.y + side.y * lateral)


func _add_deck() -> void:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for i in range(20):
		var t0 := float(i) / 20.0
		var t1 := float(i + 1) / 20.0
		var a := _point(t0, _width * 0.5)
		var b := _point(t1, _width * 0.5)
		var c := _point(t1, -_width * 0.5)
		var d := _point(t0, -_width * 0.5)
		for vertex in [a, c, b, a, d, c]:
			st.add_vertex(vertex)
	st.generate_normals()
	st.set_material(_material(Color("#6d8e82"), 0.91))
	var deck := MeshInstance3D.new()
	deck.mesh = st.commit()
	deck.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	add_child(deck)
	_add_shell_plates()


func _add_shell_plates() -> void:
	# Broad overlapping growth plates, not regularly spaced timber-like ties.
	for i in range(6):
		var centre_t := (float(i) + 0.5) / 6.0
		var half_length := 0.070 + 0.010 * sin(float(i) * 1.8)
		var half_width := _width * (0.39 + 0.035 * cos(float(i) * 2.3))
		var t0 := centre_t - half_length
		var t1 := centre_t + half_length
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		var points := [
			_point(t0, -half_width * 0.65, 0.065),
			_point(t0 - 0.012, 0.0, 0.075),
			_point(t0, half_width * 0.65, 0.065),
			_point(centre_t, half_width, 0.095),
			_point(t1, half_width * 0.68, 0.065),
			_point(t1 + 0.012, 0.0, 0.075),
			_point(t1, -half_width * 0.68, 0.065),
			_point(centre_t, -half_width, 0.095),
		]
		var middle := _point(centre_t, 0.0, 0.13)
		for corner in range(points.size()):
			for vertex in [middle, points[(corner + 1) % points.size()], points[corner]]:
				st.add_vertex(vertex)
		st.generate_normals()
		st.set_material(_material(Color("#8aa695") if i % 2 == 0 else Color("#78988a"), 0.86))
		var plate := MeshInstance3D.new()
		plate.mesh = st.commit()
		add_child(plate)


func _add_edge_roots() -> void:
	for side in [-1.0, 1.0]:
		for i in range(10):
			var t0 := float(i) / 10.0
			var t1 := float(i + 1) / 10.0
			var lateral0: float = side * (_width * 0.5 + 0.10 + 0.11 * sin(t0 * TAU * 1.5 + side))
			var lateral1: float = side * (_width * 0.5 + 0.10 + 0.11 * sin(t1 * TAU * 1.5 + side))
			_add_bar(_point(t0, lateral0, 0.22 + 0.08 * sin(t0 * PI)),
				_point(t1, lateral1, 0.22 + 0.08 * sin(t1 * PI)),
				0.23, 0.18, Color("#294e43"))
		for t in [0.20, 0.50, 0.80]:
			var lateral: float = side * (_width * 0.5 + 0.10 + 0.11 * sin(t * TAU * 1.5 + side))
			var top := _point(t, lateral, 0.31)
			var bottom := _point(t, lateral, -0.04)
			_add_bar(bottom, top, 0.18, 0.16, Color("#294e43"))


func _add_supports() -> void:
	for t in [0.30, 0.70]:
		for side in [-1.0, 1.0]:
			var top := _point(t, side * (_width * 0.5 - 0.17), -0.03)
			var bottom := Vector3(top.x, -1.95, top.z)
			_add_bar(bottom, top, 0.23, 0.23, Color("#294b43"))


func _add_bar(start: Vector3, finish: Vector3, width: float, depth: float, colour: Color) -> void:
	var delta := finish - start
	var instance := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(width, depth, delta.length())
	instance.mesh = box
	instance.position = (start + finish) * 0.5
	var forward := delta.normalized()
	var helper := Vector3.UP if absf(forward.dot(Vector3.UP)) < 0.95 else Vector3.RIGHT
	var right := helper.cross(forward).normalized()
	var up := forward.cross(right).normalized()
	instance.basis = Basis(right, up, forward)
	instance.material_override = _material(colour, 0.93)
	add_child(instance)


func _material(colour: Color, roughness: float) -> StandardMaterial3D:
	var result := StandardMaterial3D.new()
	result.albedo_color = colour
	result.roughness = roughness
	return result
