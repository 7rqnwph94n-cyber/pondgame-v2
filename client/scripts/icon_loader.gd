class_name IconLoader
extends RefCounted
## Runtime SVG loader for Codex's source icon set outside the Godot project directory.

static var _cache: Dictionary = {}


static func load_svg(path: String, scale: float = 1.0) -> Texture2D:
	var key := "%s@%s" % [path, scale]
	if _cache.has(key):
		return _cache[key]
	var bytes := FileAccess.get_file_as_bytes(path)
	if bytes.is_empty():
		return null
	var image := Image.new()
	if image.load_svg_from_buffer(bytes, scale) != OK:
		return null
	var texture := ImageTexture.create_from_image(image)
	_cache[key] = texture
	return texture
