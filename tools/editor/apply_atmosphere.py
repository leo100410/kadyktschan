"""Overcast mood (design/art/atmosphere-target.md): pale covered sky, little direct sun, cool muted colours, haze in
which distant blocks fade but stay readable. Retunes the light actors build_blockout.py placed; run after it:
  UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/apply_atmosphere.py" -unattended
Writes tools/editor/apply_atmosphere_report.txt. All values live in the tables below.
"""
import os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/apply_atmosphere_report.txt")
WORLD = "/Game/Kadykchan/Maps/Kadykchan_World"
C = unreal.LinearColor

# partly cloudy late-summer light (user photos 2026-11-07 replace the first, fully overcast target)
SUN = {"intensity": 5.0, "light_source_angle": 4.0, "atmosphere_sun_disk_color_scale": C(1, 1, 1, 1)}
# the covered sky carries most of the light, so the scene stays readable
SKY_LIGHT = {"intensity": 1.6}
# less Rayleigh (blue), more Mie (white haze): a pale grey-white sky instead of summer blue
ATMOSPHERE = {"rayleigh_scattering_scale": 0.026, "mie_scattering_scale": 0.006, "mie_absorption_scale": 0.0008,
              "mie_anisotropy": 0.6, "multi_scattering_factor": 1.0}
# haze: near blocks clear, ~1 km away only silhouettes, never a white wall (fog_max_opacity < 1)
FOG = {"fog_density": 0.012, "fog_height_falloff": 0.1, "start_distance": 2500.0, "fog_max_opacity": 0.68,
       "fog_inscattering_luminance": C(0.45, 0.52, 0.62, 1), "directional_inscattering_luminance": C(0, 0, 0, 1)}
# cool, muted grade, a little brighter than build_blockout's -1 bias so the pale sky does not turn leaden
POST = {"color_saturation": unreal.Vector4(0.84, 0.84, 0.84, 1), "color_contrast": unreal.Vector4(1.04, 1.04, 1.04, 1),
        "white_temp": 6700.0, "vignette_intensity": 0.42, "film_grain_intensity": 0.18, "auto_exposure_bias": -0.4}
# sky cycle: cooler light at both ends; the elevation path (day -> white night) is unchanged
SKY_CYCLE = {"start_temperature_k": 7000.0, "end_temperature_k": 7400.0}

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("ATM " + str(m))

def apply(obj, props, what):
    for k, v in props.items():
        try:
            obj.set_editor_property(k, v)
        except Exception as e:
            raise RuntimeError("%s.%s: %s" % (what, k, e))
    log("%s: %s" % (what, ", ".join(sorted(props))))

def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not les.load_level(WORLD):
        raise RuntimeError("could not load " + WORLD)
    found = set()
    for a in eas.get_all_level_actors():
        if isinstance(a, unreal.DirectionalLight):
            apply(a.light_component, SUN, "sun"); found.add("sun")
        elif isinstance(a, unreal.SkyLight):
            apply(a.light_component, SKY_LIGHT, "skylight"); found.add("skylight")
        elif isinstance(a, unreal.SkyAtmosphere):
            apply(a.get_component_by_class(unreal.SkyAtmosphereComponent), ATMOSPHERE, "atmosphere"); found.add("atmosphere")
        elif isinstance(a, unreal.ExponentialHeightFog):
            apply(a.get_component_by_class(unreal.ExponentialHeightFogComponent), FOG, "fog"); found.add("fog")
        elif isinstance(a, unreal.VolumetricCloud):
            found.add("cloud")
        elif isinstance(a, unreal.PostProcessVolume):
            pps = a.get_editor_property("settings")
            for k, v in POST.items():
                pps.set_editor_property("override_" + k, True)
                pps.set_editor_property(k, v)
            a.set_editor_property("settings", pps); found.add("post")
            log("post: " + ", ".join(sorted(POST)))
    if "cloud" not in found:  # broken cumulus with blue gaps, as in the user's photos of Kadykchan (2026-11-07)
        c = eas.spawn_actor_from_class(unreal.VolumetricCloud, unreal.Vector(0, 0, 0))
        c.set_actor_label("VolumetricCloud"); c.set_folder_path("Lighting"); c.set_editor_property("is_spatially_loaded", False)
        log("added volumetric cloud")
    missing = {"sun", "skylight", "atmosphere", "fog", "post"} - found
    if missing:
        raise RuntimeError("actors missing (run build_blockout.py first): %s" % sorted(missing))
    da = unreal.load_asset("/Game/Kadykchan/Gameplay/DA_SkyCycle")
    params = da.get_editor_property("params")
    for k, v in SKY_CYCLE.items():
        params.set_editor_property(k, v)
    da.set_editor_property("params", params)
    unreal.EditorAssetLibrary.save_loaded_asset(da)
    log("sky cycle: " + ", ".join("%s=%s" % kv for kv in SKY_CYCLE.items()))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

try:
    main()
    log("RESULT OK")
except Exception:
    log("RESULT FAILED\n" + traceback.format_exc())
finally:
    open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
    unreal.SystemLibrary.quit_editor()
