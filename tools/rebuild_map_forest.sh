#!/bin/zsh
# Rebuild maps/UI and distant foliage, retaining all town geometry and furnished rooms.
set -euo pipefail
cd "${0:A:h}/.."
if pgrep -f '[U]nrealEditor.*Kadyktschan.uproject' >/dev/null; then
  print 'Bitte Spiel und Unreal Editor zuerst schließen und den Befehl dann erneut starten.'
  exit 1
fi
UE_ROOT="/Users/Shared/Epic Games/UE_5.8/Engine"
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
LOGS="Saved/MapForestLogs"
mkdir -p "$LOGS"
BACKUP="Saved/MapForestSourceBackups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp Content/Kadykchan/Data/TownMap.json Content/Kadykchan/Data/Story.json assets/vegetation/veg_manifest.json "$BACKUP/"
cp -R Content/Kadykchan/Data/Foliage "$BACKUP/Foliage"
python3 -I tools/research/town_map_data.py design/research/data/blockout-2026-11-07.json assets/buildings/buildings_manifest.json Content/Kadykchan/Data/TownMap.json
python3 -I tools/research/story_data.py
python3 tools/research/test_map_forest.py
python3 tools/research/test_streets_nature.py
"$UE_ROOT/Build/BatchFiles/Mac/Build.sh" KadyktschanEditor Mac Development -Project="$PWD/Kadyktschan.uproject" -WaitMutex > "$LOGS/build.log" 2>&1 || { print 'Build fehlgeschlagen: Saved/MapForestLogs/build.log';exit 1; }
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_nature.py -- "$PWD" > "$LOGS/forest.log" 2>&1
grep -q 'NATURE MESHES OK 28' "$LOGS/forest.log"
REPORT="$PWD/tools/editor/refresh_map_forest_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "$LOGS/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE_ROOT/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_map_forest.py" -unattended > "$LOGS/unreal.log" 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && [[ "$(tail -1 "$REPORT")" == 'RESULT OK' ]] || { print 'Import fehlgeschlagen: tools/editor/refresh_map_forest_report.txt';exit 1; }
print 'Kartenbeschriftung, Einrichtungskarte und Waldsichtweite aktualisiert.'
