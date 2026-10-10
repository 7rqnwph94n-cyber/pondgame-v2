extends SceneTree
## Isolated house-only native review, never changes live asset selection.
const Architecture = preload("res://scripts/architecture_loader.gd")
const Obj = preload("res://scripts/obj_loader.gd")
var base: String
var failures: Array[String] = []
var checks := 0
func _initialize() -> void: call_deferred("run")
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures.append(message)
func inspect(node: Node) -> void:
	if node is MeshInstance3D:
		for s in range(node.mesh.get_surface_count()):
			var a: Array = node.mesh.surface_get_arrays(s)
			var v: PackedVector3Array = a[Mesh.ARRAY_VERTEX]
			var n: PackedVector3Array = a[Mesh.ARRAY_NORMAL]
			var uv: PackedVector2Array = a[Mesh.ARRAY_TEX_UV]
			check(v.size()==n.size() and v.size()==uv.size(),"vertex/normal/UV counts")
			var valid := true
			for p in v: valid = valid and p.is_finite()
			for p in n: valid = valid and p.is_finite() and p.length_squared()>.8
			check(valid,"finite geometry and normals")
			var m = node.mesh.surface_get_material(s)
			check(m is StandardMaterial3D and m.albedo_texture!=null and m.normal_texture!=null and m.roughness_texture!=null,"embedded PBR maps")
			if m is StandardMaterial3D and m.albedo_texture!=null:
				check(m.albedo_texture.get_width()==1024,"1024 material resolution")
				check(m.vertex_color_use_as_albedo,"growth tint enabled")
	for child in node.get_children(): inspect(child)
func prepare(node: Node) -> void:
	if node is Node3D and str(node.name).begins_with("Dormancy"): node.visible=false
	for child in node.get_children(): prepare(child)
func run() -> void:
	base=ProjectSettings.globalize_path("res://..").simplify_path()
	var manifest: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(base.path_join("assets/housing_polish_v01/manifest.json")))
	var palette=Image.new()
	check(palette.load(base.path_join("assets/housing_polish_v01/textures/shell_surface.png"))==OK,"source shell texture loads")
	var green := 0.0
	for y in range(0,palette.get_height(),64):
		for x in range(0,palette.get_width(),64): green+=palette.get_pixel(x,y).g
	green/=256.0
	check(green>.18 and green<.45,"exported teal palette remains in authored sRGB range")
	var args=OS.get_cmdline_user_args()
	var mode: String=args[0] if args.size() else "comparison"
	for record in manifest.assets:
		var near_bounds := AABB()
		for key in ["path","lod_path"]:
			var model=Architecture.instantiate(base.path_join(record[key]))
			check(model!=null,"load "+record[key])
			if model!=null:
				inspect(model)
				var box := Architecture.bounds(model)
				if key=="path": near_bounds=box
				else:
					for axis in range(3): check(absf(box.size[axis]-near_bounds.size[axis])<near_bounds.size[axis]*.05,"distance silhouette bounds")
				model.free()
	print("Housing polish: %d checks; %d errors" % [checks,failures.size()])
	for failure in failures: printerr(failure)
	if mode=="verify" or failures.size(): quit(0 if failures.is_empty() else 1);return
	root.size=Vector2i(1800,1100)
	root.msaa_3d=Viewport.MSAA_4X
	var world=Node3D.new();root.add_child(world)
	var env=WorldEnvironment.new();env.environment=Environment.new()
	env.environment.background_mode=Environment.BG_COLOR
	env.environment.background_color=Color("293f43")
	env.environment.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color=Color("bbd0ce")
	env.environment.ambient_light_energy=.32
	env.environment.tonemap_mode=Environment.TONE_MAPPER_FILMIC
	env.environment.ssao_enabled=true
	env.environment.ssao_radius=.6
	env.environment.ssao_intensity=1.0
	if "--greyscale" in args:
		env.environment.adjustment_enabled=true;env.environment.adjustment_saturation=0
	world.add_child(env)
	var light=DirectionalLight3D.new();light.rotation_degrees=Vector3(-48,-32,0);light.light_energy=1.4;light.shadow_enabled=true;world.add_child(light)
	var fill=DirectionalLight3D.new();fill.rotation_degrees=Vector3(-35,135,0);fill.light_energy=.35;fill.light_color=Color("a4cfd3");world.add_child(fill)
	var cam=Camera3D.new();cam.projection=Camera3D.PROJECTION_ORTHOGONAL;world.add_child(cam)
	var ground=MeshInstance3D.new();ground.mesh=PlaneMesh.new();ground.mesh.size=Vector2(100,100);ground.position.y=-.06
	var mat=StandardMaterial3D.new();mat.albedo_color=Color("525f56");mat.roughness=.96;ground.material_override=mat;world.add_child(ground)
	var old_names=["res_shelter_cluster_a","res_stable_habitat_a","res_symbiotic_a","res_memory_enclave_a"]
	if mode=="comparison" or mode=="distance":
		cam.size=18.5;cam.position=Vector3(0,22,28);cam.look_at(Vector3(0,1,0))
		for i in range(4):
			var old=MeshInstance3D.new();old.mesh=Obj.load_mesh(base.path_join("assets/verdant_v2/settlement/"+old_names[i]+".obj"))
			preload("res://scripts/verdant_surface_material.gd").apply(old.mesh,base.path_join("assets/verdant_v2/materials/biological_surface.gdshader"))
			old.position=Vector3((i-1.5)*7,0,-4);world.add_child(old)
			var model=Architecture.instantiate(base.path_join(manifest.assets[i]["lod_path" if mode=="distance" else "path"]))
			prepare(model);world.add_child(model);model.position=Vector3((i-1.5)*7,0,4)
	else:
		var index=clampi(int(mode),0,3)
		var model=Architecture.instantiate(base.path_join(manifest.assets[index].path));prepare(model);world.add_child(model)
		var box=Architecture.bounds(model);var center=box.get_center()
		cam.size=maxf(box.size.x,box.size.y)*1.45
		var angle: float=deg_to_rad(float(args[args.find("--angle")+1])) if "--angle" in args else deg_to_rad(18.0)
		cam.position=center+Vector3(sin(angle)*10,7,cos(angle)*12);cam.look_at(center)
	for frame in range(20): await process_frame
	await RenderingServer.frame_post_draw
	var suffix="_grey" if "--greyscale" in args else ""
	if "--angle" in args: suffix+="_angle"+args[args.find("--angle")+1]
	var output=base.path_join("docs/art/renders/housing_polish_v01/"+mode+suffix+".png")
	var result=root.get_texture().get_image().save_png(output)
	print("Housing capture: ",output," result=",result)
	quit(0 if result==OK else 1)
