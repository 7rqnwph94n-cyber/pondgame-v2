extends SceneTree
## Existing basin renderer + refined art. No main._ready(), bridge or simulation.
const Main = preload("res://scripts/main.gd")
const Visual = preload("res://scripts/architecture_visual.gd")
var checks := 0
var failures: Array[String] = []
var base: String
var world: Node3D
var camera: Camera3D
var models: Array[Node3D] = []
var layout_v02 := false

func fit_group(first: int,last: int) -> void:
	var low := Vector2(INF,INF)
	var high := Vector2(-INF,-INF)
	var inverse := camera.global_transform.affine_inverse()
	for i in range(first,last):
		var box: AABB = models[i].get_visual_bounds()
		for corner in range(8):
			var point: Vector3 = inverse*(models[i].global_transform*box.get_endpoint(corner))
			low = low.min(Vector2(point.x,point.y));high = high.max(Vector2(point.x,point.y))
	var centre := (low+high)*.5
	camera.global_position += camera.global_basis.x*centre.x+camera.global_basis.y*centre.y
	camera.size = maxf(high.y-low.y,(high.x-low.x)/(1800.0/1100.0))*1.3
	for i in range(first,last):
		var box: AABB = models[i].get_visual_bounds()
		var visible := true
		for corner in range(8):
			var point: Vector3 = models[i].global_transform*box.get_endpoint(corner)
			var screen := camera.unproject_position(point)
			visible = visible and not camera.is_position_behind(point) and Rect2(0,0,1800,1100).has_point(screen)
		check(visible,"group framing contains building "+str(i))

func clear_of_scenery(site: Vector2) -> bool:
	for child in world.get_children():
		if not child is MeshInstance3D or child.mesh == null: continue
		var box: AABB = child.global_transform*child.mesh.get_aabb()
		if site.x+3.5>box.position.x and site.x-3.5<box.end.x and site.y+3.5>box.position.z and site.y-3.5<box.end.z:
			return false
	return true

func _initialize() -> void: call_deferred("run")

func check(value: bool, message: String) -> void:
	checks += 1
	if not value: failures.append(message);printerr(message)

func run() -> void:
	base = ProjectSettings.globalize_path("res://..").simplify_path()
	root.size = Vector2i(1800,1100)
	world = Node3D.new();root.add_child(world)
	# Build the production environment while Main is detached from the tree:
	# its _ready() cannot start a bridge, change speed or touch a live game.
	var builder := Main.new()
	builder.style = builder._load_style()
	layout_v02 = "--layout-v2" in OS.get_cmdline_user_args()
	if layout_v02:
		var candidate: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/map_layout_v02.json"))
		var map: Dictionary = builder.style["environment"]["map"]
		for key in candidate:
			if key != "environment_overrides": map[key] = candidate[key]
		for key in candidate["environment_overrides"]:
			builder.style["environment"][key] = candidate["environment_overrides"][key]
	builder.set_meta("empty_map",true)
	builder._build_environment()
	var terrain = builder._basin_terrain
	var environment: Environment = builder._env
	for child in builder.get_children():
		builder.remove_child(child);world.add_child(child)
	check(builder.bridge == null,"review must not start simulation bridge")
	builder.free()
	if layout_v02:
		# Geographic acceptance: usable starting plain, separated provinces and dry
		# crossing landings. These are presentation checks, not domain legality.
		var original := BasinTerrain.new()
		original._smooth_channel = original._sample_channel()
		var old_dry := 0
		var new_dry := 0
		for z in [-6.0,3.0,12.0,21.0]:
			for x in [-48.0,-39.0,-30.0,-21.0]:
				check(terrain.has_dry_footprint_at(x,z),"continuous starting plain footprint")
				if original.has_dry_footprint_at(x,z): old_dry += 1
				if terrain.has_dry_footprint_at(x,z): new_dry += 1
		print("Starting plain dry samples: original %d/16; candidate %d/16"%[old_dry,new_dry])
		check(new_dry>old_dry,"starting plain improves against original sample grid")
		original.free()
		check(terrain.height_at(48,-30)>terrain.height_at(-30,9)+5,"elevated silica province")
		check(terrain.channel_distance_at(Vector2(-3,9))>=7,"west crossing landing dry")
		check(terrain.channel_distance_at(Vector2(20,9))>=7,"east crossing landing dry")
	var manifest: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(base.path_join("assets/architecture_v04/manifest.json")))
	var locations: Array[Vector2] = []
	# Use dry, reasonably level sites; these are not domain placement permissions.
	for z in [-3.0,6.0,15.0,24.0,33.0,-12.0,-21.0]:
		for x in [-41.0,-32.0,-23.0,-14.0,-50.0,-59.0,-68.0]:
			if not terrain.has_dry_footprint_at(x,z): continue
			if not clear_of_scenery(Vector2(x,z)): continue
			var heights: Array[float] = []
			for offset in [Vector2(-3,-3),Vector2(3,-3),Vector2(-3,3),Vector2(3,3)]:
				heights.append(terrain.height_at(x+offset.x,z+offset.y))
			heights.sort()
			if heights.back()-heights.front()<.65: locations.append(Vector2(x,z))
	check(locations.size()>=10,"ten dry review sites available")
	if locations.size()<10: quit(1);return
	locations.sort_custom(func(a: Vector2,b: Vector2) -> bool: return a.distance_squared_to(Vector2(-32,6))<b.distance_squared_to(Vector2(-32,6)))
	var centre := Vector3.ZERO
	for i in range(10):
		var record: Dictionary = manifest["assets"][i]
		var visual := Visual.new()
		check(visual.load_asset(base.path_join(record["path"])),"load "+record["id"])
		world.add_child(visual)
		models.append(visual)
		var site := locations[i]
		visual.position = Vector3(site.x,terrain.height_at(site.x,site.y)-.035,site.y)
		centre += visual.position
		check(terrain.has_dry_footprint_at(site.x,site.y),"dry footprint "+record["id"])
		check(clear_of_scenery(site),"clear of authored scenery "+record["id"])
		visual.set_condition_state("normal")
		visual.set_construction_progress(1)
		# Unknown local inventory stays hidden. No fake output or live production.
		visual.set_chamber_stocks({})
		visual.set_simulation_paused(true)
		check(not visual.is_processing(),"static review "+record["id"])
	centre /= 10.0
	camera = Camera3D.new();camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	world.add_child(camera)
	var panel := CanvasLayer.new();root.add_child(panel)
	var label := Label.new();label.position = Vector2(24,20)
	label.text = "VERDANT MATERIAL REVIEW — ART FIXTURE\nExisting basin terrain • no simulation, roads or stock assertions"
	label.add_theme_font_size_override("font_size",23)
	panel.add_child(label)
	if layout_v02:
		label.text = "BASIN LAYOUT V02 — ART CANDIDATE\nBroad settlement plain • river bend • separated chemical provinces\nNo simulation resource access or transport permissions"
		for model in models: model.hide()
		camera.size = 150;camera.position = Vector3(25,105,130);camera.look_at(Vector3(0,0,0))
		await capture("empty_overview")
		camera.size = 84;camera.position = Vector3(-18,64,78);camera.look_at(Vector3(-22,0,0))
		await capture("empty_start")
		for model in models: model.show()
	for view in [{"name":"settlement","size":42.0,"offset":Vector3(9,28,35)},
			{"name":"context","size":70.0,"offset":Vector3(14,39,48)},
			{"name":"low","size":44.0,"offset":Vector3(8,16,39)}]:
		camera.size = view["size"]
		camera.position = centre+view["offset"];camera.look_at(centre+Vector3(0,1,0))
		await capture(view["name"])
	var housing_centre := Vector3.ZERO
	for i in range(6):
		housing_centre += Vector3(locations[i].x,terrain.height_at(locations[i].x,locations[i].y),locations[i].y)
	housing_centre /= 6.0
	camera.size = 27;camera.position = housing_centre+Vector3(8,23,29);camera.look_at(housing_centre+Vector3(0,1,0))
	fit_group(0,6)
	await capture("housing_close")
	var industry_centre := Vector3.ZERO
	for i in range(6,10):
		industry_centre += Vector3(locations[i].x,terrain.height_at(locations[i].x,locations[i].y),locations[i].y)
	industry_centre /= 4.0
	camera.size = 27;camera.position = industry_centre+Vector3(8,23,29);camera.look_at(industry_centre+Vector3(0,1,0))
	fit_group(6,10)
	await capture("industry_close")
	# Same scene and sun, neutral fill: do not use fog to conceal weak surfaces.
	environment.ambient_light_color = Color("c2c9c1")
	environment.ambient_light_energy = .45
	camera.size = 42;camera.position = centre+Vector3(9,28,35);camera.look_at(centre+Vector3(0,1,0))
	await capture("neutral")
	print("Basin architecture fixture: %d checks; %d errors"%[checks,failures.size()])
	quit(0 if failures.is_empty() else 1)

func capture(name: String) -> void:
	for frame in range(15): await process_frame
	await RenderingServer.frame_post_draw
	var directory := "docs/art/renders/map_layout_v02" if layout_v02 else "docs/art/renders/architecture_v04"
	DirAccess.make_dir_recursive_absolute(base.path_join(directory))
	var path := base.path_join(directory+"/godot_basin_"+name+".png")
	check(root.get_texture().get_image().save_png(path)==OK,"save "+name)
