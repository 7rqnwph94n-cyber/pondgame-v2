#!/usr/bin/env python3
"""Generate deterministic environment and route blockouts for Silica Street."""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "blockout" / "environment"

MATERIALS = {
    "silt": (0.47, 0.40, 0.30),
    "sand": (0.62, 0.54, 0.39),
    "rock": (0.12, 0.15, 0.16),
    "root": (0.22, 0.18, 0.12),
    "carbonate": (0.78, 0.72, 0.58),
    "route_membrane": (0.12, 0.42, 0.42),
}


class Mesh:
    def __init__(self, name):
        self.name = name
        self.vertices = []
        self.faces = []

    def vertex(self, xyz):
        self.vertices.append(tuple(round(float(v), 5) for v in xyz))
        return len(self.vertices)

    def face(self, indices, material, group):
        self.faces.append((indices, material, group))

    def box(self, center, size, material, group):
        cx, cy, cz = center
        sx, sy, sz = (v/2 for v in size)
        vs = [self.vertex((cx+x*sx, cy+y*sy, cz+z*sz)) for x,y,z in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
        for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]:
            self.face([vs[i] for i in f], material, group)

    def ellipsoid(self, center, radii, material, group, rings=4, segments=9):
        cx, cy, cz = center
        rx, ry, rz = radii
        rows=[]
        for ring in range(rings+1):
            phi=-math.pi/2 + math.pi*ring/rings
            row=[]
            for seg in range(segments):
                theta=2*math.pi*seg/segments
                row.append(self.vertex((cx+rx*math.cos(phi)*math.cos(theta), cy+ry*(math.sin(phi)+1), cz+rz*math.cos(phi)*math.sin(theta))))
            rows.append(row)
        for ring in range(rings):
            for seg in range(segments):
                nxt=(seg+1)%segments
                self.face([rows[ring][seg],rows[ring][nxt],rows[ring+1][nxt],rows[ring+1][seg]],material,group)

    def cylinder(self, a, b, radius, material, group, sides=7):
        ax,ay,az=a; bx,by,bz=b
        dx,dy,dz=bx-ax,by-ay,bz-az
        length=math.sqrt(dx*dx+dy*dy+dz*dz)
        ux,uy,uz=dx/length,dy/length,dz/length
        helper=(0,1,0) if abs(uy)<.9 else (1,0,0)
        px,py,pz=uy*helper[2]-uz*helper[1],uz*helper[0]-ux*helper[2],ux*helper[1]-uy*helper[0]
        plen=math.sqrt(px*px+py*py+pz*pz); px,py,pz=px/plen,py/plen,pz/plen
        qx,qy,qz=uy*pz-uz*py,uz*px-ux*pz,ux*py-uy*px
        ra=[]; rb=[]
        for i in range(sides):
            t=2*math.pi*i/sides
            ox=radius*(math.cos(t)*px+math.sin(t)*qx); oy=radius*(math.cos(t)*py+math.sin(t)*qy); oz=radius*(math.cos(t)*pz+math.sin(t)*qz)
            ra.append(self.vertex((ax+ox,ay+oy,az+oz))); rb.append(self.vertex((bx+ox,by+oy,bz+oz)))
        self.face(ra[::-1],material,group); self.face(rb,material,group)
        for i in range(sides):
            n=(i+1)%sides
            self.face([ra[i],ra[n],rb[n],rb[i]],material,group)

    def terrain_grid(self, size, divisions, material, group, phase=0.0):
        rows=[]
        for z in range(divisions+1):
            row=[]
            pz=-size/2 + size*z/divisions
            for x in range(divisions+1):
                px=-size/2 + size*x/divisions
                edge=min(x,z,divisions-x,divisions-z)
                fade=min(1.0,edge/1.5)
                y=fade*(.09+.045*math.sin(px*1.1+phase)+.025*math.cos(pz*1.35-phase))
                row.append(self.vertex((px,y,pz)))
            rows.append(row)
        for z in range(divisions):
            for x in range(divisions):
                self.face([rows[z][x],rows[z][x+1],rows[z+1][x+1],rows[z+1][x]],material,group)

    def write(self, anchors=None):
        OUT.mkdir(parents=True,exist_ok=True)
        lines=[f"# Generated environment blockout: {self.name}","mtllib environment_blockout.mtl",f"o {self.name}"]
        lines += [f"v {x} {y} {z}" for x,y,z in self.vertices]
        current=None
        for indices,material,group in self.faces:
            if (material,group)!=current:
                lines += [f"g {group}",f"usemtl {material}"]
                current=(material,group)
            lines.append("f "+" ".join(str(i) for i in indices))
        (OUT/f"{self.name}.obj").write_text("\n".join(lines)+"\n")
        if anchors is not None:
            (OUT/f"{self.name}.anchors.json").write_text(json.dumps({"asset":self.name,"units":"metres","up_axis":"+Y","ground_pivot":[0,0,0],"anchors":anchors},indent=2)+"\n")


def terrain(name, material, phase):
    m=Mesh(name); m.terrain_grid(8,8,material,"surface",phase); m.write()


def ledge_straight():
    m=Mesh("ledge_straight_a")
    m.box((0,.45,0),(8, .9, 2),"rock","ledge_mass")
    for i,(x,r) in enumerate([(-3.1,.65),(-1.6,.85),(0,.72),(1.8,.9),(3.35,.58)]):
        m.ellipsoid((x,.7,-.05),(r,.45,.9),"rock",f"ledge_breakup_{i}")
    m.write({"SnapLeft":[-4,0,0],"SnapRight":[4,0,0],"TopAnchor":[0,.9,0]})


def ledge_corner():
    m=Mesh("ledge_corner_a")
    m.box((-1.5,.45,0),(5,.9,2),"rock","ledge_x")
    m.box((0,.45,1.5),(2,.9,5),"rock","ledge_z")
    m.ellipsoid((0,.65,0),(1.25,.5,1.25),"rock","corner_breakup")
    m.write({"SnapWest":[-4,0,0],"SnapNorth":[0,0,4],"TopAnchor":[0,.9,0]})


def boulder(name, radii, offset):
    m=Mesh(name)
    m.ellipsoid(offset,radii,"rock","boulder",rings=5,segments=9)
    m.write({"CameraAnchor":[offset[0],radii[1]*1.4,offset[2]]})


def root_arch():
    m=Mesh("root_arch_a")
    points=[(-3,.22,0),(-2.2,1.5,0),(-1.1,2.7,0),(0,3.15,0),(1.1,2.7,0),(2.2,1.5,0),(3,.22,0)]
    for i in range(len(points)-1):
        m.cylinder(points[i],points[i+1],.22 if i in (0,5) else .18,"root","arch",sides=8)
    for x in (-2.2,2.2):
        m.cylinder((x,.9,0),(x*.78,.12,1.35),.12,"root","brace",sides=7)
    m.write({"SnapLeft":[-3,0,0],"SnapRight":[3,0,0],"CameraAnchor":[0,2.2,0]})


def route(name, kind):
    m=Mesh(name)
    if kind=="straight":
        m.box((0,.04,0),(4,.08,.9),"route_membrane","route_surface")
        for z in (-.5,.5): m.cylinder((-2,.12,z),(2,.12,z),.065,"carbonate","route_rib")
        anchors={"SnapWest":[-2,0,0],"SnapEast":[2,0,0]}
    elif kind=="corner":
        m.box((-1,.04,0),(2,.08,.9),"route_membrane","route_x")
        m.box((0,.04,1),( .9,.08,2),"route_membrane","route_z")
        for a,b in [((-2,.12,-.5),(0,.12,-.5)),((-2,.12,.5),(-.5,.12,.5)),((-.5,.12,.5),(-.5,.12,2)),((.5,.12,0),(.5,.12,2))]: m.cylinder(a,b,.065,"carbonate","route_rib")
        anchors={"SnapWest":[-2,0,0],"SnapNorth":[0,0,2]}
    else:
        m.box((0,.04,0),(4,.08,.9),"route_membrane","route_x")
        m.box((0,.04,0),(.9,.08,4),"route_membrane","route_z")
        anchors={"SnapWest":[-2,0,0],"SnapEast":[2,0,0],"SnapNorth":[0,0,2],"SnapSouth":[0,0,-2]}
    m.write(anchors)


def write_materials():
    OUT.mkdir(parents=True,exist_ok=True)
    lines=["# Environment blockout materials"]
    for name,(r,g,b) in MATERIALS.items():
        lines += [f"newmtl {name}",f"Kd {r} {g} {b}","Ka 0.02 0.02 0.02","Ks 0.04 0.04 0.04","Ns 12",""]
    (OUT/"environment_blockout.mtl").write_text("\n".join(lines))


def main():
    write_materials()
    terrain("terrain_silt_tile_a","silt",0.0)
    terrain("terrain_silt_tile_b","silt",1.7)
    terrain("terrain_sand_tile_a","sand",.8)
    ledge_straight(); ledge_corner()
    boulder("boulder_a",(1.2,.7,.9),(0,0,0))
    boulder("boulder_b",(.75,1.1,.7),(0,0,0))
    boulder("boulder_c",(1.4,.45,1.1),(0,0,0))
    root_arch()
    route("route_flow_straight_a","straight")
    route("route_flow_corner_a","corner")
    route("route_flow_junction_a","junction")
    assets=[p.stem for p in sorted(OUT.glob("*.obj"))]
    (OUT/"manifest.json").write_text(json.dumps({"generated_by":"tools/generate_environment_blockouts.py","units":"metres","up_axis":"+Y","assets":assets},indent=2)+"\n")
    print(f"Generated {len(assets)} environment assets in {OUT}")


if __name__=="__main__":
    main()
