extends SceneTree
## Fixture-driven render check, not a manual or novice playthrough.
## Run: godot --path client --script res://tools/capture_current_opening.gd
## Starts a separate bridge on 48177; never touches the ordinary game session.

class IsolatedMain extends "res://scripts/main.gd":
	func _apply_settings(b: Node) -> void:
		super._apply_settings(b)
		b.port = 48177

var game: Node3D
var elapsed := 0.0
var stage := 0
var ready_at := 0
var plan: Dictionary
var queue: Array
var command_pending := false
var output_dir := ProjectSettings.globalize_path("res://").path_join("../docs/art/renders/current_habitat").simplify_path()
var captures: Array[String]

func _initialize() -> void:
	DirAccess.make_dir_recursive_absolute(output_dir)
	captures = [output_dir.path_join("empty.png"), output_dir.path_join("neighbourhood.png")]
	game = IsolatedMain.new()
	root.add_child.call_deferred(game)
	plan = JSON.parse_string(FileAccess.get_file_as_string(ProjectSettings.globalize_path("res://").path_join("../economy/data/plans/current_mineral_opening_v1.json")))
	queue = plan.get("commands", []).duplicate(true)

func _process(delta: float) -> bool:
	elapsed += delta
	if elapsed > 300:
		push_error("render QA timed out")
		if game.bridge != null: game.bridge.stop()
		quit(1)
		return true
	if game.bridge == null or not game.bridge.is_ready or game.view.is_empty(): return false
	if stage == 0:
		print("QA READY: ", elapsed, "s; mode=", game.view.get("spatial", {}).get("mode"), " homes=", game.view.get("residences", {}).size(), " sites=", game.view.get("sites", {}).size(), " speed=", game.speed_index)
		root.get_texture().get_image().save_png(captures[0])
		stage = 1
		ready_at = Time.get_ticks_msec()
	if stage == 1 and not command_pending:
		if queue.is_empty():
			stage = 2
			game.camera_rig.set_review_view(Vector2(-44,-9), 53)
			return false
		var entry: Dictionary = queue.pop_front()
		var advance: int = maxi(0, int(entry.at) - int(game.view.second))
		command_pending = true
		game.bridge.request("advance", {"seconds":advance}, func(reply):
			game._on_view(reply)
			game.bridge.request("command", {"cmd":entry.cmd}, func(result):
				if not result.get("ok",false):
					push_error(str(result)); quit(1)
				game.bridge.request("view", {}, func(view_reply):
					game._on_view(view_reply)
					command_pending = false)))
	if stage == 2 and not command_pending:
		stage = 3
		command_pending = true
		game.bridge.request("advance", {"seconds":600}, func(reply):
			game._on_view(reply)
			command_pending = false
			ready_at = Time.get_ticks_msec())
	if stage == 3 and not command_pending and Time.get_ticks_msec() - ready_at > 1000:
		root.get_texture().get_image().save_png(captures[1])
		print("QA PAID NEIGHBOURHOOD: time=", game.view.time, " facilities=", game.view.facilities.size(), " population=", game.view.population, " mode=",game.view.spatial.mode)
		game.bridge.stop()
		quit(0)
	return false
