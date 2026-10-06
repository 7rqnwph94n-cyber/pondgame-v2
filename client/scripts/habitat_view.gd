extends Node3D
## Published habitat rules, visualised without inventing environmental multipliers.
var terrain: Node3D
var geography: Dictionary = {}
var overlay: MeshInstance3D
var deposits: Node3D
var shown := false

func configure(basin: Node3D, data: Dictionary) -> void:
	terrain = basin
	geography = data
	overlay = MeshInstance3D.new()
	overlay.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(overlay)
	deposits = Node3D.new()
	add_child(deposits)
	var st := SurfaceTool.new()
	st.begin(Mesh.PRIMITIVE_TRIANGLES)
	var light: Dictionary = geography.get("light", {})
	var dark := float(light.get("dark_height", -2.5))
	var full := float(light.get("full_height", 1))
	for x in range(-125, 125, 5):
		for z in range(-125, 125, 5):
			var level := clampf((terrain.height_at(x + 2.5, z + 2.5) - dark) / maxf(0.001, full - dark), 0, 1)
			var colour := Color(0.16, 0.35, 0.5, 0.28).lerp(Color(0.93, 0.82, 0.36, 0.32), level)
			for zone in geography.get("extraction_zones", []):
				if in_zone(Vector2(x + 2.5, z + 2.5), zone): colour = Color(0.3, 0.9, 0.94, 0.45)
			for flat in [Vector2(x,z), Vector2(x+5,z+5), Vector2(x+5,z), Vector2(x,z), Vector2(x,z+5), Vector2(x+5,z+5)]:
				st.set_color(colour)
				st.add_vertex(Vector3(flat.x, terrain.height_at(flat.x, flat.y) + 0.15, flat.y))
	st.generate_normals()
	var material := StandardMaterial3D.new()
	material.vertex_color_use_as_albedo = true
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	st.set_material(material)
	overlay.mesh = st.commit()
	overlay.hide()
	for zone in geography.get("extraction_zones", []):
		var centre: Array = zone.get("center", zone.get("centre", [0,0]))
		for i in range(7):
			var rock := MeshInstance3D.new()
			var crystal := PrismMesh.new()
			crystal.size = Vector3(1.5, 0.6 + float(i % 3) * 0.25, 1.4)
			rock.mesh = crystal
			var flat := Vector2(float(centre[0]), float(centre[1])) + Vector2(cos(i * 2.4), sin(i * 2.4)) * (2 + i % 3)
			rock.position = Vector3(flat.x, terrain.height_at(flat.x, flat.y) + 0.2, flat.y)
			rock.rotation.y = i * 1.7
			var mineral := StandardMaterial3D.new()
			mineral.albedo_color = Color("#b3d1d5")
			mineral.roughness = 0.48
			rock.material_override = mineral
			deposits.add_child(rock)

func toggle() -> void:
	shown = not shown
	if overlay: overlay.visible = shown

static func in_zone(point: Vector2, zone: Dictionary) -> bool:
	var centre: Array = zone.get("center", zone.get("centre", [0,0]))
	return point.distance_to(Vector2(float(centre[0]), float(centre[1]))) <= float(zone.get("radius", 0))
