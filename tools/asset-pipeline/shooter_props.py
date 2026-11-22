"""Shooter mode meshes (design/gdd/shooter-mode.md): street obstacles, flat pickups, rifle, turret and tracked drone.

Blender CLI:  blender --background --factory-startup --python tools/asset-pipeline/shooter_props.py -- <project root>
Writes assets/shooter/SM_*.fbx and assets/shooter/meshes.json. Each mesh sits on its own origin (ground centre, or the
pivot for rifle/turret head/drone), long side along +X. Local helpers take UE axes (x forward, y right); the FBX
import negates Y, so y is mirrored here once.
"""
import json
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_vegetation as veg

root = Path(veg.ROOT)
veg.SRC = str(root / 'assets/shooter')
Path(veg.SRC).mkdir(parents=True, exist_ok=True)
veg.bpy.ops.wm.read_factory_settings(use_empty=True)
rnd = veg.rnd
built = {}


def box(g, x0, x1, y0, y1, z0, z1, mat):
    veg.pbox(g, x0, x1, -y1, -y0, z0, z1, mat)


def tube(g, a, b, r, mat='Metal', sides=10):
    """Capped cylinder from a to b (UE axes)."""
    veg.prism(g, (a[0], -a[1], a[2]), (b[0], -b[1], b[2]), r, mat, sides)
    faces = g.f[-sides:]
    for ring in ([g.v[face[0]] for face in faces][::-1], [g.v[face[3]] for face in faces]):
        for i in range(1, len(ring) - 1):
            tri = [ring[0], ring[i], ring[i + 1]]
            g.quad(tri + [tri[-1]], veg._uv(tri) + [veg._uv(tri)[-1]], mat)


def turned(g, x, y, z, yaw, build):
    veg.rotated(g, x, -y, z, -yaw, build)


def tilted(g, x, y, z, pitch_deg, build):
    """Build into a scratch Geo, then tip it about the local y axis (a leaning slab, a fallen panel)."""
    tmp = veg.Geo()
    build(tmp)
    c, s = math.cos(math.radians(pitch_deg)), math.sin(math.radians(pitch_deg))
    tmp.v = [(px * c + pz * s, py, -px * s + pz * c) for px, py, pz in tmp.v]
    g.append(tmp, x, -y, z, 0.0, 1.0)


def mesh(name):
    def wrap(fn):
        g = veg.Geo()
        fn(g)
        veg.export(name, g)
        built[name] = {'materials': g.mats, 'quads': len(g.f)}
        return fn
    return wrap


# --- obstacles -----------------------------------------------------------------------------------------------------
@mesh('SM_Obs_Slabs')
def slabs(g):
    """Stack of precast floor slabs left on timber bearers, one wall panel leaning against it: 1.3 m crouch cover
    with a standing-height end."""
    for k in range(4):
        box(g, -0.6, 0.6, -0.65, 0.65, k * 0.32, k * 0.32 + 0.06, 'WoodGrey')  # bearers
        dx, dy = rnd.uniform(-0.12, 0.12), rnd.uniform(-0.06, 0.06)
        box(g, -2.1 + dx, 2.1 + dx, -0.7 + dy, 0.7 + dy, k * 0.32 + 0.06, k * 0.32 + 0.3, 'Concrete')
    tilted(g, 1.9, 0.0, 0.0, -14, lambda q: box(q, -0.11, 0.11, -0.75, 0.75, 0.0, 2.4, 'Concrete'))
    veg.rubble(g, 0.0, 0.0, 0.0, 1.0)


@mesh('SM_Obs_ConcreteFence')
def concrete_fence(g):
    """Two sections of the Soviet diamond-relief concrete fence (PO-2 style) on posts, 2.3 m high: full cover."""
    for x0 in (-2.0, 0.02):
        box(g, x0, x0 + 1.98, -0.07, 0.07, 0.0, 2.3, 'Concrete')
        for i in range(4):
            for j in range(5):
                cx, cz = x0 + 0.25 + i * 0.5, 0.25 + j * 0.45
                for side in (-1, 1):  # the relief: a lozenge standing out of each face
                    turned(g, cx, side * 0.085, cz, 45, lambda q: box(q, -0.14, 0.14, -0.015, 0.015, -0.14, 0.14, 'Concrete'))
    for x in (-2.05, 0.0, 2.0):
        box(g, x - 0.1, x + 0.1, -0.12, 0.12, -0.2, 2.45, 'Concrete')
    veg.rubble(g, -1.0, 0.4, 0.0, 0.6)


@mesh('SM_Obs_Truck')
def truck(g):
    """Stripped GAZ-53-type truck on its rims: cab, bonnet, flatbed with dropped sides."""
    box(g, -3.0, 3.0, -0.45, 0.45, 0.35, 0.6, 'Metal')                      # chassis
    box(g, 1.6, 3.1, -1.0, 1.0, 0.6, 1.45, 'Metal')                         # bonnet
    box(g, 0.3, 1.6, -1.15, 1.15, 0.6, 2.35, 'Metal')                       # cab
    box(g, 1.55, 1.62, -1.0, 1.0, 1.55, 2.2, 'BlackPlastic')               # windscreen hole
    box(g, -3.2, 0.2, -1.2, 1.2, 0.6, 0.75, 'WoodGrey')                     # bed
    for y in (-1.2, 1.12):
        box(g, -3.2, 0.2, y, y + 0.08, 0.75, 1.35, 'WoodGrey')
    box(g, -3.2, -3.12, -1.2, 1.2, 0.75, 1.35, 'WoodGrey')
    for x in (-2.2, 2.3):
        for y in (-1.05, 0.8):
            tube(g, (x, y, 0.42), (x, y + 0.25, 0.42), 0.42, 'BlackPlastic', 12)


@mesh('SM_Obs_Bus')
def bus(g):
    """PAZ-672-type bus shell sunk on flat tyres, windows empty: full cover, can be looked through."""
    box(g, -3.6, 3.6, -1.2, 1.2, 0.3, 1.25, 'Lime')
    box(g, -3.6, 3.6, -1.2, 1.2, 2.05, 2.75, 'Lime')
    for x in range(8):  # window posts
        x0 = -3.6 + x * 1.03
        box(g, x0, x0 + 0.12, -1.2, -1.1, 1.25, 2.05, 'Metal')
        box(g, x0, x0 + 0.12, 1.1, 1.2, 1.25, 2.05, 'Metal')
    box(g, 3.5, 3.6, -1.2, 1.2, 1.25, 2.05, 'Metal')
    box(g, -3.55, 3.55, -1.15, 1.15, 0.3, 0.38, 'WoodGrey')                  # floor
    for x in (-2.4, 2.4):
        for y in (-1.2, 0.95):
            tube(g, (x, y, 0.34), (x, y + 0.25, 0.34), 0.42, 'BlackPlastic', 12)


@mesh('SM_Obs_Barricade')
def barricade(g):
    """The looters' barricade: doors, a wardrobe on its back, planks and sheet metal on a scaffold of posts, 1.8 m."""
    for x in (-1.7, 0.0, 1.7):
        box(g, x - 0.06, x + 0.06, -0.06, 0.06, -0.2, 1.9, 'WoodGrey')
    for k, x in enumerate((-1.7, -0.75, 0.25, 1.05)):
        tilted(g, x, -0.15, 0.0, rnd.uniform(-12, 12), lambda q, k=k: box(q, 0.0, 0.85, -0.03, 0.03, 0.0, 1.95,
                                                                           ('Furniture', 'Metal', 'Wood', 'Metal')[k]))
    box(g, -1.6, 0.4, 0.15, 0.75, 0.0, 0.62, 'Furniture')                       # wardrobe on its back
    for z in (0.4, 1.1, 1.6):
        box(g, -1.9, 1.9, 0.08, 0.12, z, z + 0.14, 'WoodGrey')
    for x in (0.9, 1.4):
        tube(g, (x, 0.5, 0.0), (x, 0.5, 0.22), 0.34, 'BlackPlastic', 10)          # tyres
        tube(g, (x, 0.5, 0.22), (x, 0.5, 0.44), 0.34, 'BlackPlastic', 10)


@mesh('SM_Obs_CableDrums')
def cable_drums(g):
    """Wooden cable drums from the mine stores: two upright, one on its flange, 1.8 m."""
    def drum(q):
        tube(q, (0, -0.45, 0.9), (0, -0.37, 0.9), 0.9, 'WoodGrey', 16)
        tube(q, (0, 0.37, 0.9), (0, 0.45, 0.9), 0.9, 'WoodGrey', 16)
        tube(q, (0, -0.37, 0.9), (0, 0.37, 0.9), 0.55, 'Metal', 12)            # wound cable
    turned(g, -1.0, 0.0, 0.0, 8, drum)
    turned(g, 0.95, 0.15, 0.0, -14, drum)
    tube(g, (0.1, 1.3, 0.0), (0.1, 1.3, 0.08), 0.9, 'WoodGrey', 16)            # third drum lying flat
    tube(g, (0.1, 1.3, 0.08), (0.1, 1.3, 0.7), 0.55, 'Metal', 12)
    tube(g, (0.1, 1.3, 0.7), (0.1, 1.3, 0.78), 0.9, 'WoodGrey', 16)


@mesh('SM_Obs_Scrap')
def scrap_wall(g):
    """Sheet metal propped on a scrap heap: looters' salvage, 1.7 m."""
    veg.scrap(g, 1.2)
    for k, x in enumerate((-1.6, -0.55, 0.5)):
        tilted(g, x, 0.0, 0.0, rnd.uniform(-10, 10), lambda q: box(q, 0.0, 1.05, -0.02, 0.02, 0.0, rnd.uniform(1.4, 1.8), 'Metal'))
    box(g, -1.7, 1.6, 0.1, 0.16, 0.5, 0.58, 'Metal')                           # rail holding the sheets
    tube(g, (-1.2, 0.8, 0.29), (-1.2, 0.8, 1.17), 0.29, 'Metal', 12)           # barrel


# --- pickups and task props --------------------------------------------------------------------------------------
@mesh('SM_Shooter_Bandage')
def bandage(g):
    box(g, -0.1, 0.1, -0.06, 0.06, 0.0, 0.08, 'Paper')
    box(g, -0.02, 0.02, -0.061, 0.061, 0.0, 0.081, 'CurtainRed')


@mesh('SM_Shooter_Medkit')
def medkit(g):
    box(g, -0.2, 0.2, -0.13, 0.13, 0.0, 0.15, 'Enamel')
    box(g, -0.025, 0.025, -0.08, 0.08, 0.15, 0.155, 'CurtainRed')
    box(g, -0.08, 0.08, -0.025, 0.025, 0.15, 0.155, 'CurtainRed')
    box(g, -0.06, 0.06, -0.02, 0.02, 0.155, 0.19, 'Metal')                     # handle


@mesh('SM_Shooter_Ammo')
def ammo(g):
    box(g, -0.18, 0.18, -0.09, 0.09, 0.0, 0.2, 'Metal')
    box(g, -0.19, 0.19, -0.1, 0.1, 0.2, 0.23, 'Metal')
    box(g, -0.06, 0.06, -0.015, 0.015, 0.23, 0.26, 'BlackPlastic')


@mesh('SM_Shooter_Vest')
def vest(g):
    box(g, -0.27, 0.27, -0.2, 0.2, 0.0, 0.06, 'Sofa')
    for y in (-0.2, 0.16):
        box(g, -0.24, 0.24, y, y + 0.04, 0.06, 0.08, 'BlackPlastic')


@mesh('SM_Shooter_Radio')
def radio(g):
    box(g, -0.15, 0.15, -0.07, 0.07, 0.0, 0.24, 'BlackPlastic')
    box(g, -0.12, 0.12, -0.071, -0.06, 0.13, 0.21, 'Metal')                    # front panel
    tube(g, (0.1, 0.0, 0.24), (0.1, 0.0, 0.62), 0.006, 'Metal', 4)


@mesh('SM_Shooter_Documents')
def documents(g):
    box(g, -0.15, 0.15, -0.11, 0.11, 0.0, 0.03, 'Paper')
    turned(g, 0.03, 0.02, 0.03, 18, lambda q: box(q, -0.2, 0.2, -0.14, 0.14, 0.0, 0.004, 'Paper'))


@mesh('SM_Shooter_Jammer')
def jammer(g):
    box(g, -0.2, 0.2, -0.12, 0.12, 0.0, 0.18, 'Metal')
    for y in (-0.08, 0.08):
        tube(g, (0.12, y, 0.18), (0.12, y, 0.75), 0.008, 'Metal', 4)
    box(g, -0.15, -0.05, -0.121, -0.11, 0.08, 0.13, 'CurtainRed')               # tell-tale lamp


@mesh('SM_Shooter_Workbench')
def workbench(g):
    """Looters' workshop: bench with a half-built drone, gas bottles, cable."""
    for x in (-0.9, 0.85):
        for y in (-0.35, 0.3):
            box(g, x, x + 0.05, y, y + 0.05, 0.0, 0.85, 'Metal')
    box(g, -0.95, 0.95, -0.4, 0.4, 0.85, 0.9, 'WoodGrey')
    box(g, -0.5, 0.2, -0.25, 0.2, 0.9, 1.1, 'Metal')                          # drone chassis being built
    for y in (-0.3, 0.25):
        box(g, -0.55, 0.25, y, y + 0.06, 0.9, 1.02, 'BlackPlastic')
    for x in (1.15, 1.45):
        tube(g, (x, 0.0, 0.0), (x, 0.0, 1.3), 0.12, 'Enamel', 12)               # gas bottles
    tube(g, (0.4, -0.2, 0.9), (0.75, 0.2, 0.92), 0.02, 'BlackPlastic', 6)


# --- weapons and machines ----------------------------------------------------------------------------------------
@mesh('SM_Shooter_Rifle')
def rifle(g):
    """Kalashnikov-pattern rifle, origin at the pistol grip, barrel along +X (first person and the looters)."""
    box(g, -0.1, 0.3, -0.022, 0.022, 0.0, 0.09, 'Metal')                     # receiver
    box(g, 0.3, 0.5, -0.025, 0.025, 0.01, 0.07, 'Furniture')                  # handguard
    tube(g, (0.5, 0.0, 0.05), (0.78, 0.0, 0.05), 0.011, 'Metal', 8)            # barrel
    box(g, 0.74, 0.79, -0.012, 0.012, 0.05, 0.09, 'Metal')                    # front sight
    box(g, 0.32, 0.5, -0.016, 0.016, 0.07, 0.1, 'Furniture')                  # gas tube cover
    for k in range(4):                                                        # curved magazine
        a = math.radians(14 * k)
        x, z = 0.16 + 0.07 * k, -0.04 - 0.06 * k * math.cos(a)
        box(g, x - 0.035, x + 0.035, -0.016, 0.016, z - 0.05, z + 0.01, 'Metal')
    tilted(g, -0.02, 0.0, 0.0, 18, lambda q: box(q, -0.03, 0.01, -0.016, 0.016, -0.13, 0.0, 'Furniture'))   # grip
    box(g, -0.42, -0.1, -0.02, 0.02, -0.04, 0.07, 'Furniture')                # stock


@mesh('SM_Shooter_TurretBase')
def turret_base(g):
    """Tripod from mine survey gear with a car battery: the head pivots 1.25 m up."""
    for a in (0, 120, 240):
        r = math.radians(a)
        tube(g, (0.0, 0.0, 1.15), (0.85 * math.cos(r), 0.85 * math.sin(r), 0.0), 0.03, 'Metal', 6)
    box(g, -0.12, 0.12, -0.12, 0.12, 1.1, 1.2, 'Metal')
    box(g, -0.55, -0.25, 0.2, 0.45, 0.0, 0.22, 'BlackPlastic')                # battery
    tube(g, (-0.4, 0.32, 0.22), (0.0, 0.0, 1.15), 0.012, 'BlackPlastic', 4)  # cable


@mesh('SM_Shooter_TurretHead')
def turret_head(g):
    """Machine gun with ammo can and a mine searchlight strapped on; origin at the pivot, barrel along +X."""
    box(g, -0.35, 0.35, -0.07, 0.07, 0.0, 0.16, 'Metal')
    tube(g, (0.35, 0.0, 0.08), (0.95, 0.0, 0.08), 0.02, 'Metal', 8)
    box(g, -0.2, 0.1, 0.07, 0.25, -0.05, 0.14, 'Metal')                       # ammo can
    tube(g, (0.0, -0.18, 0.24), (0.3, -0.18, 0.24), 0.09, 'BlackPlastic', 12)  # searchlight
    box(g, -0.05, 0.05, -0.12, -0.06, 0.14, 0.2, 'Metal')


@mesh('SM_Shooter_Drone')
def drone(g):
    """Tracked mine inspection crawler turned into a gun platform; origin on the ground, front along +X."""
    for y in (-0.36, 0.22):                                                    # tracks
        box(g, -0.45, 0.45, y, y + 0.14, 0.03, 0.22, 'BlackPlastic')
        for x in (-0.38, 0.38):
            tube(g, (x, y, 0.13), (x, y + 0.14, 0.13), 0.11, 'BlackPlastic', 10)
    box(g, -0.4, 0.4, -0.22, 0.22, 0.12, 0.38, 'Metal')                       # hull
    box(g, -0.3, 0.1, -0.15, 0.15, 0.38, 0.48, 'Metal')
    tube(g, (-0.2, 0.0, 0.48), (-0.2, 0.0, 0.85), 0.02, 'Metal', 6)          # camera mast
    box(g, -0.26, -0.12, -0.06, 0.06, 0.85, 0.95, 'BlackPlastic')
    box(g, 0.0, 0.3, -0.05, 0.05, 0.4, 0.5, 'Metal')                          # gun
    tube(g, (0.3, 0.0, 0.45), (0.62, 0.0, 0.45), 0.012, 'Metal', 6)
    tube(g, (0.4, 0.15, 0.3), (0.46, 0.15, 0.3), 0.05, 'Enamel', 10)          # mine lamp


(root / 'assets/shooter/meshes.json').write_text(json.dumps(built, indent=1))
print('SHOOTER MESHES OK', len(built), sum(m['quads'] for m in built.values()))
