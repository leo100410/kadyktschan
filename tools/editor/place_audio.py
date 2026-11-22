"""Import the ambience loops and place them: wind everywhere (2D), drips in the furnished interiors (3D).

Run after gen_audio.py and place_buildings.py:
  UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/place_audio.py" -unattended
Writes tools/editor/place_audio_report.txt. Shortcut: plain looping SoundWaves in AmbientSound actors;
briefing V1/V7 asks for MetaSounds - move these into a MetaSound source once that graph is scripted.
"""
import json, os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/place_audio_report.txt")
SRC = os.path.join(ROOT, "assets/audio")
DEST = "/Game/Kadykchan/Audio"
WORLD = "/Game/Kadykchan/Maps/Kadykchan_World"
MANIFEST = json.load(open(os.path.join(ROOT, "assets/buildings/buildings_manifest.json"), encoding="utf-8"))
DRIP_CAMERAS = ("lenina8-stairwell", "lenina8-flatB-room", "kulturhaus-back")

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("AUD " + str(m))

def main():
    tasks = []
    for f in ("A_Wind_Loop.wav", "A_Drips_Loop.wav", "A_Creaks_Loop.wav"):
        t = unreal.AssetImportTask()
        t.filename, t.destination_path = os.path.join(SRC, f), DEST
        t.automated, t.replace_existing, t.save = True, True, True
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    sounds = {}
    for name in ("A_Wind_Loop", "A_Drips_Loop", "A_Creaks_Loop"):
        snd = unreal.load_asset("%s/%s" % (DEST, name))
        if not isinstance(snd, unreal.SoundWave):
            raise RuntimeError("did not import as SoundWave: " + name)
        snd.set_editor_property("looping", True)
        unreal.EditorAssetLibrary.save_loaded_asset(snd)
        sounds[name] = snd
        log("%s: %.1f s" % (name, snd.get_editor_property("duration")))

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not les.load_level(WORLD):
        raise RuntimeError("could not load " + WORLD)
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("Ambience_"):
            eas.destroy_actor(a)

    def ambient(label, sound, loc, volume, spatial, falloff_cm=0.0):
        a = eas.spawn_actor_from_class(unreal.AmbientSound, loc)
        a.set_actor_label(label)
        a.set_folder_path("Audio")
        a.set_editor_property("is_spatially_loaded", False)
        c = a.get_component_by_class(unreal.AudioComponent)
        c.set_editor_property("sound", sound)
        c.set_editor_property("volume_multiplier", volume)
        c.set_editor_property("allow_spatialization", spatial)
        if spatial:
            c.set_editor_property("override_attenuation", True)
            att = c.get_editor_property("attenuation_overrides")
            att.set_editor_property("falloff_distance", falloff_cm)
            c.set_editor_property("attenuation_overrides", att)
        return a

    ambient("Ambience_Wind", sounds["A_Wind_Loop"], unreal.Vector(0, 0, 1000), 0.7, False)
    cams = {c["name"]: c for b in MANIFEST for c in b.get("cameras", [])}
    for name in DRIP_CAMERAS:
        c = cams.get(name)
        if c:
            ambient("Ambience_Drips_" + name, sounds["A_Drips_Loop"],
                    unreal.Vector(c["north_m"] * 100, c["east_m"] * 100, c["z_m"] * 100 + 60), 0.9, True, 900.0)
    # loose metal and doors working in the wind, from the more decayed blocks (creepy without horror cues)
    import random
    rr = random.Random(1996)
    decayed = [b for b in MANIFEST if b.get("decay", 0) >= 2]
    for b in rr.sample(decayed, min(len(decayed), 12)):
        ambient("Ambience_Creaks_" + b["label"], sounds["A_Creaks_Loop"],
                unreal.Vector(b["north_m"] * 100, b["east_m"] * 100, b["ground_m"] * 100 + 600), 0.8, True, 3500.0)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("placed wind + %d drip emitters" % sum(1 for n in DRIP_CAMERAS if n in cams))

try:
    main()
    log("RESULT OK")
except Exception:
    log("RESULT FAILED\n" + traceback.format_exc())
finally:
    open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
    unreal.SystemLibrary.quit_editor()
