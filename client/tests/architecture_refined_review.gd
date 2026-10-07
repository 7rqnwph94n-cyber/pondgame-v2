extends SceneTree
const Loader = preload("res://scripts/architecture_loader.gd")
const Visual = preload("res://scripts/architecture_visual.gd")
const Entity = preload("res://scripts/entity_view.gd")
const Placement = preload("res://scripts/build_placement.gd")
var base: String
var manifest: Dictionary
var world: Node3D
var camera: Camera3D
var models: Array[Node3D] = []
var labels: Array[Label3D] = []
var failures: Array[String] = []
var checks := 0

func _initialize() -> void: call_deferred("run")

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message);printerr("FAIL: ",message)

func visit(node: Node) -> void:
	if node is MeshInstance3D:
		for s in range(node.mesh.get_surface_count()):
			var arrays: Array = node.mesh.surface_get_arrays(s)
			var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
			var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
			var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
			var colours = arrays[Mesh.ARRAY_COLOR]
			check(vertices.size()==normals.size() and vertices.size()==uvs.size(),"textured geometry "+str(node.name))
			check(colours != null and colours.size()==vertices.size(),"geometry-following accretion tint "+str(node.name))
			var tint_valid := colours != null
			if colours != null:
				for colour in colours:
					if not (colour.r>=.55 and colour.r<=1.01 and colour.g>=.55 and colour.g<=1.01 and colour.b>=.55 and colour.b<=1.01):
						tint_valid = false;break
			check(tint_valid,"no unset or invalid accretion tint "+str(node.name))
			var valid := true
			for n in normals:
				if not n.is_finite() or n.length_squared()<.8: valid = false;break
			check(valid,"finite smooth normals "+str(node.name))
			var material: StandardMaterial3D = node.mesh.surface_get_material(s)
			check(material != null and material.albedo_texture != null,"embedded albedo "+str(node.name))
			check(material != null and material.normal_enabled and material.normal_texture != null,"embedded normals "+str(node.name))
			check(material != null and material.vertex_color_use_as_albedo,"native accretion material "+str(node.name))
	for child in node.get_children(): visit(child)

func run() -> void:
	base = ProjectSettings.globalize_path("res://..").simplify_path()
	manifest = JSON.parse_string(FileAccess.get_file_as_string(base.path_join("assets/architecture_v04/manifest.json")))
	var args := OS.get_cmdline_user_args()
	var mode := args[0] if not args.is_empty() else "housing"
	check(manifest["assets"].size()==10,"fixed ten assets")
	for record in manifest["assets"]:
		var visual := Visual.new()
		check(visual.load_asset(base.path_join(record["path"])),"load "+record["id"])
		if visual.asset == null: visual.free();continue
		visit(visual.asset)
		var box := Loader.bounds(visual.asset)
		check(box.size.y > .5 and box.size.x > 1,"valid bounds "+record["id"])
		visual.set_condition_state("active")
		visual.set_stock_state(true,true)
		visual.set_recipe_state("present",.5,"present")
		var original_scale := visual.scale
		visual._process(.3)
		check(visual.scale==original_scale,"whole building never pulses")
		visual.set_recipe_state("present",.25,"present")
		var snapshots: Array[Vector3] = []
		for node in visual._flow: snapshots.append(node.scale)
		visual._process(30)
		for j in range(visual._flow.size()): check(visual._flow[j].scale==snapshots[j],"wall clock cannot advance production")
		visual.set_condition_state("output_blocked")
		check(not visual.running,"blocked stops activity")
		for node in visual._flow: check(node.scale.is_equal_approx(Vector3.ONE),"blocked resets soft flow")
		visual.set_condition_state("dormant")
		check(not visual.running,"dormant stops activity")
		visual.set_construction_progress(.2)
		visual.set_condition_state("active")
		check(not visual.running,"unfinished architecture cannot operate")
		visual.set_construction_progress(1)
		check(visual.running,"commissioned architecture can operate")
		check(visual.set_low_detail(true),"distance mesh loads")
		visit(visual.asset)
		var distant_box := Loader.bounds(visual.asset)
		for axis in range(3):
			check(absf(distant_box.size[axis]-box.size[axis]) <= box.size[axis]*.05,"distance silhouette bounds "+record["id"])
		check(visual.running,"LOD preserves condition")
		visual.set_recipe_state("present",.25,"present")
		check(visual.set_low_detail(false),"recipe-progress near mesh restores")
		for node in visual._flow:
			check(is_equal_approx(node.scale.y,visual._original[node].y*1.012),"LOD preserves explicit recipe phase")
		check(visual.set_low_detail(false),"near mesh restores")
		visual.set_simulation_paused(true)
		check(not visual.is_processing(),"pause stops animation")
		visual.free()
	var style: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/asset_map.json"))
	style["asset_root"] = ProjectSettings.globalize_path("res://").path_join(style["asset_dir"]).simplify_path()
	check(Loader.path_for(style,"residence","shelter")=="","default mapping not replaced")
	style["architecture_review"] = true
	for definition in ["shelter","stable","symbiotic","memory"]:
		var entity := Entity.new();entity.setup("residence",style)
		entity.set_entity_identity("review_"+definition,definition)
		check(entity._body.has_method("get_visual_bounds"),"textured entity binding "+definition)
		entity.set_condition_state("normal")
		entity.set_construction_progress(.25)
		check(not entity._body.running and entity._scaffold==null,"authored construction replaces box")
		entity.set_construction_progress(1)
		check(entity._body.running,"construction returns to condition")
		check(WorldView.visual_footprint(entity._body).x>=7,"hierarchical footprint")
		entity.free()
	for definition in ["general_store","mineral_washery","ceramic_kiln","waste_digester"]:
		var preview := Placement.new();preview.configure(definition,style)
		check(preview._ghost.has_method("get_visual_bounds"),"matching PBR preview "+definition)
		check(preview.footprint.x>=7 and preview.footprint.y>=7,"preview footprint")
		preview.free()
	var store := Visual.new()
	store.load_asset(Loader.path_for(style,"facility","general_store"))
	store.set_stock_state(true,true)
	store.set_chamber_stocks({"prepared_silica":5})
	var chamber_count := 0
	var visible_count := 0
	for node in store.asset.find_children("CargoOutput__*","Node3D",true,false):
		if node is MeshInstance3D: continue
		chamber_count += 1
		if node.visible: visible_count += 1
	check(chamber_count==3,"store has three independently typed galleries")
	check(visible_count==1,"only explicitly known local silica is displayed")
	check(store.set_low_detail(true),"typed storage LOD")
	visible_count = 0
	for node in store.asset.find_children("CargoOutput__*","Node3D",true,false):
		if not node is MeshInstance3D and node.visible: visible_count += 1
	check(visible_count==1,"typed local stock survives LOD")
	store.free()
	print("Refined architecture: %d checks; %d errors" % [checks,failures.size()])
	if mode == "verify" or not failures.is_empty():
		quit(0 if failures.is_empty() else 1);return
	root.size = Vector2i(1800,1100)
	world = Node3D.new();root.add_child(world)
	var env := WorldEnvironment.new();env.environment = Environment.new()
	env.environment.background_mode = Environment.BG_COLOR
	env.environment.background_color = Color("263e40")
	env.environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.environment.ambient_light_color = Color("b3ceca")
	env.environment.ambient_light_energy = .5
	env.environment.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	world.add_child(env)
	var light := DirectionalLight3D.new();light.rotation_degrees = Vector3(-48,-28,0)
	light.light_energy = 1.2;light.shadow_enabled = true;world.add_child(light)
	camera = Camera3D.new();camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 17;world.add_child(camera);camera.position = Vector3(0,20,26);camera.look_at(Vector3(0,1,0))
	var ground := MeshInstance3D.new();ground.mesh = PlaneMesh.new();ground.mesh.size = Vector2(120,120)
	ground.position.y = -.16
	var gm := StandardMaterial3D.new();gm.albedo_color = Color("62665a");gm.roughness = .95
	ground.material_override = gm;world.add_child(ground)
	var indices := range(6) if mode == "housing" else range(6,10)
	if mode in ["orbit","density","states","greyscale","pitch","zoom","construction"]: indices = range(10)
	var columns := 3 if mode == "housing" else 2
	if mode == "density": columns = 10;indices = range(100)
	if mode in ["orbit","greyscale","pitch","zoom"]: columns = 5
	if mode == "states": columns = 4;indices = range(4)
	if mode == "construction": columns = 5;indices = range(5)
	if mode == "detail": columns = 1;indices = range(5,6)
	for j in range(indices.size()):
		var index: int = indices[j]%10
		if mode == "states": index = 7
		if mode == "construction": index = 5
		var record: Dictionary = manifest["assets"][index]
		var visual := Visual.new();visual.load_asset(base.path_join(record["path"]))
		world.add_child(visual);models.append(visual)
		visual.position = Vector3((j%columns-(columns-1)/2.0)*6.5,0,(floori(float(j)/columns)-.5)*12)
		if mode == "detail": visual.position = Vector3.ZERO
		visual.set_condition_state("normal" if index<6 else "active")
		visual.set_stock_state(true,true)
		if mode == "states":
			visual.set_condition_state(["active","awaiting_input","output_blocked","dormant"][j])
			visual.set_stock_state(j!=1,j==0 or j==2)
		if mode == "construction": visual.set_construction_progress([0.0,.25,.5,.75,1.0][j])
		if mode == "greyscale": greyscale(visual.asset)
		var label := Label3D.new();label.font_size = 36;label.pixel_size = .009
		label.text = record["id"].replace("_"," ").capitalize()
		if mode == "states": label.text = ["Active fixture","Awaiting input fixture","Blocked output fixture","Dormant fixture"][j]
		if mode == "construction": label.text = ["0%","25% frame","50% shell","75% soft tissue","100% complete"][j]
		label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
		label.position = visual.position+Vector3(0,.1,2.55);world.add_child(label)
		labels.append(label)
	if mode == "pitch":
		camera.size = 29
		for pitch in [20,38,65]:
			# At low pitch the tall foreground manor obscured the seed shelter.
			# Spread the two rows for review; never mistake that occlusion for
			# an asset mismatch or hide it by selecting a flattering yaw.
			for j in range(models.size()):
				models[j].position.z = (floori(float(j)/columns)-.5)*(20 if pitch==20 else 12)
				labels[j].position = models[j].position+Vector3(0,.1,2.55)
			camera.position = Vector3(0,sin(deg_to_rad(pitch))*40,cos(deg_to_rad(pitch))*40)
			camera.look_at(Vector3(0,1,0));await capture("pitch_%d"%pitch)
	elif mode == "zoom":
		for size in [24,42,70]:
			camera.size = size;await capture("zoom_%d"%size)
	elif mode == "orbit":
		camera.size = 27
		for yaw in range(8):
			for visual in models: visual.rotation.y = deg_to_rad(yaw*45)
			await capture("orbit_%02d"%yaw)
	elif mode == "density":
		camera.size = 95;camera.position = Vector3(0,85,110);camera.look_at(Vector3(0,0,38))
		DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
		for frame in range(60): await process_frame
		var samples: Array[float] = []
		for frame in range(180):
			var started := Time.get_ticks_usec();await process_frame
			samples.append((Time.get_ticks_usec()-started)/1000.0)
		samples.sort()
		var report := {"instances":100,"frame_ms_median":samples[90],"frame_ms_p95":samples[171],"renderer":RenderingServer.get_current_rendering_method(),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME)}
		var f := FileAccess.open(base.path_join("docs/art/renders/architecture_v04/density_report.json"),FileAccess.WRITE);f.store_string(JSON.stringify(report,"\t"));f.close()
		print("Density report: ",report);await capture("density")
	else:
		if mode == "detail":
			camera.size = 6.5;camera.position = Vector3(7,8,11);camera.look_at(Vector3(0,2,0))
		if mode=="states": camera.size = 17
		if mode in ["greyscale","construction"]: camera.size = 27
		await capture(mode)
	quit()

func capture(name: String) -> void:
	for frame in range(10): await process_frame
	await RenderingServer.frame_post_draw
	var path := base.path_join("docs/art/renders/architecture_v04/godot_"+name+".png")
	var error := root.get_texture().get_image().save_png(path)
	print("Capture ",name," ",error)

func greyscale(node: Node) -> void:
	if node is MeshInstance3D:
		for surface in range(node.mesh.get_surface_count()):
			var original: StandardMaterial3D = node.mesh.surface_get_material(surface)
			var material := ShaderMaterial.new()
			var shader := Shader.new()
			shader.code = "shader_type spatial; uniform sampler2D base_texture: source_color; void fragment(){vec3 c=texture(base_texture,UV).rgb*COLOR.rgb;ALBEDO=vec3(dot(c,vec3(.2126,.7152,.0722)));ROUGHNESS=.6;}"
			material.shader = shader
			material.set_shader_parameter("base_texture",original.albedo_texture)
			node.set_surface_override_material(surface,material)
	for child in node.get_children():greyscale(child)
