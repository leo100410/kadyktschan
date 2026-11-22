"""Refresh streets and instanced vegetation, leaving buildings and other placed props in place."""
import datetime
from pathlib import Path
import shutil
import sys
import traceback
import unreal

ROOT = Path(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_dir()))
sys.path.insert(0, str(ROOT / "tools/editor"))
REPORT = ROOT / "tools/editor/refresh_streets_nature_report.txt"
lines = []


def main():
    backup = ROOT / "Saved/StreetsNatureAssetBackups" / datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    paths = ["Content/Kadykchan/Materials", "Content/Kadykchan/Terrain", "Content/Kadykchan/Vegetation/Generated",
             "Content/Kadykchan/Maps", "Content/__ExternalActors__/Kadykchan/Maps/Kadykchan_World"]
    for name in paths:
        source = ROOT / name
        if source.is_dir():
            shutil.copytree(source, backup / name)
    lines.append("Backup: " + str(backup))
    import scanned_surfaces
    import foliage_materials
    import place_ground
    import place_vegetation
    scanned_surfaces.apply()
    foliage_materials.apply()
    place_ground.RIBBONS = [r for r in place_ground.RIBBONS if r[2] in ("Roads_Blockout", "Tracks_Dirt", "Paths_Footpaths", "Ground_VergeDetails")]
    assert len(place_ground.RIBBONS) == 4, "one of the street/ground meshes is missing"
    place_ground.main()
    place_vegetation.main(only_foliage=True)
    lines.extend(place_ground.log_lines)
    lines.extend(place_vegetation.log_lines)
    lines.append("RESULT OK")


try:
    main()
except Exception:
    lines.append("RESULT FAILED\n" + traceback.format_exc())
finally:
    REPORT.write_text("\n".join(lines) + "\n")
    unreal.log_warning("\n".join(lines))
    unreal.SystemLibrary.quit_editor()
