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
var _channel_points: Array[Vector2] = []
var _textures: Dictionary = {}


func configure_layout(map: Dictionary) -> void:
	_channel_points.clear()
	for pair in map.get("channel", []):
		if pair is Array and pair.size() >= 2:
			_channel_points.append(Vector2(float(pair[0]), float(pair[1])))


func build(texture_root: String = "") -> void:
	_smooth_channel = _sample_channel()
	_textures = _load_terrain_textures(texture_root)
	add_child(_terrain_mesh())
	add_child(_deposition_marks())
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


func has_dry_footprint_at(x: float, z: float) -> bool:
	# Presentation placement only. Keep a full building footprint off the channel;
	# simulation legality and resource access remain the domain's responsibility.
	for offset in [Vector2.ZERO, Vector2(-3.5, -3.5), Vector2(3.5, -3.5),
			Vector2(-3.5, 3.5), Vector2(3.5, 3.5)]:
		if _distance_to_path(Vector2(x, z) + offset) < 7.0:
			return false
	return true


func _terrain_weights(x: float, z: float) -> Color:
	var point := Vector2(x, z)
	var d := _distance_to_path(point)
	var bank_variation := sin(x * 0.31 + z * 0.19) * 0.9 + cos(z * 0.39 - x * 0.11) * 0.6
	var wet := (1.0 - smoothstep(5.4, 13.5 + bank_variation, d)) * 0.94
	var mineral := smoothstep(10.0, 42.0, x) * (1.0 - smoothstep(-24.0, 16.0, z))
	mineral *= 0.88
	var methane := exp(-pow((x + 36.0) / 18.0, 2.0) - pow((z - 21.0) / 16.0, 2.0)) * 0.96
	var sulphur := exp(-pow((x - 44.0) / 15.0, 2.0) - pow((z + 2.0) / 19.0, 2.0)) * 0.96
	return Color(wet, mineral, methane, sulphur)


func _secondary_weights(x: float, z: float) -> Vector2:
	# Extra province weights travel in UV2: carbonate shelf, then stable carbon-clay terrace.
	var carbonate := exp(-pow((x + 49.0) / 20.0, 2.0) - pow((z + 29.0) / 17.0, 2.0)) * 0.96
	var carbon_clay := exp(-pow((x + 18.0) / 35.0, 2.0) - pow((z + 7.0) / 27.0, 2.0)) * 0.82
	return Vector2(carbonate, carbon_clay)


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
uniform sampler2D carbonate_texture : source_color, repeat_enable, filter_linear_mipmap;
uniform sampler2D carbon_clay_texture : source_color, repeat_enable, filter_linear_mipmap;
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
	vec3 carbonate = mix(texture(carbonate_texture, terrain_uv).rgb, texture(carbonate_texture, broken_uv).rgb, 0.11);
	vec3 carbon_clay = mix(texture(carbon_clay_texture, terrain_uv).rgb, texture(carbon_clay_texture, broken_uv).rgb, 0.14);
	vec4 weights = max(COLOR, vec4(0.0));
	vec2 secondary = max(UV2, vec2(0.0));
	float all_weights = dot(weights, vec4(1.0)) + secondary.x + secondary.y;
	float fertile_weight = max(0.06, 1.0 - all_weights);
	float total = fertile_weight + all_weights;
	vec3 surface = fertile * fertile_weight + wet * weights.r + mineral * weights.g + methane * weights.b + sulphur * weights.a;
	surface += carbonate * secondary.x + carbon_clay * secondary.y;
	float broad = sin(world_position.x * 0.071) * cos(world_position.z * 0.063);
	ALBEDO = surface / total * (0.92 + broad * 0.055);
	ROUGHNESS = mix(0.91, 0.72, weights.b * 0.45 + weights.r * 0.2);
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	for texture_name in ["fertile", "wet", "mineral", "methane", "sulphur", "carbonate", "carbon_clay"]:
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
	st.set_uv2(_secondary_weights(x, z))
	st.add_vertex(Vector3(x, height, z))


func _deposition_marks() -> MeshInstance3D:
	# Short, terrain-conforming retreat lines. Breaks in the lines keep the bank organic.
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	for side_value in [-1.0, 1.0]:
		var side: float = side_value
		for i in range(3, _smooth_channel.size() - 3):
			if (i + (2 if side > 0.0 else 0)) % 11 > 2:
				continue
			var start: Vector2 = _smooth_channel[i]
			var finish: Vector2 = _smooth_channel[i + 1]
			var before: Vector2 = _smooth_channel[i - 1]
			var after: Vector2 = _smooth_channel[i + 2]
			var tangent_a := (finish - before).normalized()
			var tangent_b := (after - start).normalized()
			var normal_a := Vector2(-tangent_a.y, tangent_a.x) * side
			var normal_b := Vector2(-tangent_b.y, tangent_b.x) * side
			var offset := 8.0 + sin(float(i) * 0.47) * 0.7
			var a := start + normal_a * offset
			var b := finish + normal_b * offset
			var width := 0.14 + 0.055 * sin(float(i) * 0.23 + side)
			var quad := [a - normal_a * width, b - normal_b * width, b + normal_b * width,
				a - normal_a * width, b + normal_b * width, a + normal_a * width]
			for p in quad:
				st.add_vertex(Vector3(p.x, height_at(p.x, p.y) + 0.065, p.y))
	st.generate_normals()
	var shader := Shader.new()
	shader.code = """
shader_type spatial;
render_mode blend_mix, cull_disabled;
uniform sampler2D carbonate_texture : source_color, repeat_enable, filter_linear_mipmap;
varying vec3 world_position;
void vertex() { world_position = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment() {
	vec3 sediment = texture(carbonate_texture, world_position.xz / 12.0).rgb;
	ALBEDO = sediment * vec3(0.25, 0.32, 0.29);
	ROUGHNESS = 0.98;
	ALPHA = 0.45;
}
"""
	var material := ShaderMaterial.new()
	material.shader = shader
	if _textures.has("carbonate"):
		material.set_shader_parameter("carbonate_texture", _textures["carbonate"])
	st.set_material(material)
	var instance := MeshInstance3D.new()
	instance.mesh = st.commit()
	instance.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return instance


func _water_mesh() -> MeshInstance3D:
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var left: Array[Vector3] = []
	var right: Array[Vector3] = []
	for i in range(_smooth_channel.size()):
		var previous: Vector2 = _smooth_channel[max(0, i - 1)]
		var following: Vector2 = _smooth_channel[min(_smooth_channel.size() - 1, i + 1)]
		var direction := (following - previous).normalized()
		var half_width := 5.15 + sin(float(i) * 0.23) * 0.55 + cos(float(i) * 0.59) * 0.16
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
	float flow_filament = sin(UV.y * 22.0 + sin(UV.x * 2.3 - TIME * 0.27) * 1.2);
	flow_filament = smoothstep(0.86, 0.99, flow_filament) * smoothstep(0.10, 0.68, long_flow);
	float edge = 1.0 - smoothstep(0.0, 0.17, min(UV.y, 1.0 - UV.y));
	vec3 deep = vec3(0.015, 0.12, 0.16);
	vec3 shallow = vec3(0.035, 0.27, 0.29);
	vec3 bank_reflection = vec3(0.16, 0.29, 0.27);
	ALBEDO = mix(deep, shallow, 0.22 + small_ripple * 0.18 + long_flow * 0.10);
	ALBEDO = mix(ALBEDO, bank_reflection, edge * (0.25 + small_ripple * 0.10));
	ALBEDO += vec3(0.018, 0.034, 0.032) * flow_filament;
	ALBEDO += vec3(0.025, 0.045, 0.035) * edge * smoothstep(0.78, 1.0, small_ripple);
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


func channel_distance_at(point: Vector2) -> float:
	return _distance_to_path(point)


func _sample_channel() -> Array[Vector2]:
	var result: Array[Vector2] = []
	var points: Array = _channel_points if _channel_points.size() >= 2 else CHANNEL
	for i in range(points.size() - 1):
		var before: Vector2 = points[max(0, i - 1)]
		var start: Vector2 = points[i]
		var finish: Vector2 = points[i + 1]
		var after: Vector2 = points[min(points.size() - 1, i + 2)]
		for step in range(12):
			result.append(start.cubic_interpolate(finish, before, after, float(step) / 12.0))
	result.append(points[-1])
	return result


func material_texture(texture_name: String) -> Texture2D:
	return _textures.get(texture_name)


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
		"carbonate": "carbonate_shelf_v01.png",
		"carbon_clay": "carbon_clay_terrace_v01.png",
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
