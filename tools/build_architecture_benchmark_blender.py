"""Ten deliberately different architectural massings; no gameplay mapping changes.

blender -b -t 4 --python tools/build_architecture_benchmark_blender.py
Source and Y-up runtime candidates remain separate from accepted production art.
"""
import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/architecture_v03"
RENDER = ROOT / "docs/art/renders/architecture_v03"
OUT.mkdir(parents=True, exist_ok=True)
RENDER.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version = 0
palette = {"shell":"174B50", "chalk":"D9D5BE", "amber":"FFC05A",
           "membrane":"C3EDC2", "growth":"75B96B", "dark":"173331",
           "silica":"8CE0DE", "silt":"615D4E", "memory":"77729C"}
mats = {}
for key, value in palette.items():
    rgb = [int(value[i:i+2], 16)/255 for i in (0,2,4)]
    linear = [v/12.92 if v <= .04045 else ((v+.055)/1.055)**2.4 for v in rgb]
    m = bpy.data.materials.new(key)
    m.diffuse_color = (*linear, 1)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = m.diffuse_color
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = .55
    mats[key] = m
clay = bpy.data.materials.new("silhouette_clay")
clay.diffuse_color = (.32,.35,.34,1)
groups = {}
inventory = []


def group(name):
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    groups[name] = col
    return col


def mesh(col, name, verts, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.materials.append(mats[mat])
    data.update()
    for p in data.polygons: p.use_smooth = True
    obj = bpy.data.objects.new(name, data)
    col.objects.link(obj)
    return obj


def ball(col, name, p, size, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=12, location=p)
    obj = bpy.context.object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for c in list(obj.users_collection): c.objects.unlink(obj)
    col.objects.link(obj)
    obj.data.materials.append(mats[mat])
    for face in obj.data.polygons: face.use_smooth = True
    return obj


def tube(col, name, points, radius, mat):
    verts, faces = [], []
    for i, p in enumerate(points):
        tangent = (Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized()
        axis = Vector((0,0,1)) if abs(tangent.z)<.9 else Vector((0,1,0))
        u = tangent.cross(axis).normalized(); v = tangent.cross(u).normalized()
        for j in range(8):
            a=j*math.tau/8
            verts.append(Vector(p)+radius*(math.cos(a)*u+math.sin(a)*v))
    for i in range(len(points)-1):
        for j in range(8): faces.append((i*8+j,i*8+(j+1)%8,(i+1)*8+(j+1)%8,(i+1)*8+j))
    faces += [tuple(reversed(range(8))), tuple((len(points)-1)*8+j for j in range(8))]
    return mesh(col,name,verts,faces,mat)


def vault(col, name, p, width, length, height, mat="shell", ribs=0):
    """Open-ended elongated protective shell, not a dome on a pedestal."""
    verts, faces = [], []
    for k in range(13):
        t=k/12; y=p[1]+(t-.5)*length
        taper=.76+.24*math.sin(math.pi*t)
        for j in range(17):
            a=j*math.pi/16
            verts.append((p[0]+width*math.cos(a)*taper,y,p[2]+height*math.sin(a)*taper))
    for k in range(12):
        for j in range(16): faces.append((k*17+j,(k+1)*17+j,(k+1)*17+j+1,k*17+j+1))
    shell=mesh(col,name,verts,faces,mat)
    mod=shell.modifiers.new("grown shell thickness","SOLIDIFY"); mod.thickness=.09
    bpy.context.view_layer.objects.active=shell
    bpy.ops.object.modifier_apply(modifier=mod.name)
    for k in range(ribs):
        t=(k+1)/(ribs+1); taper=.76+.24*math.sin(math.pi*t)
        pts=[(p[0]+width*math.cos(j*math.pi/20)*taper,p[1]+(t-.5)*length,p[2]+height*math.sin(j*math.pi/20)*taper+.025) for j in range(21)]
        tube(col,"structural shell rib",pts,.045,"chalk")
    # Recessed occupied tissue: visible through the open vestibule, not an Earth door.
    ball(col,"occupied chamber",(p[0],p[1]+length*.27,p[2]+height*.33),(width*.64,length*.16,height*.3),"amber")


def basin(col, name, p, rx, ry, depth, fill):
    verts, faces=[],[]
    rings=((.68,0),(1,depth),(.88,depth),(.48,.12*depth))
    for r,z in rings:
        for j in range(32):
            a=j*math.tau/32
            verts.append((p[0]+rx*r*math.cos(a),p[1]+ry*r*math.sin(a),p[2]+z))
    for k in range(3):
        for j in range(32): faces.append((k*32+j,k*32+(j+1)%32,(k+1)*32+(j+1)%32,(k+1)*32+j))
    mesh(col,name,verts,faces,"chalk")
    ball(col,"retained contents",(p[0],p[1],p[2]+depth*.18),(rx*.65,ry*.65,.08),fill)


def foot(col,x,y,height=.3):
    ball(col,"local substrate grip",(x,y,height*.35),(.26,.42,height),"chalk")


def plate(col,name,p,width,length,rise,mat="shell"):
    """Broad asymmetrical shell ledge; unlike the early barrel-vault anatomy."""
    verts=[];faces=[]
    for i in range(13):
        t=i/12
        for j in range(13):
            u=j/12
            x=(u-.5)*width
            y=(t-.5)*length+.12*math.sin(u*math.tau)
            z=rise*(.3+math.sin(math.pi*u)*.7)*(1-.7*t)+.07*math.sin(u*math.tau*2)
            verts.append((p[0]+x,p[1]+y,p[2]+z))
    for i in range(12):
        for j in range(12): faces.append((i*13+j,i*13+j+1,(i+1)*13+j+1,(i+1)*13+j))
    obj=mesh(col,name,verts,faces,mat)
    mod=obj.modifiers.new("load-bearing shell plate","SOLIDIFY");mod.thickness=.15
    bpy.context.view_layer.objects.active=obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    tube(col,"thickened plate edge",[verts[j] for j in range(13)],.075,"chalk")


def ports(col, extent, waste_in=False):
    # All sockets are oriented toward unobstructed local approach zones.
    for x,mat,name in ((-extent,"silica","clean-flow inlet"),(extent,"silt","contained waste inlet" if waste_in else "contained waste outlet")):
        tube(col,name,[(x*.35,.35,.22),(x*.7,.65,.23),(x,.9,.25),(x,1.2,.32),(x,1.48,.28)],.105,mat)
        ball(col,"dormant utility socket",(x,1.5,.28),(.13,.04,.13),"dark")
    tube(col,"carrier vestibule",[(0,-1.1,.28),(0,-1.55,.22)],.22,"shell")


names=["01_seed_shelter","02_rooted_dwelling","03_mature_habitat","04_symbiotic_court","05_terraced_habitat","06_memory_manor","07_general_store","08_mineral_washery","09_ceramic_kiln","10_waste_digester"]
for tier,name in enumerate(names[:6],1):
    col=group(name)
    # The seed chamber remains on the front left of every evolved form.
    vault(col,"ancestral seed chamber",(-.65,-.5,.06),.68,1.5,.75,ribs=0 if tier==1 else 2)
    if tier==1:
        tube(col,"exposed anchoring tissue",[(-1.1,.1,.15),(-1.4,.4,.06),(-1.2,.9,.02)],.06,"growth")
    if tier==2:
        vault(col,"long brood mantle",(.3,.45,.08),.95,2.9,1.25,ribs=5)
        foot(col,1.0,.9);foot(col,-.4,1.1)
    if tier==3:
        vault(col,"circulation spine",(.0,.6,.08),.75,2.4,2.1,ribs=4)
        vault(col,"productive side chamber",(1,-.05,.08),.6,1.7,1.2,ribs=3)
        vault(col,"rear brood chamber",(-1.0,1,.08),.58,1.5,1.1,ribs=3)
    if tier==4:
        for x in (-1.4,1.4): vault(col,"court side wing",(x,.65,.08),.53,3.0,1.8,ribs=4)
        vault(col,"rear shared chamber",(0,1.8,.08),1.4,1,1.55,ribs=2)
        basin(col,"cultivated communal court",(0,.35,.06),.75,1.0,.25,"growth")
        tube(col,"court bridge arch",[(-1.3,.4,1.45),(-.8,.4,2.25),(0,.4,2.5),(.8,.4,2.25),(1.3,.4,1.45)],.12,"chalk")
        plate(col,"suspended cultivated court membrane",(0,.45,2.0),2.3,1.45,.35,"membrane")
    if tier>=5:
        for x,y,h in ((-1.1,.8,1.0),(.6,1.0,1.25),(1.1,-.1,.8)):
            ball(col,"enclosed lower living chamber",(x,y,h*.65),(.65,.9,h),"shell")
        plate(col,"broad collective shell terrace",(.0,.7,1.1),3.7,3.5,.65)
        vault(col,"upper inhabited gallery",(-.45,.8,1.35),.75,2.3,1.15,ribs=2)
        plate(col,"upper overlapping shell terrace",(-.35,.9,2.3),2.65,2.55,.5)
        for x in (-1.5,1.4):
            foot(col,x,1.1,.55)
            basin(col,"living terrace",(x,-.2,1.1),.48,.8,.23,"growth")
        tube(col,"vertical circulation organ",[(1.1,1.2,.2),(1.0,1.25,1.25),(.55,1.2,2.1)],.24,"membrane")
    if tier==6:
        ball(col,"protected collective archive",(-.55,1.0,2.75),(.55,.65,.8),"memory")
        for k in range(5):
            x=-1.15+k*.3
            tube(col,"archive load-bearing fan rib",[(x,1.55,2.3),(x,1.45,3.2),(x+.2,.8,4.15-.16*abs(k-2)),(x+.35,.15,3.65)],.085,"chalk")
        plate(col,"archive crown shielding",(-.35,1.05,3.25),1.8,1.7,.75,"chalk")
        vault(col,"cultural side gallery",(1.65,.45,.1),.48,2.5,1.9,ribs=3)
        for z in (2.7,3.0,3.3):
            tube(col,"encoded archive band",[(-1.03,.4,z),(-.55,.35,z+.1),(-.13,.4,z)],.045,"memory")
    ports(col,.65 if tier==1 else 1.3)

col=group(names[6])
# Store: low open galleries, physically divided goods bays beneath one shell.
vault(col,"asymmetric storage canopy",(0,.5,.7),1.9,3.1,1.1,ribs=4)
for x in (-1.1,0,1.1):
    foot(col,x,1.1,.8)
    for y in (-.6,.65):
        basin(col,"separate retained goods bay",(x,y,.12),.46,.5,.35,"silica" if x<0 else "chalk" if x>0 else "growth")
for x in (-1.1,1.1): tube(col,"wide loading mouth",[(x,-.8,.25),(x,-1.6,.2)],.28,"shell")

col=group(names[7])
# Washery: gravity/process head, descending basins and separate grit rejection.
for i in range(3):
    x=-1.35+i*1.3;z=1.65-i*.63
    foot(col,x,.1,z)
    basin(col,"separation basin %d"%i,(x,0,z),.73,.8,.46,"silt" if i==0 else "silica")
    if i<2: tube(col,"descending screened transfer",[(x+.5,0,z+.23),(x+.8,0,z+.12),(x+1.0,0,z-.38)],.16,"shell")
vault(col,"raw feed head",(-1.35,.55,1.95),.48,1.3,.8,"chalk",3)
tube(col,"enclosed raw-feed lifting duct",[(-1.7,-1.3,.25),(-1.9,-.7,.8),(-1.8,-.25,1.9),(-1.35,-.1,2.15)],.18,"shell")
basin(col,"rejected grit recess",(-.8,-1.15,.08),.65,.38,.25,"silt")
ports(col,1.6)

col=group(names[8])
# Kiln: enclosed heavy conversion core with feeding throat and cooling comb.
vault(col,"insulated thermal mantle",(-.35,.3,.08),1.3,2.5,2.7,"chalk",5)
ball(col,"sealed thermal conversion chamber",(-.35,.5,1.15),(.87,.65,1.2),"shell")
vault(col,"low fuel and silica throat",(-.4,-1.0,.1),.55,1.4,.6,"shell",2)
ball(col,"internal metabolic heat",(-.35,-.55,.6),(.4,.12,.3),"amber")
for i in range(6):
    x=.85+i*.2
    tube(col,"product cooling comb",[(x,-.7,.15),(x,-.2,.8),(x,.6,.75)],.07,"chalk")
for i in range(4):
    tube(col,"thermal exchange gill",[(-.8+i*.3,.7,2.1),(-.85+i*.3,.85,2.8),(-.8+i*.3,1.1,2.5)],.09,"shell")
foot(col,-1.3,.8,.45);foot(col,.7,1.0,.5)
ports(col,1.5)

col=group(names[9])
# Digester: sealed pressure lobes, intake containment, two unlike product organs.
for p,size in (((-.6,.5,1.25),(.95,1.2,1.45)),((.75,.8,.85),(.7,.9,1.0))):
    ball(col,"sealed fermentation lobe",p,size,"shell")
ball(col,"buried containment belly",(-.1,.3,.3),(1.35,1.1,.42),"silt")
for i in range(4):
    y=-.1+i*.35
    tube(col,"digester tension seam",[(-1.35,y,.4),(-1.2,y,1.5),(-.6,y,2.55),(.0,y,1.5),(.15,y,.45)],.045,"chalk")
tube(col,"contained digestion neck",[(-.4,.5,1),(.3,.65,1),(.8,.8,.8)],.3,"membrane")
vault(col,"sealed solid-waste intake",(-.75,-.9,.02),.65,1.3,.7,"shell",3)
basin(col,"small enzyme reservoir",(1.25,-.55,.1),.32,.4,.55,"amber")
basin(col,"broad fertiliser collection",(.0,-1.0,.05),.55,.6,.25,"growth")
for x,y in ((-.95,.9),(.9,1.2),(-.8,-.5)): foot(col,x,y,.4)
ports(col,1.55,True)

for name,col in groups.items():
    bpy.ops.object.select_all(action="DESELECT")
    for obj in col.objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=list(col.objects)[0]
    path=OUT/(name+".obj")
    bpy.ops.wm.obj_export(filepath=str(path),export_selected_objects=True,export_triangulated_mesh=True,forward_axis="NEGATIVE_Z",up_axis="Y")
    mtl=path.with_suffix(".mtl");current="";lines=[]
    for line in mtl.read_text().splitlines():
        if line.startswith("newmtl "): current=line.split(maxsplit=1)[1]
        if line.startswith("Kd ") and current in palette:
            line="Kd "+" ".join(str(int(palette[current][i:i+2],16)/255) for i in (0,2,4))
        lines.append(line)
    mtl.write_text("\n".join(lines)+"\n")
    pts=[o.matrix_world@v.co for o in col.objects for v in o.data.vertices]
    height=max(p.z for p in pts)
    anchors={"CarrierInput":[0,.22,1.55],"CarrierOutput":[1.1,.22,1.55],"CleanFlowIn":[-1.3,.28,-1.5],"WasteReturnIn" if name==names[9] else "WasteReturnOut":[1.3,.28,-1.5],"LabelAnchor":[0,height+.3,0]}
    if name==names[0]: anchors.update({"CleanFlowIn":[-.65,.28,-1.5],"WasteReturnOut":[.65,.28,-1.5]})
    if name==names[6]:
        anchors={"CarrierInput":[-1.1,.2,1.6],"CarrierOutput":[1.1,.2,1.6],"LabelAnchor":[0,height+.3,0]}
    if name in names[7:]:
        extent=1.6 if name==names[7] else 1.5 if name==names[8] else 1.55
        anchors["CleanFlowIn"]=[-extent,.28,-1.5]
        anchors["WasteReturnIn" if name==names[9] else "WasteReturnOut"]=[extent,.28,-1.5]
    if name==names[7]: anchors.update({"CarrierInput":[-1.7,.25,1.3],"CarrierOutput":[1.25,.5,.65]})
    if name==names[8]: anchors.update({"CarrierInput":[-.4,.22,1.7],"CarrierOutput":[1.4,.3,.75]})
    if name==names[9]: anchors.update({"CarrierInput":[-.75,.22,1.55],"CarrierOutput":[1.25,.35,.9]})
    (OUT/(name+".anchors.json")).write_text(json.dumps({"asset":name,"up_axis":"+Y","units":"metres","status":"visual_candidate","anchors":anchors},indent=2)+"\n")
    inventory.append({"id":name,"path":str(path.relative_to(ROOT)),"triangles":sum(len(f.vertices)-2 for o in col.objects for f in o.data.polygons),"height":height,"status":"massing_candidate"})
(OUT/"manifest.json").write_text(json.dumps({"version":3,"assets":inventory,"gameplay_bound":False},indent=2)+"\n")

scene=bpy.context.scene
scene.render.engine="CYCLES";scene.cycles.samples=20
scene.world.color=(.22,.22,.22)
scene.view_settings.view_transform="AgX"
bpy.ops.object.light_add(type="AREA",location=(0,-8,15))
light=bpy.context.object;light.data.energy=2300;light.data.size=12
bpy.ops.object.camera_add(location=(8,-14,16))
camera=bpy.context.object;camera.data.type="ORTHO";scene.camera=camera
camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat("-Z","Y").to_euler()
right=camera.rotation_euler.to_matrix()@Vector((1,0,0))
back=Vector((-right.y,right.x,0))


def sheet(filename, selection, columns, monochrome=False):
    offsets={}; rows=math.ceil(len(selection)/columns)
    for col in groups.values():col.hide_render=True
    for i,name in enumerate(selection):
        col=groups[name];col.hide_render=False
        offset=right*((i%columns-(columns-1)/2)*5.5)+back*((i//columns-(rows-1)/2)*6)
        offsets[name]=offset
        for obj in col.objects:obj.location+=offset
    scene.view_layers[0].material_override=clay if monochrome else None
    scene.render.resolution_x=1800;scene.render.resolution_y=1050 if rows>1 else 700
    scene.render.resolution_percentage=100
    bpy.context.view_layer.update()
    inv=camera.rotation_euler.to_matrix().transposed()
    pts=[inv@(o.matrix_world@v.co) for name in selection for o in groups[name].objects for v in o.data.vertices]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    camera.data.ortho_scale=max(hi[0]-lo[0],(hi[1]-lo[1])*scene.render.resolution_x/scene.render.resolution_y)*1.12
    camera.location=camera.rotation_euler.to_matrix()@Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,hi[2]+30))
    scene.render.filepath=str(RENDER/filename)
    bpy.ops.render.render(write_still=True)
    for name,offset in offsets.items():
        for obj in groups[name].objects:obj.location-=offset

sheet("housing_massing.png",names[:6],3,True)
sheet("industry_massing.png",names[6:],4,True)
sheet("housing_materials.png",names[:6],3)
sheet("industry_materials.png",names[6:],4)
scene.view_layers[0].material_override=None
for i,col in enumerate(groups.values()):
    col.hide_render=False
    for obj in col.objects:obj.location+=Vector(((i%5)*6,(i//5)*7,0))
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"architecture_benchmark_v03.blend"))
print("ARCHITECTURE BENCHMARK: ten massing candidates exported; gameplay unchanged")
