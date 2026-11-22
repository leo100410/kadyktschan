#!/bin/zsh
# Refresh furnished rooms without rebuilding terrain, vegetation or the map. Close Unreal first.
set -euo pipefail
cd "${0:A:h}/.."
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
PYTHON="/Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13"
UE="/Users/Shared/Epic Games/UE_5.8/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
python3 tools/asset-pipeline/test_furniture.py
KDK_TEX_ONLY=Fabric_A,Veneer_A "$PYTHON" tools/asset-pipeline/gen_textures.py assets/textures
mkdir -p Saved/InteriorUpdateLogs
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/build_buildings.py -- "$PWD" \
  PLA_Lenina_8 PLA_Lenina_7 PLA_SAT_S_Block PLA_OSM_170991713 PLA_Shkolnaya_8 \
  > Saved/InteriorUpdateLogs/blender.log 2>&1
grep -q 'BUILDINGS OK 5' Saved/InteriorUpdateLogs/blender.log
# A fresh report distinguishes a completed import from Unreal's known crash on exit.
REPORT="$PWD/tools/editor/refresh_interiors_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "Saved/InteriorUpdateLogs/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_interiors.py" -unattended \
  > Saved/InteriorUpdateLogs/unreal.log 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && grep -qx 'RESULT OK' "$REPORT" || { print 'Import fehlgeschlagen: Saved/InteriorUpdateLogs/unreal.log und tools/editor/refresh_interiors_report.txt prüfen.'; exit 1; }
print 'Inneneinrichtung aktualisiert. Spiel über den normalen Startknopf öffnen.'
