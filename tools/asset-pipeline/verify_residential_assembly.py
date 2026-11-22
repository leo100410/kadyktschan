"""Offline assembly check including slabs and stair routes. Skips Blender export, text glyphs and decay painting."""
import ast,json,os,sys,types
from pathlib import Path
root=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(root/'tools/asset-pipeline'))
sys.modules['bpy']=types.SimpleNamespace()
sys.argv=['offline','--',str(root)]
os.environ["KDK_ROOT"]=str(root)
import build_t5_kit as kit
kit.Part.build=lambda self:self
source=root/'tools/asset-pipeline/build_buildings.py'
tree=ast.parse(source.read_text());tree.body.pop()
ns={'__file__':str(source),'__name__':'offline_build'}
exec(compile(tree,str(source),'exec'),ns)
ns['text_polys']=lambda text,size:([],[],len(text)*size*.6)
ns['paint_decay']=lambda *args:None
mapping_tree=ast.parse((root/'tools/editor/place_buildings.py').read_text())
mapping_node=next(n for n in mapping_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SLOT_MI' for t in n.targets))
material_slots=ast.literal_eval(mapping_node.value)
parts=kit.make_parts();polys=ns['osm_polygons']()
manifest=json.loads((root/'assets/buildings/buildings_manifest.json').read_text())
updates={}
for b in ns['DATA']['buildings']:
 if b['label'] in ns['residential'].HOUSES:
  main,glass,info=ns['build_one'](b,polys.get(b.get('osm')) or ns['rect_poly'](b),parts)
  # Check the stair routes against the assembled building, including generated slabs and partition walls.
  import math
  from test_residential import obstruction,samples
  origin,along,inward=info['section_frame'];angle=math.radians(info['yaw_deg']);ca,sa=math.cos(angle),math.sin(angle)
  verts=[]
  for x,y,z in main.verts:
   wn=b['north_m']+x*ca+y*sa;we=b['east_m']+x*sa-y*ca
   dn,de=wn-origin[0],we-origin[1]
   verts.append((dn*along[0]+de*along[1],dn*inward[0]+de*inward[1],z-ns['Z0']))
  boxes=[]
  for face,mi in zip(main.faces,main.face_mat):
   vs=[verts[i] for i in face];lo=tuple(min(v[k] for v in vs) for k in range(3));hi=tuple(max(v[k] for v in vs) for k in range(3))
   if hi[0]<0 or lo[0]>3 or hi[1]<5.4 or lo[1]>10.5:continue
   boxes.append((lo,hi,main.mats[mi]))
  for floor in range(info['furnished_floors']-1):
   z=floor*2.8
   route=[(.72,6.35,z)]+[(.72,6.6+(k+.5)*.28,z+(k+1)*1.4/9) for k in range(9)]
   route +=[(.72,9.55,z+1.4),(2.25,9.55,z+1.4)]
   route +=[(2.25,9.12-(k+.5)*.28,z+1.4+(k+1)*1.4/9) for k in range(9)]
   route +=[(2.25,6.35,z+2.8),(2.25,5.8,z+2.8)]
   for x,y,zz in samples(route):
    hit=obstruction(boxes,x,y,zz)
    assert hit is None,(b['label'],floor,(x,y,zz),hit)
  assert all(name in material_slots or name.startswith('Pic_') for name in info['materials']), (b['label'],'unmapped material')
  updates[b['label']]=info
  print(info['label'],info['furnished_floors'],'floors',len(info['room_lights']),'lights',info['tris'],'tris')
output=root/'Saved/ResidentialAssemblyPreview.json'
output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps([updates.get(b['label'],b) for b in manifest]))
print('ASSEMBLY CHECK OK (no Blender export)')
