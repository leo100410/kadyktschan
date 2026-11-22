"""OSM buildings/roads/rivers + Copernicus DEM -> blockout JSON for tools/editor/build_blockout.py.

Usage: python -I blockout_data.py <osm.json> <out.json> <tile.tif>...
Heights are ANNAHMEN (design/research/phase-1-dossier.md): storey 2.8 m, pile/crawl space 1.2 m,
parapet 0.6 m; buildings without a levels tag count as 2 storeys, untagged industrial ruins as 8 m.
"""
import json, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
import dem_to_obj as dem

STOREY, PILE, PARAPET = 2.8, 1.2, 0.6
ROAD_WIDTH = {"trunk": 8.0, "residential": 6.0, "unclassified": 5.0, "service": 4.0, "track": 3.0}
EXTENT = 4000.0  # m, same as the terrain grid half-extent
LAT0, LON0, R = dem.LAT0, dem.LON0, dem.R
xy = lambda la, lo: (math.radians(lo - LON0) * R * math.cos(math.radians(LAT0)), math.radians(la - LAT0) * R)
h0 = None

def ground(x, y):
    return dem.ground(x, y) - h0  # same bare-earth filter as the terrain mesh

def obb(pts):
    best = None
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        a = math.atan2(y2 - y1, x2 - x1); ca, sa = math.cos(a), math.sin(a)
        u = [x * ca + y * sa for x, y in pts]; v = [-x * sa + y * ca for x, y in pts]
        L, W = max(u) - min(u), max(v) - min(v)
        cu, cv = (max(u) + min(u)) / 2, (max(v) + min(v)) / 2
        cand = (L * W, L, W, a, cu * ca - cv * sa, cu * sa + cv * ca)
        if best is None or cand[0] < best[0]: best = cand
    _, L, W, a, cx, cy = best
    return (L, W, a, cx, cy) if L >= W else (W, L, a + math.pi / 2, cx, cy)

LAT_STREET = {"улица Ленина": "Lenina", "Школьная улица": "Shkolnaya", "Южная улица": "Yuzhnaya", "улица Мира": "Mira", "улица 50 лет Октября": "50LetOktyabrya"}

def main():
    global h0
    osm = json.load(open(sys.argv[1])); dem.load_tiles(sys.argv[3:]); h0 = dem.ground(0.0, 0.0)
    out = {"origin": [LAT0, LON0, round(h0, 2)], "buildings": [], "roads": [], "rivers": []}
    for e in osm["elements"]:
        t = e.get("tags", {}); g = e.get("geometry")
        if not g: continue
        pts = [xy(p["lat"], p["lon"]) for p in g]
        if "building" in t:
            L, W, a, cx, cy = obb(pts)
            lv = t.get("building:levels")
            h = int(lv) * STOREY + PILE + PARAPET if lv and lv.isdigit() else (8.0 if "addr:street" not in t else 2 * STOREY + PILE + PARAPET)
            st = LAT_STREET.get(t.get("addr:street")); nr = t.get("addr:housenumber")
            out["buildings"].append({
                "label": "PLA_%s_%s" % (st, nr) if st else "PLA_OSM_%d" % e["id"],
                "folder": "Buildings/" + (st or "Unaddressed"),
                "levels": lv, "height_m": round(h, 2), "length_m": round(L, 2), "width_m": round(W, 2),
                "east_m": round(cx, 2), "north_m": round(cy, 2), "ground_m": round(ground(cx, cy), 2),
                "axis_deg_from_east": round(math.degrees(a) % 360, 2), "osm": "way/%d" % e["id"]})
        elif t.get("highway") in ROAD_WIDTH or t.get("waterway") in ("river", "stream"):
            kind = "rivers" if "waterway" in t else "roads"
            pts = [p for p in pts if abs(p[0]) < EXTENT and abs(p[1]) < EXTENT]
            if len(pts) < 2: continue
            out[kind].append({"name": t.get("name", ""), "kind": t.get("highway") or t.get("waterway"),
                              "width_m": ROAD_WIDTH.get(t.get("highway"), 6.0),
                              "points_m": [[round(x, 1), round(y, 1), round(ground(x, y), 2)] for x, y in pts], "osm": "way/%d" % e["id"]})
    # buildings seen on satellite imagery but missing in OSM (ANNAHME, see that file's _comment)
    extra = os.path.join(os.path.dirname(sys.argv[1]), "satellite-additions-2026-11-07.json")
    for b in (json.load(open(extra))["buildings"] if os.path.exists(extra) else []):
        lv = b["levels"]
        out["buildings"].append({
            "label": "PLA_SAT_" + b["id"], "folder": "Buildings/SatelliteAdditions", "levels": lv,
            "height_m": round(int(lv) * STOREY + PILE + PARAPET, 2), "length_m": b["length_m"], "width_m": b["width_m"],
            "east_m": b["east_m"], "north_m": b["north_m"], "ground_m": round(ground(b["east_m"], b["north_m"]), 2),
            "axis_deg_from_east": b["axis_deg_from_east"], "osm": "sat/" + b["id"]})
    json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
    print("buildings %d roads %d rivers %d" % (len(out["buildings"]), len(out["roads"]), len(out["rivers"])))

if __name__ == "__main__":
    main()
