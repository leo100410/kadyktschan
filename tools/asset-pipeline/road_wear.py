"""Road wear atlas: R cracks, G faded paint, B broken/repaired asphalt, A eroded shoulders.

UV 0 spans a road's width and 64 metres along it. Asphalt grain uses its own world-space 3 m texture.
Run with Blender's bundled Python (numpy): python road_wear.py <output folder>.
"""
from pathlib import Path
import math
import sys
import numpy as np
from gen_textures import save


def atlas(width=2048, height=4096):
    rng = np.random.default_rng(2011_1109)
    yy, xx = np.mgrid[0:height, 0:width]
    u, v = xx / width * 6.0, yy / height * 64.0
    noise = np.clip(0.5 + 0.22 * np.sin(u * 13 + np.sin(v * 2)) + 0.18 * np.sin(v * 8 - u * 19)
                    + rng.uniform(-0.15, 0.15, (height, width)), 0, 1)
    cracks = np.zeros((height, width), np.float32)

    def stroke(points, radius):
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            x0, x1 = max(0, int((min(ax, bx) - radius) / 6 * width)), min(width, int((max(ax, bx) + radius) / 6 * width) + 1)
            y0, y1 = max(0, int((min(ay, by) - radius) / 64 * height)), min(height, int((max(ay, by) + radius) / 64 * height) + 1)
            if x1 <= x0 or y1 <= y0:
                continue
            x, y = u[y0:y1, x0:x1], v[y0:y1, x0:x1]
            dx, dy = bx - ax, by - ay
            t = np.clip(((x - ax) * dx + (y - ay) * dy) / max(dx * dx + dy * dy, 1e-9), 0, 1)
            distance = np.hypot(x - ax - t * dx, y - ay - t * dy)
            part = cracks[y0:y1, x0:x1]
            np.maximum(part, np.clip((radius - distance) / max(radius * 0.35, 1e-9), 0, 1), out=part)

    points = [(1.8 + 0.18 * np.sin(k * math.pi / 40) + 0.05 * np.sin(k * math.pi / 8), k * 0.4) for k in range(161)]
    stroke(points, 0.013)
    for _ in range(100):
        x, y, angle = rng.uniform(0, 6), rng.uniform(0, 64), rng.uniform(0, 2 * math.pi)
        points = [(x, y)]
        for _ in range(rng.integers(5, 22)):
            angle += rng.uniform(-0.6, 0.6)
            length = rng.uniform(0.08, 0.28)
            x, y = x + math.cos(angle) * length, y + math.sin(angle) * length
            points.append((x, y))
        stroke(points, rng.uniform(0.008, 0.018))
        mid = points[len(points) // 2]
        stroke([mid, (mid[0] + rng.uniform(-0.5, 0.5), mid[1] + rng.uniform(-0.7, 0.7))], 0.009)
    centre = (np.abs(u - 3) < 0.055) & ((v % 9) < 3)
    sides = (np.abs(u - 0.6) < 0.045) | (np.abs(u - 5.4) < 0.045)
    paint = (centre * 0.85 + sides * 0.52) * np.clip((noise - 0.22) * 2.2, 0, 0.85)
    patches = np.zeros_like(cracks)
    for _ in range(30):
        cx, cy = rng.uniform(0.3, 5.7), rng.uniform(1, 63)
        rx, ry = rng.uniform(0.15, 0.6), rng.uniform(0.25, 1.3)
        angle = np.arctan2((v - cy) / ry, (u - cx) / rx)
        border = 1 + 0.2 * np.sin(angle * 3 + cy) + 0.12 * np.sin(angle * 7 + cx)
        dist = np.hypot((u - cx) / rx, (v - cy) / ry)
        patches = np.maximum(patches, np.clip((border + noise * 0.15 - dist) * 6, 0, 1) * (0.5 + noise * 0.25))
    paint *= 1 - np.clip(patches * 1.6, 0, 1)
    cracks *= 0.8
    shoulders = np.clip(noise * 0.5 + patches * 0.9, 0, 1)
    return np.stack([cracks, paint, patches, shoulders], -1)


if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    image = atlas()
    assert np.isfinite(image).all() and 0 <= image.min() <= image.max() <= 1
    save(str(out / "T_RoadWear.png"), (image * 255).round().astype(np.uint8))
    print("ROAD WEAR OK", image.shape)
