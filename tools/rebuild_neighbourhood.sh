#!/bin/zsh
# Build the curated residential and woodland update; close the game/editor first.
set -euo pipefail
cd "${0:A:h}/.."
if pgrep -f '[U]nrealEditor.*Kadyktschan.uproject' >/dev/null; then
  print 'Bitte Spiel und Unreal Editor zuerst schließen und den Befehl dann erneut starten.'
  exit 1
fi
UE_ROOT="/Users/Shared/Epic Games/UE_5.8/Engine"
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
LOGS="Saved/NeighbourhoodLogs"
mkdir -p "$LOGS"
python3 tools/asset-pipeline/test_furniture.py
python3 tools/asset-pipeline/test_residential.py
python3 tools/research/test_neighbourhood.py
python3 tools/asset-pipeline/verify_residential_assembly.py > "$LOGS/assembly.txt"
"$UE_ROOT/Build/BatchFiles/Mac/Build.sh" KadyktschanEditor Mac Development -Project="$PWD/Kadyktschan.uproject" -WaitMutex > "$LOGS/build.log" 2>&1 || { print 'Build fehlgeschlagen: Saved/NeighbourhoodLogs/build.log';exit 1; }
BACKUP="Saved/NeighbourhoodSourceBackups/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP"
cp assets/vegetation/scatter.json assets/vegetation/veg_manifest.json assets/buildings/buildings_manifest.json Content/Kadykchan/Data/Story.json Content/Kadykchan/Data/TownMap.json Content/Kadykchan/Data/Power.json "$BACKUP/"
cp -R Content/Kadykchan/Data/Foliage "$BACKUP/Foliage"
python3 - "$BACKUP" <<'PY'
import json,shutil,sys
from pathlib import Path
backup=Path(sys.argv[1])/'building-fbx';backup.mkdir()
labels={'PLA_Lenina_8','PLA_Lenina_7','PLA_SAT_S_Block','PLA_Shkolnaya_4','PLA_Shkolnaya_6'}
for b in json.load(open('assets/buildings/buildings_manifest.json')):
 if b['label'] in labels:
  for name in (b['mesh'],b.get('glass_mesh')):
   if name and (source:=Path('assets/buildings')/(name+'.fbx')).exists():shutil.copy2(source,backup/source.name)
PY
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_buildings.py -- "$PWD" PLA_Lenina_8 PLA_Lenina_7 PLA_SAT_S_Block PLA_Shkolnaya_4 PLA_Shkolnaya_6 > "$LOGS/buildings.log" 2>&1
grep -q 'BUILDINGS OK' "$LOGS/buildings.log"
python3 tools/research/neighbourhood_update.py
python3 tools/research/power_update.py
python3 -I tools/research/town_map_data.py design/research/data/blockout-2026-11-07.json assets/buildings/buildings_manifest.json Content/Kadykchan/Data/TownMap.json
python3 -I tools/research/story_data.py
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_vegetation.py -- "$PWD" > "$LOGS/vegetation.log" 2>&1
grep -q 'VEGETATION OK' "$LOGS/vegetation.log"
python3 tools/research/verify_neighbourhood.py > "$LOGS/verification.txt"
REPORT="$PWD/tools/editor/refresh_neighbourhood_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "$LOGS/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE_ROOT/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_neighbourhood.py" -unattended > "$LOGS/unreal.log" 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && [[ "$(tail -1 "$REPORT")" == 'RESULT OK' ]] || { print 'Import fehlgeschlagen: tools/editor/refresh_neighbourhood_report.txt';exit 1; }
print 'Wald, Höfe und fünf Wohnhäuser mit mehreren eingerichteten Etagen aktualisiert.'
