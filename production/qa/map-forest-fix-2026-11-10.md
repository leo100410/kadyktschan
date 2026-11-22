# Karten und Waldsichtweite — 2026-11-10

Status: Quelländerungen und Kartendaten vorbereitet. Echte Unreal-Ansicht, vollständiger Build/Link und Asset-Import noch offen.

## Karten

- Fehlerursache: Namen wurden im Slate-Zeichencode nach unten versetzt, ohne Linie zurück zum Gebäude. Die Beschriftungen konnten zudem untereinander kollidieren.
- Stadtkarte mit K/Tab: feste Namensliste nach Nummern; Nummern stehen am Gebäude oder sind bei Platzmangel durch eine Linie mit dessen exaktem Punkt verbunden. Nummernkreise überschneiden sich nicht. Kartengrafik wird auf die Zeichenfläche begrenzt, damit Straßen nicht unter die Liste oder Überschrift laufen. Hintergrund deckend gegen durchscheinende Missionsanzeige.
- Zusätzlicher Knopf ganz oben in den Einstellungen: „Einrichtungskarte öffnen“. Vergrößerter Ausschnitt für die fünf ausgebauten Wohnhäuser, genaue offene Eingänge, Etagenliste mit linker/rechter Wohnung. Nummerierung der bisherigen Stadtkarte bleibt erhalten.
- Zurück-Knopf und Esc/M/K/Tab kehren in die weiterhin pausierten Einstellungen zurück. Mausfokus wird an das Menü zurückgegeben.
- Kartendaten nutzen den tatsächlichen Abschnittsrahmen der eingerichteten Gebäudesektion. Bei Orlow war die bisherige Annahme `entrances[len/2]` ein anderer Eingang als der tatsächlich ausgebaute. Stadtkarte und Mission zeigen nun auf denselben offenen Eingang.
- Quelle und Platzierung der Details stammen aus dem aktuellen Gebäudemanifest und residential.HOUSES; keine erfundenen zusätzlichen Wohnungen in der Kartenbeschreibung.

## Ferne Vegetation

- Lärchen hatten bereits keine feste Entfernungsabschaltung. Die bisherigen Fernmodelle reduzierten jedoch auf acht Blattkarten; dadurch sank deren Gesamtblattfläche deutlich.
- LOD-Kartenanteile jetzt 1 / 0,33 / 0,16, Blattgrößen 1 / 1,8 / 2,6. Fernkronen behalten ungefähr die Blattfläche naher Bäume, mit deutlich weniger Geometrie.
- Birken bis 4,5 km statt 2,5 km, junge Lärchen bis 3 km statt 1,5 km, Weiden bis 1,8 km und Erlen bis 2,2 km. Lärchen weiterhin ohne feste Abschaltdistanz.
- foliage.MinimumScreenSize auf 0,0000001 statt Engine-Standard 0,000005; kleine ferne Instanzen werden später verworfen.
- Für die vier Blattatlanten wird Alpha-Flächenerhalt bei kleinen Texturstufen aktiviert. Ohne diese Einstellung kann das Verkleinern eine Blattmaske unter die Ausschnittsschwelle mitteln. Einstellung zentral für bestehende Assets und künftige Importe in foliage_materials.py.
- Keine neuen Baumpositionen oder Wohnungen in diesem Update. Es aktualisiert die Darstellung des zuletzt importierten Ausbaus (292.188 Pflanzen).

## Prüfungen

- C++-Compilerprüfung mit den echten vorhandenen Unreal-Response-Dateien/Engine-Headern für SKdkTownMap, SKdkSettingsMenu, PlayerController und neue Kartentests: alle erfolgreich. `-fsyntax-only`, ausdrücklich kein Link/kompletter UBT-Build. Protokolle: Saved/map-check-*.log.
- Originale Marker-Anordnungsfunktion separat mit clang++ ausgeführt: Cluster mit 5, 11 und 30 Punkten bleiben in der Fläche und die Nummernkreise kollidieren nicht.
- Vier neue Offline-Tests für tatsächliche Etagen-/Eingangsdaten, Orlows Missionsziel, Alpha-Mip-Einstellungen sowie Kronenfläche und Detailreduktion. Drei bestehende Nature-Tests bestanden.
- Zwei Unreal-Automationstests ergänzt (Marker-Anordnung und Detaildaten/Neuladen); kompiliert, hier noch nicht in Unreal ausgeführt.
- Python-Syntax und Shell-Syntax geprüft. Sichtwirkung, Menübedienung und Bildrate bleiben im Spiel zu prüfen.
- Vorher-Bild des Nutzers: evidence/2026-11-10-map-label-before.png.

## Aktualisierung

Spiel und Editor schließen; im normalen Terminal:

```sh
zsh /Users/leolange/UnrealProjects/Kadyktschan/tools/rebuild_map_forest.sh
```

Das Skript aktualisiert Kartendaten und den zugehörigen Missions-Eingang, baut C++, erzeugt Baum-/Busch-Detailstufen und importiert nur die Foliage-Prototypen samt Instanzfeld. Blatttexturen und Assets werden vorher gesichert. Importbericht tools/editor/refresh_map_forest_report.txt muss mit RESULT OK enden; Protokolle unter Saved/MapForestLogs.

Danach K/Tab-Stadtkarte sowie Einstellungen → Einrichtungskarte öffnen prüfen, verschiedene Etagenlisten und Eingangspunkte ablaufen. Die Rückkehr ins Menü darf das Spiel nicht vorzeitig fortsetzen. Wald aus erhöhtem Blickwinkel und aus Spielerhöhe bei mehreren Entfernungen ansehen; Leistung messen. Mehr ferne Blattflächen/Instanzen können die Bildrate reduzieren.

Keine Git-Befehle und keine Änderung persönlicher GameUserSettings.


### 2026-11-11 — Dokumentation und Übergabeeinstieg aktualisiert
Nutzer fragt nach vollständiger Dokumentation für Claude Code. Entscheidungslog, aktive Chronik und QA-Berichte waren vorhanden; HANDOFF.md hatte jedoch weiterhin veraltete Status-/Auftragsangaben vom 2026-11-07. Aktuelle Übergabe production/session-state/handoff-2026-11-11.md erstellt und an den Anfang von HANDOFF.md sowie in CLAUDE.md verlinkt. Historie erhalten, überholte Einschränkungen von aktuellen Nutzeraufträgen unterschieden.
Aktuelle MapForest-Protokolle geprüft: C++ Succeeded, NATURE MESHES OK 28, Import RESULT OK (Backup 20261110-082516-873887), 292188 Instanzen. Das Update ist importiert; vollständige Spielabnahme und Bildratenmessung weiterhin offen. Keine Gameplay-/Assetänderung in diesem Dokumentationsschritt, keine Git-Befehle.
