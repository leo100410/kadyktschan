"""Textures, master material and material instances for the building kit (art bible 4.1, 8.6).

Run: UnrealEditor <project>.uproject -ExecutePythonScript="tools/editor/build_materials.py" -unattended
Writes tools/editor/build_materials_report.txt. Run again after changing textures or the palette.
"""
import json, os, traceback
import unreal

ROOT = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir())
REPORT = os.path.join(ROOT, "tools/editor/build_materials_report.txt")
PALETTE = json.load(open(os.path.join(ROOT, "tools/asset-pipeline/palette_2011.json")))
TEX_SRC = os.path.join(ROOT, "assets/textures")
TEX_DIR = "/Game/Kadykchan/Materials/Textures"
MAT_DIR = "/Game/Kadykchan/Materials"

log_lines = []
def log(m):
    log_lines.append(str(m)); unreal.log_warning("MAT " + str(m))

def srgb_to_linear(hexstr):
    c = [int(hexstr[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    return [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]

def import_files(files, dest, options=None):
    tasks = []
    for f in files:
        t = unreal.AssetImportTask()
        t.filename, t.destination_path = f, dest
        t.automated, t.replace_existing, t.save = True, True, True
        if options is not None:
            t.options = options
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)
    return [p for t in tasks for p in t.imported_object_paths]

def connect(a, out_pin, b, in_pin):
    if not unreal.MaterialEditingLibrary.connect_material_expressions(a, out_pin, b, in_pin):
        raise RuntimeError("could not connect %s.%s -> %s.%s" % (a.get_class().get_name(), out_pin, b.get_class().get_name(), in_pin))

def get_or_create_mi(name, parent):
    """Update an existing instance in place (keeps references from meshes and the map) or create it."""
    path = "%s/%s" % (MAT_DIR, name)
    inst = unreal.load_asset(path) if unreal.EditorAssetLibrary.does_asset_exist(path) else None
    if inst is None:
        inst = unreal.AssetToolsHelpers.get_asset_tools().create_asset(name, MAT_DIR, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
    unreal.MaterialEditingLibrary.set_material_instance_parent(inst, parent)
    return inst

# ---------------------------------------------------------------- textures
def import_textures():
    files = sorted(os.path.join(TEX_SRC, f) for f in os.listdir(TEX_SRC) if f.endswith(".png"))
    import_files(files, TEX_DIR)
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        tex = unreal.load_asset("%s/%s" % (TEX_DIR, name))
        if name.endswith("_N"):
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
            tex.set_editor_property("srgb", False)
        elif name.endswith("_ORM"):
            tex.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
            tex.set_editor_property("srgb", False)
        unreal.EditorAssetLibrary.save_loaded_asset(tex)
    log("textures: %d" % len(files))

# ---------------------------------------------------------------- master material
def build_master():
    path = MAT_DIR + "/M_Master_Building"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Master_Building", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    def node(cls, x, y, **props):
        e = mel.create_material_expression(mat, cls, x, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e
    tex = lambda n: unreal.load_asset("%s/%s" % (TEX_DIR, n))
    t_d = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, -300, parameter_name="Detail_D", texture=tex("T_Plaster_A_D"))
    t_n = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, 200, parameter_name="Detail_N", texture=tex("T_Plaster_A_N"),
               sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    t_orm = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, 500, parameter_name="Detail_ORM", texture=tex("T_Plaster_A_ORM"),
                 sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)  # ORM is TC_MASKS
    paint = node(unreal.MaterialExpressionVectorParameter, -900, -700, parameter_name="PaintColor", default_value=unreal.LinearColor(0.45, 0.55, 0.47, 1))
    exposed = node(unreal.MaterialExpressionVectorParameter, -900, -550, parameter_name="ExposedColor", default_value=unreal.LinearColor(0.356, 0.337, 0.300, 1))
    vc = node(unreal.MaterialExpressionVertexColor, -900, -420)
    lerp = node(unreal.MaterialExpressionLinearInterpolate, -500, -600)
    connect(paint, "", lerp, "A")
    connect(exposed, "", lerp, "B")
    connect(vc, "R", lerp, "Alpha")
    d2 = node(unreal.MaterialExpressionMultiply, -500, -300, const_b=2.0)   # _D mean 0.5 -> factor mean 1.0
    connect(t_d, "RGB", d2, "A")
    base = node(unreal.MaterialExpressionMultiply, -250, -450)
    connect(lerp, "", base, "A")
    connect(d2, "", base, "B")
    r_off = node(unreal.MaterialExpressionScalarParameter, -900, 800, parameter_name="RoughnessOffset", default_value=0.0)
    rough = node(unreal.MaterialExpressionAdd, -500, 600)
    connect(t_orm, "G", rough, "A")
    connect(r_off, "", rough, "B")
    metal = node(unreal.MaterialExpressionScalarParameter, -500, 850, parameter_name="Metallic", default_value=0.0)
    # weathering (atmosphere-target.md): building-scale run-off and damp patches, then faded paint.
    # Grime is sampled at its own 16 m tile so it does not repeat with the 2 m detail; 0 = off (interiors)
    uv = node(unreal.MaterialExpressionTextureCoordinate, -1300, -100)
    g_tile = node(unreal.MaterialExpressionScalarParameter, -1300, 0, parameter_name="GrimeTiling", default_value=0.125)
    g_uv = node(unreal.MaterialExpressionMultiply, -1100, -50)
    connect(uv, "", g_uv, "A")
    connect(g_tile, "", g_uv, "B")
    t_g = node(unreal.MaterialExpressionTextureSampleParameter2D, -900, -100, parameter_name="Grime", texture=tex("T_Grime_A_D"))
    connect(g_uv, "", t_g, "UVs")
    g_amt = node(unreal.MaterialExpressionScalarParameter, -900, 50, parameter_name="GrimeStrength", default_value=0.0)
    g_lerp = node(unreal.MaterialExpressionLinearInterpolate, -600, -100, const_a=1.0)
    connect(t_g, "R", g_lerp, "B")
    connect(g_amt, "", g_lerp, "Alpha")
    grimy = node(unreal.MaterialExpressionMultiply, -100, -400)
    connect(base, "", grimy, "A")
    connect(g_lerp, "", grimy, "B")
    fade = node(unreal.MaterialExpressionScalarParameter, -100, -250, parameter_name="Fade", default_value=0.0)
    faded = node(unreal.MaterialExpressionDesaturation, 100, -400)
    connect(grimy, "", faded, "")
    connect(fade, "", faded, "Fraction")
    mel.connect_material_property(faded, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(metal, "", unreal.MaterialProperty.MP_METALLIC)
    mel.connect_material_property(t_n, "RGB", unreal.MaterialProperty.MP_NORMAL)
    mel.connect_material_property(t_orm, "R", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    for usage in ("MATUSED_NANITE", "MATUSED_STATIC_LIGHTING"):
        u = getattr(unreal.MaterialUsage, usage, None)
        if u is not None:
            mel.set_material_usage(mat, u)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    log("master material: %d expressions" % mel.get_num_material_expressions(mat))
    return mat

def make_mi(master, name, color, detail="Plaster_A", rough_offset=0.0, metallic=0.0, grime=0.0, fade=0.0):
    mi = get_or_create_mi(name, master)
    mel = unreal.MaterialEditingLibrary
    r, g, b = srgb_to_linear(color)
    mel.set_material_instance_vector_parameter_value(mi, "PaintColor", unreal.LinearColor(r, g, b, 1))
    r, g, b = srgb_to_linear(PALETTE["Concrete"])
    mel.set_material_instance_vector_parameter_value(mi, "ExposedColor", unreal.LinearColor(r, g, b, 1))
    for slot in ("D", "N", "ORM"):
        mel.set_material_instance_texture_parameter_value(mi, "Detail_" + slot, unreal.load_asset("%s/T_%s_%s" % (TEX_DIR, detail, slot)))
    mel.set_material_instance_scalar_parameter_value(mi, "RoughnessOffset", rough_offset)
    mel.set_material_instance_scalar_parameter_value(mi, "Metallic", metallic)
    mel.set_material_instance_scalar_parameter_value(mi, "GrimeStrength", grime)
    mel.set_material_instance_scalar_parameter_value(mi, "Fade", fade)
    mel.update_material_instance(mi)
    unreal.EditorAssetLibrary.save_loaded_asset(mi)
    return mi

# facade weathering strength / paint fading (atmosphere-target.md: stained, faded, time has passed)
FACADE_GRIME, FACADE_FADE = 0.9, 0.35

def build_instances(master):
    p = PALETTE
    mis = {
        "Mint": make_mi(master, "MI_T5_PaintMint", p["Mint"], grime=FACADE_GRIME, fade=FACADE_FADE),
        "Rose": make_mi(master, "MI_T5_PaintRose", p["Rose"], grime=FACADE_GRIME, fade=FACADE_FADE),
        "Concrete": make_mi(master, "MI_T5_Concrete", p["Concrete"], "Concrete_A", grime=0.8),
        "Wood": make_mi(master, "MI_T5_WindowWood", p["FrameWood"], "PaintWood_A", grime=0.7, fade=0.3),
        "Metal": make_mi(master, "MI_T5_SheetMetal", p["Rust"], "Concrete_A", -0.2, 0.35, grime=0.6),
        # opaque stand-in for glass: dark, smooth, reflects the sky (art bible 8.6 lists a glass master for later)
        "Glass": make_mi(master, "MI_T5_GlassDark", "#2B3034", "Concrete_A", -0.8, 0.0),
        "Interior": make_mi(master, "MI_T5_InteriorLime", p["Lime"]),
        "Facade_Lime": make_mi(master, "MI_Facade_Lime", p["Lime"], grime=FACADE_GRIME, fade=FACADE_FADE),
        "Facade_Concrete": make_mi(master, "MI_Facade_Concrete", p["Concrete"], grime=FACADE_GRIME, fade=FACADE_FADE),
        "Facade_Ochre": make_mi(master, "MI_Facade_Ochre", p["Ochre"], grime=FACADE_GRIME, fade=0.2),
        "Facade_Teal": make_mi(master, "MI_Facade_Teal", p["Teal"], grime=FACADE_GRIME, fade=0.2),
        "Brick": make_mi(master, "MI_Brick", p["Brick"], "Concrete_A", grime=0.7),
        "WoodGrey": make_mi(master, "MI_WoodGrey", p["WoodGrey"], "PaintWood_A", 0.1, grime=0.6),
        "Paint_OilBlue": make_mi(master, "MI_Int_OilBlue", p["OilBlue"], "Plaster_A", -0.25),
        "Wallpaper_Rose": make_mi(master, "MI_Int_WallpaperRose", p["WallpaperRose"], "Wallpaper_A"),
        "Wallpaper_Green": make_mi(master, "MI_Int_WallpaperGreen", p["WallpaperGreen"], "Wallpaper_A"),
        "FloorBoards": make_mi(master, "MI_Int_FloorBoards", p["FloorBoards"], "Planks_A", -0.1),
        "Linoleum": make_mi(master, "MI_Int_Linoleum", p["Linoleum"], "Plaster_A", -0.3),
        "Furniture": make_mi(master, "MI_Int_Furniture", p["FurnitureWood"], "PaintWood_A", -0.35),
        "Carpet": make_mi(master, "MI_Int_Carpet", p["CarpetRed"], "Carpet_A", 0.1),
        "Sofa": make_mi(master, "MI_Int_Sofa", p["SofaGreen"], "Concrete_A", 0.05),
        "Radiator": make_mi(master, "MI_Int_Radiator", p["Radiator"], "PaintWood_A", -0.2),
        "BlackPlastic": make_mi(master, "MI_Int_BlackPlastic", p["BlackPlastic"], "Plaster_A", -0.4),
        "Screen": make_mi(master, "MI_Int_Screen", "#1E2226", "Plaster_A", -0.8),
        "Paper": make_mi(master, "MI_Int_Paper", p["Paper"], "Plaster_A"),
        "Enamel": make_mi(master, "MI_Int_Enamel", p["Enamel"], "Plaster_A", -0.6),
        "Stencil": make_mi(master, "MI_T5_Stencil", p["Stencil"], "Plaster_A", 0.05, grime=0.5),
        "Mural_Red": make_mi(master, "MI_Mural_Red", p["PosterRed"], "Plaster_A", grime=FACADE_GRIME, fade=FACADE_FADE),
        "Mural_Brown": make_mi(master, "MI_Mural_Brown", p["Rust"], "Plaster_A", grime=FACADE_GRIME, fade=FACADE_FADE),
        "CurtainRed": make_mi(master, "MI_Int_Curtain", "#6E2A28", "Concrete_A", 0.1),
        "Roof": make_mi(master, "MI_Roof_Slate", p["Slate"], "Concrete_A", 0.0, grime=0.6),
        "Bark_Birch": make_mi(master, "MI_Bark_Birch", p["BirchBark"], "Concrete_A"),
        "Bark_Larch": make_mi(master, "MI_Bark_Larch", p["LarchBark"], "Concrete_A"),
    }
    mis["Facade_Mint"], mis["Facade_Rose"] = mis["Mint"], mis["Rose"]
    log("material instances: %s" % sorted(mis))
    return mis


def build_ground():
    """M_Master_Ground (art bible 8.6): detail tiling every DetailTiling UV units, macro blend ColorA/ColorB."""
    path = MAT_DIR + "/M_Master_Ground"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Master_Ground", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    mel = unreal.MaterialEditingLibrary
    def node(cls, x, y, **props):
        e = mel.create_material_expression(mat, cls, x, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e
    tex = lambda n: unreal.load_asset("%s/%s" % (TEX_DIR, n))
    uv = node(unreal.MaterialExpressionTextureCoordinate, -1300, 0)
    tile = node(unreal.MaterialExpressionScalarParameter, -1300, 150, parameter_name="DetailTiling", default_value=4000.0)
    macro_tile = node(unreal.MaterialExpressionScalarParameter, -1300, 300, parameter_name="MacroTiling", default_value=160.0)
    uv_d = node(unreal.MaterialExpressionMultiply, -1050, 0)
    connect(uv, "", uv_d, "A"); connect(tile, "", uv_d, "B")
    uv_m = node(unreal.MaterialExpressionMultiply, -1050, 300)
    connect(uv, "", uv_m, "A"); connect(macro_tile, "", uv_m, "B")
    t_d = node(unreal.MaterialExpressionTextureSampleParameter2D, -800, -200, parameter_name="Detail_D", texture=tex("T_Ground_A_D"))
    t_n = node(unreal.MaterialExpressionTextureSampleParameter2D, -800, 150, parameter_name="Detail_N", texture=tex("T_Ground_A_N"),
               sampler_type=unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    t_m = node(unreal.MaterialExpressionTextureSampleParameter2D, -800, 450, parameter_name="Macro_D", texture=tex("T_Concrete_A_D"))
    for t in (t_d, t_n):
        connect(uv_d, "", t, "UVs")
    connect(uv_m, "", t_m, "UVs")
    ca = node(unreal.MaterialExpressionVectorParameter, -800, -600, parameter_name="ColorA", default_value=unreal.LinearColor(0.16, 0.19, 0.07, 1))
    cb = node(unreal.MaterialExpressionVectorParameter, -800, -450, parameter_name="ColorB", default_value=unreal.LinearColor(0.23, 0.19, 0.09, 1))
    lerp = node(unreal.MaterialExpressionLinearInterpolate, -500, -500)
    connect(ca, "", lerp, "A"); connect(cb, "", lerp, "B")
    # sharpen the macro mask into distinct patches of bare dirt and grass (user reference 2026-11-07)
    # average with a second macro sample at a non-integer 2.6x scale so the 50 m patch grid does not repeat visibly
    uv_m2 = node(unreal.MaterialExpressionMultiply, -1050, 500, const_b=0.383)
    connect(uv_m, "", uv_m2, "A")
    t_m2 = node(unreal.MaterialExpressionTextureSample, -800, 600, texture=tex("T_Concrete_A_D"))
    connect(uv_m2, "", t_m2, "UVs")
    m_avg = node(unreal.MaterialExpressionLinearInterpolate, -700, 450, const_alpha=0.5)
    connect(t_m, "R", m_avg, "A"); connect(t_m2, "R", m_avg, "B")
    m_sub = node(unreal.MaterialExpressionSubtract, -650, 350, const_b=0.5)
    connect(m_avg, "", m_sub, "A")
    m_con = node(unreal.MaterialExpressionScalarParameter, -800, 650, parameter_name="MacroContrast", default_value=4.0)
    m_mul = node(unreal.MaterialExpressionMultiply, -550, 350)
    connect(m_sub, "", m_mul, "A"); connect(m_con, "", m_mul, "B")
    # trodden bare dirt in town, tundra outside: bias the mask by distance from the town centre (world origin)
    wp = node(unreal.MaterialExpressionWorldPosition, -1300, 800)
    wxy = node(unreal.MaterialExpressionComponentMask, -1150, 800, r=True, g=True, b=False, a=False)
    connect(wp, "", wxy, "")
    wlen = node(unreal.MaterialExpressionLength, -1000, 800)
    connect(wxy, "", wlen, "")
    town = node(unreal.MaterialExpressionMultiply, -850, 800, const_b=-1.0 / 30000.0)   # 300 m fade (cm)
    connect(wlen, "", town, "A")
    town_b = node(unreal.MaterialExpressionAdd, -750, 800, const_b=3.0)                 # 1 inside 600 m, 0 beyond 900 m
    connect(town, "", town_b, "A")
    town_s = node(unreal.MaterialExpressionSaturate, -650, 800)
    connect(town_b, "", town_s, "")
    bias = node(unreal.MaterialExpressionLinearInterpolate, -550, 650, const_a=0.12, const_b=0.45)   # outside: mostly green; town: dirt/grass mix
    connect(town_s, "", bias, "Alpha")
    m_add = node(unreal.MaterialExpressionAdd, -450, 350)
    connect(m_mul, "", m_add, "A"); connect(bias, "", m_add, "B")
    m_sat = node(unreal.MaterialExpressionSaturate, -350, 350)
    connect(m_add, "", m_sat, "")
    connect(m_sat, "", lerp, "Alpha")
    d2 = node(unreal.MaterialExpressionMultiply, -500, -200, const_b=2.0)
    connect(t_d, "RGB", d2, "A")
    # the 2 m detail repeated as a visible waffle grid; average it with a second sample at a non-integer 7.3 m scale
    uv_d2 = node(unreal.MaterialExpressionMultiply, -1050, -250, const_b=0.273)
    connect(uv_d, "", uv_d2, "A")
    t_d2 = node(unreal.MaterialExpressionTextureSample, -800, -350, texture=tex("T_Ground_A_D"))
    connect(uv_d2, "", t_d2, "UVs")
    d2b = node(unreal.MaterialExpressionMultiply, -500, -350, const_b=2.0)
    connect(t_d2, "RGB", d2b, "A")
    mix = node(unreal.MaterialExpressionLinearInterpolate, -350, -250, const_alpha=0.5)
    connect(d2, "", mix, "A"); connect(d2b, "", mix, "B")
    # full pebble/twig detail near the camera, faded with distance where its 2 m repeat would show as a grid
    depth = node(unreal.MaterialExpressionPixelDepth, -700, -50)
    near = node(unreal.MaterialExpressionMultiply, -600, -50, const_b=1.0 / 3000.0)
    connect(depth, "", near, "A")
    near_s = node(unreal.MaterialExpressionSaturate, -500, -50)
    connect(near, "", near_s, "")
    detail_amt = node(unreal.MaterialExpressionLinearInterpolate, -400, -50, const_a=1.0, const_b=0.35)
    connect(near_s, "", detail_amt, "Alpha")
    soft = node(unreal.MaterialExpressionLinearInterpolate, -300, -150, const_a=1.0)
    connect(mix, "", soft, "B"); connect(detail_amt, "", soft, "Alpha")
    base = node(unreal.MaterialExpressionMultiply, -250, -350)
    connect(lerp, "", base, "A"); connect(soft, "", base, "B")
    rough = node(unreal.MaterialExpressionScalarParameter, -250, 0, parameter_name="Roughness", default_value=0.92)
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    # flatten the tiling normal: under the low overcast sun its 2 m bumps shaded into a visible grid
    flat = node(unreal.MaterialExpressionConstant3Vector, -500, 300, constant=unreal.LinearColor(0, 0, 1, 1))
    n_soft = node(unreal.MaterialExpressionLinearInterpolate, -300, 250)
    connect(t_n, "RGB", n_soft, "A"); connect(flat, "", n_soft, "B")
    flat_amt = node(unreal.MaterialExpressionLinearInterpolate, -400, 350, const_a=0.1, const_b=0.75)
    connect(near_s, "", flat_amt, "Alpha"); connect(flat_amt, "", n_soft, "Alpha")
    mel.connect_material_property(n_soft, "", unreal.MaterialProperty.MP_NORMAL)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    def mi(name, a, b, rough_v, tiling):
        inst = get_or_create_mi(name, mat)
        for pname, hexv in (("ColorA", a), ("ColorB", b)):
            r, g, bl = srgb_to_linear(PALETTE[hexv])
            mel.set_material_instance_vector_parameter_value(inst, pname, unreal.LinearColor(r, g, bl, 1))
        mel.set_material_instance_scalar_parameter_value(inst, "Roughness", rough_v)
        mel.set_material_instance_scalar_parameter_value(inst, "DetailTiling", tiling)
        mel.update_material_instance(inst)
        unreal.EditorAssetLibrary.save_loaded_asset(inst)
    mi("MI_Ground_Tundra", "TundraGreen", "TundraDry", 0.92, 4000.0)   # terrain UV 0..1 spans 8 km -> 2 m tiles
    mi("MI_Ground_Gravel", "Gravel", "GravelDark", 0.85, 1.0)          # ribbons carry a single UV: flat gravel
    mi("MI_Ground_River", "RiverWater", "RiverWater", 0.08, 1.0)
    mi("MI_Ground_Forest", "ForestDark", "ForestLight", 0.95, 4000.0)  # backdrop ring (UV 0..1 over 60 km)
    log("ground material + 3 instances")

def build_foliage():
    """M_Master_Foliage (art bible 8.6): masked, two-sided; LeafColor x (card grey x 2), opacity from alpha."""
    path = MAT_DIR + "/M_Master_Foliage"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Master_Foliage", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_MASKED)
    mat.set_editor_property("two_sided", True)
    mel = unreal.MaterialEditingLibrary
    def node(cls, x, y, **props):
        e = mel.create_material_expression(mat, cls, x, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e
    t = node(unreal.MaterialExpressionTextureSampleParameter2D, -800, -200, parameter_name="Card_D",
             texture=unreal.load_asset(TEX_DIR + "/T_LeavesBroad_A_D"))
    col = node(unreal.MaterialExpressionVectorParameter, -800, -500, parameter_name="LeafColor", default_value=unreal.LinearColor(0.15, 0.24, 0.04, 1))
    d2 = node(unreal.MaterialExpressionMultiply, -500, -200, const_b=2.0)
    connect(t, "RGB", d2, "A")
    base = node(unreal.MaterialExpressionMultiply, -250, -350)
    connect(col, "", base, "A"); connect(d2, "", base, "B")
    rough = node(unreal.MaterialExpressionScalarParameter, -250, 0, parameter_name="Roughness", default_value=0.75)
    mel.connect_material_property(base, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(t, "A", unreal.MaterialProperty.MP_OPACITY_MASK)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    for name, color, card in (("MI_Leaves_Birch", "BirchLeaf", "T_LeavesBroad_A_D"), ("MI_Leaves_Shrub", "ShrubLeaf", "T_LeavesBroad_A_D"),
                              ("MI_Leaves_Larch", "LarchNeedle", "T_LeavesNeedle_A_D"), ("MI_Grass", "Grass", "T_GrassBlades_A_D"),
                              # facade decals reuse the masked card master (8 m tile set by the kit's per-material UV scale)
                              ("MI_Decal_Crack", "DecalCrack", "T_DecalCrack_A_D"), ("MI_Decal_Spall", "DecalSpall", "T_DecalSpall_A_D"),
                              ("MI_Decal_Rust", "DecalRust", "T_DecalRust_A_D"),
                              # road / footpath ribbons: ragged edges from the card alpha (tools/research/lines_to_obj.py UVs)
                              ("MI_Road", "RoadGravel", "T_Road_A_D"), ("MI_Path", "PathDirt", "T_Path_A_D")):
        inst = get_or_create_mi(name, mat)
        r, g, b = srgb_to_linear(PALETTE[color])
        mel.set_material_instance_vector_parameter_value(inst, "LeafColor", unreal.LinearColor(r, g, b, 1))
        mel.set_material_instance_texture_parameter_value(inst, "Card_D", unreal.load_asset(TEX_DIR + "/" + card))
        mel.update_material_instance(inst)
        unreal.EditorAssetLibrary.save_loaded_asset(inst)
    log("foliage material + 3 instances")

def build_glass():
    """M_Master_Glass (art bible 8.6): translucent window panes so daylight reaches the interiors."""
    path = MAT_DIR + "/M_Master_Glass"
    if unreal.EditorAssetLibrary.does_asset_exist(path):
        unreal.EditorAssetLibrary.delete_asset(path)
    mat = unreal.AssetToolsHelpers.get_asset_tools().create_asset("M_Master_Glass", MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())
    mat.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    tlm = getattr(unreal.TranslucencyLightingMode, "TLM_SURFACE_FORWARD_SHADING", None)
    if tlm is not None:
        mat.set_editor_property("translucency_lighting_mode", tlm)
    mel = unreal.MaterialEditingLibrary
    def node(cls, x, y, **props):
        e = mel.create_material_expression(mat, cls, x, y)
        for k, v in props.items():
            e.set_editor_property(k, v)
        return e
    col = node(unreal.MaterialExpressionVectorParameter, -500, -300, parameter_name="Color", default_value=unreal.LinearColor(0.05, 0.06, 0.06, 1))
    op = node(unreal.MaterialExpressionScalarParameter, -500, -100, parameter_name="Opacity", default_value=0.18)
    rough = node(unreal.MaterialExpressionScalarParameter, -500, 100, parameter_name="Roughness", default_value=0.06)
    mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    inst = get_or_create_mi("MI_T5_Glass", mat)
    mel.update_material_instance(inst)
    unreal.EditorAssetLibrary.save_loaded_asset(inst)
    # coloured panes of the Kulturhaus window wall (photo R4), ANNAHME colours
    for name, rgb, opacity in (("MI_Glass_StainBlue", (0.03, 0.12, 0.45), 0.5), ("MI_Glass_StainRed", (0.45, 0.04, 0.03), 0.5),
                               ("MI_Glass_StainCyan", (0.05, 0.35, 0.4), 0.45)):
        inst = get_or_create_mi(name, mat)
        mel.set_material_instance_vector_parameter_value(inst, "Color", unreal.LinearColor(*rgb, 1))
        mel.set_material_instance_scalar_parameter_value(inst, "Opacity", opacity)
        mel.update_material_instance(inst)
        unreal.EditorAssetLibrary.save_loaded_asset(inst)
    log("glass material + instance")

try:
    import_textures()
    build_instances(build_master())
    build_ground()
    build_foliage()
    build_glass()
    log("RESULT OK")
except Exception:
    log("RESULT FAILED\n" + traceback.format_exc())
finally:
    open(REPORT, "w", encoding="utf-8").write("\n".join(log_lines) + "\n")
    unreal.SystemLibrary.quit_editor()
