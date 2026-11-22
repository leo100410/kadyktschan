"""Apply the hall/roads update in place, retaining the town layout and user settings."""
import datetime
from pathlib import Path
import shutil
import sys
import traceback
import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0, str(ROOT / "tools/editor"))
REPORT = ROOT / "tools/editor/refresh_environment_report.txt"
lines = []


def main():
    backup = ROOT / "Saved/EnvironmentUpdateBackups" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    paths = ["Content/Kadykchan/Materials/Scans", "Content/Kadykchan/Terrain", "Content/Kadykchan/Maps",
             "Content/__ExternalActors__/Kadykchan/Maps/Kadykchan_World"]
    paths += ["Content/Kadykchan/Materials/" + name + ".uasset" for name in ("MI_Road", "MI_Path", "MI_Int_FloorBoards", "MI_VergeScan")]
    for name in paths:
        source, dest = ROOT / name, backup / name
        if source.is_dir():
            shutil.copytree(source, dest)
        elif source.is_file():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
    lines.append("Backup: " + str(backup))
    import refresh_interiors
    import scanned_surfaces
    import place_ground
    refresh_interiors.LABELS = {"PLA_Yuzhnaya_9"}
    refresh_interiors.main()
    lines.extend(line for line in refresh_interiors.lines if line != "RESULT OK")
    scanned_surfaces.apply()
    place_ground.RIBBONS = [r for r in place_ground.RIBBONS if r[2] in ("Roads_Blockout", "Tracks_Dirt", "Paths_Footpaths", "Ground_VergeDetails")]
    assert len(place_ground.RIBBONS) == 4, "roads, tracks, paths or verge mesh missing"
    place_ground.main()
    lines.append("RESULT OK")


try:
    main()
except Exception:
    lines.append("RESULT FAILED\n" + traceback.format_exc())
finally:
    REPORT.write_text("\n".join(lines) + "\n")
    unreal.log_warning("\n".join(lines))
    unreal.SystemLibrary.quit_editor()
