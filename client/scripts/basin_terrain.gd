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
var _textures: Dictionary = {}


func build(texture_root: String = "") -> void:
	_smooth_channel = _sample_channel()
	_textures = _load_terrain_textures(texture_root)
	add_child(_terrain_mesh())
	add_child(_shoreline_mesh())
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


func _terrain_weights(x: float, z: float) -> Color:
	var point := Vector2(x, z)
	var d := _distance_to_path(point)
	var wet := (1.0 - smoothstep(5.4, 18.0, d)) * 0.92
	var mineral := smoothstep(10.0, 42.0, x) * (1.0 - smoothstep(-24.0, 16.0, z))
	mineral *= 0.88
	var methane := exp(-pow((x + 36.0) / 18.0, 2.0) - pow((z - 21.0) / 16.0, 2.0)) * 0.96
	var sulphur := exp(-pow((x - 44.0) / 15.0, 2.0) - pow((z + 2.0) / 19.0, 2.0)) * 0.96
	return Color(wet, mineral, methane, sulphur)


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
uniform sampler2D fertile_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D wet_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D mineral_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D methane_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D sulphur_texture : source_color, repeat_enable, filter_linear_mipmap;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	vec2 terrain_uv = world_position.xz / 25.0;
	vec2 broken_uv = vec2(terrain_uv.y * 0.73 + terrain_uv.x * 0.19, -terrain_uv.x * 0.71 + terrain_uv.y * 0.23);
	vec3 fertile = mix(texture(fertile_texture, terrain_uv).rgb, texture(fertile_texture, broken_uv).rgb, 0.16);
	vec3 wet = mix(texture(wet_texture, terrain_uv).rgb, texture(wet_texture, broken_uv).rgb, 0.13);
	vec3 mineral = mix(texture(mineral_texture, terrain_uv).rgb, texture(mineral_texture, broken_uv).rgb, 0.12);
	vec3 methane = mix(texture(methane_texture, terrain_uv).rgb, texture(methane_texture, broken_uv).rgb, 0.10);
	vec3 sulphur = mix(texture(sulphur_texture, terrain_uv).rgb, texture(sulphur_texture, broken_uv).rgb, 0.12);
	vec4 weights = max(COLOR, vec4(0.0));
	float fertile_weight = max(0.08, 1.0 - dot(weights, vec4(1.0)));
	float total = fertile_weight + dot(weights, vec4(1.0));
	vec3 surface = fertile * fertile_weight + wet * weights.r + mineral * weights.g + methane * weights.b + sulphur * weights.a;
	float broad = sin(world_position.x * 0.071) * cos(world_position.z * 0.063);
	ALBEDO = surface / total * (0.92 + broad * 0.055);
	ROUGHNESS = mix(0.91, 0.72, weights.b * 0.45 + weights.r * 0.2);
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	for texture_name in ["fertile", "wet", "mineral", "methane", "sulphur"]:
		if _textures.has(texture_name):
			material.set_shader_parameter(texture_name + "_texture", _textures[texture_name])
	st.set_material(material)
	var instance := MeshInstance3D.new()
	instance.mesh = st.commit()
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	return instance


func _add_ground_vertex(st: SurfaceTool, x: float, z: float) -> void:
	var height := height_at(x, z)
	st.set_color(_terrain_weights(x, z))
	st.set_uv(Vector2(x, z) / 25.0)
	st.add_vertex(Vector3(x, height, z))


func _shoreline_mesh() -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for side_value in [-1.0, 1.0]:
		var side: float = side_value
		var inner: Array[Vector3] = []
		var outer: Array[Vector3] = []
		for i in range(_smooth_channel.size()):
			var previous: Vector2 = _smooth_channel[max(0, i - 1)]
			var following: Vector2 = _smooth_channel[min(_smooth_channel.size() - 1, i + 1)]
			var direction: Vector2 = (following - previous).normalized()
			var normal: Vector2 = Vector2(-direction.y, direction.x) * side
			var point: Vector2 = _smooth_channel[i]
			var bank_wobble := sin(float(i) * 1.73 + side) * 0.65 + cos(float(i) * 0.57) * 0.35
			var inner_2d: Vector2 = point + normal * (5.0 + bank_wobble * 0.18)
			var outer_2d: Vector2 = point + normal * (8.5 + bank_wobble * 0.82)
			inner.append(Vector3(inner_2d.x, height_at(inner_2d.x, inner_2d.y) + 0.055, inner_2d.y))
			outer.append(Vector3(outer_2d.x, height_at(outer_2d.x, outer_2d.y) + 0.045, outer_2d.y))
		for i in range(_smooth_channel.size() - 1):
			for vertex in [inner[i], outer[i + 1], inner[i + 1], inner[i], outer[i], outer[i + 1]]:
				st.add_vertex(vertex)
	st.generate_normals()
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
uniform sampler2D wet_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D fertile_texture : source_color, repeat_enable, filter_linear_mipmap;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	vec2 bank_uv = world_position.xz / 17.0;
	vec3 wet = texture(wet_texture, bank_uv).rgb;
	vec3 fertile = texture(fertile_texture, bank_uv * 0.81 + vec2(0.17, -0.23)).rgb;
	float deposit = sin(world_position.x * 0.44 + world_position.z * 0.31) * 0.5 + 0.5;
	ALBEDO = mix(wet * 0.79, fertile * 0.76, deposit * 0.23);
	ROUGHNESS = 0.78;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	if _textures.has("wet"):
		material.set_shader_parameter("wet_texture", _textures["wet"])
	if _textures.has("fertile"):
		material.set_shader_parameter("fertile_texture", _textures["fertile"])
	st.set_material(material)
	var instance := MeshInstance3D.new()
	instance.mesh = st.commit()
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return instance


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
		var t0 := float(i) / float(_smooth_channel.size() - 1) * 12.0
		var t1 := float(i + 1) / float(_smooth_channel.size() - 1) * 12.0
		var vertices := [left[i], right[i + 1], left[i + 1], left[i], right[i], right[i + 1]]
		var uvs := [Vector2(t0, 0), Vector2(t1, 1), Vector2(t1, 0), Vector2(t0, 0), Vector2(t0, 1), Vector2(t1, 1)]
		for vertex_index in range(vertices.size()):
			st.set_uv(uvs[vertex_index])
			st.add_vertex(vertices[vertex_index])
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
	float small_ripple = sin(world_position.x * 0.58 + world_position.z * 0.33 + TIME * 0.52) * 0.5 + 0.5;
	float long_flow = sin(UV.x * 3.7 - TIME * 0.36 + sin(UV.x * 0.7) * 1.8) * 0.5 + 0.5;
	float edge = 1.0 - smoothstep(0.0, 0.17, min(UV.y, 1.0 - UV.y));
	vec3 deep = vec3(0.015, 0.12, 0.16);
	vec3 shallow = vec3(0.035, 0.27, 0.29);
	vec3 bank_reflection = vec3(0.16, 0.29, 0.27);
	ALBEDO = mix(deep, shallow, 0.22 + small_ripple * 0.18 + long_flow * 0.10);
	ALBEDO = mix(ALBEDO, bank_reflection, edge * (0.25 + small_ripple * 0.10));
	METALLIC = 0.08;
	ROUGHNESS = mix(0.24, 0.38, edge);
	ALPHA = 0.94;
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
		for step in range(12):
			result.append(start.cubic_interpolate(finish, before, after, float(step) / 12.0))
	result.append(CHANNEL[-1])
	return result


func _load_terrain_textures(texture_root: String) -> Dictionary:
	var result := {}
	if texture_root == "":
		return result
	var files := {
		"fertile": "fertile_terrace_v01.png",
		"wet": "wet_sediment_v01.png",
		"mineral": "silica_escarpment_v01.png",
		"methane": "methane_basin_v01.png",
		"sulphur": "sulphur_crust_v01.png",
	}
	for texture_name in files:
		var path: String = texture_root.path_join(files[texture_name])
		var image := Image.load_from_file(path)
		if image and not image.is_empty():
			if not image.has_mipmaps():
				image.generate_mipmaps()
			result[texture_name] = ImageTexture.create_from_image(image)
		else:
			push_warning("Missing terrain texture: %s" % path)
	return result
