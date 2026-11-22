"""Refresh only foliage prototypes/instance field; preserve all placed town props and interiors."""
import datetime
from pathlib import Path
import shutil
import sys
import traceback
import unreal

ROOT=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0,str(ROOT/'tools/editor'))
REPORT=ROOT/'tools/editor/refresh_map_forest_report.txt'
lines=[]

try:
    backup=ROOT/'Saved/MapForestAssetBackups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for name in ('Content/Kadykchan/Vegetation/Generated','Content/Kadykchan/Maps','Content/__ExternalActors__/Kadykchan/Maps/Kadykchan_World'):
        source=ROOT/name
        if source.is_dir():shutil.copytree(source,backup/name)
    for name in ("LeavesBroad_A","LeavesNeedle_A","LeavesWillow_A","LeavesAlder_A"):
        for ext in (".uasset",".ubulk",".uexp"):
            relative=Path('Content/Kadykchan/Materials/Textures')/('T_'+name+'_D'+ext)
            if (ROOT/relative).is_file():
                (backup/relative).parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/relative,backup/relative)
    lines.append('Backup: '+str(backup))
    from foliage_materials import apply_leaf_mips
    apply_leaf_mips()
    import place_vegetation
    place_vegetation.main(only_foliage=True)
    lines.extend(place_vegetation.log_lines)
    lines.append('RESULT OK')
except Exception:
    lines.append('RESULT FAILED\n'+traceback.format_exc())
finally:
    REPORT.write_text('\n'.join(lines)+'\n')
    unreal.log_warning('\n'.join(lines))
    unreal.SystemLibrary.quit_editor()
