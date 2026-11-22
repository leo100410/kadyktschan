#!/bin/zsh
# Run-and-observe evidence: start the game on the world map and save a screenshot after the world settled.
# Usage: tools/ingame_shot.sh <absolute png path> [delay seconds] [extra args, e.g. -KdkSkyTime=0.95]
# (uses the -KdkShot hook in AKadyktschanGameMode)
UE="${UE_ROOT:-/Users/Shared/Epic Games/UE_5.8}/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
"$UE" "$PWD/Kadyktschan.uproject" /Game/Kadykchan/Maps/Kadykchan_World -game -windowed -ResX=1280 -ResY=720 -unattended \
  -KdkShot="$1" -KdkShotDelay="${2:-10}" ${=3} > /dev/null 2>&1 &
PID=$!
for i in $(seq 1 60); do kill -0 $PID 2>/dev/null || break; sleep 5; done
kill $PID 2>/dev/null
pkill -f CrashReportClient  # UE 5.8 on macOS 27 crashes while quitting; the shot is written before that
[ -f "$1" ] && echo "shot: $1" || { echo "no screenshot written"; exit 1; }
