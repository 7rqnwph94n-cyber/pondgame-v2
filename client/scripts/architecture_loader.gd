extends RefCounted
## Self-contained textured glTF candidates outside res://, cached as PackedScenes.
## Loading never changes simulation state or the default presentation mapping.
static var _cache: Dictionary = {}
static var _catalog: Dictionary = {}

static func path_for(style: Dictionary, kind: String, definition: String) -> String:
	if not style.get("architecture_review",false) and OS.get_environment("POND_ARCHITECTURE_V04") != "1": return ""
	if _catalog.is_empty():
		var parsed = JSON.parse_string(FileAccess.get_file_as_string("res://presentation/architecture_v04.json"))
		if not parsed is Dictionary: return ""
		_catalog = parsed
	var key := "residence_tiers" if kind == "residence" else "buildings"
	var name: String = _catalog.get(key,{}).get(definition,"")
	if name.is_empty(): return ""
	return ProjectSettings.globalize_path("res://..").simplify_path().path_join(_catalog["asset_dir"]).path_join(name+".glb")

static func instantiate(path: String) -> Node3D:
	if not FileAccess.file_exists(path): return null
	if not _cache.has(path):
		var document := GLTFDocument.new()
		var state := GLTFState.new()
		var error := document.append_from_file(path, state)
		if error != OK:
			push_error("Architecture glTF failed: %s (%d)" % [path,error])
			return null
		var scene := document.generate_scene(state)
		if scene == null: return null
		var packed := PackedScene.new()
		error = packed.pack(scene)
		scene.free()
		if error != OK: return null
		_cache[path] = packed
	return _cache[path].instantiate() as Node3D

static func bounds(node: Node3D) -> AABB:
	var points: Array[Vector3] = []
	_collect_bounds(node, Transform3D.IDENTITY, points)
	if points.is_empty(): return AABB()
	var result := AABB(points[0],Vector3.ZERO)
	for point in points: result = result.expand(point)
	return result

static func _collect_bounds(node: Node, parent_transform: Transform3D, points: Array[Vector3]) -> void:
	var transform := parent_transform
	if node is Node3D: transform = parent_transform * node.transform
	if node is MeshInstance3D and node.mesh != null:
		var box: AABB = node.mesh.get_aabb()
		for corner in range(8): points.append(transform * box.get_endpoint(corner))
	for child in node.get_children(): _collect_bounds(child,transform,points)
