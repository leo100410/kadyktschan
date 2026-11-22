"""Blockout JSON roads/rivers -> ribbon OBJ draped on the terrain mesh (cm; x east, y north, z up like dem_to_obj).

Usage: python -I lines_to_obj.py <blockout.json> <roads|rivers|paths> <out.obj> <terrain.obj> [buildings_manifest.json]
Ribbons are resampled every STEP m onto the rendered terrain triangles (terrain_mesh.py), so they neither float nor
sink between OSM nodes. UV: u = 0 (left edge) .. 1 (right edge), v = distance / (2 * width) for the road texture.
"paths" are trodden footpaths (ANNAHME) from every entrance in the manifest to the nearest road.
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from terrain_mesh import TerrainMesh

LIFT, STEP, PATH_W = 0.06, 2.0, 1.6  # m above the terrain, resample spacing, footpath width
d = json.load(open(sys.argv[1])); kind = sys.argv[2]
ground = TerrainMesh(sys.argv[4]).z


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
    for i, (x, y) in enumerate(pts):
        ax, ay = pts[max(i - 1, 0)]; bx, by = pts[min(i + 1, len(pts) - 1)]
        dx, dy = bx - ax, by - ay; n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n * w, dx / n * w  # left normal
        if i:
            dist += math.hypot(x - pts[i - 1][0], y - pts[i - 1][1])
        for sx, u in ((1, 0.0), (-1, 1.0)):
            px, py = x + sx * nx, y + sx * ny
            v.append((px, py, ground(px, py) + LIFT)); vt.append((u, dist / (2 * w)))
    for i in range(len(pts) - 1):
        a = base + 2 * i + 1  # left i (1-based)
        f.append((a, a + 1, a + 3)); f.append((a, a + 3, a + 2))  # CCW seen from above
with open(sys.argv[3], "w") as o:
    o.write("# OpenStreetMap contributors, ODbL 1.0; heights Copernicus DEM GLO-30\n")
    for x, y, z in v: o.write("v %.1f %.1f %.1f\n" % (x * 100, y * 100, z * 100))
    for u, t in vt: o.write("vt %.4f %.4f\n" % (u, t))
    for a, b, c in f: o.write("f %d/%d %d/%d %d/%d\n" % (a, a, b, b, c, c))
print("%s: %d ribbons, %d tris" % (kind, len(lines), len(f)))
