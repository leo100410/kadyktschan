import json, math, sys
d = json.load(open(sys.argv[1]))
blds = [x for x in d['elements'] if x['type'] == 'way' and 'building' in x.get('tags', {})]
def centroid(g): return sum(p['lat'] for p in g)/len(g), sum(p['lon'] for p in g)/len(g)
# Origin: centroid of the 5+ storey blocks (main residential area = Neuestes), ANNAHME
big = [centroid(b['geometry']) for b in blds if int(b['tags'].get('building:levels', '0') or 0) >= 5]
lat0 = sum(c[0] for c in big)/len(big); lon0 = sum(c[1] for c in big)/len(big)
R = 6371008.8
def xy(lat, lon): return (math.radians(lon-lon0)*R*math.cos(math.radians(lat0)), math.radians(lat-lat0)*R)
def obb(pts):
    # minimum-area rectangle over hull edges (footprints are small, brute force over edges is fine)
    best = None
    for i in range(len(pts)-1):
        (x1,y1),(x2,y2) = pts[i], pts[i+1]
        a = math.atan2(y2-y1, x2-x1); ca, sa = math.cos(a), math.sin(a)
        u = [ x*ca+y*sa for x,y in pts]; v = [-x*sa+y*ca for x,y in pts]
        L, W = max(u)-min(u), max(v)-min(v)
        if best is None or L*W < best[0]: best = (L*W, max(L,W), min(L,W), (math.degrees(a) if L>=W else math.degrees(a)+90) % 180)
    return best
print(f"origin lat0={lat0:.6f} lon0={lon0:.6f}")
rows = []
for b in blds:
    t = b['tags']; g = b['geometry']; la, lo = centroid(g)
    pts = [xy(p['lat'], p['lon']) for p in g]
    _, L, W, ang = obb(pts)
    cx, cy = xy(la, lo)
    rows.append((t.get('addr:street','-'), t.get('addr:housenumber','-'), t.get('building'), t.get('building:levels','?'), la, lo, cx, cy, L, W, ang, b['id']))
for r in sorted(rows, key=lambda r: (r[0], r[1].zfill(3))):
    print(f"{r[0]:<22} {r[1]:>3} {r[2]:<8} lv={r[3]:>2} {r[4]:.5f},{r[5]:.5f} x={r[6]:7.0f} y={r[7]:7.0f}  {r[8]:5.1f}x{r[9]:4.1f}m  az={r[10]:5.1f}  way/{r[11]}")
