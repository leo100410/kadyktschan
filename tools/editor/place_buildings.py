"""Import the assembled building meshes and put them into the world in place of the blockout boxes.

Run after tools/asset-pipeline/build_buildings.py, build_materials.py and build_blockout.py
(the blockout script recreates the world map with boxes; this script replaces them):
  UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/place_buildings.py" -unattended
Writes tools/editor/place_buildings_report.txt.
"""
import json, os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/place_buildings_report.txt")
SRC = os.path.join(ROOT, "assets/buildings")
MANIFEST = json.load(open(os.path.join(SRC, "buildings_manifest.json"), encoding="utf-8"))
WORLD = "/Game/Kadykchan/Maps/Kadykchan_World"
DEST = "/Game/Kadykchan/Buildings/Generated"
MAT_DIR = "/Game/Kadykchan/Materials"
SLOT_MI = {"Facade_Mint": "MI_T5_PaintMint", "Facade_Rose": "MI_T5_PaintRose", "Facade_Lime": "MI_Facade_Lime",
           "Facade_Concrete": "MI_Facade_Concrete", "Wood": "MI_T5_WindowWood", "Metal": "MI_T5_SheetMetal",
           "Glass": "MI_T5_Glass", "Concrete": "MI_T5_Concrete", "Interior": "MI_T5_InteriorLime",
           # furnished interiors (tools/asset-pipeline/interiors.py)
           "Lime": "MI_T5_InteriorLime", "Paint_Mint": "MI_T5_PaintMint", "Paint_OilBlue": "MI_Int_OilBlue",
           "Wallpaper_Rose": "MI_Int_WallpaperRose", "Wallpaper_Green": "MI_Int_WallpaperGreen", "FloorBoards": "MI_Int_FloorBoards",
           "Linoleum": "MI_Int_Linoleum", "Furniture": "MI_Int_Furniture", "Carpet": "MI_Int_Carpet", "Sofa": "MI_Int_Sofa",
           "Radiator": "MI_Int_Radiator", "BlackPlastic": "MI_Int_BlackPlastic", "Screen": "MI_Int_Screen", "Paper": "MI_Int_Paper",
           "WoodGrey": "MI_WoodGrey", "Enamel": "MI_Int_Enamel", "Stencil": "MI_T5_Stencil",
           # gable mosaic (tools/asset-pipeline/murals.py)
           "Mural_Red": "MI_Mural_Red", "Mural_Brown": "MI_Mural_Brown", "Mural_White": "MI_Facade_Lime", "Mural_Skin": "MI_T5_PaintRose",
           # Kulturhaus (tools/asset-pipeline/kulturhaus.py)
           "Facade_Ochre": "MI_Facade_Ochre", "Facade_Teal": "MI_Facade_Teal",
           "Crack": "MI_Decal_Crack", "Spall": "MI_Decal_Spall", "Rust": "MI_Decal_Rust",
           "CurtainRed": "MI_Int_Curtain", "Glass_StainBlue": "MI_Glass_StainBlue", "Glass_StainRed": "MI_Glass_StainRed",
           "Glass_StainCyan": "MI_Glass_StainCyan", "Parapet": "MI_Facade_Lime", "Roof": "MI_Roof_Slate", "Fin": "MI_Facade_Lime"}
# story pictures (story_textures.swift): slot Pic_<Name> -> MI_Pic_<Name> (build_materials.build_pictures)
SLOT_MI.update({"Pic_" + f[6:-6] + turn: "MI_Pic_" + f[6:-6] for f in os.listdir(os.path.join(ROOT, "assets/textures"))
                if f.startswith("T_Pic_") and f.endswith("_D.png") for turn in ("", "@90", "@180", "@270", "_90", "_180", "_270")})  # FBX turns @ into _

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("BLD " + str(m))

def main():
    mis = {k: unreal.load_asset("%s/%s" % (MAT_DIR, v)) for k, v in SLOT_MI.items()}
    missing = [k for k, v in mis.items() if v is None]
    if missing:
        raise RuntimeError("material instances missing, run build_materials.py first: %s" % missing)
    # start clean: a re-import with replace_existing keeps the old material slots (a stale Glass slot made Nanite
    # fall back to the decimated mesh), so remove the placed buildings and their assets first
    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not les.load_level(WORLD):
        raise RuntimeError("could not load " + WORLD)
    labels = {b["label"] for b in MANIFEST} | {b["label"] + "_Glass" for b in MANIFEST}
    for a in eas.get_all_level_actors():
        if a.get_actor_label() in labels:
            eas.destroy_actor(a)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    if unreal.EditorAssetLibrary.does_directory_exist(DEST):
        unreal.EditorAssetLibrary.delete_directory(DEST)

    opts = unreal.FbxImportUI()
    opts.set_editor_property("import_materials", False)
    opts.set_editor_property("import_textures", False)
    smd = opts.get_editor_property("static_mesh_import_data")
    smd.set_editor_property("combine_meshes", True)
    smd.set_editor_property("auto_generate_collision", False)
    smd.set_editor_property("generate_lightmap_u_vs", False)
    smd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
    tasks = []
    for b in MANIFEST:
        for name in filter(None, (b["mesh"], b.get("glass_mesh"))):
            t = unreal.AssetImportTask()
            t.filename, t.destination_path = os.path.join(SRC, name + ".fbx"), DEST
            t.automated, t.replace_existing, t.save, t.options = True, True, True, opts
            tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for a in unreal.EditorAssetLibrary.list_assets(DEST, recursive=False):
        if isinstance(unreal.load_asset(a), unreal.Material):
            unreal.EditorAssetLibrary.delete_asset(a)  # importer placeholders; slots use project instances

    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    meshes = {}
    for b in MANIFEST:
        mesh = unreal.load_asset("%s/%s" % (DEST, b["mesh"]))
        if not isinstance(mesh, unreal.StaticMesh):
            raise RuntimeError("did not import: " + b["mesh"])
        for i, sm in enumerate(mesh.get_editor_property("static_materials")):
            slot = str(sm.get_editor_property("material_slot_name"))
            if slot not in mis:
                raise RuntimeError("no material instance mapped for slot %s in %s" % (slot, b["mesh"]))
            mesh.set_material(i, mis[slot])
        # shortcut: Nanite off for buildings - on this Mac (UE 5.8.4, macOS 27, Nanite Beta) Nanite renders thin parts
        # (chairs, window frames, wall-unit doors) as slivers even with a clean slot list and a full-detail fallback.
        # Buildings are 15-80 k triangles, so this costs little; re-test Nanite on the Windows RTX reference.
        nanite = sms.get_nanite_settings(mesh)
        nanite.set_editor_property("enabled", False)
        sms.set_nanite_settings(mesh, nanite, True)
        # shortcut: complex-as-simple collision on the merged mesh; switch to kit UCX boxes when interiors open up
        mesh.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        meshes[b["label"]] = mesh
        if b.get("glass_mesh"):
            g = unreal.load_asset("%s/%s" % (DEST, b["glass_mesh"]))
            for i, sm in enumerate(g.get_editor_property("static_materials")):
                g.set_material(i, mis.get(str(sm.get_editor_property("material_slot_name")), mis["Glass"]))
            gn = sms.get_nanite_settings(g)
            gn.set_editor_property("enabled", False)
            sms.set_nanite_settings(g, gn, True)
            sms.remove_collisions(g)
            unreal.EditorAssetLibrary.save_loaded_asset(g)
            meshes[b["label"] + "_Glass"] = g
    log("imported %d building meshes" % len(meshes))

    for a in eas.get_all_level_actors():
        if a.get_actor_label() in meshes:
            eas.destroy_actor(a)  # blockout boxes (buildings were removed above)
    for b in MANIFEST:
        loc = unreal.Vector(b["north_m"] * 100, b["east_m"] * 100, b["ground_m"] * 100 - 10)
        a = eas.spawn_actor_from_object(meshes[b["label"]], loc, unreal.Rotator(roll=0.0, pitch=0.0, yaw=b["yaw_deg"]))
        a.set_actor_label(b["label"])
        a.set_folder_path(b["folder"])
        # shortcut: always loaded like the rest of the blockout (see build_blockout.py); HLOD/streaming later
        a.set_editor_property("is_spatially_loaded", False)
        if b["label"] + "_Glass" in meshes:
            g = eas.spawn_actor_from_object(meshes[b["label"] + "_Glass"], loc, unreal.Rotator(roll=0.0, pitch=0.0, yaw=b["yaw_deg"]))
            g.set_actor_label(b["label"] + "_Glass")
            g.set_folder_path(b["folder"])
            g.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
            g.set_editor_property("is_spatially_loaded", False)
    # player start in front of the middle entrance of ул. Ленина 8 (vertical-slice block). Respawned rather than
    # moved: a moved World Partition actor was not marked dirty and the old position stayed on disk.
    b8 = [b for b in MANIFEST if b["label"] == "PLA_Lenina_8"][0]
    if b8["entrances"]:
        n, e, yaw = b8["entrances"][len(b8["entrances"]) // 2]
        for a in eas.get_all_level_actors():
            if isinstance(a, unreal.PlayerStart):
                eas.destroy_actor(a)
        ps = eas.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(n * 100, e * 100, b8["ground_m"] * 100 + 150),
                                        unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
        ps.set_actor_label("PlayerStart_Lenina8_Entrance")
        ps.set_folder_path("Gameplay")
        ps.set_editor_property("is_spatially_loaded", False)
        log("player start -> entrance of PLA_Lenina_8 at (%.1f N, %.1f E) yaw %.0f" % (n, e, yaw))
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("placed %d buildings" % len(MANIFEST))

    # remove tonight's superseded single-building experiment (level instance + loose kit meshes)
    for old in ("/Game/Kadykchan/Buildings/PLA/LI_Lenina_8", "/Game/Kadykchan/Buildings/T5"):
        if unreal.EditorAssetLibrary.does_asset_exist(old):
            unreal.EditorAssetLibrary.delete_asset(old)
        elif unreal.EditorAssetLibrary.does_directory_exist(old):
            unreal.EditorAssetLibrary.delete_directory(old)

if __name__ == "__main__":
    try:
        main()
        log("RESULT OK")
    except Exception:
        log("RESULT FAILED\n" + traceback.format_exc())
    finally:
        open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
        unreal.SystemLibrary.quit_editor()
