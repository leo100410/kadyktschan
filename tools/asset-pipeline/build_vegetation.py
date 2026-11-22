"""Blender CLI: procedural birches, larches and dwarf shrubs, merged into one mesh per 600 m cell.

Run: blender --background --factory-startup --python tools/asset-pipeline/build_vegetation.py -- <project root>
Reads assets/vegetation/scatter.json (tools/research/scatter_vegetation.py), writes
assets/vegetation/SM_Veg_<i>_<j>.fbx and veg_manifest.json.

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
        w = rnd.uniform(0.05, 0.25) if rnd.random() < 0.6 else rnd.uniform(0.3, 0.8)
        d, h = w * rnd.uniform(0.4, 1.2), rnd.uniform(0.03, 0.14)
        hz = z + max(0.0, 0.2 * s * (1 - math.hypot(px - x, py - y) / (1.3 * s))) * rnd.random()
        pbox(g, px, px + w, py, py + d, hz - 0.12, hz + h, rnd.choice(("Concrete", "Concrete", "Lime")))


def debris(g, x, y, z, s):
    """One bit of ground litter: a stone, a concrete chunk, a board or a stick, lying flat."""
    k = rnd.random()
    if k < 0.45:
        w = rnd.uniform(0.05, 0.2) * s
        pbox(g, x, x + w, y, y + w * rnd.uniform(0.6, 1.2), z - 0.03, z + w * 0.4, "Concrete")
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
        pbox(g, px, px + w, py, py + w * rnd.uniform(0.4, 0.9), hz - 0.1, hz + rnd.uniform(0.06, 0.16), rnd.choice(("Concrete", "Concrete", "Lime")))
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


def birch():
    g, h = Geo(), rnd.uniform(9, 13)
    g.trunk(h * 0.9, 0.14, 0.04, "Bark_Birch")
    for _ in range(70):
        t = rnd.uniform(0.35, 1.0)
        r = 2.3 * math.sin(math.pi * min(1.0, (t - 0.3) / 0.75)) + 0.3
        a, d = rnd.uniform(0, 2 * math.pi), r * math.sqrt(rnd.random())
        g.card(d * math.cos(a), d * math.sin(a), h * t, rnd.uniform(1.1, 1.7), "Leaves_Birch")
    return g


def larch():
    g, h = Geo(), rnd.uniform(11, 17)
    g.trunk(h, 0.2, 0.03, "Bark_Larch")
    for _ in range(48):
        t = rnd.uniform(0.2, 1.0)
        r = 2.4 * (1 - t) + 0.25
        a, d = rnd.uniform(0, 2 * math.pi), r * (0.5 + 0.5 * rnd.random())
        g.card(d * math.cos(a), d * math.sin(a), h * t, rnd.uniform(1.2, 1.9) * (1.1 - 0.5 * t), "Leaves_Larch")
    return g


def shrub():
    g = Geo()
    for _ in range(14):
        a, d = rnd.uniform(0, 2 * math.pi), 0.8 * math.sqrt(rnd.random())
        g.card(d * math.cos(a), d * math.sin(a), rnd.uniform(0.25, 0.8), rnd.uniform(0.7, 1.1), "Leaves_Shrub")
    return g


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


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scatter = json.load(open(os.path.join(SRC, "scatter.json")))
    protos = {"birch": [birch() for _ in range(6)], "larch": [larch() for _ in range(6)], "shrub": [shrub() for _ in range(6)],
              "grass": [grass_clump() for _ in range(8)]}
    cells = {}
    for kind, items in (("birch", scatter["birch"]), ("larch", scatter["larch"]), ("shrub", scatter["shrub"]),
                        ("grass", scatter.get("grass", []))):
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
    for kind, build in (("scrap", scrap), ("woodruins", wood_ruin)):
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
    json.dump(manifest, open(os.path.join(SRC, "veg_manifest.json"), "w"), indent=1)
    print("VEGETATION OK cells=%d props=%d quads=%d" % (sum(not m.get("props") for m in manifest), sum(bool(m.get("props")) for m in manifest),
                                                         sum(m["quads"] for m in manifest)))


main()
