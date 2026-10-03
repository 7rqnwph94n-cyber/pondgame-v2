class_name CameraRig
extends Node3D
## High-angle city-builder camera: right-drag rotates, middle-drag or WASD/arrows pan, wheel zooms.

var camera: Camera3D
var _yaw := deg_to_rad(35.0)
var _pitch := deg_to_rad(-55.0)
var _distance := 105.0
var _focus := Vector3(0, 0, 0)


func _ready() -> void:
	camera = Camera3D.new()
	camera.far = 2000.0
	camera.fov = 50.0
	add_child(camera)
	camera.current = true
	_apply()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventMouseMotion:
		if event.button_mask & MOUSE_BUTTON_MASK_RIGHT:
			_yaw -= event.relative.x * 0.005
			_pitch = clamp(_pitch - event.relative.y * 0.005, deg_to_rad(-85.0), deg_to_rad(-15.0))
			_apply()
		elif event.button_mask & MOUSE_BUTTON_MASK_MIDDLE:
			_pan(Vector2(-event.relative.x, -event.relative.y) * _distance * 0.002)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_distance = max(15.0, _distance * 0.9)
			_apply()
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_distance = min(400.0, _distance * 1.1)
			_apply()


func _process(delta: float) -> void:
	var move := Vector2.ZERO
	if Input.is_key_pressed(KEY_W) or Input.is_key_pressed(KEY_UP): move.y -= 1
	if Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_DOWN): move.y += 1
	if Input.is_key_pressed(KEY_A) or Input.is_key_pressed(KEY_LEFT): move.x -= 1
	if Input.is_key_pressed(KEY_D) or Input.is_key_pressed(KEY_RIGHT): move.x += 1
	if move != Vector2.ZERO:
		_pan(move * _distance * delta)


func _pan(amount: Vector2) -> void:
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
