"""Stollen 3: swap in the terrain with the adit cells cut out, add the carved patch and the adit mesh.

Run after tools/research/mine_site.py and tools/asset-pipeline/build_mine.py:
  UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/place_mine.py" -unattended
Writes tools/editor/place_mine_report.txt.
"""
import json, os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/place_mine_report.txt")
WORLD = "/Game/Kadykchan/Maps/Kadykchan_World"
TERRAIN_DIR = "/Game/Kadykchan/Maps/Terrain"
DEST = "/Game/Kadykchan/Mine"
MAT = "/Game/Kadykchan/Materials/"
SLOT_MI = {"Concrete": "MI_T5_Concrete", "Wood": "MI_T5_WindowWood", "Metal": "MI_T5_SheetMetal", "Rock": "MI_Ground_Rock",
           "WoodGrey": "MI_WoodGrey", "BlackPlastic": "MI_Int_BlackPlastic", "Lime": "MI_Facade_Lime", "Enamel": "MI_Int_Enamel",
           "Brick": "MI_Brick", "Paper": "MI_Int_Paper"}
# story pictures (story_textures.swift): slot Pic_<Name> -> MI_Pic_<Name> (build_materials.build_pictures)
SLOT_MI.update({"Pic_" + f[6:-6] + turn: "MI_Pic_" + f[6:-6] for f in os.listdir(os.path.join(ROOT, "assets/textures"))
                if f.startswith("T_Pic_") and f.endswith("_D.png") for turn in ("", "@90", "@180", "@270", "_90", "_180", "_270")})  # FBX turns @ into _

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("MINE " + str(m))


def import_terrain(filename, name):
    """Same settings as build_blockout.import_obj: walkable complex collision, no Nanite, tundra ground."""
    task = unreal.AssetImportTask()
    task.filename, task.destination_path, task.destination_name = os.path.join(ROOT, filename), TERRAIN_DIR, name
    task.automated, task.replace_existing, task.save = True, True, True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh = [m for m in (unreal.load_asset(p) for p in task.imported_object_paths) if isinstance(m, unreal.StaticMesh)][0]
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for section in range(mesh.get_num_sections(0)):
        sms.enable_section_collision(mesh, True, 0, section)
    nanite = sms.get_nanite_settings(mesh); nanite.set_editor_property("enabled", False)
    sms.set_nanite_settings(mesh, nanite, True)
    mesh.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    for i in range(len(mesh.get_editor_property("static_materials"))):
        mesh.set_material(i, unreal.load_asset(MAT + "MI_Ground_Tundra"))
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    return mesh


def main():
    man = json.load(open(os.path.join(ROOT, "assets/mine/mine_manifest.json")))
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not les.load_level(WORLD):
        raise RuntimeError("could not load " + WORLD)
    # the big terrain keeps its asset (and actor); only its triangles around the portal are gone
    import_terrain("assets/terrain/terrain_kadykchan_8km_cut.obj", "SM_Terrain_Blockout")
    patch = import_terrain("assets/mine/terrain_adit_patch.obj", "SM_Terrain_AditPatch")
    opts = unreal.FbxImportUI()
    opts.set_editor_property("import_materials", False)
    opts.set_editor_property("import_textures", False)
    smd = opts.get_editor_property("static_mesh_import_data")
    smd.set_editor_property("combine_meshes", True)
    smd.set_editor_property("auto_generate_collision", False)
    smd.set_editor_property("generate_lightmap_u_vs", False)
    t = unreal.AssetImportTask()
    t.filename, t.destination_path = os.path.join(ROOT, "assets/mine", man["mesh"] + ".fbx"), DEST
    t.automated, t.replace_existing, t.save, t.options = True, True, True, opts
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([t])
    for a in unreal.EditorAssetLibrary.list_assets(DEST, recursive=False):
        if isinstance(unreal.load_asset(a), unreal.Material):
            unreal.EditorAssetLibrary.delete_asset(a)
    mesh = unreal.load_asset("%s/%s" % (DEST, man["mesh"]))
    for i, sm in enumerate(mesh.get_editor_property("static_materials")):
        mesh.set_material(i, unreal.load_asset(MAT + SLOT_MI[str(sm.get_editor_property("material_slot_name"))]))
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    nanite = sms.get_nanite_settings(mesh); nanite.set_editor_property("enabled", False)
    sms.set_nanite_settings(mesh, nanite, True)
    mesh.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in ("Terrain_AditPatch", "Mine_Adit"):
            eas.destroy_actor(a)
    p = eas.spawn_actor_from_object(patch, unreal.Vector(0, 0, 0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0))  # OBJ: yaw 90
    p.set_actor_label("Terrain_AditPatch"); p.set_folder_path("Terrain"); p.set_editor_property("is_spatially_loaded", False)
    m = eas.spawn_actor_from_object(mesh, unreal.Vector(man["north_m"] * 100, man["east_m"] * 100, 0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    m.set_actor_label("Mine_Adit"); m.set_folder_path("Mine"); m.set_editor_property("is_spatially_loaded", False)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("terrain cut + patch, adit at %.1f N %.1f E (%d quads)" % (man["north_m"], man["east_m"], man["quads"]))


try:
    main()
    log("RESULT OK")
except Exception:
    log("RESULT FAILED\n" + traceback.format_exc())
finally:
    open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
    unreal.SystemLibrary.quit_editor()
