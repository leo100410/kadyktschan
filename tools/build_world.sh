#!/bin/zsh
# Rebuilds the playable world from source data, in dependency order. Run from the project root.
# Needs: Blender on PATH, UE 5.8 at UE_ROOT, a Python with numpy/tifffile/imagecodecs as PYTHON (for DEM/textures),
# and the two Copernicus DEM tiles in DEM_DIR (see production/phase-reports/phase-2-blockout.md).
set -e
UE_ROOT=${UE_ROOT:-"/Users/Shared/Epic Games/UE_5.8"}
UE="$UE_ROOT/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor"
PYTHON=${PYTHON:-python3}
DEM_DIR=${DEM_DIR:?set DEM_DIR to the folder with the Copernicus_DSM_COG_10_N63_00_E14{6,7}_00_DEM.tif tiles}
P="$PWD/Kadyktschan.uproject"
DEM=("$DEM_DIR"/*E146*.tif "$DEM_DIR"/*E147*.tif)

$PYTHON -I tools/research/dem_to_obj.py assets/terrain/terrain_kadykchan_8km.obj 4000 30 "${DEM[@]}"
$PYTHON -I tools/research/blockout_data.py design/research/data/osm-kadykchan-2026-11-07.json design/research/data/blockout-2026-11-07.json "${DEM[@]}"
T=assets/terrain/terrain_kadykchan_8km.obj
# horizon: needs the N62 tiles too (Copernicus_DSM_COG_10_N62_00_E14{6,7}_00_DEM.tif) for 30 km to the south
$PYTHON -I tools/research/dem_ring_obj.py assets/terrain/terrain_backdrop_60km.obj 30000 300 3950 "$DEM_DIR"/*.tif
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json roads assets/terrain/roads_kadykchan.obj $T
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json rivers assets/terrain/rivers_kadykchan.obj $T
$PYTHON -I tools/asset-pipeline/gen_textures.py assets/textures
$PYTHON -I tools/asset-pipeline/gen_audio.py assets/audio
blender --background --factory-startup --python tools/asset-pipeline/build_t5_kit.py -- "$PWD"
blender --background --factory-startup --python tools/asset-pipeline/build_buildings.py -- "$PWD"
python3 -I tools/research/lines_to_obj.py design/research/data/blockout-2026-11-07.json paths assets/terrain/paths_kadykchan.obj $T assets/buildings/buildings_manifest.json
$PYTHON -I tools/research/scatter_vegetation.py design/research/data/blockout-2026-11-07.json assets/vegetation/scatter.json "${DEM[@]}"
rm -f assets/vegetation/SM_Veg_*.fbx
blender --background --factory-startup --python tools/asset-pipeline/build_vegetation.py -- "$PWD"
# UE 5.8 on macOS 27 crashes while quitting (Slate teardown) after saving; -unattended suppresses the dialog
for step in build_materials build_blockout place_ground place_buildings place_vegetation place_audio apply_atmosphere; do
  "$UE" "$P" -ExecutePythonScript="$PWD/tools/editor/$step.py" -unattended > /dev/null 2>&1 || true
  echo "$step: $(tail -1 tools/editor/${step}_report.txt)"
  grep -q "RESULT OK" tools/editor/${step}_report.txt || { cat tools/editor/${step}_report.txt; exit 1; }
done
