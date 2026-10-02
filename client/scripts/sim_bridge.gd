class_name SimBridge
extends Node
## Client side of the local simulation bridge (contract: docs/exchange/contracts/sim_bridge.json, protocol 1).
## Launches `python3 -m economy.bridge` from the repository root, connects over TCP and exchanges JSON lines.
## The Python domain is the only rules authority; this node only transports requests and replies.

signal connected(hello: Dictionary)
signal failed(reason: String)

const PROTOCOL := 1

var python := "python3"
var port := 47615
var overlays: PackedStringArray = []
var launch := true                    # false: connect to a bridge someone else started (tests, debugging)
var connect_timeout_s := 15.0

var _peer := StreamPeerTCP.new()
var _pid := -1
var _buffer := PackedByteArray()
var _next_id := 1
var _callbacks := {}                   # request id -> Callable(reply: Dictionary)
var _connecting := false
var _elapsed := 0.0
var _hello_sent := false
var is_ready := false


func repository_root() -> String:
	return ProjectSettings.globalize_path("res://").path_join("..").simplify_path()


func start() -> void:
	if launch:
		var root := repository_root()
		# Run the module with the repository on sys.path (create_process has no working-directory argument).
		var code := "import sys, runpy; sys.path.insert(0, %s); runpy.run_module('economy.bridge', run_name='__main__')" % JSON.stringify(root)
		var args := PackedStringArray(["-c", code, "--port", str(port)])
		for overlay in overlays:
			args.append_array(["--overlay", root.path_join(overlay)])
		_pid = OS.create_process(python, args)
		if _pid <= 0:
			failed.emit("could not start %s; set the Python path in client/settings.cfg" % python)
			return
	_connecting = true
	_elapsed = 0.0
	_peer.connect_to_host("127.0.0.1", port)


func stop() -> void:
	if _peer.get_status() == StreamPeerTCP.STATUS_CONNECTED:
		_send({"op": "quit"})
		_peer.poll()
	_peer.disconnect_from_host()
	if _pid > 0 and OS.is_process_running(_pid):
		OS.kill(_pid)
	_pid = -1
	is_ready = false


func request(op: String, payload: Dictionary = {}, callback: Callable = Callable()) -> int:
	var message := payload.duplicate()
	message["op"] = op
	var id := _send(message)
	if callback.is_valid():
		_callbacks[id] = callback
	return id


func pending() -> int:
	return _callbacks.size()


func _send(message: Dictionary) -> int:
	var id := _next_id
	_next_id += 1
	message["id"] = id
	_peer.put_data((JSON.stringify(message) + "\n").to_utf8_buffer())
	return id


func _process(delta: float) -> void:
	poll(delta)


## Separate from _process so headless tests can drive the bridge without a running scene tree loop.
func poll(delta: float) -> void:
	_peer.poll()
	var status := _peer.get_status()
	if _connecting:
		_elapsed += delta
		if status == StreamPeerTCP.STATUS_CONNECTED:
			_connecting = false
			if not _hello_sent:
				_hello_sent = true
				request("hello", {}, _on_hello)
		elif status == StreamPeerTCP.STATUS_ERROR or status == StreamPeerTCP.STATUS_NONE:
			if _elapsed > connect_timeout_s:
				_connecting = false
				failed.emit("no bridge on 127.0.0.1:%d after %.0f s" % [port, connect_timeout_s])
				return
			_peer = StreamPeerTCP.new()          # the server may not be listening yet: retry
			_peer.connect_to_host("127.0.0.1", port)
		return
	if status != StreamPeerTCP.STATUS_CONNECTED:
		return
	var available := _peer.get_available_bytes()
	if available > 0:
		var chunk := _peer.get_data(available)
		if chunk[0] == OK:
			_buffer.append_array(chunk[1])
	while true:
		var newline := _buffer.find(10)
		if newline < 0:
			break
		var line := _buffer.slice(0, newline).get_string_from_utf8()
		_buffer = _buffer.slice(newline + 1)
		var reply = JSON.parse_string(line)
		if typeof(reply) != TYPE_DICTIONARY:
			push_warning("bridge sent a malformed line")
			continue
		var id := int(reply.get("id", -1))
		if _callbacks.has(id):
			var callback: Callable = _callbacks[id]
			_callbacks.erase(id)
			callback.call(reply)


func _on_hello(reply: Dictionary) -> void:
	if not reply.get("ok", false) or int(reply.get("protocol", -1)) != PROTOCOL:
		failed.emit("bridge protocol mismatch: expected %d, got %s" % [PROTOCOL, str(reply.get("protocol"))])
		return
	is_ready = true
	connected.emit(reply)


func _exit_tree() -> void:
	stop()
