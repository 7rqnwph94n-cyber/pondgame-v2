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
    "rock": (0.20, 0.27, 0.27),
    "root": (0.22, 0.18, 0.12),
    "carbonate": (0.78, 0.72, 0.58),
    "route_membrane": (0.12, 0.42, 0.42),
    "flood_silt": (0.43, 0.42, 0.31),
    "water_dark": (0.06, 0.29, 0.33),
    "silica": (0.32, 0.72, 0.75),
    "methane": (0.10, 0.15, 0.19),
    "methane_film": (0.24, 0.31, 0.37),
    "sulphur": (0.62, 0.38, 0.12),
    "living_green": (0.31, 0.55, 0.33),
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

    def cone(self, center, height, bottom_radius, top_radius, material, group, sides=8):
        cx, cy, cz = center
        bottom=[]; top=[]
        for i in range(sides):
            angle=2*math.pi*i/sides
            bottom.append(self.vertex((cx+math.cos(angle)*bottom_radius,cy,cz+math.sin(angle)*bottom_radius)))
            top.append(self.vertex((cx+math.cos(angle)*top_radius,cy+height,cz+math.sin(angle)*top_radius)))
        self.face(bottom[::-1],material,group)
        self.face(top,material,group)
        for i in range(sides):
            nxt=(i+1)%sides
            self.face([bottom[i],bottom[nxt],top[nxt],top[i]],material,group)

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


def plant_fan(name, width, height, blades):
    m=Mesh(name)
    m.ellipsoid((0,0,0),(.42,.16,.42),"root","holdfast",rings=3,segments=7)
    for i in range(blades):
        t=-.85+1.7*i/max(1,blades-1)
        x=width*math.sin(t)*.5
        top=(x,height*(.82+.18*math.cos(t)),.12*math.sin(i*1.7))
        m.cylinder((0,.14,0),top,.055,"route_membrane",f"blade_{i}",sides=6)
        m.ellipsoid((top[0],top[1]-.12,top[2]),(.12,.2,.045),"route_membrane",f"blade_tip_{i}",rings=3,segments=6)
    m.write({"GroundPivot":[0,0,0],"CameraAnchor":[0,height*.6,0]})


def plant_ribbon(name, height, strands):
    m=Mesh(name)
    m.ellipsoid((0,0,0),(.38,.13,.38),"root","holdfast",rings=3,segments=7)
    for i in range(strands):
        angle=2*math.pi*i/strands
        base=(.18*math.cos(angle),.12,.18*math.sin(angle))
        mid=(.32*math.cos(angle+.35),height*.5,.32*math.sin(angle+.35))
        top=(.48*math.cos(angle+.7),height,.48*math.sin(angle+.7))
        m.cylinder(base,mid,.045,"route_membrane",f"ribbon_{i}",sides=5)
        m.cylinder(mid,top,.035,"route_membrane",f"ribbon_{i}",sides=5)
    m.write({"GroundPivot":[0,0,0],"CameraAnchor":[0,height*.55,0]})


def plant_cup():
    m=Mesh("plant_cup_a")
    m.ellipsoid((0,0,0),(.45,.15,.45),"root","holdfast",rings=3,segments=8)
    for i in range(7):
        t=2*math.pi*i/7
        stem=(.34*math.cos(t),.85,.34*math.sin(t))
        m.cylinder((0,.12,0),stem,.05,"root",f"stem_{i}",sides=6)
        m.ellipsoid(stem,(.3,.12,.3),"route_membrane",f"cup_{i}",rings=3,segments=7)
    m.write({"GroundPivot":[0,0,0],"CameraAnchor":[0,.7,0]})


def plant_branch(name, height, arms):
    m=Mesh(name)
    m.cylinder((0,.11,0),(0,height,0),.11,"root","trunk",sides=7)
    for i in range(arms):
        y=.35+height*.55*i/max(1,arms-1)
        side=-1 if i%2 else 1
        end=(side*(.45+.09*i),y+.32,.12*math.sin(i))
        m.cylinder((0,y,0),end,.07,"root",f"branch_{i}",sides=6)
        m.ellipsoid(end,(.16,.2,.08),"route_membrane",f"polyp_{i}",rings=3,segments=6)
    m.write({"GroundPivot":[0,0,0],"CameraAnchor":[0,height*.6,0]})


def ground_detail(name, kind):
    m=Mesh(name)
    if kind=="ripples":
        for i in range(3):
            z=-.55+i*.55
            m.cylinder((-1.2,.025,z),(1.2,.025,z),.025,"sand","ripple",sides=5)
    elif kind=="pebbles":
        for i,(x,z,r) in enumerate([(-.8,-.3,.22),(-.25,.2,.16),(.22,-.15,.19),(.7,.25,.25),(.05,.55,.12)]):
            m.ellipsoid((x,0,z),(r,r*.45,r*.8),"rock",f"pebble_{i}",rings=3,segments=6)
    else:
        for i,(a,b) in enumerate([((-1.2,.05,-.5),(1.1,.05,.45)),((-.9,.05,.6),(.65,.05,-.65)),((-.3,.05,.75),(.2,.05,-.75))]):
            m.cylinder(a,b,.035,"organic_dark" if "organic_dark" in MATERIALS else "rock","scar",sides=5)
    m.write({"GroundPivot":[0,0,0]})


def channel_bank(name, bend=False):
    m=Mesh(name)
    if not bend:
        for side in (-1,1):
            m.box((side*3.25,.22,0),(2.1,.44,8),"flood_silt",f"bank_{side}")
            for z in (-3,-1,1,3):
                m.ellipsoid((side*2.35,.25,z),(1.35,.18,1.45),"flood_silt",f"bank_lip_{side}_{z}",rings=3,segments=8)
        anchors={"SnapNorth":[0,0,-4],"SnapSouth":[0,0,4],"FlowAnchor":[0,.05,0]}
    else:
        m.box((-2.8,.22,-1.5),(2.2,.44,5),"flood_silt","outer_bank_a")
        m.box((-1.5,.22,-2.8),(5,.44,2.2),"flood_silt","outer_bank_b")
        m.ellipsoid((1.8,.18,1.8),(2.2,.16,2.2),"flood_silt","inner_deposit",rings=3,segments=9)
        anchors={"SnapWest":[-4,0,0],"SnapNorth":[0,0,-4],"FlowAnchor":[0,.05,0]}
    m.write(anchors)


def floodplain_shelf():
    m=Mesh("floodplain_shelf_a")
    m.ellipsoid((0,0,0),(5.8,.28,3.8),"flood_silt","shelf",rings=4,segments=14)
    for z in (-2.1,-.7,.7,2.1):
        m.cylinder((-4.5,.31,z),(4.4,.31,z+.22),.055,"carbonate","deposition_ripple",sides=6)
    for x in (-3.4,0,3.0):
        m.ellipsoid((x,.28,-2.6),(.5,.16,.75),"living_green","edge_growth",rings=3,segments=7)
    m.write({"GroundPivot":[0,0,0],"CultivationAnchor":[0,.3,0],"WetEdge":[0,.1,3.5]})


def silica_cliff():
    m=Mesh("silica_cliff_a")
    for i,(x,z,rx,ry,rz) in enumerate([(-3.5,.7,2.2,1.5,2.1),(-1.2,.3,2.4,2.0,2.3),(1.3,.5,2.7,1.7,2.2),(3.5,.8,2.0,1.35,1.8)]):
        m.ellipsoid((x,0,z),(rx,ry,rz),"rock",f"cliff_mass_{i}",rings=4,segments=9)
    for i,(x,h,r) in enumerate([(-3.5,4.8,.55),(-2.1,6.1,.68),(-.4,4.2,.62),(1.1,6.8,.78),(2.8,5.4,.64),(3.7,3.7,.48)]):
        m.cone((x,.7,-.35),h,r,.08,"silica",f"silica_spire_{i}",sides=7)
        m.ellipsoid((x,.35,-1.15),(r*1.5,.3,r*1.1),"carbonate",f"spire_foot_{i}",rings=3,segments=7)
    m.write({"SnapLeft":[-4.5,0,0],"SnapRight":[4.5,0,0],"ExtractionAnchor":[0,0,-2],"CameraAnchor":[0,4,0]})


def methane_seep():
    m=Mesh("methane_seep_a")
    for i,(x,z,rx,rz) in enumerate([(-2.5,-.5,2.5,1.7),(1.0,.7,3.0,2.1),(3.3,-1.4,1.7,1.25)]):
        m.ellipsoid((x,0,z),(rx,.11,rz),"methane_film",f"seep_film_{i}",rings=3,segments=12)
    for i,(x,z,h) in enumerate([(-3.2,-.7,1.3),(-.4,.5,.9),(1.5,.2,1.7),(3.5,-1.5,1.15)]):
        m.cone((x,.08,z),h,.48,.16,"methane",f"gas_vent_{i}",sides=7)
        m.ellipsoid((x,h+.18,z),(.32,.22,.32),"methane_film",f"gas_sac_{i}",rings=3,segments=7)
    m.write({"GroundPivot":[0,0,0],"FilterAnchor":[0,.15,2.8],"HazardAnchor":[1,0,0]})


def sulphur_vents():
    m=Mesh("sulphur_vent_cluster_a")
    m.ellipsoid((0,0,0),(4.5,.35,3.4),"rock","vent_bed",rings=4,segments=12)
    for i,(x,z,h,r) in enumerate([(-2.5,-1.0,3.6,.75),(-.8,1.1,5.2,1.0),(1.1,-.8,4.3,.85),(2.7,1.0,3.1,.65)]):
        m.cone((x,.2,z),h,r,.28,"sulphur",f"vent_{i}",sides=8)
        m.ellipsoid((x,h+.28,z),(.5,.32,.5),"carbonate",f"vent_crown_{i}",rings=3,segments=7)
    m.write({"GroundPivot":[0,0,0],"ExtractionAnchor":[0,.4,-3],"CameraAnchor":[0,3,0]})


def delta_island(name, phase):
    m=Mesh(name)
    m.ellipsoid((0,0,0),(5.5,.24,2.4),"flood_silt","island",rings=4,segments=14)
    for i in range(7):
        x=-3.8+i*1.25
        z=.5*math.sin(i*1.8+phase)
        m.cylinder((x,.22,z),(x+.18,.85+.18*math.cos(i),z+.12),.06,"living_green",f"filter_stalk_{i}",sides=6)
    m.write({"GroundPivot":[0,0,0],"DepositAnchor":[0,.25,0],"FlowLeft":[-5.5,0,0],"FlowRight":[5.5,0,0]})


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
    plant_fan("plant_fan_a",1.2,1.35,5)
    plant_fan("plant_fan_b",1.7,1.8,7)
    plant_ribbon("plant_ribbon_a",1.6,5)
    plant_ribbon("plant_ribbon_b",2.25,7)
    plant_cup()
    plant_branch("plant_branch_a",1.55,4)
    plant_branch("plant_branch_b",2.1,6)
    ground_detail("detail_ripple_a","ripples")
    ground_detail("detail_pebbles_a","pebbles")
    ground_detail("detail_scar_a","scar")
    channel_bank("channel_bank_straight_a")
    channel_bank("channel_bank_bend_a",bend=True)
    floodplain_shelf()
    silica_cliff()
    methane_seep()
    sulphur_vents()
    delta_island("delta_island_a",0.0)
    delta_island("delta_island_b",1.7)
    assets=[p.stem for p in sorted(OUT.glob("*.obj"))]
    (OUT/"manifest.json").write_text(json.dumps({"generated_by":"tools/generate_environment_blockouts.py","units":"metres","up_axis":"+Y","assets":assets},indent=2)+"\n")
    print(f"Generated {len(assets)} environment assets in {OUT}")


if __name__=="__main__":
    main()
