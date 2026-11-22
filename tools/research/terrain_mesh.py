"""Height of the terrain mesh written by dem_to_obj.py, interpolated on its triangles exactly as rendered.

The raw DEM sample (dem_to_obj.ground) only matches the mesh at the 30 m grid points; between them anything placed
on the DEM floats or sinks by up to metres on slopes. Use z() for everything that must sit on the ground.
"""
import math


class TerrainMesh:
    def __init__(self, obj_path):
        zs, xs = [], []
        for line in open(obj_path):
            if line.startswith("v "):
                _, x, y, z = line.split()
                xs.append(float(x) / 100); zs.append(float(z) / 100)
        self.n = int(round(math.sqrt(len(zs))))
        assert self.n * self.n == len(zs), "terrain OBJ is not a square grid"
        self.x0, self.step, self.zs = xs[0], xs[1] - xs[0], zs

    def z(self, x, y):
        """Metres above the terrain origin (same frame as the OBJ: x east, y north)."""
        fi, fj = (x - self.x0) / self.step, (y - self.x0) / self.step
        i, j = min(max(int(fi), 0), self.n - 2), min(max(int(fj), 0), self.n - 2)
        fx, fy = fi - i, fj - j
        a = j * self.n + i; b, c = a + 1, a + self.n; d = c + 1
        za, zb, zc, zd = self.zs[a], self.zs[b], self.zs[c], self.zs[d]
        if fx >= fy:   # triangle (a, b, d), diagonal a-d as in dem_to_obj
            return za + fx * (zb - za) + fy * (zd - zb)
        return za + fy * (zc - za) + fx * (zd - zc)


if __name__ == "__main__":  # self-check on a synthetic 3x3 grid
    import os, tempfile
    p = os.path.join(tempfile.mkdtemp(), "t.obj")
    with open(p, "w") as f:
        for y in (-30, 0, 30):
            for x in (-30, 0, 30):
                f.write("v %d %d %d\n" % (x * 100, y * 100, (x + 2 * y) * 100))  # plane z = x + 2y
    t = TerrainMesh(p)
    for x, y in ((0, 0), (12.5, -7), (-29, 29), (20, 20)):
        assert abs(t.z(x, y) - (x + 2 * y)) < 1e-6, (x, y, t.z(x, y))
    print("terrain_mesh OK")
