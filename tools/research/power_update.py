"""Fictional local diesel power station, repair objective and road-safe town props.
Positions are assumptions, not a reconstruction of a historical power plant.
"""
import json
import math
from pathlib import Path
from terrain_mesh import TerrainMesh

ROOT = Path(__file__).resolve().parents[2]
LAYOUT = ROOT / 'design/research/data/blockout-2026-11-07.json'


def segment_distance(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((x-a[0])*dx + (y-a[1])*dy) / (dx*dx+dy*dy or 1)))
    return math.hypot(x-a[0]-t*dx, y-a[1]-t*dy)


def road_clear(x, y, roads, margin):
    return all(segment_distance(x, y, a, b) > r['width_m']/2 + margin
               for r in roads for a, b in zip(r['points_m'], r['points_m'][1:]))


def building_clear(x, y, buildings, margin):
    for b in buildings:
        angle = math.radians(b['axis_deg_from_east'])
        dx, dy = x-b['east_m'], y-b['north_m']
        u, v = dx*math.cos(angle)+dy*math.sin(angle), -dx*math.sin(angle)+dy*math.cos(angle)
        if abs(u) < b['length_m']/2+margin and abs(v) < b['width_m']/2+margin:
            return False
    return True


def choose_site(layout, ground):
    candidates = []
    for e in range(150, 361, 5):
        for n in range(75, 246, 5):
            if not road_clear(e, n, layout['roads'], 16) or not building_clear(e, n, layout['buildings'], 18):
                continue
            near = min(segment_distance(e, n, a, b) for r in layout['roads'] for a,b in zip(r['points_m'],r['points_m'][1:]))
            if near > 40:
                continue
            heights = [ground(e+x, n+y) for x in (-10,0,10) for y in (-8,0,8)]
            slope = max(heights)-min(heights)
            if slope < 0.8:
                candidates.append((math.hypot(e-260,n)+slope*60+near, e,n,max(heights)+0.12))
    assert candidates, 'No clear station site: inspect layout before placing'
    _, e,n,z = min(candidates)
    return {'east_m':e,'north_m':n,'floor_m':round(z,3),'fictional':True}


def station_access(roads, site):
    start=(site['east_m'],site['north_m']-11,0)
    best=None
    for r in roads:
        for a,b in zip(r['points_m'],r['points_m'][1:]):
            dx,dy=b[0]-a[0],b[1]-a[1]
            t=max(0,min(1,((start[0]-a[0])*dx+(start[1]-a[1])*dy)/(dx*dx+dy*dy or 1)))
            q=(a[0]+t*dx,a[1]+t*dy,0)
            dist=math.dist(start,q)
            if best is None or dist<best[0]: best=(dist,q)
    assert best, 'No road for station access'
    return {'points_m':[start,best[1]],'width_m':2.4,'kind':'footway'}


def clear_props(scatter, layout, site):
    """Split pipes before road crossings instead of bridging across them."""
    e,n = site['east_m'],site['north_m']
    access=station_access(layout['roads'],site)
    roads=layout['roads']+[access]
    outside = lambda x,y: math.hypot(x-e,y-n) > 18
    pipes=[]
    for line in scatter.get('pipes',[]):
        run=[]
        for a,b in zip(line,line[1:]):
            count=max(1,math.ceil(math.dist(a[:2],b[:2])/0.5))
            safe=all(road_clear(a[0]+(b[0]-a[0])*t/count, a[1]+(b[1]-a[1])*t/count,roads,1.0)
                     and outside(a[0]+(b[0]-a[0])*t/count,a[1]+(b[1]-a[1])*t/count) for t in range(count+1))
            if safe:
                if not run: run=[a]
                run.append(b)
            else:
                if len(run)>1: pipes.append(run)
                run=[]
        if len(run)>1: pipes.append(run)
    scatter['pipes']=pipes
    for kind,items in list(scatter.items()):
        if kind == 'pipes' or not isinstance(items,list): continue
        if not items or not isinstance(items[0],list) or len(items[0])<3 or not isinstance(items[0][0],(float,int)): continue
        # Clear the new building footprint, keeping the rest of the town intact.
        scatter[kind]=[p for p in items if outside(p[0],p[1]) and road_clear(p[0],p[1],[access],1.5)]
    for kind,margin in [('lamps',2.2),('benches',1.5),('playgrounds',5),('garages',5),('tanks',3),('huts',6)]:
        scatter[kind]=[p for p in scatter.get(kind,[]) if road_clear(p[0],p[1],layout['roads'],margin)]


def power_step(site):
    e,n,z=site['east_m'],site['north_m'],site['floor_m']
    finds=[('power_inspect','Notstromanlage prüfen','Die alte Netzeinspeisung ist abgetrennt. Ein kleines Dieselaggregat versorgt nur den Beleuchtungsring. Die Ersatzsicherung liegt auf der Werkbank.','Inspect backup plant','The old mains feed is isolated. A small diesel set supplies only the lighting circuit. A spare fuse is on the workbench.',[n+3.1,e-3.8,z+1.45]),
           ('power_fuse','Ersatzsicherung einsetzen','Du setzt die bereitliegende Sicherung in den getrennten Notstromkreis ein. Jetzt fehlt noch der Start am Starthebel.','Fit spare fuse','You fit the spare fuse into the isolated backup circuit. Use the start lever to start the set.',[n+1,e+3.6,z+1.05]),
           ('power_restore','Notstrom starten','Das Aggregat läuft an. Auf der Straße leuchten erste gelbe Lampen. Einige Leitungen und Leuchten sind beschädigt; die Versorgung bleibt unzuverlässig.','Start backup power','The generator starts. The first yellow streetlights come on. Damaged cables and fixtures leave parts of the circuit unreliable.',[n+3.1,e-1.8,z+1.35])]
    return {'id':'power','place':'Elektrizitätswerk','place_en':'Power station','sequential':True,
            'goal':'Geh zum verlassenen Elektrizitätswerk. Prüfe die Anlage, setze die Ersatzsicherung ein und starte den Notstrom (E).',
            'goal_en':'Go to the abandoned power station. Inspect the set, fit the spare fuse and start backup power (E).',
            'done':'Der Beleuchtungsring hat wieder Strom. Sieh dich nun in Antoninas Wohnung um.',
            'done_en':"The lighting circuit has power again. Now explore Antonina’s flat.",
            'door':[n-5.8,e,z],
            'clues':[dict(id=i,title=t,text=x,title_en=te,text_en=xe,pos=p) for i,t,x,te,xe,p in finds]}


def main():
    layout=json.loads(LAYOUT.read_text())
    ground=TerrainMesh(ROOT/'assets/terrain/terrain_kadykchan_8km.obj').z
    sitepath=ROOT/'assets/power/site.json'
    site= json.loads(sitepath.read_text()) if sitepath.exists() else choose_site(layout,ground)
    sitepath.parent.mkdir(parents=True,exist_ok=True)
    sitepath.write_text(json.dumps(site,indent=1))
    scatterpath=ROOT/'assets/vegetation/scatter.json'
    scatter=json.loads(scatterpath.read_text())
    before=sum(len(x) for x in scatter['pipes'])
    clear_props(scatter,layout,site)
    scatterpath.write_text(json.dumps(scatter,separators=(',',':')))
    lights=[]
    for e,n,z,yaw in scatter['lamps']:
        a=math.radians(yaw)
        lights.append(dict(pos=[n+1.6*math.cos(a),e+1.6*math.sin(a),z+7.02],indoor=False))
    # Camera positions are inside the furnished rooms; lift toward their ceilings.
    manifest=json.loads((ROOT/'assets/buildings/buildings_manifest.json').read_text())
    for b in manifest:
        if b['label'] not in ('PLA_Lenina_8','PLA_Lenina_7','PLA_SAT_S_Block','PLA_Shkolnaya_4','PLA_Shkolnaya_6'): continue
        if b.get('room_lights'):
            lights.extend(dict(pos=p,indoor=True) for p in b['room_lights'])
            continue
        for camera in b.get('cameras',[]):
            if not any(camera['name'].endswith('-'+room) for room in ('living','kitchen','bedroom')): continue
            lights.append(dict(pos=[camera['north_m'],camera['east_m'],camera['z_m']+0.8],indoor=True))
    data=dict(site=site,lights=lights)
    (ROOT/'Content/Kadykchan/Data/Power.json').write_text(json.dumps(data,indent=1))
    print('POWER DATA OK',site,'lights',len(lights),'pipe points',before,'->',sum(len(x) for x in scatter['pipes']))


if __name__=='__main__': main()
