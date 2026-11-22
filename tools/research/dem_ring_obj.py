"""Distant backdrop: a coarse DEM ring around the 8 km play terrain, so the real Kolyma ranges stand on the horizon.

Usage: python -I dem_ring_obj.py <out.obj> <half_extent_m> <step_m> <inner_half_m> <tile.tif>...
Same axes and origin height as dem_to_obj.py; quads fully inside inner_half are left out (the play terrain is there),
and the ring is lowered SINK m so its edge hides under the play terrain. No UV detail needed: seen from kilometres.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import dem_to_obj as dem

SINK = 3.0

def main():
    out, half, step, inner = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
    dem.load_tiles(sys.argv[5:])
    h0 = dem.ground(0.0, 0.0)
    n = int(2 * half / step) + 1
    coords = [-half + i * step for i in range(n)]
    with open(out, "w") as f:
        f.write("# Copernicus DEM GLO-30 (c) DLR e.V. 2010-2014 and (c) Airbus Defence and Space GmbH 2014-2018, provided under COPERNICUS by the EU and ESA\n")
        for y in coords:
            for x in coords:
                f.write("v %.1f %.1f %.1f\n" % (x * 100, y * 100, (dem.height(*dem.latlon(x, y)) - h0 - SINK) * 100))
        for j in range(n):
            for i in range(n):
                f.write("vt %.5f %.5f\n" % (i / (n - 1), j / (n - 1)))
        quads = 0
        for j in range(n - 1):
            for i in range(n - 1):
                x0, x1, y0, y1 = coords[i], coords[i + 1], coords[j], coords[j + 1]
                if max(abs(x0), abs(x1)) < inner and max(abs(y0), abs(y1)) < inner:
                    continue
                a = j * n + i + 1; b = a + 1; c = a + n; d = c + 1
                f.write("f %d/%d %d/%d %d/%d\nf %d/%d %d/%d %d/%d\n" % (a, a, b, b, d, d, a, a, d, d, c, c))
                quads += 1
    print("ring %d quads, %.0f km wide, step %.0f m" % (quads, 2 * half / 1000, step))

main()
