extends SceneTree
## Import verification and normal-renderer art review, separate from gameplay.
## godot --path client -s res://tests/verdant_library_review.gd -- residence
## godot --headless --path client -s res://tests/verdant_library_review.gd -- verify

const Loader = preload("res://scripts/obj_loader.gd")
const Surface = preload("res://scripts/verdant_surface_material.gd")
var base: String

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	base = ProjectSettings.globalize_path("res://..").simplify_path()
	var args := OS.get_cmdline_user_args()
	var mode := args[0] if args.size() else "residence"
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(base.path_join("assets/verdant_v2/manifest.json")))
	var errors: Array[String] = []
	var plain := "--plain" in args
	var shader_path := base.path_join("assets/verdant_v2/materials/biological_surface.gdshader")
	for record in manifest["assets"]:
		var mesh_path: String = base.path_join(record["path"])
		for extension in [".mtl", ".anchors.json"]:
			if not FileAccess.file_exists(mesh_path.get_basename() + extension):
				errors.append("missing companion " + record["id"] + extension)
		var loaded := Loader.load_mesh(mesh_path)
		if loaded == null:
			errors.append("missing mesh " + record["id"])
			continue
		for surface in range(loaded.get_surface_count()):
			var arrays := loaded.surface_get_arrays(surface)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			if vertices.size() != normals.size():
				errors.append("normal count " + record["id"])
			for vertex in vertices:
				if not vertex.is_finite():
					errors.append("invalid vertex " + record["id"])
					break
			for normal in normals:
				if not normal.is_finite() or normal.length_squared() < 0.8:
					errors.append("invalid normal " + record["id"])
					break
		if not plain:
			Surface.apply(loaded,shader_path)
			for index in range(loaded.get_surface_count()):
				if not loaded.surface_get_material(index) is ShaderMaterial: errors.append("missing candidate surface " + record["id"])
	print("Verdant library: %d meshes checked; %d import errors" % [manifest["assets"].size(), errors.size()])
	for error in errors: printerr(error)
	if not errors.is_empty() or mode == "verify":
		quit(0 if errors.is_empty() else 1)
		return
	root.size = Vector2i(1600, 900)
	var world := Node3D.new()
	root.add_child(world)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("203b3c")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color("b9d8d0")
	env.environment.ambient_light_energy = 0.42
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	if "--greyscale" in args:
		env.environment.adjustment_enabled = true
		env.environment.adjustment_saturation = 0.0
	world.add_child(env)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55,-25,0)
	light.light_energy = 1.05
	light.shadow_enabled = true
	world.add_child(light)
	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = {"residence":12, "industry":14, "carriers":10, "goods":7, "ecology":15, "reef":36}.get(mode,14)
	world.add_child(camera)
	camera.position = Vector3(0,20,23)
	camera.look_at(Vector3(0,0.7,0))
	var names: Array = ["res_shelter_cluster_a","res_stable_habitat_a","res_symbiotic_a","res_memory_enclave_a"]
	if mode == "industry":
		names = ["building_mineral_washery_a","building_ceramic_kiln_a","building_composite_workshop_a","building_general_store_a","building_first_nursery_a","building_filter_crown_a","building_sediment_dredge_a","building_survey_organ_a"]
	if mode == "carriers":
		names = []
		for kind in ["general","burrowing","filter","mineral_jaw","detox","vascular","memory"]: names.append("unit_"+kind+"_carrier_a")
	if mode == "goods":
		names = []
		for kind in ["raw_silicate","prepared_silica","carbonate","fired_ceramic","raw_fibre","woven_fibre","raw_resin","cured_resin","biomass","staple","organic_waste","repair_enzyme"]: names.append("payload_"+kind+"_a")
	if mode == "ecology":
		names = []
		for i in range(1,7): names.append("plant_current_meadow_%02d" % i)
	if mode == "reef":
		names = []
		for i in range(4): names.append("great_work_memory_reef_stage_%d" % i)
	var spacing: float = {"carriers":2.8, "goods":1.65, "ecology":4.2, "reef":11.0}.get(mode,5.1)
	var paths := {}
	for record in manifest["assets"]: paths[record.id] = record.path
	for i in range(names.size()):
		var instance := MeshInstance3D.new()
		instance.mesh = Loader.load_mesh(base.path_join(paths[names[i]]))
		instance.position = Vector3((i%4-1.5)*spacing,0,(i/4-(ceilf(names.size()/4.0)-1)/2.0)*spacing if names.size()>4 else 0.0)
		world.add_child(instance)
	var ground := MeshInstance3D.new()
	ground.mesh = PlaneMesh.new()
	ground.mesh.size = Vector2(60,60)
	ground.position.y = -0.12
	var ground_mat := StandardMaterial3D.new()
	ground_mat.albedo_color = Color("43504a")
	ground_mat.roughness = 0.95
	ground.material_override = ground_mat
	world.add_child(ground)
	for frame in range(12): await process_frame
	await RenderingServer.frame_post_draw
	var path := base.path_join("docs/art/renders/library_v02/godot_"+mode+("_plain" if plain else "_surface")+("_grey" if "--greyscale" in args else "")+".png")
	var result := root.get_texture().get_image().save_png(path)
	print("Gallery capture: ", path, " result=", result)
	quit(0 if result == OK else 1)
