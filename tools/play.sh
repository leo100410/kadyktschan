#!/bin/zsh
# Start the newest version of the game: compile changed C++ first (seconds when nothing changed), then run.
# Used by the desktop shortcut. -unattended hides the harmless crash dialog UE 5.8 shows on quit under macOS 27.
cd "${0:A:h}/.."
UE="/Users/Shared/Epic Games/UE_5.8/Engine"
"$UE/Build/BatchFiles/Mac/Build.sh" KadyktschanEditor Mac Development -Project="$PWD/Kadyktschan.uproject" -WaitMutex > Saved/play-build.log 2>&1 \
  || { osascript -e 'display alert "Kadyktschan" message "Kompilieren fehlgeschlagen, siehe Saved/play-build.log"'; exit 1; }
"$UE/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor" "$PWD/Kadyktschan.uproject" -game -unattended > /dev/null 2>&1 &
