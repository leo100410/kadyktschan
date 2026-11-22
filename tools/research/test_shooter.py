"""Offline checks for the shooter mode data: nothing in walls or doorways, every flat stocked, a way in and out."""
import json
import math
import unittest
from power_update import ROOT, LAYOUT, building_clear
import shooter_data as sd


class ShooterDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = sd.main()
        cls.layout = json.loads(LAYOUT.read_text())
        manifest = json.loads((ROOT / 'assets/buildings/buildings_manifest.json').read_text())
        cls.doors = [(p[0], p[1]) for b in manifest for p in b.get('entrances', [])]

    def area(self):
        a = self.data['area']
        return a['east'][0], a['east'][1], a['north'][0], a['north'][1]

    def test_obstacles_stay_out_of_buildings_and_doorways(self):
        self.assertGreater(len(self.data['obstacles']), 20)
        for o in self.data['obstacles']:
            n, e, _ = o['pos']
            self.assertIn(o['mesh'], sd.OBSTACLES)
            self.assertTrue(building_clear(e, n, self.layout['buildings'], 1.9), o)
            self.assertTrue(sd.doors_clear(e, n, self.doors, sd.DOOR_CLEAR - 0.1), o)
            self.assertTrue(sd.inside(e, n, self.area()), o)

    def test_every_furnished_flat_has_its_household_item(self):
        flats = self.data['flats']
        self.assertEqual(len(flats), 24)
        for f in flats:
            self.assertIn(f['item'], self.data['items'])
            self.assertGreaterEqual(len(f['points']), 2, f['where'])
        # the five houses with two flats per furnished floor
        self.assertEqual(len({(f['house'], f['floor'], f['side']) for f in flats}), 24)

    def test_starts_and_tasks_lie_in_the_play_area(self):
        self.assertGreaterEqual(len(self.data['starts']), 3)
        for n, e, _, yaw in self.data['starts']:
            self.assertTrue(sd.inside(e, n, self.area()))
            self.assertTrue(-180 <= yaw <= 180)
        ids = {t['id'] for t in self.data['tasks']}
        self.assertGreaterEqual(len(ids), self.data['tuning']['tasks_per_round'])
        for t in self.data['tasks']:
            if 'pos' in t:
                self.assertTrue(sd.inside(t['pos'][1], t['pos'][0], self.area()), t['id'])

    def test_turrets_and_patrols_are_placed(self):
        self.assertGreaterEqual(len(self.data['turrets']), 3)
        self.assertGreaterEqual(len(self.data['patrols']), 5)
        for p in self.data['patrols']:
            self.assertEqual(len(p['route']), 3)

    def test_obstacle_slalom_leaves_a_lane(self):
        # no two street obstacles closer than 9 m: the street never closes completely
        street = [o for o in self.data['obstacles']]
        for i, a in enumerate(street):
            for b in street[i + 1:]:
                self.assertGreater(math.hypot(a['pos'][0] - b['pos'][0], a['pos'][1] - b['pos'][1]), 8.9)


if __name__ == '__main__':
    unittest.main()
