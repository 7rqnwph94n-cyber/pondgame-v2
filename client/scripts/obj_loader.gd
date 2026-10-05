class_name ObjLoader
extends RefCounted
## Minimal runtime Wavefront OBJ/MTL reader for Codex's blockout kit (positions, polygons, usemtl, Kd).
## Reading at runtime keeps the presentation assets outside the Godot project untouched (no .import files)
## and lets Codex replace an asset file without any engine step. Normals are generated flat per face.

static var _cache: Dictionary = {}
static var stats: Dictionary = {}     # path -> {vertices, triangles, materials}; testable without a renderer


## Returns an ArrayMesh, or null when the file is missing or empty.
static func load_mesh(path: String) -> ArrayMesh:
	if _cache.has(path):
		return _cache[path]
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return null
	var materials := {}
	var positions: Array[Vector3] = []
	var faces_by_material := {}   # material name -> Array of PackedInt32Array (0-based indices)
	var current := "_default"
	while not file.eof_reached():
		var line := file.get_line().strip_edges()
		if line.is_empty() or line.begins_with("#"):
			continue
		var parts := line.split(" ", false)
		match parts[0]:
			"mtllib":
				materials.merge(_load_mtl(path.get_base_dir().path_join(parts[1])))
			"v":
				positions.append(Vector3(parts[1].to_float(), parts[2].to_float(), parts[3].to_float()))
			"usemtl":
				current = parts[1]
			"f":
				var face := PackedInt32Array()
				for i in range(1, parts.size()):
					var index := parts[i].split("/")[0].to_int()
					face.append(index - 1 if index > 0 else positions.size() + index)
				if not faces_by_material.has(current):
					faces_by_material[current] = []
				faces_by_material[current].append(face)
	if positions.is_empty() or faces_by_material.is_empty():
		return null
	var mesh := ArrayMesh.new()
	var triangles := 0
	for name in faces_by_material:
		var st := SurfaceTool.new()
		st.begin(Mesh.PRIMITIVE_TRIANGLES)
		for face in faces_by_material[name]:
			for k in range(1, face.size() - 1):   # triangle fan; OBJ winding is counter-clockwise
				triangles += 1
				for idx in [face[0], face[k + 1], face[k]]:
					st.add_vertex(positions[idx])
		st.generate_normals()
		var material := StandardMaterial3D.new()
		material.resource_name = str(name)
		material.albedo_color = materials.get(name, Color(0.6, 0.65, 0.65))
		material.roughness = 0.55
		material.cull_mode = BaseMaterial3D.CULL_DISABLED
		st.set_material(material)
		st.commit(mesh)
	_cache[path] = mesh
	stats[path] = {"vertices": positions.size(), "triangles": triangles, "materials": faces_by_material.size()}
	return mesh


static func _load_mtl(path: String) -> Dictionary:
	var colours := {}
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		return colours
	var current := ""
	while not file.eof_reached():
		var parts := file.get_line().strip_edges().split(" ", false)
		if parts.is_empty():
			continue
		if parts[0] == "newmtl":
			current = parts[1]
		elif parts[0] == "Kd" and current != "":
			colours[current] = Color(parts[1].to_float(), parts[2].to_float(), parts[3].to_float())
	return colours
