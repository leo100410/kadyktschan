# Entscheidungslog (autonome Arbeit)

Ab 2026-11-07 ~01:30 arbeitet die KI ohne Rückfragen (Nutzer schläft, Auftrag: selbst entscheiden,
so viel wie möglich bauen). Jede Entscheidung mit Grund, damit sie morgen geprüft oder
zurückgenommen werden kann.

| Zeit | Entscheidung | Grund | Rücknahme |
|---|---|---|---|
| 01:30 | Keine Commits | Nutzer hat Commit zurückgestellt | – |
| 01:35 | Häuser werden in Blender aus den Kit-Teilen zu **einem Mesh pro Adresse** zusammengesetzt (statt ~900 Actors pro Haus in Unreal) | schneller, ohne Editor prüfbar, L-Grundrisse möglich; Packed Level Actor (Briefing V4) wäre zur Laufzeit gleichwertig. Vorerst StaticMeshActor `PLA_<Adresse>` in der Welt | Packen zu PLA/Level-Instanz, sobald Innenräume dazukommen |
| 01:35 | Grundriss = OSM-Polygon gerastert auf 3-m-Achsen; Rechteck-Grundrisse (≤ 4 Ecken) bekommen 12 m Tiefe (ANNAHME), L-Formen folgen dem Polygon | OSM-Tiefen 15–24 m sind für Plattenscheiben unplausibel | Tiefe in `kit_grid.json` |
| 01:35 | Alle Gebäude mit Adresse (2–9 Geschosse) bekommen den Platten-Kit; Industriebauten ohne Adresse bleiben Quader | Typenserien unbekannt (ANNAHME); sichtbarer Fortschritt für die ganze Stadt | eigene Kits je Typ-Klasse später |
| 01:35 | Eingangstreppe (6 Stufen + Podest) und Dachlüfter ergänzt; Laufspuren der Putztextur abgeschwächt | Tür hing 1,65 m in der Luft (Pfahlgründung); Fotos zeigen Treppen und Dachaufbauten | – |
| 01:50 | Alle 34 Adressen als Plattenbau-Meshes (Blender, `build_buildings.py`), Industrie bleibt Quader | sichtbarer Gesamtstand der Stadt | – |
| 01:55 | Fassadenfarben je Haus deterministisch aus 6 Schemata (Mint/Rosa, Kalk, Beton …), Lenina 8 fix Mint/Rosa nach Foto 6480312099 | Fotos zeigen gemischte Farben; Zuordnung pro Haus unbelegt (ANNAHME) | `SCHEMES` in `build_buildings.py` |
| 02:00 | Eingänge nur an Längsseiten, auf der Seite zur Stadtmitte, alle 9 Achsen ab Achse 3 | Plattenbau-Sektionen; Giebel ohne Eingänge (Fotos) | – |
| 02:05 | `M_Master_Ground` mit Tundra-Grün/Trocken, Schotter-Straßen, dunkler Fluss (Palette um Vegetationsfarben ergänzt, Farbton 80–100°) | Art Bible 4.1/8.6 | – |
| 02:10 | Vegetation: 420 Birken (6–30 m von Fassaden), 1 500 Zwergsträucher, 2 600 Lärchen (dichter nach außen und an Hängen), Blattkarten maskiert, kein Nanite, keine Kollision, 600-m-Zellen | Briefing V3 Schritt 4, Art Bible 8.7/8.8 | `scatter_vegetation.py` |
| 02:15 | C++-Hook `-KdkShot=<png>` im GameMode für Belegbilder aus dem laufenden Spiel; Blick wird waagerecht gestellt (macOS-Cursor verdreht sonst die Kamera) | `run-and-observe.md` verlangt Bilder aus dem Spiel; `-ExecCmds` feuert zu früh | `tools/ingame_shot.sh` |
| 02:15 | Spielerstart vor dem mittleren Eingang von ул. Ленина 8 (wird neu erzeugt statt verschoben) | verschobener WP-Actor wurde nicht gespeichert | – |
| 02:25 | Innenräume zuerst nur für die mittlere Eingangssektion von ул. Ленина 8 (Erdgeschoss): Treppenhaus + 2 gespiegelte Wohnungen mit allen V5-Pflicht-Requisiten | PDF-Phase 3 „ein Block, zwei Wohnungen“; Spieler startet dort | `INTERIOR_SECTIONS` in `build_buildings.py` |
| 02:25 | Wohnungsgrundriss: Zimmer + Küche zur Fassade, Flur + Bad hinten (ANNAHME) | Typengrundrisse unbelegt (Dossier Frage 2) | `interiors.py` |
| 02:25 | Zimmerboden Dielen statt Fischgrät-Parkett (Wohnung A), Linoleum (B) | Fischgrät-Muster als kachelnde Prozedurtextur noch nicht gelöst; PDF V6 nennt Fischgrät | Textur `Planks_A` ersetzen |
| 02:30 | Hausnummern als Text-Geometrie (Blender-Standardschrift, Kyrillisch) über dem ersten Eingang, Schreibweise wie Foto „ЛЕНИНА 18“ (Genitiv, ohne „ул.“) | Art Bible 7 / Briefing V4 „Hausnummern als Decals, Original-Kyrillisch“; Geometrie statt Decal spart eine Decal-Pipeline | später echte Decals, Muttersprachler-Prüfung offen |
| 02:40 | Fensterglas transluzent (`M_Master_Glass`) statt dunkler Platzhalter | Platzhalter war undurchsichtig, Wohnungen blieben schwarz | – |
| 02:58 | Nanite für die Gebäude-Meshes aus | transluzentes Glas im selben Mesh → Nanite rendert das Ersatz-Mesh, Rahmen zerfallen zu Splittern; Gebäude sind ohnehin nur 15–80 k Dreiecke | Glas als eigenes Nicht-Nanite-Mesh exportieren, dann Nanite wieder an (Art Bible 8.7) |
| 03:10 | Glas je Gebäude als eigenes Mesh (`SM_Bld_*_Glass`, ohne Nanite), Gebäude wieder mit Nanite | löst den 02:58-Kompromiss, Art Bible 8.7 | – |
| 03:10 | 15 % der Fenster ohne Rahmen (ausgebaut), Glas nur in vorhandenen Rahmen; Erker-Säulen an ул. Ленина 8 (Achsen 9 und 18 der Straßenseite, rosa) | Art Bible 6 Verfall; Foto 6480312099 (Lage der Erker ANNAHME) | `FRAME_MISSING`, `BAYS` |
| 03:40 | Nanite für Gebäude doch aus (Glas bleibt getrennt) | auch nach sauberem Re-Import und Fallback-Fehler 0 zerlegt Nanite auf diesem Mac dünne Teile zu Splittern; Blender-Render der Geometrie ist korrekt | auf Windows + RTX erneut testen, dann `enabled` in `place_buildings.py` |
| 03:40 | Wandbild (Figur im Pelzmantel + springendes Rentier) auf dem Giebel von ул. Мира 1, Haus in Mint | Foto 6480317815 / Briefing R3; welches 9-Geschoss-Haus es ist, ist ANNAHME; stilisiert, keine Fotokopie | `GABLE_MURALS` |
| 04:05 | Kulturhaus in ул. Южная 9 (U-Grundriss), Saal 24 × 15 m doppelt hoch an der Straße: Bleiglas (blau/rot/türkis, 30 % Scheiben zerbrochen), roter Fries, Bühne mit Portal und Vorhangresten, Klappstuhlreihen (30 % fehlen, 15 % umgekippt), Zugang über Flur vom Hofeingang | Briefing V10 Priorität A, Fotos R4; Gebäude unbelegt (ANNAHME) | `KULTURHAUS` in `build_buildings.py` |
| 04:05 | Korrektur: Hausnummern und Wandbild nicht spiegeln | FBX-Import erhält die sichtbare Händigkeit (am Wandbild nachgewiesen); vorher waren die Hausnummern spiegelverkehrt | – |
| 04:25 | Straßenausstattung: Fernwärme-Doppelrohre auf Betonstützen 5 m neben den Stadtstraßen (≤ 700 m vom Zentrum), Schutthaufen an den Längswänden, 2 Rosttanks je großem Industriebau, 8 Blechgaragen am Südrand; eigene `SM_Props_*`-Zellen mit Kollision | Briefing V3 Schritt 4, V10 C; Lagen ANNAHME (oberirdische Fernwärme ist für Permafrost-Städte typisch, für Kadyktschan unbelegt) | `scatter_vegetation.py` |
| 04:35 | Loggien (eingelassene Balkone, Kalk-Brüstung) an ~50 % der Wohnblocks, jede 3./4. Achse der Straßenseite | Foto 6480281023; Fassadenvielfalt; Verteilung ANNAHME | `loggia_cells` in `build_buildings.py` |
| 04:35 | 8 m um jeden Hauseingang ohne Bäume | Spielerstart stand vor einem Birkenstamm | – |
| 04:40 | Klang: prozedurale Wind-Loop (2D, überall) und Tropfen (3D, Treppenhaus, Wohnung B, Kulturhaus) als SoundWave in AmbientSound | Briefing V7; MetaSounds per Skript ungeprüft; Hunde/Radio bewusst weggelassen (Synthese klingt schlechter als Stille) | auf MetaSound-Quelle umstellen |
| 04:45 | Schadensstufen: 1 = herausgebrochene Platten (6 % der Felder, Brocken darunter), 2 = eingestürzte Ecke über 1–3 Geschosse mit Schuttkegel; Wahrscheinlichkeit 10 % (Wohnblock) / 20 % (2-geschossig), nie bei Lenina 7/8, Mira 1, Kulturhaus | Art Bible 8.3 `_Ruin`, Wikipedia „major buildings were blown up“, Fotos 2011; Verteilung ANNAHME | `NO_COLLAPSE`, `PANEL_LOSS` |
| 04:55 | Himmels-Zyklus in C++ (`AKdkSkyCycleActor`, `DA_SkyCycle`): Sonne läuft in 90 min von 40° Süd / 5800 K zur Weißnacht 4° Nord / 4500 K, Smoothstep; 4 Unit-Tests grün | Nutzer-Entscheidung „Zeit läuft langsam“; Art Bible 2 (A1/A2); Coding Standards (datengetrieben, testbar) | Werte in `DA_SkyCycle` |
| 04:55 | `commands.test/run/smoke` für macOS in `project.yaml` eingetragen (vorher TODO) | auf UE 5.8.4 geprüft | `/settings` |
| 05:00 | Laden „МАГАЗИН“ im Erdgeschoss von ул. Школьная 3 (rosa Erdgeschoss = Ladenfront laut Art Bible 4.1) mit Theke, Waage, Kasse, Regalen, Schild | Briefing V10 B „Läden“; Lage ANNAHME | `INTERIOR_SECTIONS` |
| 05:20 | Weißnacht-Ende: 6° Sonnenhöhe, **6500 K** (Art Bible 2 nennt 4300–4800 K) | mit 4° / 4500 K wirkte das Licht gesättigt orange statt „golden-blass“; die Atmosphäre färbt die tiefe Sonne schon golden, neutrale Lichtfarbe ergibt den blassen Ton (Belegbild verglichen) | Werte in `DA_SkyCycle` (maßgeblich) / `KdkSkyCycle.h` |
| 05:40 | Hofausstattung: 134 Betonlaternen (alle 35 m an Wohnstraßen, Gegenseite der Rohre), Bänke an 45 % der Eingänge, 6 Spielplätze (Klettergerüst + Schaukelgestell, Stahlrohr, Rost) | typischer Mikrorayon, Briefing V8 „echte Straßen“; Lagen ANNAHME | `scatter_vegetation.py` |
| 05:55 | Satteldächer (30°, 0,5 m Überstand, graues Wellasbest „шифер“) auf den schmalen (≤ 15 m) rechteckigen 2-Geschossern; breite Hallenbauten behalten das Flachdach (sonst > 10 m hohe „Scheunendächer“) | Foto 6480171585 zeigt ältere Bauten mit Steildach; Material ANNAHME (typisch sowjetisch) | `add_gable_roof` |
| 06:05 | Schule = ул. Школьная 1 (langer 2-Geschosser) mit großen Sprossenfenstern zwischen hellen Lisenen, Wand Betongrau | Foto 6480300155 „School“ / Briefing R3; Dossier: Schule an der ул. Школьная; Gebäude ANNAHME | `SCHOOL` |

## 2026-11-07 — Einstellungsmenü, Startblick, Desktop-Starter (Auftrag des Nutzers)
- **Menü in Slate (C++), nicht UMG-Blueprint:** komplett per Code testbar und ohne Editor-Klickarbeit. Esc öffnet (im Editor M, weil Esc dort das Spiel beendet). Spiel pausiert.
- **Einstellungen in `UKdkGameUserSettings`** (Unterklasse von `UGameUserSettings`, `GameUserSettings.ini`): Maus-Empfindlichkeit, Y umkehren, Hardware-Raytracing, Nanite, FPS-Anzeige plus die Engine-Qualitätsgruppen.
- **Hardware-Raytracing standardmäßig aus** (`r.RayTracing.Enable` + `r.Lumen.HardwareRayTracing`, dazu `r.RayTracing.EnableOnDemand=1`): größter Kostenfaktor auf dem MacBook Air. Rückweg: Menü oder Default in `SetToDefaults`.
- **Renderauflösung 25–100 %:** die Engine erlaubt 0 %, ältere Speicherstände darunter werden auf 100 % gesetzt.
- **Entwickler-Bildschirmmeldungen ausgeblendet** (`DisableAllScreenMessages`), sie verdeckten das Menü.
- **Startblick:** Blickeingaben der ersten 1,5 s ignoriert, danach Blick waagerecht (macOS-Cursorsprung beim Fensteröffnen kippte den Blick auf −70°).
- **Desktop-Starter** `~/Desktop/Kadyktschan.app` → `tools/play.sh` (kompiliert geänderten C++-Code, startet `-game`).
- **Atmosphären-Zielbild des Nutzers** gespeichert: `design/art/atmosphere-target.md`; ersetzt die sonnige Sommerstimmung der Art Bible.

## 2026-11-07 — Atmosphäre Stufe 1 (Auftrag: Zielbild `design/art/atmosphere-target.md`)
- **Bedeckter Himmel ohne Wolken-Actor:** VolumetricCloud entfernt (zeigte blaue Lücken, teuer auf dem Mac); der blasse Himmel kommt aus SkyAtmosphere (wenig Rayleigh, mehr Mie). Sonne 2,2 lux, Quellwinkel 12° (weiche Schatten), keine Sonnenscheibe; Himmelslicht trägt das Bild.
- **Dunst:** Höhennebel mit maximaler Deckkraft 0,88, damit entfernte Blöcke verblassen, aber nie ganz verschwinden (Zielbild: „die Stadt geht dort weiter“).
- **Farbe:** Sättigung 0,72, kühler Weißabgleich, Belichtung −0,4. Sky-Cycle-Temperaturen 7000 → 7400 K. Weicht von Art Bible §2 (sonniger Sommer) ab — Zielbild des Nutzers hat Vorrang.
- **Häuser „Rohbau“-Eindruck beseitigt:** Schmutz-Textur (16-m-Kachel, Laufspuren + Feuchteflecken) und Verblassen im Master-Material, nur für Außenflächen; Fensterrahmen verwittertes Grau (`FrameWood`); Vordach als Betonplatte ohne Stangen; Schutt flach und eingesunken.
- Werte zentral in `tools/editor/apply_atmosphere.py` und `FACADE_GRIME/FACADE_FADE` in `build_materials.py`. Rückweg: Skript nicht ausführen bzw. Werte auf 0.

## 2026-11-07 — Häuser stehen auf dem Boden, verwilderter Boden (Nutzer: „das Haus fliegt noch“)
- **Geschlossener Sockel (ANNAHME):** Betonschürze mit einer Lüftungsöffnung pro Achse vor dem Kriechraum, bis 3 m unter die Nennhöhe (`BURY`). Der offene Kriechraum mit Pfählen las sich als schwebendes Haus, weil das Gelände unter langen Blöcken abfällt. Fotobeleg für offene vs. geschlossene Sockel in Kadyktschan steht aus — Rückweg: `SM_T5_Skirt_A_Aged` in `build_buildings.py` nicht setzen.
- **Pfähle und Eingangstreppen** reichen ebenfalls 3 m unter die Nennhöhe; das Gelände verdeckt den Rest.
- **Gras als Vernachlässigung statt Rasen:** 40 % als Unkrautsaum an den Hauswänden, 60 % in 260 unregelmäßigen Flecken mit kahlem Boden dazwischen. Tundra-Bodenfarben Richtung Erde/Grau verschoben.

## 2026-11-07 — Karte gegen Satellitenbild geprüft (Auftrag des Nutzers)
- **Vergleich:** OSM-Blockout als 1-m/px-Overlay auf den Google-Maps-Screenshot des Nutzers gelegt. Zentrum, Süden, Schule, Hauptstraßen und Fluss stimmen; OSM liegt ~8 m westlich des Bildes.
- **15 fehlende Gebäude ergänzt (ANNAHME):** Viertel Профилакторий / Знаменитый двор im Nordosten, vier Schrägblöcke im Osten, ein Block im Süden — sichtbar im Bild, nicht in OSM. Datei `design/research/data/satellite-additions-2026-11-07.json` (Positionen ±5 m, Geschosszahl aus Schatten geschätzt). Bild nur als Referenz vermessen, nicht abgepaust oder ausgeliefert. Rückweg: Datei löschen und `blockout_data.py` neu laufen lassen.
- Verstärkt das Zielbild („hinter Häusern weitere Häuser“) mit belegten statt erfundenen Gebäuden.

## 2026-11-07 — Fenster: Spuren von Zeit und Bewohnern
- Verglasung: 30 % intakt, 30 % teilweise zerbrochen (Scherbe, einzelne Flügel), Rest leer; 15 % ohne Rahmen.
- 10 % der Erdgeschossfenster mit Brettern vernagelt; 7 % der oberen Fenster mit Vorhangrest (rot oder Tüll) — bewusst sparsam (Zielbild: Details sollen in der Leere auffallen).

## 2026-11-07 — Nordviertel nach Zoom-Bildern (Google + Apple Karten) verfeinert
- Maßstab über die beiden Google-Marker (Профилакторий, Знаменитый двор) bestimmt: 3,02 px/m. Langer Block 94 m statt 55 m; Профилакторий als Hofbau (53 × 36 m); Westflügel des Знаменитый-двор-Hofs; zwei kleine Walmdachhäuser; drei Satteldachhäuser 15 m weiter nördlich. Alle +7 m Ost an die OSM-Lage angeglichen.
- **19 Fundamente abgerissener Holzhäuser** im Raster nördlich davon: niedrige, lückige Betonränder mit Schutt und Gras (`foundation()` in `build_vegetation.py`). Starke „Spur früherer Normalität“ laut Zielbild, und belegt.
- **Gras in den Wegen:** ~700 kleine Büschel entlang Fahrspuren und Mittellinie innerhalb 900 m vom Zentrum.
- **Boden-Kachelmuster beseitigt:** zweite Detailprobe im 7,3-m-Maßstab, Detailkontrast und Normal-Map gedämpft (das 2-m-Raster war von oben als Waffelmuster sichtbar).

## 2026-11-07 — Zwei Häuser komplett gestaltet (Auftrag: „ein oder zwei Häuser, wo man spawnt, komplett fertig“)
- **ул. Ленина 8 und 7** (`HERO` in `build_buildings.py`) als Referenz, wohin die ganze Stadt gehen soll.
- **Decals auf dem maskierten Kartenmaster** (8-m-Kachel über `MAT_UV` im Kit): Risse (auf ~45 % der Platten, sonst Muster-Eindruck), abgeplatzter Putz (alle Platten, in Clustern), Rostfahnen unter ~25 % der Fensterbänke.
- **Rost braun-grau statt rot:** die erste, rote Fassung las sich wie Blut — Horror-Klischee, vom Briefing ausgeschlossen.
- **Geometrie:** offene/abgerissene Fensterflügel (22 %), schief offene Haustüren, Fallrohre an jeder vierten Fuge mit fehlenden Stücken, hängende Kabel, 3 Fernsehantennen + 1 umgestürzte, selbstgebaute Holzverglasung auf 40 % der Loggien, zurückgelassene Kiste/Bretter/Wäscheleine auf 35 %, Wohnungsschilder „КВ. 21-40“ (ANNAHME: 4 Wohnungen × 5 Geschosse je Eingang).
- **Bewuchs:** Birkenschösslinge, Sträucher und Gras auf dem Dach und am Sockel (über das Manifest an die Vegetation übergeben).
- Seltenere Plattenausbrüche als im Rest der Stadt; kein Teileinsturz an den beiden Häusern.

## 2026-11-07 — Fliegen, Boden und Wege (Auftrag des Nutzers, Referenzbild `generated-image-3.png`)
- **Fliegen (F):** Betrachtungshilfe im Charakter, keine Spielmechanik. Ohne Kollision, Bewegung in Blickrichtung, Leertaste/E hoch, C/Q runter, Shift ×4, Mausrad Grundtempo (3–200 m/s). Steht unten im Einstellungsmenü. Getestet: 63 m Steigung in 2,5 s.
- **Gelände-exakte Höhen:** neues `tools/research/terrain_mesh.py` interpoliert das 30-m-Gelände-Mesh so wie gerendert. Vegetation, Requisiten und Wege nutzten bisher die rohen DEM-Werte und schwebten/versanken zwischen den Gitterpunkten.
- **Wege neu:** Straßenbänder alle 2 m auf das Gelände gelegt (6 cm Abstand statt 30 cm), echte UVs; Schotter-Karte mit zwei Fahrspuren, bewachsenem Mittelstreifen, Schlaglöchern und ausgefransten Rändern (maskierter Kartenmaster). **Trampelpfade (ANNAHME)** von jedem Eingang zur nächsten Straße.
- **Boden:** Detailtextur jetzt staubige Erde mit Kieseln und Zweigen; Erdfarbe sandiger. Am ganzen Gelände statt nur einem Viertel — prozedural ist das gleich viel Arbeit.
- **Streugut:** 5000 Steine, Betonbrocken, Bretter, Äste (dichter nahe den Wänden) und Schutthaufen aus Plattenresten an einzelnen Sockeln.
- **Nachjustiert:** Erd/Gras-Maske geschärft (Kontrast 4), in der Stadt Richtung Erde, ab 600–900 m Richtung Tundra (Weltposition); zweite Makroprobe (×0,383) gegen das 50-m-Raster; Detail und Normal-Map entfernungsabhängig (voll nah, ab 30 m gedämpft).
- **Stabile Texturen:** jeder Generator in `gen_textures.py` hat jetzt einen eigenen Zufallsstrom (`seed(name)`); vorher verschob jede neue Textur alle späteren.

## 2026-11-07 — Schwebender Boden behoben; Layout gegen Apple Karten korrigiert
- **Unsichtbarer Boden:** die Trampelpfade (ein stadtweites Mesh) bekamen beim Import automatisch eine konvexe Hülle als Kollision — eine unsichtbare Fläche über tiefer liegendem Gelände. Kollision der Pfade entfernt (Mesh + Actor). Geprüft: Figur am Spawn auf 7,16 m bei Gelände 6,18 m + halbe Kapsel.
- **Layout:** Apple-Karten-Fenster des Nutzers (1,53 px/m) mit allen Umrissen überlagert — OSM und frühere Satelliten-Ergänzungen passen. 8 weitere Gebäude ergänzt (ANNAHME): Flügelbau ganz im Osten, zwei kleine Häuser östlich der Hauptstraße, drei Bauten im Nordwesten. Das Schräg-Luftbild des Nutzers diente nur zur Kontrolle (Positionen aus Draufsicht gemessen).
- Beleg ohne Apple-Seitenleiste (private Suchverläufe): `production/qa/evidence/2026-11-07-map-vs-applemaps-overlay.png`.

## 2026-11-07 — Atmosphäre nach echten Fotos (Auftrag: „grüner, wie im echten Bild, auch die Umgebung“)
- **Vorrang:** die vom Nutzer gelieferten Luftbilder (kolymahistory.ru u. a., nur Referenz) ersetzen das ganz bedeckte Zielbild beim Licht: aufgelockerte Bewölkung mit blauen Lücken (VolumetricCloud wieder da), Sonne 5 lux, wenig Dunst (Dichte 0,006, max. 0,55), Sättigung 0,92. Das Gefühl aus `atmosphere-target.md` (Größe, Leere, Spuren) bleibt Maßstab.
- **Bewuchs:** Stadt dicht zugewachsen: +7000 gelbgrüne Gebüsche in 420 Clustern, +1500 junge Lärchen/Birken; Taiga außen 6500 statt 2600 Lärchen. Strauchfarbe Richtung Frühherbst-Gelbgrün, Boden grüner.
- **Horizont:** echter DEM-Ring 60 × 60 km (300-m-Raster, `tools/research/dem_ring_obj.py`), dafür zwei südliche Copernicus-Kacheln (N62 E146/E147) nachgeladen; ohne Kollision, Waldmaterial.
- **Platzhalter-Kisten:** unadressierte OSM-Gebäude (Schuppen, Werke ≥ 30 m²) werden jetzt ebenfalls mit dem Baukasten gebaut.
- **Risiko Leistung:** deutlich mehr Vegetation; auf dem Mac ggf. Vegetation/Sichtweite im Menü senken. HLOD/Culling steht aus.
- Nachjustiert: Gebüsche 1,4–3 m groß, +10 000 statt +7000; Umland grüner (Masken-Bias außen 0,12).

## 2026-11-07 — Flackernde Streifen an allen Häusern behoben (Nutzer-Video)
- **Ursache:** Z-Fighting. Die Deckenplatten reichten bis zur Fassadenebene und überlappten die Außenseite der Wandplatte darunter um ~20 cm in derselben Ebene (Fuge J/2 < Deckenstärke 0,22 m).
- **Fix:** Deckenkanten an Außenseiten 3 cm nach innen (`SLAB_INSET`), innen bleiben die Zellen bündig. Gilt für alle 76 Gebäude.
- **Nebel:** auf Wunsch etwas dichter (Dichte 0,012, max. 0,68, Start 25 m).

## 2026-11-07 — Großes Update (autonom, Nutzer abwesend)
- **Verfallsstufen statt Detailhaus:** jedes Haus bekommt Stufe 0–3 (`DECAY` in `build_buildings.py`; 25/40/25/10 %, Teileinsturz = 3, Ленина 7/8 = 1). Stufe steuert Putzschäden, Risse, Rost, offene Flügel, fehlende Rahmen, Plattenausbrüche, Dachlöcher mit freiliegenden Balken, Bewuchs auf Dach und Sockel. Ergebnis im Manifest (`decay`).
- **Farben:** Ocker und Türkis als zusätzliche Fassadenschemata (Luftbilder); Kulturhaus ул. Южная 9 ocker.
- **Nach Nutzerfotos:** Kulturhaus mit Wandbild (Familien-Silhouetten, roter Ballon — frei nachempfunden, keine Kopie) und beschädigter Büste davor; rostige Ofenrohre auf niedrigen Baracken; gemauerter Kesselhaus-Schornstein (~32 m, Eisenringe) am nächsten Werksgebäude.
- **Stadt gefüllt:** Autowracks, Fassgruppen, Schrotthaufen, Holzzäune, Strommasten alle 35 m an Straßen (15 % fehlen), Möbel im Freien, Bushaltestellen an den drei breitesten Straßen, Ruinenfeld mit 140 zusammengefallenen Holzhäusern im Süden.
- Neue Materialien: Ziegel, verwittertes graues Holz.
- Nachjustiert: Familien-Wandbild auf eine fensterlose Giebelwand des Kulturhauses; Dachpflanzen überwiegend Gras, Birken nur noch als halb so große Schösslinge.

## 2026-11-07 — Weniger eckig, leicht unheimlich, Dämmerungsmodus
- **Häuser:** Platten je 0–2,5 cm nach innen versetzt (keine perfekt glatte Fassade), Bewehrungsstahl in ausgebrochenen Plattenfeldern, abgebrochene Dachkanten mit Brocken (Wahrscheinlichkeit 12 % × Verfallsstufe).
- **Auto:** abgestufter Körper und Kabine (wirkt gerundet), Fensterband, Stoßstangen, Räder als Kreuz zweier Quader (60 %), sonst auf dem Boden.
- **Unheimlich ohne Klischees:** prozedurales Knarren und fernes Metallscheppern (loses Blech, hängende Türen) aus 12 verfallenen Häusern, Reichweite 35 m; keine Stimmen, keine Schockeffekte. Sättigung 0,84, Vignette 0,42, Filmkorn 0,18.
- **Dämmerungsmodus** (Esc-Menü „Dämmerung“, gespeichert): Sonne 2° über dem Horizont, 4200 K, 30 % Licht, Belichtung −1,5 (`r.ExposureOffset`), sonst würde die Auto-Belichtung aufhellen.
- **Videokamera-Modus** (Esc-Menü): Laufzeit-PostProcessVolume (Sättigung 0,55–0,75, Blaugrün, Korn 0,75, Farbsäume 3,5, Vignette 0,85, Bloom) + Slate-Einblendung „● REC / CAMERA 01“, nach Nutzervideo.
- **Regler (Esc-Menü):** Helligkeit −2…+2 Blenden (`r.ExposureOffset`), Dämmerungsstärke 0–100 % (Sonnenhöhe/Licht/Belichtung interpoliert), Verpixelung Videokamera 0–100 % (Renderauflösung 100→20 %, `r.Upscale.Quality 0` = ungefiltert). Beim Ausschalten wird die eigene Renderauflösung wiederhergestellt.

## 2026-11-07 — Videokamera nachjustiert, Nebel-Regler (Nutzer: „zu blau“, „Rausch-Slider für die Kamera“)
- **Farbe neutral-warm statt Blaugrün:** `ColorGain` 1,0 / 0,98 / 0,92 statt Blaugrün — der Nutzer fand den Look „zu blau“.
- **Verpixelungs-Fix:** Nur `r.ScreenPercentage` zu senken reichte nicht, weil TSR die niedrige Auflösung über die Zeit wieder glättete. Solange die Verpixelung aktiv ist, steht deshalb `r.AntiAliasingMethod 0`; danach kommt der gespeicherte Wert zurück. `r.ScreenPercentage` wird mit derselben Code-Priorität zurückgesetzt (ein normaler Schreibzugriff aus den Spieleinstellungen kann einen von Code gesetzten Wert nicht überschreiben). Ohne Verpixelung wird der Wert alle 0,5 s an den Auflösungsregler angeglichen.
- **Regler „Stärke (Videokamera)“** (`CamNoise`, 0–100 %, Standard 75 % = bisher abgestimmter Look): Ein Regler verändert den ganzen Effekt (Sättigung, Kontrast, Farbstich, Korn, Farbsäume, Vignette, Bloom), weil der Nutzer „den ganzen Videokamera-Effekt“ stärker oder schwächer haben wollte, nicht nur das Rauschen.
- **Regler „Nebel“** (`FogAmount`, 0–300 %, wirkt im `AKdkSkyCycleActor` auf die Grunddichte des Nebels).
- **Menü merkt die Scrollposition** beim Schließen und Öffnen (die langen Listen sprangen sonst an den Anfang).
- Status: Im Spiel geprüft mit den Nutzereinstellungen (Stärke 95 %, Nebel 180 %). Look und Einblendung „● REC / CAMERA 01“ sind sichtbar: `production/qa/evidence/2026-11-07-camcorder-overlay-window.png` (Fensteraufnahme; `HighResShot` nimmt keine Slate-Einblendungen auf). Regler laut Nutzer (2026-11-07) alle funktionsfähig, keine Änderung nötig.

## 2026-11-07 — Phase-3-Grafik freigegeben, erster Commit, Start Mechanik
- Nutzer: „mache 1 und 2 beides selbstständig“, also Grafikteil von Phase 3 freigeben, ersten Commit anlegen und mit dem Notizbuch-Prototyp beginnen.
- Commit-Autor über `git -c` nur für diesen Commit gesetzt (im Repo ist kein `user.name` konfiguriert); kein Push.
