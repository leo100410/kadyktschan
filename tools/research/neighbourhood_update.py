"""Denser, clustered woodland and deliberately placed courtyard details; no new historical buildings."""
import json
import math
from pathlib import Path
import random
from power_update import segment_distance, station_access, clear_props
from terrain_mesh import TerrainMesh

ROOT=Path(__file__).resolve().parents[2]
GRID=json.loads((ROOT/'tools/asset-pipeline/kit_grid.json').read_text())['T5']
FLOOR_OFFSET=GRID['pile']['crawl_height']+GRID['plinth_band']-.1
PLANTS=('larch','birch','sapling','willow','low_willow','alder','shrub','dry_shrub','grass')


def densify(data,layout,manifest,ground,power=None,mine=None,targets=(80000,12000,3500)):
    if data.get('neighbourhood_detail_version')==1: return data
    rng=random.Random(20111110)
    segments=[]
    roads=list(layout['roads'])
    # Keep every existing approach to a doorway clear, including the new power station.
    for b in manifest:
        for n,e,yaw in b.get('entrances',[]):
            a=math.radians(yaw);sx,sy=e+4.5*math.sin(a),n+4.5*math.cos(a)
            best=None
            for r in layout['roads']:
                for p,q in zip(r['points_m'],r['points_m'][1:]):
                    dx,dy=q[0]-p[0],q[1]-p[1]
                    t=max(0,min(1,((sx-p[0])*dx+(sy-p[1])*dy)/(dx*dx+dy*dy or 1)))
                    x,y=p[0]+t*dx,p[1]+t*dy;d=math.hypot(x-sx,y-sy)
                    if best is None or d<best[0]:best=(d,x,y)
            if best and best[0]<150:
                roads.append(dict(points_m=[(sx,sy,0),(best[1],best[2],0)],width_m=2.2))
    if power: roads.append(station_access(layout['roads'],power))
    buckets={}
    for road in roads+[{**r,'width_m':20} for r in layout.get('rivers',[])]:
        for a,b in zip(road['points_m'],road['points_m'][1:]):
            pad=road['width_m']/2+5
            idx=len(segments);segments.append((a,b,road['width_m']/2))
            for i in range(math.floor((min(a[0],b[0])-pad)/32),math.floor((max(a[0],b[0])+pad)/32)+1):
                for j in range(math.floor((min(a[1],b[1])-pad)/32),math.floor((max(a[1],b[1])+pad)/32)+1):
                    buckets.setdefault((i,j),[]).append(idx)
    footprints=[];build_grid={}
    for b in layout['buildings']:
        angle=math.radians(b['axis_deg_from_east']);ca,sa=math.cos(angle),math.sin(angle)
        hl,hw=b['length_m']/2+3,b['width_m']/2+3
        idx=len(footprints);footprints.append((b['east_m'],b['north_m'],ca,sa,hl,hw))
        radius=math.hypot(hl,hw)
        for i in range(math.floor((b['east_m']-radius)/32),math.floor((b['east_m']+radius)/32)+1):
            for j in range(math.floor((b['north_m']-radius)/32),math.floor((b['north_m']+radius)/32)+1):
                build_grid.setdefault((i,j),[]).append(idx)
    doors=[(e,n) for b in manifest for n,e,_ in b.get('entrances',[])]
    def safe(e,n,margin=2):
        key=(math.floor(e/32),math.floor(n/32))
        for idx in buckets.get(key,[]):
            a,b,half=segments[idx]
            if segment_distance(e,n,a,b)<half+margin:return False
        for idx in build_grid.get(key,[]):
            x,y,ca,sa,hl,hw=footprints[idx];dx,dy=e-x,n-y
            if abs(dx*ca+dy*sa)<hl and abs(-dx*sa+dy*ca)<hw:return False
        if math.hypot(e,n)<900 and any(math.hypot(e-x,n-y)<8 for x,y in doors):return False
        if power and math.hypot(e-power['east_m'],n-power['north_m'])<19:return False
        if mine and math.hypot(e-mine[0],n-mine[1])<80:return False
        return True
    occupied={(math.floor(e/5),math.floor(n/5)) for kind in ('larch','birch') for e,n,*_ in data.get(kind,[])}
    added={}
    for zone,target in enumerate(targets):
        accepted=0
        for _ in range(target*20):
            if accepted>=target:break
            if zone==0:
                lo,hi=(350,1700) if rng.random()<.78 else (1700,2500)
            elif zone==1:lo,hi=220,1400
            else:lo,hi=0,650
            radius=math.sqrt(rng.uniform(lo*lo,hi*hi));angle=rng.uniform(0,math.tau)
            e,n=radius*math.cos(angle),radius*math.sin(angle)
            patch=math.sin(e*.009)+math.cos(n*.013)+.6*math.sin((e+n)*.023)
            if rng.random()>(.92 if patch>-.3 else .32):continue
            if not safe(e,n):continue
            cell=(math.floor(e/5),math.floor(n/5))
            if zone==0 and cell in occupied:continue
            kind='larch' if zone==0 else rng.choice(('alder','low_willow','sapling','shrub')) if zone==1 else rng.choice(('birch','sapling','low_willow'))
            if zone==0:occupied.add(cell)
            scale=rng.uniform(.85,1.4) if zone==0 else rng.uniform(.7,1.2)
            data.setdefault(kind,[]).append([round(e,2),round(n,2),round(ground(e,n),3),round(rng.uniform(0,360),1),round(scale,2)])
            added[kind]=added.get(kind,0)+1;accepted+=1
    # Group objects beside actual buildings instead of spreading isolated boxes over the streets.
    details=[]
    for b in layout['buildings']:
        if math.hypot(b['east_m'],b['north_m'])>850:continue
        a=math.radians(b['axis_deg_from_east']);ca,sa=math.cos(a),math.sin(a)
        for side in (-1,1):
            u=rng.uniform(-.32,.32)*b['length_m'];v=side*(b['width_m']/2+7)
            e,n=b['east_m']+u*ca-v*sa,b['north_m']+u*sa+v*ca
            occupied_props=[p for kind in ('huts','tanks','garages','playgrounds') for p in data.get(kind,[])]
            if safe(e,n,4) and all(math.hypot(e-p[0],n-p[1])>9 for p in occupied_props) and all(math.hypot(e-p[0],n-p[1])>8 for p in details):
                details.append([round(e,2),round(n,2),round(ground(e,n),3),round(math.degrees(a),1),rng.randrange(5)])
    data['courtyard_details']=details
    # Leave usable space around the small scenes (bins, benches, cycle racks, planters).
    detail_grid={}
    for e,n,*_ in details:detail_grid.setdefault((math.floor(e/16),math.floor(n/16)),[]).append((e,n))
    for kind in PLANTS:
        kept=[]
        for plant in data.get(kind,[]):
            e,n=plant[:2];i,j=math.floor(e/16),math.floor(n/16)
            if any(math.hypot(e-x,n-y)<3.5 for di in (-1,0,1) for dj in (-1,0,1) for x,y in detail_grid.get((i+di,j+dj),[])):continue
            kept.append(plant)
        data[kind]=kept
    data['neighbourhood_detail_version']=1
    if power:clear_props(data,layout,power)
    print('NEIGHBOURHOOD added',added,'courtyard groups',len(details))
    return data


def blocked_doors(manifest):
    opened={'PLA_Lenina_8','PLA_Lenina_7','PLA_SAT_S_Block','PLA_Shkolnaya_4','PLA_Shkolnaya_6',
            'PLA_Shkolnaya_3','PLA_Shkolnaya_8','PLA_OSM_170991713'}
    blocked=[]
    for b in manifest:
        entries=b.get('entrances',[]);allowed=len(entries)//2 if b['label']=='PLA_Yuzhnaya_9' else -1
        frame=b.get('section_frame')
        if b['label'] in opened and entries and frame:
            origin,along,inward=frame
            centre=(origin[0]+along[0]*1.5,origin[1]+along[1]*1.5)
            allowed=min(range(len(entries)),key=lambda i:math.hypot(entries[i][0]+6*math.cos(math.radians(entries[i][2]))-centre[0],entries[i][1]+6*math.sin(math.radians(entries[i][2]))-centre[1]))
        for i,(n,e,yaw) in enumerate(entries):
            if i==allowed:continue
            a=math.radians(yaw)
            blocked.append([round(e+6.08*math.sin(a),3),round(n+6.08*math.cos(a),3),round(b['ground_m']+FLOOR_OFFSET,3),yaw])
    return blocked


def main():
    path=ROOT/'assets/vegetation/scatter.json';data=json.loads(path.read_text())
    layout=json.loads((ROOT/'design/research/data/blockout-2026-11-07.json').read_text())
    manifest=json.loads((ROOT/'assets/buildings/buildings_manifest.json').read_text())
    power=json.loads((ROOT/'assets/power/site.json').read_text())
    mine=json.loads((ROOT/'assets/mine/adit_site.json').read_text())['portal']
    densify(data,layout,manifest,TerrainMesh(ROOT/'assets/terrain/terrain_kadykchan_8km.obj').z,power,mine)
    data['blocked_doors']=blocked_doors(manifest)
    path.write_text(json.dumps(data,separators=(',',':')))
    print('NEIGHBOURHOOD DATA OK','blocked doors',len(data['blocked_doors']))


if __name__=='__main__':main()
