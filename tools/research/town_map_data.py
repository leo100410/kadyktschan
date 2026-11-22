"""Town plan for the in-game map (K): building footprints, roads, rivers and the furnished places.

Usage: python3 -I town_map_data.py <blockout.json> <buildings_manifest.json> <out TownMap.json>
Coordinates in metres, east/north from the town origin (UE: X = north * 100, Y = east * 100).
"""
import json, os, sys

# furnished interiors, numbered as on the map; kind "story" = story rooms, "base" = phase-3 interiors
PLACES = [
    ("PLA_SAT_S_Block", "story", "Wohnung Gorbunow"),
    ("PLA_OSM_170991713", "story", "Kesselhaus"),
    ("PLA_Shkolnaya_8", "story", "Telefonzentrale"),
    ("PLA_Lenina_8", "story", "Antonina (Lenina 8)"),
    ("PLA_Lenina_7", "story", "Brigadier Orlow (Lenina 7)"),
    ("PLA_Shkolnaya_3", "base", "Laden"),
    ("PLA_Yuzhnaya_9", "base", "Kulturhaus"),
]

NAME_EN = {"Wohnung Gorbunow": "Gorbunov's flat", "Kesselhaus": "Boiler house", "Telefonzentrale": "Telephone exchange",
           "Brigadier Orlow (Lenina 7)": "Brigade leader Orlov (Lenina 7)", "Laden": "Shop", "Kulturhaus": "House of Culture"}


def main():
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    man = {b["label"]: b for b in json.load(open(sys.argv[2], encoding="utf-8"))}
    out = {
        "buildings": [[b["east_m"], b["north_m"], b["length_m"], b["width_m"], b["axis_deg_from_east"]] for b in d["buildings"]],
        "roads": [[[p[0], p[1]] for p in r["points_m"]] for r in d["roads"]],
        "rivers": [[[p[0], p[1]] for p in r["points_m"]] for r in d["rivers"]],
        "places": [],
    }
    by_label = {b["label"]: b for b in d["buildings"]}
    for label, kind, name in PLACES:
        b = by_label[label]
        ent = man[label]["entrances"]
        n, e, _ = ent[len(ent) // 2]
        if man[label].get("section_frame"):
            origin, along, inward = man[label]["section_frame"]
            n, e = origin[0]+along[0]*1.5-inward[0]*6, origin[1]+along[1]*1.5-inward[1]*6
        out["places"].append({"name": name, "name_en": NAME_EN.get(name, name), "kind": kind, "east_m": b["east_m"], "north_m": b["north_m"], "door": [e, n]})
    site = os.path.join(os.path.dirname(sys.argv[2]), "..", "mine", "adit_site.json")
    if os.path.exists(site):  # Stollen 3 (tools/research/mine_site.py): a place without a building footprint
        e, n = json.load(open(site))["portal"]
        out["places"].append({"name": "Stollen 3", "name_en": "Adit 3", "kind": "story", "east_m": e, "north_m": n, "door": [e, n]})
    power_site = os.path.join(os.path.dirname(sys.argv[2]), "..", "power", "site.json")
    if os.path.exists(power_site):
        power = json.load(open(power_site))
        e, n = power["east_m"], power["north_m"]
        out["places"].append({"name": "Elektrizitätswerk", "name_en": "Power station", "kind": "story", "east_m": e, "north_m": n, "door": [e, n-5.8]})
        out["buildings"].append([e, n, 12, 10, 0])
    for label, name in (("PLA_Shkolnaya_4", "Wohnhaus Schkolnaja 4"), ("PLA_Shkolnaya_6", "Wohnhaus Schkolnaja 6")):
        b = man.get(label)
        if b and b.get("section_frame"):
            origin, along, inward = b["section_frame"]
            n, e = origin[0] + along[0]*1.5 - inward[0]*6, origin[1] + along[1]*1.5 - inward[1]*6
            out["places"].append({"name": name, "name_en": name.replace("Wohnhaus Schkolnaja", "Residential block Shkolnaya"), "kind": "base", "east_m": b["east_m"], "north_m": b["north_m"], "door": [e,n]})
    # Detail map: exact furnished entrance and the actual floor allocation from the residential builder.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "asset-pipeline"))
    from residential import HOUSES
    profiles = {"teacher": ("Lehrerin", "Teacher"), "nurse": ("Pflegekraft", "Nurse"), "family": ("Familie", "Family"),
                "seamstress": ("Schneiderin", "Seamstress"), "technician": ("Funktechniker", "Radio technician"), "retired": ("Ruheständler", "Retired resident")}
    ground = {"lenina8": ("Antonina / Nachbarwohnung", "Antonina / neighbour"), "lenina7": ("Orlow / beschädigte Wohnung", "Orlov / damaged flat"),
              "family": ("Gorbunow / Nachbarwohnung", "Gorbunov / neighbour")}
    for label, (floors, kind, themes) in HOUSES.items():
        b = man.get(label)
        if not b or not b.get("section_frame") or not b.get("furnished_floors"): continue
        place = min(out["places"], key=lambda p: (p["east_m"]-b["east_m"])**2+(p["north_m"]-b["north_m"])**2)
        assert abs(place["east_m"]-b["east_m"])<.1 and abs(place["north_m"]-b["north_m"])<.1
        origin, along, _ = b["section_frame"]
        place["entry"] = [round(origin[1]+along[1]*1.5,3), round(origin[0]+along[0]*1.5,3)]
        place["floors"] = b["furnished_floors"]
        de, en = [], []
        for level in range(floors):
            if level == 0 and kind in ground:
                pair = ground[kind]
            else:
                offset = (level-(kind != "homes"))*2
                a, c = profiles[themes[offset]], profiles[themes[offset+1]]
                pair = (a[0]+" / "+c[0], a[1]+" / "+c[1])
            de.append(("EG" if level==0 else str(level)+". OG")+": "+pair[0])
            en.append(("Ground" if level==0 else "Floor "+str(level))+": "+pair[1])
        place["details"], place["details_en"] = "\n".join(de), "\n".join(en)
    json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False)
    assert len(out["places"]) >= len(PLACES) and out["buildings"] and out["roads"]
    print("town map: %d buildings, %d roads, %d places" % (len(out["buildings"]), len(out["roads"]), len(out["places"])))


if __name__ == "__main__":
    main()
