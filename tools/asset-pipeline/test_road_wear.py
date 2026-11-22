"""Run with a Python that has numpy (Blender's bundled Python is sufficient)."""
import unittest
import numpy as np
from road_wear import atlas


class RoadWearTest(unittest.TestCase):
    def test_deterministic_finite_channels(self):
        a = atlas(256, 512)
        np.testing.assert_array_equal(a, atlas(256, 512))
        self.assertTrue(np.isfinite(a).all())
        self.assertGreaterEqual(a.min(), 0)
        self.assertLessEqual(a.max(), 1)
        self.assertTrue(all((a[..., i] > 0).any() for i in range(4)))

    def test_centre_line_has_gaps_and_is_not_solid_white(self):
        paint = atlas(256, 512)[:, 128, 1]
        self.assertGreater(np.count_nonzero(paint), 10)
        self.assertGreater(np.count_nonzero(paint == 0), 200)
        self.assertLess(paint.max(), 1)


if __name__ == "__main__":
    unittest.main()
