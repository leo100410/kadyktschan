"""Download the selected CC0 Poly Haven surfaces; no account or extra package required."""
import hashlib
import json
from pathlib import Path
import urllib.request
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ("gravel_road", "forest_floor", "wood_floor", "asphalt_02")
MAPS = ("diff", "nor_dx", "rough")


def valid_jpeg(data):
    return 1000 < len(data) <= 32 * 1024 * 1024 and data[:2] == b"\xff\xd8" and data[-2:] == b"\xff\xd9"


def main():
    out = ROOT / "assets/third-party/polyhaven"
    out.mkdir(parents=True, exist_ok=True)
    records = []
    for asset in ASSETS:
        for kind in MAPS:
            name = "%s_%s_2k.jpg" % (asset, kind)
            url = "https://dl.polyhaven.org/file/ph-assets/Textures/jpg/2k/%s/%s" % (asset, name)
            dest = out / name
            if not dest.exists():
                req = urllib.request.Request(url, headers={"User-Agent": "Kadyktschan asset pipeline"})
                with urllib.request.urlopen(req, timeout=45) as response:
                    data = response.read(32 * 1024 * 1024 + 1)
                if not valid_jpeg(data):
                    raise ValueError("download is not a supported JPEG: " + url)
                partial = dest.with_suffix(".part")
                partial.write_bytes(data)
                partial.replace(dest)
            data = dest.read_bytes()
            assert valid_jpeg(data), "invalid cached texture: " + str(dest)
            records.append({"file": name, "url": url, "source": "https://polyhaven.com/a/" + asset,
                            "license": "CC0-1.0", "sha256": hashlib.sha256(data).hexdigest()})
            print(name, len(data), flush=True)
    (out / "downloads.json").write_text(json.dumps(records, indent=2) + "\n")
    print("SURFACES OK", len(records))


if __name__ == "__main__":
    try:
        main()
    except (URLError, TimeoutError) as error:
        raise SystemExit("Download von Poly Haven fehlgeschlagen. Internetverbindung prüfen und den Befehl erneut starten. Details: " + str(error))
