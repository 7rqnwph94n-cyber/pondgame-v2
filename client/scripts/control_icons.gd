extends RefCounted
## Small vector UI glyphs, rasterised at runtime so buttons remain crisp.
static var cache := {}
const PATHS := {
 "anoxic_organics": '<circle cx="16" cy="28" r="8"/><circle cx="32" cy="31" r="6"/><circle cx="27" cy="13" r="5"/>',
 "balanced_gel": '<path d="M12 35c-7-10 2-25 13-24 12-1 20 12 12 23-8 8-17 10-25 1Z"/><path d="M17 29c4 4 10 4 15-1"/>',
 "cured_resin": '<path d="m12 13 20-4 9 22-13 10-19-8ZM12 13l16 28M12 13l29 18"/>',
 "fired_ceramic": '<path d="M12 14h24l-3 25H15ZM10 9h28M16 21h16M19 28h10"/>',
 "growth_nutrient": '<path d="M24 41V23c-13 1-15-9-15-14 12-1 18 5 15 14 0-13 9-17 17-16 0 13-7 18-17 16M14 41h20"/>',
 "habitat_composite": '<path d="m14 8 20 0 10 16-10 16H14L4 24ZM14 8l10 16L14 40M34 8 24 24l10 16M4 24h40"/>',
 "organic_waste": '<path d="M12 15h24l-3 25H15ZM9 15h30M19 8h10M20 21v13M28 21v13"/>',
 "phosphate_sediment": '<path d="m7 18 17-10 17 10-17 10ZM7 27l17 10 17-10M7 35l17 10 17-10"/>',
 "pigment_ornament": '<circle cx="24" cy="24" r="16"/><path d="m24 10 4 10 10 4-10 4-4 10-4-10-10-4 10-4Z"/>',
 "raw_fibre": '<path d="M12 39C35 28 4 20 26 8M23 40C46 28 15 21 37 9M8 27l32-6"/>',
 "raw_pigment": '<path d="M24 8 40 22 33 39H14L7 23ZM7 23h33M14 39l10-31 9 31"/>',
 "raw_resin": '<path d="M24 8C19 22 10 23 12 33c3 12 25 10 25-2 0-9-11-16-13-23ZM18 31c0 5 4 7 7 7"/>',
 "recovered_fertiliser": '<path d="M15 15h18l5 24H10ZM19 15l-3-6h16l-3 6M24 33V21M24 28l-6-5M24 27l6-6"/>',
 "stored_value": '<circle cx="24" cy="24" r="17"/><circle cx="24" cy="24" r="12"/><path d="M24 16v16M19 21l5-5 5 5M19 27l5 5 5-5"/>',
 "suspended_nutrient": '<path d="M18 8h12M20 8v12L9 37q-2 4 4 4h22q6 0 4-4L28 20V8M16 29h16"/><circle cx="22" cy="35" r="1"/>',
 "woven_fibre": '<path d="M10 13h28v25H10ZM17 10v31M25 10v31M33 10v31M7 21h34M7 30h34"/>',
	"home": '<path d="M8 25L24 10l16 15M12 23v17h24V23M21 40V29h7v11"/>',
	"food": '<path d="M12 36C9 14 28 9 39 10c0 20-10 29-27 26Zm0 0 19-18"/>',
	"extraction": '<path d="m9 35 13-22 9 3 8 19ZM17 12l18 18M28 10l10 7M12 39h28"/>',
	"processing": '<path d="M10 38h28V23H27v7h-8V18h-9ZM12 18V9h5v9M29 13h9M34 8v10"/>',
	"service": '<path d="M24 8 39 14v11c0 9-8 14-15 17C17 39 9 34 9 25V14ZM24 18v14M17 25h14"/>',
	"logistics": '<path d="M9 14h30v24H9ZM9 14l15-7 15 7M24 14v24M9 26h30"/>',
	"institution": '<path d="m7 17 17-9 17 9ZM9 39h30M13 21v14M24 21v14M35 21v14"/>',
	"luxury": '<path d="m24 7 15 15-15 19L9 22ZM9 22h30M17 14l7 27 7-27"/>',
	"build": '<path d="M12 39V24l12-12 12 12v15M6 25l18-18 18 18M19 39V28h10v11"/>',
	"pause": '<path d="M18 12v25M30 12v25"/>',
	"play": '<path d="m17 10 21 14-21 14Z"/>',
	"cancel": '<path d="m13 13 22 22M35 13 13 35"/>',
	"up": '<path d="m12 27 12-14 12 14M24 14v26"/>',
	"reset": '<path d="M11 21a14 14 0 1 1 1 14M11 11v10h10"/>',
	"inspect": '<circle cx="22" cy="21" r="12"/><path d="m31 30 10 10M22 15v12M16 21h12"/>',
	"info": '<circle cx="24" cy="24" r="17"/><path d="M24 22v12M24 14v2"/>',
	"log": '<path d="M12 9h24v31H12ZM18 17h12M18 24h12M18 31h8"/>',
	"plus": '<path d="M24 11v26M11 24h26"/>',
	"minus": '<path d="M11 24h26"/>',
	"follow": '<circle cx="24" cy="24" r="10"/><path d="M24 5v8M24 35v8M5 24h8M35 24h8"/>',
	"unit": '<circle cx="24" cy="13" r="5"/><path d="M24 18v11M12 23l12-5 12 5M24 29l-9 12M24 29l9 12"/>',
	"water": '<path d="M24 7C17 19 12 23 12 30a12 12 0 0 0 24 0c0-7-5-11-12-23Z"/>',
	"other": '<circle cx="24" cy="24" r="15"/><path d="M16 24h16M24 16v16"/>'
}
static func texture(id: String) -> Texture2D:
	if cache.has(id): return cache[id]
	var svg := '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><g fill="none" stroke="#e8dfc4" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round">%s</g></svg>' % PATHS.get(id, PATHS["other"])
	var image := Image.new()
	image.load_svg_from_string(svg)
	var result := ImageTexture.create_from_image(image)
	cache[id] = result
	return result
