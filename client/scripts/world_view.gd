class_name WorldView
extends Node3D
## Keeps one EntityView per domain entity in step with the bridge's player view.
## Player placements override the fallback layout. Layout is presentation-only: the Milestone A domain has districts, not coordinates, so each entity gets a
## deterministic slot in a band for its kind and category. A site keeps its slot when it becomes a facility.

const SPACING := 10.0
const BANDS := ["residence", "food", "extraction", "processing", "service", "logistics", "institution", "luxury", "other"]
const EntityViewScript = preload("res://scripts/entity_view.gd")

var style: Dictionary = {}
var building_categories: Dictionary = {}     # building id -> category (from hello)
var views: Dictionary = {}                   # entity id -> EntityView
var _slots: Dictionary = {}                  # entity id -> Vector3
var _footprints: Dictionary = {}
var obstacles: Array[AABB] = []
var spatial_enabled := false
var road_network: Node3D
var spatial_placements: Dictionary = {}
var _rotations: Dictionary = {}             # player placement yaw, retained through commissioning/evolution
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
	spatial_enabled = view.get("spatial", {}).get("enabled", false)
	spatial_placements = view.get("spatial", {}).get("placements", {})
	for id in spatial_placements:
		var placement: Dictionary = spatial_placements[id]
		var pair: Array = placement.get("position", [])
		if pair.size() < 2: continue
		var point := Vector3(float(pair[0]), 0, float(pair[1]))
		if terrain != null: point.y = terrain.height_at(point.x, point.z) + 0.05
		var footprint: Array = placement.get("footprint", [7, 7])
		reserve_placement(id, point, float(placement.get("yaw", 0)), Vector2(float(footprint[0]), float(footprint[1])))
		if views.has(id):
			views[id].position = point
			views[id].rotation.y = float(placement.get("yaw", 0))
	var seen := {}
	for id in spatial_placements:
		if spatial_placements[id].get("kind") == "pile":
			var pile := _ensure(id, "pile", "salvage", "logistics")
			pile.set_condition_state("awaiting_transport")
			seen[id] = true
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
		if f.get("cycle_progress") != null: v.set_recipe_state("", float(f["cycle_progress"]), "")
		seen[id] = true
	for id in spatial_placements:
		if views.has(id) and not spatial_placements[id].get("connected", false):
			views[id].set_condition_state("road_disconnected")
	for id in views.keys():
		if not seen.has(id):
			views[id].queue_free()
			views.erase(id)
			_slots.erase(id)
			_rotations.erase(id)
			_footprints.erase(id)


func _ensure(id: String, kind: String, definition: String, category: String) -> Node3D:
	if views.has(id):
		return views[id]
	var v: Node3D = EntityViewScript.new()
	v.setup(kind, style)
	v.set_category(category)
	v.set_entity_identity(id, definition)
	v.position = slot_for(id, "residence" if kind == "residence" else category)
	v.rotation.y = _rotations.get(id, 0.0)
	add_child(v)
	if not _footprints.has(id): _footprints[id] = mesh_footprint(v._body.mesh)
	views[id] = v
	return v


func reserve_placement(id: String, point: Vector3, yaw: float, footprint: Vector2 = Vector2(7, 7)) -> void:
	_footprints[id] = footprint
	_slots[id] = point
	_rotations[id] = yaw


func release_placement(id: String) -> void:
	if not views.has(id):
		_slots.erase(id)
		_rotations.erase(id)
		_footprints.erase(id)


func placement_reason(point: Vector3, yaw: float, footprint: Vector2 = Vector2(7, 7)) -> String:
	if terrain == null: return "Terrain unavailable"
	var low := INF
	var high := -INF
	# Sample the entire rotated footprint, including edges and centre.
	for x in [-footprint.x / 2, 0.0, footprint.x / 2]:
		for z in [-footprint.y / 2, 0.0, footprint.y / 2]:
			var sample := point + Vector3(x, 0, z).rotated(Vector3.UP, yaw)
			if absf(sample.x) > BasinTerrain.SIZE / 2 - 1 or absf(sample.z) > BasinTerrain.SIZE / 2 - 1:
				return "Outside the map"
			if not terrain.submerged and terrain.channel_distance_at(Vector2(sample.x, sample.z)) < 7.0:
				return "Too close to water"
			var height: float = terrain.height_at(sample.x, sample.z)
			low = minf(low, height)
			high = maxf(high, height)
	if high - low > 1.5: return "Ground too steep"
	if spatial_enabled and road_network != null:
		if road_network.footprint_overlaps_road(point, yaw, footprint): return "Footprint overlaps current lane"
		var connection: String = road_network.connection_reason(point, yaw, footprint)
		if connection != "": return connection
	for obstacle in obstacles:
		var centre := obstacle.get_center()
		if footprints_overlap(point, yaw, centre, 0, footprint, Vector2(obstacle.size.x, obstacle.size.z)):
			return "Blocked by rocks or a natural feature"
	for id in _slots:
		if footprints_overlap(point, yaw, _slots[id], _rotations.get(id, 0.0), footprint, _footprints.get(id, Vector2(7, 7))):
			return "Overlaps a building or construction site"
	return ""


static func footprints_overlap(a: Vector3, yaw_a: float, b: Vector3, yaw_b: float, size_a: Vector2 = Vector2(7, 7), size_b: Vector2 = Vector2(7, 7)) -> bool:
	# Separating-axis test for two rotated rectangular footprints, plus 0.3m clearance.
	var ax := Vector3.RIGHT.rotated(Vector3.UP, yaw_a)
	var az := Vector3.BACK.rotated(Vector3.UP, yaw_a)
	var bx := Vector3.RIGHT.rotated(Vector3.UP, yaw_b)
	var bz := Vector3.BACK.rotated(Vector3.UP, yaw_b)
	var difference := Vector3(b.x - a.x, 0, b.z - a.z)
	for axis in [ax, az, bx, bz]:
		var extent: float = size_a.x / 2 * absf(axis.dot(ax)) + size_a.y / 2 * absf(axis.dot(az)) + size_b.x / 2 * absf(axis.dot(bx)) + size_b.y / 2 * absf(axis.dot(bz)) + 0.3
		if absf(difference.dot(axis)) >= extent: return false
	return true


static func mesh_footprint(mesh: Mesh) -> Vector2:
	var bounds := mesh.get_aabb()
	return Vector2(maxf(7, 2 * maxf(absf(bounds.position.x), absf(bounds.end.x)) + 0.4),
		maxf(7, 2 * maxf(absf(bounds.position.z), absf(bounds.end.z)) + 0.4))
