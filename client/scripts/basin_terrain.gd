class_name BasinTerrain
extends Node3D
## Continuous presentation terrain for the Verdant Carbon Basin.
## It is deliberately independent of simulation legality and yields.

const SIZE := 260.0
const CELLS := 192
const CHANNEL := [
	Vector2(-62, -47), Vector2(-46, -38), Vector2(-36, -19), Vector2(-14, -15),
	Vector2(-4, 5), Vector2(18, 8), Vector2(25, 29), Vector2(55, 43)]
var _smooth_channel: Array[Vector2] = []


func build() -> void:
	_smooth_channel = _sample_channel()
	add_child(_terrain_mesh())
	add_child(_water_mesh())


func height_at(x: float, z: float) -> float:
	var point := Vector2(x, z)
	var channel_distance := _distance_to_path(point)
	var micro := sin(x * 0.17) * 0.16 + cos(z * 0.13) * 0.12 + sin((x + z) * 0.07) * 0.2
	var height := micro
	if channel_distance < 6.2:
		height -= 2.7 * (1.0 - smoothstep(0.0, 6.2, channel_distance))
	elif channel_distance < 17.0:
		height -= 0.45 * (1.0 - smoothstep(6.2, 17.0, channel_distance))
	# Silica escarpment: a broad geological rise, not an isolated prop platform.
	var ridge_face := smoothstep(13.0, 24.0, x)
	var ridge_reach := 1.0 - smoothstep(-34.0, 10.0, z)
	var ridge: float = ridge_face * ridge_reach
	height += ridge * 10.5
	height += ridge * (sin(z * 0.22) * 0.7 + cos(x * 0.31) * 0.35)
	# Sheltered settlement terrace and methane depression.
	height += exp(-pow((x + 19.0) / 19.0, 2.0) - pow((z + 6.0) / 14.0, 2.0)) * 1.1
	height -= exp(-pow((x + 36.0) / 15.0, 2.0) - pow((z - 21.0) / 13.0, 2.0)) * 1.2
	return height


func _terrain_colour(x: float, z: float, height: float) -> Color:
	var point := Vector2(x, z)
	var d := _distance_to_path(point)
	var deep := Color("#17383a")
	var wet := Color("#425b4c")
	var upland := Color("#30483f")
	var colour := deep.lerp(wet, smoothstep(4.8, 12.5, d))
	colour = colour.lerp(upland, smoothstep(12.0, 27.0, d))
	if x > 15.0 and z < 5.0:
		colour = colour.lerp(Color("#68736c"), clamp((x - 15.0) / 35.0, 0.0, 0.75))
	var methane := exp(-pow((x + 36.0) / 17.0, 2.0) - pow((z - 21.0) / 15.0, 2.0))
	colour = colour.lerp(Color("#263b42"), methane * 0.82)
	var sulphur := exp(-pow((x - 44.0) / 14.0, 2.0) - pow((z + 2.0) / 18.0, 2.0))
	colour = colour.lerp(Color("#66543a"), sulphur * 0.75)
	var variation := 0.92 + 0.05 * sin(x * 0.41) * cos(z * 0.37) + 0.03 * sin((x-z) * 0.83)
	colour = Color(colour.r * variation, colour.g * variation, colour.b * variation)
	if height > 5.0:
		colour = colour.lerp(Color("#7c8580"), 0.22)
	return colour


func _terrain_mesh() -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for z_index in range(CELLS):
		for x_index in range(CELLS):
			var x0 := -SIZE * 0.5 + SIZE * float(x_index) / CELLS
			var x1 := -SIZE * 0.5 + SIZE * float(x_index + 1) / CELLS
			var z0 := -SIZE * 0.5 + SIZE * float(z_index) / CELLS
			var z1 := -SIZE * 0.5 + SIZE * float(z_index + 1) / CELLS
			_add_ground_vertex(st, x0, z0)
			_add_ground_vertex(st, x1, z0)
			_add_ground_vertex(st, x1, z1)
			_add_ground_vertex(st, x0, z0)
			_add_ground_vertex(st, x1, z1)
			_add_ground_vertex(st, x0, z1)
	st.index()
	st.generate_normals()
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	float broad = sin(world_position.x * 0.095) * cos(world_position.z * 0.081);
	float grain = sin(world_position.x * 0.73 + world_position.z * 0.41) * 0.5 + 0.5;
	float mottling = 0.84 + broad * 0.08 + grain * 0.07;
	ALBEDO = pow(COLOR.rgb, vec3(1.22)) * mottling * 0.82;
	ROUGHNESS = 0.9 - grain * 0.08;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	st.set_material(material)
	var instance := MeshInstance3D.new()
	instance.mesh = st.commit()
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	return instance


func _add_ground_vertex(st: SurfaceTool, x: float, z: float) -> void:
	var height := height_at(x, z)
	st.set_color(_terrain_colour(x, z, height))
	st.add_vertex(Vector3(x, height, z))


func _water_mesh() -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var half_width := 5.15
	var left: Array[Vector3] = []
	var right: Array[Vector3] = []
	for i in range(_smooth_channel.size()):
		var previous: Vector2 = _smooth_channel[max(0, i - 1)]
		var following: Vector2 = _smooth_channel[min(_smooth_channel.size() - 1, i + 1)]
		var direction := (following - previous).normalized()
		var normal := Vector2(-direction.y, direction.x) * half_width
		var point: Vector2 = _smooth_channel[i]
		left.append(Vector3(point.x + normal.x, -1.45, point.y + normal.y))
		right.append(Vector3(point.x - normal.x, -1.45, point.y - normal.y))
	for i in range(_smooth_channel.size() - 1):
		for vertex in [left[i], right[i + 1], left[i + 1], left[i], right[i], right[i + 1]]:
			st.add_vertex(vertex)
	st.generate_normals()
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
render_mode blend_mix, depth_draw_opaque, cull_disabled;
varying vec3 world_position;
void vertex() {
	world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	VERTEX.y += sin(VERTEX.x * 0.21 + TIME * 0.35) * 0.045 + cos(VERTEX.z * 0.18 - TIME * 0.23) * 0.035;
}
void fragment() {
	float ripple = sin(world_position.x * 0.42 + world_position.z * 0.19 + TIME * 0.45) * 0.5 + 0.5;
	ALBEDO = mix(vec3(0.035, 0.24, 0.27), vec3(0.08, 0.48, 0.51), ripple * 0.35);
	METALLIC = 0.12;
	ROUGHNESS = 0.22;
	ALPHA = 0.92;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	st.set_material(material)
	var instance := MeshInstance3D.new()
	instance.mesh = st.commit()
	return instance


func _distance_to_path(point: Vector2) -> float:
	var nearest := INF
	for i in range(_smooth_channel.size() - 1):
		var a: Vector2 = _smooth_channel[i]
		var b: Vector2 = _smooth_channel[i + 1]
		var ab := b - a
		var t: float = clampf((point - a).dot(ab) / ab.length_squared(), 0.0, 1.0)
		nearest = min(nearest, point.distance_to(a + ab * t))
	return nearest


func _sample_channel() -> Array[Vector2]:
	var result: Array[Vector2] = []
	for i in range(CHANNEL.size() - 1):
		var before: Vector2 = CHANNEL[max(0, i - 1)]
		var start: Vector2 = CHANNEL[i]
		var finish: Vector2 = CHANNEL[i + 1]
		var after: Vector2 = CHANNEL[min(CHANNEL.size() - 1, i + 2)]
		for step in range(7):
			result.append(start.cubic_interpolate(finish, before, after, float(step) / 7.0))
	result.append(CHANNEL[-1])
	return result
