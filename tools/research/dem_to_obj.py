"""Copernicus DEM GLO-30 tiles -> terrain grid OBJ in Unreal units (cm), centred on the project origin.

Usage: python -I dem_to_obj.py <out.obj> <half_extent_m> <step_m> <tile.tif>...
Axes written: OBJ x = east, y = north, z = up (cm); the editor import script fixes orientation.
"""
import math, sys

LAT0, LON0 = 63.085870, 147.050008  # origin, see design/research/phase-1-dossier.md
R = 6371008.8

def load(path):
    import numpy as np, tifffile  # only needed for the DEM tiles; the OBJ fallback below runs on plain Python
    with tifffile.TiffFile(path) as t:
        page = t.pages[0]
        sx, sy, _ = page.tags["ModelPixelScaleTag"].value
        tp = page.tags["ModelTiepointTag"].value  # (i, j, k, lon, lat, z)
        return page.asarray().astype(np.float64), tp[3], tp[4], sx, sy

tiles = []  # filled by main or by load_tiles()

def load_tiles(paths):
    tiles[:] = [load(p) for p in paths]

OBJ_GRID = []  # [x0 m, step m, n, absolute heights row-major by y] when built from a terrain OBJ instead of the tiles

def load_obj(path):
    """Read heights back from a terrain OBJ written by main() (when the DEM tiles are not at hand). Same surface the
    game shows, so props sampled from it sit on the rendered ground."""
    h0, zs, x0, x1 = 0.0, [], None, None
    for line in open(path):
        if line.startswith("# origin height"):
            h0 = float(line.split()[3])
        elif line.startswith("v "):
            x, y, z = map(float, line.split()[1:4])
            if x0 is None:
                x0 = x
            elif x1 is None:
                x1 = x
            zs.append(h0 + z / 100.0)
    n = int(round(math.sqrt(len(zs))))
    assert n * n == len(zs), "terrain OBJ is not a square grid"
    OBJ_GRID[:] = [x0 / 100.0, (x1 - x0) / 100.0, n, zs]
    return h0  # the origin height the OBJ was written with (heights in the world are relative to it)

def height(lat, lon):
    for a, lon_tl, lat_tl, sx, sy in tiles:
        c, r = (lon - lon_tl) / sx - 0.5, (lat_tl - lat) / sy - 0.5  # pixel-is-area centres
        if -0.5 <= c <= a.shape[1] - 0.5 and -0.5 <= r <= a.shape[0] - 0.5:
            # clamp so the half-pixel band at a tile seam samples the edge pixels
            c = min(max(c, 0.0), a.shape[1] - 1.001); r = min(max(r, 0.0), a.shape[0] - 1.001)
            c0, r0 = int(c), int(r); fc, fr = c - c0, r - r0
            q = a[r0:r0 + 2, c0:c0 + 2]
            return (q[0, 0] * (1 - fc) + q[0, 1] * fc) * (1 - fr) + (q[1, 0] * (1 - fc) + q[1, 1] * fc) * fr
    raise ValueError("point outside tiles: %f %f" % (lat, lon))

FILTER_M = 30.0  # one DEM pixel

def ground(x, y):
    """Approximate bare-earth height (m, absolute) at local metres x/y.

    Copernicus GLO-30 is a surface model: buildings and trees are in it, so a courtyard between
    15 m blocks reads several metres too high. A 3x3 minimum filter at pixel spacing strips them
    (it also lowers sharp ridges by a few metres, acceptable for the blockout).
    """
    if OBJ_GRID:  # bilinear on the written grid (already filtered)
        x0, step, n, zs = OBJ_GRID
        c = min(max((x - x0) / step, 0.0), n - 1.001); r = min(max((y - x0) / step, 0.0), n - 1.001)
        c0, r0 = int(c), int(r); fc, fr = c - c0, r - r0
        z = lambda i, j: zs[(r0 + j) * n + c0 + i]
        return (z(0, 0) * (1 - fc) + z(1, 0) * fc) * (1 - fr) + (z(0, 1) * (1 - fc) + z(1, 1) * fc) * fr
    return min(height(*latlon(x + i * FILTER_M, y + j * FILTER_M)) for i in (-1, 0, 1) for j in (-1, 0, 1))

def latlon(x, y):  # local metres -> degrees (equirectangular, fine at town scale)
    return LAT0 + math.degrees(y / R), LON0 + math.degrees(x / (R * math.cos(math.radians(LAT0))))

def main():
    load_tiles(sys.argv[4:])
    out, half, step = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    h0 = ground(0.0, 0.0)
    n = int(2 * half / step) + 1
    coords = [-half + i * step for i in range(n)]
    with open(out, "w") as f:
        f.write("# Copernicus DEM GLO-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the EU and ESA\n")
        f.write("# origin height %.2f m above EGM2008\n" % h0)
        for y in coords:
            for x in coords:
                f.write("v %.1f %.1f %.1f\n" % (x * 100, y * 100, (ground(x, y) - h0) * 100))
        for j in range(n):
            for i in range(n):
                f.write("vt %.5f %.5f\n" % (i / (n - 1), j / (n - 1)))
        for j in range(n - 1):
            for i in range(n - 1):
                a = j * n + i + 1; b = a + 1; c = a + n; d = c + 1
                f.write("f %d/%d %d/%d %d/%d\nf %d/%d %d/%d %d/%d\n" % (a, a, b, b, d, d, a, a, d, d, c, c))  # CCW seen from above
    print("origin height %.1f m, grid %dx%d, step %.0f m" % (h0, n, n, step))

if __name__ == "__main__":
    main()
