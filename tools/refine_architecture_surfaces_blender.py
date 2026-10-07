"""Fast material-only refresh of the approved architecture Blender source.

Blender -b -t 4 --python-exit-code 1 --python tools/refine_architecture_surfaces_blender.py
Uses the same material functions as the full generator. No geometry authoring.
"""
import ast
import json
import math
from pathlib import Path

import bpy
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"assets/architecture_v04"
source=ROOT/"tools/build_architecture_refined_blender.py"
tree=ast.parse(source.read_text())
# Extract only literal palette/resolution and the two pure material authoring
# functions. Importing the full generator would delete/rebuild the scene.
selected=[]
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ("PALETTE","TEXTURE_SIZE") for t in node.targets):selected.append(node)
    if isinstance(node,ast.FunctionDef) and node.name in ("surface_maps","material"):selected.append(node)
bpy.ops.wm.open_mainfile(filepath=str(OUT/"verdant_architecture_v04.blend"))
bpy.context.preferences.filepaths.save_version=0
MATS={}
exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),"exec"))
prior={key:bpy.data.materials.get("verdant_"+key) for key in PALETTE}
for key,old in prior.items():
    if old:old.name="previous_"+key
for key,value in PALETTE.items():
    material(key,value)
    if prior[key]:
        prior[key].user_remap(MATS[key]);bpy.data.materials.remove(prior[key])
manifest=json.loads((OUT/"manifest.json").read_text())
for record in manifest["assets"]:
    col=bpy.data.collections[record["id"]]
    root=bpy.data.objects[record["id"]]
    saved_location=root.location.copy();root.location=(0,0,0)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    for obj in col.objects:obj.select_set(True)
    options=dict(export_format="GLB",use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_materials="EXPORT",export_animations=False)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/record["path"]),**options)
    originals={}
    for obj in col.objects:
        if obj.type!="MESH":continue
        originals[obj]=obj.data;obj.data=obj.data.copy()
        modifier=obj.modifiers.new("settlement distance simplification","DECIMATE")
        modifier.ratio=.42;modifier.use_collapse_triangulate=True
        bpy.context.view_layer.objects.active=obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    triangles=sum(len(p.vertices)-2 for obj in originals for p in obj.data.polygons)
    assert triangles==record["lod_triangles"],"Distance geometry changed: "+record["id"]
    bpy.ops.export_scene.gltf(filepath=str(ROOT/record["lod_path"]),**options)
    for obj,data in originals.items():obj.data=data
    root.location=saved_location
for data in list(bpy.data.meshes):
    if data.users==0:bpy.data.meshes.remove(data)
for data in list(bpy.data.images):
    if data.users==0:bpy.data.images.remove(data)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/"verdant_architecture_v04.blend"),compress=True)
print("SURFACE REFRESH: ten near/distance exports; original forms preserved")
