"""House-only concept refinement. Reuse approved architecture authoring functions.

Blender -b -t 4 --python-exit-code 1 --python tools/build_housing_polish_blender.py
Outputs an isolated candidate package; never rewrites accepted v04 or live maps.
"""
from pathlib import Path
import math
import json
import bpy

ROOT=Path(__file__).resolve().parents[1]
source=(ROOT/'tools/build_architecture_refined_blender.py').read_text()
# Reuse the full established UV/material/anatomy pipeline, up to (not including)
# processors. Keep approved house forms; enrich cultivated tissue at their roots.
setup=source.split('# Store: integrated low organism')[0]
setup=setup.replace('assets/architecture_v04','assets/housing_polish_v01').replace('docs/art/renders/architecture_v04','docs/art/renders/housing_polish_v01')
setup=setup.replace('TEXTURE_SIZE=512','TEXTURE_SIZE=1024')
setup=setup.replace('for tier,name in enumerate(NAMES[:6],1):\n','for tier,name in enumerate(NAMES[:6],1):\n    if tier not in (1,2,4,6):continue\n')
# A quieter waxed mantle with broad tonal variation; carbonate stays matte.
setup=setup.replace('rough=.59+.09*broad+.08*bands;relief=.025','rough=.40+.10*broad+.055*bands;relief=.017')
setup=setup.replace('variation=.18*broad+.055*medium-.075*bands','variation=.24*broad+.065*medium-.045*bands')
setup=setup.replace('"chalk":"C5C3A6"','"chalk":"D0C8AD"')
# Smaller, deeper organ cores leave a visible dark habitation recess rather
# than filling apertures with flat yellow discs. Finer root tips avoid tusks.
setup=setup.replace('"amber":"EEB34D"','"amber":"BF842F"')
setup=setup.replace('q=surface-normal*.075','q=surface-normal*.11')
setup=setup.replace('(width*.82,depth*.80,.035)','(width*.59,depth*.66,.028)')
setup=setup.replace('[.075,.09,.115,.15]','[.070,.082,.075,.045]')
setup=setup.replace('[.085,.09,.025]','[.060,.045,.014]')
setup=setup.replace('height=.035*bands+.018*medium','height=.018*bands+.012*medium')
exec(compile(setup,str(ROOT/'tools/build_architecture_refined_blender.py'),'exec'))

for index,(name,col) in enumerate(COLS.items()):
    tier=(1,2,4,6)[index]
    # Substrate-attached tissue, kept to flanks so habitation and supply mouths
    # stay visible. Varied blade lengths and seed vesicles replace pot ornaments.
    # A mixed bed wraps the rear/side roots, visibly touching the substrate.
    garden(col,(-.85,.32,.025),.30,.32,7,60+index)
    if tier>1: garden(col,(1.0,.85,.035),.38,.28,9,70+index)
    for side in (-1,1):
        x=side*(.94 if tier==1 else 1.42)
        y=.05 if tier==1 else .45
        for j in range(4 if tier==1 else 7):
            a=.85*j+side*.6
            px=x+.18*math.cos(a);py=y+.24*math.sin(a)
            leaf(col,(px,py,.045),.38+.09*((j+index)%4),.045+.012*(j%2),a,'growth',j+index*10)
            tube(col,'rooted vascular stem',[(px,py,.035),(px+.025,py,.18),(px+.06,py,.3+.035*(j%3))],[.018,.013,.009],'fibre',sides=6)
            ball(col,'cultivated seed vesicle',(px+.06,py,.3+.035*(j%3)),(.043,.038,.060),'memory' if tier>=4 and j%3==0 else 'growth',segments=12)
    if tier==1:
        # A small brood cluster rests inside the receiving recess, not a floating
        # light stuck onto the facade. Pale soft tissue signals habitation.
        for j in range(5):
            ball(col,'protected brood vesicle',(-.85+.09*j,-1.12,.16+.025*(j%2)),(.065,.055,.08),'membrane',segments=16)
    # Mineral nodules grow out of local contact roots, without a circular plinth.
    for j in range(7 if tier<4 else 12):
        a=.35+j*math.tau/(7 if tier<4 else 12)
        if math.sin(a)<-.55:continue
        r=1.1 if tier==1 else 1.85
        ball(col,'substrate carbonate accretion',(r*math.cos(a),.25+r*.7*math.sin(a),.045),(.11+.025*(j%2),.085,.065),'chalk',segments=12)

# Use identical export/state/LOD conventions, with a distinct output directory.
export=source[source.index('def consolidate(col):'):source.index('scene=bpy.context.scene;scene.render.engine=')]
exec(compile(export,str(ROOT/'tools/build_architecture_refined_blender.py'),'exec'))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'housing_polish_v01.blend'),compress=True)
manifest=json.loads((OUT/'manifest.json').read_text())
manifest.update(version=1,source='Approved v04 anatomy with house-only material and tissue refinement',gameplay_bound=False)
(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('HOUSE POLISH:',[(r['id'],r['triangles'],r['lod_triangles']) for r in RECORDS])
