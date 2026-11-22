"""Refresh five residential buildings and town vegetation/props, retaining other buildings and missions."""
import datetime
from pathlib import Path
import shutil
import sys
import traceback
import unreal

ROOT=Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0,str(ROOT/'tools/editor'))
REPORT=ROOT/'tools/editor/refresh_neighbourhood_report.txt'
lines=[]


def main():
    backup=ROOT/'Saved/NeighbourhoodAssetBackups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    for name in ('Content/Kadykchan/Maps','Content/Kadykchan/Vegetation/Generated','Content/Kadykchan/Terrain',
                 'Content/__ExternalActors__/Kadykchan/Maps/Kadykchan_World'):
        source=ROOT/name
        if source.is_dir():shutil.copytree(source,backup/name)
    lines.append('Backup: '+str(backup))
    import refresh_interiors
    refresh_interiors.LABELS={'PLA_Lenina_8','PLA_Lenina_7','PLA_SAT_S_Block','PLA_Shkolnaya_4','PLA_Shkolnaya_6'}
    refresh_interiors.main()
    lines.extend(x for x in refresh_interiors.lines if x!='RESULT OK')
    import place_vegetation
    place_vegetation.main()
    lines.extend(place_vegetation.log_lines)
    lines.append('Five residential houses, upper floors, barriers and courtyard/woodland geometry imported.')
    lines.append('RESULT OK')


try:main()
except Exception:lines.append('RESULT FAILED\n'+traceback.format_exc())
finally:
    REPORT.write_text('\n'.join(lines)+'\n')
    unreal.log_warning('\n'.join(lines))
    unreal.SystemLibrary.quit_editor()
