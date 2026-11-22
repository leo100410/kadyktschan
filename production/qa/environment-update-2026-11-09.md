# Saal, Wege und Wegesränder – 2026-11-09

## Stand

Quellen umgesetzt, Geometrie offline erzeugt und geprüft. **Noch nicht in Unreal importiert.** Im Spiel gilt bis zum erfolgreichen neuen Import weiterhin der vorherige Stand.

Run result: NOT VERIFIED — der lokale Download scheitert an der Namensauflösung für dl.polyhaven.org; Blender/Unreal hatten in dieser Ausführungsumgebung bereits Startprobleme. Keine neue Spielaufnahme, kein Lauf- oder Leistungsnachweis. Der Nutzer bekommt einen zusammenhängenden Aktualisierungsbefehl für das normale Terminal.

## Umgesetzt

- Kulturhaus-Saal: geformte Holzlehnen und gepolsterte Klappsitze mit Metallgestell, einzelne hochgeklappte Sitzflächen, gefaltete Vorhangreste mit unregelmäßigem Saum, unregelmäßiger Putzschutt statt weißer Rechtecke, runder Kronleuchter mit Fassungen und Schirmen. Mittelgang und zusätzliche Querpassage zur Tür bleiben frei.
- Wege: deterministische Breitenvariation von höchstens acht Prozent; Höhen weiterhin ausschließlich vom gerenderten TerrainMesh. Bestehende Straßenverläufe und Eingänge bleiben die Grundlage.
- 120 Bodendetailflächen neben Straßen im Umkreis von 900 m, mit 0,5-m-Raster ans Gelände angepasst; 15360 Dreiecke, keine Kollision, keine Schatten. Keine neuen Gebäude, keine Rodung oder Veränderung der Hügel.
- Neue Oberflächen für Kieswege, Waldbodeninseln und Holzböden vorbereitet. Jeweils 2K-Farbe, DirectX-Normalen und Rauheit. Straßen und Bodendetails verwenden weltbezogene 2-m-Kacheln, damit breite Straßen keine riesigen gestreckten Kiesel zeigen. Ausgeschnittene unregelmäßige Ränder statt gerader Materialstreifen; Bodendetails werden rund begrenzt.
- Holz wird leicht entsättigt und matt gehalten. Die gemeinsame Holzfußboden-Instanz betrifft auch die bereits eingerichteten Häuser.
- Neuer Aktualisierungsbefehl sichert vorhandene Materialien, Gelände-Assets, Map und zugehörige externe Actors; der Kulturhaus-Mesh wird über den bestehenden, erfolgreich benutzten Innenraum-Importer ersetzt. Für neue Polster-/Emaille-Slots werden die vorhandenen Projektmaterialien benutzt.
- Regulärer Welt-Neuaufbau lädt die gewählten Oberflächen und stellt ihre Materialbelegung wieder her. Keine neue Bibliothek erforderlich.

## Fertige Materialien und Lizenz

Die offiziellen Poly-Haven-Assetseiten und Lizenzseite wurden geöffnet und geprüft:

- https://polyhaven.com/a/gravel_road – Kieswege
- https://polyhaven.com/a/forest_floor – Wegesränder
- https://polyhaven.com/a/wood_floor – Holzfußböden
- https://polyhaven.com/license – CC0 1.0, kommerzielle Verwendung und Weitergabe erlaubt.

Die ausdrückliche Nutzerfreigabe für fertige Assets gilt hier auch für diese eigenständigen PBR-Materialien. Historische Referenzfotos werden weiterhin nicht als Texturen benutzt.

**Die eigentlichen Texturdateien sind noch nicht heruntergeladen.** `fetch_surfaces.py` prüft Dateigröße und JPEG-Signatur, speichert erst nach erfolgreichem Download und legt danach `downloads.json` mit Quellen und SHA-256-Werten an. Kein `downloads.json` und kein erfolgreicher Unreal-Bericht dürfen als vorhanden behauptet werden, solange der Nutzerlauf fehlt.

## Prüfung

- `python3 tools/asset-pipeline/test_furniture.py`: 5/5 bestanden, einschließlich geschlossenem Saalmodell und freiem Mittelgang.
- `python3 tools/research/test_environment_assets.py`: 3/3 bestanden (Downloadsignaturen, Geländekontakt, aufwärts gerichtete Flächen, Mindestbreite).
- Neue Straßen-/Weggeometrie in temporäre Dateien erzeugt: 53 Straßenstreifen / 54128 Dreiecke; 118 Fußwege / 7552 Dreiecke.
- Bodendetails erzeugt: VERGES OK 120 patches 15360 triangles.
- Python-Syntax und zsh-Syntax geprüft.
- Vereinfachte Geometrievorschau angesehen: neue Sitzformen und Querpassage sind sichtbar. Beleg `production/qa/evidence/2026-11-09-hall-geometry-comparison.png` (oben vorher, unten nachher). **Kein Spielbild, keine Darstellung der noch nicht heruntergeladenen Scans.**
- Aktualisierungsskript startet die Prüfungen erfolgreich und stoppt vor dem Import beim Downloadfehler. Bestehende Spiel-Assets wurden hierbei nicht verändert.

## Übernehmen und anschließend prüfen

Unreal schließen, dann:

```sh
zsh "/Users/leolange/UnrealProjects/Kadyktschan/tools/rebuild_environment.sh"
```

Erwartet: SURFACES OK 9, BUILDINGS OK 1, abschließend tools/editor/refresh_environment_report.txt mit letzter Zeile RESULT OK. Danach Kulturhaus (Karte Nr. 7), Wege und Wegesränder ansehen; Mittelgang, Querpassage und Treppe laufen. Die neue Shaderdarstellung, endgültige Sitz-/Vorhangansicht und Bildrate sind noch nicht im Spiel verifiziert. Bei Problemen zuerst den frischen Bericht und Saved/EnvironmentUpdateLogs prüfen.

Kein Commit, keine Git-Befehle, keine Änderung der Nutzereinstellungen oder Story-Texte.

## Nachtrag: erster Nutzerlauf

Alle neun Poly-Haven-Dateien wurden heruntergeladen; SHA-256 stimmt mit downloads.json überein. Blender meldet BUILDINGS OK 1 und der Kulturhaus-Mesh wurde importiert. Anschließend Abbruch in scanned_surfaces.apply: invalid material pin: Input. Im installierten UE-Quellcode bestätigt: UMaterialGraphNode::GetShortenPinName wandelt Input in NAME_None um (MaterialGraphNode.cpp:610). Die beiden betroffenen Verbindungen verwenden jetzt den ersten Eingang über den leeren Namen. Der Außenbericht übernimmt außerdem kein zwischenzeitliches RESULT OK des Saal-Importers mehr. Erneuter Import und vollständiges RESULT OK stehen aus.

## Erfolgreicher Nutzerlauf, 2026-11-09 ~16:59

Frischer Bericht refresh_environment_report.txt endet mit RESULT OK. Backups: EnvironmentUpdateBackups/20261109-165839-798699 und InteriorUpdateBackups/20261109-165840-520573. Download, Kulturhaus-Import, Scanmaterialien sowie Straßen-, Fußweg- und Wegesrand-Import sind durchgelaufen. Endgültige Darstellung, Begehbarkeit und Leistung im Spiel sind noch nicht durch neue Spielbilder/Lauftests bestätigt.
