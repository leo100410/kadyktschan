"""Fictional abandoned neighbourhood diesel power station, open entrance and repair props."""
import json
import math
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import build_vegetation as veg
sys.path.insert(0,str(Path(veg.ROOT)/'tools/research'))
from terrain_mesh import TerrainMesh

root=Path(veg.ROOT)
site=json.loads((root/'assets/power/site.json').read_text())
e,n,f=site['east_m'],site['north_m'],site['floor_m']
ground=TerrainMesh(root/'assets/terrain/terrain_kadykchan_8km.obj').z
veg.bpy.ops.wm.read_factory_settings(use_empty=True)
g=veg.Geo()

def box(n0,n1,e0,e1,z0,z1,mat):
    veg.pbox(g,n0,n1,-e1,-e0,f+z0,f+z1,mat)

def tube(a,b,r,mat='Metal',sides=12):
    veg.prism(g,(a[0],-a[1],f+a[2]),(b[0],-b[1],f+b[2]),r,mat,sides)
    faces=g.f[-sides:]
    for ring in ([g.v[face[0]] for face in faces][::-1],[g.v[face[3]] for face in faces]):
        for i in range(1,len(ring)-1):
            tri=[ring[0],ring[i],ring[i+1]]
            g.quad(tri+[tri[-1]],veg._uv(tri)+[veg._uv(tri)[-1]],mat)

# Thick masonry shell with a 2.6 m entrance and an open interior aisle.
box(-5.5,5.5,-6,6,-1.3,0,'Concrete')
for y0,y1 in ((-6,-5.65),(5.65,6)):
    box(-5.4,5.4,y0,y1,0,2.1,'Brick');box(-5.4,5.4,y0,y1,3.6,4.5,'Brick')
    for a,b in ((-5.4,-3),(-.8,.4),(2.6,5.4)):
        box(a,b,y0,y1,2.1,3.6,'Brick')
    for a,b in ((-3,-.8),(.4,2.6)):
        for x in (a,b,(a+b)/2): box(x,x+.05,y0,y1,2.1,3.6,'Metal')
        for z in (2.1,2.85,3.55): box(a,b,y0,y1,z,z+.05,'Metal')
box(5,5.4,-6,6,0,4.5,'Brick')
box(-5.4,-5,-6,-1.3,0,4.5,'Brick');box(-5.4,-5,1.3,6,0,4.5,'Brick')
box(-5.4,-5,-1.3,1.3,3.1,4.5,'Concrete')
# Weathered roof: ventilation slot over generator, skylight bays left open.
for e0,e1 in ((-6.3,-0.6),(1.2,6.3)):
    box(-5.7,5.7,e0,e1,4.5,4.7,'Metal')
for x in (-4,-1,2,4.8):
    box(x,x+0.16,-5.8,5.8,4.2,4.4,'Metal')
for y in (-5.9,5.9):
    tube((-5.7,y,4.9),(5.7,y,4.9),0.08)
# Front double doors folded out of the route, warning board and lintel sign.
box(-7,-5.3,-1.65,-1.5,0.1,3,'Metal');box(-7,-5.3,1.5,1.65,0.1,3,'Metal')
box(-5.48,-5.4,-3.7,-1.8,1.5,2.3,'Enamel')
box(-5.52,-5.4,-1.3,1.3,3.45,4.05,'Concrete')
# Ramp meets rendered terrain; no single tall doorstep.
verts=[(-11,1.3,ground(e-1.3,n-11)+0.03),(-11,-1.3,ground(e+1.3,n-11)+0.03),(-5.45,-1.3,f+0.01),(-5.45,1.3,f+0.01)]
g.quad(verts,veg._uv(verts),'Concrete')
g.quad(verts[::-1],veg._uv(verts[::-1]),'Concrete')
# Diesel set: rounded engine blocks, flywheel, exhaust, cooling ribs, fuel pipes.
box(-1.7,1.6,-4.3,-1.6,0,0.3,'Concrete')
box(-1.5,1.4,-4.1,-1.8,0.3,0.5,'Metal')
tube((-1,-2.9,1.15),(1.1,-2.9,1.15),0.65,'Metal',24)
for k in range(7):
    box(-0.9+k*.27,-0.78+k*.27,-3.45,-2.35,1.2,1.9,'Metal')
tube((-1.1,-2.9,1.1),(-1.35,-2.9,1.1),0.8,'BlackPlastic',24)
tube((0.8,-3.5,1.4),(0.8,-3.5,5.8),0.13)
tube((0.8,-3.5,5.8),(1.8,-3.5,5.8),0.13)
for k in range(12):
    box(0.8,1.35,-3.8+k*.15,-3.75+k*.15,0.7,1.7,'BlackPlastic')
# Control cabinets; cream meters, gauges and a protruding green start lever.
for y in (-3.8,-1.8,0.3):
    box(3.45,4.5,y-.7,y+.7,0.15,2.6,'Metal')
    box(3.3,3.45,y-.6,y+.6,0.3,2.5,'Enamel')
    for dz in (1.75,2.1):
        tube((3.25,y,dz),(3.28,y,dz),.16,'BlackPlastic',16)
    tube((3.12,y,1.35),(3.3,y,1.35),.07,'BlackPlastic')
box(3.03,3.13,-1.88,-1.72,1.3,1.5,'Furniture')
# Workbench and the replacement cartridge, screws, spares and tool tray.
box(.2,1.8,2.6,4.6,.9,1.02,'WoodGrey')
for x in (.3,1.6):
    for y in (2.7,4.4): box(x,x+.08,y,y+.08,0,.9,'Metal')
tube((.85,3.6,1.1),(1.15,3.6,1.1),.075,'Enamel',16)
for x in (.83,1.13): tube((x,3.6,1.1),(x+.035,3.6,1.1),.085)
box(.5,1.2,4,4.4,1.02,1.12,'BlackPlastic')
# Cable trays overhead and isolated porcelain insulators outside.
for y in (-4.8,4.8):
    tube((-4.5,y,3.7),(4.5,y,3.7),.045,'BlackPlastic')
for y in (-3,0,3):
    box(7,9,y-.8,y+.8,-.5,.3,'Concrete')
    box(7.3,8.7,y-.65,y+.65,.3,1.8,'Metal')
    for dz in (1.85,2.05,2.25):
        tube((8,y,dz),(8,y,dz+.08),.26,'Enamel',16)
# Rain gutter and scattered fragments along walls; keep the centre clear.
for k in range(18):
    x=-4.5+(k%9)*1.05; y=(-5.3 if k<9 else 5.3)
    veg.rock(g,x,-y,f+.07,.16,.12,.08,'Brick')
# Raised lettering uses an existing font, no external asset dependency.
font=veg.bpy.data.curves.new('PowerSign','FONT');font.body='DIESEL  /  04';font.size=.35
obj=veg.bpy.data.objects.new('PowerSign',font);veg.bpy.context.collection.objects.link(obj)
obj.location=(-5.54,1.15,f+3.62);obj.rotation_euler=(math.pi/2,0,-math.pi/2)
mesh=obj.evaluated_get(veg.bpy.context.evaluated_depsgraph_get()).to_mesh()
for poly in mesh.polygons:
    pts=[tuple(obj.matrix_world @ mesh.vertices[i].co) for i in poly.vertices]
    if len(pts)>=3:
        for j in range(1,len(pts)-1):
            tri=[pts[0],pts[j],pts[j+1]]
            g.quad(tri+[tri[-1]],[(0,0)]*4,'BlackPlastic')
veg.SRC=str(root/'assets/power')
veg.export('SM_PowerStation',g)
(root/'assets/power/mesh.json').write_text(json.dumps(dict(materials=g.mats,quads=len(g.f))))
print('POWER MESH OK',len(g.f))
