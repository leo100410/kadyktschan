# HANDOFF — Kadyktschan (Stand 2026-11-07, Ende Sitzung 1)

Ausführlicher Pipeline-/Feature-Stand: `production/session-state/handoff-2026-11-07.md`. Diese Datei hier ist der Einstieg.

## 1. Zuletzt konkret bearbeitet (Ist-Zustand, kompiliert, NICHT im Spiel getestet)
Einstellungsmenü der Videokamera (`Source/Kadyktschan/KadyktschanPlayerController.cpp::UpdateCamcorder`, `SKdkSettingsMenu.cpp`,
`KdkGameUserSettings.h`): Regler „Stärke (Videokamera)“ (`CamNoise`, skaliert Sättigung/Kontrast/Farbstich/Korn/Farbsäume/Vignette/Bloom;
75 % = Standard), Verpixelungs-Fix (TSR aus während Verpixelung; `r.ScreenPercentage` mit Code-Priorität zurücksetzen und solange keine
Verpixelung aktiv ist alle 0,5 s an den Auflösungsregler angleichen), Nebel-Regler (`FogAmount`, im `AKdkSkyCycleActor`), Menü merkt Scrollposition.

## 2. Letzte gültige Anweisung des Nutzers
„Füge noch einen Rausch-Slider für die Kamera hinzu“ → präzisiert: der Regler soll **den ganzen Videokamera-Effekt** stärker/schwächer machen. Erledigt.
Davor (weiter gültig): Grafik/Assets vor Mechanik/Story; Zielbild `design/art/atmosphere-target.md` inkl. Nachtrag (grüner, aufgelockerte
Wolken wie echte Fotos); „weniger eckig“; leicht unheimlich, **ohne Horror-Klischees**.

## 3. Wichtige Entscheidungen (Begründung jeweils in `production/decision-log.md`)
- Nur Zustand „verlassen 2011“, Sommer; 1:1 nach OSM; fehlende Gebäude aus Satellitenbildern (Google/Apple, nur Referenz) als **ANNAHME** in `design/research/data/satellite-additions-2026-11-07.json`.
- Alles prozedural (Blender-CLI + Editor-Python), kein Hand-Asset; Fotos nie als Textur.
- Nanite für Gebäude aus (Mac-Artefakte), HW-Raytracing standardmäßig aus (Leistung MacBook Air).
- Platzierung immer über `tools/research/terrain_mesh.py` (Rohe DEM-Werte ließen Objekte schweben).
- Verfallsstufen 0–3 statt einheitlicher Details (Nutzerwunsch: unterschiedlich heruntergekommen).
- Rost braun-grau statt rot (rot wirkte wie Blut = Horror-Klischee).
- Einstellungen als Slate-Menü in C++ (`UKdkGameUserSettings`), Dämmerung/Videokamera/Helligkeit/Nebel als Regler.

## 4. Verworfene Alternativen
- Komplett bedeckter, grauer Himmel (erstes Zielbild) → Nutzer wollte nach echten Fotos grüner/heller.
- Offener Kriechraum auf Pfählen → wirkte „schwebend“; jetzt geschlossener Sockel (ANNAHME).
- Blechvordach auf Stangen → wirkte wie Baustelle; jetzt Betonplatte.
- Kreisrunde Putzflecken (explizite Blobs) → künstlich; zurück zu Rauschen mit Exponent 1,25.
- Videokamera blaugrün → Nutzer: „zu blau“; jetzt neutral-warm.
- Verpixelung nur über `r.ScreenPercentage` → TSR glättete es weg.
- Volumetric Clouds entfernt → später wieder eingeführt (echte Fotos).

## 5. Konventionen / Muster
- Deutsch, einfache Sprache gegenüber dem Nutzer. Achsen: UE +X Nord, +Y Ost, cm; Daten in Metern (east_m/north_m).
- Neue Werte zentral als Tabellen/Konstanten oben im Skript (z. B. `DECAY`, `FOG`, `POST`); Palette nur in `tools/asset-pipeline/palette_2011.json` (sRGB-Hex).
- Jede Textur mit eigenem Seed (`seed(name)` in `gen_textures.py`). Material-Verbindungen über `connect()` (bricht bei falschem Pin ab).
- Neue Materialslots müssen in `SLOT_MI` (`place_buildings.py` bzw. `place_vegetation.py`) eingetragen werden, sonst Abbruch.
- Jede Entscheidung → `production/decision-log.md`; Belegbilder → `production/qa/evidence/2026-11-07-*.png`.
- Editor: `-unattended`, danach `pkill -f CrashReportClient`; Reports `tools/editor/*_report.txt` müssen `RESULT OK` enden.

## 6. Nicht ohne Rückfrage ändern
- **Keine Commits, Resets, Bereinigungen oder sonstigen Git-Änderungen** (ausdrückliche Anweisung).
- Kreative Richtung (Zielbild, Ethik: keine realen Opfer 1996 namentlich, Gulag nicht verharmlosen/ausschlachten, keine Monster/Jump-Scares).
- Erfundene Gebäude ohne Beleg; Löschen von Daten/Assets des Nutzers; Mechanik/Story beginnen (zurückgestellt).

## 7. Arbeitsverzeichnis und Voraussetzungen
- Starten in `/Users/leolange/UnrealProjects/Kadyktschan` (Hooks/CCGS laden nur dort). UE 5.8.4 unter `/Users/Shared/Epic Games/UE_5.8`, Blender 5.2 (`blender` im PATH), Xcode-Toolchain.
- Python mit numpy, tifffile, imagecodecs (altes venv im Session-Scratchpad, evtl. weg → neu anlegen). DEM-Kacheln N62/N63 × E146/E147 (Quelle in der Detail-Übergabe §3).
- C++ bauen: `"/Users/Shared/Epic Games/UE_5.8/Engine/Build/BatchFiles/Mac/Build.sh" KadyktschanEditor Mac Development -Project="$PWD/Kadyktschan.uproject" -WaitMutex`.

## 8. Vorhandene Änderungen / was erhalten bleiben muss
- Git ohne einzigen Commit: **das gesamte Arbeitsverzeichnis ist uncommitteter Stand** und muss erhalten bleiben. Fremde Änderungen sind nicht erkennbar,
  außer: `Saved/Config/MacEditor/GameUserSettings.ini` enthält Einstellungen des Nutzers (z. B. Maus 0,3) — nicht überschreiben.
- `~/Desktop/Kadyktschan.app` + `tools/play.sh` (Start für den Nutzer). Alte Kopie `~/Documents/Unreal Projects/Kadyktschan` ist veraltet (nicht löschen ohne Zustimmung).

## 9. Nächste Schritte (priorisiert)
1. Fehlende Einträge im `production/decision-log.md` nachtragen (Videokamera neutral, Verpixelungs-Fix, Nebel-Regler, Scrollposition, Stärke-Regler).
2. Im Spiel prüfen: Videokamera-Einblendung „REC/CAMERA 01“, Regler, Dämmerung, Wandbild am Kulturhaus, Knarr-Klang.
3. Leistung: Cull-Distanzen/HLOD für ~970 000 Vegetations-/Requisiten-Quads (Mac 20–27 FPS).
4. „Weniger eckig“: Requisiten (Fässer, Zäune, Büste, Ruinen) mit echten Formen/Bevel in Blender; abgeschlagene Hausecken; mehr eingestürzte Dachbereiche (Nutzervideo).
5. Danach mit dem Nutzer: Phase-3-Freigabe, erster Commit (nur auf Anweisung), Mechanik/Story.

## 10. Zuerst lesen (Reihenfolge)
1. `HANDOFF.md` (diese Datei) — Überblick, Regeln, nächste Schritte.
2. `production/session-state/handoff-2026-11-07.md` — Pipeline-Tabelle, Features, Hilfsmittel.
3. `design/art/atmosphere-target.md` — verbindliches Zielbild des Nutzers.
4. `production/decision-log.md` — nur bei Bedarf per Suche (lang); begründet jede Abweichung.
5. `CLAUDE.md` / `project.yaml` — Projektregeln (CCGS), Befehle. Weitere Doku nur gezielt, nicht das ganze Repo.

## 11. Prüfung dieser Übergabe / Lücken
- Ist-Zustand und Pläne sind getrennt (§1/§8 Ist, §9 Plan). Überholt: `production/phase-reports/phase-3-vertical-slice.md` (veraltet), ältere Einträge in
  `production/session-state/active.md` (Chronik, nicht maßgeblich), Art-Bible-Lichtangaben (durch Zielbild-Nachtrag ersetzt).
- **Nicht vollständig gesichert:** Die letzten Videokamera-/Regler-Änderungen sind nur kompiliert, nicht getestet und nicht im Entscheidungslog. Wegen
  knappen Kontexts wurde der Chatverlauf nicht noch einmal komplett gegengelesen; Details früherer Iterationen stehen nur im Entscheidungslog.
