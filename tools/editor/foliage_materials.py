"""Two additional leaf shapes/colours using the existing masked foliage material."""
import json
from pathlib import Path
import unreal


def preserve_leaf_mips(texture):
    """Keep masked leaves from disappearing when the texture selects a small mip."""
    texture.set_editor_property("do_scale_mips_for_alpha_coverage", True)
    texture.set_editor_property("alpha_coverage_thresholds", unreal.Vector4(0,0,0,.333))
    assert texture.get_editor_property("do_scale_mips_for_alpha_coverage")


def apply_leaf_mips():
    for name in ("LeavesBroad_A", "LeavesNeedle_A", "LeavesWillow_A", "LeavesAlder_A"):
        texture = unreal.load_asset("/Game/Kadykchan/Materials/Textures/T_"+name+"_D")
        assert texture, "missing leaf texture: "+name
        preserve_leaf_mips(texture)
        assert unreal.EditorAssetLibrary.save_loaded_asset(texture)


def apply():
    root = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
    folder = "/Game/Kadykchan/Materials"
    parent = unreal.load_asset(folder + "/M_Master_Foliage")
    assert parent, "foliage master missing"
    palette = json.loads((root / "tools/asset-pipeline/palette_2011.json").read_text())
    for kind, texture_name, color in (("Willow", "LeavesWillow_A", "WillowLeaf"), ("Alder", "LeavesAlder_A", "AlderLeaf")):
        source = root / "assets/textures" / ("T_" + texture_name + "_D.png")
        assert source.is_file(), "leaf texture missing: " + str(source)
        task = unreal.AssetImportTask()
        task.filename, task.destination_path = str(source), folder + "/Textures"
        task.automated = task.replace_existing = task.save = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        assert task.imported_object_paths, "leaf texture import failed"
        texture = unreal.load_asset(task.imported_object_paths[0])
        preserve_leaf_mips(texture)
        assert unreal.EditorAssetLibrary.save_loaded_asset(texture)
        name = "MI_Leaves_" + kind
        mi = unreal.load_asset(folder + "/" + name)
        if mi is None:
            mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, folder, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel = unreal.MaterialEditingLibrary
        mel.set_material_instance_parent(mi, parent)
        rgb = [int(palette[color][i:i + 2], 16) / 255 for i in (1, 3, 5)]
        rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
        mel.set_material_instance_vector_parameter_value(mi, "LeafColor", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1))
        mel.set_material_instance_texture_parameter_value(mi, "Card_D", texture)
        assert mel.get_material_instance_texture_parameter_value(mi, "Card_D") == texture, "leaf texture assignment failed"
        mel.set_material_instance_scalar_parameter_value(mi, "Variation", 0.35)
        mel.update_material_instance(mi)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mi), "could not save " + name
