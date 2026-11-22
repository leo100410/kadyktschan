"""Shooter mode "Einsatz" (design/gdd/shooter-mode.md): tuning, task pool, flat pickups, spawns and obstacles.

Fiction only: looters and their machines in the empty centre, no real people. Everything is placed from the existing
data (buildings manifest, blockout roads, scatter props, story finds), so nothing lands in a wall or a doorway.
Usage: python3 tools/research/shooter_data.py   -> Content/Kadykchan/Data/Shooter.json
Positions are [north, east, z] metres like Story.json; z of ground points is the rendered terrain (the game still
traces down onto road ribbons and floors).
"""
import json
import math
import random
from pathlib import Path
from power_update import ROOT, LAYOUT, segment_distance, road_clear, building_clear
from terrain_mesh import TerrainMesh

OUT = ROOT / 'Content/Kadykchan/Data/Shooter.json'
MARGIN = 30.0         # play area = the furnished centre's bounding box plus this, metres
OBSTACLE_STEP = 17.0  # metres of road between two obstacles: breaks the long sightlines of the straight streets
DOOR_CLEAR = 5.0      # keep doorways and their approach free
PROP_CLEAR = 3.2      # keep clear of the street furniture already there (pipes, cars, lamps ...)
YARD_STEP = 20        # grid spacing (m) of the courtyard candidates

# player and enemy tuning; damage is health points per hit, ranges metres, intervals seconds (rationale in the GDD)
TUNING = {
    'player': {'health': 100, 'mag': 30, 'reserve': 90, 'damage': 40, 'range_m': 160, 'interval_s': 0.1,
               'spread_deg': 0.6, 'spread_hip_deg': 2.2, 'reload_s': 2.3, 'fov': 100, 'fov_aim': 72,
               'noise_m': 70},
    'enemies': {
        # first playtest 2026-11-11: 22 damage killed the player in 5 s at the start; now about 7 looter hits
        # user 2026-11-11: no more standing and firing from far away - fire only inside range_m, fight from a spot
        # engage_min..engage_max metres away (cover first), move on after reposition_s, flank
        'looter': {'health': 100, 'damage': 14, 'interval_s': 0.16, 'burst': 3, 'pause_s': 1.2, 'spread_deg': 4.0,
                   'range_m': 32, 'sight_m': 60, 'react_s': 0.9, 'speed': 360, 'cover_below': 0.65,
                   'engage_min_m': 12, 'engage_max_m': 26, 'reposition_s': 8},
        'drone': {'health': 60, 'damage': 8, 'interval_s': 0.12, 'burst': 5, 'pause_s': 1.6, 'spread_deg': 5.0,
                  'range_m': 16, 'sight_m': 40, 'react_s': 0.5, 'speed': 520, 'cover_below': 0,
                  'engage_min_m': 5, 'engage_max_m': 12, 'reposition_s': 2.5},
        # 16 damage and bursts of 6 killed in 5 s at 19 m (playtest 2026-11-11): the whine must leave time for cover
        'turret': {'health': 160, 'damage': 11, 'interval_s': 0.22, 'burst': 5, 'pause_s': 1.8, 'spread_deg': 2.6,
                   'range_m': 45, 'sight_m': 45, 'react_s': 1.6, 'speed': 0, 'cover_below': 0},
    },
    'distortion_exponent': 0.8,  # camcorder breakdown = (1 - health/max)^exponent: early hits already show
    'extract_hold_s': 30, 'tasks_per_round': 3, 'pickup_share': 0.6, 'jam_s': 60,
    'reinforcements': 2,         # looters arriving from the far edge after every finished task
    'target_fps': 45,            # dynamic graphics: frame rate the round tries to hold (user 2026-11-11)
    'max_shooters': 2,           # looters firing at once; the rest advance and flank (readable fights)
    'safe_start_m': 55,          # no enemy spawns this close to the player's start
    # user 2026-11-11: health recovers slowly, the picture faster; a new hit drops the picture back to the health
    'regen_delay_s': 5, 'health_regen': 1.5, 'vision_regen': 12,
}
# what each household leaves behind (residential.THEMES plus the ground-floor story flats)
ITEMS = {'bandage': {'heal': 35}, 'medkit': {'heal': 70}, 'ammo': {'rounds': 60}, 'vest': {'armor': 50}}
THEME_ITEM = {'teacher': 'bandage', 'nurse': 'medkit', 'family': 'bandage', 'seamstress': 'bandage',
              'technician': 'ammo', 'retired': 'medkit', 'antonina': 'bandage', 'neighbour': 'ammo',
              'orlow': 'vest', 'damaged': 'ammo', 'gorbunov': 'ammo'}
GROUND_STORY = {'PLA_Lenina_8': ('antonina', 'neighbour'), 'PLA_Lenina_7': ('orlow', 'damaged'),
                'PLA_SAT_S_Block': ('gorbunov', 'neighbour')}
HOUSE_NAME = {'PLA_Lenina_8': ('Lenina 8', 'Lenina 8'), 'PLA_Lenina_7': ('Lenina 7', 'Lenina 7'),
              'PLA_SAT_S_Block': ('Gorbunows Block', "Gorbunov's block"),
              'PLA_Shkolnaya_4': ('Schkolnaja 4', 'Shkolnaya 4'), 'PLA_Shkolnaya_6': ('Schkolnaja 6', 'Shkolnaya 6')}
FLOOR = (('EG', 'ground floor'), ('1. OG', 'floor 1'), ('2. OG', 'floor 2'))
SIDE = (('links', 'left'), ('rechts', 'right'))
# obstacle meshes (tools/asset-pipeline/shooter_props.py); half length across the road, metres
OBSTACLES = {'SM_Obs_Slabs': 2.2, 'SM_Obs_ConcreteFence': 2.0, 'SM_Obs_Truck': 2.6, 'SM_Obs_Bus': 2.9,
             'SM_Obs_Barricade': 1.8, 'SM_Obs_CableDrums': 1.6, 'SM_Obs_Scrap': 1.7}


def residential_households():
    """residential.HOUSES without importing it (it needs Blender's helpers)."""
    import ast
    src = (ROOT / 'tools/asset-pipeline/residential.py').read_text()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], 'id', '') == 'HOUSES')
    return ast.literal_eval(node.value)


def flats(manifest):
    """One entry per furnished flat: household, floor, side and the floor points under its ceiling lights."""
    grid = json.loads((ROOT / 'tools/asset-pipeline/kit_grid.json').read_text())['T5']
    axis, storey = grid['axis'], grid['storey_height']
    houses = residential_households()
    out = []
    for b in manifest:
        if not b.get('room_lights') or b['label'] not in houses:
            continue
        floors, kind, themes = houses[b['label']]
        first = 0 if kind == 'homes' else 1
        (on, oe), (an, ae), _ = b['section_frame']
        levels = sorted({round(p[2], 1) for p in b['room_lights']})
        assert len(levels) == floors, b['label'] + ': lights do not match the furnished floors'
        groups = {}
        for n, e, z in b['room_lights']:
            along = (n - on) * an + (e - oe) * ae
            if 0.3 < along < axis - 0.3:
                continue  # stairwell lamp
            level = levels.index(round(z, 1))
            groups.setdefault((level, 0 if along < 0 else 1), []).append([round(n, 2), round(e, 2), round(z - 0.25, 2)])
        for (level, side), points in sorted(groups.items()):
            theme = GROUND_STORY[b['label']][side] if level < first else themes[(level - first) * 2 + side]
            name = HOUSE_NAME[b['label']]
            out.append({'house': b['label'], 'theme': theme, 'item': THEME_ITEM[theme], 'floor': level, 'side': side,
                        'where': '%s, %s %s' % (name[0], FLOOR[level][0], SIDE[side][0]),
                        'where_en': '%s, %s %s' % (name[1], FLOOR[level][1], SIDE[side][1]),
                        'points': points, 'storey_m': storey})
    return out


def play_area(places):
    keys = [p for p in places if p['name'] in ('Antonina (Lenina 8)', 'Brigadier Orlow (Lenina 7)', 'Wohnung Gorbunow',
                                                'Wohnhaus Schkolnaja 4', 'Wohnhaus Schkolnaja 6', 'Laden',
                                                'Telefonzentrale', 'Elektrizitätswerk')]
    assert len(keys) == 8, 'town map places renamed: update shooter_data.play_area'
    es, ns = [p['east_m'] for p in keys], [p['north_m'] for p in keys]
    return min(es) - MARGIN, max(es) + MARGIN, min(ns) - MARGIN, max(ns) + MARGIN


def inside(e, n, box, pad=0.0):
    return box[0] + pad <= e <= box[1] - pad and box[2] + pad <= n <= box[3] - pad


def road_points(roads, box, step):
    """Points every `step` metres along the roads inside the box: (east, north, direction east, direction north, width)."""
    out = []
    for r in roads:
        carry = 0.0
        for a, b in zip(r['points_m'], r['points_m'][1:]):
            length = math.hypot(b[0] - a[0], b[1] - a[1])
            if length < 0.1:
                continue
            de, dn = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            t = carry
            while t < length:
                e, n = a[0] + de * t, a[1] + dn * t
                if inside(e, n, box):
                    out.append((e, n, de, dn, r['width_m']))
                t += step
            carry = t - length
    return out


def edges(roads, box):
    """Where the roads leave the play area: starts and pick-up points sit just inside."""
    out = []
    for r in roads:
        for a, b in zip(r['points_m'], r['points_m'][1:]):
            if inside(a[0], a[1], box) != inside(b[0], b[1], box):
                lo, hi = 0.0, 1.0  # bisect to the crossing
                for _ in range(30):
                    mid = (lo + hi) / 2
                    p = (a[0] + (b[0] - a[0]) * mid, a[1] + (b[1] - a[1]) * mid)
                    if inside(p[0], p[1], box) == inside(a[0], a[1], box):
                        lo = mid
                    else:
                        hi = mid
                d = (b[0] - a[0], b[1] - a[1]) if inside(a[0], a[1], box) else (a[0] - b[0], a[1] - b[1])
                l = math.hypot(*d)
                e, n = p[0] - d[0] / l * 8, p[1] - d[1] / l * 8  # 8 m inward
                yaw = math.degrees(math.atan2(-d[0], -d[1]))  # facing into the area (UE yaw: 0 = north, 90 = east)
                if all(math.hypot(e - o[1], n - o[0]) > 40 for o in out):
                    out.append([round(n, 2), round(e, 2), round(yaw, 1)])
    return out


def props_clear(e, n, scatter, margin):
    for kind in ('cars', 'heaps', 'fences', 'garages', 'lamps', 'poles', 'benches', 'huts', 'barrels', 'busstops',
                 'playgrounds', 'tanks', 'scrap', 'furniture', 'courtyard_details'):
        for p in scatter.get(kind, []):
            if math.hypot(p[0] - e, p[1] - n) < margin + (4 if kind in ('playgrounds', 'garages', 'tanks') else 0):
                return False
    for line in scatter.get('pipes', []):
        for a, b in zip(line, line[1:]):
            if segment_distance(e, n, a, b) < margin:
                return False
    return True


def doors_clear(e, n, doors, margin):
    return all(math.hypot(e - d[0], n - d[1]) > margin for d in doors)


def obstacles(layout, scatter, box, doors, ground, rnd):
    out = []
    kinds = sorted(OBSTACLES)
    for k, (e, n, de, dn, width) in enumerate(road_points(layout['roads'], box, OBSTACLE_STEP)):
        side = 1 if k % 2 else -1  # alternate sides: a slalom, never a wall across the street
        half = OBSTACLES[kinds[k % len(kinds)]]
        off = width / 2 - half * 0.35
        pe, pn = e - dn * off * side, n + de * off * side
        if (not building_clear(pe, pn, layout['buildings'], 2.0) or not doors_clear(pe, pn, doors, DOOR_CLEAR)
                or not props_clear(pe, pn, scatter, PROP_CLEAR) or not inside(pe, pn, box, 6)
                or any(math.hypot(pe - o['pos'][1], pn - o['pos'][0]) < 9 for o in out)):
            continue
        across = math.degrees(math.atan2(-dn, de))  # obstacle long side across the road ... turned a little
        along = math.degrees(math.atan2(de, dn))
        if half >= 2.6:  # trucks and buses are longer than the street is wide: parked askew along it
            yaw = along + rnd.choice((-1, 1)) * rnd.uniform(12, 30)
        else:
            yaw = (across + rnd.uniform(-25, 25)) if k % 3 else along + rnd.uniform(-10, 10)
        out.append({'mesh': kinds[k % len(kinds)], 'pos': [round(pn, 2), round(pe, 2), round(ground(pe, pn), 2)],
                    'yaw': round(yaw % 360, 1)})
    # courtyards: smaller cover between the blocks, off the streets
    yard = ('SM_Obs_Slabs', 'SM_Obs_ConcreteFence', 'SM_Obs_Barricade', 'SM_Obs_CableDrums', 'SM_Obs_Scrap')
    for n in range(int(box[2]) + 8, int(box[3]) - 8, YARD_STEP):
        for e in range(int(box[0]) + 8, int(box[1]) - 8, YARD_STEP):
            pe, pn = e + rnd.uniform(-5, 5), n + rnd.uniform(-5, 5)
            if (road_clear(pe, pn, layout['roads'], 6) and building_clear(pe, pn, layout['buildings'], 3.0)
                    and doors_clear(pe, pn, doors, DOOR_CLEAR + 2) and props_clear(pe, pn, scatter, PROP_CLEAR)
                    and all(math.hypot(pe - o['pos'][1], pn - o['pos'][0]) > 14 for o in out)):
                out.append({'mesh': rnd.choice(yard), 'pos': [round(pn, 2), round(pe, 2), round(ground(pe, pn), 2)],
                            'yaw': round(rnd.uniform(0, 360), 1)})
    return out


def nearest_road(e, n, roads):
    best = None
    for r in roads:
        for a, b in zip(r['points_m'], r['points_m'][1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            t = max(0, min(1, ((e - a[0]) * dx + (n - a[1]) * dy) / (dx * dx + dy * dy or 1)))
            q = (a[0] + t * dx, a[1] + t * dy)
            d = math.hypot(e - q[0], n - q[1])
            if best is None or d < best[0]:
                best = (d, q, (dx, dy))
    return best


def point(e, n, ground):
    return [round(n, 2), round(e, 2), round(ground(e, n), 2)]


def main():
    layout = json.loads(LAYOUT.read_text())
    manifest = json.loads((ROOT / 'assets/buildings/buildings_manifest.json').read_text())
    scatter = json.loads((ROOT / 'assets/vegetation/scatter.json').read_text())
    town = json.loads((ROOT / 'Content/Kadykchan/Data/TownMap.json').read_text())
    story = {s['id']: s for s in json.loads((ROOT / 'Content/Kadykchan/Data/Story.json').read_text())['steps']}
    ground = TerrainMesh(ROOT / 'assets/terrain/terrain_kadykchan_8km.obj').z
    rnd = random.Random(2011)
    box = play_area(town['places'])
    doors = [(p[0], p[1]) for b in manifest for p in b.get('entrances', [])]
    doors += [tuple(p['door']) for p in town['places'] if 'door' in p]
    flat_list = flats(manifest)
    assert len(flat_list) == 24, 'expected the 24 furnished flats, got %d' % len(flat_list)
    obs = obstacles(layout, scatter, box, doors, ground, rnd)
    starts = edges(layout['roads'], box)
    assert len(starts) >= 3, 'need at least three road exits for start and pick-up'
    for s in starts:
        s.insert(2, round(ground(s[1], s[0]), 2))

    # patrols: from each open house door out to the street and along it; guards wait inside flats
    patrols = []
    for p in town['places']:
        if 'entry' not in p and p['name'] not in ('Laden', 'Telefonzentrale', 'Elektrizitätswerk'):
            continue
        e, n = p['door']
        # 4 m out of the door, away from the building centre: toward the nearest road could cut through the house
        # (Shkolnaya 4/6 and Lenina 8 face their courtyards; first nav check 2026-11-11)
        ie, i_n = p['east_m'] - e, p['north_m'] - n
        il = math.hypot(ie, i_n) or 1
        _, (qe, qn), (dx, dy) = nearest_road(e, n, layout['roads'])
        l = math.hypot(dx, dy) or 1
        route = [(e - ie / il * 4, n - i_n / il * 4), (qe + dx / l * 25, qn + dy / l * 25), (qe - dx / l * 25, qn - dy / l * 25)]
        clamp = lambda v, lo, hi: min(max(v, lo + 4), hi - 4)  # stay inside the round's navigation bounds
        route = [point(clamp(re, box[0], box[1]), clamp(rn, box[2], box[3]), ground) for re, rn in route]
        patrols.append({'name': p['name'], 'route': route})
    # turrets beside the street where the tasks are: the player has to cross their field of fire
    turrets = []
    for name in ('Laden', 'Brigadier Orlow (Lenina 7)', 'Wohnung Gorbunow', 'Elektrizitätswerk'):
        p = next(x for x in town['places'] if x['name'] == name)
        e, n = p['door']
        _, (qe, qn), (dx, dy) = nearest_road(e, n, layout['roads'])
        l = math.hypot(dx, dy) or 1
        for side in (1, -1, 2, -2):  # beside the road, out of the doorway, clear of props
            te, tn = qe - dy / l * 5 * side, qn + dx / l * 5 * side
            if (building_clear(te, tn, layout['buildings'], 1.5) and doors_clear(te, tn, doors, DOOR_CLEAR)
                    and props_clear(te, tn, scatter, 2.0)):
                turrets.append(point(te, tn, ground))
                break
    drones = [point(*xy, ground) for xy in ((300.0, 55.0), (45.0, 25.0), (180.0, -5.0))]

    ats = story['ats']['clues'][0]['pos']
    orlow = story['orlow']['clues'][2]['pos']
    power = story['power']['clues'][2]['pos']
    shop = next(x for x in town['places'] if x['name'] == 'Laden')
    se, sn = shop['door']
    tasks = [
        {'id': 'radio', 'kind': 'fetch_flat', 'item': 'radio',
         'goal': 'Hol das Funkgerät aus der Wohnung {where}.', 'goal_en': 'Fetch the radio from the flat {where}.',
         'done': 'Funkgerät gesichert.', 'done_en': 'Radio secured.'},
        {'id': 'power', 'kind': 'power_on', 'pos': power,
         'goal': 'Starte den Notstrom im Elektrizitätswerk. Achtung: dann laufen auch die Geschütze der Plünderer.',
         'goal_en': 'Start the backup power at the power station. Careful: the looters\' guns run on it too.',
         'done': 'Strom läuft. Die Geschütze sind jetzt scharf; am Schalter kannst du ihn wieder abschalten.',
         'done_en': 'Power is on. The guns are live now; the switch turns it off again.'},
        {'id': 'jammer', 'kind': 'jam', 'pos': ats,
         'goal': 'Bring in der Telefonzentrale den Störsender an.', 'goal_en': 'Fit the jammer at the telephone exchange.',
         'done': 'Störsender läuft: Maschinen und Geschütze sind eine Minute lang blind.',
         'done_en': 'Jammer running: machines and guns are blind for a minute.'},
        {'id': 'workshop', 'kind': 'destroy', 'pos': [round(sn + 4.5, 2), round(se + 6.5, 2), round(ground(se, sn) + 0.9, 2)],
         'mesh': 'SM_Shooter_Workbench',
         'goal': 'Mach die Werkstatt der Plünderer im Laden unbrauchbar.', 'goal_en': 'Wreck the looters\' workshop in the shop.',
         'done': 'Werkstatt zerstört: keine neuen Maschinen mehr.', 'done_en': 'Workshop wrecked: no more new machines.'},
        {'id': 'intel', 'kind': 'fetch', 'pos': orlow, 'item': 'documents',
         'goal': 'In Orlows Wohnung (Lenina 7, EG) liegt die Lagekarte der Plünderer. Hol sie.',
         'goal_en': 'The looters\' situation map is in Orlov\'s flat (Lenina 7, ground floor). Fetch it.',
         'done': 'Lagekarte gesichert: ihre Streifen sind jetzt auf der Karte (K).',
         'done_en': 'Situation map secured: their patrols now show on the map (K).'},
    ]
    data = {'area': {'east': box[:2], 'north': box[2:], 'z': [-20, 60]}, 'tuning': TUNING, 'items': ITEMS,
            'flats': flat_list, 'tasks': tasks, 'starts': starts, 'patrols': patrols, 'turrets': turrets,
            'drones': drones, 'obstacles': obs, 'power_switch': power}
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print('SHOOTER DATA OK flats', len(flat_list), 'obstacles', len(obs), 'starts', len(starts), 'patrols', len(patrols),
          'turrets', len(turrets), 'area', [round(v) for v in box])
    return data


if __name__ == '__main__':
    main()
