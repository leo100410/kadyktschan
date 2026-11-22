"""Check actual generated update data before replacing assets in Unreal."""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'asset-pipeline'))
from residential import HOUSES
from neighbourhood_update import ROOT,blocked_doors

manifest=json.loads((ROOT/'assets/buildings/buildings_manifest.json').read_text())
by_label={b['label']:b for b in manifest}
for label,(floors,kind,themes) in HOUSES.items():
    b=by_label[label]
    assert b['furnished_floors']==floors,(label,'wrong floor count')
    assert b['section_frame'] and b['room_lights'],(label,'missing room layout')
    assert any('floor1-' in c['name'] for c in b['cameras']),(label,'upper floor absent')
    if floors==3:assert any('floor2-' in c['name'] for c in b['cameras']),(label,'second upper floor absent')
    assert len(b['room_lights'])==floors*9,(label,'ceiling fixtures not exported correctly')
    print(label, floors,'floors;',floors*2,'flats;',len(b['room_lights']),'lights')
scatter=json.loads((ROOT/'assets/vegetation/scatter.json').read_text())
assert scatter['neighbourhood_detail_version']==1
assert scatter['blocked_doors']==blocked_doors(manifest)
assert len(scatter['larch'])>180000
assert len(scatter['courtyard_details'])>15
story=json.loads((ROOT/'Content/Kadykchan/Data/Story.json').read_text())
assert story['steps'][0]['id']=='power'
assert len(story['steps'])==7
print('TOTAL',sum(x[0]*2 for x in HOUSES.values()),'flats;',len(scatter['larch']),'larches;',len(scatter['courtyard_details']),'courtyard groups')
print('RESULT OK')
