class_name CameraRig
extends Node3D
## High-angle city-builder camera: middle-drag / WASD pan, Alt-middle-drag or Q/E rotate, wheel / trackpad / buttons zoom.

signal navigation_started

var camera: Camera3D
var _yaw := deg_to_rad(35.0)
var _pitch := deg_to_rad(-49.0)
var _distance := 105.0
var _focus := Vector3(0, 0, 0)
var _capture_locked := false


func _ready() -> void:
	camera = Camera3D.new()
	camera.far = 2000.0
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 88.0
	add_child(camera)
	camera.current = true
	_apply()


func set_review_view(focus: Vector2, zoom: float) -> void:
	_focus = Vector3(focus.x, 0.0, focus.y)
	camera.size = clampf(zoom, 42.0, 118.0)
	_apply()


func set_capture_locked(locked: bool) -> void:
	_capture_locked = locked


func _unhandled_input(event: InputEvent) -> void:
	if _capture_locked:
		return
	if event is InputEventMouseMotion:
		if event.button_mask & MOUSE_BUTTON_MASK_MIDDLE and event.alt_pressed:
			_yaw -= event.relative.x * 0.005
			_pitch = clamp(_pitch - event.relative.y * 0.005, deg_to_rad(-85.0), deg_to_rad(-15.0))
			_apply()
		elif event.button_mask & MOUSE_BUTTON_MASK_MIDDLE:
			_pan(Vector2(-event.relative.x, -event.relative.y) * _distance * 0.002)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			zoom_by(pow(0.88, maxf(event.factor, 0.1)))
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			zoom_by(pow(1.0 / 0.88, maxf(event.factor, 0.1)))

	elif event is InputEventPanGesture:
		zoom_by(exp(event.delta.y * 0.035))
	elif event is InputEventMagnifyGesture:
		zoom_by(1.0 / maxf(event.factor, 0.01))
	elif event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_EQUAL, KEY_PLUS, KEY_KP_ADD: zoom_by(0.85)
			KEY_MINUS, KEY_KP_SUBTRACT: zoom_by(1.18)
			KEY_HOME: reset_view()


func zoom_by(factor: float) -> void:
	if is_zero_approx(factor):
		reset_view()
		return
	camera.size = clampf(camera.size * factor, 24.0, 150.0)
	_apply()


func reset_view() -> void:
	navigation_started.emit()
	_focus = Vector3.ZERO
	_yaw = deg_to_rad(35.0)
	_pitch = deg_to_rad(-49.0)
	camera.size = 88.0
	_apply()


func focus_on(position: Vector3) -> void:
	_focus = position
	_apply()


func _process(delta: float) -> void:
	if _capture_locked:
		return
	if Input.is_key_pressed(KEY_Q): _yaw += delta
	if Input.is_key_pressed(KEY_E): _yaw -= delta
	_apply()
	var move := Vector2.ZERO
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP): move.y -= 1
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN): move.y += 1
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT): move.x -= 1
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT): move.x += 1
	if move != Vector2.ZERO:
		_pan(move * camera.size * delta * 0.45)


func _pan(amount: Vector2) -> void:
	navigation_started.emit()
	var forward := Vector3(sin(_yaw), 0, cos(_yaw))
	var right := Vector3(cos(_yaw), 0, -sin(_yaw))
	_focus += right * amount.x + forward * amount.y
	_apply()


func _apply() -> void:
	if camera == null:
		return
	var offset := Vector3(sin(_yaw) * cos(_pitch), -sin(_pitch), cos(_yaw) * cos(_pitch)) * _distance
	camera.position = _focus + offset
	camera.look_at(_focus, Vector3.UP)
