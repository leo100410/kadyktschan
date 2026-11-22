"""Stollen 3 (Nordhang): pick the adit portal on the terrain and cut the terrain for it.

Usage: python3 -I mine_site.py <terrain.obj> <out cut terrain.obj> <out patch.obj> <out adit_site.json>

The adit is FIKTION (concept: "Mysterium"; the real shaft 10 is scenery only). The site is the steepest slope near the
town on the north-west side (ANNAHME), 540 m up from the boiler house. The 30 m terrain grid cannot show a portal, so
the terrain cells around it are removed from the big mesh and replaced by a 0.5 m patch with the same surface plus the
cutting: a level trench in front of the portal, cut vertically at its sides (the retaining walls of build_mine.py hide
the cut faces). Heights are interpolated on the original triangles, so the patch meets the big mesh without seams.
"""
import json, math, sys

SITE = (-688.0, 983.0)       # metres east/north: steepest slope found by the 2026-11-08 search
UPHILL_DEG = 130.0           # into the hill, degrees from east (counter-clockwise)
BACK = 10.0                  # portal this far downhill of SITE
CUT = 5.0                    # natural ground above the trench floor at the portal face
HALF_W = 4.0                 # trench half width (floor), retaining walls stand at HALF_W .. HALF_W + 0.6
BLOCK = 2                    # cells removed around the portal cell in every direction (5 x 5 cells, 150 m)
STEP = 0.5                   # patch grid
MOUTH = 1.6                  # trench floor runs this far under the portal block; the hole ends at MOUTH + 0.7


def read_obj(path):
    head, verts, uvs, faces = [], [], [], []
    for line in open(path):
        if line.startswith("v "):
            verts.append(tuple(map(float, line.split()[1:4])))
        elif line.startswith("vt "):
            uvs.append(line)
        elif line.startswith("f "):
            faces.append(line)
        elif line.startswith("#"):
            head.append(line)
    return head, verts, uvs, faces


def main():
    head, verts, uvs, faces = read_obj(sys.argv[1])
    n = int(round(math.sqrt(len(verts))))
    x0, step = verts[0][0] / 100.0, (verts[1][0] - verts[0][0]) / 100.0
    z = lambda i, j: verts[j * n + i][2] / 100.0      # metres, relative to the origin height

    def ground(x, y):
        """Height on the original triangles (a, b, d) / (a, d, c) of cell (i, j), exactly as rendered."""
        fi, fj = (x - x0) / step, (y - x0) / step
        i, j = min(int(fi), n - 2), min(int(fj), n - 2)
        u, v = fi - i, fj - j
        a, b, c, d = z(i, j), z(i + 1, j), z(i, j + 1), z(i + 1, j + 1)
        return a + (b - a) * u + (d - b) * v if u >= v else a + (d - c) * u + (c - a) * v

    ux, uy = math.cos(math.radians(UPHILL_DEG)), math.sin(math.radians(UPHILL_DEG))
    px, py = SITE[0] - ux * BACK, SITE[1] - uy * BACK
    floor = ground(px, py) - CUT
    ci, cj = int((px - x0) / step), int((py - x0) / step)
    i0, i1, j0, j1 = ci - BLOCK, ci + BLOCK + 1, cj - BLOCK, cj + BLOCK + 1   # removed cells [i0, i1) x [j0, j1)

    def carved(x, y):
        h = ground(x, y)
        u, v = (x - px) * ux + (y - py) * uy, -(x - px) * uy + (y - py) * ux
        if u <= MOUTH and abs(v) <= HALF_W:   # under the portal block too, so no slanted face reaches into the mouth
            return min(h, floor)   # cut only, never fill: downhill the natural ground falls below the floor
        return h

    # big mesh without the removed cells (face k covers cell (k // 2) % (n - 1), (k // 2) // (n - 1))
    with open(sys.argv[2], "w") as f:
        f.writelines(head)
        f.write("# cells i %d..%d, j %d..%d removed for the adit patch (tools/research/mine_site.py)\n" % (i0, i1 - 1, j0, j1 - 1))
        for x, y, zz in verts:
            f.write("v %.1f %.1f %.1f\n" % (x, y, zz))
        f.writelines(uvs)
        for k, line in enumerate(faces):
            cell = k // 2
            i, j = cell % (n - 1), cell // (n - 1)
            if not (i0 <= i < i1 and j0 <= j < j1):
                f.write(line)
    # patch on a 0.5 m grid over exactly the removed cells, UVs continuing the big mesh's 0..1 mapping
    ax, ay = x0 + i0 * step, x0 + j0 * step
    m = int(round((i1 - i0) * step / STEP)) + 1
    span = step * (n - 1)
    with open(sys.argv[3], "w") as f:
        f.write("# Stollen 3 adit terrain patch, same surface as the big mesh plus the portal cutting\n")
        for b in range(m):
            for a in range(m):
                x, y = ax + a * STEP, ay + b * STEP
                f.write("v %.1f %.1f %.1f\n" % (x * 100, y * 100, carved(x, y) * 100))
        for b in range(m):
            for a in range(m):
                f.write("vt %.6f %.6f\n" % ((ax + a * STEP - x0) / span, (ay + b * STEP - x0) / span))
        dropped = 0
        for b in range(m - 1):
            for a in range(m - 1):
                # the drift mouth: a heightfield closes it with a vertical face from the trench floor up to the hill,
                # so leave a hole under the portal block (build_mine.py covers u -0.8..2.4, |v| <= 4.6)
                x, y = ax + (a + 0.5) * STEP, ay + (b + 0.5) * STEP
                u, v = (x - px) * ux + (y - py) * uy, -(x - px) * uy + (y - py) * ux
                if -0.3 < u < MOUTH + 0.7 and abs(v) < 2.3:
                    dropped += 1
                    continue
                p = b * m + a + 1; q = p + 1; r = p + m; s = r + 1
                f.write("f %d/%d %d/%d %d/%d\nf %d/%d %d/%d %d/%d\n" % (p, p, q, q, s, s, p, p, s, s, r, r))
        assert dropped > 0, "no patch cells under the portal"
    # the natural ground along the trench sides, for the retaining walls
    walls = []
    for side in (-1, 1):
        row = []
        u = 0.0
        while u > -40.0:
            vv = side * (HALF_W + 0.3)
            x, y = px + ux * u - uy * vv, py + uy * u + ux * vv
            h = max(ground(x + dx, y + dy) for dx in (-0.4, 0, 0.4) for dy in (-0.4, 0, 0.4))
            if h <= floor + 0.3:
                break
            row.append([round(u, 2), round(h, 2)])
            u -= 1.0
        walls.append(row)
    site = {"portal": [round(px, 2), round(py, 2)], "uphill": [round(ux, 5), round(uy, 5)], "floor_m": round(floor, 2),
            "half_width_m": HALF_W, "cells": [i0, i1, j0, j1], "wall_tops": walls,
            "ground_at_portal": round(ground(px, py), 2), "ground_samples": [[u, round(ground(px + ux * u, py + uy * u), 2)] for u in range(-60, 61, 5)]}
    json.dump(site, open(sys.argv[4], "w"), indent=1)
    # self-check: the patch meets the big mesh on its border and the trench floor is level at the portal
    for t in (0.0, 0.37, 1.0):
        bx, by = ax + t * (i1 - i0) * step, ay
        assert abs(carved(bx, by) - ground(bx, by)) < 1e-6
    assert abs(carved(px - ux * 0.5, py - uy * 0.5) - floor) < 1e-6
    print("portal %.1f E %.1f N, floor %.1f m, natural %.1f m, trench %d m, cells %s" % (px, py, floor, ground(px, py), len(walls[0]), [i0, i1, j0, j1]))


if __name__ == "__main__":
    main()
