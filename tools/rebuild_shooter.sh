#!/bin/zsh
# Shooter mode "Einsatz" (design/gdd/shooter-mode.md): data, meshes, sounds and their import. Close the game/editor
# first. Only new assets under /Game/Kadykchan/Shooter are written; the world map is not touched.
# PYTHON must have numpy (sounds), e.g. PYTHON=/path/to/venv/bin/python tools/rebuild_shooter.sh
set -euo pipefail
cd "${0:A:h}/.."
UE_ROOT="/Users/Shared/Epic Games/UE_5.8/Engine"
BLENDER="${BLENDER:-blender}"
PYTHON="${PYTHON:-python3}"
if pgrep -f '[U]nrealEditor.*Kadyktschan.uproject' > /dev/null; then
  print 'Bitte Kadyktschan und den Unreal Editor zuerst schließen, dann den Befehl erneut starten.'
  exit 1
fi
LOGS="Saved/ShooterLogs"
mkdir -p "$LOGS"
python3 tools/research/test_shooter.py > "$LOGS/data.log" 2>&1 || { print 'Datenprüfung fehlgeschlagen: Saved/ShooterLogs/data.log'; exit 1; }
"$BLENDER" --background --factory-startup --python-exit-code 1 --python tools/asset-pipeline/shooter_props.py -- "$PWD" > "$LOGS/props.log" 2>&1
grep -q 'SHOOTER MESHES OK' "$LOGS/props.log"
"$PYTHON" -I tools/asset-pipeline/shooter_audio.py assets/shooter/audio > "$LOGS/audio.log" 2>&1
grep -q 'SHOOTER AUDIO OK' "$LOGS/audio.log"
"$UE_ROOT/Build/BatchFiles/Mac/Build.sh" KadyktschanEditor Mac Development -Project="$PWD/Kadyktschan.uproject" -WaitMutex > "$LOGS/build.log" 2>&1 || { print 'Build fehlgeschlagen: Saved/ShooterLogs/build.log'; exit 1; }
REPORT="$PWD/tools/editor/refresh_shooter_report.txt"
[[ ! -f "$REPORT" ]] || mv "$REPORT" "$LOGS/import-$(date +%Y%m%d-%H%M%S).txt"
"$UE_ROOT/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/Kadyktschan.uproject" -ExecutePythonScript="$PWD/tools/editor/refresh_shooter.py" -unattended > "$LOGS/unreal.log" 2>&1 || true
pkill -f CrashReportClient || true
[[ -f "$REPORT" ]] && [[ "$(tail -1 "$REPORT")" == 'RESULT OK' ]] || { print 'Import fehlgeschlagen: tools/editor/refresh_shooter_report.txt'; exit 1; }
print 'Einsatz-Modus: Daten, Modelle und Geräusche aktualisiert.'
