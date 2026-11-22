"""Small offline checks for downloaded-file validation, terrain contact and road widths."""
import ast
import math
from pathlib import Path
import unittest

from fetch_surfaces import valid_jpeg
from verge_details import patch


class EnvironmentAssetsTest(unittest.TestCase):
    def test_download_rejects_html_and_truncated_files(self):
        self.assertFalse(valid_jpeg(b"<html>Forbidden</html>" * 100))
        self.assertFalse(valid_jpeg(b"\xff\xd8" + b"x" * 2000))
        self.assertTrue(valid_jpeg(b"\xff\xd8" + b"x" * 2000 + b"\xff\xd9"))

    def test_patch_tracks_terrain_and_faces_upwards(self):
        ground = lambda x, y: x * 0.2 - y * 0.3
        vs, uv, faces = patch(ground, 20, -30)
        self.assertEqual(len(vs), 81)
        self.assertEqual(len(faces), 128)
        for x, y, z in vs:
            self.assertAlmostEqual(z - ground(x, y), 0.04)
        for a, b, c in faces:
            ax, ay, _ = vs[a]; bx, by, _ = vs[b]; cx, cy, _ = vs[c]
            self.assertGreater((bx - ax) * (cy - ay) - (by - ay) * (cx - ax), 0)

    def test_road_erosion_keeps_at_least_92_percent_of_width(self):
        source = Path(__file__).with_name("lines_to_obj.py")
        tree = ast.parse(source.read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "edge_width")
        namespace = {"math": math}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), namespace)
        for x in range(-1000, 1001, 13):
            width = namespace["edge_width"](x, x * 0.7, 0.8)
            self.assertTrue(0.8 * 0.92 <= width <= 0.8 * 1.08)


if __name__ == "__main__":
    unittest.main()
