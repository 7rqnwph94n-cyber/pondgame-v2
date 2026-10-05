class_name WorldView
extends Node3D
## Keeps one EntityView per domain entity in step with the bridge's player view.
## Layout is presentation-only: the Milestone A domain has districts, not coordinates, so each entity gets a
## deterministic slot in a band for its kind and category. A site keeps its slot when it becomes a facility.

const SPACING := 10.0
const BANDS := ["residence", "food", "extraction", "processing", "service", "logistics", "institution", "luxury", "other"]
const EntityViewScript = preload("res://scripts/entity_view.gd")

var style: Dictionary = {}
var building_categories: Dictionary = {}     # building id -> category (from hello)
var views: Dictionary = {}                   # entity id -> EntityView
var _slots: Dictionary = {}                  # entity id -> Vector3
var _band_counts: Dictionary = {}
var terrain: Node3D


func configure_terrain(value: Node3D) -> void:
	terrain = value


func configure(asset_style: Dictionary, hello: Dictionary) -> void:
	style = asset_style
	for building in hello.get("buildings", {}):
		building_categories[building] = hello["buildings"][building].get("category", "other")


func slot_for(entity_id: String, band: String) -> Vector3:
	if _slots.has(entity_id):
		return _slots[entity_id]
	var map: Dictionary = style.get("environment", {}).get("map", {})
	var centres: Dictionary = map.get("district_centres", {})
	var fallback_row: int = BANDS.find(band)
	if fallback_row < 0:
		fallback_row = BANDS.size() - 1
	var pair: Array = centres.get(band, [0, (fallback_row - 3) * SPACING])
	var centre := Vector3(float(pair[0]), 0, float(pair[1]))
	var index: int = _band_counts.get(band, 0)
	var position := centre
	for attempt in range(120):
		var ring: int = index / 6
		var angle := float(index % 6) / 6.0 * TAU + float(ring) * 0.35
		var radius := 3.4 + float(ring) * 5.8
		position = centre + Vector3(cos(angle) * radius, 0, sin(angle) * radius)
		index += 1
		if terrain != null and not terrain.has_dry_footprint_at(position.x, position.z):
			continue
		var clear := true
		for previous in _slots.values():
			if Vector2(position.x, position.z).distance_to(Vector2(previous.x, previous.z)) < 8.0:
				clear = false
				break
		if clear:
			break
	_band_counts[band] = index
	if terrain != null:
		position.y = terrain.height_at(position.x, position.z) + 0.05
	_slots[entity_id] = position
	return position


func sync(view: Dictionary) -> void:
	var seen := {}
	for id in view.get("residences", {}):
		var r: Dictionary = view["residences"][id]
		var v := _ensure(id, "residence", r.get("tier", "shelter"), "residence")
		if v.kind == "site":         # a shelter site was commissioned into a home
			v.definition_id = r.get("tier", "shelter")
			v.complete_as("residence")
		elif v.definition_id != r.get("tier"):
			v.set_entity_identity(id, r.get("tier"))
			v.play_feedback("evolved")
		v.set_condition_state(r.get("condition", "normal"))
		seen[id] = true
	for id in view.get("sites", {}):
		var s: Dictionary = view["sites"][id]
		if s.get("kind", "building") != "building":
			continue
		var category: String = "residence" if s.get("target", "") == "shelter" else building_categories.get(s.get("target", ""), "other")
		var v := _ensure(id, "site", s.get("target", ""), category)
		v.set_condition_state(s.get("state", "awaiting_materials"))
		v.set_construction_progress(float(s.get("progress", 0.05)))
		seen[id] = true
	for id in view.get("facilities", {}):
		var f: Dictionary = view["facilities"][id]
		var v := _ensure(id, "facility", f.get("building", ""), f.get("category", "other"))
		if v.kind == "site":         # commissioned: same id, same slot
			v.complete_as("facility")
		v.set_condition_state("paused" if f.get("paused", false) else f.get("status", "idle"))
		seen[id] = true
	for id in views.keys():
		if not seen.has(id):
			views[id].queue_free()
			views.erase(id)


func _ensure(id: String, kind: String, definition: String, category: String) -> Node3D:
	if views.has(id):
		return views[id]
	var v: Node3D = EntityViewScript.new()
	v.setup(kind, style)
	v.set_category(category)
	v.set_entity_identity(id, definition)
	v.position = slot_for(id, "residence" if kind == "residence" else category)
	add_child(v)
	views[id] = v
	return v
