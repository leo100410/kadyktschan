"""Editor-viewport screenshots from fixed cameras (overview + courtyard), then quit.

Run: UnrealEditor <project>.uproject /Game/Kadykchan/Maps/Kadykchan_World -ExecCmds="py <abs path>/tools/editor/editor_shots.py"
(-ExecutePythonScript quits the editor right after the script returns, which kills the tick callbacks.)
Shots land in production/qa/evidence/. HighResShot needs rendered frames, so work is spread over wall time.
"""
import json, math, os, time
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
# KDK_SHOT_DIR: write somewhere else (iteration shots that are not evidence)
EVIDENCE = os.environ.get("KDK_SHOT_DIR") or os.path.join(ROOT, "production/qa/evidence")
DATE = "2026-11-07"
# (name, location cm, rotation) — project axes +X north, +Y east
SHOTS = [
    ("town-overview", unreal.Vector(-60000, -40000, 35000), unreal.Rotator(roll=0.0, pitch=-28.0, yaw=35.0)),
    ("lenina8-entrance", unreal.Vector(-74, 26047, 780), unreal.Rotator(roll=0.0, pitch=8.0, yaw=145.5)),
    # eye level ~20 m in front of Lenina 8 (the view the user judged "floating" on 2026-11-07)
    ("lenina8-eye", unreal.Vector(1574, 24915, 800), unreal.Rotator(roll=0.0, pitch=4.0, yaw=145.5)),
    # the north-east quarter added from satellite imagery (design/research/data/satellite-additions-2026-11-07.json)
    ("ne-quarter", unreal.Vector(18000, 25000, 9000), unreal.Rotator(roll=0.0, pitch=-22.0, yaw=10.0)),
    # foundations of demolished wooden houses north of the Profilaktoriy (satellite additions)
    ("n-foundations", unreal.Vector(45000, 4400, 2800), unreal.Rotator(roll=0.0, pitch=-20.0, yaw=0.0)),
    # hero buildings (fully dressed exteriors): Lenina 7 from the courtyard, Lenina 8 from above for roof/antennas
    ("lenina7-eye", unreal.Vector(1574, 24915, 800), unreal.Rotator(roll=0.0, pitch=6.0, yaw=-57.5)),
    ("lenina8-roof", unreal.Vector(3000, 23600, 3200), unreal.Rotator(roll=0.0, pitch=-22.0, yaw=150.0)),
    ("lenina-courtyard-wide", unreal.Vector(4500, 18500, 1200), unreal.Rotator(roll=0.0, pitch=2.0, yaw=120.0)),
    ("mira-9storey", unreal.Vector(15000, -4000, 900), unreal.Rotator(roll=0.0, pitch=12.0, yaw=-37.0)),
    ("school-shkolnaya-1", unreal.Vector(8941, 9704, 659), unreal.Rotator(roll=0.0, pitch=6.0, yaw=21.5)),
    ("collapse-50let-7", unreal.Vector(2500, -11000, 900), unreal.Rotator(roll=0.0, pitch=2.0, yaw=55.0)),
    ("lenina8-street-bays", unreal.Vector(-4500, 30500, 1000), unreal.Rotator(roll=0.0, pitch=8.0, yaw=-30.0)),
    ("shkolnaya-street", unreal.Vector(1000, -9000, 800), unreal.Rotator(roll=0.0, pitch=4.0, yaw=60.0)),
]
# interior cameras computed by build_buildings.py (furnished sections)
_manifest = os.path.join(ROOT, "assets/buildings/buildings_manifest.json")
if os.path.exists(_manifest) and os.environ.get("KDK_SHOT_INTERIORS", "1") == "1":
    import json
    for _b in json.load(open(_manifest, encoding="utf-8")):
        for _c in _b.get("cameras", []):
            SHOTS.append((_c["name"], unreal.Vector(_c["north_m"] * 100, _c["east_m"] * 100, _c["z_m"] * 100),
                          unreal.Rotator(roll=0.0, pitch=_c.get("pitch_deg", -5.0), yaw=_c["yaw_deg"])))
_scatter = os.path.join(ROOT, "assets/vegetation/scatter.json")
if os.path.exists(_scatter):
    import json
    for _c in json.load(open(_scatter)).get("cameras", []):
        SHOTS.append((_c["name"], unreal.Vector(_c["north_m"] * 100, _c["east_m"] * 100, _c["z_m"] * 100),
                      unreal.Rotator(roll=0.0, pitch=-4.0, yaw=_c["yaw_deg"])))
if os.path.exists(_scatter):  # the club with its bust, and the boiler-house chimney (props from scatter.json)
    _sc = json.load(open(_scatter))
    for _e, _n, _z, _yaw in _sc.get("busts", [])[:1]:
        _dn, _de = math.cos(math.radians(_yaw)), math.sin(math.radians(_yaw))
        SHOTS.append(("club-front", unreal.Vector((_n - _dn * 14) * 100, (_e - _de * 14) * 100, (_z + 4) * 100),
                      unreal.Rotator(roll=0.0, pitch=-4.0, yaw=_yaw)))
    for _e, _n, _z, _yaw in _sc.get("cars", [])[:1]:
        SHOTS.append(("car-wreck", unreal.Vector((_n - 5) * 100, (_e - 3) * 100, (_z + 2.2) * 100),
                      unreal.Rotator(roll=0.0, pitch=-15.0, yaw=31.0)))
    for _e, _n, _z, _yaw in _sc.get("chimneys", [])[:1]:
        SHOTS.append(("works-chimney", unreal.Vector((_n - 45) * 100, (_e - 30) * 100, (_z + 12) * 100),
                      unreal.Rotator(roll=0.0, pitch=8.0, yaw=33.7)))
# KDK_SHOT_ONLY: comma-separated shot names to take
if os.environ.get("KDK_SHOT_ONLY"):
    SHOTS = [s for s in SHOTS if s[0] in os.environ["KDK_SHOT_ONLY"].split(",")]
WAIT_S, SETTLE_S, WRITE_S = float(os.environ.get("KDK_SHOT_WAIT", "60")), 8.0, 6.0  # seconds: streaming/shaders, view settle, file write
# Slate post-tick fires many times per engine frame while loading, so pace by wall time, not ticks.
# The first callback dt can span the whole editor start-up, so measure from script start instead.
START = time.time()
state = {"t": 0.0, "i": 0, "phase": "wait", "until": WAIT_S}

def tick(_dt):
    state["t"] = time.time() - START
    if state["t"] < state["until"]:
        return
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if state["phase"] == "shoot":
        name = SHOTS[state["i"] - 1][0]
        path = os.path.join(EVIDENCE, "%s-%s.png" % (DATE, name))
        unreal.SystemLibrary.execute_console_command(None, "HighResShot 1600x900 filename=%s" % path)
        unreal.log_warning("SHOT " + path)
        state["phase"], state["until"] = "wait", state["t"] + WRITE_S
    elif state["i"] < len(SHOTS):
        name, loc, rot = SHOTS[state["i"]]
        les.set_level_viewport_camera_info(loc, rot, les.get_active_viewport_config_key())
        les.editor_invalidate_viewports()
        state["i"] += 1
        state["phase"], state["until"] = "shoot", state["t"] + SETTLE_S
    else:
        unreal.SystemLibrary.quit_editor()

unreal.register_slate_post_tick_callback(tick)
