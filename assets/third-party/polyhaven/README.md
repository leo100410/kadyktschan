# Oberflächen von Poly Haven

Vom Nutzer am 2026-11-09 erlaubt: fertige Assets für Saal, Umgebung und Wege.

| Asset | Verwendung | Original |
|---|---|---|
| Gravel Road | Feld- und Fußwege | https://polyhaven.com/a/gravel_road |
| Asphalt 02 | verwitterte Asphaltstraßen; Feld- und Fußwege bleiben Kies | https://polyhaven.com/a/asphalt_02 |
| Forest Floor | unregelmäßige Laub-/Erdinseln neben Wegen | https://polyhaven.com/a/forest_floor |
| Wood Floor | Holzböden im Saal und den bereits eingerichteten Gebäuden | https://polyhaven.com/a/wood_floor |

Lizenz: **CC0 1.0**, siehe https://polyhaven.com/license . Die offizielle Lizenzseite und die drei Assetseiten wurden am 2026-11-09 geprüft. Es handelt sich um eigenständige PBR-Materialien; historische Referenzfotos werden weiterhin nicht als Texturen verwendet.

`python3 tools/research/fetch_surfaces.py` lädt für die vier Oberflächen jeweils Diffuse, DirectX-Normalen und Roughness als 2K-JPEG herunter. `downloads.json` hält anschließend die tatsächlichen Download-URLs und SHA-256-Werte fest. Diese Dateien werden vom prozeduralen Textur-Neuaufbau nicht überschrieben. Weiße Markierungen und große Schäden stammen aus dem eigenen RoadWear-Atlas, nicht aus einer Behauptung über historisch belegte Fahrbahnmarkierungen.

Noch kein Download-/Importnachweis allein durch das Vorhandensein dieser README. Der Aktualisierungsbericht muss den tatsächlichen Import bestätigen.
