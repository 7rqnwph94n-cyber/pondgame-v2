extends Node3D
## Candidate state adapter. Only explicit caller evidence animates activity or goods.
const Loader = preload("res://scripts/architecture_loader.gd")
var asset: Node3D
var condition := "idle"
var recipe_progress := 0.0
var running := false
var _flow: Array[Node3D] = []
var _original: Dictionary = {}
var _path := ""
var _low_detail := false
var _input_stock := false
var _output_stock := false
var _construction := 1.0
var _chamber_stocks: Dictionary = {}

func load_asset(path: String) -> bool:
	_path = path
	return _reload(path)

func _reload(path: String) -> bool:
	var next := Loader.instantiate(path)
	if next == null: return false
	_flow.clear()
	_original.clear()
	if asset: remove_child(asset);asset.free()
	asset = next
	add_child(asset)
	_collect(asset)
	set_construction_progress(_construction)
	set_condition_state(condition)
	set_stock_state(_input_stock,_output_stock)
	set_recipe_state("",recipe_progress,"")
	return true

func set_low_detail(value: bool) -> bool:
	if value == _low_detail: return true
	var path := _path.get_basename()+"_lod.glb" if value else _path
	if not _reload(path): return false
	_low_detail = value
	return true

func _collect(node: Node) -> void:
	if node is Node3D and str(node.name).begins_with("Flow") and not node is MeshInstance3D:
		_flow.append(node)
		_original[node] = node.scale
	for child in node.get_children(): _collect(child)

func _groups(node: Node, prefix: String, show: bool) -> void:
	if node is Node3D and str(node.name).begins_with(prefix): node.visible = show
	for child in node.get_children(): _groups(child,prefix,show)

func set_condition_state(value: String) -> void:
	condition = value
	running = value in ["active","running","normal"] and _construction >= .999
	if asset:
		_groups(asset,"Activity",running or value == "strained" and _construction >= .999)
		_groups(asset,"Flow",value != "dormant" and _construction >= .999)
		_groups(asset,"Dormancy",value == "dormant")
	# Blocked, paused, idle and dormant do not invent production motion.
	if not running:
		for node in _flow: node.scale = _original[node]

func set_recipe_state(_input_state: String, progress: float, _output_state: String) -> void:
	recipe_progress = clampf(progress,0,1)
	if running:
		for node in _flow:
			node.scale = _original[node] * Vector3(1,1+.012*sin(recipe_progress*TAU),1)

func set_stock_state(has_input: bool, has_output: bool) -> void:
	_input_stock = has_input
	_output_stock = has_output
	if not asset: return
	_groups(asset,"CargoInput",has_input and _construction >= .999)
	_groups(asset,"CargoOutput",has_output and _construction >= .999)
	_apply_chamber_stocks(asset)

func set_chamber_stocks(known_local_counts: Dictionary) -> void:
	# Presence only, not exact unit count. Missing resources stay hidden.
	_chamber_stocks = known_local_counts.duplicate()
	if asset:
		if _chamber_stocks.is_empty(): set_stock_state(_input_stock,_output_stock)
		else: _apply_chamber_stocks(asset)

func _apply_chamber_stocks(node: Node) -> void:
	if _chamber_stocks.is_empty(): return
	var name_base := str(node.name).split(".")[0]
	for prefix in ["CargoInput__","CargoOutput__"]:
		if node is Node3D and name_base.begins_with(prefix) and not node is MeshInstance3D:
			var resource := name_base.trim_prefix(prefix)
			# Godot sanitises Blender's .001 suffix to _001 in node names.
			var last := resource.rfind("_")
			if last >= 0 and resource.substr(last+1).is_valid_int(): resource = resource.substr(0,last)
			node.visible = float(_chamber_stocks.get(resource,0)) > 0 and _construction >= .999
	for child in node.get_children(): _apply_chamber_stocks(child)

func set_construction_progress(value: float) -> void:
	_construction = clampf(value,0,1)
	if not asset: return
	_groups(asset,"GrowthFrame",_construction >= .05)
	_groups(asset,"GrowthShell",_construction >= .33)
	_groups(asset,"GrowthSoft",_construction >= .70)
	_groups(asset,"Flow",_construction >= .999 and condition != "dormant")
	_groups(asset,"Residue",_construction >= .999)
	set_condition_state(condition)
	set_stock_state(_input_stock,_output_stock)

func set_simulation_paused(paused: bool) -> void:
	set_process(not paused)

func get_visual_bounds() -> AABB:
	return Loader.bounds(asset) if asset else AABB()

func _process(_delta: float) -> void:
	var viewport := get_viewport()
	var camera: Camera3D = viewport.get_camera_3d() if viewport else null
	if camera and camera.projection == Camera3D.PROJECTION_ORTHOGONAL:
		var should_be_low := camera.size > (24.0 if _low_detail else 28.0)
		if should_be_low != _low_detail: set_low_detail(should_be_low)
	# Work deformation changes only when authoritative recipe progress changes.
	# Wall-clock frames (including a paused simulation) never invent production.
