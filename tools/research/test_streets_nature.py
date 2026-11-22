import copy
import importlib.util
import math
from pathlib import Path
import random
import sys
import types
import unittest
from unittest.mock import patch

from refine_vegetation import refine


class NatureTest(unittest.TestCase):
    def test_refinement_preserves_props_safe_locations_and_roof_plants(self):
        data = {"larch": [], "birch": [], "willow": [[i * 3, i * 2, 0, i, 1] for i in range(200)],
                "sapling": [[800 + i, 400, 0, 0, 1] for i in range(100)],
                "shrub": [[10, 20, 5, 0, 0.5]], "pipes": [[[1, 2, 3], [4, 5, 6]]]}
        old = copy.deepcopy(data)
        layout = {"roads": [], "rivers": [], "buildings": []}
        result = refine(data, lambda e, n: 0, layout, [])
        self.assertEqual(result["pipes"], old["pipes"])
        self.assertIn(old["shrub"][0], result["shrub"])
        locations = {tuple(v[:3]) for kind in ("larch", "birch", "willow", "sapling", "shrub") for v in old[kind]}
        plants = [p for k in ("larch", "birch", "willow", "sapling", "shrub", "low_willow", "alder", "dry_shrub") for p in result[k]]
        self.assertTrue(all(tuple(p[:3]) in locations for p in plants))
        self.assertEqual(len(plants), len({tuple(p[:3]) for p in plants}))
        self.assertEqual(result, refine(copy.deepcopy(result), lambda e, n: 0, layout, []))

    def test_roadside_growth_keeps_the_road_and_entrance_clear(self):
        data = {"larch": [], "willow": [[i * 0.7, 12, 0, 0, 1] for i in range(150)], "sapling": [], "shrub": []}
        layout = {"roads": [{"width_m": 6, "points_m": [[-100, 0, 0], [200, 0, 0]]}], "rivers": [], "buildings": []}
        result = refine(data, lambda e, n: 0, layout, [{"entrances": [[0, 30, 0]]}])
        plants = [v for k in ("willow", "low_willow", "alder", "shrub", "dry_shrub") for v in result[k]]
        self.assertTrue(any(p[1] < 10 for p in plants))
        for e, n, *_ in plants:
            self.assertGreaterEqual(n, 3.8)
            self.assertGreaterEqual(math.hypot(e - 30, n), 9)

    def test_new_bushes_have_distinct_heights_and_consistent_lod_materials(self):
        root = Path(__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location("nature_geometry_test", root / "tools/asset-pipeline/build_vegetation.py")
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {"bpy": types.SimpleNamespace()}), patch.object(sys, "argv", ["test", "--", str(root)]):
            spec.loader.exec_module(module)
        heights = {}
        for kind in ("low_willow", "alder", "dry_shrub"):
            slots = None
            for lod in range(3):
                module.rnd = random.Random(kind)
                g = getattr(module, kind)(lod)
                self.assertEqual(len(g.f), len(g.uv))
                self.assertTrue(all(math.isfinite(v) for p in g.v for v in p))
                if slots is None:
                    slots = g.mats
                    heights[kind] = max(v[2] for v in g.v)
                self.assertEqual(slots, g.mats)
        self.assertLess(heights["low_willow"], 1.5)
        self.assertGreater(heights["alder"], 2)
        self.assertLess(heights["dry_shrub"], 1.5)


if __name__ == "__main__":
    unittest.main()
