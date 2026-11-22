"""Import the repaired road/prop geometry and fictional power station, with backups."""
import datetime
import json
from pathlib import Path
import shutil
import sys
import traceback
import unreal

ROOT=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0,str(ROOT/'tools/editor'))
REPORT=ROOT/'tools/editor/refresh_power_roads_report.txt'
lines=[]


def main():
    backup=ROOT/'Saved/PowerRoadAssetBackups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for name in ('Content/Kadykchan/Materials','Content/Kadykchan/Terrain','Content/Kadykchan/Vegetation/Generated',
                 'Content/Kadykchan/Maps','Content/Kadykchan/Power','Content/__ExternalActors__/Kadykchan/Maps/Kadykchan_World'):
        source=ROOT/name
        if source.is_dir(): shutil.copytree(source,backup/name)
    lines.append('Backup: '+str(backup))
    import scanned_surfaces
    scanned_surfaces.apply()
    import place_ground
    place_ground.RIBBONS=[r for r in place_ground.RIBBONS if r[2] in ('Roads_Blockout','Paths_Footpaths')]
    assert len(place_ground.RIBBONS)==2
    place_ground.main()
    import place_vegetation
    place_vegetation.main()
    lines.extend(place_ground.log_lines)
    lines.extend(place_vegetation.log_lines)
    options=unreal.FbxImportUI()
    options.set_editor_property('import_materials',False)
    options.set_editor_property('import_textures',False)
    options.static_mesh_import_data.set_editor_property('combine_meshes',True)
    options.static_mesh_import_data.set_editor_property('auto_generate_collision',False)
    task=unreal.AssetImportTask()
    task.filename=str(ROOT/'assets/power/SM_PowerStation.fbx')
    task.destination_path='/Game/Kadykchan/Power'
    task.destination_name='SM_PowerStation'
    task.automated,task.replace_existing,task.save,task.options=True,True,True,options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    mesh=unreal.load_asset('/Game/Kadykchan/Power/SM_PowerStation')
    assert isinstance(mesh,unreal.StaticMesh),'station FBX import failed'
    slots=dict(place_vegetation.SLOT_MI)
    slots['WoodGrey']='MI_WoodGrey'
    for i,m in enumerate(mesh.get_editor_property('static_materials')):
        name=str(m.get_editor_property('material_slot_name'))
        material=unreal.load_asset('/Game/Kadykchan/Materials/'+slots[name])
        assert material, 'missing station material '+name
        mesh.set_material(i,material)
    sms=unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    nanite=sms.get_nanite_settings(mesh);nanite.set_editor_property('enabled',False)
    sms.set_nanite_settings(mesh,nanite,True)
    sms.remove_collisions(mesh)
    for section in range(mesh.get_num_sections(0)):
        sms.enable_section_collision(mesh,True,0,section)
    assert mesh.get_editor_property('body_setup'),'station body setup missing'
    mesh.get_editor_property('body_setup').set_editor_property('collision_trace_flag',unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    eas=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    station=next((a for a in eas.get_all_level_actors() if a.get_actor_label()=='Power_Station'),None)
    site=json.loads((ROOT/'assets/power/site.json').read_text())
    if station is None:
        station=eas.spawn_actor_from_object(mesh,unreal.Vector(site['north_m']*100,site['east_m']*100,0))
        station.set_actor_label('Power_Station');station.set_folder_path('Power')
        station.set_editor_property('is_spatially_loaded',False)
    station.modify();station.static_mesh_component.set_static_mesh(mesh)
    station.set_actor_location(unreal.Vector(site['north_m']*100,site['east_m']*100,0),False,False)
    # Shared emissive warm bulb material; actual illumination is distance-limited at runtime.
    path='/Game/Kadykchan/Materials/M_PowerBulb'
    mat=unreal.load_asset(path)
    if mat is None:
        mat=unreal.AssetToolsHelpers.get_asset_tools().create_asset('M_PowerBulb','/Game/Kadykchan/Materials',unreal.Material,unreal.MaterialFactoryNew())
        color=unreal.MaterialEditingLibrary.create_material_expression(mat,unreal.MaterialExpressionConstant3Vector)
        color.set_editor_property('constant',unreal.LinearColor(6,3.6,1.38,1))
        assert unreal.MaterialEditingLibrary.connect_material_property(color,'',unreal.MaterialProperty.MP_EMISSIVE_COLOR)
        unreal.MaterialEditingLibrary.recompile_material(mat)
    unreal.EditorAssetLibrary.save_loaded_asset(mat)
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    lines.append('Power station imported; roads and props refreshed.')
    lines.append('RESULT OK')


try: main()
except Exception: lines.append('RESULT FAILED\n'+traceback.format_exc())
finally:
    REPORT.write_text('\n'.join(lines)+'\n')
    unreal.log_warning('\n'.join(lines))
    unreal.SystemLibrary.quit_editor()
