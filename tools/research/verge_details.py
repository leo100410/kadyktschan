"""Sparse, terrain-following forest-floor patches outside road edges; no collision or new buildings."""
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from terrain_mesh import TerrainMesh

ROOT = Path(__file__).resolve().parents[2]


def patch(ground, east, north):
    """4 m patch sampled on the actual terrain; returns vertices in metres and local UVs."""
    vertices, uvs, faces = [], [], []
    for j in range(9):
        for i in range(9):
            x, y = east - 2 + i * 0.5, north - 2 + j * 0.5
            vertices.append((x, y, ground(x, y) + 0.04))
            uvs.append((i / 8, j / 8))
    for j in range(8):
        for i in range(8):
            a = j * 9 + i
            faces += [(a, a + 1, a + 10), (a, a + 10, a + 9)]
    return vertices, uvs, faces


def main():
    ground = TerrainMesh(ROOT / "assets/terrain/terrain_kadykchan_8km.obj").z
    data = json.loads((ROOT / "design/research/data/blockout-2026-11-07.json").read_text())
    vertices, uvs, faces = [], [], []
    centres = []
    for road in data["roads"]:
        for a, b in zip(road["points_m"], road["points_m"][1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            if length < 30:
                continue
            for i in range(max(1, int(length / 90))):
                t = (i + 0.5) / max(1, int(length / 90))
                for side in (-1, 1):
                    offset = road["width_m"] * 0.54 + 2.5
                    x, y = a[0] + dx * t - dy / length * offset * side, a[1] + dy * t + dx / length * offset * side
                    if math.hypot(x, y) > 900 or any(math.hypot(x - px, y - py) < 8 for px, py in centres):
                        continue
                    if len(centres) >= 120:
                        continue
                    centres.append((x, y))
                    vs, ts, fs = patch(ground, x, y)
                    base = len(vertices)
                    vertices.extend(vs); uvs.extend(ts); faces.extend(tuple(base + v for v in f) for f in fs)
    target = ROOT / "assets/terrain/verge_details.obj"
    with target.open("w") as f:
        for x, y, z in vertices:
            f.write("v %.2f %.2f %.2f\n" % (x * 100, y * 100, z * 100))
        for u, v in uvs:
            f.write("vt %.4f %.4f\n" % (u, v))
        for face in faces:
            f.write("f " + " ".join("%d/%d" % (i + 1, i + 1) for i in face) + "\n")
    assert centres and len(faces) <= 120 * 128
    print("VERGES OK", len(centres), "patches", len(faces), "triangles")


if __name__ == "__main__":
    main()
