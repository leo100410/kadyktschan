"""Blender CLI: assemble every addressed building from the T5 kit into one mesh per address.

Run: blender --background --factory-startup --python tools/asset-pipeline/build_buildings.py -- <project root> [label ...]
Reads design/research/data/{osm-kadykchan-2026-11-07,blockout-2026-11-07}.json and kit_grid.json.
Writes assets/buildings/SM_Bld_<Street>_<No>.fbx and assets/buildings/buildings_manifest.json.

Footprint: the OSM polygon in the building frame (u along the long axis, v across), rasterised on
the axis grid. Rectangles get the kit depth (ANNAHME 12 m, kit_grid.json); other shapes follow the
polygon. Geometry is built mirrored in v (Blender y = -v) because the FBX import negates Y
(verified 2026-11-07), so the imported mesh matches the map.
"""
import hashlib, json, math, os, random, sys
import bpy

ROOT = sys.argv[sys.argv.index("--") + 1]
ONLY = sys.argv[sys.argv.index("--") + 2:]
os.environ["KDK_ROOT"] = ROOT
sys.path.insert(0, os.path.join(ROOT, "tools/asset-pipeline"))
import build_t5_kit as kit  # noqa: E402  (kit part geometry and Part helper)
import interiors  # noqa: E402
import murals  # noqa: E402
import kulturhaus  # noqa: E402
import story_rooms  # noqa: E402
import residential  # noqa: E402

# addresses with an enterable ground-floor section at the middle entrance: "flats" = stairwell + two flats
# (PDF phase 3: ул. Ленина block), "shop" = магазин (briefing V10 B; building ANNAHME, pink ground floor);
# story rooms (story_rooms.py, FIKTION): Gorbunov flat in an unaddressed block, the boiler house beside the chimney,
# the telephone exchange on ул. Школьная (dossier: house unknown, Школьная 8 ANNAHME)
INTERIOR_SECTIONS = {"PLA_Lenina_8": "lenina8", "PLA_Lenina_7": "lenina7", "PLA_Shkolnaya_3": "shop",
                     "PLA_SAT_S_Block": "family", "PLA_OSM_170991713": "boiler", "PLA_Shkolnaya_8": "radio"}

INTERIOR_SECTIONS.update({label: info[1] for label, info in residential.HOUSES.items()})

G = kit.G
AX, ST, T = G["axis"], G["storey_height"], G["panel_thickness"]
CRAWL, PLINTH, PARAPET = G["pile"]["crawl_height"], G["plinth_band"], G["parapet"]
Z0 = CRAWL + PLINTH
GLASS_SHARE = 0.3     # intact double glazing
BROKEN_SHARE = 0.3    # some panes left (atmosphere-target.md: single damaged windows, not a rubble field)
FRAME_MISSING = 0.15
BOARDED = 0.1         # ground floor only
# per-building decay level (user 2026-11-07: "some clearly more run down, some less"); probabilities per panel/window
DECAY = {
    0: dict(spall=0.45, crack=0.15, rust=0.08, sash=0.08, lglaze=0.45, lclutter=0.25, ploss=0.0, frame=0.08, roofplants=3, base=0.15, roofhole=0.0, pipes=0.5),
    1: dict(spall=1.0, crack=0.45, rust=0.25, sash=0.22, lglaze=0.4, lclutter=0.35, ploss=0.5, frame=0.15, roofplants=14, base=0.35, roofhole=0.0, pipes=1.0),
    2: dict(spall=1.0, crack=0.7, rust=0.35, sash=0.3, lglaze=0.3, lclutter=0.3, ploss=1.6, frame=0.35, roofplants=30, base=0.6, roofhole=0.12, pipes=1.0),
    3: dict(spall=1.0, crack=0.85, rust=0.4, sash=0.35, lglaze=0.2, lclutter=0.2, ploss=3.0, frame=0.55, roofplants=50, base=0.8, roofhole=0.3, pipes=1.0),
}
SLAB_INSET = 0.03     # m, slab edges behind the facade plane (see slabs)
HERO = {"PLA_Lenina_8", "PLA_Lenina_7"}  # fully dressed exteriors at the player start (user request 2026-11-07)
CURTAIN = 0.07        # sparse curtain remnants: dark windows should suggest flats, a few show who lived there
# bay-window columns (pink, from the ground-floor colour) at these axes of the street side - photo 6480312099; ANNAHME positions
BAYS = {"PLA_Lenina_8": (9, 18)}
OUT = os.path.join(ROOT, "assets/buildings")
OSM = json.load(open(os.path.join(ROOT, "design/research/data/osm-kadykchan-2026-11-07.json")))
DATA = json.load(open(os.path.join(ROOT, "design/research/data/blockout-2026-11-07.json"), encoding="utf-8"))
LAT0, LON0, R = 63.085870, 147.050008, 6371008.8

# facade colour schemes (upper floors, ground floor) - ANNAHME from the 2011 photos; art bible 4.1 names
SCHEMES = [("Mint", "Rose"), ("Lime", "Lime"), ("Concrete", "Lime"), ("Lime", "Rose"), ("Mint", "Mint"), ("Concrete", "Concrete"),
           ("Ochre", "Ochre"), ("Teal", "Lime"), ("Ochre", "Lime")]  # pastel blocks seen on the user's aerial photos
FIXED_SCHEME = {"PLA_Lenina_8": ("Mint", "Rose"),  # reference photo 6480312099
                "PLA_Shkolnaya_1": ("Concrete", "Concrete"),  # school: grey panels between light fins
                "PLA_Mira_1": ("Mint", "Mint"),
                "PLA_Yuzhnaya_9": ("Ochre", "Ochre")}  # yellow club, user photo 2026-11-07   # 9-storey with the mosaic gable, photo 6480317815 (building ANNAHME)
GABLE_MURALS = {"PLA_Mira_1": "reindeer_and_figure"}
KULTURHAUS = {"PLA_Yuzhnaya_9"}  # building ANNAHME, see kulturhaus.py
SCHOOL = {"PLA_Shkolnaya_1"}  # school facade with fins (photo 6480300155); building ANNAHME (dossier: school on ул. Школьная)
# damage (art bible 8.3 "_Ruin" state, Wikipedia "major buildings were blown up"): 1 = broken-out panels,
# 2 = collapsed corner. Probabilities ANNAHME; the vertical-slice buildings never collapse.
NO_COLLAPSE = {"PLA_Lenina_8", "PLA_Lenina_7", "PLA_Mira_1", "PLA_Yuzhnaya_9"}
PANEL_LOSS = 0.06
# house-number stencils in the original spelling: street (genitive, no "ул.") + number, photo 6480291063 "ЛЕНИНА 18"
STREET_RU = {"Lenina": "ЛЕНИНА", "Shkolnaya": "ШКОЛЬНАЯ", "Yuzhnaya": "ЮЖНАЯ", "Mira": "МИРА", "50LetOktyabrya": "50 ЛЕТ ОКТЯБРЯ"}
_text_cache = {}


def text_polys(text, size):
    """Flat glyph polygons of Blender's built-in font (Cyrillic-capable) in the XY plane, facing +Z."""
    key = (text, size)
    if key not in _text_cache:
        cu = bpy.data.curves.new("txt", type="FONT")
        cu.body, cu.size = text, size
        ob = bpy.data.objects.new("txt", cu)
        bpy.context.scene.collection.objects.link(ob)
        me = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        verts = [tuple(v.co) for v in me.vertices]
        polys = [tuple(p.vertices) for p in me.polygons]
        width = max(v[0] for v in verts) - min(v[0] for v in verts)
        bpy.data.objects.remove(ob, do_unlink=True)
        _text_cache[key] = (verts, polys, width)
    return _text_cache[key]


def add_gable_roof(acc, x0, y0, x1, y1, z, span):
    """Gable roof over the box x0..x1, y0..y1 with the ridge along the longer side; 30 deg pitch, 0.5 m eaves."""
    over = 0.5
    along_x = (x1 - x0) >= (y1 - y0)
    rise = span / 2 * math.tan(math.radians(30))
    if along_x:
        ym = (y0 + y1) / 2
        e = [(x0 - over, y0 - over, z), (x1 + over, y0 - over, z), (x1 + over, y1 + over, z), (x0 - over, y1 + over, z)]
        r0, r1 = (x0 - over, ym, z + rise), (x1 + over, ym, z + rise)
        slopes = [(e[0], e[1], r1, r0), (e[2], e[3], r0, r1)]
        gables = [(e[3], e[0], r0), (e[1], e[2], r1)]
    else:
        xm = (x0 + x1) / 2
        e = [(x0 - over, y0 - over, z), (x1 + over, y0 - over, z), (x1 + over, y1 + over, z), (x0 - over, y1 + over, z)]
        r0, r1 = (xm, y0 - over, z + rise), (xm, y1 + over, z + rise)
        slopes = [(e[1], e[2], r1, r0), (e[3], e[0], r0, r1)]
        gables = [(e[0], e[1], r0), (e[2], e[3], r1)]
    for slot in ("Roof",):
        if slot not in acc.mats:
            acc.mats.append(slot)
    mi = acc.mats.index("Roof")
    for quad in slopes:
        b = len(acc.verts)
        acc.verts += list(quad)
        for f in ((b, b + 1, b + 2, b + 3), (b + 3, b + 2, b + 1, b)):  # two-sided: no gap if seen from the attic
            acc.faces.append(f)
            acc.face_mat.append(mi)
    if "Facade_Lime" not in acc.mats:
        acc.mats.append("Facade_Lime")
    gm = acc.mats.index("Facade_Lime")
    for tri in gables:
        b = len(acc.verts)
        acc.verts += list(tri)
        for f in ((b, b + 1, b + 2), (b + 2, b + 1, b)):
            acc.faces.append(f)
            acc.face_mat.append(gm)


def add_mural(acc, pieces, px, py, d, width):
    """Mosaic on a gable: convex polygons in viewer coordinates (x to the right as seen from outside), two-sided."""
    left = (-d[1], d[0])
    for shapes, ox, oy, scale in pieces:
        for poly, slot, layer in shapes():
            bb = -0.015 - 0.008 * layer  # in front of the panel; details float over the base colour
            base = len(acc.verts)
            for x, y in poly:
                a = ox + x * scale
                acc.verts.append((px + d[0] * a + left[0] * bb, py + d[1] * a + left[1] * bb, Z0 + oy + y * scale))
            if slot not in acc.mats:
                acc.mats.append(slot)
            idx = list(range(base, base + len(poly)))
            for f in (tuple(idx), tuple(reversed(idx))):
                acc.faces.append(f)
                acc.face_mat.append(acc.mats.index(slot))


def add_stencil(acc, text, px, py, d, n, z, size=0.26, mat="Stencil", out=0.012):
    """House number centred above an entrance, two-sided. Authored as read from outside in Blender: the FBX import
    converts coordinates but keeps the visual handedness (verified on the gable mosaic 2026-11-07)."""
    verts, polys, width = text_polys(text, size)
    left = (-d[1], d[0])  # inward
    base = len(acc.verts)
    for tx, ty, _ in verts:
        a = AX / 2 - width / 2 + tx          # left-to-right as seen from outside
        bb = -out                            # just in front of the outer face (or of a sign board)
        acc.verts.append((px + d[0] * a + left[0] * bb, py + d[1] * a + left[1] * bb, z + ty))
    if mat not in acc.mats:
        acc.mats.append(mat)
    mi = acc.mats.index(mat)
    for poly in polys:
        for f in (poly, tuple(reversed(poly))):
            acc.faces.append(tuple(base + i for i in f))
            acc.face_mat.append(mi)


def osm_polygons():
    xy = lambda la, lo: (math.radians(lo - LON0) * R * math.cos(math.radians(LAT0)), math.radians(la - LAT0) * R)
    return {"way/%d" % e["id"]: [xy(p["lat"], p["lon"]) for p in e["geometry"]] for e in OSM["elements"]
            if e["type"] == "way" and "building" in e.get("tags", {}) and e.get("geometry")}


def rect_poly(b):
    """Footprint corners (east, north) of a building known only by its oriented box (satellite additions)."""
    a = math.radians(b["axis_deg_from_east"]); ca, sa = math.cos(a), math.sin(a)
    hl, hw = b["length_m"] / 2, b["width_m"] / 2
    return [(b["east_m"] + u * ca - v * sa, b["north_m"] + u * sa + v * ca) for u, v in ((-hl, -hw), (hl, -hw), (hl, hw), (-hl, hw))]


def inside(pt, poly):
    x, y, c = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


class Acc(kit.Part):
    """Accumulates transformed kit parts and raw boxes into one mesh."""

    def add(self, part, theta, px, py, pz, remap):
        c, s = math.cos(theta), math.sin(theta)
        base = len(self.verts)
        self.verts += [(px + x * c - y * s, py + x * s + y * c, pz + z) for x, y, z in part.verts]
        self.smooth_faces.update(len(self.faces) + i for i in part.smooth_faces)
        for f, mi in zip(part.faces, part.face_mat):
            name = remap.get(part.mats[mi], part.mats[mi])
            if name not in self.mats:
                self.mats.append(name)
            self.faces.append(tuple(base + i for i in f))
            self.face_mat.append(self.mats.index(name))


def build_one(b, poly_world, parts):
    lv = int(b["levels"]) if (b["levels"] or "").isdigit() else 2
    yaw = math.radians(90.0 - b["axis_deg_from_east"])  # UE yaw, same convention as the blockout
    dX, dY = (math.cos(yaw), math.sin(yaw)), (-math.sin(yaw), math.cos(yaw))  # (north, east) of local +X / +Y
    cn, ce = b["north_m"], b["east_m"]
    local = [((y - cn) * dX[0] + (x - ce) * dX[1], (y - cn) * dY[0] + (x - ce) * dY[1]) for x, y in poly_world]
    if local[0] == local[-1]:
        local = local[:-1]
    if len(local) <= 4:  # rectangle: OSM length, kit depth for slabs (ANNAHME), OSM width for low public buildings
        nu = max(1, round(b["length_m"] / AX))
        nv = max(1, round((G["depth"] if lv >= 3 else b["width_m"]) / AX))
        cells = {(i, j) for i in range(nu) for j in range(nv)}
        u0, v0 = -nu * AX / 2, -nv * AX / 2
    else:
        us, vs = [p[0] for p in local], [p[1] for p in local]
        nu, nv = math.ceil((max(us) - min(us)) / AX), math.ceil((max(vs) - min(vs)) / AX)
        u0, v0 = (max(us) + min(us)) / 2 - nu * AX / 2, (max(vs) + min(vs)) / 2 - nv * AX / 2
        cells = {(i, j) for i in range(nu) for j in range(nv) if inside((u0 + (i + .5) * AX, v0 + (j + .5) * AX), local)}
    # Blender space: x = u, y = -v (mirrored, see module doc). Cell (i, j) spans x0..x0+AX, y0..y0+AX.
    cell_xy = lambda i, j: (u0 + i * AX, -(v0 + (j + 1) * AX))
    # outward normals in Blender space: j+1 is -y after the mirror
    nbr = {(0, 1): (0, -1), (0, -1): (0, 1), (-1, 0): (-1, 0), (1, 0): (1, 0)}

    acc = Acc(b["label"].replace("PLA_", "SM_Bld_"))
    glass = Acc(acc.name + "_Glass")  # translucent panes in their own mesh so the building keeps Nanite (art bible 8.7)
    rnd = random.Random(int(hashlib.md5(b["label"].encode()).hexdigest()[:8], 16))
    up, ground = FIXED_SCHEME.get(b["label"]) or SCHEMES[rnd.randrange(len(SCHEMES))]

    # entrance side: the one facing the town origin (courtyards face inward), ANNAHME
    to_o = (-(cn * dX[0] + ce * dX[1]), (cn * dY[0] + ce * dY[1]))  # (u, -v) of the origin direction
    # only the two long sides (normals across the long axis) can carry entrances; gables never do
    entrance_n = max(((0, 1), (0, -1)), key=lambda n: n[0] * to_o[0] + n[1] * to_o[1])

    edges = []  # (start point, direction, normal) per boundary cell edge
    for (i, j) in cells:
        x0, y0 = cell_xy(i, j)
        for (di, dj), n in nbr.items():
            if (i + di, j + dj) in cells:
                continue
            d = (-n[1], n[0])  # walk so the outward normal is on the right of the walking direction
            corners = {(0, -1): (x0, y0), (0, 1): (x0 + AX, y0 + AX), (-1, 0): (x0, y0 + AX), (1, 0): (x0 + AX, y0)}
            edges.append(((i, j, di, dj), corners[n], d, n))
    edge_keys = {e[0] for e in edges}

    def run_info(key):
        i, j, di, dj = key
        step = (1, 0) if dj != 0 else (0, 1)
        lo = hi = 0
        while (i - step[0] * (lo + 1), j - step[1] * (lo + 1), di, dj) in edge_keys:
            lo += 1
        while (i + step[0] * (hi + 1), j + step[1] * (hi + 1), di, dj) in edge_keys:
            hi += 1
        return lo, lo + hi + 1

    top = Z0 + lv * ST
    entrances = []  # [north_m, east_m, yaw_deg toward the door]

    def classify(key, d, n):
        pos, run = run_info(key)
        # position along the run in walking direction (walk can be against the index direction)
        k = pos if (d[0] + d[1]) > 0 else run - 1 - pos
        gable = run <= 5 and lv >= 3
        is_entrance = (n == entrance_n and lv >= 3 and run >= 6 and k >= 3 and k <= run - 3 and (k - 3) % 9 == 0) or \
                      (n == entrance_n and lv < 3 and run >= 2 and k == run // 2)
        return gable, is_entrance

    # interior section at the middle entrance (ordered along the facade)
    section_key, section_cells, stair_col, shaft = None, set(), set(), set()
    furnished_floors = residential.HOUSES.get(b["label"], (1,))[0]
    if b["label"] in INTERIOR_SECTIONS:
        ent = sorted((e for e in edges if classify(e[0], e[2], e[3])[1]), key=lambda e: e[1][0] * e[2][0] + e[1][1] * e[2][1])
        if ent:
            section_key, (spx, spy), sd, sn = ent[len(ent) // 2]
            i_e, j_e, di, dj = section_key
            step = int(sd[0]) if sd[0] else int(sd[1])
            cell_at = lambda c, depth_k: ((i_e + c * step, j_e - dj * depth_k) if di == 0 else (i_e - di * depth_k, j_e + c * step))
            # the flats run through the whole block (interiors.DEEP) when every cell behind them exists
            deep = b["label"] in residential.HOUSES or INTERIOR_SECTIONS[b["label"]] in story_rooms.DEEP_KINDS
            assert not deep or all(cell_at(c, k) in cells for c in range(-2, 3) for k in range(interiors.DEEP)), b["label"] + ": block too shallow for the deep flats"
            for c in range(-2, 3):
                for depth_k in range(interiors.DEEP if deep else 2):
                    section_cells.add(cell_at(c, depth_k))
            if deep:  # stair column: shaft walls on the first floor, no slab over the back half (open stair shaft)
                stair_col = {cell_at(0, k) for k in range(interiors.DEEP)}
                shaft = {cell_at(0, k) for k in range(2, interiors.DEEP)}

    hall, corridor, hall_key = set(), set(), None
    if b["label"] in KULTURHAUS:
        street_n = (-entrance_n[0], -entrance_n[1])
        hall = kulturhaus.hall_cells(nu, nv, street_n) & cells
        ent = sorted((e for e in edges if classify(e[0], e[2], e[3])[1]), key=lambda e: e[1][0] * e[2][0] + e[1][1] * e[2][1])
        if ent and hall:
            hall_key = ent[len(ent) // 2][0]
            i_e, j_e, _, dj = hall_key
            j = j_e
            while (i_e, j) in cells and (i_e, j) not in hall:
                corridor.add((i_e, j))
                j -= dj  # walk inward from the entrance facade
    bay_cells = set()
    if b["label"] in BAYS:
        street_n = (-entrance_n[0], -entrance_n[1])
        run = sorted((e for e in edges if e[3] == street_n), key=lambda e: e[1][0] * e[2][0] + e[1][1] * e[2][1])
        bay_cells = {(run[k][0][0], run[k][0][1]) for k in BAYS[b["label"]] if k < len(run)}
    # loggia columns on the street side of about half the residential blocks (photo 6480281023), ANNAHME
    loggia_cells = set()
    if lv >= 3 and b["label"] not in BAYS and rnd.random() < 0.5:
        street_n = (-entrance_n[0], -entrance_n[1])
        run = sorted((e for e in edges if e[3] == street_n and not classify(e[0], e[2], e[3])[0]),
                     key=lambda e: e[1][0] * e[2][0] + e[1][1] * e[2][1])
        period = rnd.choice((3, 4))
        loggia_cells = {(e[0][0], e[0][1]) for k, e in enumerate(run) if k % period == 1}
    r_damage = rnd.random()
    damage = 2 if r_damage < (0.2 if lv < 3 else 0.1) and b["label"] not in NO_COLLAPSE else (1 if r_damage < 0.45 else 0)
    hero = True  # every building gets the dressed exterior now; how much depends on its decay level
    r_decay = rnd.random()
    decay = 1 if b["label"] in HERO else (3 if damage == 2 else (0 if r_decay < 0.25 else 1 if r_decay < 0.65 else 2 if r_decay < 0.9 else 3))
    if b["label"] in HERO:
        damage = 1
    elif decay >= 2:
        damage = max(damage, 1)
    D = DECAY[decay]
    collapse, cut = set(), lv
    if damage == 2:
        ci = rnd.choice((0, nu - 1)); cj = rnd.choice((0, nv - 1))
        size = rnd.choice((2, 3))
        collapse = {(i, j) for (i, j) in cells if abs(i - ci) < size and abs(j - cj) < size}
        cut = rnd.randint(max(0, lv - 3), lv - 1)  # storeys from `cut` upwards are gone in the corner

    def gone(i, j, s):
        return (i, j) in collapse and s >= cut and not ((i, j) in section_cells and s <= furnished_floors)

    ent_edges = []
    for key, (px, py), d, n in edges:
        theta = math.atan2(d[1], d[0])
        gable, is_entrance = classify(key, d, n)
        acc.add(parts["SM_T5_PlinthBand_A_Aged"], theta, px, py, CRAWL, {})
        acc.add(parts["SM_T5_Skirt_A_Aged"], theta, px, py, 0.0, {})
        if not gone(key[0], key[1], lv - 1):
            if rnd.random() < 0.12 * decay:  # parapet broken off: a gap with chunks on the roof
                for k in range(3):
                    cx_, cy_ = px + d[0] * rnd.uniform(0.3, 2.7) - n[0] * rnd.uniform(0.3, 1.5), py + d[1] * rnd.uniform(0.3, 2.7) - n[1] * rnd.uniform(0.3, 1.5)
                    w_ = rnd.uniform(0.2, 0.6)
                    acc.box(cx_, cx_ + w_, cy_, cy_ + w_ * 0.7, top, top + rnd.uniform(0.08, 0.25), "Facade_" + up)
            else:
                acc.add(parts["SM_T5_RoofEdge_A_Aged"], theta, px, py, top, {"Facade": "Facade_" + up})
        hall_edge = (key[0], key[1]) in hall and n == (-entrance_n[0], -entrance_n[1])
        for s in range(lv):
            z, face = Z0 + s * ST, {"Facade": "Facade_" + (ground if s == 0 else up)}
            if gone(key[0], key[1], s):
                continue
            if (damage >= 1 and key not in (section_key, hall_key) and not hall_edge and not (s == 0 and is_entrance)
                    and rnd.random() < PANEL_LOSS * D["ploss"]):
                for k in range(rnd.randint(3, 7)):  # bent rebar left standing in the hole
                    rx = rnd.uniform(0.2, AX - 0.2)
                    acc.box(px + d[0] * rx - 0.006, px + d[0] * rx + 0.006 + n[0] * 0.01, py + d[1] * rx - 0.006, py + d[1] * rx + 0.006 + n[1] * 0.01,
                            z + rnd.uniform(0.0, 0.4), z + ST - rnd.uniform(0.0, 1.2), "Metal")
                for k in range(3):  # broken-out panel: hole into the storey, chunks on the ground below
                    ox, oy = px + d[0] * rnd.uniform(0.3, 2.7) + n[0] * rnd.uniform(0.5, 2.5), py + d[1] * rnd.uniform(0.3, 2.7) + n[1] * rnd.uniform(0.5, 2.5)
                    w = rnd.uniform(0.4, 1.4)
                    acc.box(ox, ox + w, oy, oy + w * 0.6, -0.1, rnd.uniform(0.15, 0.45), "Facade_" + (ground if s == 0 else up))
                continue
            if hall_edge:
                if s == 0:  # one two-storey window panel covers both storeys
                    tw, twg = kit.Part("tw"), kit.Part("twg")
                    kulturhaus.tall_window(tw, AX, 2 * ST, twg, rnd)
                    acc.add(tw, theta, px, py, z, face)
                    glass.add(twg, theta, px, py, z, {})
                continue
            # panels never sit perfectly flush in an old precast block: shift each a little inward (decals stay in front)
            jit = rnd.uniform(0.0, 0.025)
            jpx, jpy = px - n[0] * jit, py - n[1] * jit
            if gable:
                acc.add(parts["SM_T5_WallPlate_A_Aged"], theta, jpx, jpy, z, face)
                if rnd.random() < D["spall"]:
                    acc.add(parts["SM_Decal_Wall_Spall"], theta, px, py, z, {})
                if rnd.random() < D["crack"]:
                    acc.add(parts["SM_Decal_Wall_Crack"], theta, px, py, z, {})
            elif s == 0 and is_entrance:
                acc.add(parts["SM_T5_Entrance_Open_A_Aged" if key in (section_key, hall_key) or hero else "SM_T5_Entrance_A_Aged"], theta, px, py, z, face)
                ent_edges.append((px, py, d, n))
                if hero and key not in (section_key, hall_key):  # door hanging open on its hinge
                    c, sn, dx0 = math.cos(theta), math.sin(theta), (AX - 1.2) / 2
                    acc.add(parts["SM_T5_DoorAjar"], theta - math.radians(rnd.uniform(35, 70)),
                            px + dx0 * c - 0.22 * sn, py + dx0 * sn + 0.22 * c, z, {})
                # world position 6 m in front of the door, facing it (for player starts / cameras)
                ex, ey = px + d[0] * AX / 2 + n[0] * 6.0, py + d[1] * AX / 2 + n[1] * 6.0
                eu, ev, fu, fv = ex, -ey, -n[0], n[1]
                entrances.append([round(cn + eu * dX[0] + ev * dY[0], 2), round(ce + eu * dX[1] + ev * dY[1], 2),
                                  round(math.degrees(math.atan2(fu * dX[1] + fv * dY[1], fu * dX[0] + fv * dY[0])), 1)])
                inward = (-n[0], -n[1])
                if not gone(key[0], key[1], lv - 1):
                    acc.add(parts["SM_T5_RoofVent_A_Aged"], theta, px + d[0] * 1.0 + inward[0] * 4, py + d[1] * 1.0 + inward[1] * 4, top, {"Facade": "Facade_" + up})
            elif b["label"] in SCHOOL and not gable:
                acc.add(parts["SM_T5_SchoolWindow_A_Aged"], theta, px, py, z, face)
                if rnd.random() < GLASS_SHARE:
                    sg = kit.Part("sg")
                    sg.box(0.5, 2.5, 0.145, 0.15, 0.65, 2.5, "Glass")
                    glass.add(sg, theta, px, py, z, {})
            elif s >= 1 and n != entrance_n and (key[0], key[1]) in loggia_cells:
                acc.add(parts["SM_T5_Loggia_A_Aged"], theta, px, py, z, face)
                if hero:
                    if rnd.random() < D["lglaze"]:
                        acc.add(parts["SM_T5_LoggiaGlazing"], theta, px, py, z, {})
                        if rnd.random() < 0.5:
                            glass.add(parts["SM_T5_LoggiaGlazingGlass"], theta, px, py, z, {})
                    if rnd.random() < D["lclutter"]:
                        acc.add(parts["SM_T5_LoggiaClutter"], theta, px, py, z, {})
            else:
                acc.add(parts["SM_T5_WindowPlate_A_Aged"], theta, jpx, jpy, z, face)
                if hero:  # damage varies panel to panel; uniform cracks read as a pattern
                    if rnd.random() < D["spall"]:
                        acc.add(parts["SM_Decal_Window_Spall"], theta, px, py, z, {})
                    if rnd.random() < D["crack"]:
                        acc.add(parts["SM_Decal_Window_Crack"], theta, px, py, z, {})
                    if rnd.random() < D["rust"]:
                        acc.add(parts["SM_Decal_RustSill"], theta, px, py, z, {})
                if s == 0 and rnd.random() < BOARDED:  # boarded-up ground floor windows
                    acc.add(parts["SM_T5_WindowBoards_A_Aged"], theta, px, py, z, {})
                if rnd.random() > D["frame"]:  # art bible 6: "ausgebaute Fenster"
                    acc.add(parts["SM_T5_WindowFrame_A_Aged"], theta, px, py, z, {})
                    if hero and rnd.random() < D["sash"]:  # a casement swung open (inward, or torn outward by wind)
                        c, sn = math.cos(theta), math.sin(theta)
                        hx, hy = kit.WIN_OX, kit.WIN["reveal"] + 0.16
                        swing = math.radians(rnd.uniform(40, 110)) * (1 if rnd.random() < 0.7 else -1)
                        if s < furnished_floors and (key[0], key[1]) in section_cells:
                            swing = -abs(swing)  # never into a furnished room: the player walks along these windows
                        sash_xy = (px + hx * c - hy * sn, py + hx * sn + hy * c)
                        acc.add(parts["SM_T5_SashOpen"], theta + swing, sash_xy[0], sash_xy[1], z, {})
                        if rnd.random() < 0.5:
                            glass.add(parts["SM_T5_SashGlassShard"], theta + swing, sash_xy[0], sash_xy[1], z, {})
                    r_glass = rnd.random()
                    if r_glass < GLASS_SHARE:
                        glass.add(parts["SM_T5_WindowGlass_A"], theta, px, py, z, {})
                    elif r_glass < GLASS_SHARE + BROKEN_SHARE:
                        glass.add(parts["SM_T5_WindowGlassBroken_A"], theta, px, py, z, {})
                    if s >= 1 and rnd.random() < CURTAIN:  # a trace of the people who lived there, used sparingly
                        acc.add(parts[rnd.choice(("SM_T5_CurtainRag_Red", "SM_T5_CurtainRag_Tulle"))], theta, px, py, z, {})
                if s >= 1 and n != entrance_n and (key[0], key[1]) in bay_cells:
                    acc.add(parts["SM_T5_Bay_A_Aged"], theta, px, py, z, {"Facade": "Facade_" + ground})

    if hero:
        for key, (px, py), d, n in edges:
            theta = math.atan2(d[1], d[0])
            gable, is_entrance = classify(key, d, n)
            if gone(key[0], key[1], lv - 1):
                continue
            if (key[0] if abs(d[0]) > abs(d[1]) else key[1]) % 4 == 0 and not is_entrance and rnd.random() < D["pipes"]:  # downpipe
                missing = rnd.randrange(lv) if rnd.random() < 0.6 else -1
                for s_ in range(lv):
                    if s_ != missing:
                        acc.add(parts["SM_T5_PipeSeg"], theta, px, py, Z0 + s_ * ST, {})
                acc.add(parts["SM_T5_PipeHead"], theta, px, py, top, {})
                if missing != 0:
                    acc.add(parts["SM_T5_PipeOutlet"], theta, px, py, Z0 - 0.9, {})
            if rnd.random() < 0.06:  # loose cable from the roof edge
                acc.add(parts["SM_T5_Cable_%d" % rnd.choice((16, 32, 48))], theta, px + d[0] * rnd.uniform(0.3, 2.7), py + d[1] * rnd.uniform(0.3, 2.7), top - 0.1, {})
        roof_cells = rnd.sample(sorted(cells), min(len(cells), 6))
        if lv >= 3:
            for k, (i, j) in enumerate(roof_cells[:rnd.randint(1, 4)]):  # TV antennas, one fallen
                x0, y0 = cell_xy(i, j)
                acc.add(parts["SM_T5_AntennaFallen" if k == 0 else "SM_T5_Antenna"], rnd.uniform(0, math.pi), x0 + AX / 2, y0 + AX / 2, top, {})
        else:  # low barracks: rusty stove pipes on the roof (user photo 1, 2026-11-07)
            for (i, j) in roof_cells[:rnd.randint(3, 6)]:
                x0, y0 = cell_xy(i, j)
                acc.add(parts["SM_T5_StovePipe"], 0.0, x0 + rnd.uniform(0.8, AX - 0.8), y0 + rnd.uniform(0.8, AX - 0.8), top, {})

    # slabs per cell (ground floor, storeys, roof), party walls every 2 axes, spine wall at mid depth
    for (i, j) in cells:
        x0, y0 = cell_xy(i, j)
        for s in range(lv + 1):
            if (i, j) in hall and 0 < s < lv:
                continue  # double-height hall
            if gone(i, j, min(s, lv - 1)) and s > 0:
                continue  # collapsed corner
            if 0 < s < furnished_floors and (i, j) in shaft:
                continue  # stair shaft over the half landing (interiors.stairwell)
            z = Z0 + s * ST
            # pull the slab edge 3 cm in from the facade: flush with the panels' outer face it overlapped the panel
            # below by ~20 cm in the same plane and z-fought as a flickering band at every storey (user video 2026-11-07)
            if s == lv and rnd.random() < D["roofhole"] * (2.0 if lv <= 2 else 1.0):
                for k in range(4):  # roof fallen in: only the beams are left (user photo 1)
                    if rnd.random() < 0.75:
                        bx = x0 + 0.3 + k * 0.8
                        acc.box(bx, bx + 0.12, y0, y0 + AX, z - 0.2, z - 0.02, "Wood")
                continue
            ix0 = SLAB_INSET if (i - 1, j) not in cells else 0.0
            ix1 = SLAB_INSET if (i + 1, j) not in cells else 0.0
            iy0 = SLAB_INSET if (i, j + 1) not in cells else 0.0   # Blender y is mirrored: j+1 lies at -y
            iy1 = SLAB_INSET if (i, j - 1) not in cells else 0.0
            acc.box(x0 + ix0, x0 + AX - ix1, y0 + iy0, y0 + AX - iy1, z - 0.22, z, "Concrete")
        for s in range(lv):
            if gone(i, j, s):
                continue
            za, zb = Z0 + s * ST, Z0 + (s + 1) * ST - 0.22
            # the furnished section brings its own ground-floor walls
            if (s < furnished_floors and ((i, j) in section_cells or (i - 1, j) in section_cells)) or \
                    (s == 1 and ((i, j) in stair_col or (i - 1, j) in stair_col)):
                party = False
            else:
                party = True
            if (i, j) in hall or (s == 0 and (i, j) in corridor and (i - 1, j) in corridor):
                party = False
            if party and i % 2 == 0 and (i - 1, j) in cells:
                acc.box(x0 - 0.08, x0 + 0.08, y0 + 0.4, y0 + AX - 0.4, za, zb, "Interior")
            spine_in_section = (s < furnished_floors and ((i, j) in section_cells or (i, j - 1) in section_cells or (i, j) in corridor
                                            or (i, j - 1) in corridor)) or (i, j) in hall or (i, j - 1) in hall or \
                (s == 1 and ((i, j) in stair_col or (i, j - 1) in stair_col))
            if j == nv // 2 and (i, j - 1) in cells and nv >= 4 and not spine_in_section:
                acc.box(x0 + 0.4, x0 + AX - 0.4, y0 + AX - 0.08, y0 + AX + 0.08, za, zb, "Interior")
    street = b["label"].split("_")[1] if b["label"].count("_") >= 2 else None
    stencil_view = None
    if ent_edges and street in STREET_RU:
        px, py, d, n = min(ent_edges, key=lambda e: e[0] * e[2][0] + e[1] * e[2][1])  # first entrance along the facade
        add_stencil(acc, "%s %s" % (STREET_RU[street], b["label"].rsplit("_", 1)[1]), px, py, d, n, Z0 + 2.85)
        if hero:  # flat numbers above the other entrances (ANNAHME: 4 flats x 5 storeys per entrance)
            per = 4 * lv
            for k, (qx, qy, qd, qn) in enumerate(sorted(ent_edges, key=lambda e: e[0] * e[2][0] + e[1] * e[2][1])[1:], start=1):
                add_stencil(acc, "КВ. %d-%d" % (k * per + 1, (k + 1) * per), qx, qy, qd, qn, Z0 + 2.85)
        stencil_view = (px + d[0] * AX / 2, py + d[1] * AX / 2, n)

    if b["label"] in KULTURHAUS:  # family silhouettes on a windowless gable wall, as on the user's photo
        gab = sorted(((p0, d) for key, p0, d, n in edges if classify(key, d, n)[0]), key=lambda e: (e[0][0], e[0][1]))
        if gab:
            (gx, gy), d = gab[0]
            add_mural(acc, [(murals.family, 0.5, 0.15, 1.0)], gx, gy, d, AX)

    mural_view = None
    if b["label"] in GABLE_MURALS:
        gables = {}
        for key, p0, d, n in edges:
            if classify(key, d, n)[0]:
                gables.setdefault(n, []).append((p0, d))
        if gables:
            n, segs = sorted(gables.items())[0]
            segs.sort(key=lambda e: e[0][0] * e[1][0] + e[0][1] * e[1][1])
            (gx, gy), d = segs[0]
            add_mural(acc, murals.MURALS[GABLE_MURALS[b["label"]]], gx, gy, d, len(segs) * AX)
            mural_view = (gx, gy, d, n, len(segs) * AX)

    cameras, section_frame, clues, room_lights = [], None, {}, []

    def to_world(x, y):  # Blender (x, y) -> (north, east): undo the v mirror, then the building rotation
        u, v = x, -y
        return cn + u * dX[0] + v * dY[0], ce + u * dX[1] + v * dY[1]

    if stencil_view and b["label"] == "PLA_Lenina_8":  # evidence that the house number reads left-to-right
        sx, sy, n = stencil_view
        n0, e0 = to_world(sx + n[0] * 6, sy + n[1] * 6)
        n1, e1 = to_world(sx, sy)
        cameras.append({"name": "lenina_8-house-number", "north_m": round(n0, 2), "east_m": round(e0, 2),
                        "z_m": round(b["ground_m"] - 0.1 + Z0 + 2.4, 2), "yaw_deg": round(math.degrees(math.atan2(e1 - e0, n1 - n0)), 1), "pitch_deg": 6.0})
    if mural_view:  # camera 28 m in front of the gable centre, looking up at the mosaic
        gx, gy, d, n, w = mural_view
        mx, my = gx + d[0] * w / 2, gy + d[1] * w / 2
        n0, e0 = to_world(mx + n[0] * 28, my + n[1] * 28)
        n1, e1 = to_world(mx, my)
        cameras.append({"name": b["label"].replace("PLA_", "").lower() + "-mural", "north_m": round(n0, 2), "east_m": round(e0, 2),
                        "z_m": round(b["ground_m"] + 6.0, 2), "yaw_deg": round(math.degrees(math.atan2(e1 - e0, n1 - n0)), 1), "pitch_deg": 22.0})

    if hall:
        xs = [u0 + i * AX for i, _ in hall] + [u0 + (i + 1) * AX for i, _ in hall]
        ys = [-(v0 + (j + 1) * AX) for _, j in hall] + [-(v0 + j * AX) for _, j in hall]
        hx0, hx1, hy0, hy1 = min(xs), max(xs), min(ys), max(ys)
        facade_y = hy0 if entrance_n == (0, 1) else hy1   # street side = opposite of the entrance side
        door = None
        if hall_key:
            dx0 = u0 + hall_key[0] * AX
            door = (dx0 + 0.6, dx0 + AX - 0.6)
        views = kulturhaus.build_hall(acc, hx0, hx1, hy0, hy1, facade_y, Z0, Z0 + lv * ST - 0.22, seed=1964, door=door)
        for name, (vx, vy, vz, _) in views.items():
            tx, ty = ((hx1, (hy0 + hy1) / 2) if name == "back" else (hx0 + 3.0, facade_y))
            n0, e0 = to_world(vx, vy)
            n1, e1 = to_world(tx, ty)
            cameras.append({"name": "kulturhaus-" + name, "north_m": round(n0, 2), "east_m": round(e0, 2),
                            "z_m": round(b["ground_m"] - 0.1 + vz, 2), "yaw_deg": round(math.degrees(math.atan2(e1 - e0, n1 - n0)), 1)})

    if section_key:
        sp = kit.Part("section")
        kind = INTERIOR_SECTIONS[b["label"]]
        if b["label"] in residential.HOUSES:
            built = residential.build(sp, b["label"], AX, ST, T, seed=8)
        else:
            built = {"shop": interiors.shop, "flats": interiors.section, **story_rooms.ROOMS}[kind](sp, AX, ST, T, seed=8)
        acc.add(sp, math.atan2(sd[1], sd[0]), spx, spy, Z0, {})
        if kind == "shop":  # shop sign over the entrance: board + red Cyrillic letters
            ex, ey = spx + sd[0] * 0.2, spy + sd[1] * 0.2
            sign = kit.Part("sign")
            sign.box(0.0, AX - 0.4, -0.06, 0.0, 0.0, 0.55, "Lime")
            acc.add(sign, math.atan2(sd[1], sd[0]), ex, ey, Z0 + 2.62, {})
            add_stencil(acc, "МАГАЗИН", spx, spy, sd, sn, Z0 + 2.7, size=0.42, mat="Mural_Red", out=0.075)
        left = (-sd[1], sd[0])
        def world(a, bb):  # section (along, inward) -> (north, east), via Blender (x, y) and the mirrored v
            x, y = spx + sd[0] * a + left[0] * bb, spy + sd[1] * a + left[1] * bb
            u, v = x, -y
            return cn + u * dX[0] + v * dY[0], ce + u * dX[1] + v * dY[1]
        views = story_rooms.VIEWS.get(kind) or ((("flatA-room", (-3.6, 1.0), (-5.6, 2.6)), ("flatA-kitchen", (-0.5, 3.2), (-2.2, 0.4)),
                  ("stairwell", (1.5, 0.7), (1.0, 5.0)), ("flatB-room", (8.4, 1.1), (6.1, 2.2))) if kind == "flats" else
                 (("shop", (1.5, 0.8), (-2.0, 4.6)), ("shop-counter", (7.5, 1.0), (0.0, 4.0))))
        prefix = b["label"].replace("PLA_", "").lower().replace("_", "") + "-"
        # section frame in world metres (north, east): origin, +1 m along the facade, +1 m inward (walk checks)
        o, a1, i1 = world(0, 0), world(1, 0), world(0, 1)
        section_frame = [list(map(lambda v: round(v, 3), o)), [round(a1[0] - o[0], 4), round(a1[1] - o[1], 4)],
                         [round(i1[0] - o[0], 4), round(i1[1] - o[1], 4)]]
        floor_z = b["ground_m"] - 0.1 + Z0   # ground-floor level in world metres (as the camera heights below)
        for lx, ly, lz in getattr(built, "lights", []):
            ln, le = world(lx, ly)
            room_lights.append([round(ln,3), round(le,3), round(floor_z+lz,3)])
        for name, (cx, cy, cz) in (getattr(built, "clues", None) or {}).items():
            n_, e_ = world(cx, cy)
            clues[name] = [round(n_, 3), round(e_, 3), round(floor_z + cz, 3)]
        if kind == "homes": views = []
        views = [(name, frm, to, 0) for name, frm, to in views] + getattr(built, "extra_views", [])
        for name, frm, to, floor in views:
            n0, e0 = world(*frm)
            n1, e1 = world(*to)
            cameras.append({"name": prefix + name, "north_m": round(n0, 2), "east_m": round(e0, 2),
                            "z_m": round(b["ground_m"] - 0.1 + Z0 + 1.6 + floor * ST, 2), "yaw_deg": round(math.degrees(math.atan2(e1 - e0, n1 - n0)), 1)})
    if lv <= 2 and len(local) <= 4 and not collapse and not hall and min(nu, nv) * AX <= 15.0:
        # older two-storey blocks: gable roof in corrugated asbestos-cement slate (photo 6480171585), ANNAHME
        add_gable_roof(acc, u0, -(v0 + nv * AX), u0 + nu * AX, -v0, top + PARAPET * 0.5, min(nu, nv) * AX)
    if collapse:  # rubble cone of the collapsed corner: slabs, panels, plaster
        xs = [u0 + i * AX for i, _ in collapse] + [u0 + (i + 1) * AX for i, _ in collapse]
        ys = [-(v0 + (j + 1) * AX) for _, j in collapse] + [-(v0 + j * AX) for _, j in collapse]
        cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
        rad = (max(xs) - min(xs)) * 0.75
        for _ in range(140 + 40 * (lv - cut)):
            a, r = rnd.uniform(0, 2 * math.pi), rad * math.sqrt(rnd.random())
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            hz = (1 - r / rad) * (1.2 + 0.9 * (lv - cut)) * rnd.random()
            w, dd = rnd.uniform(0.3, 2.2), rnd.uniform(0.2, 1.2)
            acc.box(x, x + w, y, y + dd, hz - 0.3, hz + rnd.uniform(0.1, 0.3), rnd.choice(("Concrete", "Concrete", "Facade_" + up, "Lime")))
    # piles: every second grid point on the cell corners, three rows across
    rows = {0, nv // 2, nv}
    for i in range(0, nu + 1, G["pile"]["spacing_axes"]):
        for j in rows:
            if any((i + a, j + c) in cells for a in (-1, 0) for c in (-1, 0)):
                x, y = u0 + i * AX, -(v0 + j * AX)
                acc.add(parts["SM_T5_Pile_A_Aged"], 0.0, min(max(x, u0 + 0.3), u0 + nu * AX - 0.7) , y - 0.2, 0.0, {})

    # plants for the vegetation scatter (world north/east, z above the terrain origin like scatter.json):
    # birch saplings and weeds on the roof and against the base of the hero buildings
    plants = []
    if hero:
        for (i, j) in rnd.sample(sorted(cells), min(len(cells), D["roofplants"])):
            x0, y0 = cell_xy(i, j)
            nn, ee = to_world(x0 + rnd.uniform(0.5, AX - 0.5), y0 + rnd.uniform(0.5, AX - 0.5))
            plants.append([rnd.choice(("grass", "grass", "shrub", "birch")), round(nn, 2), round(ee, 2), round(b["ground_m"] - 0.1 + top, 2)])
        for key, (px, py), d, n in edges:
            if rnd.random() < D["base"]:
                nn, ee = to_world(px + d[0] * rnd.uniform(0.3, 2.7) + n[0] * 0.8, py + d[1] * rnd.uniform(0.3, 2.7) + n[1] * 0.8)
                plants.append([rnd.choice(("shrub", "birch", "grass")), round(nn, 2), round(ee, 2), None])

    glass_ob = None
    if glass.faces:
        glass_ob = glass.build()
    ob = acc.build()
    paint_decay(ob, rnd)
    return ob, glass_ob, {"label": b["label"], "mesh": acc.name, "glass_mesh": glass.name if glass_ob else None, "folder": b["folder"], "north_m": cn, "east_m": ce,
                "ground_m": b["ground_m"], "yaw_deg": math.degrees(yaw), "levels": lv, "cells": len(cells),
                "scheme": [up, ground], "materials": acc.mats, "plants": plants, "tris": len(acc.faces) * 2,
                "entrances": entrances, "cameras": cameras, "damage": damage, "decay": decay,
                "section_frame": section_frame, "clues": clues, "room_lights": room_lights, "furnished_floors": furnished_floors if section_key else 0}


def paint_decay(ob, rnd):
    """Vertex colour R = plaster loss (art bible 8.6): strongest just above the plinth, plus random patches."""
    me = ob.data
    col = me.color_attributes["Col"]
    facade = {i for i, m in enumerate(me.materials) if m.name.startswith("Facade")}
    vrnd = {}
    for poly in me.polygons:
        if poly.material_index not in facade:
            continue
        for li in poly.loop_indices:
            vi = me.loops[li].vertex_index
            z = me.vertices[vi].co.z
            if vi not in vrnd:
                vrnd[vi] = rnd.random()
            base = max(0.0, 1.0 - (z - Z0) / 1.4) * 0.55 * vrnd[vi]
            patch = 0.5 if vrnd[vi] > 0.93 else 0.0
            col.data[li].color = (min(1.0, base + patch), 0.0, 0.0, 1.0)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT, exist_ok=True)
    parts = kit.make_parts()
    polys = osm_polygons()
    manifest = []
    for b in DATA["buildings"]:
        # unaddressed OSM buildings (sheds, works) are built too: as blockout boxes they read as white placeholders
        if not b["label"].startswith("PLA_") or b["length_m"] * b["width_m"] < 30:
            continue
        if ONLY and b["label"] not in ONLY:
            continue
        for o in list(bpy.data.objects):
            bpy.data.objects.remove(o, do_unlink=True)
        for m in list(bpy.data.meshes):
            bpy.data.meshes.remove(m)
        ob, glass_ob, info = build_one(b, polys.get(b["osm"]) or rect_poly(b), parts)
        for o, name in ((ob, info["mesh"]), (glass_ob, info["glass_mesh"])):
            if o is None:
                continue
            bpy.ops.object.select_all(action="DESELECT")
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, name + ".fbx"), use_selection=True, apply_unit_scale=True,
                                     apply_scale_options="FBX_SCALE_UNITS", mesh_smooth_type="FACE", colors_type="SRGB",
                                     add_leaf_bones=False, bake_anim=False)
        manifest.append(info)
        print("BLD %-26s lv=%d cells=%3d tris=%6d scheme=%s" % (info["label"], info["levels"], info["cells"], info["tris"], info["scheme"]))
    built_count = len(manifest)
    path = os.path.join(OUT, "buildings_manifest.json")
    if ONLY:
        old = json.load(open(path))
        updated = {b["label"]: b for b in manifest}
        manifest = [updated.pop(b["label"], b) for b in old] + list(updated.values())
    json.dump(manifest, open(path, "w"), ensure_ascii=False, indent=1)
    print("BUILDINGS OK", built_count)


main()
