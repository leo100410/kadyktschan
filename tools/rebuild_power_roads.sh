#!/bin/zsh
# Close the game/editor first. Preserve old source and imported assets before replacing them.
set -euo pipefail
cd "${0:A:h}/.."
UE_ROOT="/Users/Shared/Epic Games/UE_5.8/Engine"
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
if pgrep -f '[U]nrealEditor.*Kadyktschan.uproject' > /dev/null; then
  print 'Bitte Kadyktschan und den Unreal Editor zuerst schließen, dann den Befehl erneut starten.'
  exit 1
fi
LOGS="Saved/PowerRoadLogs"
mkdir -p "$LOGS"
python3 tools/research/test_power_update.py
python3 tools/research/test_environment_assets.py
BACKUP="Saved/PowerRoadSourceBackups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp assets/vegetation/scatter.json assets/vegetation/veg_manifest.json assets/terrain/roads_kadykchan.obj assets/terrain/paths_kadykchan.obj Content/Kadykchan/Data/Story.json Content/Kadykchan/Data/TownMap.json "$BACKUP/"
cp -R Content/Kadykchan/Data/Foliage "$BACKUP/Foliage"
"$UE_ROOT/Build/BatchFiles/Mac/Build.sh" KadyktschanEditor Mac Development -Project="$PWD/Kadyktschan.uproject" -WaitMutex > "$LOGS/build.log" 2>&1 || { print 'Build fehlgeschlagen: Saved/PowerRoadLogs/build.log'; exit 1; }
python3 tools/research/power_update.py
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json roads assets/terrain/roads_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json paths assets/terrain/paths_kadykchan.obj assets/terrain/terrain_kadykchan_8km.obj assets/buildings/buildings_manifest.json
python3 -I tools/research/town_map_data.py design/research/data/blockout-2026-11-07.json assets/buildings/buildings_manifest.json Content/Kadykchan/Data/TownMap.json
python3 -I tools/research/story_data.py
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_power_station.py -- "$PWD" > "$LOGS/station.log" 2>&1
grep -q 'POWER MESH OK' "$LOGS/station.log"
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_vegetation.py -- "$PWD" > "$LOGS/props.log" 2>&1
grep -q 'VEGETATION OK' "$LOGS/props.log"
REPORT="$PWD/tools/editor/refresh_power_roads_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "$LOGS/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE_ROOT/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_power_roads.py" -unattended > "$LOGS/unreal.log" 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && [[ "$(tail -1 "$REPORT")" == 'RESULT OK' ]] || { print 'Import fehlgeschlagen: tools/editor/refresh_power_roads_report.txt'; exit 1; }
print 'Elektrizitätswerk, Startmission, Beleuchtung und Straßen aktualisiert.'
