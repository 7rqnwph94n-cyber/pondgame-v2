class_name EntityView
extends Node3D
## Presentation adapter for one domain entity (CLAUDE.md "Adapter surface").
## The domain pushes state in through these methods; the wrapper decides how to show it. Replaceable:
## Codex can swap the mesh (asset_map.json) or replace this script without touching gameplay.
## Unsupported actions and states fall back to idle/default visuals.

signal picked(entity_id: String)

var entity_id := ""
var definition_id := ""
var kind := ""                     # facility | site | residence
var category := ""
var state_id := ""

var _body: Node3D
var _scaffold: MeshInstance3D
var _lamp: MeshInstance3D
var _label: Label3D
var _style: Dictionary = {}
var _pulse := 0.0


func setup(entity_kind: String, style: Dictionary) -> void:
	kind = entity_kind
	_style = style
	_lamp = MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.45
	sphere.height = 0.9
	_lamp.mesh = sphere
	_lamp.position = Vector3(0, 5.2, 0)
	add_child(_lamp)
	_label = Label3D.new()
	_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	_label.font_size = 42
	_label.pixel_size = 0.018
	_label.outline_size = 10
	_label.position = Vector3(0, 5.7, 0)
	_label.width = 240
	_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	add_child(_label)
	var area := StaticBody3D.new()
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(7, 6, 7)
	shape.shape = box
	shape.position = Vector3(0, 3, 0)
	area.add_child(shape)
	area.set_meta("entity_view", self)
	add_child(area)


# ------------------------------------------------------------------ adapter surface
## CLAUDE.md names this set_identity(); Node3D.set_identity() already exists in Godot, hence set_entity_identity().
func set_entity_identity(id: String, definition: String, _culture_id: String = "verdant") -> void:
	entity_id = id
	definition_id = definition
	name = id
	_rebuild_body()
	_refresh_label()


func set_category(value: String) -> void:
	category = value


func set_action(action_id: String) -> void:
	set_condition_state(action_id)


func set_payload(_resource_id: String, _amount: int, _capacity: int) -> void:
	pass   # payload props arrive with logistics (later milestone)


func set_recipe_state(_input_state: String, progress: float, _output_state: String) -> void:
	if _body:
		_body.scale = Vector3.ONE * (1.0 + 0.03 * sin(progress * TAU))


func set_construction_progress(progress: float) -> void:
	if _scaffold == null:
		_scaffold = MeshInstance3D.new()
		var box := BoxMesh.new()
		box.size = Vector3(6, 1, 6)
		_scaffold.mesh = box
		var mat := StandardMaterial3D.new()
		mat.albedo_color = Color(0.6, 0.65, 0.68, 0.45)
		mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		_scaffold.material_override = mat
		add_child(_scaffold)
	var height: float = max(0.2, 4.0 * clamp(progress, 0.0, 1.0))
	_scaffold.scale = Vector3(1, height, 1)
	_scaffold.position = Vector3(0, height / 2.0, 0)
	var done := progress >= 0.999
	_scaffold.visible = not done
	if _body:
		_body.visible = done


func set_condition_state(value: String) -> void:
	state_id = value
	var colours: Dictionary = _style.get("status_colours", {})
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color(colours.get(value, "#9e9e9e"))
	mat.emission_enabled = true
	mat.emission = mat.albedo_color
	mat.emission_energy_multiplier = 0.6
	_lamp.material_override = mat
	_refresh_label()


func set_patch_state(_grade: String, _remaining: float, _contamination: float) -> void:
	pass


func set_season(_season_id: String, _transition_progress: float) -> void:
	pass   # handled by the world for now


## CLAUDE.md names this set_owner(); Node.set_owner() already exists in Godot, so the adapter uses set_owner_identity().
func set_owner_identity(_owner_id: String, _display_colour: Color) -> void:
	pass


func play_feedback(event_id: String, _payload: Dictionary = {}) -> void:
	if event_id == "commissioned" or event_id == "evolved":
		_pulse = 1.0


## A construction site became the finished entity (same id, same slot).
func complete_as(new_kind: String) -> void:
	kind = new_kind
	_rebuild_body()
	set_construction_progress(1.0)
	play_feedback("commissioned")


# ------------------------------------------------------------------ internals
func set_selected(selected: bool) -> void:
	_label.modulate = Color(1, 0.95, 0.5) if selected else Color(1, 1, 1)


func _process(delta: float) -> void:
	if _pulse > 0.0:
		_pulse = max(0.0, _pulse - delta)
		_lamp.scale = Vector3.ONE * (1.0 + _pulse)


func _refresh_label() -> void:
	if _label:
		_label.text = "%s\n%s" % [definition_id.replace("_", " "), state_id.replace("_", " ")]


func _rebuild_body() -> void:
	if _body:
		_body.queue_free()
	var mesh: ArrayMesh = null
	var asset := ""
	if kind == "residence":
		asset = _style.get("residence_tiers", {}).get(definition_id, "")
	else:
		asset = _style.get("buildings", {}).get(definition_id, "")
	if asset != "":
		mesh = ObjLoader.load_mesh(_style.get("asset_root", "").path_join(asset + ".obj"))
	var instance := MeshInstance3D.new()
	if mesh:
		instance.mesh = mesh
	else:
		instance.mesh = _placeholder_mesh()
		var mat := StandardMaterial3D.new()
		var colours: Dictionary = _style.get("category_colours", {})
		mat.albedo_color = Color(colours.get("residence" if kind == "residence" else category, "#8899aa"))
		instance.material_override = mat
		instance.position = Vector3(0, 1.5, 0)
	instance.set_meta("asset", asset if mesh else "placeholder")
	_body = instance
	add_child(_body)


func _placeholder_mesh() -> Mesh:
	if kind == "residence":
		var dome := SphereMesh.new()
		dome.radius = 2.6
		dome.height = 3.0
		return dome
	var cyl := CylinderMesh.new()
	cyl.top_radius = 2.2
	cyl.bottom_radius = 2.8
	cyl.height = 3.0
	return cyl


func uses_asset() -> String:
	return str(_body.get_meta("asset")) if _body else ""
