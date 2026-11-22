"""Check actual map metadata and foliage crown coverage without the editor."""
import importlib.util
import json
import math
from pathlib import Path
import random
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]


def area(g,face):
    points=[g.v[i] for i in face];a=points[0];total=0
    for i in range(1,len(points)-1):
        b,c=points[i],points[i+1]
        u=[b[j]-a[j] for j in range(3)];v=[c[j]-a[j] for j in range(3)]
        cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        total+=math.sqrt(sum(x*x for x in cross))/2
    return total


class MapForestTest(unittest.TestCase):
    def test_detail_map_has_exact_entries_and_all_furnished_floors(self):
        data=json.loads((ROOT/'Content/Kadykchan/Data/TownMap.json').read_text())
        places=[p for p in data['places'] if p.get('floors',0)>=2]
        self.assertEqual(len(places),5)
        self.assertEqual(sorted(p['floors'] for p in places),[2,2,2,3,3])
        for p in places:
            self.assertEqual(len(p['entry']),2)
            self.assertAlmostEqual(math.dist(p['entry'],p['door']),6,delta=.02)
            self.assertEqual(len(p['details'].splitlines()),p['floors'])
            self.assertEqual(len(p['details_en'].splitlines()),p['floors'])
            self.assertLess(math.dist(p['entry'],[p['east_m'],p['north_m']]),25)
            self.assertTrue(all(' / ' in line for line in p['details'].splitlines()))

    def test_orlow_mission_targets_the_open_entrance(self):
        plan=json.loads((ROOT/'Content/Kadykchan/Data/TownMap.json').read_text())
        place=next(p for p in plan['places'] if p['name']=='Brigadier Orlow (Lenina 7)')
        story=json.loads((ROOT/'Content/Kadykchan/Data/Story.json').read_text())
        step=next(s for s in story['steps'] if s['id']=='orlow')
        self.assertAlmostEqual(step['door'][0],place['door'][1],delta=.02)
        self.assertAlmostEqual(step['door'][1],place['door'][0],delta=.02)

    def test_leaf_alpha_coverage_is_preserved_in_distant_mips(self):
        spec=importlib.util.spec_from_file_location('leaf_material_test',ROOT/'tools/editor/foliage_materials.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'unreal':types.SimpleNamespace(Vector4=lambda *v:v)}):
            spec.loader.exec_module(module)
        class Texture:
            values={}
            def set_editor_property(self,key,value):self.values[key]=value
            def get_editor_property(self,key):return self.values[key]
        texture=Texture();module.preserve_leaf_mips(texture)
        self.assertTrue(texture.values['do_scale_mips_for_alpha_coverage'])
        self.assertEqual(texture.values['alpha_coverage_thresholds'],(0,0,0,.333))

    def test_far_tree_crowns_keep_leaf_coverage_with_fewer_triangles(self):
        spec=importlib.util.spec_from_file_location('forest_test',ROOT/'tools/asset-pipeline/build_vegetation.py')
        module=importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules,{'bpy':types.SimpleNamespace()}),patch.object(sys,'argv',['test','--',str(ROOT)]):
            spec.loader.exec_module(module)
        for kind in ('larch','birch','sapling'):
            totals=[0,0,0];faces=[0,0,0]
            for lod in range(3):
                for k in range(4):
                    module.rnd=random.Random(f'{kind}-{k}')
                    g=module.INSTANCED[kind][0](lod)
                    totals[lod]+=sum(area(g,f) for f,m in zip(g.f,g.mat) if g.mats[m].startswith('Leaves_'))
                    faces[lod]+=len(g.f)
            self.assertGreater(totals[2],totals[0]*.85,kind)
            self.assertLess(faces[2],faces[0]*.4,kind)
        self.assertEqual(module.INSTANCED['larch'][2],0)
        self.assertGreaterEqual(module.INSTANCED['birch'][2],450000)
        self.assertGreaterEqual(module.INSTANCED['sapling'][2],300000)


if __name__=='__main__':unittest.main()
