#!/bin/zsh
# Close Unreal before running. Only hall, roads and verges are rebuilt.
set -euo pipefail
cd "${0:A:h}/.."
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
python3 tools/asset-pipeline/test_furniture.py
python3 tools/research/test_environment_assets.py
python3 tools/research/fetch_surfaces.py
"/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13" tools/asset-pipeline/road_wear.py assets/textures
LOGS="Saved/EnvironmentUpdateLogs"
mkdir -p "$LOGS"
SOURCE_BACKUP="Saved/EnvironmentSourceBackups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$SOURCE_BACKUP"
cp assets/terrain/roads_kadykchan.obj assets/terrain/paths_kadykchan.obj "$SOURCE_BACKUP/"
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json roads assets/terrain/roads_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json tracks assets/terrain/tracks_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json paths assets/terrain/paths_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj assets/buildings/buildings_manifest.json
python3 -I tools/research/verge_details.py
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_buildings.py -- "$PWD" PLA_Yuzhnaya_9 > "$LOGS/blender.log" 2>&1
grep -q 'BUILDINGS OK 1' "$LOGS/blender.log"
REPORT="$PWD/tools/editor/refresh_environment_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "$LOGS/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_environment.py" -unattended > "$LOGS/unreal.log" 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && [[ "$(tail -1 "$REPORT")" == 'RESULT OK' ]] || { print 'Aktualisierung nicht abgeschlossen. tools/editor/refresh_environment_report.txt und Saved/EnvironmentUpdateLogs prüfen.'; exit 1; }
print 'Saal, Wege und Wegesränder aktualisiert.'
