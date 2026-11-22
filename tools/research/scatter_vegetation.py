"""Scatter positions for birches, larches and shrubs (briefing V3 step 4, art bible 6).

Usage: python -I scatter_vegetation.py <blockout.json> <out.json> <tile.tif>...
Rules (ANNAHME, tuned by eye against the 2011 photos): birches in the courtyards 6-30 m from facades,
dwarf shrubs across the town, larches thickening with distance from the centre and on slopes.
Nothing on roads (5 m), the river (8 m) or inside building footprints (+3 m). Deterministic seed.
Positions are local metres (east, north) with ground height relative to the origin, like blockout.json.
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
import dem_to_obj as dem

rnd = random.Random(2011)

def seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)

def main():
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    if sys.argv[3].endswith(".obj"):  # no DEM tiles here: sample the terrain mesh the game uses
        h0 = dem.load_obj(sys.argv[3])
    else:
        dem.load_tiles(sys.argv[3:])
        h0 = dem.ground(0.0, 0.0)
    from terrain_mesh import TerrainMesh  # objects sit on the rendered mesh, not the raw DEM samples
    gz = TerrainMesh(os.path.join(os.path.dirname(sys.argv[2]), "..", "terrain", "terrain_kadykchan_8km.obj")).z

    def gfoot(x, y, r):
        """Lowest ground under a rigid prop's footprint: set there it never floats on a slope, the uphill side sinks in."""
        return min([gz(x, y)] + [gz(x + r * math.cos(k * math.pi / 4), y + r * math.sin(k * math.pi / 4)) for k in range(8)])
    # cheap spatial test lists
    lines = [(r["points_m"], 5.0 + r["width_m"] / 2) for r in data["roads"]] + [(r["points_m"], 8.0) for r in data["rivers"]]
    blds = []
    for b in data["buildings"]:
        a = math.radians(b["axis_deg_from_east"])
        lv = int(b["levels"]) if (b["levels"] or "").isdigit() else 2
        hw = min(b["width_m"] / 2, 6.0) if lv >= 3 and not b["label"].startswith("PLA_OSM_") else b["width_m"] / 2  # kit depth 12 m
        blds.append((b["east_m"], b["north_m"], math.cos(a), math.sin(a), b["length_m"] / 2, hw))

    def facade_dist(x, y):
        if in_section(x, y):
            return -1
        best = 1e9
        for cx, cy, ca, sa, hl, hw in blds:
            u, v = (x - cx) * ca + (y - cy) * sa, -(x - cx) * sa + (y - cy) * ca
            du, dv = max(abs(u) - hl, 0), max(abs(v) - hw, 0)
            best = min(best, math.hypot(du, dv) if (du or dv) else -1)
        return best

    # keep the ground in front of every entrance free (player start, paths); entrances come from build_buildings.py
    entrances, sections = [], []
    man = os.path.join(os.path.dirname(sys.argv[2]), "..", "buildings", "buildings_manifest.json")
    if os.path.exists(man):
        entrances = [(e, n) for b in json.load(open(man, encoding="utf-8")) for n, e, _ in b.get("entrances", [])]
        sections = [b["section_frame"] for b in json.load(open(man, encoding="utf-8")) if b.get("section_frame")]

    def in_section(x, y):
        """Inside a furnished section (x = east, y = north). The deep flats reach up to 1.5 m past the blockout
        rectangle, and a willow grew in Orlow's living room (2026-11-08)."""
        for (n0, e0), (an, ae), (inn, ie) in sections:
            dn, de = y - n0, x - e0
            det = an * ie - inn * ae
            a, i = (dn * ie - inn * de) / det, (an * de - ae * dn) / det
            if -8.0 < a < 11.0 and -2.0 < i < 14.0:  # plus a crown width outside the facades
                return True
        return False

    # the adit site (tools/research/mine_site.py) is cut into the slope: keep it and its heap free
    site_f = os.path.join(os.path.dirname(sys.argv[2]), "..", "mine", "adit_site.json")
    adit = json.load(open(site_f))["portal"] if os.path.exists(site_f) else None

    def clear(x, y, margin, wall=3.0):
        if any(abs(x - ex) < 8 and abs(y - ey) < 8 for ex, ey in entrances):
            return False
        if adit and math.hypot(x - adit[0], y - adit[1]) < 75:
            return False
        for pts, w in lines:
            for (ax, ay, _), (bx, by, _) in zip(pts, pts[1:]):
                if abs(x - ax) < 400 and abs(y - ay) < 400 and seg_dist(x, y, ax, ay, bx, by) < w + margin:
                    return False
        return facade_dist(x, y) > wall

    def slope(x, y):
        return abs(dem.ground(x + 15, y) - dem.ground(x - 15, y)) / 30 + abs(dem.ground(x, y + 15) - dem.ground(x, y - 15)) / 30

    out = {"origin_height": h0, "birch": [], "larch": [], "shrub": [], "sapling": [], "willow": []}
    tries = 0
    while len(out["birch"]) < 900 and tries < 80000:  # courtyards
        tries += 1
        x, y = rnd.uniform(-700, 700), rnd.uniform(-700, 700)
        d = facade_dist(x, y)
        if 6 <= d <= 30 and clear(x, y, 1.0):
            out["birch"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.7, 1.25), 2)])
    tries = 0
    while len(out["shrub"]) < 1500 and tries < 60000:  # town and fringe
        tries += 1
        r, a = 1500 * math.sqrt(rnd.random()), rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if clear(x, y, 0.5):
            out["shrub"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.6, 1.4), 2)])
    out["grass"] = []
    tries = 0
    # neglect, not a lawn (atmosphere-target.md): rank weeds against the building bases, the rest in irregular
    # patches around random centres, with bare ground between them
    patches = []
    while len(patches) < 260:
        r, a = 600 * math.sqrt(rnd.random()), rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if 3 < facade_dist(x, y) < 40:
            patches.append((x, y, rnd.uniform(2.0, 7.0)))
    if os.path.exists(os.path.join(os.path.dirname(sys.argv[1]), "satellite-additions-2026-11-07.json")):
        for e, n, size in json.load(open(os.path.join(os.path.dirname(sys.argv[1]), "satellite-additions-2026-11-07.json"))).get("foundations", []):
            patches.append((e, n, size / 3))
    while len(out["grass"]) < 9000 and tries < 300000:
        tries += 1
        if rnd.random() < 0.4:  # wall band
            r, a = 600 * math.sqrt(rnd.random()), rnd.uniform(0, 2 * math.pi)
            x, y = r * math.cos(a), r * math.sin(a)
            ok, scale = 0.25 < facade_dist(x, y) < 1.8 and clear(x, y, 0.3, wall=0.25), rnd.uniform(1.0, 1.6)
        else:
            px, py, spread = patches[rnd.randrange(len(patches))]
            x, y = rnd.gauss(px, spread), rnd.gauss(py, spread)
            ok, scale = clear(x, y, 0.3), rnd.uniform(0.6, 1.3)
        if ok:
            out["grass"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(scale, 2)])
    # grass breaking through the roads inside town (atmosphere-target.md: vegetation through cracks): along both
    # wheel-worn edges and the crown line, small clumps, never in front of entrances
    for r in data["roads"]:
        p = r["points_m"]
        for (ax, ay, _), (bx, by, _) in zip(p, p[1:]):
            L = math.hypot(bx - ax, by - ay)
            if L < 1 or math.hypot(ax, ay) > 900:
                continue
            nx, ny = -(by - ay) / L, (bx - ax) / L
            for _ in range(int(L / 6)):
                t, lane = rnd.random(), rnd.choice((-0.45, 0.0, 0.45))
                off = lane * r["width_m"] + rnd.gauss(0, 0.25)
                x, y = ax + (bx - ax) * t + nx * off, ay + (by - ay) * t + ny * off
                if rnd.random() < 0.55 or any(abs(x - ex) < 8 and abs(y - ey) < 8 for ex, ey in entrances):
                    continue
                out["grass"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.35, 0.75), 2)])
    # roof and base plants of the hero buildings (build_buildings.py manifest); z None = on the terrain
    if os.path.exists(man):
        for b in json.load(open(man, encoding="utf-8")):
            for kind, n, e, z in b.get("plants", []):
                zz = gz(e, n) if z is None else z
                sc = {"birch": rnd.uniform(0.25, 0.45), "shrub": rnd.uniform(0.5, 0.9), "grass": rnd.uniform(0.6, 1.1)}[kind]
                if z is not None and kind == "birch":   # on roofs: saplings, and mostly weeds instead (photos)
                    kind, sc = ("birch", sc * 0.5) if rnd.random() < 0.35 else ("grass", rnd.uniform(0.7, 1.2))
                rot = round(rnd.uniform(0, 360))
                if z is None and any(abs(e - ex) < 8 and abs(n - ey) < 8 for ex, ey in entrances):
                    continue  # base plants too keep the doors free (story-room doors were blocked, 2026-11-07)
                out[kind].append([round(e, 1), round(n, 1), round(zz, 2), rot, round(sc, 2)])
    tries = 0
    # closed larch taiga around the town and up the hills (user photo 2026-11-08), thinning only near the houses;
    # area-uniform radius so the ring does not crowd inward
    while len(out["larch"]) < 110000 and tries < 3000000:
        tries += 1
        r, a = math.sqrt(rnd.uniform(250 ** 2, 3800 ** 2)), rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if abs(x) > 3900 or abs(y) > 3900:
            continue
        p = 0.3 + 0.7 * min(1.0, (r - 250) / 700)
        if rnd.random() < p and clear(x, y, 2.0):
            out["larch"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.6, 1.3), 2)])
    # young larches where the forest creeps back into the town fringe
    tries = 0
    while len(out["sapling"]) < 15000 and tries < 500000:
        tries += 1
        r, a = math.sqrt(rnd.uniform(150 ** 2, 1300 ** 2)), rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        if clear(x, y, 1.0, wall=2.0):
            out["sapling"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.7, 1.3), 2)])
    # --- street furniture (briefing V3 "Schutt an Hauswänden", V10 C "Garagen, Kioske, Tanks, Leitungen"); ANNAHME positions
    out["pipes"], out["rubble"], out["tanks"], out["garages"] = [], [], [], []
    for r in data["roads"]:
        if r["kind"] not in ("residential", "service"):
            continue
        pts = r["points_m"]
        if min(math.hypot(x, y) for x, y, _ in pts) > 700:
            continue
        line = []
        for (ax, ay, _), (bx, by, _) in zip(pts, pts[1:]):  # heat pipeline 5 m beside the road, supports every 6 m
            seg = math.hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / (seg or 1), (bx - ax) / (seg or 1)
            off = 5.0 + r["width_m"] / 2
            for k in range(int(seg // 6) + 1):
                t = k * 6 / (seg or 1)
                x, y = ax + (bx - ax) * t + nx * off, ay + (by - ay) * t + ny * off
                if facade_dist(x, y) > 2.0:
                    line.append([round(x, 1), round(y, 1), round(gz(x, y), 2)])
                elif len(line) > 1:
                    out["pipes"].append(line); line = []
                else:
                    line = []
        if len(line) > 1:
            out["pipes"].append(line)
    for cx, cy, ca, sa, hl, hw in blds:  # rubble heaps along the long walls
        if hl * hw > 2500:
            continue
        for _ in range(rnd.randint(4, 9)):
            u, side = rnd.uniform(-hl, hl), rnd.choice((-1, 1))
            v = side * (hw + rnd.uniform(0.6, 2.0))
            x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
            out["rubble"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.6, 1.5), 2)])
    # ground litter (user reference 2026-11-07): stones, concrete chunks, boards and sticks, densest near the walls;
    # bigger heaps of broken panels against some bases
    out["debris"], out["heaps"] = [], []
    tries = 0
    while len(out["debris"]) < 5000 and tries < 200000:
        tries += 1
        r, a = 650 * math.sqrt(rnd.random()), rnd.uniform(0, 2 * math.pi)
        x, y = r * math.cos(a), r * math.sin(a)
        fd = facade_dist(x, y)
        if fd < 0.3 or rnd.random() > math.exp(-max(fd, 0) / 18):
            continue
        out["debris"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.6, 1.4), 2)])
    for cx, cy, ca, sa, hl, hw in blds:
        for _ in range(rnd.randint(0, 3)):
            u, side = rnd.uniform(-hl * 0.9, hl * 0.9), rnd.choice((-1, 1))
            v = side * (hw + rnd.uniform(0.8, 2.2))
            x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
            if clear(x, y, 0.5, wall=0.5):
                out["heaps"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(1.6, 2.6), 2)])
    # the town is overgrown (user photos): yellow-green willow/alder thickets and young larches/birches everywhere
    # except on roads, in footprints and in front of entrances; clustered, denser away from the walls
    # (2026-11-08: four times the thickets, as willow/alder bushes and young larches instead of scaled-up dwarf shrubs)
    thick = [(rnd.uniform(-750, 750), rnd.uniform(-650, 650), rnd.uniform(8, 30)) for _ in range(900)]
    tries, placed = 0, 0
    while tries < 1000000 and placed < 70000:
        tries += 1
        cx, cy, spread = thick[rnd.randrange(len(thick))]
        x, y = rnd.gauss(cx, spread), rnd.gauss(cy, spread)
        if clear(x, y, 0.5, wall=1.5):
            kind = "willow" if rnd.random() < 0.62 else "sapling"
            out[kind].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.7, 1.3), 2)])
            placed += 1
    added = 0
    while added < 1500 and tries < 260000:
        tries += 1
        x, y = rnd.uniform(-750, 750), rnd.uniform(-650, 650)
        if clear(x, y, 1.0, wall=4.0):
            kind = "sapling" if rnd.random() < 0.55 else "birch"
            sc = rnd.uniform(0.8, 1.3) if kind == "sapling" else rnd.uniform(0.3, 0.6)
            out[kind].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360)), round(sc, 2)])
            added += 1
    # things left behind (user 2026-11-07: "the town is very empty"): wrecks, barrels, scrap, fences, furniture,
    # utility poles, bus stops, a ruin field of collapsed wooden houses in the south, the club's bust, a chimney
    for k in ("cars", "barrels", "fences", "poles", "furniture", "busstops", "busts", "chimneys", "scrap", "woodruins"):
        out[k] = []
    def spot(r_max, wall, margin=1.0):
        for _ in range(400):
            x, y = rnd.uniform(-r_max, r_max), rnd.uniform(-r_max * 0.85, r_max * 0.85)
            if clear(x, y, margin, wall=wall):
                return x, y
        return None
    for kind, count, rmax, wall in (("cars", 28, 650, 4.0), ("furniture", 45, 600, 2.0)):
        for _ in range(count):
            p_ = spot(rmax, wall)
            if p_:
                out[kind].append([round(p_[0], 1), round(p_[1], 1), round(gfoot(*p_, 2.5), 2), round(rnd.uniform(0, 360))])
    for _ in range(45):                                    # barrel groups
        p_ = spot(650, 3.0)
        if p_:
            for _ in range(rnd.randint(1, 5)):
                x, y = p_[0] + rnd.uniform(-1.5, 1.5), p_[1] + rnd.uniform(-1.5, 1.5)
                out["barrels"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(rnd.uniform(0, 360))])
    for _ in range(60):
        p_ = spot(650, 3.0)
        if p_:
            out["scrap"].append([round(p_[0], 1), round(p_[1], 1), round(gz(*p_), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.7, 1.6), 2)])
    for cx, cy, ca, sa, hl, hw in blds:                   # fence runs beside the low buildings
        if hl * hw < 900 and rnd.random() < 0.6:
            for _ in range(rnd.randint(1, 3)):
                u, side = rnd.uniform(-hl, hl), rnd.choice((-1, 1))
                v = side * (hw + rnd.uniform(4, 10))
                x, y = cx + u * ca - v * sa, cy + u * sa + v * ca
                if clear(x, y, 1.0):
                    out["fences"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(math.degrees(math.atan2(sa, ca)))])
    for r in data["roads"]:                                # utility poles along the roads, some gone
        pts, acc_d = r["points_m"], 0.0
        for (ax, ay, _), (bx, by, _) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay)
            if L < 1 or math.hypot(ax, ay) > 1100:
                continue
            nx, ny = -(by - ay) / L, (bx - ax) / L
            t = (35 - acc_d % 35) / L
            while t < 1:
                x, y = ax + (bx - ax) * t + nx * (r["width_m"] / 2 + 2.5), ay + (by - ay) * t + ny * (r["width_m"] / 2 + 2.5)
                if rnd.random() < 0.85 and facade_dist(x, y) > 3:
                    out["poles"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(math.degrees(math.atan2(by - ay, bx - ax)))])
                t += 35 / L
            acc_d += L
    for r in sorted(data["roads"], key=lambda r: -r["width_m"]):   # bus shelters on the three widest roads near town
        pts = [q for q in r["points_m"] if math.hypot(q[0], q[1]) < 600]
        if len(pts) >= 2 and len(out["busstops"]) < 3:
            (ax, ay, _), (bx, by, _) = pts[len(pts) // 2 - 1], pts[len(pts) // 2]
            L = math.hypot(bx - ax, by - ay) or 1
            nx, ny = -(by - ay) / L, (bx - ax) / L
            x, y = (ax + bx) / 2 + nx * (r["width_m"] / 2 + 3), (ay + by) / 2 + ny * (r["width_m"] / 2 + 3)
            out["busstops"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 2.0), 2), round(math.degrees(math.atan2(by - ay, bx - ax)))])
    n_ruin = 0
    while n_ruin < 140:                                    # ruin field of the private wooden houses, south of town
        x, y = rnd.uniform(-650, 350), rnd.uniform(-650, -250)
        if clear(x, y, 3.0, wall=8.0):
            out["woodruins"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 4.0), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.8, 1.2), 2)])
            n_ruin += 1
    if os.path.exists(man):
        for b in json.load(open(man, encoding="utf-8")):
            if b["label"] == "PLA_Yuzhnaya_9" and b.get("entrances"):   # bust in front of the club, facing it
                n0, e0, yaw = b["entrances"][len(b["entrances"]) // 2]
                dn, de = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
                x, y = e0 - de * 5, n0 - dn * 5
                out["busts"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 0.8), 2), round(yaw)])
    works = [b for b in data["buildings"] if b["label"].startswith("PLA_OSM_") and b["length_m"] > 30]
    if works:                                              # boiler-house chimney at the nearest works building
        b = min(works, key=lambda b: math.hypot(b["east_m"], b["north_m"]))
        a = math.radians(b["axis_deg_from_east"])
        x, y = b["east_m"] + math.cos(a) * (b["length_m"] / 2 + 4), b["north_m"] + math.sin(a) * (b["length_m"] / 2 + 4)
        out["chimneys"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 1.5), 2), 0])
    print("props: " + ", ".join("%s %d" % (k, len(out[k])) for k in ("cars", "barrels", "fences", "poles", "furniture", "busstops", "busts", "chimneys", "scrap", "woodruins")))
    # foundations of demolished wooden houses, measured on satellite imagery (ANNAHME, see that file)
    extra = os.path.join(os.path.dirname(sys.argv[1]), "satellite-additions-2026-11-07.json")
    out["foundations"] = [[e, n, round(gfoot(e, n, size / 2), 2), size]
                          for e, n, size in (json.load(open(extra)).get("foundations", []) if os.path.exists(extra) else [])]
    for b in data["buildings"]:  # rusty tanks beside the unaddressed (industrial) buildings, photo briefing V7
        if b["label"].startswith("PLA_OSM_") and b["length_m"] > 40:
            a = math.radians(b["axis_deg_from_east"])
            for k in range(2):
                u, v = -b["length_m"] / 2 + 6 + k * 9, b["width_m"] / 2 + 8
                x, y = b["east_m"] + u * math.cos(a) - v * math.sin(a), b["north_m"] + u * math.sin(a) + v * math.cos(a)
                out["tanks"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 3.0), 2), rnd.choice((4.5, 6.0, 7.5))])
    gx, gy = 120.0, -560.0  # a row of eight metal garages at the southern edge of the town
    for k in range(8):
        x, y = gx + k * 3.4, gy
        if clear(x, y, 1.0):
            out["garages"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 2.5), 2)])
    # courtyard furniture (typical Soviet microdistrict, ANNAHME): street lamps, benches by the doors, playgrounds
    out["lamps"], out["benches"], out["playgrounds"] = [], [], []
    for r in data["roads"]:
        if r["kind"] != "residential":
            continue
        pts = r["points_m"]
        acc_len = 0.0
        for (ax, ay, _), (bx, by, _) in zip(pts, pts[1:]):
            seg = math.hypot(bx - ax, by - ay)
            nx, ny = -(by - ay) / (seg or 1), (bx - ax) / (seg or 1)
            off = -(3.5 + r["width_m"] / 2)  # opposite side of the heat pipes
            t = (35.0 - acc_len % 35.0) if acc_len else 0.0
            while t <= seg:
                x, y = ax + (bx - ax) * t / seg + nx * off, ay + (by - ay) * t / seg + ny * off
                if facade_dist(x, y) > 2.0:
                    out["lamps"].append([round(x, 1), round(y, 1), round(gz(x, y), 2), round(math.degrees(math.atan2(-ny, -nx)))])
                t += 35.0
            acc_len += seg
    for ex, ey in entrances:
        if rnd.random() < 0.45:
            x, y = ex + rnd.choice((-3.0, 3.0)), ey + rnd.uniform(-1.0, 1.0)
            out["benches"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 1.0), 2), round(rnd.uniform(0, 360))])
    tries = 0
    while len(out["playgrounds"]) < 6 and tries < 20000:
        tries += 1
        x, y = rnd.uniform(-400, 400), rnd.uniform(-450, 350)
        if 16 <= facade_dist(x, y) <= 40 and clear(x, y, 6.0) and all(math.hypot(x - px, y - py) > 120 for px, py, *_ in out["playgrounds"]):
            out["playgrounds"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 4.0), 2), round(rnd.uniform(0, 360))])
    if out["playgrounds"]:  # evidence camera 14 m from the first playground (editor_shots.py reads it)
        px, py, pz, _ = out["playgrounds"][0]
        out["cameras"] = [{"name": "courtyard-playground", "north_m": py - 11, "east_m": px - 9, "z_m": pz + 1.7,
                           "yaw_deg": round(math.degrees(math.atan2(px + 2 - (px - 9), py + 1 - (py - 11))), 1)}]
    # ruins and small structures (user 2026-11-08: "mehr als nur Häuser - zerstörte Häuser, Haufen"; ANNAHME positions):
    # remains of demolished panel blocks (standing wall panels, slabs, rubble) on open ground between the houses,
    # and the small concrete/brick huts of the photo (transformer stations, pump houses) beside the roads
    out["ruins"], out["huts"] = [], []
    for _ in range(9):
        for _ in range(60):
            p_ = spot(620, 18.0, margin=6.0)
            if p_ and all(math.hypot(p_[0] - q[0], p_[1] - q[1]) > 80 for q in out["ruins"]):
                out["ruins"].append([round(p_[0], 1), round(p_[1], 1), round(gfoot(*p_, 16.0), 2), round(rnd.uniform(0, 360)), round(rnd.uniform(0.8, 1.2), 2)])
                break
    for r in data["roads"]:
        pts = r["points_m"]
        for (ax, ay, _), (bx, by, _) in zip(pts, pts[1:]):
            L = math.hypot(bx - ax, by - ay)
            if L < 40 or math.hypot(ax, ay) > 750 or rnd.random() > 0.35:
                continue
            t, side = rnd.uniform(0.2, 0.8), rnd.choice((-1, 1))
            nx, ny = -(by - ay) / L * side, (bx - ax) / L * side
            off = r["width_m"] / 2 + rnd.uniform(9, 14)
            x, y = ax + (bx - ax) * t + nx * off, ay + (by - ay) * t + ny * off
            if clear(x, y, 2.0, wall=6.0):
                out["huts"].append([round(x, 1), round(y, 1), round(gfoot(x, y, 5.0), 2), round(math.degrees(math.atan2(by - ay, bx - ax)))])
    print("ruins %d huts %d" % (len(out["ruins"]), len(out["huts"])))
    from refine_vegetation import refine
    refine(out, gz, data, json.load(open(man)))
    power_site = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../assets/power/site.json")
    if os.path.exists(power_site):
        from power_update import clear_props
        clear_props(out, data, json.load(open(power_site)))
    from neighbourhood_update import densify, blocked_doors
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    mine_path = root / "assets/mine/adit_site.json"
    mine_portal = json.load(open(mine_path))["portal"] if mine_path.exists() else None
    manifest = json.load(open(man))
    densify(out, data, manifest, gz, json.load(open(power_site)) if os.path.exists(power_site) else None, mine_portal)
    out["blocked_doors"] = blocked_doors(manifest)
    json.dump(out, open(sys.argv[2], "w"))
    print("lamps %d benches %d playgrounds %d" % (len(out["lamps"]), len(out["benches"]), len(out["playgrounds"])))
    print("birch %d shrub %d larch %d | pipes %d rubble %d tanks %d garages %d" % (
        len(out["birch"]), len(out["shrub"]), len(out["larch"]), len(out["pipes"]), len(out["rubble"]), len(out["tanks"]), len(out["garages"])))

if __name__ == "__main__":
    main()
