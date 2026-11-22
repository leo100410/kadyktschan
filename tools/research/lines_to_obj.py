"""Blockout JSON roads/rivers -> ribbon OBJ draped on the terrain mesh (cm; x east, y north, z up like dem_to_obj).

Usage: python -I lines_to_obj.py <blockout.json> <roads|tracks|rivers|paths> <out.obj> <terrain.obj> [buildings_manifest.json]
Ribbons are resampled every STEP m onto the rendered terrain triangles (terrain_mesh.py), so they neither float nor
sink between OSM nodes. UV: u = 0 (left edge) .. 1 (right edge), v = distance / (2 * width) for the road texture.
"paths" are trodden footpaths (ANNAHME) from every entrance in the manifest to the nearest road.
Asphalt roads use three vertices across their crown and v = distance / 64 for the wear atlas; OSM tracks stay separate.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from terrain_mesh import TerrainMesh

LIFT, STEP, PATH_W = 0.06, 2.0, 1.6  # m above the terrain, resample spacing, footpath width
d = json.load(open(sys.argv[1])); kind = sys.argv[2]
ground = TerrainMesh(sys.argv[4]).z


def edge_width(x, y, half_width):
    """Gentle, deterministic erosion; edge wear stays within three centimetres."""
    return half_width + 0.02 * math.sin(x * 0.12 + y * 0.09) + 0.01 * math.sin(x * 0.37 - y * 0.21)


def footpaths(roads, manifest):
    """Entrance -> nearest point on a road, with a slight kink so the path does not look ruled."""
    out = []
    for b in json.load(open(manifest, encoding="utf-8")):
        for n, e, yaw in b.get("entrances", []):
            # entrances are 6 m in front of the door, facing it; start the path at the steps
            dn, de = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
            sx, sy = e + de * 4.5, n + dn * 4.5
            best = None
            for r in roads:
                p = r["points_m"]
                for (ax, ay, _), (bx, by, _) in zip(p, p[1:]):
                    vx, vy = bx - ax, by - ay
                    t = max(0.0, min(1.0, ((sx - ax) * vx + (sy - ay) * vy) / ((vx * vx + vy * vy) or 1e-9)))
                    qx, qy = ax + vx * t, ay + vy * t
                    dist = math.hypot(qx - sx, qy - sy)
                    if best is None or dist < best[0]:
                        best = (dist, qx, qy)
            if best and best[0] < 150:
                _, qx, qy = best
                mx, my = (sx + qx) / 2 + (qy - sy) * 0.08, (sy + qy) / 2 - (qx - sx) * 0.08
                out.append({"points_m": [[sx, sy, 0], [mx, my, 0], [qx, qy, 0]], "width_m": PATH_W})
    return out


if kind == "paths":
    lines = footpaths(d["roads"], sys.argv[5])
    power_site = os.path.join(os.path.dirname(sys.argv[5]), "..", "power", "site.json")
    if os.path.exists(power_site):
        from power_update import station_access
        lines.append(station_access(d["roads"], json.load(open(power_site))))
elif kind in ("roads", "tracks"):
    lines = [r for r in d["roads"] if (r["kind"] == "track") == (kind == "tracks")]
else:
    lines = d[kind]

v, vt, f = [], [], []
for ln in lines:
    w = (ln["width_m"] if kind != "rivers" else 8.0) / 2
    # resample the polyline every STEP metres
    pts, p = [], ln["points_m"]
    for (ax, ay, _), (bx, by, _) in zip(p, p[1:]):
        k = max(1, int(math.ceil(math.hypot(bx - ax, by - ay) / STEP)))
        pts += [(ax + (bx - ax) * i / k, ay + (by - ay) * i / k) for i in range(k)]
    pts.append(tuple(p[-1][:2]))
    base, dist = len(v), 0.0
    columns = (0.0, 0.5, 1.0) if kind == "roads" else (0.0, 1.0)
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]; bx, by = pts[min(i + 1, len(pts) - 1)]
        dx, dy = bx - ax, by - ay; n = math.hypot(dx, dy) or 1.0
        width = edge_width(x, y, w) if kind != "rivers" else w
        nx, ny = -dy / n * width, dx / n * width  # left normal
        if i:
            dist += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        for u in columns:
            sx = 1 - 2 * u
            if kind == "roads":
                sx *= 1 + 0.015 / width * math.sin(x * 0.11 + y * 0.07 + sx * 2.8)
            px, py = x + sx * nx, y + sx * ny
            lift = 0.018 + 0.042 * (1 - abs(1 - 2 * u)) if kind == "roads" else LIFT
            v.append((px, py, ground(px, py) + lift))
            vt.append((u, dist / 64.0 if kind == "roads" else dist / (2 * w)))
    for i in range(len(pts) - 1):
        stride = len(columns)
        for j in range(stride - 1):
            a = base + stride * i + j + 1  # left i (1-based)
            f.append((a, a + 1, a + stride + 1)); f.append((a, a + stride + 1, a + stride))
with open(sys.argv[3], "w") as o:
    o.write("# OpenStreetMap contributors, ODbL 1.0; heights Copernicus DEM GLO-30\n")
    for x, y, z in v: o.write("v %.1f %.1f %.1f\n" % (x * 100, y * 100, z * 100))
    for u, t in vt: o.write("vt %.4f %.4f\n" % (u, t))
    for a, b, c in f:
        pa, pb, pc = v[a - 1], v[b - 1], v[c - 1]
        area = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
        if abs(area) < 1e-10:
            continue  # duplicate OSM nodes can collapse a triangle at a bend
        if area < 0:
            b, c = c, b
        o.write("f %d/%d %d/%d %d/%d\n" % (a, a, b, b, c, c))
print("%s: %d ribbons, %d tris" % (kind, len(lines), len(f)))
