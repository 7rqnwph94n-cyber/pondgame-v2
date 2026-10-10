extends RefCounted
## Candidate material adapter; only the explicit library review invokes it.
static var shader: Shader
static var materials: Dictionary = {}

static func apply(mesh: ArrayMesh, material_path: String) -> void:
	if shader == null:
		shader = load(material_path)
	for index in range(mesh.get_surface_count()):
		var old = mesh.surface_get_material(index)
		if not old is StandardMaterial3D: continue
		var key: String = old.resource_name
		if not materials.has(key):
			var material := ShaderMaterial.new()
			material.shader = shader
			material.resource_name = key
			material.set_shader_parameter("base_colour", old.albedo_color)
			var family := 0.0
			if key in ["verdant_carbonate","verdant_ceramic","verdant_silt","verdant_rock"]: family = 1.0
			elif key == "verdant_silica": family = 2.0
			elif key in ["verdant_growth","verdant_membrane","verdant_fibre"]: family = 3.0
			elif key in ["verdant_amber","verdant_resin","verdant_pigment","verdant_memory"]: family = 4.0
			material.set_shader_parameter("family",family)
			material.set_shader_parameter("base_roughness",0.46)
			materials[key] = material
		mesh.surface_set_material(index,materials[key])
