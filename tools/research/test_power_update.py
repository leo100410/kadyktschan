"""Offline regression checks for road clearance and the new repair objective."""
import ast
import copy
import json
import math
from pathlib import Path
import unittest
from power_update import ROOT, clear_props, road_clear, choose_site, power_step


class PowerUpdateTest(unittest.TestCase):
    def test_pipes_split_before_crossing_and_remain_idempotent(self):
        layout={'roads':[{'width_m':6,'points_m':[[-20,0,0],[20,0,0]]}]}
        scatter={'pipes':[[[0,y,0] for y in range(-18,19,3)]], 'lamps':[[0,0,0,0],[0,10,0,0]]}
        clear_props(scatter,layout,{'east_m':100,'north_m':100})
        self.assertEqual(len(scatter['pipes']),2)
        self.assertEqual(len(scatter['lamps']),1)
        for line in scatter['pipes']:
            for a,b in zip(line,line[1:]):
                for i in range(21):
                    self.assertTrue(road_clear(a[0]+(b[0]-a[0])*i/20,a[1]+(b[1]-a[1])*i/20,layout['roads'],1))
        before=copy.deepcopy(scatter)
        clear_props(scatter,layout,{'east_m':100,'north_m':100})
        self.assertEqual(scatter,before)

    def test_road_edges_move_centimetres_not_metres(self):
        source=Path(__file__).with_name('lines_to_obj.py')
        tree=ast.parse(source.read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='edge_width')
        ns={'math':math}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),str(source),'exec'),ns)
        for x in range(-2000,2000):
            for w in (2,4,7):
                self.assertLessEqual(abs(ns['edge_width'](x,x*.7,w)-w),.030001)

    def test_site_is_clear_and_repair_precedes_old_story(self):
        layout=json.loads((ROOT/'design/research/data/blockout-2026-11-07.json').read_text())
        from terrain_mesh import TerrainMesh
        ground=TerrainMesh(ROOT/'assets/terrain/terrain_kadykchan_8km.obj').z
        site=choose_site(layout,ground)
        self.assertTrue(road_clear(site['east_m'],site['north_m'],layout['roads'],16))
        step=power_step(site)
        self.assertTrue(step['sequential'])
        self.assertEqual([c['id'] for c in step['clues']],['power_inspect','power_fuse','power_restore'])
        self.assertEqual(len({tuple(c['pos']) for c in step['clues']}),3)
        self.assertTrue(all(c['text_en'] for c in step['clues']))

    def test_station_mesh_is_finite_and_entrance_is_clear(self):
        import random
        import types
        from terrain_mesh import TerrainMesh
        source=ROOT/'tools/asset-pipeline/build_vegetation.py'
        nodes=[n for n in ast.parse(source.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in ('Geo','_uv','pbox','prism','rock')]
        helpers={'math':math,'rnd':random.Random(1943)}
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(source),'exec'),helpers)
        veg=types.SimpleNamespace(ROOT=str(ROOT),**{k:helpers[k] for k in ('Geo','_uv','pbox','prism','rock')})
        station=ROOT/'tools/asset-pipeline/build_power_station.py'
        text=station.read_text().split('# Raised lettering')[0]
        tree=ast.parse(text)
        nodes=[n for n in tree.body if not isinstance(n,(ast.Import,ast.ImportFrom)) and not (isinstance(n,ast.Expr) and isinstance(n.value,ast.Call) and (ast.unparse(n.value.func).startswith('sys.path.') or ast.unparse(n.value.func).startswith('veg.bpy.')))]
        ns=dict(Path=Path,math=math,json=json,veg=veg,TerrainMesh=TerrainMesh)
        exec(compile(ast.Module(body=nodes,type_ignores=[]),str(station),'exec'),ns)
        mesh=ns['g']; floor=ns['f']
        self.assertGreater(len(mesh.f),1000)
        self.assertTrue(all(0 <= i < len(mesh.v) for face in mesh.f for i in face))
        self.assertTrue(all(math.isfinite(c) for v in mesh.v for c in v))
        # A standing capsule can pass the front doorway; side doors and lintel stay outside it.
        for face in mesh.f:
            vs=[mesh.v[i] for i in face]
            lo=[min(v[a] for v in vs) for a in range(3)]
            hi=[max(v[a] for v in vs) for a in range(3)]
            overlaps=all(lo[a]<b and hi[a]>a0 for a,a0,b in ((0,-5.6,-4.9),(1,-.4,.4),(2,floor+.2,floor+2)))
            self.assertFalse(overlaps,'geometry obstructs doorway')


if __name__=='__main__': unittest.main()
