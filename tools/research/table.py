import json, math, sys
exec(open('tools/research/osm_buildings.py').read().split("print(f\"origin")[0].replace("d = json.load(open(sys.argv[1]))", "d = json.load(open('design/research/data/osm-kadykchan-2026-11-07.json'))"))
tr = {'улица Ленина':('ул. Ленина','Lenina'),'Школьная улица':('ул. Школьная','Shkolnaya'),'Южная улица':('ул. Южная','Yuzhnaya'),
      'улица Мира':('ул. Мира','Mira'),'улица 50 лет Октября':('ул. 50 лет Октября','50LetOktyabrya')}
def typ(lv, L, W):
    lv = int(lv) if lv.isdigit() else 0
    return {9:'T9 Plattenbau 9-geschossig',5:'T5 Plattenbau 5-geschossig',3:'T3 Wohnblock 3-geschossig',2:'T2 2-geschossig',1:'T1 1-geschossig'}.get(lv,'unbekannt')
rows=[]
for b in blds:
    t=b['tags']; g=b['geometry']; la,lo=centroid(g); pts=[xy(p['lat'],p['lon']) for p in g]
    _,L,W,ang=obb(pts); cx,cy=xy(la,lo)
    st=t.get('addr:street'); nr=t.get('addr:housenumber','')
    ru,lat=tr.get(st,('— (ohne Adresse)',None))
    pla=f"PLA_{lat}_{nr}" if lat else f"PLA_OSM_{b['id']}"
    lv=t.get('building:levels','?')
    rows.append((ru, nr, pla, lv, typ(lv,L,W), f"{la:.5f}, {lo:.5f}", f"{cy*100:,.0f} / {cx*100:,.0f}".replace(',', ' '), f"{L:.1f} × {W:.1f}", f"{ang:.0f}°", f"way/{b['id']}"))
rows.sort(key=lambda r:(r[0].startswith('—'), r[0], r[1].zfill(3)))
print("| Adresse | Nr. | Asset-Name | Geschosse (OSM) | Typ-Klasse | Lat, Lon | UE X / Y (cm) | Grundriss L × B (m) | Ausrichtung | OSM |")
print("|---|---|---|---|---|---|---|---|---|---|")
for r in rows: print("| "+" | ".join(r)+" |")
