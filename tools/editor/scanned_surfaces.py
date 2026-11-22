"""Apply the selected CC0 surfaces without changing the landscape or rebuilding the town."""
from pathlib import Path
import json
import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
DEST = "/Game/Kadykchan/Materials/Scans"


def apply():
    mel = unreal.MaterialEditingLibrary
    configs = [("asphalt_02", ("MI_Road",), "road"),
               ("gravel_road", ("MI_Path",), "ribbon"),
               ("forest_floor", ("MI_VergeScan",), "patch"),
               ("wood_floor", ("MI_Int_FloorBoards",), "floor")]
    tasks = []
    for asset, _, _ in configs:
        for kind in ("diff", "nor_dx", "rough"):
            source = ROOT / "assets/third-party/polyhaven" / (asset + "_" + kind + "_2k.jpg")
            assert source.is_file(), "run tools/research/fetch_surfaces.py first: " + str(source)
            t = unreal.AssetImportTask()
            t.filename, t.destination_path, t.destination_name = str(source), DEST, "T_Scan_" + asset + "_" + kind
            t.automated = t.replace_existing = True
            t.save = False
            tasks.append(t)
    wear_source = ROOT / "assets/textures/T_RoadWear.png"
    assert wear_source.is_file(), "generate road_wear.py first"
    t = unreal.AssetImportTask()
    t.filename, t.destination_path, t.destination_name = str(wear_source), DEST, "T_RoadWear"
    t.automated = t.replace_existing = True
    t.save = False
    tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    for task in tasks:
        assert task.imported_object_paths, "texture import failed: " + task.filename
        tex = unreal.load_asset(task.imported_object_paths[0])
        kind = task.destination_name.rsplit("_", 1)[-1]
        if kind in ("dx", "rough", "RoadWear"):
            tex.set_editor_property("srgb", False)
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP if kind == "dx" else unreal.TextureCompressionSettings.TC_MASKS)
        assert unreal.EditorAssetLibrary.save_loaded_asset(tex), "cannot save " + task.destination_name
    for asset, instances, edge in configs:
        name = "M_Scan_" + asset
        mat = unreal.load_asset(DEST + "/" + name)
        if mat is None:
            mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, DEST, unreal.Material, unreal.MaterialFactoryNew())
        mel.delete_all_material_expressions(mat)
        mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_OPAQUE if edge == "floor" else unreal.BlendMode.BLEND_MASKED)

        def node(cls, **props):
            e = mel.create_material_expression(mat, cls, 0, 0)
            for k, v in props.items():
                e.set_editor_property(k, v)
            return e

        def link(a, out, b, pin):
            assert mel.connect_material_expressions(a, out, b, pin), "invalid material pin: " + pin

        uv = node(unreal.MaterialExpressionTextureCoordinate)
        sample_uv = uv
        if edge != "floor":
            world = node(unreal.MaterialExpressionWorldPosition)
            xy = node(unreal.MaterialExpressionComponentMask, r=True, g=True, b=False, a=False)
            sample_uv = node(unreal.MaterialExpressionMultiply, const_b=1 / 300 if edge == "road" else 0.005)
            link(world, "", xy, ""); link(xy, "", sample_uv, "A")
        samples = {}
        for kind, sampler in (("diff", unreal.MaterialSamplerType.SAMPLERTYPE_COLOR),
                              ("nor_dx", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL),
                              ("rough", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)):
            texture = unreal.load_asset(DEST + "/T_Scan_" + asset + "_" + kind)
            assert texture, "scan texture not imported: " + asset + kind
            sample = node(unreal.MaterialExpressionTextureSample, texture=texture, sampler_type=sampler)
            link(sample_uv, "", sample, "UVs")
            samples[kind] = sample
        color, color_pin = samples["diff"], "RGB"
        rough, rough_pin = samples["rough"], "R"
        if edge == "road":
            wear = node(unreal.MaterialExpressionTextureSample, texture=unreal.load_asset(DEST + "/T_RoadWear"), sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
            link(uv, "", wear, "UVs")
            palette = json.loads((ROOT / "tools/asset-pipeline/palette_2011.json").read_text())
            for channel, key in (("B", "GravelDark"), ("R", "BlackPlastic"), ("G", "Paper")):
                rgb = [int(palette[key][i:i + 2], 16) / 255 for i in (1, 3, 5)]
                rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
                tint = node(unreal.MaterialExpressionConstant3Vector, constant=unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1))
                layer = node(unreal.MaterialExpressionLinearInterpolate)
                link(color, color_pin, layer, "A"); link(tint, "", layer, "B"); link(wear, channel, layer, "Alpha")
                color, color_pin = layer, ""
            worn = node(unreal.MaterialExpressionMax, const_b=0.86)
            link(rough, "R", worn, "A")
            rough, rough_pin = worn, ""
        if edge == "floor":
            faded = node(unreal.MaterialExpressionDesaturation)
            amount = node(unreal.MaterialExpressionConstant, r=0.25)
            link(color, "RGB", faded, ""); link(amount, "", faded, "Fraction")
            color, color_pin = faded, ""
            worn = node(unreal.MaterialExpressionMax, const_b=0.78)
            link(rough, "R", worn, "A")
            rough, rough_pin = worn, ""
        assert mel.connect_material_property(color, color_pin, unreal.MaterialProperty.MP_BASE_COLOR)
        assert mel.connect_material_property(samples["nor_dx"], "RGB", unreal.MaterialProperty.MP_NORMAL)
        assert mel.connect_material_property(rough, rough_pin, unreal.MaterialProperty.MP_ROUGHNESS)
        if edge != "floor":
            twice = node(unreal.MaterialExpressionMultiply, const_b=2.0)
            centred = node(unreal.MaterialExpressionSubtract, const_b=1.0)
            link(uv, "", twice, "A"); link(twice, "", centred, "A")
            if edge in ("ribbon", "road"):
                one = node(unreal.MaterialExpressionComponentMask, r=True, g=False, b=False, a=False)
                link(centred, "", one, "")
                distance = node(unreal.MaterialExpressionAbs)
                link(one, "", distance, "")
            else:
                distance = node(unreal.MaterialExpressionLength)
                link(centred, "", distance, "")
            inside = node(unreal.MaterialExpressionOneMinus)
            strength = node(unreal.MaterialExpressionMultiply, const_b=32.0 if edge == "road" else 5.0)
            noise = node(unreal.MaterialExpressionMultiply, const_b=0.25 if edge == "road" else 0.5)
            mask = node(unreal.MaterialExpressionSubtract)
            link(distance, "", inside, ""); link(inside, "", strength, "A")
            link(wear if edge == "road" else samples["diff"], "A" if edge == "road" else "R", noise, "A")
            link(strength, "", mask, "A"); link(noise, "", mask, "B")
            assert mel.connect_material_property(mask, "", unreal.MaterialProperty.MP_OPACITY_MASK)
        mel.recompile_material(mat)
        assert unreal.EditorAssetLibrary.save_loaded_asset(mat), "cannot save " + name
        for instance in instances:
            path = "/Game/Kadykchan/Materials/" + instance
            mi = unreal.load_asset(path)
            if mi is None:
                mi = unreal.AssetToolsHelpers.get_asset_tools().create_asset(instance, "/Game/Kadykchan/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
            mel.set_material_instance_parent(mi, mat)
            mel.update_material_instance(mi)
            assert unreal.EditorAssetLibrary.save_loaded_asset(mi), "cannot save " + instance
