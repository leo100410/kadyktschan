"""Refresh only tree/bush prototypes and instance lists; retain grass and all existing town props."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_vegetation as veg

root = Path(veg.ROOT)
veg.bpy.ops.wm.read_factory_settings(use_empty=True)
scatter = json.loads((root / "assets/vegetation/scatter.json").read_text())
path = root / "assets/vegetation/veg_manifest.json"
manifest = json.loads(path.read_text())
manifest["layers"] = veg.build_layers(scatter)
path.write_text(json.dumps(manifest, indent=1))
print("NATURE MESHES OK", len(manifest["layers"]), "layers")
