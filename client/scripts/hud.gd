class_name Hud
extends CanvasLayer
## Shell HUD: clock, season, colony state, speed controls, store, build list, event log and the stall inspector.
## Deliberately plain: Codex's UI contract (docs/art/SILICA_STREET_UI_CONTRACT.md) styles it later.

signal speed_selected(index: int)
signal autoplay_toggled(enabled: bool)
signal build_requested(building: String)
signal road_requested
signal action_requested(cmd: Dictionary)

const STAFF_FIRST_RANK := 3   # same rank as construction: above other production, below services and Builders
signal inspect_requested(entity_id: String)

signal zoom_requested(factor: float)
signal follow_requested(entity_id: String)
const Glyph = preload("res://scripts/control_icons.gd")
const BUILD_COPY := {"shelter": "Homes for General workers", "culture_bed": "Grows Staple food from Biomass", "photosynthetic_field": "Produces Biomass", "silicate_pit": "Extracts Raw Silicate", "mineral_washery": "Prepares Silica for construction", "clean_flow_node": "Provides clean flow to homes", "waste_collector": "Collects household waste", "waste_digester": "Produces Repair Enzyme from waste", "maintenance_organ": "Maintains nearby homes", "ceramic_kiln": "Fires construction Ceramic", "first_nursery": "Supports population growth", "general_store": "Colony storage", "survey_organ": "Surveys mineral resources"}
var _root: Control
var _food: Label
var _summary: Label
var _catalogue: VBoxContainer
var _build_heading: Label
var _category_buttons := {}
var _active_category := ""
var _context: PopupMenu
var _inventory: PanelContainer
var _inventory_values := {}
var _stock_grid: GridContainer
var _context_commands: Array[Dictionary] = []

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
var _inspector_panel: PanelContainer
var _build_panel: PanelContainer
var _event_panel: PanelContainer
var _build_toggle: Button
var _event_toggle: Button


func configure_style(style: Dictionary) -> void:
	_style = style


func _ready() -> void:
	var root := Control.new()
	root.set_anchors_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_root = root
	var theme := Theme.new()
	var panel := StyleBoxFlat.new()
	panel.bg_color = Color("#102c30f2")
	panel.border_color = Color("#477c78")
	panel.set_border_width_all(1)
	panel.set_corner_radius_all(9)
	panel.content_margin_left = 12
	panel.content_margin_right = 12
	panel.content_margin_top = 10
	panel.content_margin_bottom = 10
	theme.set_stylebox("panel", "PanelContainer", panel)
	for state in ["normal", "hover", "pressed", "focus"]:
		var button := panel.duplicate()
		button.bg_color = Color("#28524f") if state == "hover" else (Color("#386b60") if state == "pressed" else Color("#163a3c"))
		button.set_content_margin_all(7)
		theme.set_stylebox(state, "Button", button)
	theme.default_font_size = 15
	root.theme = theme
	var top := _panel(root, Vector2(96, 10), Vector2(800, 74))
	top.set_anchors_preset(Control.PRESET_TOP_WIDE)
	top.offset_left = 96
	top.offset_right = -10
	var top_stack := VBoxContainer.new()
	top.add_child(top_stack)
	var bar := HBoxContainer.new()
	bar.add_theme_constant_override("separation", 12)
	top_stack.add_child(bar)
	_clock = Label.new()
	_clock.custom_minimum_size = Vector2(145, 0)
	bar.add_child(_clock)
	bar.add_child(_small_icon("unit", "Population. Hover the number for growth blockers."))
	_colony = Label.new()
	_colony.mouse_filter = Control.MOUSE_FILTER_STOP
	_colony.custom_minimum_size = Vector2(48, 0)
	bar.add_child(_colony)
	_food = Label.new()
	_food.mouse_filter = Control.MOUSE_FILTER_STOP
	bar.add_child(_small_icon("food", "Food reserves, in minutes of consumption."))
	bar.add_child(_food)
	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	bar.add_child(spacer)
	var labels := ["", "1×", "2×", "4×", "8×", "16×", "32×"]
	for i in labels.size():
		var b := Button.new()
		b.text = labels[i]
		b.focus_mode = Control.FOCUS_NONE
		if i == 0: b.icon = Glyph.texture("pause")
		b.expand_icon = true
		b.custom_minimum_size = Vector2(34, 30)
		b.toggle_mode = true
		b.tooltip_text = "Pause / resume (Space)" if i == 0 else "Speed %s (key %d)" % [labels[i], i]
		b.pressed.connect(func(): speed_selected.emit((0 if b.button_pressed else 1) if i == 0 else i))
		bar.add_child(b)
		_speed_buttons.append(b)
	_auto = CheckBox.new()
	_auto.focus_mode = Control.FOCUS_NONE
	_auto.icon = Glyph.texture("play")
	_auto.expand_icon = true
	_auto.custom_minimum_size = Vector2(48, 32)
	_auto.tooltip_text = "Autoplay: let the colony governor demonstrate the opening."
	_auto.toggled.connect(func(on): autoplay_toggled.emit(on))
	bar.add_child(_auto)
	_event_toggle = _icon_button("log", "Recent events (L)")
	_event_toggle.toggle_mode = true
	_event_toggle.toggled.connect(func(open): _event_panel.visible = open)
	bar.add_child(_event_toggle)
	var resources := HBoxContainer.new()
	resources.add_theme_constant_override("separation", 18)
	top_stack.add_child(resources)
	for entry in [["raw_silicate", "Raw Silicate"], ["prepared_silica", "Prepared Silica"], ["staple", "Staple food"], ["carbonate", "Carbonate"], ["biomass", "Biomass"], ["repair_enzyme", "Repair Enzyme"], ["stored_value", "Trade credit"], ["builder", "Builders"]]:
		_resource_chip(resources, entry[0], entry[1])
	show_speed(1, 1)

	var rail := _panel(root, Vector2(10, 10), Vector2(76, 790))
	rail.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	rail.offset_top = 10
	rail.offset_bottom = -10
	var rail_box := VBoxContainer.new()
	rail_box.add_theme_constant_override("separation", 7)
	rail.add_child(rail_box)
	var brand := _heading("POND")
	brand.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	rail_box.add_child(brand)
	for category in ["residence", "food", "extraction", "processing", "service", "logistics", "institution", "luxury"]:
		var b := _icon_button("home" if category == "residence" else category, "%s buildings — click to choose" % category.capitalize())
		b.custom_minimum_size = Vector2(48, 48)
		b.toggle_mode = true
		b.pressed.connect(func(): open_build_category(category))
		rail_box.add_child(b)
		_category_buttons[category] = b
	var road := _icon_button("road", "Roads (T) — click start, then end; right-click finishes")
	road.pressed.connect(func(): road_requested.emit(); _close_build_panel())
	rail_box.add_child(road)
	var stock := _icon_button("stock", "All colony resources — click for stock; hover icons for names")
	stock.pressed.connect(func(): _inventory.visible = not _inventory.visible)
	rail_box.add_child(stock)
	var reef := _icon_button("reef", "Memory Reef — inspect unlock requirements")
	reef.pressed.connect(func(): inspect_requested.emit("great_work"))
	rail_box.add_child(reef)
	var rail_spacer := Control.new()
	rail_spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	rail_box.add_child(rail_spacer)
	for entry in [["plus", "Zoom in (+, wheel or trackpad)", 0.85], ["minus", "Zoom out (−, wheel or trackpad)", 1.18], ["reset", "Reset camera (Home)", 0.0]]:
		var b := _icon_button(entry[0], entry[1])
		b.pressed.connect(func(): zoom_requested.emit(float(entry[2])))
		rail_box.add_child(b)

	_build_panel = _panel(root, Vector2(96, 94), Vector2(270, 560))
	_build_panel.visible = false
	var lbox := VBoxContainer.new()
	_build_panel.add_child(lbox)
	_build_heading = _heading("Build")
	lbox.add_child(_build_heading)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(246, 490)
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	lbox.add_child(scroll)
	_catalogue = VBoxContainer.new()
	_catalogue.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(_catalogue)
	_store = RichTextLabel.new()
	_build_list = ItemList.new() # compatibility; visible catalogue uses single-click icon buttons
	lbox.add_child(_store)
	lbox.add_child(_build_list)
	_store.hide()
	_build_list.hide()

	_inspector_panel = _panel(root, Vector2(0, 94), Vector2(300, 200))
	_inspector_panel.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT, Control.PRESET_MODE_KEEP_SIZE, 10)
	_inspector_panel.position.y = 94
	_inspector_panel.hide()
	var rbox := VBoxContainer.new()
	_inspector_panel.add_child(rbox)
	var title_row := HBoxContainer.new()
	rbox.add_child(title_row)
	_inspector_title = _heading("Inspector")
	_inspector_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title_row.add_child(_inspector_title)
	var close := _icon_button("cancel", "Close inspection (Esc)")
	close.pressed.connect(func(): inspect_requested.emit(""))
	title_row.add_child(close)
	_summary = Label.new()
	_summary.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_summary.custom_minimum_size = Vector2(274, 50)
	rbox.add_child(_summary)
	_actions = HBoxContainer.new()
	rbox.add_child(_actions)
	var details := _icon_button("info", "Detailed requirements, workforce changes and input competitors")
	details.toggle_mode = true
	details.toggled.connect(func(on): _inspector_body.visible = on)
	rbox.add_child(details)
	_inspector_body = RichTextLabel.new()
	_inspector_body.custom_minimum_size = Vector2(274, 270)
	_inspector_body.bbcode_enabled = true
	_inspector_body.hide()
	rbox.add_child(_inspector_body)

	_event_panel = _panel(root, Vector2(600, 690), Vector2(600, 160))
	_event_panel.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT, Control.PRESET_MODE_KEEP_SIZE, 10)
	_event_panel.hide()
	_events = RichTextLabel.new()
	_events.custom_minimum_size = Vector2(580, 140)
	_events.scroll_following = true
	_event_panel.add_child(_events)
	_status = Label.new()
	_status.position = Vector2(110, 820)
	_status.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_status.add_theme_font_size_override("font_size", 18)
	root.add_child(_status)
	_flash = Label.new()
	_flash.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_flash.position = Vector2(110, 860)
	root.add_child(_flash)
	_inventory = _panel(root, Vector2(96, 94), Vector2(370, 220))
	_inventory.hide()
	var stock_box := VBoxContainer.new()
	_inventory.add_child(stock_box)
	stock_box.add_child(_heading("Resources"))
	var stock_grid := GridContainer.new()
	_stock_grid = stock_grid
	stock_grid.name = "Grid"
	stock_grid.columns = 4
	stock_grid.add_theme_constant_override("h_separation", 16)
	stock_grid.add_theme_constant_override("v_separation", 12)
	stock_box.add_child(stock_grid)
	_context = PopupMenu.new()
	_context.id_pressed.connect(_context_action)
	add_child(_context)


func _icon_button(icon: String, tooltip: String) -> Button:
	var b := Button.new()
	b.icon = Glyph.texture(icon)
	b.expand_icon = true
	b.custom_minimum_size = Vector2(36, 36)
	b.tooltip_text = tooltip
	b.focus_mode = Control.FOCUS_NONE
	return b


func _small_icon(icon: String, tooltip: String) -> TextureRect:
	var image := TextureRect.new()
	image.texture = Glyph.texture(icon)
	image.custom_minimum_size = Vector2(24, 24)
	image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	image.tooltip_text = tooltip
	return image


func open_build_category(category: String = "residence") -> void:
	var closing := _build_panel.visible and _active_category == category
	_inventory.hide()
	_active_category = category
	_build_panel.visible = not closing
	for key in _category_buttons:
		_category_buttons[key].set_pressed_no_signal(key == category and not closing)
	_build_heading.text = category.capitalize()
	for button in _catalogue.get_children(): button.queue_free()
	var names := _buildings.keys()
	names.sort()
	for id in names:
		var definition: Dictionary = _buildings[id]
		var cat: String = "residence" if id == "shelter" else str(definition.get("category", "other"))
		if cat != category: continue
		var b := _icon_button("home" if cat == "residence" else cat, _build_tooltip(id, definition))
		b.text = str(id).replace("_", " ").capitalize()
		b.alignment = HORIZONTAL_ALIGNMENT_LEFT
		b.custom_minimum_size = Vector2(240, 48)
		b.set_meta("building", id)
		b.pressed.connect(func(): build_requested.emit(id); _close_build_panel())
		_catalogue.add_child(b)


func _close_build_panel() -> void:
	_build_panel.hide()
	for button in _category_buttons.values(): button.set_pressed_no_signal(false)


func _build_tooltip(id: String, definition: Dictionary) -> String:
	var parts := PackedStringArray()
	for good in definition.get("cost", {}):
		parts.append("%s %s" % [definition["cost"][good], str(good).replace("_", " ")])
	var jobs := PackedStringArray()
	for job in definition.get("jobs", {}):
		jobs.append("%s %s" % [definition["jobs"][job], str(job).capitalize()])
	return "%s\n%s\nCost: %s\nWorkers: %s\nClick to choose a position. R rotates; right-click cancels." % [str(id).replace("_", " ").capitalize(), BUILD_COPY.get(id, "Colony infrastructure"), ", ".join(parts), ", ".join(jobs)]


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		if event.keycode == KEY_B:
			open_build_category()
		elif event.keycode == KEY_L:
			_event_toggle.button_pressed = not _event_toggle.button_pressed


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
	var path := str(_style.get("icon_root", "")).path_join(icon_name + ".svg")
	image.texture = IconLoader.load_svg(path, 0.6) if FileAccess.file_exists(path) else Glyph.texture(icon_name)
	chip.add_child(image)
	var value := Label.new()
	value.text = "–"
	chip.tooltip_text = label_text
	chip.mouse_filter = Control.MOUSE_FILTER_STOP
	image.mouse_filter = Control.MOUSE_FILTER_IGNORE
	value.mouse_filter = Control.MOUSE_FILTER_IGNORE
	value.custom_minimum_size = Vector2(35 if icon != "builder" else 90, 0)
	chip.add_child(value)
	_headline_values[icon] = value
	parent.add_child(chip)


# ------------------------------------------------------------------ updates
func configure(hello: Dictionary) -> void:
	_auto.disabled = not hello.get("autoplay_available", true)
	if _auto.disabled: _auto.tooltip_text = "Build connected roads and place buildings yourself"
	var grid := _stock_grid
	for child in grid.get_children(): child.queue_free()
	_inventory_values.clear()
	for resource in hello.get("resources", []):
		var chip := HBoxContainer.new()
		chip.tooltip_text = str(resource).replace("_", " ").capitalize()
		var image := TextureRect.new()
		var icon_id: String = "staple_food" if resource == "staple" else str(resource)
		var path := str(_style.get("icon_root", "")).path_join(icon_id + ".svg")
		image.texture = IconLoader.load_svg(path, 0.6) if FileAccess.file_exists(path) else Glyph.texture(str(resource))
		image.custom_minimum_size = Vector2(28, 28)
		image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		image.mouse_filter = Control.MOUSE_FILTER_IGNORE
		chip.add_child(image)
		var amount := Label.new()
		amount.custom_minimum_size.x = 34
		amount.mouse_filter = Control.MOUSE_FILTER_IGNORE
		chip.add_child(amount)
		grid.add_child(chip)
		_inventory_values[resource] = amount
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
	_clock.text = "%s · %s" % [view.get("time", "--:--"), str(view.get("season", "")).replace("_", " ").capitalize()]
	_clock.tooltip_text = "%s in %d:%02d" % [str(view.get("next_season", "")).replace("_", " ").capitalize(), to_next / 60, to_next % 60]
	_clock.mouse_filter = Control.MOUSE_FILTER_STOP
	var food = view.get("food_minutes")
	var growth_blockers: Array = view.get("colony_blockers", [])
	_colony.text = "%s%s" % [str(view.get("population", 0)), " !" if not growth_blockers.is_empty() else ""]
	_colony.tooltip_text = "Population: %s\n%s" % [view.get("population", 0), str(growth_blockers[0].get("text", "stalled")) if not growth_blockers.is_empty() else "Population growth is not blocked"]
	if view.get("residences", {}).is_empty() and view.get("facilities", {}).is_empty():
		_colony.tooltip_text += "\nFounders wait off-map. Draw a road (T), connect shelter entrances, then start time (Space)."
	_food.text = "%s min%s" % ["–" if food == null else "%.1f" % food, " !" if view.get("food_emergency", false) else ""]
	_food.modulate = Color("#ff8a70") if view.get("food_emergency", false) else Color.WHITE
	_food.tooltip_text = "Food reserve at current consumption.\nUpkeep: %s" % view.get("maintenance_upkeep", "")
	var store: Dictionary = view.get("store", {})
	_set_headline("raw_silicate", int(store.get("raw_silicate", 0)))
	_set_headline("prepared_silica", int(store.get("prepared_silica", 0)))
	_set_headline("staple", int(store.get("staple", 0)))
	_set_headline("carbonate", int(store.get("carbonate", 0)))
	_set_headline("biomass", int(store.get("biomass", 0)))
	_set_headline("repair_enzyme", int(store.get("repair_enzyme", 0)))
	_set_headline("stored_value", int(store.get("stored_value", 0)))
	if _headline_values.has("builder"):
		_headline_values["builder"].text = "%s" % str(view.get("builders", "idle")).replace("_", " ")
	for resource in _inventory_values:
		_inventory_values[resource].text = str(int(store.get(resource, 0)))
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
		label.text = str(amount)


func clear_inspection() -> void:
	_inspector_panel.visible = false
	_inspector_title.text = "Inspector: click anything"
	_inspector_body.text = ""
	for c in _actions.get_children():
		c.queue_free()
	_last_inspection = {}


func show_inspection(reply: Dictionary) -> void:
	_inspector_panel.visible = true
	if not reply.get("ok", false):
		_inspector_body.text = "[color=#ff8a80]%s[/color]" % ", ".join(PackedStringArray(reply.get("reasons", [])))
		return
	var kind: String = reply.get("kind", "")
	var entity: String = reply.get("entity", "")
	_inspector_title.text = str(reply.get("building", reply.get("builds", reply.get("tier", "Memory Reef")))).replace("_", " ").capitalize()
	_summary.text = _inspection_summary(reply)
	var lines := PackedStringArray()
	match kind:
		"facility":
			lines.append("Building: %s" % reply.get("building"))
			lines.append("Status: [b]%s[/b] %s" % [_facility_status_copy(reply), reply.get("detail", "")])
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
			if reply.get("next_tier") != null:
				lines.append("Next tier: %s" % str(reply["next_tier"]).capitalize())
				var workforce_change := _workforce_change_copy(reply.get("evolution_workforce_change", {}))
				if workforce_change != "":
					lines.append("[color=#ffcc80]On evolution: %s[/color]" % workforce_change)
			var services: Dictionary = reply.get("services_for_next_tier", {})
			for s in services:
				lines.append("  %s %s" % ["✔" if services[s] else "✘", s])
		"great_work":
			lines.append("Memory Reef: %s, stage %d" % ["begun" if reply.get("begun") else "not begun", int(reply.get("stage", 0))])
	var reasons: Array = reply.get("reasons", [])
	if reasons.is_empty():
		if kind == "facility" and reply.get("status") == "idle":
			lines.append("\nNo current task; assigned workers remain occupied here.")
		else:
			lines.append("\n[color=#a5d6a7]Nothing is blocking this.[/color]")
	else:
		lines.append("\n[b]Why it is not progressing:[/b]")
		for r in reasons:
			lines.append("[color=#ffcc80]• %s[/color]" % str(r).replace("_", " "))
	lines.append_array(_consumer_copy(reply))
	_inspector_body.text = "\n".join(lines)
	if _last_inspection.get("entity", "") != entity or _last_inspection.get("kind", "") != kind \
			or _last_inspection.get("labour_priority_overridden") != reply.get("labour_priority_overridden") \
			or _last_inspection.get("status") != reply.get("status") \
			or _consumer_ids(_last_inspection) != _consumer_ids(reply):
		_rebuild_actions(kind, entity, reply)
	_last_inspection = reply.duplicate(true)


func _consumer_ids(reply: Dictionary) -> Array:
	var ids: Array = []
	for blocker in reply.get("blockers", []):
		if blocker.get("code") == "waiting_input":
			for rows in blocker.get("params", {}).get("consumers", {}).values():
				for row in rows:
					if not ids.has(row["entity"]):
						ids.append(row["entity"])
	ids.sort()
	return ids


func _consumer_copy(reply: Dictionary) -> PackedStringArray:
	var lines := PackedStringArray()
	for blocker in reply.get("blockers", []):
		if blocker.get("code") != "waiting_input":
			continue
		var consumers: Dictionary = blocker.get("params", {}).get("consumers", {})
		for good in consumers:
			for row in consumers[good]:
				var outputs := PackedStringArray()
				for output in row.get("outputs", {}):
					outputs.append(str(output).replace("_", " "))
				lines.append("\n[b]%s also uses %s[/b] (%s): %s per cycle → %s." % [
					str(row["building"]).replace("_", " ").capitalize(), str(good).replace("_", " "),
					row["entity"], row["per_cycle"], ", ".join(outputs)])
				if row.get("state") == "waiting_input":
					lines.append("It is waiting for inputs too; it competes for the next available batch.")
				if int(row.get("held", 0)) > 0:
					lines.append("%s already reserved in its current cycle; pausing does not return it." % row["held"])
	if not lines.is_empty():
		lines.append("Inspect a competing building to pause it temporarily. Its output will stop too; check food reserves before pausing food production, and resume when construction has its materials.")
	return lines


func _facility_status_copy(reply: Dictionary) -> String:
	if reply.get("status", "") == "idle":
		return "Idle · workers assigned" if float(reply.get("staffing", 0.0)) > 0.0 else "Idle · unstaffed"
	return str(reply.get("status", "")).replace("_", " ").capitalize()


func _workforce_change_copy(change: Dictionary) -> String:
	var classes := change.keys()
	classes.sort()
	var parts := PackedStringArray()
	for worker_class in classes:
		var amount := int(change[worker_class])
		if amount != 0:
			parts.append("%s%d %s" % ["+" if amount > 0 else "", amount, str(worker_class).capitalize()])
	return ", ".join(parts)


func _rebuild_actions(kind: String, entity: String, reply: Dictionary) -> void:
	for c in _actions.get_children():
		c.queue_free()
	match kind:
		"facility":
			if reply.get("status") == "paused":
				_action("Resume", {"do": "resume", "target": entity})
			else:
				_action("Pause", {"do": "pause", "target": entity})
			# sim_bridge v2: one click to staff a starved building before its category (rank 3 = construction).
			for blocker in reply.get("blockers", []):
				if blocker.get("code", "") == "unstaffed" and blocker.get("params", {}).get("can_raise_priority", false):
					_action("Staff first", {"do": "set_labour_priority", "target": entity, "value": STAFF_FIRST_RANK})
					break
			if reply.get("labour_priority_overridden", false):
				_action("Normal priority", {"do": "set_labour_priority", "target": entity, "value": null})
		"site":
			_action("Cancel", {"do": "cancel", "target": entity})
		"residence":
			var workforce_change := _workforce_change_copy(reply.get("evolution_workforce_change", {}))
			_action("Evolve", {"do": "evolve", "residence": entity},
				"Workforce on evolution: %s" % workforce_change if workforce_change != "" else "")
		"great_work":
			if not reply.get("begun", false):
				_action("Begin", {"do": "begin_great_work", "priority": 5})

	for consumer_id in _consumer_ids(reply):
		var button := _icon_button("inspect", "Inspect competing building: %s" % consumer_id)
		button.set_meta("action_label", "Inspect %s" % consumer_id)
		button.pressed.connect(func(): inspect_requested.emit(str(consumer_id)))
		_actions.add_child(button)


func _action(text: String, cmd: Dictionary, tooltip: String = "") -> void:
	var glyph: String = {"Pause": "pause", "Resume": "play", "Cancel": "cancel", "Evolve": "up", "Staff first": "unit", "Normal priority": "reset", "Begin": "build"}.get(text, "other")
	var b := _icon_button(glyph, text + ("\n" + tooltip if tooltip != "" else ""))
	b.set_meta("action_label", text)
	b.pressed.connect(func(): action_requested.emit(cmd))
	_actions.add_child(b)


func _inspection_summary(reply: Dictionary) -> String:
	var summary := ""
	match reply.get("kind", ""):
		"facility": summary = "%s · %d%% staffed" % [_facility_status_copy(reply), int(float(reply.get("staffing", 0)) * 100)]
		"site": summary = "%s · %d%% built" % [str(reply.get("state", "")).replace("_", " "), int(float(reply.get("work_progress", 0)) * 100)]
		"great_work": summary = "Stage %d · %s" % [int(reply.get("stage", 0)), "begun" if reply.get("begun", false) else "not begun"]
		"residence": summary = "%s / %s residents · %s" % [reply.get("population", 0), reply.get("capacity", 0), reply.get("condition", "normal")]
	var reasons: Array = reply.get("reasons", [])
	if not reasons.is_empty(): summary += "\n" + str(reasons[0]).replace("_", " ")
	return summary


func show_unit_inspection(id: String, moving: bool, state: Dictionary = {}) -> void:
	_inspector_panel.show()
	_inspector_title.text = "Carrier %s" % id.get_slice("_", 1)
	_summary.text = "Following colony route" if moving else "Paused with colony"
	if not state.is_empty():
		var cargo: Dictionary = state.get("cargo", {})
		var parts := PackedStringArray()
		for good in cargo: parts.append("%s %s" % [cargo[good], str(good).replace("_", " ")])
		_summary.text = ("Carrying " + ", ".join(parts) if not parts.is_empty() else "Empty") + " · " + str(state.get("state", "idle")).replace("_", " ")
		if not moving: _summary.text += " · Paused"
		_inspector_body.text = "From %s to %s. Cargo is held by this carrier until delivery; transport advances with simulation time." % [state.get("source", "anchor"), state.get("target", "anchor")]
	else:
		_inspector_body.text = "Visual carrier on the colony route. Cargo and individual worker orders are not simulated yet. Production is managed through buildings."
	if _last_inspection.get("entity") != id:
		for c in _actions.get_children(): c.queue_free()
		var follow := _icon_button("follow", "Follow this carrier with the camera")
		follow.pressed.connect(func(): follow_requested.emit(id))
		_actions.add_child(follow)
	_last_inspection = {"entity": id, "kind": "carrier"}


func show_context(position: Vector2, reply: Dictionary = {}) -> void:
	_context.clear()
	_context_commands.clear()
	if reply.is_empty():
		_context_entry("Build…", {"ui": "build"}, "build")
		_context_entry("Pause / resume", {"ui": "pause"}, "pause")
		_context_entry("Reset camera", {"ui": "reset"}, "reset")
	elif reply.get("kind") == "road":
		_context_entry("Inspect road", {"ui": "inspect", "target": reply["entity"]}, "road")
		_context_entry("Remove road", {"do": "remove_road", "target": reply["entity"]}, "cancel")
	elif reply.get("kind") == "carrier":
		_context_entry("Inspect carrier", {"ui": "inspect", "target": reply["entity"]}, "unit")
		_context_entry("Follow carrier", {"ui": "follow", "target": reply["entity"]}, "follow")
	else:
		var id: String = reply.get("entity", "")
		_context_entry("Inspect " + str(reply.get("building", reply.get("builds", reply.get("tier", id)))).replace("_", " "), {"ui": "inspect", "target": id}, "inspect")
		match reply.get("kind"):
			"facility":
				var paused: bool = reply.get("status") == "paused"
				_context_entry("Resume" if paused else "Pause", {"do": "resume" if paused else "pause", "target": id}, "play" if paused else "pause")
				if reply.get("labour_priority_overridden", false):
					_context_entry("Normal priority", {"do": "set_labour_priority", "target": id, "value": null}, "reset")
				else:
					for blocker in reply.get("blockers", []):
						if blocker.get("code") == "unstaffed" and blocker.get("params", {}).get("can_raise_priority", false):
							_context_entry("Staff first", {"do": "set_labour_priority", "target": id, "value": STAFF_FIRST_RANK}, "unit")
							break
			"site": _context_entry("Cancel construction", {"do": "cancel", "target": id}, "cancel")
			"residence":
				if reply.get("next_tier") != null:
					var change := _workforce_change_copy(reply.get("evolution_workforce_change", {}))
					_context_entry("Evolve to " + str(reply["next_tier"]).capitalize() + (" · " + change if change != "" else ""), {"do": "evolve", "residence": id}, "up")
	_context.position = Vector2i(position)
	_context.popup()


func _context_entry(label: String, command: Dictionary, icon: String) -> void:
	_context.add_icon_item(Glyph.texture(icon), label, _context_commands.size())
	_context_commands.append(command)


func _context_action(index: int) -> void:
	var command := _context_commands[index]
	match command.get("ui", ""):
		"build": open_build_category()
		"pause": speed_selected.emit(1 if _speed_buttons[0].button_pressed else 0)
		"reset": zoom_requested.emit(0.0)
		"inspect": inspect_requested.emit(command["target"])
		"follow": follow_requested.emit(command["target"])
		_: action_requested.emit(command)


func show_road_inspection(id: String, road: Dictionary) -> void:
	_inspector_panel.show()
	_inspector_title.text = "Dirt road"
	_summary.text = "%.1f m · Right-click for options" % float(road.get("length", 0))
	_inspector_body.text = "Buildings need road access to the founding supply anchor. Removing a road can disconnect buildings and halt deliveries."
	if _last_inspection.get("entity") != id:
		for child in _actions.get_children(): child.queue_free()
	_last_inspection = {"entity": id, "kind": "road"}
