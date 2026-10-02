#!/usr/bin/env python3
"""Generate deterministic Silica Street OBJ blockouts with no third-party deps."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "blockout" / "silica_street"

MATERIALS = {
    "carbonate": (0.78, 0.72, 0.58),
    "shell_teal": (0.035, 0.25, 0.27),
    "membrane": (0.42, 0.82, 0.82),
    "silicate_raw": (0.28, 0.72, 0.88),
    "silicate_prepared": (0.78, 0.88, 0.84),
    "active_amber": (0.95, 0.45, 0.08),
    "host_rock": (0.08, 0.10, 0.12),
    "organic_dark": (0.13, 0.09, 0.055),
}


class Mesh:
    def __init__(self, name: str):
        self.name = name
        self.vertices: list[tuple[float, float, float]] = []
        self.faces: list[tuple[list[int], str, str]] = []

    def add_vertex(self, value):
        self.vertices.append(tuple(round(float(v), 5) for v in value))
        return len(self.vertices)

    def face(self, indices, material, group):
        self.faces.append((list(indices), material, group))

    def box(self, center, size, material, group):
        cx, cy, cz = center
        sx, sy, sz = (v / 2 for v in size)
        vs = [
            self.add_vertex((cx + x * sx, cy + y * sy, cz + z * sz))
            for x, y, z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]
        ]
        for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]:
            self.face([vs[i] for i in f], material, group)

    def ellipsoid(self, center, radii, material, group, rings=5, segments=10):
        cx, cy, cz = center
        rx, ry, rz = radii
        rows = []
        for ring in range(rings + 1):
            phi = -math.pi / 2 + math.pi * ring / rings
            row = []
            for seg in range(segments):
                theta = 2 * math.pi * seg / segments
                row.append(self.add_vertex((
                    cx + rx * math.cos(phi) * math.cos(theta),
                    cy + ry * (math.sin(phi) + 1),
                    cz + rz * math.cos(phi) * math.sin(theta),
                )))
            rows.append(row)
        for ring in range(rings):
            for seg in range(segments):
                nxt = (seg + 1) % segments
                self.face([rows[ring][seg], rows[ring][nxt], rows[ring+1][nxt], rows[ring+1][seg]], material, group)

    def cylinder_between(self, a, b, radius, material, group, sides=6):
        ax, ay, az = a
        bx, by, bz = b
        dx, dy, dz = bx-ax, by-ay, bz-az
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        if length == 0:
            return
        ux, uy, uz = dx/length, dy/length, dz/length
        helper = (0, 1, 0) if abs(uy) < 0.9 else (1, 0, 0)
        px = uy*helper[2] - uz*helper[1]
        py = uz*helper[0] - ux*helper[2]
        pz = ux*helper[1] - uy*helper[0]
        plen = math.sqrt(px*px + py*py + pz*pz)
        px, py, pz = px/plen, py/plen, pz/plen
        qx, qy, qz = uy*pz-uz*py, uz*px-ux*pz, ux*py-uy*px
        ra, rb = [], []
        for i in range(sides):
            t = 2*math.pi*i/sides
            ox = radius*(math.cos(t)*px + math.sin(t)*qx)
            oy = radius*(math.cos(t)*py + math.sin(t)*qy)
            oz = radius*(math.cos(t)*pz + math.sin(t)*qz)
            ra.append(self.add_vertex((ax+ox, ay+oy, az+oz)))
            rb.append(self.add_vertex((bx+ox, by+oy, bz+oz)))
        self.face(ra[::-1], material, group)
        self.face(rb, material, group)
        for i in range(sides):
            n = (i+1) % sides
            self.face([ra[i], ra[n], rb[n], rb[i]], material, group)

    def crystal(self, center, radius, height, material, group, sides=5, tilt=(0, 0)):
        cx, cy, cz = center
        tx, tz = tilt
        lower, upper = [], []
        for i in range(sides):
            t = 2*math.pi*i/sides
            lower.append(self.add_vertex((cx+radius*math.cos(t), cy, cz+radius*math.sin(t))))
            upper.append(self.add_vertex((cx+tx+radius*.68*math.cos(t), cy+height*.72, cz+tz+radius*.68*math.sin(t))))
        tip = self.add_vertex((cx+tx*1.25, cy+height, cz+tz*1.25))
        self.face(lower[::-1], material, group)
        for i in range(sides):
            n = (i+1)%sides
            self.face([lower[i], lower[n], upper[n], upper[i]], material, group)
            self.face([upper[i], upper[n], tip], material, group)

    def write(self, anchors):
        OUT.mkdir(parents=True, exist_ok=True)
        path = OUT / f"{self.name}.obj"
        lines = [f"# Generated Silica Street blockout: {self.name}", "mtllib silica_street_blockout.mtl", f"o {self.name}"]
        lines += [f"v {x} {y} {z}" for x, y, z in self.vertices]
        current = None
        for indices, material, group in self.faces:
            key = (material, group)
            if key != current:
                lines += [f"g {group}", f"usemtl {material}"]
                current = key
            lines.append("f " + " ".join(str(i) for i in indices))
        path.write_text("\n".join(lines) + "\n")
        (OUT / f"{self.name}.anchors.json").write_text(json.dumps({
            "asset": self.name,
            "units": "metres",
            "up_axis": "+Y",
            "ground_pivot": [0, 0, 0],
            "anchors": anchors,
        }, indent=2) + "\n")


def radial_ribs(mesh, radius_x, radius_z, peak_y, count, group):
    for i in range(count):
        t = 2*math.pi*i/count
        edge = (radius_x*math.cos(t), .12, radius_z*math.sin(t))
        shoulder = (radius_x*.62*math.cos(t), peak_y*.72, radius_z*.62*math.sin(t))
        mesh.cylinder_between(edge, shoulder, .095, "carbonate", group)
        mesh.cylinder_between(shoulder, (0, peak_y, 0), .075, "carbonate", group)


def payload_raw():
    m = Mesh("payload_raw_silicate_a")
    for i, (x, z, r, h) in enumerate([(-.22,-.08,.13,.55),(.05,.08,.16,.72),(.27,-.02,.11,.48),(-.02,-.2,.1,.42)]):
        m.crystal((x, 0, z), r, h, "silicate_raw", f"facet_{i}", tilt=(x*.18, z*.2))
    m.write({"PayloadAnchor": [0, 0, 0], "LabelAnchor": [0, .9, 0]})


def payload_prepared():
    m = Mesh("payload_prepared_silica_a")
    for i in range(7):
        t = 2*math.pi*i/7
        rad = .22 if i else 0
        m.ellipsoid((rad*math.cos(t), 0, rad*math.sin(t)), (.13,.11,.13), "silicate_prepared", f"pellet_{i}", rings=3, segments=6)
    m.write({"PayloadAnchor": [0, 0, 0], "LabelAnchor": [0, .5, 0]})


def outcrop():
    m = Mesh("patch_silicate_a")
    m.ellipsoid((0,0,0), (3.2,.85,2.55), "host_rock", "host_rock", rings=4, segments=12)
    crystals = [(-1.5,-.4,.5,2.7),(-.65,.2,.65,3.25),(.2,-.25,.48,2.35),(.85,.35,.6,2.9),(1.55,-.2,.42,2.0),(.2,.8,.35,1.7)]
    for i,(x,z,r,h) in enumerate(crystals):
        m.crystal((x,.55,z), r,h,"silicate_raw",f"facet_{i}",tilt=(x*.08,z*.05))
    m.write({"WorkerAnchor_1": [-2.5,0,-2.2], "WorkerAnchor_2": [0,0,-2.8], "PayloadAnchor": [2.3,.2,-1.8], "LabelAnchor": [0,4.2,0], "FXAnchor": [0,2,0]})


def carrier():
    m = Mesh("unit_general_carrier_a")
    m.ellipsoid((0,.18,0), (.62,.28,.34), "shell_teal", "mantle", rings=4, segments=10)
    m.ellipsoid((-.22,.48,-.22), (.32,.18,.25), "membrane", "cargo_left", rings=4, segments=8)
    m.ellipsoid((-.22,.48,.22), (.32,.18,.25), "membrane", "cargo_right", rings=4, segments=8)
    for i,(start,end) in enumerate([
        ((-.2,.25,-.22),(-.52,.10,-.46)),((.22,.25,-.22),(.52,.10,-.42)),
        ((-.2,.25,.22),(-.52,.10,.46)),((.22,.25,.22),(.52,.10,.42)),
    ]):
        m.cylinder_between(start,end,.075,"carbonate",f"limb_{i}",sides=6)
        m.ellipsoid((end[0],0,end[2]),(.14,.05,.12),"shell_teal",f"foot_{i}",rings=3,segments=6)
    m.ellipsoid((.46,.23,0),(.18,.12,.16),"active_amber","activity_organ",rings=3,segments=8)
    m.write({"PayloadAnchor": [-.22,.55,0], "DeliveryContact": [-.67,.18,0], "CameraAnchor": [0,.65,0], "LabelAnchor": [0,.9,0], "GroundPivot": [0,0,0]})


def store():
    m = Mesh("store_general_a")
    m.ellipsoid((0,0,0),(2.9,.45,2.35),"shell_teal","base",rings=4,segments=12)
    radial_ribs(m,2.9,2.35,2.7,10,"lattice")
    for i,(x,z,mat) in enumerate([(-1.15,-.65,"silicate_raw"),(1.1,-.65,"silicate_prepared"),(0,1.0,"organic_dark")]):
        m.ellipsoid((x,.32,z),(.78,.28,.65),mat,f"stock_chamber_{i}",rings=3,segments=8)
    m.write({"InputAnchor_raw_silicate": [-1.6,.2,-2.25], "InputAnchor_prepared_silica": [1.5,.2,-2.25], "WorkerAnchor_1": [0,0,-2.8], "LabelAnchor": [0,3.25,0], "CameraAnchor": [0,1.4,0]})


def washery():
    m = Mesh("proc_mineral_washery_a")
    m.ellipsoid((0,0,0),(3.8,.42,2.8),"shell_teal","base",rings=4,segments=14)
    # Left-to-right process, viewed from negative Z.
    m.ellipsoid((-2.25,.35,-.35),(1.0,.5,1.25),"organic_dark","dirty_intake",rings=4,segments=10)
    m.ellipsoid((0,.45,0),(1.15,.42,1.5),"membrane","wash_basin",rings=4,segments=10)
    m.ellipsoid((2.3,.35,-.35),(.95,.32,1.2),"silicate_prepared","output_shelf",rings=3,segments=9)
    radial_ribs(m,3.75,2.75,3.45,12,"lattice")
    m.cylinder_between((-1.45,.75,-.2),(1.35,.75,-.2),.12,"membrane","flow_channel",sides=8)
    for x in (-2.8,2.8):
        m.ellipsoid((x,.42,1.65),(.24,.22,.24),"active_amber","activity_organs",rings=3,segments=7)
    m.write({"InputAnchor_raw_silicate": [-3.5,.25,-1.6], "OutputAnchor_prepared_silica": [3.45,.25,-1.6], "WorkerAnchor_1": [-1.2,0,-3.0], "WorkerAnchor_2": [1.2,0,-3.0], "ServiceAnchor": [0,.2,2.9], "LabelAnchor": [0,4.0,0], "FXAnchor": [0,1.2,0], "CameraAnchor": [0,1.8,0]})


def shelter():
    m = Mesh("res_shelter_cluster_a")
    m.ellipsoid((0,0,0),(3.35,.35,2.75),"shell_teal","foundation",rings=4,segments=12)
    for i,(x,z,rx,rz) in enumerate([(-1.35,0,.95,1.35),(.2,.55,1.15,1.2),(1.55,-.2,.8,1.15)]):
        m.ellipsoid((x,.28,z),(rx,.95,rz),"shell_teal",f"chamber_{i}",rings=5,segments=10)
        m.ellipsoid((x,.38,z-rz*.78),(rx*.27,.32,.18),"active_amber",f"occupancy_{i}",rings=3,segments=7)
    radial_ribs(m,3.3,2.7,3.45,11,"lattice")
    m.cylinder_between((-2.8,.12,2.0),(2.7,.12,2.0),.11,"membrane","service_channel",sides=6)
    m.write({"WorkerAnchor_1": [-2.4,0,-2.45], "WorkerAnchor_2": [1.6,0,-2.6], "ServiceAnchor": [0,.12,2.75], "ConstructionAnchor": [-3.2,0,0], "LabelAnchor": [0,3.9,0], "CameraAnchor": [0,1.8,0]})


def clean_flow():
    m = Mesh("service_clean_flow_a")
    m.ellipsoid((0,0,0),(1.45,.3,1.45),"shell_teal","base",rings=4,segments=10)
    radial_ribs(m,1.42,1.42,2.35,8,"lattice")
    m.ellipsoid((0,.2,0),(.72,.18,.72),"membrane","flow_basin",rings=3,segments=10)
    for t in (0, math.pi/2, math.pi, 3*math.pi/2):
        a=(.55*math.cos(t),.48,.55*math.sin(t))
        b=(1.35*math.cos(t),.12,1.35*math.sin(t))
        m.cylinder_between(a,b,.11,"membrane","flow_arms",sides=6)
    m.ellipsoid((0,.65,0),(.22,.35,.22),"active_amber","activity_organ",rings=3,segments=7)
    m.write({"WorkerAnchor_1": [0,0,-1.7], "ServiceAnchor": [0,.1,1.55], "InputAnchor_clean_flow": [-1.55,.1,0], "OutputAnchor_clean_flow": [1.55,.1,0], "LabelAnchor": [0,2.8,0], "CameraAnchor": [0,1.2,0]})


def waste_collector():
    m = Mesh("waste_collector")
    m.ellipsoid((0,0,0),(1.9,.32,1.9),"shell_teal","base",rings=4,segments=10)
    radial_ribs(m,1.88,1.88,2.25,9,"lattice")
    for i,(x,z) in enumerate([(-.75,-.55),(.75,-.55),(0,.7)]):
        m.ellipsoid((x,.28,z),(.58,.38,.58),"organic_dark",f"waste_chamber_{i}",rings=3,segments=8)
    m.ellipsoid((0,.45,0),(.22,.25,.22),"active_amber","activity_organ",rings=3,segments=7)
    m.write({"WorkerAnchor_1": [0,0,-2.2], "ServiceAnchor": [0,.1,2.0], "InputAnchor_waste": [0,.25,-1.75], "LabelAnchor": [0,2.7,0], "CameraAnchor": [0,1.2,0]})


def photosynthetic_field():
    m = Mesh("farm_photosynthetic_a")
    # Three broad cultivation beds with low carbonate edges and leaf membranes.
    for row,z in enumerate((-1.75,0,1.75)):
        m.box((0,.12,z),(8.6,.24,1.25),"organic_dark",f"bed_{row}")
        for side in (-1,1):
            m.cylinder_between((-4.3,.25,z+side*.62),(4.3,.25,z+side*.62),.07,"carbonate",f"bed_edge_{row}",sides=6)
        for col,x in enumerate((-3.5,-2.3,-1.1,.1,1.3,2.5,3.7)):
            scale=.34 + .04*((row+col)%3)
            m.ellipsoid((x,.22,z),(scale,.12,scale*.72),"membrane",f"leaf_{row}_{col}",rings=3,segments=7)
    m.write({"WorkerAnchor_1": [-3.5,0,-3.0], "WorkerAnchor_2": [0,0,-3.0], "WorkerAnchor_3": [3.5,0,-3.0], "OutputAnchor_photosynthetic_food": [4.45,.2,0], "ServiceAnchor": [-4.45,.1,0], "LabelAnchor": [0,1.4,0], "CameraAnchor": [0,.8,0]})


def write_materials():
    OUT.mkdir(parents=True, exist_ok=True)
    lines = ["# Silica Street blockout materials"]
    for name,(r,g,b) in MATERIALS.items():
        lines += [f"newmtl {name}", f"Kd {r} {g} {b}", "Ka 0.02 0.02 0.02", "Ks 0.08 0.08 0.08", "Ns 24", ""]
    (OUT / "silica_street_blockout.mtl").write_text("\n".join(lines))


def main():
    write_materials()
    for fn in (payload_raw, payload_prepared, outcrop, carrier, store, washery, shelter, clean_flow, waste_collector, photosynthetic_field):
        fn()
    manifest = {
        "generated_by": "tools/generate_blockout_assets.py",
        "units": "metres",
        "up_axis": "+Y",
        "format": "Wavefront OBJ blockout source",
        "assets": ["payload_raw_silicate_a", "payload_prepared_silica_a", "patch_silicate_a", "unit_general_carrier_a", "store_general_a", "proc_mineral_washery_a", "res_shelter_cluster_a", "service_clean_flow_a", "waste_collector", "farm_photosynthetic_a"],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated {len(manifest['assets'])} assets in {OUT}")


if __name__ == "__main__":
    main()
