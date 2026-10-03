class_name Hud
extends CanvasLayer
## Shell HUD: clock, season, colony state, speed controls, store, build list, event log and the stall inspector.
## Deliberately plain: Codex's UI contract (docs/art/SILICA_STREET_UI_CONTRACT.md) styles it later.

signal speed_selected(index: int)
signal autoplay_toggled(enabled: bool)
signal build_requested(building: String)
signal action_requested(cmd: Dictionary)
signal inspect_requested(entity_id: String)

const IconLoader = preload("res://scripts/icon_loader.gd")

var _clock: Label
var _colony: Label
var _status: Label
var _flash: Label
var _flash_timer := 0.0
var _speed_buttons: Array[Button] = []
var _store: RichTextLabel
var _events: RichTextLabel
var _build_list: ItemList
var _inspector_title: Label
var _inspector_body: RichTextLabel
var _actions: HBoxContainer
var _buildings: Dictionary = {}
var _last_inspection: Dictionary = {}
var _auto: CheckBox
var _event_lines: PackedStringArray = []
var _style: Dictionary = {}
var _headline_values: Dictionary = {}


func configure_style(style: Dictionary) -> void:
	_style = style


func _ready() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	var top := _panel(root, Vector2(10, 10), Vector2(1580, 92))
	var top_stack := VBoxContainer.new()
	top_stack.add_theme_constant_override("separation", 3)
	top.add_child(top_stack)
	var bar := HBoxContainer.new()
	bar.add_theme_constant_override("separation", 14)
	top_stack.add_child(bar)
	_clock = Label.new()
	_clock.custom_minimum_size = Vector2(250, 0)
	bar.add_child(_clock)
	_colony = Label.new()
	_colony.custom_minimum_size = Vector2(430, 0)
	bar.add_child(_colony)
	var labels := ["II", "1×", "2×", "4×", "8×", "16×", "32×"]
	for i in labels.size():
		var b := Button.new()
		b.text = labels[i]
		b.toggle_mode = true
		b.tooltip_text = "Pause (Space)" if i == 0 else "Speed %s (key %d)" % [labels[i], i]
		b.pressed.connect(func(): speed_selected.emit(i))
		bar.add_child(b)
		_speed_buttons.append(b)
	_auto = CheckBox.new()
	var auto := _auto
	auto.text = "Autoplay"
	auto.tooltip_text = "Let the reference governor play (a balance aid, not game AI)"
	auto.toggled.connect(func(on): autoplay_toggled.emit(on))
	bar.add_child(auto)
	var resources := HBoxContainer.new()
	resources.add_theme_constant_override("separation", 18)
	top_stack.add_child(resources)
	_resource_chip(resources, "raw_silicate", "Raw Silicate")
	_resource_chip(resources, "prepared_silica", "Prepared Silica")
	_resource_chip(resources, "staple", "Staple")
	_resource_chip(resources, "repair_enzyme", "Repair Enzyme")
	_resource_chip(resources, "builder", "Builders")
	show_speed(1, 1)

	var left := _panel(root, Vector2(10, 112), Vector2(300, 712))
	var lbox := VBoxContainer.new()
	left.add_child(lbox)
	lbox.add_child(_heading("Store"))
	_store = RichTextLabel.new()
	_store.custom_minimum_size = Vector2(280, 300)
	_store.bbcode_enabled = true
	lbox.add_child(_store)
	lbox.add_child(_heading("Build (double-click)"))
	_build_list = ItemList.new()
	_build_list.custom_minimum_size = Vector2(280, 330)
	_build_list.item_activated.connect(func(index): build_requested.emit(_build_list.get_item_metadata(index)))
	lbox.add_child(_build_list)
	var reef := Button.new()
	reef.text = "Why no Memory Reef yet?"
	reef.pressed.connect(func(): inspect_requested.emit("great_work"))
	lbox.add_child(reef)

	var right := _panel(root, Vector2(1240, 112), Vector2(350, 520))
	right.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT, Control.PRESET_MODE_KEEP_SIZE, 10)
	right.position.y = 112
	var rbox := VBoxContainer.new()
	right.add_child(rbox)
	_inspector_title = _heading("Inspector: click anything")
	rbox.add_child(_inspector_title)
	_inspector_body = RichTextLabel.new()
	_inspector_body.custom_minimum_size = Vector2(330, 420)
	_inspector_body.bbcode_enabled = true
	rbox.add_child(_inspector_body)
	_actions = HBoxContainer.new()
	rbox.add_child(_actions)

	var bottom := _panel(root, Vector2(320, 720), Vector2(900, 170))
	bottom.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_LEFT, Control.PRESET_MODE_KEEP_SIZE, 10)
	bottom.position.x = 320
	_events = RichTextLabel.new()
	_events.custom_minimum_size = Vector2(880, 150)
	_events.scroll_following = true
	bottom.add_child(_events)

	_status = Label.new()
	_status.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	_status.add_theme_font_size_override("font_size", 26)
	root.add_child(_status)
	_flash = Label.new()
	_flash.position = Vector2(330, 60)
	root.add_child(_flash)


func _panel(parent: Control, pos: Vector2, size: Vector2) -> PanelContainer:
	var p := PanelContainer.new()
	p.position = pos
	p.custom_minimum_size = size
	p.mouse_filter = Control.MOUSE_FILTER_STOP
	parent.add_child(p)
	return p


func _heading(text: String) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", 18)
	return l


func _resource_chip(parent: Container, icon: String, label_text: String) -> void:
	var chip := HBoxContainer.new()
	chip.add_theme_constant_override("separation", 5)
	var image := TextureRect.new()
	image.custom_minimum_size = Vector2(26, 26)
	image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	var icon_name := icon if icon != "staple" else "staple_food"
	image.texture = IconLoader.load_svg(str(_style.get("icon_root", "")).path_join(icon_name + ".svg"), 0.6)
	chip.add_child(image)
	var value := Label.new()
	value.text = "%s  –" % label_text
	value.custom_minimum_size = Vector2(130 if icon != "builder" else 150, 0)
	chip.add_child(value)
	_headline_values[icon] = value
	parent.add_child(chip)


# ------------------------------------------------------------------ updates
func configure(hello: Dictionary) -> void:
	_buildings = hello.get("buildings", {})
	_build_list.clear()
	var names := _buildings.keys()
	names.sort()
	for b in names:
		var cost: Dictionary = _buildings[b].get("cost", {})
		var parts := PackedStringArray()
		for r in cost:
			parts.append("%d %s" % [cost[r], r.replace("_", " ")])
		var index := _build_list.add_item("%s  (%s)" % [b.replace("_", " "), ", ".join(parts)])
		_build_list.set_item_metadata(index, b)


func show_status(text: String, error: bool) -> void:
	_status.text = text
	_status.modulate = Color(1, 0.5, 0.5) if error else Color(1, 1, 1)


func show_speed(index: int, _value: int) -> void:
	for i in _speed_buttons.size():
		_speed_buttons[i].button_pressed = i == index


func flash(text: String, error: bool) -> void:
	_flash.text = text
	_flash.modulate = Color(1, 0.6, 0.5) if error else Color(0.7, 1, 0.7)
	_flash_timer = 4.0


func _process(delta: float) -> void:
	if _flash_timer > 0.0:
		_flash_timer -= delta
		if _flash_timer <= 0.0:
			_flash.text = ""


func show_view(view: Dictionary) -> void:
	_auto.set_pressed_no_signal(view.get("autoplay", false))
	var to_next := int(view.get("seconds_to_next_season", 0))
	_clock.text = "%s   %s → %s in %d:%02d" % [view.get("time", "--:--"), str(view.get("season", "")).replace("_", " "),
		str(view.get("next_season", "")).replace("_", " "), to_next / 60, to_next % 60]
	var food = view.get("food_minutes")
	_colony.text = "Pop %s · Food %s min%s · Builders %s · Upkeep %s" % [
		str(view.get("population", 0)), "–" if food == null else "%.1f" % food,
		" (EMERGENCY)" if view.get("food_emergency", false) else "", str(view.get("builders", "")).replace("_", " "),
		str(view.get("maintenance_upkeep", ""))]
	var store: Dictionary = view.get("store", {})
	_set_headline("raw_silicate", int(store.get("raw_silicate", 0)))
	_set_headline("prepared_silica", int(store.get("prepared_silica", 0)))
	_set_headline("staple", int(store.get("staple", 0)))
	_set_headline("repair_enzyme", int(store.get("repair_enzyme", 0)))
	if _headline_values.has("builder"):
		_headline_values["builder"].text = "Builders  %s" % str(view.get("builders", "idle")).replace("_", " ")
	var keys := store.keys()
	keys.sort()
	var text := ""
	for k in keys:
		if int(store[k]) != 0:
			text += "%s  [b]%d[/b]\n" % [k.replace("_", " "), int(store[k])]
	_store.text = text
	for e in view.get("events", []):
		_event_lines.append(e)
	if _event_lines.size() > 60:
		_event_lines = _event_lines.slice(_event_lines.size() - 60)
	_events.text = "\n".join(_event_lines)


func _set_headline(key: String, amount: int) -> void:
	if _headline_values.has(key):
		var label: Label = _headline_values[key]
		var title := str(label.text).split("  ")[0]
		label.text = "%s  %d" % [title, amount]


func clear_inspection() -> void:
	_inspector_title.text = "Inspector: click anything"
	_inspector_body.text = ""
	for c in _actions.get_children():
		c.queue_free()
	_last_inspection = {}


func show_inspection(reply: Dictionary) -> void:
	if not reply.get("ok", false):
		_inspector_body.text = "[color=#ff8a80]%s[/color]" % ", ".join(PackedStringArray(reply.get("reasons", [])))
		return
	var kind: String = reply.get("kind", "")
	var entity: String = reply.get("entity", "")
	_inspector_title.text = "%s: %s" % [kind.capitalize(), entity]
	var lines := PackedStringArray()
	match kind:
		"facility":
			lines.append("Building: %s" % reply.get("building"))
			lines.append("Status: [b]%s[/b] %s" % [reply.get("status"), reply.get("detail", "")])
			lines.append("Staffing: %d%%" % int(round(float(reply.get("staffing", 0)) * 100)))
			if reply.get("cycle_progress") != null:
				lines.append("Cycle: %d%%" % int(round(float(reply["cycle_progress"]) * 100)))
		"site":
			lines.append("Building: %s" % reply.get("builds"))
			lines.append("State: [b]%s[/b]" % reply.get("state"))
			lines.append("Work: %d%%" % int(round(float(reply.get("work_progress", 0)) * 100)))
			var waited: Dictionary = reply.get("waited_minutes", {})
			for k in waited:
				lines.append("  waited %s min: %s" % [str(waited[k]), k])
		"residence":
			lines.append("Tier: [b]%s[/b] · %s" % [reply.get("tier"), reply.get("condition")])
			lines.append("Population %s / %s" % [str(reply.get("population")), str(reply.get("capacity"))])
			var services: Dictionary = reply.get("services_for_next_tier", {})
			for s in services:
				lines.append("  %s %s" % ["✔" if services[s] else "✘", s])
		"great_work":
			lines.append("Memory Reef: %s, stage %d" % ["begun" if reply.get("begun") else "not begun", int(reply.get("stage", 0))])
	var reasons: Array = reply.get("reasons", [])
	if reasons.is_empty():
		lines.append("\n[color=#a5d6a7]Nothing is blocking this.[/color]")
	else:
		lines.append("\n[b]Why it is not progressing:[/b]")
		for r in reasons:
			lines.append("[color=#ffcc80]• %s[/color]" % str(r).replace("_", " "))
	_inspector_body.text = "\n".join(lines)
	if _last_inspection.get("entity", "") != entity or _last_inspection.get("kind", "") != kind:
		_rebuild_actions(kind, entity, reply)
	_last_inspection = reply


func _rebuild_actions(kind: String, entity: String, reply: Dictionary) -> void:
	for c in _actions.get_children():
		c.queue_free()
	match kind:
		"facility":
			_action("Pause", {"do": "pause", "target": entity})
			_action("Resume", {"do": "resume", "target": entity})
		"site":
			_action("Cancel", {"do": "cancel", "target": entity})
		"residence":
			_action("Evolve", {"do": "evolve", "residence": entity})
		"great_work":
			if not reply.get("begun", false):
				_action("Begin", {"do": "begin_great_work", "priority": 5})


func _action(text: String, cmd: Dictionary) -> void:
	var b := Button.new()
	b.text = text
	b.pressed.connect(func(): action_requested.emit(cmd))
	_actions.add_child(b)
