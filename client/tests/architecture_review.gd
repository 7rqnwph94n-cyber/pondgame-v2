extends SceneTree
## Separate ten-model review. No economy or playable asset mapping changes.
const Loader = preload("res://scripts/obj_loader.gd")

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var base := ProjectSettings.globalize_path("res://..").simplify_path()
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(base.path_join("assets/architecture_v03/manifest.json")))
	var args := OS.get_cmdline_user_args()
	var mode := args[0] if not args.is_empty() else "housing"
	var errors: Array[String] = []
	for record in manifest["assets"]:
		var loaded := Loader.load_mesh(base.path_join(record["path"]))
		if loaded == null:
			errors.append("missing mesh " + record["id"])
			continue
		for s in range(loaded.get_surface_count()):
			var arrays := loaded.surface_get_arrays(s)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			if vertices.size() != normals.size(): errors.append("normal count " + record["id"])
			for normal in normals:
				if not normal.is_finite() or normal.length_squared() < .8:
					errors.append("invalid normal " + record["id"])
					break
	print("Architecture benchmark: %d imports; %d errors" % [manifest["assets"].size(),errors.size()])
	for error in errors: printerr(error)
	if mode == "verify" or not errors.is_empty():
		quit(0 if errors.is_empty() else 1)
		return
	root.size = Vector2i(1800,1100)
	var world := Node3D.new()
	root.add_child(world)
	var env := WorldEnvironment.new()
	env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("203b3c")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color("d0ded7")
	env.environment.ambient_light_energy = .55
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	world.add_child(env)
	var light := DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-55,-25,0)
	light.light_energy = 1.1
	light.shadow_enabled = true
	world.add_child(light)
	var camera := Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 16
	world.add_child(camera)
	camera.position = Vector3(0,20,26)
	camera.look_at(Vector3(0,1,0))
	var indices := range(6) if mode == "housing" else range(6,10)
	var cols := 3 if mode == "housing" else 2
	for j in range(indices.size()):
		var record: Dictionary = manifest["assets"][indices[j]]
		var instance := MeshInstance3D.new()
		instance.mesh = Loader.load_mesh(base.path_join(record["path"]))
		instance.position = Vector3((j%cols-(cols-1)/2.0)*5.8,0,(floori(float(j)/cols)-.5)*9.0)
		world.add_child(instance)
		var label := Label3D.new()
		label.text = record["id"].replace("_"," ").capitalize()
		label.font_size = 45
		label.pixel_size = .008
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.position = instance.position + Vector3(0,.1,2.7)
		world.add_child(label)
	var ground := MeshInstance3D.new()
	ground.mesh = PlaneMesh.new()
	ground.mesh.size = Vector2(60,60)
	ground.position.y = -.15
	var ground_mat := StandardMaterial3D.new()
	ground_mat.albedo_color = Color("43504a")
	ground_mat.roughness = .95
	ground.material_override = ground_mat
	world.add_child(ground)
	for frame in range(15): await process_frame
	await RenderingServer.frame_post_draw
	var path := base.path_join("docs/art/renders/architecture_v03/godot_"+mode+".png")
	var result := root.get_texture().get_image().save_png(path)
	print("Architecture capture: ",path," result=",result)
	quit(0 if result == OK else 1)
