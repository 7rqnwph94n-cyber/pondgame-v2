"""Concept-led Verdant architecture, textured glTF plus editable Blender source.

Run with Blender -b -t 4 --python tools/build_architecture_refined_blender.py.
Only art output is generated. No economy values or playable mappings are written.
"""
import json
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets/architecture_v04"
RENDER = ROOT / "docs/art/renders/architecture_v04"
for folder in (OUT, OUT/"textures", RENDER): folder.mkdir(parents=True, exist_ok=True)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
random.seed(41)
PALETTE={"shell":"174B50","chalk":"C5C3A6","resin":"B4914C","amber":"EEB34D",
         "membrane":"AAD8C3","silica":"8CC9CB","growth":"6B9C57","silt":"615D4E",
         "dark":"253B37","ceramic":"B7AE91","memory":"77729C","fibre":"859367"}
MATS={};COLS={};ROOTS={};RECORDS=[];STATE={};PHASES={}


def material(key,hexcol):
    rgb=[int(hexcol[i:i+2],16)/255 for i in (0,2,4)]
    image=bpy.data.images.new(key+"_surface",width=256,height=256,alpha=True)
    pixels=[]
    for y in range(256):
        for x in range(256):
            grain=math.sin(x*1.71+y*2.13)*math.sin(x*.37-y*.81)
            growth=math.sin(y*.11+2*math.sin(x*.021))
            fine=math.sin(x*.071+y*.12)*math.sin(x*.14-y*.03)
            variation=1+.014*grain+.025*fine+.022*growth
            if key=="chalk":variation-=.13*max(0,grain-.5)
            pixels.extend([max(0,min(1,c*variation)) for c in rgb]+[1])
    image.pixels.foreach_set(pixels)
    image.filepath_raw=str(OUT/"textures"/(key+"_surface.png"));image.file_format="PNG";image.save()
    normal=bpy.data.images.new(key+"_micro_normal",width=256,height=256,alpha=True)
    normal.colorspace_settings.name="Non-Color"
    pixels=[]
    strength=.009 if key=="shell" else .025 if key in ("chalk","ceramic") else .008
    for y in range(256):
        for x in range(256):
            pixels.extend([.5+strength*math.sin(x*.22+y*.31),.5+strength*math.cos(x*.27-y*.19),1,1])
    normal.pixels.foreach_set(pixels)
    normal.filepath_raw=str(OUT/"textures"/(key+"_normal.png"));normal.file_format="PNG";normal.save()
    m=bpy.data.materials.new("verdant_"+key);m.use_nodes=True
    shader=m.node_tree.nodes["Principled BSDF"]
    shader.inputs["Roughness"].default_value={"shell":.46,"resin":.4,"silica":.28,"amber":.45,"chalk":.82}.get(key,.6)
    shader.inputs["Metallic"].default_value=0
    shader.inputs["Coat Weight"].default_value=.06 if key=="shell" else 0
    texture=m.node_tree.nodes.new("ShaderNodeTexImage");texture.image=image
    m.node_tree.links.new(texture.outputs["Color"],shader.inputs["Base Color"])
    texture=m.node_tree.nodes.new("ShaderNodeTexImage");texture.image=normal
    nm=m.node_tree.nodes.new("ShaderNodeNormalMap")
    m.node_tree.links.new(texture.outputs["Color"],nm.inputs["Color"])
    m.node_tree.links.new(nm.outputs["Normal"],shader.inputs["Normal"])
    if key=="amber":
        shader.inputs["Emission Color"].default_value=(.42,.16,.025,1)
        shader.inputs["Emission Strength"].default_value=.15
    MATS[key]=m
for key,value in PALETTE.items():material(key,value)


def group(name):
    col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col);COLS[name]=col
    root=bpy.data.objects.new(name,None);col.objects.link(root);ROOTS[name]=root
    STATE[name]={};PHASES[name]={}
    return col


def parent(col,obj,state="Structure"):
    if state not in STATE[col.name]:
        root=bpy.data.objects.new(state,None);col.objects.link(root);root.parent=ROOTS[col.name]
        STATE[col.name][state]=root
    target=STATE[col.name][state]
    if state=="Structure":
        mat=obj.data.materials[0].name.removeprefix("verdant_") if obj.data.materials else "shell"
        phase="GrowthFrame" if mat in ("chalk","resin","silt") else "GrowthSoft" if mat in ("membrane","growth","fibre") else "GrowthShell"
        if phase not in PHASES[col.name]:
            node=bpy.data.objects.new(phase,None);col.objects.link(node);node.parent=target;PHASES[col.name][phase]=node
        target=PHASES[col.name][phase]
    obj.parent=target


def mesh(col,name,vertices,faces,mat,state="Structure",smooth=True):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.materials.append(MATS[mat]);data.update()
    uv=data.uv_layers.new(name="SurfaceUV")
    for face in data.polygons:
        face.use_smooth=smooth
        n=face.normal;axis=max(range(3),key=lambda i:abs(n[i]));dims=[i for i in range(3) if i!=axis]
        for li in face.loop_indices:
            p=data.vertices[data.loops[li].vertex_index].co
            uv.data[li].uv=(p[dims[0]]*.65,p[dims[1]]*.65)
    obj=bpy.data.objects.new(name,data);col.objects.link(obj);parent(col,obj,state)
    return obj


def ball(col,name,p,size,mat,state="Structure",segments=20):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments,ring_count=12,location=p)
    o=bpy.context.object;o.name=name;o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for c in list(o.users_collection):c.objects.unlink(o)
    col.objects.link(o);o.data.materials.append(MATS[mat]);parent(col,o,state)
    for face in o.data.polygons:face.use_smooth=True
    return o


def tube(col,name,points,radius,mat="chalk",state="Structure",sides=6):
    vertices=[];faces=[]
    previous_u=None
    closed=(Vector(points[0])-Vector(points[-1])).length<.00001
    for i,p in enumerate(points):
        tangent=(Vector(points[1])-Vector(points[-2])).normalized() if closed and i in (0,len(points)-1) else (Vector(points[min(i+1,len(points)-1)])-Vector(points[max(0,i-1)])).normalized()
        axis=Vector((0,0,1)) if abs(tangent.z)<.9 else Vector((0,1,0))
        u=previous_u-tangent*previous_u.dot(tangent) if previous_u is not None else tangent.cross(axis)
        if u.length_squared<.00001:u=tangent.cross(axis)
        u.normalize();v=tangent.cross(u).normalized();previous_u=u
        taper=1 if closed else 1-.12*i/max(1,len(points)-1)
        section_radius=radius[i] if isinstance(radius,(list,tuple)) else radius
        for j in range(sides):
            a=j*math.tau/sides;vertices.append(Vector(p)+section_radius*taper*(math.cos(a)*u+math.sin(a)*v))
    for i in range(len(points)-1):
        for j in range(sides):faces.append((i*sides+j,i*sides+(j+1)%sides,(i+1)*sides+(j+1)%sides,(i+1)*sides+j))
    faces += [tuple(reversed(range(sides))),tuple((len(points)-1)*sides+j for j in range(sides))]
    return mesh(col,name,vertices,faces,mat,state)


def arc(col,name,p,rx,ry,z,mat="chalk",r=.055,start=0,end=math.tau,state="Structure"):
    pts=[(p[0]+rx*math.cos(a),p[1]+ry*math.sin(a),p[2]+z) for a in [start+(end-start)*i/32 for i in range(33)]]
    return tube(col,name,pts,r,mat,state)


def organ(col,p,size,seed=0,kind="home"):
    """Closed shell with three warm protected apertures and nonuniform growth seams."""
    prior={o for o in col.objects}
    rx,ry,h=size
    def point(a,t,scale=1):
        s=math.sin(t);w=1
        return (p[0]+rx*s*math.cos(a)*scale*w,p[1]+ry*s*math.sin(a)*scale,p[2]+h*math.cos(t)*scale)
    verts=[];faces=[];n=48;rings=32
    holes=[(-math.pi/2-.57,1.65,.36,.48),(-math.pi/2+.52,1.37,.20,.31),(math.pi/2+.17,1.65,.27,.35)]
    if kind=="kiln":holes=[(-math.pi/2,1.85,.40,.48)]
    if kind=="store":holes=[]
    for k in range(rings+1):
        t=.015+(math.pi-.03)*k/rings
        for j in range(n):verts.append(point(j*math.tau/n,t))
    for k in range(rings):
        t=.015+(math.pi-.03)*(k+.5)/rings
        for j in range(n):
            a=(j+.5)*math.tau/n
            faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    o=mesh(col,"closed protective carapace",verts,faces,"ceramic" if kind=="kiln" else "shell")
    mod=o.modifiers.new("shell thickness","SOLIDIFY");mod.thickness=.045
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    ball(col,"inner enclosed habitation",p,(rx*.84,ry*.84,h*.86),"dark")
    for ha,ht,wa,wt in holes:
        surface=Vector(point(ha,ht))
        normal=Vector((math.cos(ha)*math.sin(ht)/rx,math.sin(ha)*math.sin(ht)/ry,math.cos(ht)/h)).normalized()
        u=normal.cross(Vector((0,0,1))).normalized();v=normal.cross(u).normalized()
        width=wa*min(rx,ry)*.94;depth=wt*h*.93
        bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=1,depth=1,location=surface)
        cutter=bpy.context.object;cutter.name="temporary aperture cutter"
        cutter.rotation_euler=normal.to_track_quat("Z","Y").to_euler();cutter.scale=(width,depth,max(rx,ry,h)*.75)
        mod=o.modifiers.new("smooth protected opening","BOOLEAN");mod.operation="DIFFERENCE";mod.solver="EXACT";mod.object=cutter
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
        pts=[]
        for j in range(41):
            a=j*math.tau/40
            q=surface+u*width*math.cos(a)+v*depth*math.sin(a)
            rel=q-Vector(p);radii=(rx,ry,h)
            aa=sum((normal[i]/radii[i])**2 for i in range(3))
            bb=2*sum(rel[i]*normal[i]/radii[i]**2 for i in range(3))
            cc=sum((rel[i]/radii[i])**2 for i in range(3))-1
            distance=(-bb+math.sqrt(max(0,bb*bb-4*aa*cc)))/(2*aa)
            pts.append(q+normal*(distance+.015))
        tube(col,"continuous grown aperture rim",pts,.040,"resin",sides=8)
        # Protective mineral brow grows around the principal aperture, not two
        # identical eye-like discs attached to every chamber.
        if ha==holes[0][0]:
            brow=[Vector(pts[j])+normal*.025+Vector((0,0,.035)) for j in range(2,19)]
            tube(col,"grown protective aperture brow",brow,[.04+.06*math.sin(math.pi*i/16) for i in range(17)],"chalk",sides=8)
        # A closed dormant pore has a real silhouette/state change, not an icon.
        shutter_verts=[surface]+[Vector(q)-normal*.01 for q in pts[:-1]]
        shutter_faces=[(0,j+1,(j+1)%40+1) for j in range(40)]
        mesh(col,"protective pore closure",shutter_verts,shutter_faces,"shell" if kind!="kiln" else "ceramic","Dormancy")
        q=surface-normal*.075
        window=ball(col,"recessed amber organ",q,(width*.82,depth*.80,.035),"amber","Activity",20)
        window.rotation_euler=normal.to_track_quat("Z","Y").to_euler()
    for a in (-2.9,-1.76,-.60,.55,1.5):
        tube(col,"asymmetric carapace seam",[point(a+.07*math.sin(t*3),t,1.018) for t in [.12+i*2.8/24 for i in range(25)]],.022,"resin")
    for a in (-2.80,-.30):
        tube(col,"protective carbonate shoulder",[point(a+.12*math.sin(t*2),t,1.025) for t in [.28+i*1.75/20 for i in range(21)]],
             [.04+.035*math.sin(math.pi*i/20) for i in range(21)],"chalk",sides=10)
    # Low organic buttresses, not a shared foundation ring.
    for a in (-3.0,-.25,.85,1.85,2.55):
        points=[point(a,1.55),point(a,1.9,1.07),
                (p[0]+rx*math.cos(a)*1.16,p[1]+ry*math.sin(a)*1.16,p[2]-h*.62),
                (p[0]+rx*math.cos(a)*1.30,p[1]+ry*math.sin(a)*1.27,max(.04,p[2]-h*.93))]
        tube(col,"grown flared load-bearing root",points,[.075,.09,.115,.15],"chalk",sides=10)
        end=Vector(points[-1]);tip=end+Vector((.18*math.cos(a+.7),.18*math.sin(a+.7),-.015))
        tube(col,"forked substrate root",[points[-2],end,tip],[.085,.09,.025],"chalk",sides=8)
    # A coherent grown mantle, not perfect spheres plus ornaments. Warp shell,
    # carved openings, rims and enclosed organs together so they remain fitted.
    bpy.context.view_layer.update()
    for obj in [o for o in col.objects if o not in prior and o.type=="MESH"]:
        world=obj.matrix_world.copy();inverse=world.inverted()
        for vertex in obj.data.vertices:
            q=world@vertex.co;rel=q-Vector(p);z=max(-1,min(1,rel.z/h))
            a=math.atan2(rel.y/ry,rel.x/rx)
            mantle=1+.055*math.sin(a*3+seed*.61)*(1-z*z)
            taper=1.035-.17*z
            x=rel.x*taper*mantle+.13*rx*(z+1)*.5*math.sin(seed*.75)
            y=rel.y*taper*mantle+.14*ry*z+.065*ry*z*z
            crown=q.z+.07*h*math.sin(a*2+seed*.4)*(1-z*z)
            vertex.co=inverse@Vector((p[0]+x,p[1]+y,crown))
        obj.data.update()


def lattice(col,p,rx,ry,height,levels=2,seed=0):
    """Offset cellular support web; pores are actual geometry, not dark decals."""
    rng=random.Random(seed);nodes=[];count=11
    for k in range(levels+1):
        row=[]
        for j in range(count):
            a=j*math.tau/count+.17*(k%2)
            row.append((p[0]+rx*math.cos(a)*(1-.06*k),p[1]+ry*math.sin(a)*(1-.06*k),p[2]+height*k/levels+.04*rng.random()))
        nodes.append(row)
    for k in range(levels):
        for j in range(count):
            corners=[Vector(nodes[k][j]),Vector(nodes[k][(j+1)%count]),Vector(nodes[k+1][(j+1)%count]),Vector(nodes[k+1][j])]
            def bilinear(u,v):
                return corners[0]*(1-u)*(1-v)+corners[1]*u*(1-v)+corners[2]*u*v+corners[3]*(1-u)*v
            outer=[(0,0),(.5,0),(1,0),(1,.5),(1,1),(.5,1),(0,1),(0,.5)]
            inner=[]
            for u,v in outer:
                a=math.atan2(v-.5,u-.5)
                width=.25+.04*rng.random();depth=.27+.045*rng.random()
                inner.append((.5+width*math.cos(a),.5+depth*math.sin(a)))
            vertices=[bilinear(u,v) for u,v in outer+inner]
            faces=[(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
            o=mesh(col,"perforated carbonate support tissue",vertices,faces,"chalk")
            mod=o.modifiers.new("porous load-bearing thickness","SOLIDIFY");mod.thickness=.13
            bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
            bevel=o.modifiers.new("rounded living pore edges","BEVEL");bevel.width=.025;bevel.segments=2
            bpy.ops.object.modifier_apply(modifier=bevel.name)
    for k in range(levels+1):
        tube(col,"structural web chord",nodes[k]+[nodes[k][0]],.075,sides=8)


def cup(col,p,rx,ry,height,mat="chalk",state="Structure"):
    verts=[];faces=[];n=32
    for r,z in ((.60,0),(.93,height*.65),(1,height),(.88,height-.05),(.46,height*.22)):
        for j in range(n):
            a=j*math.tau/n;w=1+.025*math.sin(a*3)
            verts.append((p[0]+rx*r*math.cos(a)*w,p[1]+ry*r*math.sin(a),p[2]+z))
    for k in range(4):
        for j in range(n):faces.append((k*n+j,k*n+(j+1)%n,(k+1)*n+(j+1)%n,(k+1)*n+j))
    mesh(col,"retaining process chamber",verts,faces,mat,state)
    arc(col,"thick chamber rim",p,rx,ry,height,"resin",.025,state=state)


def goods(col,p,kind,count=15,state="CargoOutput",spread=(.45,.45),seed=1):
    if state in ("CargoInput","CargoOutput"):
        resource={"raw":"raw_silicate","silica":"prepared_silica","food":"staple","carbonate":"carbonate","ceramic":"fired_ceramic","fertiliser":"recovered_fertiliser","waste":"organic_waste"}[kind]
        state += "__"+resource
    rng=random.Random(seed)
    for i in range(count):
        a=rng.random()*math.tau;r=math.sqrt(rng.random())
        q=(p[0]+math.cos(a)*r*spread[0],p[1]+math.sin(a)*r*spread[1],p[2]+rng.random()*.13)
        if kind=="raw":
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.13,location=q)
            o=bpy.context.object;o.scale=(1.2,.7,1+rng.random());o.name="raw silicate fragment"
            for c in list(o.users_collection):c.objects.unlink(o)
            col.objects.link(o);o.data.materials.append(MATS["silt"]);parent(col,o,state)
        elif kind=="silica":ball(col,"prepared silica granule",q,(.095,.08,.09),"silica",state,12)
        elif kind=="food":ball(col,"retained nutrient disc",q,(.12,.095,.025),"growth",state,12)
        elif kind=="ceramic":
            cup(col,q,.12,.12,.10,"ceramic",state)
        elif kind=="fertiliser":ball(col,"recovered fertiliser granule",q,(.06,.05,.065),"silt",state,12)
        elif kind=="waste":ball(col,"contained organic waste",q,(.12,.10,.085),"dark",state,12)
        else:ball(col,"stored carbonate nodule",q,(.09,.08,.08),"chalk",state,12)


def leaf(col,p,height,width,angle,mat="growth",seed=0):
    verts=[];faces=[];spine=[]
    for i in range(9):
        t=i/8;w=width*math.sin(math.pi*t)
        c=Vector((p[0]+.3*math.cos(angle)*t*t,p[1]+.3*math.sin(angle)*t*t,p[2]+height*t))
        u=Vector((-math.sin(angle),math.cos(angle),0));spine.append(tuple(c))
        verts += [c-u*w,c+Vector((0,0,.05*math.sin(t*math.pi))),c+u*w]
    for i in range(8):
        for j in range(2):faces.append((i*3+j,(i+1)*3+j,(i+1)*3+j+1,i*3+j+1))
    mesh(col,"cultivated lamina",verts,faces,mat)
    tube(col,"lamina nutrient vein",spine,.015,"resin")


def garden(col,p,rx=.5,ry=.5,count=7,seed=0):
    rng=random.Random(seed)
    # A low branching culture mat grows directly into the host structure. No
    # pottery-like standalone bowl or perfect circular rim around every bed.
    for j in range(5):
        a=j*math.tau/5+.3;r=.3+.12*rng.random()
        q=(p[0]+rx*r*math.cos(a),p[1]+ry*r*math.sin(a),p[2]+.035)
        ball(col,"intergrown cultivation cushion",q,(rx*.55,ry*.54,.085),"growth",segments=12)
        tube(col,"cultivation nutrient root",[q,(p[0]+rx*.8*math.cos(a),p[1]+ry*.8*math.sin(a),p[2]+.03),
             (p[0]+rx*1.10*math.cos(a),p[1]+ry*1.10*math.sin(a),p[2]-.015)],[.035,.025,.012],"fibre")
    for j in range(count):
        a=rng.random()*math.tau;r=.65*math.sqrt(rng.random())
        q=(p[0]+rx*r*math.cos(a),p[1]+ry*r*math.sin(a),p[2]+.08)
        leaf(col,q,.24+rng.random()*.46,.10+rng.random()*.04,a,seed=seed)
        if j%2==0:
            leaf(col,q,.16+rng.random()*.16,.13,a+1.8,"membrane" if j%4==0 else "growth",seed)
        if j%3==0:
            ball(col,"retained cultivation bud",(q[0],q[1],q[2]+.08),(.065,.08,.09),"memory" if seed>=8 else "growth",segments=12)


def canopy(col,points,support_floor=.12):
    # Curved tension membrane, corners physically connected to living supports.
    a,b,c=map(Vector,points);n=10;verts=[];faces=[]
    centre=(a+b+c)/3
    def surface(u,v):
        w=1-u-v;p=a*w+b*u+c*v
        edge=math.sin(math.pi*u)*math.sin(math.pi*v)+math.sin(math.pi*v)*math.sin(math.pi*w)+math.sin(math.pi*w)*math.sin(math.pi*u)
        p+=(centre-p)*(.30*edge)
        p.z-=.38*math.sin(math.pi*u)*math.sin(math.pi*v)*math.sin(math.pi*w)
        return p
    for i in range(n+1):
        for j in range(n+1-i):
            u=i/n;v=j/n;verts.append(surface(u,v))
    row=[];offset=0
    for i in range(n+1):row.append(offset);offset+=n+1-i
    for i in range(n):
        for j in range(n-i):
            faces.append((row[i]+j,row[i+1]+j,row[i]+j+1))
            if j<n-i-1:faces.append((row[i]+j+1,row[i+1]+j,row[i+1]+j+1))
    mesh(col,"tensioned symbiotic membrane",verts,faces,"membrane")
    for edge in ([(i/n,0) for i in range(n+1)],[(1-i/n,i/n) for i in range(n+1)],[(0,1-i/n) for i in range(n+1)]):
        tube(col,"curved membrane tensile edge",[surface(u,v) for u,v in edge],.040,"resin")
    for p in (a,b,c):
        tube(col,"grown branching canopy support",[(p.x,p.y,support_floor),(p.x+.12,p.y+.05,p.z-.5),p],[.16,.10,.045],"chalk",sides=10)
    for t in (.25,.5,.75):
        tube(col,"curved membrane tension vein",[surface(t*(1-k/n),k/n) for k in range(n+1)],.012,"resin")


def terrace(col,p,rx,ry):
    # A living, genuinely perforated support frame beneath a continuous terrace.
    lattice(col,(p[0],p[1],p[2]-.55),rx*.92,ry*.9,.53,2,int(p[2]*10))
    n=48;verts=[(p[0],p[1],p[2])];faces=[]
    for j in range(n):
        a=j*math.tau/n;r=1+.08*math.sin(a*3+.3)+.025*math.sin(a*5)
        verts.append((p[0]+rx*r*math.cos(a),p[1]+ry*r*math.sin(a),p[2]+.04*math.sin(a*4)))
    for j in range(n):faces.append((0,j+1,(j+1)%n+1))
    o=mesh(col,"inhabited shell terrace",verts,faces,"chalk")
    mod=o.modifiers.new("terrace depth","SOLIDIFY");mod.thickness=.1
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    tube(col,"grown terrace retaining edge",[(v[0],v[1],v[2]+.10) for v in verts[1:]+[verts[1]]],.035,"resin")


def utility(col,x,y,z=.24,waste_in=False):
    for sign,key in ((-1,"silica"),(1,"silt")):
        p=(x+sign*.26,y,z)
        tube(col,"isolated utility channel",[(p[0],y-1.0,z+.06),(p[0],y-.6,z+.12),p,(p[0],y+.25,z)],.075,key)
        arc(col,"utility valve lip",(p[0],y+.25,z),.085,.085,0,"resin",.018)
    # Visible coupled port is not a shared circular foundation.


def anchor(col,name,p):
    o=bpy.data.objects.new(name,None);col.objects.link(o);o.parent=ROOTS[col.name];o.location=p
    o.empty_display_type="PLAIN_AXES";o.empty_display_size=.15


NAMES=["01_seed_shelter","02_rooted_dwelling","03_mature_habitat","04_symbiotic_court","05_terraced_habitat","06_memory_manor","07_general_store","08_mineral_washery","09_ceramic_kiln","10_waste_digester"]
for tier,name in enumerate(NAMES[:6],1):
    col=group(name)
    # Enclosed ancestral chamber: smallest stage is not a roof-only hut.
    organ(col,(-.65,-.4,.61),(.75,.80,.61),1)
    if tier==1:
        for j in range(3):leaf(col,(-1.25+j*.15,.25,.03),.35+j*.12,.08,j)
    if tier==2:
        organ(col,(.35,.55,.82),(.91,1.12,.84),2)
        lattice(col,(.1,.4,.1),1.27,1.5,.58,1,2)
        garden(col,(1.12,-.3,.1),.35,.45,5,2)
    if tier==3:
        organ(col,(-.1,.75,1.08),(.95,1.0,1.10),3)
        organ(col,(1.10,.1,.68),(.58,.75,.65),4)
        lattice(col,(.2,.45,.12),1.65,1.55,.68,2,3)
        garden(col,(.5,-1.05,.14),.65,.42,8,3)
        canopy(col,[(-1.15,.8,2.65),(1.28,.95,2.5),(.55,-.5,2.35)])
    if tier==4:
        organ(col,(-1.0,1.1,1.0),(.8,.85,.95),4)
        organ(col,(1.12,.65,.85),(.8,.92,.82),5)
        organ(col,(.1,1.85,.75),(.72,.6,.72),6)
        lattice(col,(0,.5,.1),2.12,2.0,.68,2,4)
        garden(col,(.05,.1,.12),.78,.7,12,4)
        canopy(col,[(-1.15,1.8,2.30),(1.55,1.45,2.5),(.7,-.45,2.05)])
        garden(col,(-1.3,-.9,.12),.32,.45,5,12)
    if tier>=5:
        organ(col,(1.0,.2,.82),(.8,1.0,.8),6)
        organ(col,(-1.0,1.0,.88),(.83,.88,.87),7)
        terrace(col,(0,.6,1.5),2.2,1.85)
        organ(col,(-.1,.7,2.15),(.85,.92,.7),8)
        for j,p in enumerate(((-1.45,.25,1.55),(1.35,.8,1.55),(.5,-.65,1.55))):garden(col,p,.65,.23,9,8+j)
        canopy(col,[(-1.2,1.5,3.45),(1.2,1.25,3.35),(.9,-.55,3.05)],1.55)
    if tier==6:
        terrace(col,(-.2,.9,2.92),1.36,1.35)
        organ(col,(-.45,1.05,3.42),(.66,.6,.6),9)
        # Encoded curved silica archive leaves instead of an arbitrary crystal crown.
        for j in range(5):
            leaf(col,(-.95+j*.25,1.35,3.1),1.50+.15*math.sin(j),.25,(j-2)*.28,"silica" if j%2==0 else "memory",j)
        for j,p in enumerate(((-.9,.25,2.97),(.75,.7,2.97))):garden(col,p,.40,.20,6,15+j)
        organ(col,(1.70,.8,1.0),(.45,.8,.92),11)
    # All-tier biological receiving mouth stays unobscured by later upper growth.
    cup(col,(-.65,-1.22,.06),.27,.3,.16,"shell")
    utility(col,0 if tier==1 else 1.3,1.05 if tier==1 else 1.9)
    anchor(col,"CarrierInput",(-.65,-1.5,.18));anchor(col,"CarrierOutput",(-.2,-1.4,.2))
    anchor(col,"CleanFlowIn",(-.26 if tier==1 else 1.04,1.3 if tier==1 else 2.15,.24))
    anchor(col,"WasteReturnOut",(.26 if tier==1 else 1.56,1.3 if tier==1 else 2.15,.24))

# Store: integrated low organism with three visible typed retention galleries.
col=group(NAMES[6])
organ(col,(0,.62,.92),(1.8,.88,.90),21,"store")
for i,(x,y,kind) in enumerate(((-1.12,-.3,"silica"),(0,-.75,"food"),(1.1,-.25,"carbonate"))):
    cup(col,(x,y,.12),.65,.68,.6,"shell")
    lattice(col,(x,y,.08),.63,.65,.36,1,21+i)
    goods(col,(x,y,.35),kind,22,"CargoOutput",(.48,.45),22+i)
    # Upper retaining rim and short protective leaf; contents are not covered.
    arc(col,"inventory chamber retention rim",(x,y,.12),.65,.68,.6,"resin",.045)
    cup(col,(x,1.65,.1),.44,.42,.45,"shell")
    lattice(col,(x,1.65,.06),.43,.40,.28,1,25+i)
    goods(col,(x,1.65,.26),kind,12,"CargoOutput",(.30,.28),27+i)
    tube(col,"continuous typed storage gallery",[(x,y,.22),(x,.75,.23),(x,1.65,.23)],.12,"shell")
for x in (-1.6,1.6):
    cup(col,(x,-1.0,.04),.32,.4,.18,"shell")
    anchor(col,"CarrierInput" if x<0 else "CarrierOutput",(x,-1.35,.2))

# Washery: rigid porous backbone behind descending asymmetric process anatomy.
col=group(NAMES[7])
for i in range(3):
    x=-1.5+i*1.4;z=1.65-i*.62
    lattice(col,(x,.1,.05),.63,.68,z,3,30+i)
    cup(col,(x,.1,z),.72,.77,.44)
    goods(col,(x,.1,z+.16),"raw" if i==0 else "silica",18,"CargoInput" if i==0 else "CargoOutput",(.5,.45),30+i)
    if i<2:
        tube(col,"enclosed screened process transfer",[(x+.5,.1,z+.22),(x+.8,.1,z+.15),(x+1.1,.1,z-.42)],.15,"membrane","Flow")
    if i==1:
        for k in range(5):
            tube(col,"porous screening gill",[(x-.35+k*.15,-.35,z+.28),(x-.35+k*.15,.1,z+.60),(x-.35+k*.15,.50,z+.28)],.032,"resin")
organ(col,(-1.45,.85,1.0),(.6,.55,.95),30,"store")
for j in range(2):
    tube(col,"washery carbonate process backbone",[(-1.75+j*.40,.95,.12),(-1.3+j*.35,1.02,1.8),
         (-.20+j*.35,.95,1.22),(1.15+j*.30,.78,.30)],[.14,.13,.10,.075],"chalk",sides=10)
for j in range(5):leaf(col,(-1.9+j*.18,.85,1.9),.8+.2*math.sin(j),.10,j*.4,"membrane",j)
cup(col,(-1.1,-1.0,.08),.48,.40,.26);goods(col,(-1.1,-1,.19),"raw",8,"Residue",(.3,.25),41)
utility(col,-1.9,1.25)
anchor(col,"CarrierInput",(-1.9,-.1,2.05));anchor(col,"CarrierOutput",(1.35,-.5,.7))
anchor(col,"CleanFlowIn",(-2.16,1.5,.24));anchor(col,"WasteReturnOut",(-1.64,1.5,.24))

# Kiln: closed heavy mantle, mineral heat insulation, recessed loading throat.
col=group(NAMES[8])
organ(col,(-.5,.4,1.35),(1.15,1.1,1.4),40,"kiln")
# Overlapping pale insulated panels do not share the household teal roof silhouette.
for j in range(7):
    a=.15+j*math.pi/6
    pts=[(-.5+1.22*math.cos(a)*math.sin(t),.4+1.18*math.sin(a)*math.sin(t),1.35+1.47*math.cos(t)) for t in [.15+i*2.65/24 for i in range(25)]]
    tube(col,"mineral thermal buttress",pts,.11,"ceramic")
cup(col,(-.65,-.85,.12),.5,.55,.35,"ceramic")
for i in range(4):
    terrace(col,(.95,-.55+i*.43,.35+i*.16),.5,.22)
    goods(col,(.95,-.55+i*.43,.37+i*.16),"ceramic",4,"CargoOutput",(.3,.12),50+i)
for j in range(5):leaf(col,(-1.05+j*.23,.95,2.0),.80,.1,j*.3,"ceramic",j)
cup(col,(-1.45,-.7,.05),.28,.4,.2,"shell");goods(col,(-1.45,-.7,.17),"silica",8,"CargoInput",(.18,.2),50)
for j in range(4):ball(col,"contained metabolic fuel",(-1.5,-.15+j*.17,.15),(.13,.11,.12),"dark","CargoInput__anoxic_organics",12)
utility(col,-1.5,1.25)
anchor(col,"CarrierInput",(-.65,-1.35,.24));anchor(col,"CarrierOutput",(1.4,-.55,.45))
anchor(col,"CleanFlowIn",(-1.76,1.5,.24));anchor(col,"WasteReturnOut",(-1.24,1.5,.24))

# Digester: no household apertures. Sealed asymmetrical muscular fermentation sacs.
col=group(NAMES[9])
for j,(p,size) in enumerate((((-.6,.5,1.2),(.95,1.1,1.2)),((.85,.85,.8),(.70,.75,.85)))):
    mantle=ball(col,"sealed fermentation mantle",p,size,"dark",segments=32)
    for vertex in mantle.data.vertices:
        q=vertex.co;z=q.z/size[2];a=math.atan2(q.y/size[1],q.x/size[0])
        wave=1+.045*math.cos(a*6+.2*j)*(1-z*z)
        q.x*=wave*(1-.08*z);q.y*=wave;q.x+=.08*size[0]*z*z
    mantle.data.update()
    rx,ry,h=size
    for k in range(6):
        a=k*math.tau/6+.17*j
        tube(col,"pressurised lobe seam",[(p[0]+rx*math.sin(t)*math.cos(a)*(1-.08*math.cos(t))+.08*rx*math.cos(t)**2,p[1]+ry*math.sin(t)*math.sin(a),p[2]+h*math.cos(t)) for t in [.13+i*2.84/24 for i in range(25)]],.045,"shell")
ball(col,"buried containment tissue",(0,.35,.12),(1.6,1.2,.3),"silt")
lattice(col,(0,.55,.1),1.35,1.18,.7,2,70)
tube(col,"sealed digestion transfer neck",[(-.2,.5,.85),(.3,.75,.65),(.7,.8,.55)],.21,"membrane","Flow")
cup(col,(-.7,-.9,.06),.55,.5,.32,"dark");goods(col,(-.7,-.9,.15),"waste",13,"CargoInput",(.35,.28),70)
tube(col,"contained waste receiving throat",[(-.7,-.62,.19),(-.75,-.40,.22),(-.60,-.18,.37)],
     [.22,.20,.16],"dark",sides=12)
tube(col,"enzyme separation tissue",[(.7,.50,.40),(1.25,.16,.28),(1.35,-.2,.24)],.10,"membrane","Flow")
cup(col,(1.35,-.2,.09),.24,.35,.40,"shell")
ball(col,"retained enzyme output",(1.35,-.2,.29),(.16,.22,.15),"amber","CargoOutput__repair_enzyme")
cup(col,(.4,-1.0,.05),.55,.40,.25,"shell");goods(col,(.4,-1,.16),"fertiliser",24,"CargoOutput",(.4,.26),71)
utility(col,-1.4,1.35,waste_in=True)
anchor(col,"CarrierInput",(-.7,-1.3,.22));anchor(col,"CarrierOutput",(1.4,-.65,.3))
anchor(col,"CleanFlowIn",(-1.66,1.6,.24));anchor(col,"WasteReturnIn",(-1.14,1.6,.24))


def consolidate(col):
    """One mesh per state group, material-indexed surfaces. No hundred-node assets."""
    for state,root in list(STATE[col.name].items())+list(PHASES[col.name].items()):
        objects=[o for o in col.objects if o.type=="MESH" and o.parent==root]
        if not objects:continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in objects:o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        bpy.ops.object.join()
        bpy.context.object.name=state+"Mesh"


for name,col in COLS.items():
    bpy.context.view_layer.update()
    pts=[o.matrix_world@v.co for o in col.objects if o.type=="MESH" for v in o.data.vertices]
    hi=[max(p[i] for p in pts) for i in range(3)];lo=[min(p[i] for p in pts) for i in range(3)]
    anchor(col,"LabelAnchor",(0,0,hi[2]+.3));anchor(col,"CameraAnchor",(0,0,hi[2]*.5))
    anchor(col,"WorkAnchor",(0,-1.0,.3))
    consolidate(col)
    if "Dormancy" in STATE[name]:
        STATE[name]["Dormancy"].hide_render=True
        for obj in STATE[name]["Dormancy"].children:obj.hide_render=True
    anchors={o.name.split(".")[0]:[o.location.x,o.location.z,-o.location.y] for o in col.objects if o.type=="EMPTY" and o.parent==ROOTS[name] and o not in STATE[name].values()}
    (OUT/(name+".anchors.json")).write_text(json.dumps({"asset":name,"up_axis":"+Y","units":"metres","anchors":anchors,"authoritative":False},indent=2)+"\n")
    bpy.ops.object.select_all(action="DESELECT")
    for o in col.objects:o.select_set(True)
    path=OUT/(name+".glb")
    bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLB",use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials="EXPORT",export_animations=False)
    triangles=sum(len(p.vertices)-2 for o in col.objects if o.type=="MESH" for p in o.data.polygons)
    surfaces=sum(len({p.material_index for p in o.data.polygons}) for o in col.objects if o.type=="MESH")
    originals={}
    for obj in list(col.objects):
        if obj.type!="MESH":continue
        originals[obj]=obj.data
        obj.data=obj.data.copy()
        mod=obj.modifiers.new("settlement distance simplification","DECIMATE");mod.ratio=.42;mod.use_collapse_triangulate=True
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
    lod_path=OUT/(name+"_lod.glb")
    bpy.ops.export_scene.gltf(filepath=str(lod_path),export_format="GLB",use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials="EXPORT",export_animations=False)
    lod_triangles=sum(len(p.vertices)-2 for o in col.objects if o.type=="MESH" for p in o.data.polygons)
    for obj,data in originals.items():obj.data=data
    RECORDS.append({"id":name,"path":str(path.relative_to(ROOT)),"lod_path":str(lod_path.relative_to(ROOT)),"triangles":triangles,"lod_triangles":lod_triangles,"surfaces":surfaces,"bounds_y_up":{"min":[lo[0],lo[2],-hi[1]],"max":[hi[0],hi[2],-lo[1]]},"states":list(STATE[name]),"construction_phases":list(PHASES[name]),"status":"refined_candidate"})
(OUT/"manifest.json").write_text(json.dumps({"version":4,"gameplay_bound":False,"materials":list(PALETTE),"assets":RECORDS},indent=2)+"\n")

scene=bpy.context.scene;scene.render.engine="CYCLES";scene.cycles.samples=32
if "--quick-review" in sys.argv:scene.cycles.samples=16
scene.world.use_nodes=True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.25,.32,.34,1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.45
scene.view_settings.view_transform="AgX"
for loc,power,size in (((-6,-9,12),1900,9),((8,4,10),1500,8)):
    bpy.ops.object.light_add(type="AREA",location=loc);o=bpy.context.object;o.data.energy=power;o.data.size=size
    o.rotation_euler=(-o.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.object.camera_add(location=(8,-14,12));camera=bpy.context.object;scene.camera=camera;camera.data.type="ORTHO"
camera.rotation_euler=(Vector((0,0,1))-camera.location).to_track_quat("-Z","Y").to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.12));ground=bpy.context.object
ground.data.materials.append(MATS["silt"])
right=camera.rotation_euler.to_matrix()@Vector((1,0,0));back=Vector((-right.y,right.x,0))


def sheet(filename,names,columns=3,spacing=6.5):
    offsets={};rows=math.ceil(len(names)/columns)
    for col in COLS.values():col.hide_render=True
    for i,name in enumerate(names):
        col=COLS[name];col.hide_render=False
        offset=right*((i%columns-(columns-1)/2)*spacing)+back*((i//columns-(rows-1)/2)*spacing*1.2)
        ROOTS[name].location=offset;offsets[name]=offset
    scene.render.resolution_x=1800;scene.render.resolution_y=1100 if rows>1 else 850
    if "--quick-review" in sys.argv:
        scene.render.resolution_x=1400;scene.render.resolution_y=900 if rows>1 else 700
    scene.render.resolution_percentage=100;bpy.context.view_layer.update()
    inv=camera.rotation_euler.to_matrix().transposed()
    pts=[inv@(o.matrix_world@v.co) for name in names for o in COLS[name].objects if o.type=="MESH" for v in o.data.vertices]
    lo=[min(p[i] for p in pts) for i in range(3)];hi=[max(p[i] for p in pts) for i in range(3)]
    camera.data.ortho_scale=max(hi[0]-lo[0],(hi[1]-lo[1])*scene.render.resolution_x/scene.render.resolution_y)*1.15
    camera.location=camera.rotation_euler.to_matrix()@Vector(((lo[0]+hi[0])/2,(lo[1]+hi[1])/2,hi[2]+30))
    scene.render.filepath=str(RENDER/filename);bpy.ops.render.render(write_still=True)
    for name in offsets:ROOTS[name].location=(0,0,0)

if "--export-only" not in sys.argv:
    sheet("housing_refined.png",NAMES[:6])
    sheet("industry_refined.png",NAMES[6:],2,7)
    if "--quick-review" not in sys.argv:
        sheet("seed_shelter_detail.png",[NAMES[0]],1)
        sheet("memory_manor_detail.png",[NAMES[5]],1)
for i,(name,col) in enumerate(COLS.items()):
    col.hide_render=False;ROOTS[name].location=((i%5)*7,(i//5)*8,0)
for data in list(bpy.data.meshes):
    if data.users==0:bpy.data.meshes.remove(data)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"verdant_architecture_v04.blend"),compress=True)
print("REFINED ARCHITECTURE: ten textured GLB candidates exported")
