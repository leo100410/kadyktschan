"""Import the shooter mode meshes and sounds (tools/asset-pipeline/shooter_props.py, shooter_audio.py).

Only new assets under /Game/Kadykchan/Shooter: the world map is not touched, the game spawns everything at runtime.
Writes tools/editor/refresh_shooter_report.txt, ending in RESULT OK.
"""
import json
from pathlib import Path
import sys
import traceback
import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0, str(ROOT / 'tools/editor'))
REPORT = ROOT / 'tools/editor/refresh_shooter_report.txt'
DEST = '/Game/Kadykchan/Shooter'
NO_COLLISION = ('SM_Shooter_Bandage', 'SM_Shooter_Medkit', 'SM_Shooter_Ammo', 'SM_Shooter_Vest', 'SM_Shooter_Radio',
                'SM_Shooter_Documents', 'SM_Shooter_Jammer', 'SM_Shooter_Rifle')
LOOPS = ('A_DroneMotor_Loop',)
lines = []


def import_task(filename, dest, name, options=None):
    task = unreal.AssetImportTask()
    task.filename = str(filename)
    task.destination_path = dest
    task.destination_name = name
    task.automated, task.replace_existing, task.save = True, True, True
    if options:
        task.options = options
    return task


def main():
    import place_vegetation
    slots = dict(place_vegetation.SLOT_MI, Paper='MI_Int_Paper', CurtainRed='MI_Int_Curtain', Sofa='MI_Int_Sofa',
                 Carpet='MI_Int_Carpet')
    meshes = json.loads((ROOT / 'assets/shooter/meshes.json').read_text())
    options = unreal.FbxImportUI()
    options.set_editor_property('import_materials', False)
    options.set_editor_property('import_textures', False)
    smd = options.static_mesh_import_data
    smd.set_editor_property('combine_meshes', True)
    smd.set_editor_property('auto_generate_collision', False)
    smd.set_editor_property('generate_lightmap_u_vs', False)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    tools.import_asset_tasks([import_task(ROOT / 'assets/shooter' / (n + '.fbx'), DEST, n, options) for n in meshes])
    sms = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    for name in meshes:
        mesh = unreal.load_asset(DEST + '/' + name)
        assert isinstance(mesh, unreal.StaticMesh), 'FBX import failed: ' + name
        for i, m in enumerate(mesh.get_editor_property('static_materials')):
            slot = str(m.get_editor_property('material_slot_name'))
            material = unreal.load_asset('/Game/Kadykchan/Materials/' + slots[slot])
            assert material, 'missing material for slot %s in %s' % (slot, name)
            mesh.set_material(i, material)
        nanite = sms.get_nanite_settings(mesh)
        nanite.set_editor_property('enabled', False)  # buildings run without Nanite on the Mac too
        sms.set_nanite_settings(mesh, nanite, True)
        sms.remove_collisions(mesh)
        collide = name not in NO_COLLISION
        for section in range(mesh.get_num_sections(0)):
            sms.enable_section_collision(mesh, collide, 0, section)
        if collide:
            body = mesh.get_editor_property('body_setup')
            assert body, 'missing collision body: ' + name
            body.set_editor_property('collision_trace_flag', unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        unreal.EditorAssetLibrary.save_loaded_asset(mesh)
        lines.append('%s: %d quads, collision %s' % (name, meshes[name]['quads'], collide))
    wavs = sorted((ROOT / 'assets/shooter/audio').glob('*.wav'))
    assert len(wavs) >= 7, 'run shooter_audio.py first'
    tools.import_asset_tasks([import_task(w, DEST + '/Audio', w.stem) for w in wavs])
    for w in wavs:
        sound = unreal.load_asset(DEST + '/Audio/' + w.stem)
        if not isinstance(sound, unreal.SoundWave):
            raise RuntimeError('did not import as SoundWave: ' + w.stem)
        sound.set_editor_property('looping', w.stem in LOOPS)
        unreal.EditorAssetLibrary.save_loaded_asset(sound)
        lines.append('sound %s' % w.stem)
    lines.append('%d meshes, %d sounds under %s' % (len(meshes), len(wavs), DEST))


try:
    main()
    lines.append('RESULT OK')
except Exception:
    lines.append(traceback.format_exc())
    lines.append('RESULT FAILED')
REPORT.write_text('\n'.join(lines) + '\n')
