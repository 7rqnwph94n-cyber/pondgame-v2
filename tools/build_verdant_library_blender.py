"""Rebuild the Verdant presentation library, retaining the original blockouts.

Blender 5.x: blender -b -t 4 --python tools/build_verdant_library_blender.py
Exports deterministic Y-up OBJ meshes with authored normals, material families,
visual anchors, an inventory, editable Blender source, and review sheets.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/verdant_v2"
RENDER = ROOT / "docs/art/renders/library_v02"
OUT.mkdir(parents=True, exist_ok=True)
RENDER.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version = 0

COLOURS = {
    "shell": "174B50", "shell_light": "286B68", "growth": "75B96B",
    "membrane": "C3EDC2", "amber": "FFC05A", "carbonate": "D9D5BE",
    "silica": "8CE0DE", "silt": "615D4E", "pigment": "EF7967",
    "memory": "77729C", "dark": "173331", "rock": "344746",
    "fibre": "8A9F6B", "resin": "C48B39", "ceramic": "B4B19A",
    "anoxic": "27353E", "sulphur": "9F8441",
}
RGB = {k: tuple(int(v[i:i + 2], 16) / 255 for i in (0, 2, 4)) for k, v in COLOURS.items()}


def linear(v):
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


MATS = {}
for key, rgb in RGB.items():
    material = bpy.data.materials.new("verdant_" + key)
    material.diffuse_color = (*map(linear, rgb), 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = material.diffuse_color
    shader.inputs["Roughness"].default_value = 0.34 if key in ("shell", "shell_light", "resin", "silica") else 0.68
    MATS[key] = material

inventory = []
groups = {}


def group(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    groups[name] = col
    return col


def mesh(name, verts, faces, material, col, smooth=True):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.materials.append(MATS[material])
    data.update()
    for poly in data.polygons:
        poly.use_smooth = smooth
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    return obj


def ball(col, name, p, size, material="shell", detail=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=detail, ring_count=8, location=p)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(MATS[material])
    for face in obj.data.polygons:
        face.use_smooth = True
    return obj


def tube(col, name, points, radius, material="carbonate", sides=6):
    verts, faces = [], []
    for i, point in enumerate(points):
        tangent = Vector(points[min(i + 1, len(points) - 1)]) - Vector(points[max(0, i - 1)])
        tangent.normalize()
        axis = Vector((0, 0, 1)) if abs(tangent.z) < 0.9 else Vector((0, 1, 0))
        u = tangent.cross(axis).normalized()
        v = tangent.cross(u).normalized()
        rad = radius * (1 - 0.25 * i / max(1, len(points) - 1))
        for j in range(sides):
            a = j * math.tau / sides
            verts.append(Vector(point) + rad * (math.cos(a) * u + math.sin(a) * v))
    for i in range(len(points) - 1):
        for j in range(sides):
            n = (j + 1) % sides
            faces.append((i * sides + j, i * sides + n, (i + 1) * sides + n, (i + 1) * sides + j))
    faces += [tuple(reversed(range(sides))), tuple((len(points) - 1) * sides + j for j in range(sides))]
    return mesh(name, verts, faces, material, col)


def hoop(col, name, p, radius, material="carbonate", thickness=0.055, oval=(1, 1), tilt=0):
    points = []
    for i in range(33):
        a = i * math.tau / 32
        r = radius * (1 + 0.025 * math.sin(5 * a))
        points.append((p[0] + r * math.cos(a) * oval[0], p[1] + r * math.sin(a) * oval[1] * math.cos(tilt), p[2] + r * math.sin(a) * oval[1] * math.sin(tilt)))
    return tube(col, name, points, thickness, material)


def cup(col, p, radius=0.8, height=0.48, fill="dark"):
    # An open bowl with a continuous rim and a recessed interior.
    verts, faces = [], []
    rings = ((0.48, 0), (0.8, height * 0.35), (1, height), (0.85, height * 0.93), (0.47, height * 0.27))
    for r, z in rings:
        for j in range(24):
            a = j * math.tau / 24
            verts.append((p[0] + radius * r * math.cos(a), p[1] + radius * r * math.sin(a), p[2] + z))
    for k in range(len(rings) - 1):
        for j in range(24):
            n = (j + 1) % 24
            faces.append((k * 24 + j, k * 24 + n, (k + 1) * 24 + n, (k + 1) * 24 + j))
    mesh("open living cup", verts, faces, "shell_light", col)
    hoop(col, "grown cup lip", (p[0], p[1], p[2] + height), radius, thickness=0.045)
    ball(col, "visible cup contents", (p[0], p[1], p[2] + height * 0.29), (radius * 0.68, radius * 0.68, 0.07), fill)


def leaf(col, p, height=1.6, width=0.38, angle=0, material="growth", bend=0.5):
    verts, faces, spine = [], [], []
    for i in range(9):
        t = i / 8
        w = width * math.sin(math.pi * t) ** 0.8
        centre = Vector((p[0] + math.cos(angle) * bend * t * t, p[1] + math.sin(angle) * bend * t * t, p[2] + height * t))
        lateral = Vector((-math.sin(angle), math.cos(angle), 0))
        spine.append(tuple(centre + Vector((0, 0, 0.012))))
        verts += [centre - lateral * w, centre + Vector((0, 0, 0.08 * math.sin(math.pi * t))), centre + lateral * w]
    for i in range(8):
        for j in range(2):
            faces.append((i * 3 + j, (i + 1) * 3 + j, (i + 1) * 3 + j + 1, i * 3 + j + 1))
    mesh("bent living blade", verts, faces, material, col)
    tube(col, "leaf midrib", spine, 0.024, "fibre", 5)


def dome(col, p, size=(1.1, 0.9, 1.1), material="shell", ribs=7):
    # A protected half shell; the lower front sector remains open to the brood.
    verts, faces = [], []
    n = 32
    for k in range(9):
        phi = k * math.pi / 16
        for j in range(n):
            a = j * math.tau / n
            verts.append((p[0] + size[0] * math.cos(phi) * math.cos(a), p[1] + size[1] * math.cos(phi) * math.sin(a), p[2] + size[2] * math.sin(phi)))
    for k in range(8):
        for j in range(n):
            a = (j + 0.5) * math.tau / n
            if k < 3 and math.sin(a) < -0.83:
                continue
            faces.append((k*n+j, k*n+(j+1)%n, (k+1)*n+(j+1)%n, (k+1)*n+j))
    mesh("inhabited shell", verts, faces, material, col)
    for i in range(ribs):
        a = math.tau * i / ribs + 0.1
        pts = [(p[0] + size[0] * math.cos(t) * math.cos(a), p[1] + size[1] * math.cos(t) * math.sin(a), p[2] + size[2] * math.sin(t) + 0.025) for t in [j * math.pi / 16 for j in range(9)]]
        tube(col, "growth seam", pts, 0.035, "carbonate")
    ball(col, "warm occupied cavity", (p[0], p[1] - size[1] * 0.5, p[2] + 0.28), (0.25, 0.14, 0.24), "amber")


def base(col, radius=2):
    for x,y,s in ((-0.35,0.1,0.69),(0.42,0.2,0.58),(0,-0.35,0.62)):
        ball(col, "irregular anchoring lobe", (x,y,0.045), (radius*s,radius*s*0.72,0.085), "dark")
    for i in range(7):
        a = i * math.tau / 7 + 0.2 + 0.12*math.sin(i*3)
        reach=radius*(0.83+0.12*math.sin(i*2))
        tube(col, "anchoring root", [(math.cos(a)*radius*0.38, math.sin(a)*radius*0.3, 0.17), (math.cos(a+0.12)*radius*0.62, math.sin(a+0.12)*radius*0.5, 0.12), (math.cos(a)*reach, math.sin(a)*reach*0.76, 0.035)], 0.075, "shell_light")


def crystal(col, p, height=1.2, radius=0.25, material="silica"):
    verts = []
    for z, r, ox in ((0, radius, 0), (height * 0.7, radius * 0.78, height * 0.13)):
        verts += [(p[0]+ox+r*math.cos(i*math.tau/5), p[1]+r*math.sin(i*math.tau/5), p[2]+z) for i in range(5)]
    verts.append((p[0]+height*0.17, p[1], p[2]+height))
    faces = [tuple(reversed(range(5)))]
    for i in range(5):
        j = (i + 1) % 5
        faces.extend(((i, j, j+5, i+5), (i+5, j+5, 10)))
    mesh("cleaved mineral", verts, faces, material, col, False)


def export(col, name, family, anchors=None, provenance="new Blender geometry"):
    folder = OUT / family
    folder.mkdir(exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in col.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = list(col.objects)[0]
    path = folder / (name + ".obj")
    bpy.ops.wm.obj_export(filepath=str(path), export_selected_objects=True, export_triangulated_mesh=True, forward_axis="NEGATIVE_Z", up_axis="Y")
    # OBJ colours are sRGB; Blender shaders use linear colours. Keep the two
    # representations aligned instead of baking the contact-sheet lighting.
    mtl = folder / (name + ".mtl")
    lines, current = [], None
    for line in mtl.read_text().splitlines():
        if line.startswith("newmtl verdant_"):
            current = line.split("verdant_", 1)[1]
        if line.startswith("Kd ") and current in RGB:
            line = "Kd " + " ".join(f"{v:.6f}" for v in RGB[current])
        lines.append(line)
    mtl.write_text("\n".join(lines) + "\n")
    pts = [obj.matrix_world @ v.co for obj in col.objects if obj.type == "MESH" for v in obj.data.vertices]
    triangles = sum(len(p.vertices)-2 for o in col.objects if o.type == "MESH" for p in o.data.polygons)
    bounds = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
    record = {"id": name, "family": family, "triangles": triangles, "objects": len(col.objects), "bounds_blender_z_up": bounds, "provenance": provenance, "status": "candidate", "path": str(path.relative_to(ROOT))}
    inventory.append(record)
    anchor_data = {"asset": name, "units": "metres", "up_axis": "+Y", "ground_pivot": [0,0,0], "anchors": anchors or {"LabelAnchor": [0,bounds[2][1]+0.3,0], "InputAnchor": [-1.7,0.4,0], "OutputAnchor": [1.7,0.4,0]}}
    (folder / (name + ".anchors.json")).write_text(json.dumps(anchor_data, indent=2) + "\n")


def residence(name, tier):
    col = group(name)
    base(col, 1.9 + tier * 0.38)
    dome(col, (-0.35, 0.05, 0.15), (1.2,1,1.1+0.13*tier))
    if tier >= 1:
        dome(col, (1.05,0.55,0.15), (0.75,0.7,0.86))
        cup(col, (0.7,-0.9,0.15), 0.58, 0.35, "growth")
    if tier >= 2:
        dome(col, (-1.25,0.75,0.15), (0.68,0.7,0.82))
        for i in range(5):
            leaf(col, (-1.4+i*0.55,1.1,0.22), 1.5+i%2*0.4, 0.28, 0.3+i, "membrane", 0.25)
        for i in range(4):
            leaf(col, (-1.7+i*0.85,-0.65,0.15), 0.7, 0.17, i*1.2)
    if tier >= 3:
        hoop(col, "memory crown base", (0,0.4,1.5), 0.62, "memory")
        for i in range(5):
            a=i*math.tau/5
            crystal(col, (math.cos(a)*0.5,0.4+math.sin(a)*0.5,1.5), 0.72+i%2*0.25, 0.16)
        for i in range(5):
            ball(col, "encoded pigment", (-1+i*0.5,-0.72,0.48), (0.07,0.06,0.07), "pigment")
    return col


def facility(name, kind):
    col=group(name)
    base(col, 2.15)
    if kind in ("general_store", "living_goods_store", "trade_landing"):
        for i in range(3):
            cup(col, (-1.15+i*1.12,0,0.2),0.64,0.7, ("silica","carbonate","growth")[i])
        for x in (-1.2,0,1.2):
            tube(col,"arched storage rib",[(x,-0.7,0.1),(x,-0.55,1.1),(x,0,1.65),(x,0.65,0.8),(x,0.85,0.1)],0.07)
        if kind=="living_goods_store":
            for i in range(4): leaf(col,(-1.2+i*0.75,0.65,0.15),1.8,0.48,math.pi,"membrane",0.7)
        if kind=="trade_landing":
            for i in range(5): leaf(col,(-1+i*0.5,0.75,0.18),2.0+i%2*0.4,0.3,0,"membrane",0.4)
    elif kind in ("photosynthetic_field","culture_bed","fibre_garden","resin_grove","pigment_bed"):
        for i in range(6):
            x=(i%3-1)*1.05; y=(i//3-0.5)*0.9
            cup(col,(x,y,0.14),0.47,0.28,"pigment" if kind=="pigment_bed" else "growth")
            if kind=="resin_grove":
                leaf(col,(x,y,0.3),1.2+(i%2)*0.35,0.3,i,"growth",0.3)
                ball(col,"resin secretion",(x+0.1,y-0.05,0.7),(0.17,0.15,0.25),"resin")
            elif kind=="fibre_garden":
                for j in range(3): leaf(col,(x+j*0.13-0.13,y,0.3),1.5+j*0.15,0.12,0.3,"fibre",0.5)
            elif kind=="photosynthetic_field":
                leaf(col,(x,y,0.25),0.8+(i%2)*0.2,0.42,i*0.5,"growth",0.55)
            else:
                for j in range(3): ball(col,"culture vesicle",(x+(j-1)*0.16,y,0.46),(0.13,0.16,0.13),"pigment" if kind=="pigment_bed" else "growth")
    elif kind in ("nutrient_washer","mineral_washery","channel_separator","nutrient_kitchen","retting_pool"):
        fills={"mineral_washery":"silica","nutrient_washer":"growth","channel_separator":"membrane","nutrient_kitchen":"amber","retting_pool":"fibre"}
        for i in range(3):
            x=-1.1+i*1.1; z=0.9-i*0.3
            ball(col,"supporting chamber",(x,0,z/2),(0.64,0.55,z/2),"shell")
            cup(col,(x,0,z),0.65,0.32,fills[kind])
            if i<2: tube(col,"visible process throat",[(x+0.4,0,z+0.2),(x+0.67,0,z+0.15),(x+0.85,0,z-0.12)],0.075,"membrane")
        for i in range(4): leaf(col,(-1.3+i*0.3,0.6,0.1),1.8,0.18,i,"membrane",0.25)
        if kind=="retting_pool":
            for i in range(6): tube(col,"separated fibre",[(-0.5,-0.55+i*0.1,0.6),(1.45,-0.55+i*0.1,0.45)],0.027,"fibre",5)
        if kind=="nutrient_kitchen": cup(col,(0,-0.8,0.2),0.42,0.4,"growth")
    elif kind in ("ceramic_kiln","resin_curing","waste_digester","emergency_enzyme","anoxic_pump","detox_clinic"):
        hot=kind=="ceramic_kiln"
        dome(col,(0,0.2,0.15),(1.15,0.85,1.7 if hot else 1.2),"ceramic" if hot else "shell")
        for side in (-1,1):
            ball(col,"processing side sac",(side*1.12,0.15,0.6),(0.52,0.5,0.7),"anoxic" if kind in ("waste_digester","anoxic_pump","detox_clinic") else "resin")
            hoop(col,"sac growth band",(side*1.12,0.15,0.73),0.5,"carbonate",0.035)
        cup(col,(-1,-0.65,0.15),0.48,0.35,"dark")
        cup(col,(1,-0.65,0.15),0.48,0.35,"ceramic" if hot else "amber")
        if hot:
            for i in range(3): hoop(col,"insulating growth band",(0,0.2,0.5+i*0.35),1.05-i*0.14,"ceramic",0.055)
        else:
            for i in range(3): leaf(col,(-0.4+i*0.4,0.7,0.15),1.8+i%2*0.3,0.18,i,"membrane",0.3)
    elif kind in ("composite_workshop","artisan_organ"):
        for i in range(6):
            a=i*math.tau/6
            tube(col,"tensioned forming rib",[(math.cos(a)*1.5,math.sin(a)*0.9,0.15),(math.cos(a+0.2)*0.9,math.sin(a+0.2)*0.65,1.3),(0,0,2)],0.065,"fibre")
        for z in (0.55,1.05,1.55): hoop(col,"woven cross strand",(0,0,z),1.45-z*0.55,"resin",0.04,oval=(1,0.7))
        cup(col,(0,0,0.2),0.6,0.4,"pigment" if kind=="artisan_organ" else "silica")
        for i in range(3): cup(col,(-0.9+i*0.9,-0.9,0.1),0.28,0.25,("resin","fibre","pigment")[i])
    elif kind in ("sediment_dredge","filter_crown","silicate_pit","carbonate_cutter"):
        dome(col,(0,0.4,0.15),(0.95,0.75,0.95))
        if kind=="filter_crown":
            for i in range(9): leaf(col,(-1.1+i*0.28,0.4,0.35),1.7+0.5*math.sin(i/8*math.pi),0.21,(i-4)*0.15,"membrane",0.35)
        elif kind=="sediment_dredge":
            for side in (-1,1):
                tube(col,"dredging limb",[(side*0.6,0.1,0.7),(side*1.5,-0.45,0.85),(side*1.6,-1,0.2)],0.12,"shell")
                ball(col,"digging paddle",(side*1.6,-1,0.2),(0.4,0.52,0.11),"carbonate")
        else:
            for i in range(4): crystal(col,(-1+i*0.65,-0.8,0.15),0.5+i%2*0.4,0.27,"silica" if kind=="silicate_pit" else "carbonate")
            for side in (-1,1): tube(col,"mineral brace",[(side*0.6,0,0.6),(side*1.3,-0.3,1.2),(side*0.75,-0.9,0.4)],0.11,"carbonate")
        cup(col,(1.15,0.65,0.15),0.46,0.35,"silt")
    else:
        # Civic families retain radial calm but have distinct functional crowns.
        dome(col,(0,0.15,0.15),(1.05,0.9,1.05))
        count=7 if kind=="additional_nursery" else 5 if kind=="first_nursery" else 3
        for i in range(count):
            a=i*math.tau/count
            p=(math.cos(a)*1.25,math.sin(a)*0.83,0.15)
            cup(col,p,0.38,0.35,"amber" if "nursery" in kind else "membrane")
            if "nursery" in kind: ball(col,"brood egg",(p[0],p[1],0.58),(0.12,0.12,0.17),"membrane")
        if kind in ("clean_flow_node","distribution_node"):
            for i in range(5): leaf(col,(-0.6+i*0.3,0.5,0.5),1.5+0.4*math.sin(i*math.pi/4),0.27,i*0.3,"membrane",0.4)
        elif kind=="survey_organ":
            tube(col,"sensory stalk",[(0,0.3,0.8),(0.1,0.4,1.8),(0,0.5,2.3)],0.09,"shell")
            for i in range(6): leaf(col,(0,0.5,2),0.65,0.18,i*math.tau/6,"membrane",0.65)
        elif kind=="memory_circle":
            for i in range(6):
                a=i*math.tau/6
                crystal(col,(math.cos(a)*1.25,math.sin(a)*0.83,0.45),0.85,0.13,"memory")
        elif kind=="maintenance_organ":
            for i in range(3): tube(col,"repair feeler",[(-0.6+i*0.6,0.5,0.7),(-0.6+i*0.6,0.7,1.6),(-0.4+i*0.5,0.2,1.9)],0.075,"fibre")
        elif kind=="waste_collector":
            cup(col,(0,-0.95,0.2),0.68,0.45,"anoxic")
    return col


defs=json.loads((ROOT/"economy/data/verdant_v0_2.json").read_text())
mapping={}
res_names={"shelter":"res_shelter_cluster_a","stable":"res_stable_habitat_a","symbiotic":"res_symbiotic_a","memory":"res_memory_enclave_a"}
for tier,(key,name) in enumerate(res_names.items()):
    col=residence(name,tier)
    export(col,name,"settlement")
for key in defs["buildings"]:
    if key=="shelter":
        mapping[key]=res_names["shelter"]
        continue
    name="building_"+key+"_a"
    col=facility(name,key)
    export(col,name,"settlement")
    mapping[key]=name

# All goods have a portable physical form using the same material as their
# source/processor. Value is encoded as a cultural token, not a coin from Earth.
for index,key in enumerate(defs["resources"]):
    name="payload_"+key+"_a"; col=group(name)
    material=("silica" if "silic" in key else "carbonate" if key=="carbonate" else "fibre" if "fibre" in key else "resin" if "resin" in key else "pigment" if "pigment" in key else "ceramic" if "ceramic" in key else "dark" if key in ("organic_waste","anoxic_organics") else "amber" if key in ("repair_enzyme","balanced_gel","stored_value") else "growth")
    for i in range(4):
        a=i*2.4
        p=(math.cos(a)*0.15,math.sin(a)*0.15,0.08)
        if key=="raw_silicate": crystal(col,p,0.35+i*0.08,0.1)
        elif "fibre" in key: tube(col,"bound strand",[(p[0]-0.3,p[1],0.1+i*0.04),(p[0]+0.3,p[1]+0.05,0.14+i*0.04)],0.045,material)
        else: ball(col,"payload piece",p,(0.16,0.12,0.09+(i%2)*0.04),material,12)
    export(col,name,"settlement",{"PayloadAnchor":[0,0,0]})

# Upgrade every existing environmental object: weld the duplicated blockout
# poles, remove degenerate faces, recalculate outward normals, harmonise palette.
def material_family(name):
    n=name.lower()
    for term,key in (("carbonate","carbonate"),("silica","silica"),("silicate","silica"),("sulphur","sulphur"),("methane","anoxic"),("amber","amber"),("signal","amber"),("rim","carbonate"),("membrane","membrane"),("cilia","membrane"),("living","growth"),("bower","growth"),("root","fibre"),("rock","rock"),("silt","silt"),("sand","silt"),("route","shell_light"),("current","shell")):
        if term in n: return key
    return "rock"

for path in sorted((ROOT/"assets/blockout/environment").glob("*.obj")):
    name=path.stem
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.wm.obj_import(filepath=str(path),forward_axis="NEGATIVE_Z",up_axis="Y")
    imported=list(bpy.context.selected_objects)
    col=group(name)
    for obj in imported:
        for old in list(obj.users_collection): old.objects.unlink(obj)
        col.objects.link(obj)
        bm=bmesh.new(); bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=0.0001)
        bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=0.00001)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        bm.to_mesh(obj.data); bm.free()
        for slot in obj.material_slots:
            family=material_family(slot.material.name if slot.material else "rock")
            slot.material=MATS[family]
        for face in obj.data.polygons:
            material=obj.data.materials[face.material_index].name if obj.data.materials else ""
            face.use_smooth=not any(k in material for k in ("rock","silica","silt","carbonate"))
    anchors_path=path.with_suffix(".anchors.json")
    anchors=json.loads(anchors_path.read_text())["anchors"] if anchors_path.exists() else None
    export(col,name,"environment",anchors,provenance=str(path.relative_to(ROOT))+"; topology and material refinement")

# Six new current-swept plant clumps, each with a different stature and density.
for variant in range(6):
    name=f"plant_current_meadow_{variant+1:02d}"; col=group(name)
    rng=random.Random(510+variant)
    for i in range(5+variant):
        x=rng.uniform(-0.9,0.9); y=rng.uniform(-0.65,0.65)
        leaf(col,(x,y,0.03),rng.uniform(0.8,1.6)*(0.65+variant*0.16),rng.uniform(0.14,0.32),0.3+variant*0.25,"growth" if variant%2==0 else "membrane",0.45+variant*0.1)
    export(col,name,"environment")

# A redesigned carrier plus the six silhouette-changing morphology options.
for family in ("silicate","carbonate"):
    for stage,count in (("rich",13),("worked",5),("depleted",0)):
        name=f"patch_{family}_{stage}_a"; col=group(name)
        rng=random.Random(418)
        for i in range(5):
            p=(rng.uniform(-1.4,1.4),rng.uniform(-1,1),0.15)
            ball(col,"exposed resource matrix",p,(0.85,0.65,0.32),"rock" if family=="silicate" else "carbonate",12)
        for i in range(count):
            x=rng.uniform(-1.5,1.5); y=rng.uniform(-0.9,0.9)
            if family=="silicate": crystal(col,(x,y,0.25),rng.uniform(0.55,1.65),rng.uniform(0.16,0.32))
            else:
                cup(col,(x,y,0.22),rng.uniform(0.25,0.5),rng.uniform(0.3,0.6),"carbonate")
                # Chalk on the exposed exterior keeps this distinct from a civic organ.
                for obj in list(col.objects)[-3:]:
                    for slot in obj.material_slots:
                        if slot.material==MATS["shell_light"]: slot.material=MATS["carbonate"]
        for i in range(7):
            x=rng.uniform(-1.5,1.5); y=rng.uniform(-1,1)
            tube(col,"worked mineral scar",[(x-0.25,y,0.22),(x+0.25,y+0.1,0.25)],0.025,"silica" if family=="silicate" else "ceramic",5)
        export(col,name,"environment")

# A redesigned carrier plus the six silhouette-changing morphology options.
for kind in ("general","burrowing","filter","mineral_jaw","detox","vascular","memory"):
    name="unit_"+kind+"_carrier_a"; col=group(name)
    ball(col,"streamlined abdomen",(0,0.15,0.53),(0.55,0.9,0.4))
    dome(col,(0,-0.55,0.48),(0.43,0.44,0.35),ribs=5)
    for side in (-1,1):
        ball(col,"amber eye",(side*0.28,-0.8,0.64),(0.1,0.08,0.11),"amber")
        for i in range(3):
            y=-0.3+i*0.45
            leaf(col,(side*0.4,y,0.45),0.18,0.16,0 if side==1 else math.pi,"membrane",0.6)
        cup(col,(side*0.42,0.35,0.74),0.27 if kind!="vascular" else 0.42,0.2,"dark")
    if kind=="burrowing":
        for s in (-1,1): ball(col,"broad paddle",(s*0.65,-0.65,0.25),(0.3,0.4,0.1),"carbonate")
    if kind=="filter":
        for i in range(7): leaf(col,(-0.4+i*0.13,-0.55,0.8),0.65,0.1,(i-3)*0.3,"membrane",0.3)
    if kind=="mineral_jaw":
        for s in (-1,1): crystal(col,(s*0.22,-0.95,0.35),0.38,0.13)
    if kind=="detox":
        for s in (-1,1): ball(col,"detox sac",(s*0.55,0,0.6),(0.22,0.3,0.25),"anoxic")
    if kind=="memory":
        ball(col,"protected ganglion",(0,-0.2,1),(0.27,0.3,0.2),"memory")
        for i in range(5): tube(col,"signal tendril",[(0,-0.15,1.1),((i-2)*0.2,-0.15,1.4)],0.02,"membrane",5)
    export(col,name,"settlement",{"PayloadAnchor":[0,1,0.35],"LabelAnchor":[0,1.6,0]})

for stage in range(4):
    name=f"great_work_memory_reef_stage_{stage}"; col=group(name)
    base(col,4.0)
    for ring in range(2): hoop(col,"accreting reef foundation",(0,0,0.2+ring*0.25),2.8-ring*0.55,"carbonate",0.18,oval=(1,0.82))
    if stage>=1:
        for i in range(9):
            a=i*math.tau/9
            tube(col,"reef buttress",[(math.cos(a)*2.8,math.sin(a)*2.25,0.2),(math.cos(a+0.1)*1.9,math.sin(a+0.1)*1.5,1.35),(math.cos(a)*1.1,math.sin(a)*0.9,2.4)],0.14,"carbonate")
    if stage>=2:
        for z in (0.75,1.2,1.65,2.1): hoop(col,"living reef lattice",(0,0,z),2.9-z*0.72,"fibre",0.075,oval=(1,0.82))
        for i in range(7): leaf(col,(-1.5+i*0.5,0.4,0.3),2.8,0.38,i*0.4,"membrane",0.55)
    if stage>=3:
        for i in range(7):
            a=i*math.tau/7
            crystal(col,(math.cos(a)*1.2,math.sin(a)*0.85,2.15),1.3+i%2*0.35,0.26)
            ball(col,"encoded memory node",(math.cos(a)*2.3,math.sin(a)*1.8,0.75),(0.16,0.16,0.2),"memory")
    export(col,name,"settlement")

for stage in range(3):
    name=f"construction_growth_stage_{stage}"; col=group(name)
    base(col,1.9)
    for i in range(7):
        a=i*math.tau/7
        tube(col,"living scaffold rib",[(math.cos(a)*1.55,math.sin(a)*1.15,0.1),(math.cos(a)*1.1,math.sin(a)*0.8,0.75),(0,0,1.35)],0.055,"fibre")
    if stage>=1:
        dome(col,(0,0,0.12),(0.9,0.72,0.85),"shell_light")
    if stage>=2:
        for i in range(4): leaf(col,(-0.6+i*0.4,0.45,0.2),1.15,0.2,i,"growth",0.3)
    export(col,name,"settlement")

style=json.loads((ROOT/"client/presentation/asset_map.json").read_text())
style["asset_dir"]="../assets/verdant_v2/settlement"
style["environment_dir"]="../assets/verdant_v2/environment"
style["buildings"]=mapping
style["residence_tiers"]=res_names
style["payloads"]={key:"payload_"+key+"_a" for key in defs["resources"]}
style["carrier_morphologies"]={key:"unit_"+key+"_carrier_a" for key in ("general","burrowing","filter","mineral_jaw","detox","vascular","memory")}
style["great_work_stages"]=[f"great_work_memory_reef_stage_{i}" for i in range(4)]
style["construction_growth_stages"]=[f"construction_growth_stage_{i}" for i in range(3)]
style["resource_patch_states"]={family:{stage:f"patch_{family}_{stage}_a" for stage in ("rich","worked","depleted")} for family in ("silicate","carbonate")}
scenery=style["environment"]["scenery"]
scenery[:]=[item for item in scenery if not item["asset"].startswith("plant_current_meadow_")]
for i,(x,z) in enumerate(((-40,5),(-25,27),(32,30),(-46,-18),(44,-14),(12,34))):
    scenery.append({"asset":f"plant_current_meadow_{i+1:02d}","position":[x,0.08,z],"rotation_y":i*31,"scale":0.9})
style["_comment"]="Blender Verdant library v2; presentation mapping only. Original blockouts retained."
(OUT/"draft_asset_map.json").write_text(json.dumps(style,indent=2)+"\n")
(OUT/"manifest.json").write_text(json.dumps({"version":2,"units":"metres","up_axis":"+Y","assets":inventory},indent=2)+"\n")

# Store every exported collection, separated for editability. Source layout
# is a catalogue; OBJ exports above retain their local pivots.
for i,record in enumerate(inventory):
    col=groups[record["id"]]
    for obj in col.objects:
        obj.location+=Vector(((i%12)*9,(i//12)*9,0))

scene=bpy.context.scene
scene.render.engine="CYCLES"; scene.cycles.samples=24
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(0.14,0.2,0.21,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0.6
scene.view_settings.view_transform="AgX"
for loc,power,size in (((-8,-10,20),2400,12),((10,7,14),1800,10)):
    bpy.ops.object.light_add(type="AREA",location=loc)
    bpy.context.object.data.energy=power; bpy.context.object.data.size=size
    bpy.context.object.rotation_euler=(Vector((0,0,0))-bpy.context.object.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(9,-14,18))
camera=bpy.context.object; camera.data.type="ORTHO"; scene.camera=camera
camera.rotation_euler=(Vector((0,0,0.4))-camera.location).to_track_quat("-Z","Y").to_euler()
source=OUT/"verdant_library_v02.blend"
bpy.ops.wm.save_as_mainfile(filepath=str(source))

def sheet(filename, names, columns=4, spacing=5.5):
    # Render a family at a common world scale; hide the catalogue elsewhere.
    previous={}
    for col in groups.values(): col.hide_render=True
    rows=math.ceil(len(names)/columns)
    right=camera.rotation_euler.to_matrix() @ Vector((1,0,0))
    up_ground=Vector((-right.y,right.x,0))
    for i,name in enumerate(names):
        col=groups[name]; col.hide_render=False
        target=right*((i%columns-(columns-1)/2)*spacing)+up_ground*((i//columns-(rows-1)/2)*spacing)
        record=next(r for r in inventory if r["id"]==name)
        catalogue_i=inventory.index(record)
        offset=Vector(((catalogue_i%12)*9,(catalogue_i//12)*9,0))
        previous[name]=target-offset
        for obj in col.objects: obj.location+=previous[name]
    scene.render.resolution_x=1800
    scene.render.resolution_y=max(700,int(1800*rows/columns*0.72))
    scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    inv=camera.rotation_euler.to_matrix().transposed()
    points=[inv @ (obj.matrix_world @ v.co) for name in names for obj in groups[name].objects if obj.type=="MESH" for v in obj.data.vertices]
    lo=[min(p[i] for p in points) for i in range(3)]
    hi=[max(p[i] for p in points) for i in range(3)]
    aspect=scene.render.resolution_x/scene.render.resolution_y
    camera.data.ortho_scale=max(hi[0]-lo[0],(hi[1]-lo[1])*aspect)*1.12
    camera.location=camera.rotation_euler.to_matrix() @ Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,hi[2]+30))
    scene.render.filepath=str(RENDER/filename)
    bpy.ops.render.render(write_still=True)
    for name,delta in previous.items():
        for obj in groups[name].objects: obj.location-=delta

sheet("residence_ladder.png",list(res_names.values()),4,6.2)
sheet("industry_and_civic.png",[mapping[k] for k in ("mineral_washery","ceramic_kiln","composite_workshop","waste_digester","first_nursery","general_store","survey_organ","memory_circle","sediment_dredge","filter_crown","anoxic_pump","nutrient_kitchen")],4,5.3)
sheet("cultivation_and_carriers.png",[mapping[k] for k in ("photosynthetic_field","fibre_garden","resin_grove","pigment_bed")]+["unit_"+k+"_carrier_a" for k in ("general","burrowing","filter","vascular")],4,5)
sheet("ecology_variants.png",[f"plant_current_meadow_{i:02d}" for i in range(1,7)],3,3.5)
sheet("memory_reef_growth.png",[f"great_work_memory_reef_stage_{i}" for i in range(4)],4,8)
sheet("resource_depletion.png",[f"patch_{family}_{stage}_a" for family in ("silicate","carbonate") for stage in ("rich","worked","depleted")],3,5)
print(f"VERDANT LIBRARY: {len(inventory)} assets, {sum(r['triangles'] for r in inventory)} total triangles")
