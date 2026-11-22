"""Turn the existing safe plant locations into mixed growth forms; retain props, entrances and mine clearance."""
import json
import math
from pathlib import Path
import random
import sys
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terrain_mesh import TerrainMesh

ROOT = Path(__file__).resolve().parents[2]


def refine(data, ground, layout, manifest):
    if all(kind in data for kind in ("low_willow", "alder", "dry_shrub")):
        return data
    rng = random.Random(2011_1109)
    segments, buckets = [], {}
    for road in layout["roads"]:
        for a, b in zip(road["points_m"], road["points_m"][1:]):
            index = len(segments)
            segments.append((a[0], a[1], b[0], b[1], road["width_m"] / 2))
            for i in range(math.floor((min(a[0], b[0]) - 20) / 32), math.floor((max(a[0], b[0]) + 20) / 32) + 1):
                for j in range(math.floor((min(a[1], b[1]) - 20) / 32), math.floor((max(a[1], b[1]) + 20) / 32) + 1):
                    buckets.setdefault((i, j), []).append(index)
    entrances = [(e, n) for b in manifest for n, e, _ in b.get("entrances", [])]
    footprints = [(b["east_m"], b["north_m"], math.radians(b["axis_deg_from_east"]), b["length_m"] / 2 + 3,
                   b["width_m"] / 2 + 3) for b in layout["buildings"]]

    def projection(e, n, segment):
        ax, ay, bx, by = segment[:4]
        dx, dy = bx - ax, by - ay
        t = max(0, min(1, ((e - ax) * dx + (n - ay) * dy) / max(dx * dx + dy * dy, 1e-9)))
        x, y = ax + t * dx, ay + t * dy
        return math.hypot(e - x, n - y), x, y

    def verge(e, n):
        candidates = buckets.get((math.floor(e / 32), math.floor(n / 32)), [])
        if not candidates or math.hypot(e, n) > 850:
            return e, n
        distance, x, y, half = min((*projection(e, n, segments[i]), segments[i][4]) for i in candidates)
        if distance < half + 3 or distance > 18:
            return e, n
        offset = half + rng.uniform(1.2, 2.2)
        x, y = x + (e - x) / distance * offset, y + (n - y) / distance * offset
        if any(math.hypot(x - ex, y - ny) < 9 for ex, ny in entrances):
            return e, n
        for ex, ny, angle, hl, hw in footprints:
            dx, dy = x - ex, y - ny
            if abs(dx * math.cos(angle) + dy * math.sin(angle)) < hl and abs(-dx * math.sin(angle) + dy * math.cos(angle)) < hw:
                return e, n
        for i in buckets.get((math.floor(x / 32), math.floor(y / 32)), []):
            if projection(x, y, segments[i])[0] < segments[i][4] + 0.8:
                return e, n
        for river in layout["rivers"]:
            for a, b in zip(river["points_m"], river["points_m"][1:]):
                if projection(x, y, (*a[:2], *b[:2]))[0] < 8:
                    return e, n
        return round(x, 1), round(y, 1)
    sources = {kind: data.get(kind, []) for kind in ("willow", "sapling", "shrub")}
    for kind in (*sources, "low_willow", "alder", "dry_shrub"):
        data[kind] = []
    forms = ("low_willow", "alder", "shrub", "willow")
    for source, items in sources.items():
        for e, n, z, yaw, scale in items:
            if abs(z - ground(e, n)) > 0.3:  # keep the deliberate roof and elevated facade plants
                data[source].append([e, n, z, yaw, scale])
                continue
            radius = math.hypot(e, n)
            if source == "sapling" and rng.random() < (0.15 if radius < 800 else 0.65):
                if radius > 1100 and rng.random() < 0.25:
                    data["larch"].append([e, n, z, yaw, round(rng.uniform(0.65, 1.0), 2)])
                else:
                    data["sapling"].append([e, n, z, yaw, scale])
                continue
            # A few clearings between dense thickets; growth forms share a 35 m patch, not a checkerboard of plants.
            if math.sin(e * 0.008) * math.sin(n * 0.01) > 0.65 and rng.random() < 0.35:
                continue
            cell = "%d,%d" % (math.floor(e / 35), math.floor(n / 35))
            dominant = zlib.crc32(cell.encode()) % len(forms)
            kind = forms[dominant] if rng.random() < 0.72 else rng.choice(forms)
            if rng.random() < 0.045:
                kind = "dry_shrub"
            if kind in ("low_willow", "shrub", "dry_shrub") and rng.random() < 0.3:
                e, n = verge(e, n)
                z = round(ground(e, n), 2)
            scale = rng.uniform(0.7, 1.3) * (0.8 if kind == "willow" else 1.0)
            data[kind].append([e, n, z, yaw, round(scale, 2)])
    return data


if __name__ == "__main__":
    path = ROOT / "assets/vegetation/scatter.json"
    data = json.loads(path.read_text())
    refine(data, TerrainMesh(ROOT / "assets/terrain/terrain_kadykchan_8km.obj").z,
           json.loads((ROOT / "design/research/data/blockout-2026-11-07.json").read_text()),
           json.loads((ROOT / "assets/buildings/buildings_manifest.json").read_text()))
    path.write_text(json.dumps(data, separators=(",", ":")))
    print("NATURE OK", {k: len(data.get(k, [])) for k in ("larch", "sapling", "willow", "low_willow", "alder", "shrub", "dry_shrub")})
