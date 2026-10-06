"""Build Pondlife's submerged transport organs in Blender 5.x.

The .blend is the editable source. OBJ/MTL exports use metres and +Y up for
the existing Godot blockout loader. This is visual-only: no network rules.

Run from the repo root:
  /Applications/Blender.app/Contents/MacOS/Blender -b -t 2 --python tools/generate_current_organs_blender.py
"""

from __future__ import annotations

import math
from pathlib import Path

import bpy
from mathutils import Vector


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "blockout" / "environment"
SOURCE = ROOT / "assets" / "source" / "blender"
PREVIEW = ROOT / "docs" / "art" / "renders"
for folder in (OUT, SOURCE, PREVIEW):
    folder.mkdir(parents=True, exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


def mat(name, rgb, rough=0.68, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.diffuse_color = (*rgb, 1)
    material.use_nodes = True
    shader = material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*rgb, 1)
    shader.inputs["Roughness"].default_value = rough
    shader.inputs["Metallic"].default_value = metallic
    return material


membrane = mat("Current | dark living membrane", (0.055, 0.22, 0.23))
ridge = mat("Current | green-blue rib", (0.12, 0.39, 0.37))
lip = mat("Current | pale intake lip", (0.35, 0.65, 0.57))
cilia = mat("Current | mint cilia", (0.48, 0.73, 0.58))
throat = mat("Current | recessed throat", (0.035, 0.12, 0.15))
signal = mat("Current | amber signal", (0.83, 0.55, 0.19), metallic=0.06)
shell = mat("Current | carbonate footing", (0.30, 0.40, 0.37))


def collection(name):
    return bpy.data.collections.new(name)


def put(obj, group, material):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    group.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def ellipsoid(name, loc, scale, material, group, segments=12, rings=6):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if any(word in name for word in ("bed", "pad", "footing")):
        for vertex in obj.data.vertices:
            angle = math.atan2(vertex.co.y, vertex.co.x)
            warp = 1 + 0.045 * math.sin(7 * angle + 0.6) + 0.035 * math.cos(4 * angle)
            vertex.co.x *= warp
            vertex.co.y *= warp
    return put(obj, group, material)


def cylinder_between(name, a, b, r0, r1, material, group, vertices=9):
    a, b = Vector(a), Vector(b)
    mid = (a + b) / 2
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=r0, radius2=r1, depth=(b - a).length,
        location=mid,
    )
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = (b - a).to_track_quat("Z", "Y").to_euler()
    return put(obj, group, material)


def torus(name, loc, major, minor, material, group, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(
        major_segments=18, minor_segments=5,
        location=loc, rotation=rotation, major_radius=major, minor_radius=minor,
    )
    obj = bpy.context.object
    obj.name = name
    # Break the lathed, machined ring silhouette without obscuring the mouth.
    for vertex in obj.data.vertices:
        angle = math.atan2(vertex.co.y, vertex.co.x)
        warp = 1 + 0.045 * math.sin(5 * angle + 0.35) + 0.02 * math.sin(9 * angle)
        vertex.co.x *= warp
        vertex.co.y *= warp
    return put(obj, group, material)


def vein(name, points, radius, material, group):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 3
    curve.bevel_depth = radius
    curve.bevel_resolution = 1
    poly = curve.splines.new("POLY")
    poly.points.add(len(points) - 1)
    for point, xyz in zip(poly.points, points):
        point.co = (*xyz, 1)
    obj = bpy.data.objects.new(name, curve)
    group.objects.link(obj)
    curve.materials.append(material)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj.select_set(False)
    return bpy.context.view_layer.objects.active


def new_group(name):
    group = collection(name)
    bpy.context.scene.collection.children.link(group)
    return group


def grow_socket(group, name, direction, radius=0.62, height=0.82, many_cilia=True):
    """A visibly hollow, horizontally facing intake, not a road-end cap."""
    d = Vector(direction).normalized()
    start = d * 0.45 + Vector((0, 0, 0.22))
    end = d * 1.25 + Vector((0, 0, height))
    cylinder_between(name + " neck", start, end, radius * 0.48, radius * 0.64, ridge, group, 12)
    # The mouth faces outward in the horizontal plane; the black cavity sits
    # behind the pale ring so its function survives the overhead game camera.
    mouth = end + d * 0.055
    q = d.to_track_quat("Z", "Y")
    ring = torus(name + " living rim", mouth, radius, 0.085, lip, group)
    ring.rotation_euler = q.to_euler()
    dark = ellipsoid(name + " hollow throat", mouth - d * 0.045, (radius * 0.65, radius * 0.65, 0.035), throat, group)
    dark.rotation_euler = q.to_euler()
    if many_cilia:
        tangent = Vector((-d.y, d.x, 0))
        for i in range(9):
            t = (i - 4) / 4
            foot = mouth + tangent * (t * radius * 0.92) + Vector((0, 0, -0.22))
            tip = foot + d * (0.28 + 0.06 * (i % 3)) + Vector((0, 0, 0.11 + (1 - abs(t)) * 0.11))
            cylinder_between(name + f" cilium {i}", foot, tip, 0.026, 0.007, cilia, group, 5)
    return mouth


# 1. Four-way current junction: a soft distribution organism, readable from
# the normal isometric camera, with four real-looking mouths and a crown.
junction = new_group("node_current_junction_a")
ellipsoid("anchoring bed", (0, 0, 0.14), (1.47, 1.36, 0.24), shell, junction)
ellipsoid("central fluid organ", (0, 0, 0.51), (0.85, 0.78, 0.47), membrane, junction)
ellipsoid("raised flow crown", (0.04, -0.07, 0.82), (0.44, 0.43, 0.24), ridge, junction)
torus("visible valve halo", (0.04, -0.07, 0.99), 0.31, 0.045, lip, junction)
for label, direction in (("north", (0, 1, 0)), ("east", (1, 0, 0)), ("south", (0, -1, 0)), ("west", (-1, 0, 0))):
    grow_socket(junction, label, direction, 0.37, 0.57, False)
for i in range(8):
    a = i * math.tau / 8 + 0.17
    p = Vector((math.cos(a), math.sin(a), 0))
    vein(f"anchoring vane {i}", [(p.x * 0.33, p.y * 0.33, 0.43), (p.x * 0.91, p.y * 0.91, 0.3), (p.x * 1.3, p.y * 1.3, 0.13)], 0.047, ridge, junction)
for i in range(12):
    a = i * math.tau / 12
    ellipsoid(f"pulse vesicle {i}", (math.cos(a) * 0.7, math.sin(a) * 0.7, 0.66), (0.065, 0.065, 0.042), signal if i % 3 == 0 else cilia, junction, 8, 4)


# 2. Building intake port: deliberately one-sided, so a building can show
# which face meets a controlled current. Its local +X is the outward mouth.
intake = new_group("node_building_intake_a")
ellipsoid("rooted mounting pad", (0, 0, 0.12), (1.22, 1.04, 0.2), shell, intake)
ellipsoid("muscular chamber", (0.13, 0, 0.42), (0.87, 0.77, 0.4), membrane, intake)
grow_socket(intake, "outward intake", (1, 0, 0), 0.54, 0.83, True)
for side in (-1, 1):
    vein(f"return vein {side}", [(-0.73, side * 0.28, 0.18), (-0.32, side * 0.6, 0.38), (0.55, side * 0.48, 0.56), (1.2, side * 0.17, 0.82)], 0.075, ridge, intake)
    for n in range(3):
        z = 0.26 + n * 0.17
        ellipsoid(f"signal bead {side} {n}", (-0.24 + n * 0.28, side * 0.64, z), (0.07, 0.07, 0.07), signal, intake, 8, 4)


# 3. Transfer organ: a different, cargo-facing silhouette with receiving cups
# and a tall sensory fan. It can stand beside storage without reading as a hut.
transfer = new_group("node_transfer_fan_a")
ellipsoid("flared footing", (0, 0, 0.13), (1.76, 1.21, 0.24), shell, transfer)
ellipsoid("transfer body", (-0.1, 0, 0.48), (1.18, 0.7, 0.43), membrane, transfer)
grow_socket(transfer, "incoming", (-1, 0, 0), 0.42, 0.65, False)
grow_socket(transfer, "outgoing", (1, 0, 0), 0.42, 0.65, False)
for i, y in enumerate((-0.58, 0, 0.58)):
    ellipsoid(f"cargo cup {i}", (0.0, y, 0.84), (0.39, 0.25, 0.13), ridge, transfer)
    torus(f"cargo cup lip {i}", (0.0, y, 0.95), 0.21, 0.035, lip, transfer)
    ellipsoid(f"cup darkness {i}", (0, y, 0.95), (0.18, 0.17, 0.02), throat, transfer, 10, 5)
for i in range(7):
    y = (i - 3) * 0.17
    spine = [(-0.62, y * 0.4, 0.53), (-0.67, y * 1.1, 0.95), (-0.49, y * 1.5, 1.66 + 0.14 * (1 - abs(i - 3) / 3))]
    vein(f"sensory fan rib {i}", spine, 0.045, ridge, transfer)
    ellipsoid(f"sensory tip {i}", spine[-1], (0.07, 0.07, 0.095), cilia, transfer, 8, 4)
for i in range(6):
    a = i * math.tau / 6 + 0.3
    ellipsoid(f"footer nodule {i}", (math.cos(a) * 1.36, math.sin(a) * 0.78, 0.28), (0.13, 0.13, 0.11), signal if i in (1, 4) else lip, transfer, 8, 4)


# Export each group with a local origin and no stage objects. The Blender 5.x
# OBJ exporter transforms Z-up source geometry to Y-up engine geometry.
groups = (junction, intake, transfer)
for group in groups:
    bpy.ops.object.select_all(action="DESELECT")
    for obj in group.objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = list(group.objects)[0]
    bpy.ops.wm.obj_export(
        filepath=str(OUT / (group.name + ".obj")),
        export_selected_objects=True,
        export_materials=True,
        export_triangulated_mesh=True,
        forward_axis="NEGATIVE_Z",
        up_axis="Y",
    )


# Keep an arranged, lit presentation stage in the editable Blender source.
offsets = (-4.1, 0, 4.25)
for group, offset in zip(groups, offsets):
    for obj in group.objects:
        obj.location.x += offset

stage = new_group("Preview stage (not exported)")
for x in offsets:
    ellipsoid("quiet silt disc", (x, 0, -0.06), (2.15, 1.65, 0.05), mat("Preview silt", (0.31, 0.34, 0.29)), stage)

world = bpy.context.scene.world
world.color = (0.055, 0.11, 0.12)
bpy.ops.object.light_add(type="AREA", location=(-3, -4, 8))
key = bpy.context.object
key.name = "soft submerged key"
key.data.energy = 1700
key.data.shape = "DISK"
key.data.size = 7
bpy.ops.object.light_add(type="AREA", location=(6, 3, 6))
fill = bpy.context.object
fill.name = "cool backlight"
fill.data.energy = 1100
fill.data.color = (0.45, 0.84, 1)
fill.data.size = 6
bpy.ops.object.camera_add(location=(7.2, -9.5, 9.4))
camera = bpy.context.object
camera.rotation_euler = (Vector((0, 0, 0.52)) - camera.location).to_track_quat("-Z", "Y").to_euler()
camera.data.type = "ORTHO"
camera.data.ortho_scale = 15.2
bpy.context.scene.camera = camera

scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.render.resolution_x = 1500
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(PREVIEW / "submerged_current_organs_v01.png")
scene.view_settings.view_transform = "AgX"
bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE / "submerged_current_organs_v01.blend"))
bpy.ops.render.render(write_still=True)

for group in groups:
    faces = sum(len(p.vertices) - 2 for obj in group.objects if obj.type == "MESH" for p in obj.data.polygons)
    print(f"{group.name}: {faces} triangles")
print(f"Source: {SOURCE / 'submerged_current_organs_v01.blend'}")
print(f"Preview: {scene.render.filepath}")
