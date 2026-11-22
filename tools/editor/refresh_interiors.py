"""Reimport the five furnished buildings and their new fabric/veneer; keep map actors and material references."""
import datetime
import json
from pathlib import Path
import shutil
import traceback

import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
REPORT = ROOT / "tools/editor/refresh_interiors_report.txt"
LABELS = {"PLA_Lenina_8", "PLA_Lenina_7", "PLA_SAT_S_Block", "PLA_OSM_170991713", "PLA_Shkolnaya_8"}
MAT = "/Game/Kadykchan/Materials"
DEST = "/Game/Kadykchan/Buildings/Generated"
lines = []


def main():
    buildings = [b for b in json.loads((ROOT / "assets/buildings/buildings_manifest.json").read_text()) if b["label"] in LABELS]
    assert {b["label"] for b in buildings} == LABELS, "furnished building missing from manifest"
    opts = unreal.FbxImportUI()
    opts.import_materials = opts.import_textures = False
    data = opts.get_editor_property("static_mesh_import_data")
    data.combine_meshes = True
    data.auto_generate_collision = data.generate_lightmap_u_vs = False
    data.normal_import_method = unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS
    tasks, bindings, backup_assets = [], {}, []
    glass_paths = set()

    def task(source, destination, options=None):
        assert source.is_file(), "missing source: " + str(source)
        t = unreal.AssetImportTask()
        t.filename, t.destination_path = str(source), destination
        t.automated = t.replace_existing = t.replace_existing_settings = True
        t.save = False  # validate the import and restore materials before saving
        if options:
            t.options = options
        tasks.append(t)

    from place_buildings import SLOT_MI
    for b in buildings:
        for mesh_name in (b["mesh"], b.get("glass_mesh")):
            if not mesh_name: continue
            path = DEST + "/" + mesh_name
            if mesh_name == b.get("glass_mesh"): glass_paths.add(path)
            mesh = unreal.load_asset(path)
            assert isinstance(mesh, unreal.StaticMesh), "missing placed mesh: " + path
            bindings[path] = {str(s.material_slot_name): s.material_interface for s in mesh.get_editor_property("static_materials")}
            for slot in b["materials"]:
                if slot not in bindings[path]:
                    assert slot in SLOT_MI, "unknown material slot: " + slot
                    bindings[path][slot] = unreal.load_asset(MAT + "/" + SLOT_MI[slot])
            backup_assets.append(path)
            task(ROOT / "assets/buildings" / (mesh_name + ".fbx"), DEST, opts)
    materials = {"MI_Int_Furniture": "Veneer_A", "MI_Int_Sofa": "Fabric_A", "MI_Int_Curtain": "Fabric_A"}
    for name in materials:
        assert unreal.load_asset(MAT + "/" + name), "missing material: " + name
        backup_assets.append(MAT + "/" + name)
    for name in ("Fabric_A", "Veneer_A"):
        for suffix in ("D", "N", "ORM"):
            task(ROOT / "assets/textures" / ("T_%s_%s.png" % (name, suffix)), MAT + "/Textures")
            backup_assets.append(MAT + "/Textures/T_%s_%s" % (name, suffix))
    backup = ROOT / "Saved/InteriorUpdateBackups" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    for asset in backup_assets:
        for suffix in (".uasset", ".ubulk", ".uexp"):
            relative = Path("Content") / (asset.removeprefix("/Game/") + suffix)
            if (ROOT / relative).is_file():
                (backup / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / relative, backup / relative)
    lines.append("Backup: " + str(backup))
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for t in tasks:
        assert t.imported_object_paths, "import failed: " + t.filename
    for path, old in bindings.items():
        mesh = unreal.load_asset(path)
        for i, slot in enumerate(mesh.get_editor_property("static_materials")):
            name = str(slot.material_slot_name)
            assert name in old and old[name], "unmapped material slot: " + name
            mesh.set_material(i, old[name])
        if path not in glass_paths:
            body = mesh.get_editor_property("body_setup")
            assert body, "missing collision body: " + path
            body.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mesh), "could not save mesh: " + path
    for name in ("Fabric_A", "Veneer_A"):
        for suffix in ("D", "N", "ORM"):
            texture = unreal.load_asset(MAT + "/Textures/T_%s_%s" % (name, suffix))
            if suffix != "D":
                texture.srgb = False
                texture.compression_settings = (unreal.TextureCompressionSettings.TC_NORMALMAP if suffix == "N"
                                                else unreal.TextureCompressionSettings.TC_MASKS)
            assert unreal.EditorAssetLibrary.save_loaded_asset(texture), "could not save texture: " + name + suffix
    for name, detail in materials.items():
        mi = unreal.load_asset(MAT + "/" + name)
        for suffix in ("D", "N", "ORM"):
            texture = unreal.load_asset(MAT + "/Textures/T_%s_%s" % (detail, suffix))
            assert texture, "missing texture: " + detail + suffix
            unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(mi, "Detail_" + suffix, texture)
            # UE 5.8's setter always returns false; verify the assigned value instead.
            assert unreal.MaterialEditingLibrary.get_material_instance_texture_parameter_value(mi, "Detail_" + suffix) == texture, "texture assignment failed: " + name + suffix
        unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(mi, "RoughnessOffset", 0.0)
        unreal.MaterialEditingLibrary.update_material_instance(mi)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mi), "could not save material: " + name
    lines.append("RESULT OK")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        lines.append("RESULT FAILED\n" + traceback.format_exc())
    finally:
        REPORT.write_text("\n".join(lines) + "\n")
        unreal.log_warning("\n".join(lines))
        unreal.SystemLibrary.quit_editor()
