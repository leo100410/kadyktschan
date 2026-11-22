"""Import the vegetation: grass and prop cell meshes (one actor per 600 m cell) and the instanced tree prototypes
(three LODs each, drawn by one AKdkFoliageField from Content/Kadykchan/Data/Foliage/*.txt).

Run after build_vegetation.py, build_materials.py and build_blockout.py:
  UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/place_vegetation.py" -unattended
Writes tools/editor/place_vegetation_report.txt.
"""
import json, os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/place_vegetation_report.txt")
SRC = os.path.join(ROOT, "assets/vegetation")
_M = json.load(open(os.path.join(SRC, "veg_manifest.json")))
MANIFEST, LAYERS = _M["cells"], _M["layers"]
WORLD = "/Game/Kadykchan/Maps/Kadykchan_World"
DEST = "/Game/Kadykchan/Vegetation/Generated"
SLOT_MI = {"Bark_Birch": "MI_Bark_Birch", "Bark_Larch": "MI_Bark_Larch", "Leaves_Birch": "MI_Leaves_Birch",
           "Leaves_Larch": "MI_Leaves_Larch", "Leaves_Shrub": "MI_Leaves_Shrub", "Grass": "MI_Grass",
           "Leaves_Willow": "MI_Leaves_Willow", "Leaves_Alder": "MI_Leaves_Alder",
           # street furniture in the SM_Props_* cells
           "Metal": "MI_T5_SheetMetal", "Concrete": "MI_T5_Concrete", "Lime": "MI_Facade_Lime",  # outdoor props weather like facades
           "Furniture": "MI_Int_Furniture", "Wood": "MI_T5_WindowWood",
           "Brick": "MI_Brick", "WoodGrey": "MI_WoodGrey", "Enamel": "MI_Int_Enamel", "BlackPlastic": "MI_Int_BlackPlastic"}

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("VEG " + str(m))

def main(only_foliage=False):
    cells = [] if only_foliage else MANIFEST
    mis = {k: unreal.load_asset("/Game/Kadykchan/Materials/" + v) for k, v in SLOT_MI.items()}
    if any(v is None for v in mis.values()):
        raise RuntimeError("vegetation materials missing, run build_materials.py first")
    opts = unreal.FbxImportUI()
    opts.set_editor_property("import_materials", False)
    opts.set_editor_property("import_textures", False)
    smd = opts.get_editor_property("static_mesh_import_data")
    smd.set_editor_property("combine_meshes", True)
    smd.set_editor_property("auto_generate_collision", False)
    smd.set_editor_property("generate_lightmap_u_vs", False)
    tasks = []
    for name in [m["mesh"] for m in cells] + [l["lods"][0] for l in LAYERS]:
        t = unreal.AssetImportTask()
        t.filename, t.destination_path = os.path.join(SRC, name + ".fbx"), DEST
        t.automated, t.replace_existing, t.save, t.options = True, True, True, opts
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    meshes = {}
    for m in cells:
        mesh = unreal.load_asset("%s/%s" % (DEST, m["mesh"]))
        for i, sm in enumerate(mesh.get_editor_property("static_materials")):
            mesh.set_material(i, mis[str(sm.get_editor_property("material_slot_name"))])
        nanite = sms.get_nanite_settings(mesh)
        nanite.set_editor_property("enabled", False)  # art bible 8.7: Nanite foliage unverified in 5.8 (props: see buildings)
        sms.set_nanite_settings(mesh, nanite, True)
        sms.remove_collisions(mesh)  # art bible 8.8: vegetation without collision (trunks later)
        if m.get("props"):  # pipes, tanks, garages, rubble block the player
            mesh.get_editor_property("body_setup").set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        meshes[m["mesh"]] = mesh

    # tree prototypes: LOD0 imported above; LOD1/2 are our own reduced card sets (fewer, bigger cards)
    protos = {}
    for l in LAYERS:
        mesh = unreal.load_asset("%s/%s" % (DEST, l["lods"][0]))
        opts_r = unreal.EditorScriptingMeshReductionOptions()
        opts_r.set_editor_property("auto_compute_lod_screen_size", False)
        opts_r.set_editor_property("reduction_settings", [unreal.EditorScriptingMeshReductionSettings(1.0, 1.0),
                                                          unreal.EditorScriptingMeshReductionSettings(0.5, 0.12),
                                                          unreal.EditorScriptingMeshReductionSettings(0.2, 0.035)])
        sms.set_lods(mesh, opts_r)
        import_lod = getattr(sms, "import_lod", None) or getattr(unreal.EditorStaticMeshLibrary, "import_lod", None)
        for lod in (1, 2):
            if import_lod is None or import_lod(mesh, lod, os.path.join(SRC, l["lods"][lod] + ".fbx")) < 0:
                log("LOD%d import failed for %s, keeping the reduced LOD" % (lod, l["lods"][0]))
        for i, sm in enumerate(mesh.get_editor_property("static_materials")):
            mesh.set_material(i, mis[str(sm.get_editor_property("material_slot_name"))])
        nanite = sms.get_nanite_settings(mesh)
        nanite.set_editor_property("enabled", False)
        sms.set_nanite_settings(mesh, nanite, True)
        sms.remove_collisions(mesh)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        protos[l["lods"][0]] = mesh

    les = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    eas = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not les.load_level(WORLD):
        raise RuntimeError("could not load " + WORLD)
    for a in eas.get_all_level_actors():
        if a.get_actor_label().startswith("Foliage_") or (not only_foliage and a.get_actor_label().startswith(("Veg_", "Props_"))):
            eas.destroy_actor(a)
    for m in cells:
        a = eas.spawn_actor_from_object(meshes[m["mesh"]], unreal.Vector(m["north_m"] * 100, m["east_m"] * 100, 0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
        a.set_actor_label(m["mesh"].replace("SM_", ""))
        a.set_folder_path("Props" if m.get("props") else "Vegetation")
        if not m.get("props"):
            a.static_mesh_component.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
        a.set_editor_property("is_spatially_loaded", False)  # shortcut: like the blockout; HLOD later
    field = eas.spawn_actor_from_class(unreal.KdkFoliageField, unreal.Vector(0, 0, 0), unreal.Rotator(roll=0.0, pitch=0.0, yaw=0.0))
    layers = []
    for l in LAYERS:
        fl = unreal.KdkFoliageLayer()
        fl.set_editor_property("mesh", protos[l["lods"][0]])
        fl.set_editor_property("data_file", l["data"])
        fl.set_editor_property("cull_end", l["cull_cm"])
        fl.set_editor_property("cast_shadow", l["shadow"])
        layers.append(fl)
    field.set_editor_property("foliage_layers", layers)
    field.set_actor_label("Foliage_Field")
    field.set_folder_path("Vegetation")
    field.set_editor_property("is_spatially_loaded", False)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
    log("placed %d vegetation cells (%d quads), %d instanced layers (%d instances)" % (len(cells), sum(m["quads"] for m in cells),
        len(LAYERS), sum(l["count"] for l in LAYERS)))

if __name__ == "__main__":
    try:
        main()
        log("RESULT OK")
    except Exception:
        log("RESULT FAILED\n" + traceback.format_exc())
    finally:
        open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
        unreal.SystemLibrary.quit_editor()
