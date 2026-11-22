"""Blender CLI: procedural trees and bushes as instanced prototypes, grass and props merged per 600 m cell.

Run: blender --background --factory-startup --python tools/asset-pipeline/build_vegetation.py -- <project root>
Reads assets/vegetation/scatter.json (tools/research/scatter_vegetation.py), writes
assets/vegetation/SM_Veg_<i>_<j>.fbx (grass), SM_Props_<i>_<j>.fbx, SM_Tree_<kind>_<k>_LOD<l>.fbx (prototypes with three
levels of detail), Content/Kadykchan/Data/Foliage/<kind>_<k>.txt (instances, read by AKdkFoliageField) and veg_manifest.json.

Trees are a tapered trunk plus alpha-masked leaf cards (art bible 8.7: vegetation as cards, no Nanite
until Nanite foliage is verified for 5.8). Cell meshes are built with Blender x = north, y = -east,
because the FBX import negates Y; the actor then sits at the cell centre with yaw 0.
"""
import json, math, os, random, sys
import bpy

ROOT = sys.argv[sys.argv.index("--") + 1]
SRC = os.path.join(ROOT, "assets/vegetation")
CELL = 600.0  # ~150 cells for the 8 km terrain; one draw-call group per cell
rnd = random.Random(1943)


class Geo:
    def __init__(self):
        self.v, self.f, self.uv, self.mat, self.mats = [], [], [], [], []

    def _m(self, name):
        if name not in self.mats:
            self.mats.append(name)
        return self.mats.index(name)

    def quad(self, pts, uvs, mat):
        b = len(self.v)
        self.v += pts
        self.f.append((b, b + 1, b + 2, b + 3))
        self.uv.append(uvs)
        self.mat.append(self._m(mat))

    def trunk(self, h, r0, r1, mat, sides=7):
        for k in range(sides):
            a0, a1 = 2 * math.pi * k / sides, 2 * math.pi * (k + 1) / sides
            pts = [(r0 * math.cos(a0), r0 * math.sin(a0), -0.3), (r0 * math.cos(a1), r0 * math.sin(a1), -0.3),
                   (r1 * math.cos(a1), r1 * math.sin(a1), h), (r1 * math.cos(a0), r1 * math.sin(a0), h)]
            u0, u1 = k / sides * 0.6, (k + 1) / sides * 0.6
            self.quad(pts, [(u0, 0), (u1, 0), (u1, h / 2), (u0, h / 2)], mat)

    def card(self, cx, cy, cz, size, mat):
        # random orientation; two-sided material, so one quad per card
        yaw, tilt = rnd.uniform(0, math.pi), rnd.uniform(-0.6, 0.6)
        ux, uy, uz = math.cos(yaw) * size / 2, math.sin(yaw) * size / 2, 0.0
        vx, vy, vz = -math.sin(yaw) * math.sin(tilt) * size / 2, math.cos(yaw) * math.sin(tilt) * size / 2, math.cos(tilt) * size / 2
        pts = [(cx - ux - vx, cy - uy - vy, cz - uz - vz), (cx + ux - vx, cy + uy - vy, cz + uz - vz),
               (cx + ux + vx, cy + uy + vy, cz + uz + vz), (cx - ux + vx, cy - uy + vy, cz - uz + vz)]
        self.quad(pts, [(0, 0), (1, 0), (1, 1), (0, 1)], mat)

    def append(self, other, x, y, z, yaw, s):
        c, si = math.cos(yaw), math.sin(yaw)
        b = len(self.v)
        self.v += [(x + (px * c - py * si) * s, y + (px * si + py * c) * s, z + pz * s) for px, py, pz in other.v]
        for f, uv, m in zip(other.f, other.uv, other.mat):
            self.f.append(tuple(b + i for i in f))
            self.uv.append(uv)
            self.mat.append(self._m(other.mats[m]))


def _uv(pts):
    """Box-projected UVs in metres / 2 (art bible 8.4 texel density) on the quad's dominant axis."""
    (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = pts[0], pts[1], pts[2]
    nx, ny, nz = (y1 - y0) * (z2 - z0) - (z1 - z0) * (y2 - y0), (z1 - z0) * (x2 - x0) - (x1 - x0) * (z2 - z0), (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
    ax = max(range(3), key=lambda i: abs((nx, ny, nz)[i]))
    return [tuple(c * 0.5 for c in ((p[1], p[2]), (p[0], p[2]), (p[0], p[1]))[ax]) for p in pts]


def pbox(g, x0, x1, y0, y1, z0, z1, mat):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        pts = [v[i] for i in f]
        g.quad(pts, _uv(pts), mat)


def prism(g, a, b, r, mat, sides=8):
    """Closed-enough tube from a to b (pipes): side quads only, ends are hidden by supports or the ground."""
    dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
    l = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
    t = (dx / l, dy / l, dz / l)
    u = (-t[1], t[0], 0.0) if abs(t[2]) < 0.9 else (1.0, 0.0, 0.0)
    ul = math.sqrt(sum(c * c for c in u)); u = tuple(c / ul for c in u)
    w = (t[1] * u[2] - t[2] * u[1], t[2] * u[0] - t[0] * u[2], t[0] * u[1] - t[1] * u[0])
    ring = lambda p, k: tuple(p[i] + r * (math.cos(2 * math.pi * k / sides) * u[i] + math.sin(2 * math.pi * k / sides) * w[i]) for i in range(3))
    for k in range(sides):
        pts = [ring(a, k), ring(a, k + 1), ring(b, k + 1), ring(b, k)]
        g.quad(pts, [(k / sides, 0), ((k + 1) / sides, 0), ((k + 1) / sides, l / 2), (k / sides, l / 2)], mat)


def rock(g, x, y, z, sx, sy, sz, mat, tilt=0.35, jitter=0.25):
    """Irregular chunk: a box with every corner pushed in or out and the whole thing tipped over - broken concrete
    and stone instead of clean blocks (user 2026-11-08: "nicht einfach nur alles viereckig")."""
    yaw, pitch, roll = rnd.uniform(0, 2 * math.pi), rnd.uniform(-tilt, tilt), rnd.uniform(-tilt, tilt)
    cy_, sy_, cp, sp, cr, sr = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch), math.cos(roll), math.sin(roll)
    def tf(px, py, pz):
        py, pz = py * cr - pz * sr, py * sr + pz * cr          # roll about x
        px, pz = px * cp + pz * sp, -px * sp + pz * cp          # pitch about y
        return (x + px * cy_ - py * sy_, y + px * sy_ + py * cy_, z + pz)
    v = []
    for dz in (0, 1):
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            j = lambda: rnd.uniform(1 - jitter, 1 + jitter * 0.4)
            v.append(tf(dx * sx / 2 * j(), dy * sy / 2 * j(), (dz - 0.3) * sz * j()))
    for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        pts = [v[i] for i in f]
        g.quad(pts, _uv(pts), mat)


def rebar(g, x, y, z, n=3):
    """Bent reinforcing bars sticking out of broken concrete."""
    for _ in range(n):
        a, L = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.4, 1.4)
        mid = (x + math.cos(a) * L * 0.4, y + math.sin(a) * L * 0.4, z + rnd.uniform(0.2, 0.6))
        end = (mid[0] + math.cos(a + rnd.uniform(-1, 1)) * L * 0.6, mid[1] + math.sin(a + rnd.uniform(-1, 1)) * L * 0.6, mid[2] + rnd.uniform(-0.3, 0.3))
        prism(g, (x, y, z), mid, 0.012, "Metal", 4)
        prism(g, mid, end, 0.012, "Metal", 4)


def panel(g, x0, x1, y0, y1, z0, z1, mat, window):
    """Wall panel, optionally with a window hole (sill, lintel and two piers around it)."""
    if not window:
        pbox(g, x0, x1, y0, y1, z0, z1, mat)
        return
    w = x1 - x0
    pbox(g, x0, x1, y0, y1, z0, z0 + 0.85, mat)
    pbox(g, x0, x1, y0, y1, z0 + 2.3, z1, mat)
    pbox(g, x0, x0 + w * 0.27, y0, y1, z0 + 0.85, z0 + 2.3, mat)
    pbox(g, x1 - w * 0.27, x1, y0, y1, z0 + 0.85, z0 + 2.3, mat)


def panel_ruin(t, s):
    """What is left of a demolished or collapsed panel block: wall panels standing to one or two storeys at one end,
    stepping down to stubs, floor slabs tipped into the rubble, a long heap of panels and plaster with rebar."""
    L, D, AX, ST = 3.0 * rnd.randint(5, 9), 11.0, 3.0, 2.8
    n = int(L / AX)
    keep = rnd.uniform(0.3, 0.7)                     # where the standing part ends
    for k in range(n):
        f = k / n
        storeys = 2 if f < keep * 0.6 else (1 if f < keep else 0)
        for y0 in (0.0, D - 0.25):
            for st in range(storeys):
                if rnd.random() < 0.15:
                    continue
                panel(t, k * AX + 0.02, (k + 1) * AX - 0.02, y0, y0 + 0.25, st * ST, (st + 1) * ST - 0.02,
                      "Lime" if y0 == 0.0 else "Concrete", window=rnd.random() < 0.75)
            if storeys == 0 and rnd.random() < 0.6:  # stub of a broken panel
                rock(t, k * AX + 1.5, y0 + 0.12, 0.0, AX * rnd.uniform(0.4, 0.9), 0.25, rnd.uniform(0.4, 1.2), "Lime", tilt=0.15, jitter=0.15)
        if 0 < storeys and rnd.random() < 0.7:     # floor slab still spanning
            pbox(t, k * AX, (k + 1) * AX, 0.25, D - 0.25, storeys * ST - 0.22, storeys * ST, "Concrete")
    for x0 in (0.0, L - 0.25):                       # gable walls: the standing end keeps its gable
        if x0 == 0.0:
            for st in range(2):
                pbox(t, x0, x0 + 0.25, 0.0, D, st * ST, (st + 1) * ST - 0.02, "Lime")
    pbox(t, -0.3, L * keep + 0.3, -0.3, D + 0.3, -1.5, 0.05, "Concrete")  # strip foundation, shows on slopes instead of a gap
    hx0 = L * keep
    for _ in range(int(40 * s)):                     # the collapsed part: slabs at angles, chunks, rebar
        x, y = rnd.uniform(hx0 - 2, L + 2), rnd.uniform(-2, D + 2)
        hgt = max(0.0, 1.8 * (1 - abs(y - D / 2) / (D / 2 + 2)))
        if rnd.random() < 0.45:
            rock(t, x, y, rnd.uniform(0, hgt), rnd.uniform(1.5, 3.0), rnd.uniform(1.0, 2.8), 0.22, rnd.choice(("Concrete", "Lime")), tilt=0.7, jitter=0.08)
        else:
            rock(t, x, y, rnd.uniform(0, hgt), rnd.uniform(0.3, 1.0), rnd.uniform(0.3, 0.9), rnd.uniform(0.2, 0.6), rnd.choice(("Concrete", "Concrete", "Lime")))
        if rnd.random() < 0.15:
            rebar(t, x, y, hgt * 0.5)
    for _ in range(3):                               # a slab leaning against the standing wall
        rock(t, hx0 - rnd.uniform(0.5, 2.0), rnd.uniform(1, D - 1), 0.8, 2.6, 1.2, 0.2, "Concrete", tilt=1.0, jitter=0.05)


def hut(t):
    """Small concrete/brick hut beside a road (transformer station or pump house, user photo): flat roof slab with
    overhang, steel door ajar, louvres, a broken corner."""
    w, d, h = rnd.uniform(3.0, 4.5), rnd.uniform(3.0, 4.0), rnd.uniform(2.6, 3.2)
    mat = rnd.choice(("Brick", "Concrete", "Lime"))
    pbox(t, 0, w, 0, 0.25, -1.0, h, mat)
    pbox(t, 0, w, d - 0.25, d, -1.0, h, mat)
    pbox(t, 0, 0.25, 0.25, d - 0.25, -1.0, h, mat)
    pbox(t, w - 0.25, w, 0.25, d * 0.3, -1.0, h, mat)          # door opening in the end wall
    pbox(t, w - 0.25, w, d * 0.3 + 1.0, d - 0.25, -1.0, h, mat)
    pbox(t, w - 0.25, w, d * 0.3, d * 0.3 + 1.0, 2.1, h, mat)
    rotated(t, w, d * 0.3, 0.0, rnd.uniform(-75, -30), lambda q: pbox(q, 0.0, 0.05, 0.0, 1.0, 0.02, 2.05, "Metal"))
    for k in range(4):                                         # louvres
        pbox(t, w * 0.3, w * 0.7, -0.05, 0.0, h - 1.0 + k * 0.15, h - 0.92 + k * 0.15, "Metal")
    pbox(t, -0.3, w + 0.3, -0.3, d + 0.3, h, h + 0.2, "Concrete")
    for _ in range(6):
        rock(t, rnd.uniform(-1, w + 1), rnd.uniform(-1.5, 0), 0.0, rnd.uniform(0.2, 0.6), rnd.uniform(0.2, 0.5), rnd.uniform(0.1, 0.3), mat)


def tank(g, x, y, z, r):
    h = r * 1.3
    sides = 16
    for k in range(sides):
        a0, a1 = 2 * math.pi * k / sides, 2 * math.pi * (k + 1) / sides
        pts = [(x + r * math.cos(a0), y + r * math.sin(a0), z - 0.3), (x + r * math.cos(a1), y + r * math.sin(a1), z - 0.3),
               (x + r * math.cos(a1), y + r * math.sin(a1), z + h), (x + r * math.cos(a0), y + r * math.sin(a0), z + h)]
        g.quad(pts, [(k / sides * r, 0), ((k + 1) / sides * r, 0), ((k + 1) / sides * r, h / 2), (k / sides * r, h / 2)], "Metal")
        g.quad([(x, y, z + h + 0.4), (x, y, z + h + 0.4), (x + r * math.cos(a0), y + r * math.sin(a0), z + h),
                (x + r * math.cos(a1), y + r * math.sin(a1), z + h)], [(0, 0), (0, 0), (1, 0), (0, 1)], "Metal")
    for k in range(int(h / 0.35)):  # ladder rungs
        pbox(g, x + r, x + r + 0.05, y - 0.25, y + 0.25, z + k * 0.35, z + k * 0.35 + 0.04, "Metal")
    for s in (-0.25, 0.25):
        pbox(g, x + r + 0.05, x + r + 0.1, y + s - 0.02, y + s + 0.02, z, z + h + 1.0, "Metal")


def garage(g, x, y, z):
    pbox(g, x, x + 3.2, y, y + 6.0, z - 0.2, z + 2.4, "Metal")
    pbox(g, x - 0.02, x, y + 0.3, y + 5.7, z, z + 2.1, "Concrete")  # door leaf, set into the front


def rubble(g, x, y, z, s):
    # flat, half-sunk fragments of mixed size; tall even blocks read as building material on a site
    for _ in range(int(10 * s) + 5):
        px, py = x + rnd.uniform(-1.0, 1.0) * s, y + rnd.uniform(-1.0, 1.0) * s
        w = rnd.uniform(0.08, 0.3) if rnd.random() < 0.6 else rnd.uniform(0.3, 0.8)
        hz = z + max(0.0, 0.2 * s * (1 - math.hypot(px - x, py - y) / (1.3 * s))) * rnd.random()
        rock(g, px, py, hz - 0.05, w, w * rnd.uniform(0.4, 1.2), rnd.uniform(0.06, 0.2), rnd.choice(("Concrete", "Concrete", "Lime")))


def debris(g, x, y, z, s):
    """One bit of ground litter: a stone, a concrete chunk, a board or a stick, lying flat."""
    k = rnd.random()
    if k < 0.45:
        w = rnd.uniform(0.05, 0.2) * s
        rock(g, x, y, z - 0.02, w, w * rnd.uniform(0.6, 1.2), w * 0.5, "Concrete")
    elif k < 0.75:
        L, a = rnd.uniform(0.5, 1.8) * s, rnd.random() < 0.5
        dx, dy = (L, 0.12) if a else (0.12, L)
        pbox(g, x, x + dx, y, y + dy, z - 0.01, z + 0.025, rnd.choice(("Wood", "Furniture")))
    else:
        L, a = rnd.uniform(0.4, 1.2) * s, rnd.random() < 0.5
        dx, dy = (L, 0.025) if a else (0.025, L)
        pbox(g, x, x + dx, y, y + dy, z - 0.01, z + 0.025, "Furniture")


def heap(g, x, y, z, s):
    """Heap of broken panels and plaster against a base: big flat slabs under smaller chunks."""
    for k in range(int(6 * s)):
        r = (1 - k / (6 * s)) * s
        px, py = x + rnd.uniform(-r, r), y + rnd.uniform(-r, r) * 0.6
        w = rnd.uniform(0.3, 1.1) * (1.2 - k / (6 * s))
        hz = z + (k / (6 * s)) * 0.5 * s
        rock(g, px, py, hz - 0.05, w, w * rnd.uniform(0.4, 0.9), rnd.uniform(0.08, 0.18), rnd.choice(("Concrete", "Concrete", "Lime")), tilt=0.5, jitter=0.1)
    if rnd.random() < 0.5:
        rebar(g, x, y, z + 0.3 * s)
    rubble(g, x, y, z, s * 0.6)


def car_wreck(t):
    """Stripped Soviet saloon (Moskvich/Zhiguli shape): stepped body and cabin so the profile reads rounded,
    bumpers, dark window band, wheels on some, others sitting on their hubs."""
    on_wheels = rnd.random() < 0.6
    dz = 0.0 if on_wheels else -0.16      # without wheels the body rests on the ground
    for z0, z1, hx, hy in ((0.18, 0.55, 2.1, 0.82), (0.55, 0.72, 2.02, 0.8), (0.72, 0.8, 1.9, 0.76)):
        pbox(t, -hx, hx, -hy, hy, z0 + dz, z1 + dz, "Metal")
    for z0, z1, x0, x1, hy in ((0.8, 1.05, -0.95, 0.8, 0.72), (1.05, 1.2, -0.8, 0.62, 0.68), (1.2, 1.28, -0.65, 0.45, 0.62)):
        pbox(t, x0, x1, -hy, hy, z0 + dz, z1 + dz, "Metal")
    pbox(t, -0.92, 0.77, -0.73, 0.73, 0.86 + dz, 1.12 + dz, "BlackPlastic")    # window band (glass long gone)
    for x in (-2.18, 2.08):
        pbox(t, x, x + 0.1, -0.85, 0.85, 0.28 + dz, 0.4 + dz, "Metal")          # bumpers
    for x in (-1.3, 1.3):
        for y in (-0.8, 0.62):
            if on_wheels:  # cross of two boxes: an octagon-ish wheel seen from the side
                pbox(t, x - 0.32, x + 0.32, y, y + 0.18, 0.08, 0.5, "BlackPlastic")
                pbox(t, x - 0.24, x + 0.24, y, y + 0.18, 0.0, 0.58, "BlackPlastic")


def barrel(t):
    for a in (0.0, 0.785):
        rotated(t, 0, 0, 0, math.degrees(a), lambda q: pbox(q, -0.28, 0.28, -0.28, 0.28, 0.0, 0.88, "Metal"))


def scrap(t, s):
    """Heap of bent sheet and rods, rusty (user photo 1)."""
    for _ in range(int(9 * s)):
        L, w = rnd.uniform(0.6, 2.4) * s, rnd.uniform(0.03, 0.4)
        z0 = rnd.uniform(0.0, 0.5) * s
        rotated(t, rnd.uniform(-1, 1) * s, rnd.uniform(-1, 1) * s, z0, rnd.uniform(0, 180),
                lambda q, L=L, w=w: pbox(q, -L / 2, L / 2, -w / 2, w / 2, 0.0, rnd.uniform(0.02, 0.12), "Metal"))


def fence(t):
    """6 m of plank fence on posts, a few planks gone, one section fallen flat."""
    for x in (0.0, 2.0, 4.0, 6.0):
        pbox(t, x - 0.06, x + 0.06, -0.06, 0.06, -0.3, 1.5, "WoodGrey")
    for k in range(40):
        x = 0.1 + k * 0.15
        if rnd.random() < 0.18:
            continue
        if x > 4.0 and rnd.random() < 0.5:
            pbox(t, x, x + 0.11, 0.3, 1.6, 0.0, 0.025, "WoodGrey")      # fallen
        else:
            pbox(t, x, x + 0.11, 0.06, 0.085, 0.05, rnd.uniform(1.3, 1.6), "WoodGrey")


def pole(t):
    """Wooden utility pole with a cross-arm and insulators."""
    pbox(t, -0.12, 0.12, -0.12, 0.12, -0.5, 8.5, "WoodGrey")
    pbox(t, -0.06, 0.06, -0.9, 0.9, 7.9, 8.05, "WoodGrey")
    for y in (-0.8, -0.3, 0.3, 0.8):
        pbox(t, -0.04, 0.04, y - 0.04, y + 0.04, 8.05, 8.2, "Enamel")


def furniture_out(t):
    """A wardrobe or fridge left outside, on its back or upright."""
    if rnd.random() < 0.5:
        pbox(t, -0.5, 0.5, -0.3, 0.3, 0.0, 1.9, "Furniture") if rnd.random() < 0.5 else pbox(t, -0.95, 0.95, -0.3, 0.3, 0.0, 0.6, "Furniture")
    else:
        pbox(t, -0.3, 0.3, -0.3, 0.3, 0.0, 1.5, "Enamel") if rnd.random() < 0.5 else pbox(t, -0.75, 0.75, -0.3, 0.3, 0.0, 0.6, "Enamel")


def bus_stop(t):
    """Concrete bus shelter: back wall, two sides, flat roof, bench."""
    pbox(t, -1.8, 1.8, 0.6, 0.75, 0.0, 2.4, "Concrete")
    for x in (-1.8, 1.65):
        pbox(t, x, x + 0.15, -0.6, 0.75, 0.0, 2.4, "Concrete")
    pbox(t, -2.0, 2.0, -0.8, 0.9, 2.4, 2.55, "Concrete")
    pbox(t, -1.4, 1.4, 0.2, 0.55, 0.4, 0.47, "WoodGrey")


def wood_ruin(t, s):
    """Collapsed log house: a standing corner, low wall stubs, roof boards in a heap (south ruin field)."""
    w, d = rnd.uniform(5, 9) * s, rnd.uniform(4, 7) * s
    pbox(t, 0, 0.25, 0, 0.25, 0, rnd.uniform(1.2, 2.6), "WoodGrey")
    for (x0, x1, y0, y1) in ((0, w, 0, 0.2), (0, 0.2, 0, d), (w - 0.2, w, 0, d), (0, w, d - 0.2, d)):
        if rnd.random() < 0.8:
            pbox(t, x0, x1, y0, y1, 0, rnd.uniform(0.2, 0.9), "WoodGrey")
    for _ in range(int(14 * s)):
        L = rnd.uniform(1.5, 4.5)
        rotated(t, rnd.uniform(0.5, w - 0.5), rnd.uniform(0.5, d - 0.5), rnd.uniform(0, 0.6), rnd.uniform(0, 180),
                lambda q, L=L: pbox(q, -L / 2, L / 2, -0.12, 0.12, 0, 0.05, "WoodGrey"))
    if rnd.random() < 0.6:
        pbox(t, w * 0.3, w * 0.3 + 0.6, d * 0.4, d * 0.4 + 0.6, 0, rnd.uniform(1.0, 2.2), "Brick")   # stove stack


def bust(t):
    """Damaged bust on a plinth in front of the club (user photo 2): head and shoulders, face broken off."""
    pbox(t, -0.35, 0.35, -0.35, 0.35, 0.0, 1.7, "Concrete")
    pbox(t, -0.45, 0.45, -0.45, 0.45, 1.7, 1.8, "Brick")
    pbox(t, -0.4, 0.4, -0.22, 0.22, 1.8, 2.2, "Lime")
    pbox(t, -0.18, 0.18, -0.2, 0.12, 2.2, 2.62, "Lime")


def chimney(t):
    """Brick boiler-house chimney with iron bands, ~32 m (user photo 3, dated 1963 there)."""
    for k in range(16):
        z0, r = k * 2.0, 1.25 - k * 0.025
        for a in (0.0, 30.0, 60.0):
            rotated(t, 0, 0, z0, a, lambda q, r=r: pbox(q, -r, r, -r * 0.58, r * 0.58, 0.0, 2.0, "Brick"))
        rotated(t, 0, 0, z0 + 1.6, 0.0, lambda q, r=r: pbox(q, -r - 0.04, r + 0.04, -r - 0.04, r + 0.04, 0.0, 0.1, "Metal"))


def foundation(g, x, y, z, size):
    """Footing of a demolished wooden house: broken low concrete rim, rubble inside (satellite: light squares)."""
    h = size / 2
    for (x0, x1, y0, y1) in ((-h, h, -h, -h + 0.4), (-h, h, h - 0.4, h), (-h, -h + 0.4, -h, h), (h - 0.4, h, -h, h)):
        n = max(1, int(max(x1 - x0, y1 - y0) / 2.5))
        for k in range(n):  # segments, some missing, uneven height
            if rnd.random() < 0.25:
                continue
            a0, a1 = k / n, (k + 1) / n
            sx0, sx1 = (x0 + (x1 - x0) * a0, x0 + (x1 - x0) * a1) if x1 - x0 > y1 - y0 else (x0, x1)
            sy0, sy1 = (y0 + (y1 - y0) * a0, y0 + (y1 - y0) * a1) if y1 - y0 >= x1 - x0 else (y0, y1)
            pbox(g, x + sx0, x + sx1, y + sy0, y + sy1, z - 0.4, z + rnd.uniform(0.15, 0.55), "Concrete")
    for _ in range(int(size / 3)):
        rubble(g, x + rnd.uniform(-h + 1, h - 1), y + rnd.uniform(-h + 1, h - 1), z, rnd.uniform(0.6, 1.2))


def rotated(g, x, y, z, yaw, build):
    """Build into a scratch Geo, then append it rotated about z."""
    tmp = Geo()
    build(tmp)
    g.append(tmp, x, y, z, math.radians(yaw), 1.0)


def lamp(t):
    """Concrete street-lamp post with a sheet-metal head on a bent arm."""
    pbox(t, -0.11, 0.11, -0.11, 0.11, -0.3, 7.5, "Concrete")
    pbox(t, 0.0, 1.6, -0.04, 0.04, 7.3, 7.38, "Metal")
    pbox(t, 1.3, 1.9, -0.15, 0.15, 7.05, 7.3, "Metal")


def bench(t):
    for x in (-0.7, 0.7):
        pbox(t, x - 0.08, x + 0.08, -0.25, 0.25, -0.1, 0.42, "Concrete")
    for k in range(3):
        pbox(t, -0.9, 0.9, -0.22 + k * 0.15, -0.12 + k * 0.15, 0.42, 0.46, "Furniture")
    pbox(t, -0.9, 0.9, 0.22, 0.26, 0.5, 0.85, "Furniture")


def playground(t):
    """Tube climbing frame and a swing frame (steel, painted long ago - now mostly rust)."""
    for i in range(4):
        for j in range(3):
            prism(t, (i * 0.9, j * 0.9, 0.0), (i * 0.9, j * 0.9, 2.2), 0.03, "Metal", 6)
    for z in (0.7, 1.45, 2.2):
        for j in range(3):
            prism(t, (0.0, j * 0.9, z), (2.7, j * 0.9, z), 0.025, "Metal", 6)
        for i in range(4):
            prism(t, (i * 0.9, 0.0, z), (i * 0.9, 1.8, z), 0.025, "Metal", 6)
    sx = 5.0
    for y in (0.0, 2.4):  # A-frames
        prism(t, (sx - 0.8, y, 0.0), (sx, y, 2.4), 0.04, "Metal", 6)
        prism(t, (sx + 0.8, y, 0.0), (sx, y, 2.4), 0.04, "Metal", 6)
    prism(t, (sx, 0.0, 2.4), (sx, 2.4, 2.4), 0.05, "Metal", 6)
    for y in (0.7, 1.7):  # one swing left, one chain hanging empty
        prism(t, (sx - 0.15, y - 0.2, 2.4), (sx - 0.15, y - 0.2, 0.5), 0.01, "Metal", 4)
        prism(t, (sx - 0.15, y + 0.2, 2.4), (sx - 0.15, y + 0.2, 0.5 if y < 1 else 1.4), 0.01, "Metal", 4)
    pbox(t, sx - 0.35, sx + 0.05, 0.45, 0.95, 0.46, 0.5, "Furniture")


class Stem:
    """Tapered stem between two points (bushes: several leaning stems)."""
    @staticmethod
    def add(g, a, b, r0, r1, mat, sides=5):
        dx, dy, dz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        L = math.sqrt(dx * dx + dy * dy + dz * dz) or 1.0
        # two unit vectors perpendicular to the stem
        ux, uy, uz = (-dy / (math.hypot(dx, dy) or 1.0), dx / (math.hypot(dx, dy) or 1.0), 0.0) if math.hypot(dx, dy) > 1e-3 else (1.0, 0.0, 0.0)
        vx, vy, vz = (dy * uz - dz * uy) / L, (dz * ux - dx * uz) / L, (dx * uy - dy * ux) / L
        ring = lambda p, r, k: tuple(p[i] + r * (math.cos(2 * math.pi * k / sides) * (ux, uy, uz)[i] + math.sin(2 * math.pi * k / sides) * (vx, vy, vz)[i]) for i in range(3))
        for k in range(sides):
            g.quad([ring(a, r0, k), ring(a, r0, k + 1), ring(b, r1, k + 1), ring(b, r1, k)],
                   [(k / sides * 0.6, 0), ((k + 1) / sides * 0.6, 0), ((k + 1) / sides * 0.6, L / 2), (k / sides * 0.6, L / 2)], mat)


# Keep roughly the same leaf coverage in each LOD; sparse far cards made the forest look empty.
LOD_CARDS = (1.0, 0.33, 0.16)
LOD_SIZE = (1.0, 1.8, 2.6)


def larch_tree(lod=0):
    """Dahurian larch, 11-17 m: slender trunk, narrow open cone of needle clusters along branch tiers."""
    g, h = Geo(), rnd.uniform(11, 17)
    g.trunk(h, 0.2, 0.03, "Bark_Larch", sides=(7, 5, 4)[lod])
    for _ in range(max(5, int(110 * LOD_CARDS[lod]))):
        t = rnd.uniform(0.22, 1.0)
        r = (3.3 * (1 - t) + 0.25) * rnd.uniform(0.35, 1.0)
        a = rnd.uniform(0, 2 * math.pi)
        g.card(r * math.cos(a), r * math.sin(a), h * t - r * 0.25, rnd.uniform(0.8, 1.3) * (1.15 - 0.5 * t) * LOD_SIZE[lod], "Leaves_Larch")
    return g


def sapling(lod=0):
    """Young larch, 2-6 m, dense to the ground: what fills the abandoned town (user photo 2026-11-08)."""
    g, h = Geo(), rnd.uniform(2.0, 6.0)
    g.trunk(h, 0.06, 0.015, "Bark_Larch", sides=(5, 4, 3)[lod])
    for _ in range(max(4, int(55 * LOD_CARDS[lod]))):
        t = rnd.uniform(0.08, 1.0)
        r = (h * 0.24 * (1 - t) + 0.12) * rnd.uniform(0.4, 1.0)
        a = rnd.uniform(0, 2 * math.pi)
        g.card(r * math.cos(a), r * math.sin(a), h * t, rnd.uniform(0.55, 0.9) * (1.2 - 0.5 * t) * LOD_SIZE[lod], "Leaves_Larch")
    return g


def willow(lod=0):
    """Willow / alder bush, 1.5-3.5 m: several leaning stems, leaf clusters at their upper ends - a loose irregular
    crown instead of a block of cards."""
    g = Geo()
    stems = rnd.randint(3, 6)
    for _ in range(stems):
        a, lean = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.15, 0.55)
        L = rnd.uniform(1.5, 3.5)
        base = (rnd.uniform(-0.25, 0.25), rnd.uniform(-0.25, 0.25), -0.1)
        tip = (base[0] + math.cos(a) * math.sin(lean) * L, base[1] + math.sin(a) * math.sin(lean) * L, math.cos(lean) * L)
        # every LOD keeps the stems first: the material slot order has to match across LODs
        Stem.add(g, base, tip, 0.035, 0.012, "Bark_Larch", sides=(5, 3, 3)[lod])
        for _ in range(rnd.randint(2, 4)):
            t = rnd.uniform(0.45, 1.0)
            cx, cy, cz = (base[i] + (tip[i] - base[i]) * t for i in range(3))
            for _ in range(max(1, int(9 * LOD_CARDS[lod]))):
                g.card(cx + rnd.gauss(0, 0.3), cy + rnd.gauss(0, 0.3), cz + rnd.gauss(0, 0.22),
                       rnd.uniform(0.3, 0.55) * LOD_SIZE[lod], "Leaves_Willow")
    return g


def low_willow(lod=0):
    """Low spreading growth: leaning branches with foliage close to the ground."""
    g = Geo()
    tips = []
    for _ in range(5):
        a = rnd.uniform(0, math.tau)
        tip = (math.cos(a) * rnd.uniform(0.45, 0.85), math.sin(a) * rnd.uniform(0.45, 0.85), rnd.uniform(0.45, 0.95))
        Stem.add(g, (0, 0, -0.08), tip, 0.018, 0.005, "Bark_Larch", (5, 3, 3)[lod])
        tips.append(tip)
    for x, y, z in tips:
        for _ in range(max(2, int(6 * LOD_CARDS[lod]))):
            t = rnd.uniform(0.45, 1.0)
            g.card(x * t + rnd.uniform(-0.2, 0.2), y * t + rnd.uniform(-0.2, 0.2), z * t + rnd.uniform(-0.1, 0.1),
                   rnd.uniform(0.35, 0.55) * LOD_SIZE[lod], "Leaves_Willow")
    return g


def alder(lod=0):
    """Upright multi-stem thicket with a broad, uneven crown, distinct from the low willow."""
    g, tips = Geo(), []
    for _ in range(4):
        a, h = rnd.uniform(0, math.tau), rnd.uniform(1.8, 3.0)
        tip = (math.cos(a) * 0.55, math.sin(a) * 0.55, h)
        Stem.add(g, (0, 0, -0.1), tip, 0.035, 0.008, "Bark_Larch", (5, 3, 3)[lod])
        tips.append(tip)
        mid = (tip[0] * 0.5, tip[1] * 0.5, h * 0.5)
        end = (tip[0] + math.cos(a + 0.8) * 0.55, tip[1] + math.sin(a + 0.8) * 0.55, h * 0.85)
        Stem.add(g, mid, end, 0.014, 0.004, "Bark_Larch", (5, 3, 3)[lod])
    for x, y, z in tips:
        for _ in range(max(2, int(14 * LOD_CARDS[lod]))):
            a, r = rnd.uniform(0, math.tau), rnd.uniform(0, 0.7)
            t = rnd.uniform(0.35, 1.0)
            g.card(x * t + r * math.cos(a), y * t + r * math.sin(a), z * t + rnd.uniform(-0.15, 0.2),
                   rnd.uniform(0.45, 0.75) * LOD_SIZE[lod], "Leaves_Alder")
    return g


def dry_shrub(lod=0):
    """Sparse bare branches among living thickets; no oversized leaf cards."""
    g = Geo()
    for _ in range((6, 4, 3)[lod]):
        a, h = rnd.uniform(0, math.tau), rnd.uniform(0.5, 1.1)
        tip = (math.cos(a) * 0.35, math.sin(a) * 0.35, h)
        Stem.add(g, (0, 0, -0.06), tip, 0.012, 0.003, "Bark_Larch", 3)
        for side in (-1, 1):
            mid = tuple(v * 0.6 for v in tip)
            end = (tip[0] + math.cos(a + side) * 0.3, tip[1] + math.sin(a + side) * 0.3, h * 0.9)
            Stem.add(g, mid, end, 0.006, 0.001, "Bark_Larch", 3)
    return g


def grass_clump():
    """Five vertical blade cards in a star, 0.4-0.9 m tall."""
    g = Geo()
    h = rnd.uniform(0.4, 0.9)
    for k in range(5):
        a = math.pi * k / 5 + rnd.uniform(-0.2, 0.2)
        ux, uy = math.cos(a) * h * 0.6, math.sin(a) * h * 0.6
        ox, oy = rnd.uniform(-0.15, 0.15), rnd.uniform(-0.15, 0.15)
        g.quad([(ox - ux, oy - uy, -0.03), (ox + ux, oy + uy, -0.03), (ox + ux, oy + uy, h), (ox - ux, oy - uy, h)],
               [(0, 0), (1, 0), (1, 1), (0, 1)], "Grass")
    return g


def birch(lod=0):
    g, h = Geo(), rnd.uniform(9, 13)
    g.trunk(h * 0.9, 0.14, 0.04, "Bark_Birch", sides=(7, 5, 4)[lod])
    for _ in range(max(5, int(70 * LOD_CARDS[lod]))):
        t = rnd.uniform(0.35, 1.0)
        r = 2.3 * math.sin(math.pi * min(1.0, (t - 0.3) / 0.75)) + 0.3
        a, d = rnd.uniform(0, 2 * math.pi), r * math.sqrt(rnd.random())
        g.card(d * math.cos(a), d * math.sin(a), h * t, rnd.uniform(1.1, 1.7) * LOD_SIZE[lod], "Leaves_Birch")
    return g


def shrub(lod=0):
    """Dwarf shrub (dwarf birch, blueberry), knee high: two or three low clumps."""
    g = Geo()
    for _ in range(rnd.randint(2, 3)):
        cx, cy = rnd.uniform(-0.5, 0.5), rnd.uniform(-0.5, 0.5)
        for _ in range(max(1, int(6 * LOD_CARDS[lod]))):
            a, d = rnd.uniform(0, 2 * math.pi), 0.45 * math.sqrt(rnd.random())
            g.card(cx + d * math.cos(a), cy + d * math.sin(a), rnd.uniform(0.2, 0.6), rnd.uniform(0.5, 0.8) * LOD_SIZE[lod], "Leaves_Shrub")
    return g


# instanced kinds: (builder, variants, cull distance cm (0 = never), cast shadow)
INSTANCED = {"larch": (larch_tree, 4, 0, True), "birch": (birch, 4, 450000, True), "sapling": (sapling, 4, 300000, True),
             "willow": (willow, 4, 180000, True), "shrub": (shrub, 3, 25000, False),
             "low_willow": (low_willow, 3, 35000, False), "alder": (alder, 3, 220000, True), "dry_shrub": (dry_shrub, 3, 20000, False)}


def export(name, geo):
    me = bpy.data.meshes.new(name)
    me.from_pydata(geo.v, [], geo.f)
    me.update()
    uv = me.uv_layers.new(name="UVMap")
    for poly in me.polygons:
        poly.material_index = geo.mat[poly.index]
        for k, li in enumerate(poly.loop_indices):
            uv.data[li].uv = geo.uv[poly.index][k]
    col = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
    for c in col.data:
        c.color = (0.0, 0.0, 0.0, 1.0)
    for m in geo.mats:
        me.materials.append(bpy.data.materials.get(m) or bpy.data.materials.new(m))
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=os.path.join(SRC, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                             apply_scale_options="FBX_SCALE_UNITS", mesh_smooth_type="FACE", colors_type="SRGB",
                             add_leaf_bones=False, bake_anim=False)
    bpy.data.objects.remove(ob, do_unlink=True)


def build_layers(scatter):
    global rnd
    data_dir = os.path.join(ROOT, "Content/Kadykchan/Data/Foliage")
    os.makedirs(data_dir, exist_ok=True)
    layers = []
    for kind, (build, variants, cull, shadow) in INSTANCED.items():
        items = scatter.get(kind, [])
        for k in range(variants):
            lods = []
            for lod in range(3):
                rnd = random.Random("%s-%d" % (kind, k))  # same seed per LOD: the same tree, fewer and bigger cards
                name = "SM_Tree_%s_%d_LOD%d" % (kind, k, lod)
                export(name, build(lod))
                lods.append(name)
            data = "%s_%d.txt" % (kind, k)
            with open(os.path.join(data_dir, data), "w") as f:
                for east, north, z, yaw, sc in items[k::variants]:
                    f.write("%.0f %.0f %.0f %d %.2f\n" % (north * 100, east * 100, z * 100, yaw, sc))
            layers.append({"kind": kind, "lods": lods, "data": data, "count": len(items[k::variants]), "cull_cm": cull, "shadow": shadow})
    return layers


def courtyard(g,variant):
    """Small coherent yard scenes, on the verge rather than in the traffic lane."""
    def box(a,b,c,d,e,f,mat):pbox(g,a,b,c,d,e,f,mat)
    if variant==0:
        box(-1.5,1.5,-1,1,-.35,.04,"Concrete")
        for x in (-.7,.65):
            box(x-.5,x+.5,-.55,.55,.1,1.0,"Metal")
            box(x-.55,x+.55,-.6,.6,1,1.08,"Metal")
            for z in (.25,.55,.85):box(x-.52,x+.52,-.57,-.55,z,z+.035,"BlackPlastic")
            for y in (-.45,.45):prism(g,(x-.4,y,.13),(x+.4,y,.13),.06,"BlackPlastic",12)
    elif variant==1:
        bench(g)
        for x in (-1.8,1.8):
            box(x-.4,x+.4,-.4,.4,-.3,.45,"Concrete")
            box(x-.3,x+.3,-.3,.3,.45,.48,"WoodGrey")
            for k in range(5):
                prism(g,(x+(k-2)*.08,0,.48),(x+(k-2)*.1,.1,.9+k*.02),.018,"WoodGrey",6)
    elif variant==2:
        box(-1.7,1.7,-.8,.8,-.3,0,"Concrete")
        for x in (-1,0,1):
            prism(g,(x,-.6,0),(x,-.6,.75),.035,"Metal",12)
            prism(g,(x,.6,0),(x,.6,.75),.035,"Metal",12)
            prism(g,(x,-.6,.75),(x,.6,.75),.035,"Metal",12)
        # Bent bicycle frame, wheels as open rings and a saddle.
        for cx in (-.65,.65):
            for k in range(24):
                a,b=k*math.tau/24,(k+1)*math.tau/24
                prism(g,(cx+.34*math.cos(a),-.8,.36+.34*math.sin(a)),(cx+.34*math.cos(b),-.8,.36+.34*math.sin(b)),.025,"BlackPlastic",6)
        for a,b in (((-.65,-.8,.36),(0,-.8,.8)),((0,-.8,.8),(.65,-.8,.36)),((-.65,-.8,.36),(.65,-.8,.36))):prism(g,a,b,.025,"Metal",8)
        box(-.15,.15,-.9,-.7,.8,.86,"BlackPlastic")
    elif variant==3:
        for x in (-2,2):
            prism(g,(x,0,-.5),(x,0,2.2),.045,"Metal",12)
            prism(g,(x,-.8,2.1),(x,.8,2.1),.035,"Metal",10)
        for y in (-.6,0,.6):prism(g,(-2,y,2.1),(2,y,2.1),.008,"Metal",6)
        for k in range(7):
            box(-1.9+k*.6,-1.85+k*.6,.95,1.02,-.25,.7-(k%3)*.08,"WoodGrey")
        box(-2.2,2.2,.96,1.01,.45,.5,"WoodGrey")
    else:
        for x in (-.8,.8):box(x-.05,x+.05,0,.1,-.4,1.8,"Metal")
        box(-1,1,0,.06,.8,1.9,"WoodGrey")
        for k in range(5):box(-.8+k*.32,-.55+k*.32,-.005,0,1.0,1.25+(k%2)*.2,"Enamel")
        for k in range(12):rock(g,-1.7+(k%4)*.22,.8+(k//4)*.18,.05,.2,.12,.1,"Brick")


def boarded_door(g):
    pbox(g,-.04,.08,-.65,.65,0,2.2,"WoodGrey")
    for k in range(7):pbox(g,-.08,-.04,-.7,.7,.1+k*.3,.27+k*.3,"Wood")
    for y in (-.6,.6):pbox(g,-.12,-.08,y-.025,y+.025,0,2.25,"Metal")
    prism(g,(-.14,-.6,.2),(-.14,.6,2.0),.045,"WoodGrey",4)


def main():
    global rnd
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scatter = json.load(open(os.path.join(SRC, "scatter.json")))
    protos = {"grass": [grass_clump() for _ in range(8)]}
    layers = build_layers(scatter)
    rnd = random.Random(1943)
    cells = {}
    for kind, items in (("grass", scatter.get("grass", [])),):
        for east, north, z, yaw, s in items:
            key = (math.floor(north / CELL), math.floor(east / CELL))
            cells.setdefault(key, []).append((kind, east, north, z, yaw, s))
    props = {}
    def pcell(east, north):
        key = (math.floor(north / CELL), math.floor(east / CELL))
        return props.setdefault(key, Geo()), (key[0] + 0.5) * CELL, (key[1] + 0.5) * CELL
    for line in scatter.get("pipes", []):  # two insulated heat pipes on concrete supports
        for (e0, n0, z0), (e1, n1, z1) in zip(line, line[1:]):
            g, cn, ce = pcell(e0, n0)
            a, b = (n0 - cn, -(e0 - ce), z0), (n1 - cn, -(e1 - ce), z1)
            for off in (-0.3, 0.3):
                dx, dy = b[0] - a[0], b[1] - a[1]
                l = math.hypot(dx, dy) or 1.0
                ox, oy = -dy / l * off, dx / l * off
                prism(g, (a[0] + ox, a[1] + oy, a[2] + 0.9), (b[0] + ox, b[1] + oy, b[2] + 0.9), 0.22, "Metal")
            pbox(g, a[0] - 0.15, a[0] + 0.15, a[1] - 0.45, a[1] + 0.45, a[2] - 0.3, a[2] + 0.65, "Concrete")
    for east, north, z, yaw, s in scatter.get("rubble", []):
        g, cn, ce = pcell(east, north)
        rubble(g, north - cn, -(east - ce), z, s)
    for east, north, z, yaw, s in scatter.get("debris", []):
        g, cn, ce = pcell(east, north)
        debris(g, north - cn, -(east - ce), z, s)
    for east, north, z, yaw, s in scatter.get("heaps", []):
        g, cn, ce = pcell(east, north)
        heap(g, north - cn, -(east - ce), z, s)
    for kind, build in (("cars", car_wreck), ("barrels", barrel), ("fences", fence), ("poles", pole),
                        ("furniture", furniture_out), ("busstops", bus_stop), ("busts", bust), ("chimneys", chimney)):
        for east, north, z, yaw in scatter.get(kind, []):
            g, cn, ce = pcell(east, north)
            rotated(g, north - cn, -(east - ce), z, yaw, build)
    for east, north, z, yaw in scatter.get("huts", []):
        g, cn, ce = pcell(east, north)
        rotated(g, north - cn, -(east - ce), z, yaw, hut)
    for kind, build in (("scrap", scrap), ("woodruins", wood_ruin), ("ruins", panel_ruin)):
        for east, north, z, yaw, s in scatter.get(kind, []):
            g, cn, ce = pcell(east, north)
            rotated(g, north - cn, -(east - ce), z, yaw, lambda q, s=s, build=build: build(q, s))
    for east, north, z, size in scatter.get("foundations", []):
        g, cn, ce = pcell(east, north)
        foundation(g, north - cn, -(east - ce), z, size)
    for east, north, z, r in scatter.get("tanks", []):
        g, cn, ce = pcell(east, north)
        tank(g, north - cn, -(east - ce), z, r / 2)
    for east, north, z in scatter.get("garages", []):
        g, cn, ce = pcell(east, north)
        garage(g, north - cn, -(east - ce), z)
    for east, north, z, yaw in scatter.get("lamps", []):
        g, cn, ce = pcell(east, north)
        rotated(g, north - cn, -(east - ce), z, -yaw, lamp)
    for east, north, z, yaw in scatter.get("benches", []):
        g, cn, ce = pcell(east, north)
        rotated(g, north - cn, -(east - ce), z, yaw, bench)
    for east, north, z, yaw in scatter.get("playgrounds", []):
        g, cn, ce = pcell(east, north)
        rotated(g, north - cn, -(east - ce), z, yaw, playground)
    for east,north,z,yaw,variant in scatter.get("courtyard_details",[]):
        g,cn,ce=pcell(east,north)
        rotated(g,north-cn,-(east-ce),z,-yaw,lambda t: courtyard(t,int(variant)))
    for east,north,z,yaw in scatter.get("blocked_doors",[]):
        g,cn,ce=pcell(east,north)
        rotated(g,north-cn,-(east-ce),z,-yaw,boarded_door)
    manifest = []
    for (i, j), g in sorted(props.items()):
        name = "SM_Props_%d_%d" % (i, j)
        export(name, g)
        manifest.append({"mesh": name, "north_m": (i + 0.5) * CELL, "east_m": (j + 0.5) * CELL, "count": 0, "quads": len(g.f),
                         "materials": g.mats, "props": True})
    for (i, j), items in sorted(cells.items()):
        cn, ce = (i + 0.5) * CELL, (j + 0.5) * CELL
        geo = Geo()
        for kind, east, north, z, yaw, s in items:
            # Blender x = north, y = -east (mirrored for the FBX Y flip), relative to the cell centre
            geo.append(rnd.choice(protos[kind]), north - cn, -(east - ce), z, math.radians(yaw), s)
        name = "SM_Veg_%d_%d" % (i, j)
        export(name, geo)
        manifest.append({"mesh": name, "north_m": cn, "east_m": ce, "count": len(items), "quads": len(geo.f), "materials": geo.mats})
    json.dump({"cells": manifest, "layers": layers}, open(os.path.join(SRC, "veg_manifest.json"), "w"), indent=1)
    print("VEGETATION OK cells=%d props=%d quads=%d instances=%d" % (sum(not m.get("props") for m in manifest), sum(bool(m.get("props")) for m in manifest),
          sum(m["quads"] for m in manifest), sum(l["count"] for l in layers)))


if __name__ == "__main__":  # build_mine.py imports the geometry helpers
    main()
