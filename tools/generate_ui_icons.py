#!/usr/bin/env python3
"""Generate the first native SVG resource, service and status icons."""

from __future__ import annotations

import json
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets"/"ui"/"icons"

COLORS={
    "teal":"#123f42","cyan":"#78d6dc","pale":"#e8dfc4","amber":"#f0a23a",
    "coral":"#dc5a4b","green":"#80bb62","dark":"#10282b","muted":"#718487",
}


def svg(body, accent="cyan"):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img">
  <circle cx="32" cy="32" r="29" fill="{COLORS['dark']}" stroke="{COLORS['pale']}" stroke-width="3"/>
  <g fill="none" stroke="{COLORS[accent]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{body}</g>
</svg>\n'''


ICONS={
"raw_silicate":svg('<path d="M18 45 24 18 34 9 46 22 43 47Z"/><path d="m24 18 12 12 10-8M36 30l7 17M18 45l18-15"/>'),
"prepared_silica":svg('<circle cx="22" cy="37" r="8"/><circle cx="34" cy="22" r="8"/><circle cx="43" cy="39" r="8"/>'),
"staple_food":svg('<path d="M16 35c11-14 25-13 33-4-8 13-23 18-33 4Z"/><path d="M20 36c11-2 18-5 26-11"/>',"green"),
"carbonate":svg('<path d="M14 45c2-13 12-25 24-29l12 10-2 19Z"/><circle cx="27" cy="34" r="3"/><circle cx="39" cy="31" r="2"/>',"pale"),
"biomass":svg('<path d="M17 47c1-19 14-29 30-31-1 18-14 30-30 31Z"/><path d="M20 44c8-10 16-17 25-24M29 36l-8-10M36 30l8 9"/>',"green"),
"repair_enzyme":svg('<path d="M31 11c12 13 17 21 17 31a16 16 0 0 1-32 0c0-10 6-19 15-31Z"/><path d="M24 43c3 4 8 5 13 2"/>',"amber"),
"nutrition":svg('<path d="M18 41c2-16 15-25 29-22-1 16-12 27-29 22Z"/><path d="M21 40c8-7 14-12 22-17"/>',"green"),
"clean_flow":svg('<path d="M32 10c10 13 16 22 16 31a16 16 0 0 1-32 0c0-9 6-18 16-31Z"/><path d="M23 42c4 5 11 6 17 1"/>'),
"waste":svg('<path d="M18 24 32 15l14 9-3 23H21Z"/><path d="m23 25 9 7 9-7M32 32v15"/>',"amber"),
"health":svg('<path d="M27 14h10v13h13v10H37v13H27V37H14V27h13Z"/>'),
"culture":svg('<path d="M32 49V22M32 30 20 20M32 34l13-13M32 40l-12 5M32 43l12 4"/><circle cx="20" cy="20" r="4"/><circle cx="45" cy="21" r="4"/>',"amber"),
"builder":svg('<path d="m16 43 20-25 12 10-19 24Z"/><path d="m34 19 8-8 11 9-7 9M15 48h22"/>',"amber"),
"waiting_input":svg('<path d="M18 19h28v27H18Z"/><path d="M25 12v14M20 21l5 5 5-5"/>',"amber"),
"output_blocked":svg('<path d="M14 32h28M34 24l8 8-8 8"/><path d="M49 18v28"/>',"coral"),
"unstaffed":svg('<circle cx="26" cy="23" r="8"/><path d="M13 48c1-11 7-17 13-17s12 6 13 17M43 20l10 10M53 20 43 30"/>',"muted"),
"strained":svg('<path d="M32 12 52 49H12Z"/><path d="M32 25v11M32 43h.1"/>',"amber"),
"dormant":svg('<circle cx="32" cy="32" r="17"/><path d="m20 44 24-24"/>',"muted"),
"food_emergency":svg('<path d="M32 10 54 50H10Z"/><path d="M24 36c5-8 12-9 17-4-3 7-10 10-17 4ZM32 41v4"/>',"coral"),
"season_bloom":svg('<circle cx="32" cy="32" r="8"/><path d="M32 10v8M32 46v8M10 32h8M46 32h8M16 16l6 6M42 42l6 6M48 16l-6 6M22 42l-6 6"/>',"amber"),
"season_dry":svg('<circle cx="32" cy="25" r="10"/><path d="M12 46c8-7 14 7 22 0s12 5 18-1M32 9v5M14 25h5M45 25h5"/>',"amber"),
}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    for name,data in ICONS.items():
        (OUT/f"{name}.svg").write_text(data)
    (OUT/"manifest.json").write_text(json.dumps({"generated_by":"tools/generate_ui_icons.py","view_box":"0 0 64 64","icons":sorted(ICONS)},indent=2)+"\n")
    print(f"Generated {len(ICONS)} SVG icons in {OUT}")


if __name__=="__main__":
    main()
