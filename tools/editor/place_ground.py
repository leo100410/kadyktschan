"""Re-import the draped road, river and footpath ribbons and give them their materials, without rebuilding the map.

Run after tools/research/lines_to_obj.py and build_materials.py:
  UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/place_ground.py" -unattended
Writes tools/editor/place_ground_report.txt. The meshes are replaced in place, so the placed actors keep them.
"""
import os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/place_ground_report.txt")
WORLD = "/Game/Kadykchan/Maps/Kadykchan_World"
TERRAIN_DIR = "/Game/Kadykchan/Terrain"
# (OBJ, mesh asset, actor label, material instance, collision)
RIBBONS = [("assets/terrain/roads_kadykchan.obj", "SM_Roads_Blockout", "Roads_Blockout", "MI_Road", True),
           ("assets/terrain/rivers_kadykchan.obj", "SM_Rivers_Blockout", "River_Kadykchan_Blockout", "MI_Ground_River", True),
           ("assets/terrain/paths_kadykchan.obj", "SM_Paths", "Paths_Footpaths", "MI_Path", False),
           # real Kolyma ranges on the horizon (tools/research/dem_ring_obj.py)
           ("assets/terrain/terrain_backdrop_60km.obj", "SM_Terrain_Backdrop", "Terrain_Backdrop", "MI_Ground_Forest", False)]

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("GND " + str(m))

def import_obj(filename, name, collision):
    task = unreal.AssetImportTask()
    task.filename, task.destination_path, task.destination_name = os.path.join(ROOT, filename), TERRAIN_DIR, name
    task.automated, task.replace_existing, task.save = True, True, True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    meshes = [m for m in (unreal.load_asset(p) for p in task.imported_object_paths) if isinstance(m, unreal.StaticMesh)]
    if not meshes:
        raise RuntimeError("import produced no StaticMesh for " + filename)
    mesh = meshes[0]
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for section in range(mesh.get_num_sections(0)):
        sms.enable_section_collision(mesh, collision, 0, section)
    nanite = sms.get_nanite_settings(mesh); nanite.set_editor_property("enabled", False)  # thin ribbons, see build_blockout
    sms.set_nanite_settings(mesh, nanite, True)
    if collision:
        mesh.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    else:
        # the importer also builds a simple convex hull; over a town-wide mesh that hull is an invisible floor
        # floating above the lower ground (user report 2026-11-07), so drop all collision
        sms.remove_collisions(mesh)
    return mesh

def main():
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not les.load_level(WORLD):
        raise RuntimeError("could not load " + WORLD)
    actors = {a.get_actor_label(): a for a in eas.get_all_level_actors()}
    for obj, name, label, mi_name, collision in RIBBONS:
        mesh = import_obj(obj, name, collision)
        mi = unreal.load_asset("/Game/Kadykchan/Materials/" + mi_name)
        if mi is None:
            raise RuntimeError("missing %s, run build_materials.py first" % mi_name)
        mesh.set_material(0, mi)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        a = actors.get(label)
        if a is None:  # OBJ import negates y: yaw 90 maps mesh space onto the project axes (see build_blockout)
            a = eas.spawn_actor_from_object(mesh, unreal.Vector(0, 0, 0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))
            a.set_actor_label(label); a.set_folder_path("Terrain"); a.set_editor_property("is_spatially_loaded", False)
            log("placed " + label)
        if not collision:
            a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        log("%s <- %s (%s, collision %s)" % (label, obj, mi_name, collision))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)

try:
    main()
    log("RESULT OK")
except Exception:
    log("RESULT FAILED\n" + traceback.format_exc())
finally:
    open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
    unreal.SystemLibrary.quit_editor()
