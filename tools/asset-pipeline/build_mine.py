"""Blender CLI: Stollen 3 (Nordhang), the adit at the end of the story path (FIKTION; layout ANNAHME after typical
Kolyma coal adits): concrete portal with retaining walls in the cutting, a barred gate standing open, 52 m of drift
with timber sets and then steel arches, narrow-gauge track out to the waste heap, mine cars, lamp house, power poles.
The drift ends in a fall of rock - the story's finale place (empty board brackets and Pjotr's note before it).

Run: blender --background --factory-startup --python tools/asset-pipeline/build_mine.py -- <project root>
Reads assets/mine/adit_site.json and terrain_adit_patch.obj (tools/research/mine_site.py); writes
assets/mine/SM_Mine_Adit.fbx. Mesh space like the vegetation cells: Blender x = north, y = -east, z = metres above
the origin height, relative to the portal; the actor sits at the portal with yaw 0.
"""
import json, math, os, random, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_vegetation as veg  # noqa: E402  (Geo, pbox, prism, rock, rebar, hut, pole, export)

ROOT = sys.argv[sys.argv.index("--") + 1]
SRC = os.path.join(ROOT, "assets/mine")
veg.rnd = random.Random(1952)
rnd = veg.rnd
SITE = json.load(open(os.path.join(SRC, "adit_site.json")))
PE, PN = SITE["portal"]
UX, UY = SITE["uphill"]
F = SITE["floor_m"]
HW = SITE["half_width_m"]
DRIFT = 52.0          # drift length from the portal face
ROCK = "Rock"


def load_patch():
    vs = [tuple(float(c) / 100.0 for c in l.split()[1:4]) for l in open(os.path.join(SRC, "terrain_adit_patch.obj")) if l.startswith("v ")]
    m = int(round(math.sqrt(len(vs))))
    return vs, m


PATCH, PM = load_patch()
PSTEP = PATCH[1][0] - PATCH[0][0]


def ground_uv(u, v):
    """Carved terrain height at local (u along the drift, v to the left), bilinear on the 0.5 m patch."""
    x, y = PE + UX * u - UY * v, PN + UY * u + UX * v
    fi = min(max((x - PATCH[0][0]) / PSTEP, 0.0), PM - 1.001)
    fj = min(max((y - PATCH[0][1]) / PSTEP, 0.0), PM - 1.001)
    i, j = int(fi), int(fj)
    a, b = fi - i, fj - j
    z = lambda ii, jj: PATCH[jj * PM + ii][2]
    return (z(i, j) * (1 - a) + z(i + 1, j) * a) * (1 - b) + (z(i, j + 1) * (1 - a) + z(i + 1, j + 1) * a) * b


def both(g, pts, mat):
    """Quad visible from both sides (rock shell of the drift: seen from inside, sealed from outside)."""
    g.quad(pts, veg._uv(pts), mat)
    g.quad(pts[::-1], veg._uv(pts[::-1]), mat)


def portal(t):
    # the block reaches 2.4 m into the hill: it covers the hole mine_site.py leaves in the terrain at the drift mouth
    w, top, back = HW + 0.6, F + 6.2, 2.4
    veg.pbox(t, -0.8, back, -w, -1.7, F - 0.3, top, "Concrete")          # piers
    veg.pbox(t, -0.8, back, 1.7, w, F - 0.3, top, "Concrete")
    veg.pbox(t, -0.8, back, -1.7, 1.7, F + 3.45, top, "Concrete")        # lintel
    for z0, z1, hw in ((F + 2.8, F + 3.1, 1.55), (F + 3.1, F + 3.3, 1.3), (F + 3.3, F + 3.45, 0.9)):  # stepped arch
        veg.pbox(t, -0.8, back, -1.7, -hw, z0, z1, "Concrete")
        veg.pbox(t, -0.8, back, hw, 1.7, z0, z1, "Concrete")
    veg.pbox(t, -1.05, back, -w - 0.25, w + 0.25, top, top + 0.28, "Concrete")   # cornice
    veg.pbox(t, -0.95, -0.8, -1.3, 1.3, F + 4.1, F + 4.9, "Wood")             # name board (lettering gone)
    for v in (-1.1, 1.1):
        veg.pbox(t, -0.97, -0.95, v - 0.05, v + 0.05, F + 4.2, F + 4.8, "Metal")
    # retaining walls along the cutting, stepped to the natural ground (mine_site.py wall_tops)
    for side, row in zip((-1, 1), SITE["wall_tops"]):
        # one sloped wall following the ground line (stepped 1 m boxes read as a sawtooth, user 2026-11-08),
        # running out to the trench floor 2 m after the last sample
        pts = row + ([[row[-1][0] - 2.0, F]] if row else [])
        y0, y1 = (HW, HW + 0.6) if side > 0 else (-HW - 0.6, -HW)
        c0, c1 = (HW - 0.05, HW + 0.65) if side > 0 else (-HW - 0.65, -HW + 0.05)
        for (ua, ha), (ub, hb) in zip(pts, pts[1:]):
            wedge(t, ub, ua, y0, y1, F - 0.3, F - 0.3, hb + 0.35, ha + 0.35, "Concrete")
            wedge(t, ub, ua, c0, c1, hb + 0.35, ha + 0.35, hb + 0.45, ha + 0.45, "Concrete")  # coping
    # gate: steel bars, the left leaf shut, the right leaf standing open (its padlock gone, see Orlow's key board)
    for k in range(12):
        v = -1.65 + k * 0.14
        veg.prism(t, (-0.95, v, F), (-0.95, v, F + 2.75), 0.016, "Metal", 4)
    for z in (F + 0.15, F + 1.4, F + 2.7):
        veg.prism(t, (-0.95, -1.7, z), (-0.95, 0.0, z), 0.02, "Metal", 4)
    a = math.radians(-70)
    for k in range(12):
        d = 0.14 * (k + 1)
        x, y = -0.95 + math.sin(-a) * -d, 1.7 - math.cos(a) * d
        veg.prism(t, (x, y, F), (x, y, F + 2.75), 0.016, "Metal", 4)
    for z in (F + 0.15, F + 1.4, F + 2.7):
        veg.prism(t, (-0.95, 1.7, z), (-0.95 + math.sin(-a) * -1.7, 1.7 - math.cos(a) * 1.7, z), 0.02, "Metal", 4)


def wedge(t, x0, x1, y0, y1, b0, b1, t0, t1, mat):
    """Box from x0 to x1 with sloped bottom (b0 -> b1) and top (t0 -> t1) along x."""
    v = [(x0, y0, b0), (x1, y0, b1), (x1, y1, b1), (x0, y1, b0), (x0, y0, t0), (x1, y0, t1), (x1, y1, t1), (x0, y1, t0)]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        pts = [v[i] for i in f]
        t.quad(pts, veg._uv(pts), mat)


def drift(t):
    """Rock shell (irregular rings every 1.5 m), floor, timber sets for 8 m, steel arches after, cable, fall of rock."""
    prof = [(-1.5, -0.05), (-1.75, 1.5), (-1.45, 2.85), (-0.65, 3.4), (0.65, 3.4), (1.45, 2.85), (1.75, 1.5), (1.5, -0.05)]
    rings, u = [], 0.6
    while u <= DRIFT + 0.01:
        j = 0.0 if u < 1.0 else 0.13
        rings.append([(u, v + rnd.uniform(-j, j), F + z + rnd.uniform(-j, j)) for v, z in prof])
        u += 1.5
    for r0, r1 in zip(rings, rings[1:]):
        for k in range(len(prof) - 1):
            both(t, [r0[k], r0[k + 1], r1[k + 1], r1[k]], ROCK)
    end = rings[-1]
    for k in range(1, len(prof) - 2):
        both(t, [end[0], end[k], end[k + 1], end[k + 1]], ROCK)
    # floor up to just under the rail heads (mud and ballast): rails 17 cm proud stopped the player (walk check)
    veg.pbox(t, -0.9, DRIFT, -1.55, 1.55, F - 0.3, F + 0.12, ROCK)
    u = 1.0
    while u < 8.0:                                                                         # timber sets + lagging
        for v in (-1.35, 1.15):
            veg.pbox(t, u, u + 0.2, v, v + 0.2, F, F + 2.9, "Wood")
        veg.pbox(t, u - 0.05, u + 0.25, -1.5, 1.5, F + 2.9, F + 3.1, "Wood")
        u += 1.0
    for k in range(int(7.0 / 0.25)):
        uu = 1.0 + k * 0.25
        veg.pbox(t, uu, uu + 0.2, -1.4, 1.4, F + 3.1, F + 3.16, "WoodGrey")
    u = 8.6
    while u < DRIFT - 7.0:                                                                  # steel arches (TH profile)
        pts = [(-1.4, 0.0), (-1.4, 2.0)] + [(-1.4 * math.cos(a), 2.0 + 1.2 * math.sin(a)) for a in (0.5, 1.0, 1.5708, 2.14, 2.64)] + [(1.4, 2.0), (1.4, 0.0)]
        for (v0, z0), (v1, z1) in zip(pts, pts[1:]):
            veg.prism(t, (u, v0, F + z0), (u, v1, F + z1), 0.06, "Metal", 5)
        if rnd.random() < 0.6:                                                              # tie bars
            for v in (-1.4, 1.4):
                veg.prism(t, (u, v, F + 1.6), (u + 1.2, v, F + 1.6), 0.025, "Metal", 4)
        u += 1.2
    veg.prism(t, (0.6, 1.55, F + 2.25), (DRIFT - 7, 1.55, F + 2.25), 0.03, "BlackPlastic", 5)   # power cable
    for k in range(int((DRIFT - 8) / 3)):
        veg.pbox(t, 1.0 + k * 3, 1.03 + k * 3, 1.5, 1.6, F + 2.2, F + 2.35, "Metal")
    for _ in range(70):                                                                    # the fall of rock
        u = rnd.uniform(DRIFT - 8, DRIFT)
        hgt = 3.2 * min(1.0, (u - (DRIFT - 8)) / 4.0)
        veg.rock(t, u, rnd.uniform(-1.5, 1.5), F + rnd.uniform(0, hgt), rnd.uniform(0.4, 1.3), rnd.uniform(0.4, 1.1), rnd.uniform(0.3, 0.9), ROCK)
    for k in range(3):                                                                    # broken arch in the fall
        veg.prism(t, (DRIFT - 6.5 + k * 0.8, -1.3, F + 0.3), (DRIFT - 6.0 + k * 0.8, 0.9, F + 1.4 + k * 0.3), 0.06, "Metal", 5)
    # the finale place (design/narrative/story-places.md, proposal Under Review): on the left wall the two brackets of
    # the brigade's honour board, empty, a clean rectangle where it hung; on a crate before the fall Pjotr's note under
    # his helmet lamp
    for zz in (F + 1.25, F + 2.05):
        for uu in (41.7, 43.1):
            veg.pbox(t, uu, uu + 0.08, 1.38, 1.5, zz, zz + 0.06, "Metal")
    veg.pbox(t, 41.6, 43.3, 1.47, 1.5, F + 1.2, F + 2.15, "Concrete")
    veg.pbox(t, 41.6, 42.4, -1.3, -0.7, F + 0.12, F + 0.55, "Wood")
    # the field telephone Pjotr ran from the boiler house; its cable runs on into the fall (story_data: radio log)
    veg.pbox(t, 42.12, 42.34, -1.2, -0.98, F + 0.55, F + 0.68, "BlackPlastic")
    veg.prism(t, (42.3, -1.0, F + 0.6), (43.6, -0.6, F + 0.2), 0.008, "BlackPlastic", 3)
    veg.prism(t, (0.6, -1.4, F + 0.15), (42.15, -1.15, F + 0.6), 0.008, "BlackPlastic", 3)
    # his note on the crate (story picture, corners counter-clockwise from above: not mirrored)
    pts = [(41.7, -1.2, F + 0.553), (42.08, -1.2, F + 0.553), (42.08, -0.82, F + 0.553), (41.7, -0.82, F + 0.553)]
    t.quad(pts, [(0, 0), (1, 0), (1, 1), (0, 1)], "Pic_NoteMine")
    # the ventilation raise on the right wall, the way out: timber frame, a black void behind it, ladder rungs going
    # up, coal-dust hand prints on the posts
    u0, u1 = 37.6, 38.8
    for uu in (u0, u1 - 0.14):
        veg.pbox(t, uu, uu + 0.14, -1.5, -1.32, F, F + 1.95, "Wood")
    veg.pbox(t, u0, u1, -1.5, -1.32, F + 1.95, F + 2.12, "Wood")
    veg.pbox(t, u0 + 0.14, u1 - 0.14, -1.95, -1.55, F, F + 1.95, "BlackPlastic")
    for k in range(7):
        veg.pbox(t, u0 + 0.25, u1 - 0.25, -1.62, -1.58, F + 0.3 + k * 0.28, F + 0.33 + k * 0.28, "Metal")
    for k in range(4):
        veg.pbox(t, u0 + 0.02, u0 + 0.12, -1.32, -1.318, F + 0.9 + k * 0.22, F + 1.0 + k * 0.22, "BlackPlastic")


def track(t, u0, u1):
    """600 mm narrow-gauge track on sleepers, following the floor inside and the cut ground outside."""
    u = u0
    while u < u1:
        z0 = F if u > 0 else ground_uv(u, 0.0)
        z1 = F if u + 1 > 0 else ground_uv(u + 1, 0.0)
        for v in (-0.3, 0.3):
            veg.prism(t, (u, v, z0 + 0.14), (u + 1.0, v, z1 + 0.14), 0.035, "Metal", 4)
        if rnd.random() < 0.85:
            veg.pbox(t, u + 0.3, u + 0.45, -0.55, 0.55, z0 - 0.02, z0 + 0.1, "WoodGrey")
        if u < -0.9:  # ballast bed outside, level with the drift floor inside
            veg.pbox(t, u, u + 1.0, -0.75, 0.75, min(z0, z1) - 0.25, (z0 + z1) / 2 + 0.12, ROCK)
        u += 1.0


def mine_car(t, u, v, z, tipped=False):
    """V-shaped side-tipping mine car (вагонетка) on its frame; tipped = lying on its side by the heap."""
    if tipped:
        veg.rock(t, u, v, z + 0.45, 1.6, 0.8, 0.9, "Metal", tilt=1.2, jitter=0.04)
        return
    veg.pbox(t, u - 0.7, u + 0.7, v - 0.35, v + 0.35, z + 0.25, z + 0.4, "Metal")         # frame
    for k in range(4):                                                                     # body, widening upward
        hw = 0.35 + k * 0.08
        veg.pbox(t, u - 0.8, u + 0.8, v - hw, v + hw, z + 0.4 + k * 0.15, z + 0.55 + k * 0.15, "Metal")
    for du in (-0.45, 0.45):
        for dv in (-0.3, 0.3):
            veg.prism(t, (u + du, v + dv - 0.04, z + 0.17), (u + du, v + dv + 0.04, z + 0.17), 0.16, "Metal", 8)


def heap(t, uc, vc, r, h):
    """Waste heap (отвал): rough cone of rock rings, boulders on the flanks."""
    gz = ground_uv(uc, vc)
    rings = []
    for k in range(7):
        rr, zz = r * (1 - k / 7.0), gz - 0.5 + h * (k / 7.0) ** 0.8
        rings.append([(uc + rr * math.cos(a) * rnd.uniform(0.85, 1.1), vc + rr * math.sin(a) * rnd.uniform(0.85, 1.1), zz + rnd.uniform(-0.3, 0.3))
                      for a in (2 * math.pi * i / 18 for i in range(18))])
    top = (uc, vc, gz + h)
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(18):
            pts = [r0[i], r0[(i + 1) % 18], r1[(i + 1) % 18], r1[i]]
            both(t, pts, ROCK)
    for i in range(18):
        pts = [rings[-1][i], rings[-1][(i + 1) % 18], top, top]
        both(t, pts, ROCK)
    for _ in range(60):
        a, d = rnd.uniform(0, 2 * math.pi), r * rnd.uniform(0.3, 1.05)
        zz = ground_uv(uc + d * math.cos(a), vc + d * math.sin(a)) if d > r * 0.95 else gz + h * (1 - d / r) * 0.9
        veg.rock(t, uc + d * math.cos(a), vc + d * math.sin(a), zz, rnd.uniform(0.3, 1.2), rnd.uniform(0.3, 1.0), rnd.uniform(0.2, 0.7), ROCK)


def site(t):
    portal(t)
    drift(t)
    track(t, -44.0, DRIFT - 9)
    mine_car(t, 18.0, 0.0, F + 0.1)
    mine_car(t, -9.0, 0.0, ground_uv(-9.0, 0.0))
    mine_car(t, -44.0, 2.5, ground_uv(-44.0, 2.5), tipped=True)
    heap(t, -55.0, 6.0, 13.0, 6.0)
    lamp = veg.Geo()
    veg.hut(lamp)
    t.append(lamp, -16.0, 9.0, ground_uv(-16.0, 9.0), math.radians(90), 1.0)               # lamp house (ламповая)
    for k, u in enumerate((-20.0, -55.0, -90.0)):                                         # power line down to the valley
        p = veg.Geo()
        veg.pole(p)
        t.append(p, u, -8.0, ground_uv(u, -8.0) if u > -75 else ground_uv(-75, -8.0), 0.0, 1.0)
    for (u0, u1) in ((-20.0, -55.0), (-55.0, -90.0)):
        z0, z1 = ground_uv(u0, -8.0), ground_uv(u1 if u1 > -75 else -75, -8.0)
        for v in (-8.8, -8.3, -7.7, -7.2):
            veg.prism(t, (u0, v, z0 + 8.15), (u1, v, z1 + 8.15), 0.008, "Metal", 3)
    veg.prism(t, (-20.0, -8.3, ground_uv(-20.0, -8.0) + 8.1), (-0.9, -4.0, F + 5.5), 0.012, "Metal", 3)   # feed to the portal
    for _ in range(30):                                                                     # rubble in the cutting
        u, v = rnd.uniform(-12, -1), rnd.choice((-1, 1)) * rnd.uniform(2.5, 3.9)
        veg.rock(t, u, v, F, rnd.uniform(0.2, 0.7), rnd.uniform(0.2, 0.6), rnd.uniform(0.15, 0.5), ROCK)


def main():
    veg.bpy.ops.wm.read_factory_settings(use_empty=True)
    local = veg.Geo()
    site(local)
    g = veg.Geo()
    # local (u, v) -> Blender (north, -east): u along (UX east, UY north), v to its left (-UY east, UX north)
    yaw = math.atan2(-UX, UY)
    g.append(local, 0.0, 0.0, 0.0, yaw, 1.0)
    veg.SRC = SRC
    veg.export("SM_Mine_Adit", g)
    # interactive finds (tools/research/story_data.py): local (u along the drift, v to the left, z world metres)
    world = lambda u, v, z: [round(PN + UY * u + UX * v, 3), round(PE + UX * u - UY * v, 3), round(z, 3)]
    clues = {"mine_gate": world(-0.95, 1.0, F + 1.4), "mine_board": world(42.4, 1.45, F + 1.65),
             "mine_vent": world(38.2, -1.4, F + 1.2), "mine_note": world(41.89, -1.01, F + 0.56)}
    json.dump({"mesh": "SM_Mine_Adit", "north_m": PN, "east_m": PE, "quads": len(g.f), "materials": g.mats, "clues": clues},
              open(os.path.join(SRC, "mine_manifest.json"), "w"), indent=1)
    print("MINE OK quads=%d materials=%s" % (len(g.f), g.mats))


main()
