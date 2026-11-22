"""Geometry checks without launching Blender: python3 tools/asset-pipeline/test_furniture.py."""
import ast
from collections import Counter
import math
from pathlib import Path
import random
import types
import unittest
from unittest.mock import patch

import furniture as fu
from interiors import Section, FlatView


def mesh_class(filename, name, namespace):
    # Load the real accumulator without Blender; these checks only use its geometry arrays.
    tree = ast.parse(Path(__file__).with_name(filename).read_text())
    node = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == name)
    exec(compile(ast.Module(body=[node], type_ignores=[]), filename, "exec"), namespace)
    return namespace[name]


Part = mesh_class("build_t5_kit.py", "Part", {})
Acc = mesh_class("build_buildings.py", "Acc", {"kit": types.SimpleNamespace(Part=Part), "math": math})


def section(mirror=False):
    p = Part("test")
    return p, FlatView(Section(p, 2.6, random.Random(8)), 3.0, mirror)


class FurnitureTest(unittest.TestCase):
    def assert_closed(self, p):
        edges = Counter()
        volume = 0.0
        for face in p.faces:
            for a, b in zip(face, face[1:] + face[:1]):
                edges[tuple(sorted((a, b)))] += 1
            a = p.verts[face[0]]
            for i in range(1, len(face) - 1):
                b, c = p.verts[face[i]], p.verts[face[i + 1]]
                cross = (b[1] * c[2] - b[2] * c[1], b[2] * c[0] - b[0] * c[2], b[0] * c[1] - b[1] * c[0])
                volume += sum(a[k] * cross[k] for k in range(3)) / 6
        self.assertTrue(edges and all(n == 2 for n in edges.values()), "open or non-manifold mesh")
        self.assertGreater(volume, 0, "inward normals")
        self.assertEqual(len(p.faces), len(p.face_mat))
        self.assertTrue(all(math.isfinite(v) for point in p.verts for v in point))
        self.assertTrue(all(0 <= i < len(p.faces) for i in p.smooth_faces))

    def test_curved_parts_are_closed_and_mirror_outward(self):
        for mirror in (False, True):
            for rot in range(4):
                for build in (lambda p: fu.cushion(p, 0, 0.6, 0, 0.4, 0.4, 0.6),
                              lambda p: fu.blanket(p, 0, 1.4, 0, 1.8, 0.5), fu.chair, fu.armchair,
                              fu.sofa, fu.bed, fu.sewing_machine, lambda p: fu.curtains(p.S, -2.2, -0.8, 0.2)):
                    with self.subTest(mirror=mirror, rot=rot, shape=build):
                        p, f = section(mirror)
                        build(f.place(1, 2, rot))
                        self.assert_closed(p)

    def test_mirror_keeps_curves_and_cylinders_with_the_furniture(self):
        for build in (fu.chair, fu.sofa, fu.table, fu.bed, fu.sewing_machine, fu.tv):
            normal, f = section()
            reflected, r = section(True)
            args = (0.9, 0.7) if build is fu.table else ()
            build(f.place(-2, 1, 1), *args)
            build(r.place(-2, 1, 1), *args)
            self.assertEqual(len(normal.verts), len(reflected.verts))
            expected = sorted((round(3 - x, 6), round(y, 6), round(z, 6)) for x, y, z in normal.verts)
            actual = sorted(tuple(round(v, 6) for v in point) for point in reflected.verts)
            self.assertEqual(expected, actual)

    def test_cushions_stay_inside_the_previous_furniture_footprint(self):
        p, f = section()
        fu.cushion(f.place(0, 0), 0, 2, 0, 0.9, 0.3, 0.53)
        for x, y, z in p.verts:
            self.assertTrue(0 <= x <= 2 and 0 <= y <= 0.9 and 0.3 <= z <= 0.53)

    def test_building_merge_preserves_smooth_faces(self):
        p, f = section()
        fu.cushion(f.place(0, 0), 0, 1, 0, 1, 0, 0.2)
        acc = Acc("building")
        acc.box(0, 1, 0, 1, 0, 1, "Concrete")
        offset = len(acc.faces)
        acc.add(p, 0.3, 2, 3, 4, {})
        self.assertEqual(acc.smooth_faces, {offset + i for i in p.smooth_faces})

    def test_hall_curved_props_are_closed_and_keep_the_centre_aisle_clear(self):
        import kulturhaus
        with patch.dict("sys.modules", {"build_t5_kit": types.SimpleNamespace(Part=Part)}):
            p = Acc("hall")
            kulturhaus.build_hall(p, 0, 24, 0, 15, 0, 0, 5.38, 1964, door=(10.5, 12.3))
        self.assert_closed(p)
        self.assertGreater(len(p.smooth_faces), 1000)
        for index, face in enumerate(p.faces):
            points = [p.verts[i] for i in face]
            xs, ys, zs = zip(*points)
            blocked = max(xs) > 1 and min(xs) < 17 and max(ys) > 7.2 and min(ys) < 8.0 and max(zs) > 0.1 and min(zs) < 1.7
            self.assertFalse(blocked, "centre aisle blocked by " + p.mats[p.face_mat[index]])


if __name__ == "__main__":
    unittest.main()
