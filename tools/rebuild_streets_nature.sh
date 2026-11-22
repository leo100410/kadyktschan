#!/bin/zsh
# Close Unreal first. Rebuild roads and foliage, retaining buildings, grass cells and town props.
set -euo pipefail
cd "${0:A:h}/.."
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
PYTHON="/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13"
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
python3 tools/research/test_environment_assets.py
python3 tools/research/test_streets_nature.py
"$PYTHON" tools/asset-pipeline/test_road_wear.py
python3 tools/research/fetch_surfaces.py
LOGS="Saved/StreetsNatureLogs"
mkdir -p "$LOGS"
BACKUP="Saved/StreetsNatureSourceBackups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp assets/vegetation/scatter.json assets/vegetation/veg_manifest.json assets/terrain/roads_kadykchan.obj "$BACKUP/"
[[ ! -f assets/terrain/tracks_kadykchan.obj ]] || cp assets/terrain/tracks_kadykchan.obj "$BACKUP/"
cp -R Content/Kadykchan/Data/Foliage "$BACKUP/Foliage"
"$PYTHON" tools/asset-pipeline/road_wear.py assets/textures
KDK_TEX_ONLY=LeavesWillow_A,LeavesAlder_A "$PYTHON" tools/asset-pipeline/gen_textures.py assets/textures
python3 -I tools/research/refine_vegetation.py
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json roads assets/terrain/roads_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json tracks assets/terrain/tracks_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_nature.py -- "$PWD" > "$LOGS/blender.log" 2>&1
grep -q 'NATURE MESHES OK 28' "$LOGS/blender.log"
REPORT="$PWD/tools/editor/refresh_streets_nature_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "$LOGS/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_streets_nature.py" -unattended > "$LOGS/unreal.log" 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && [[ "$(tail -1 "$REPORT")" == 'RESULT OK' ]] || { print 'Aktualisierung nicht abgeschlossen. tools/editor/refresh_streets_nature_report.txt und Saved/StreetsNatureLogs prüfen.'; exit 1; }
print 'Asphaltstraßen, Markierungen und Buschgruppen aktualisiert.'
