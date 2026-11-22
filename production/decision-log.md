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
- **Notizbuch-Prototyp als HTML, nicht in UE:** Die Hypothese betrifft Logik und Fairness der Thesen, nicht Gefühl oder Grafik. Eine Browser-Seite lässt sich in Minuten ändern und an Testpersonen weitergeben. Riskanteste Annahme: Feedback „X von N stimmen“ ohne Kosten führt zum Durchprobieren. Zwei Thesen, 9 Funde, Ablenker. Kyrillische Namen mit deutschen Lesehilfen, damit die Sprache nicht das Ergebnis verfälscht. Familie, Wohnung 14 und Stollen 3 sind FIKTION und keiner realen Adresse zugeordnet (Ethik-Regel).

## 2026-11-07 — Story-Innenräume (Nutzer: lieber wenige Räume mit detaillierter, zur Story passender Einrichtung)
- **Drei Orte statt vieler Grundeinrichtungen.** Grundlage ist die Geschichte aus dem Notizbuch-Prototyp (FIKTION): Walja und Lida fahren im Oktober 2003 mit dem Bus weg, Pjotr bleibt und hält Kessel 2 durch den Winter 2003/04 am Laufen, und der Funkamateur in der Telefonzentrale nimmt das auf Band auf.
  1. **Wohnung der Familie Gorbunow** im Satelliten-Haus `PLA_SAT_S_Block` (ohne echte Adresse, nahe ул. Ленина), damit die Familie keiner realen Adresse zugeordnet ist (Ethik-Regel). Ein Zimmer für drei: Ehebett mit nackter Matratze, Wandteppich, Nachttisch mit herausgezogener Schublade und Brief, offener leerer Schrank mit Kinderschuh, Spiegel mit Foto dahinter, Lidas Bett mit Schulranzen, Heften und Kinderzeichnung. Küche für eine Person: ein Teller, eine Tasse, voller Aschenbecher, Konservendosen-Turm, halb zugeklebtes Fenster, Kalender mit rot markiertem Freitag, Drahtfunk-Lautsprecher. Flur: Grubenhelm am Haken, leere Haken, Filzstiefel, Briefstapel hinter der Tür, Hörer neben dem Telefon. Nachbarwohnung bewusst fast leer (Kontrast).
  2. **Kesselhaus** im Werksgebäude `PLA_OSM_170991713` (dort steht schon der Schornstein): Kessel 1 kalt, die Tür liegt am Boden; Kessel 2 mit Kohlehalde, Schaufel und Schubkarre. In Pjotrs Ecke: Eisenpritsche, Kiste als Tisch, Kessel, Tasse, Petroleumlampe, Logbuch, Feldtelefon zur Telefonzentrale, Kalender mit durchgestrichenen Tagen, Familienfoto, Wattejacke, Filzstiefel, Brennholz, Werkbank.
  3. **Telefonzentrale** in `PLA_Shkolnaya_8` (Dossier: Haus unbekannt, ANNAHME): Relaishalle mit drei Gestellreihen, abgenommenen Blechen und hängenden Kabeln. Funkraum mit Sender, Empfänger, Tonbandgerät mit Spulen, Morsetaste, Mikrofon, Kopfhörer, Weltkarte mit QSL-Karten und Antennenkabel zum Fenster. Dazu ein Regal mit nummerierten Tonbandkartons, in dem ein Karton fehlt (Band 41).
- Runde Formen (Kessel, Rohre, Spulen, Tassen, Brennholz) als echte Zylinder (`story_rooms.cyl/hcyl`), passend zu „weniger eckig“. Nur vorhandene Materialien, daher keine neuen `SLOT_MI`-Einträge.
- Die Pflanzenpositionen dieser drei Häuser im Manifest haben sich verschoben (anderer Zufallsverlauf). Die Vegetation wurde nicht neu gestreut, die alten Positionen liegen weiter auf denselben Dächern und Rändern.
- Der Prototyp nennt „Wohnung 14, dritter Stock“; im Spiel liegt die Wohnung im Erdgeschoss, weil nur Erdgeschoss-Ausschnitte gebaut werden. Das wird beim Story-Design angeglichen.

## 2026-11-07 — Innenräume begehbar, Karte im Spiel, Taschenlampe

- **Anlass (Nutzer):** „in das Haus 1 komme ich nicht rein weil der Weg blockiert ist“, Karte ins Spiel, Taschenlampe, Häuser innen dunkel.
- **Ursachen gefunden (Code gelesen, Gegenstände nachgemessen):**
  1. Treppenhaus (`interiors.stairwell`, auch Lenina 8): Treppe an der linken Wand bis nach hinten, Zwischenpodest quer über die Rückseite, Schutthaufen in der Mitte. Die beiden Wohnungstüren hinten links und rechts waren nicht erreichbar (rechts blieben 32 cm, die Spielfigur braucht 68 cm).
     **Neu:** Die Treppe beginnt hinten und steigt zur Fassade. Der Schutt liegt auf den oberen Stufen, die Briefkästen hängen an der rechten Wand. Rechte Hälfte und Rückseite sind frei.
  2. Küche (Gorbunow und Lenina 8): Der Kühlschrank stand direkt hinter der Küchentür.
     **Neu:** Die Tür liegt bei -1,4..-0,6, Herd und Kühlschrank stehen an der Treppenhauswand.
  3. Kesselhaus: Der Kohlehaufen versperrte den einzigen Weg zu Pjotrs Ecke. Er liegt jetzt in der Halle neben Kessel 2.
  5. Zimmertür (Gorbunow und Lenina 8): Die Badwand bei x = -4,2 lief mitten durch die Türöffnung -4,6..-3,8, vom Flur blieben 40 cm.
     **Neu:** Die Tür liegt bei -4,05..-3,25. Lidas Bett steht jetzt am Fenster, die Fotos hängen neben der Tür. Das Sofa in Lenina 8 ist kürzer.
  6. **Hauptursache:** Die Eingangstreppe aller Häuser endete auf der nominellen Bodenhöhe des Hauses. Wo das Gelände vor dem Haus abfällt, blieb ein etwa 1 m hoher Block. Gefunden mit dem Lauftest am Kesselhaus, Belegbild `2026-11-08-walk-kessel.png`.
     **Neu:** `build_t5_kit.entrance` legt 6 zusätzliche Stufen unter die Bodenlinie (insgesamt 11 × 27,5 cm). Auf ebenem Boden liegen sie unter dem Gelände. Das betrifft alle Häuser.
  4. Vor den Türen der eingerichteten Häuser standen Bäume und Schutt (Telefonzentrale: Birke direkt in der Tür). `scatter.json` war älter als die Eingänge im Manifest. Die Basis-Pflanzen der Heldengebäude umgingen außerdem die Eingangs-Freihaltung.
     **Fix:** `scatter_vegetation.py` hält jetzt auch bei Basis-Pflanzen 8 m vor jedem Eingang frei.
     **Neu:** Aus `scatter.json` habe ich einmalig Birken, Büsche, Schutt und Trümmer im 8-m-Feld vor den 6 eingerichteten Häusern entfernt: 16 Birken, 7 Büsche, 11 Schutt, 37 Trümmer. Dachpflanzen, Bänke und die Büste bleiben. Ein kompletter Neulauf ist nicht möglich, weil die DEM-Kacheln auf diesem Mac fehlen.
- **Adresse der Familie:** Laut Nutzer ist es egal, ob das Haus eine echte Adresse hat. Die Wohnung bleibt trotzdem im Block PLA_SAT_S_Block, ohne Umbau. Das ist ein bestehendes Haus von Satellitenbildern, das in OSM ohne Adresse eingetragen ist. Es wurde kein neues Haus gebaut.
- **Karte (K oder Tab):** Slate-Overlay `SKdkTownMap`, das Spiel läuft weiter.
  - **Inhalt:** Grundrisse, Straßen, Fluss, die 6 eingerichteten Häuser nummeriert und eingefärbt (rot Story, blau Phase 3), ein Pfeil für Spielerposition und Blickrichtung, Maßstab 100 m.
  - **Daten:** `Content/Kadykchan/Data/TownMap.json` aus `tools/research/town_map_data.py`. Wird als UFS-Datei mit ins Paket gepackt.
- **Taschenlampe (L):** Spotlicht an der Kamera.
  - **Werte:** 1200 lm, warm, Kegel 12°/28°, Reichweite 25 m, wirft Schatten, beim Start aus.
- **Prüf-Hooks (nur Kommandozeile):** `-KdkStart=N,E,Yaw`, `-KdkWalk=N,E;…` (protokolliert „reached“ oder „stuck“), `-KdkTorch`, `-KdkMap`.

## 2026-11-08 — Großes Update über Nacht (Nutzer: Vegetation, Gelände, Details, Innenräume am Start, Stollen)

Auftrag des Nutzers vor dem Schlafen: „mache … ohne weitere Aufforderung weiter … großes Update“.
Referenz: das Luftbild der Nutzerin (Image #20). Darauf ist das Tal dicht bewaldet, im Ort steht überall gelbgrünes Jungholz, zwischen den Blöcken wenig freier Boden, die Hügel tragen dunklen Wald.

- **Vegetation als Instanzen**
  - **Technik:** Neue C++-Klasse `AKdkFoliageField`, die je Art und Variante ein Hierarchical-Instanced-Static-Mesh-Bauteil aus `Content/Kadykchan/Data/Foliage/*.txt` füllt. Dazu ein Automation-Test `Kadyktschan.Foliage.ParseSkipsMalformedLines`.
  - **Warum:** Das Zusammenführen pro Zelle skaliert nicht auf 200.000 Pflanzen.
  - **Formen:** Neue Vorlagen mit 3 LODs: Lärche mit Astetagen, junge Lärche, Weidenbusch mit mehreren Stämmen, Birke, Zwergstrauch. LOD1 und LOD2 haben weniger, aber größere Karten.
  - **Grenzen:** Grasbüschel und Requisiten bleiben in Zellen zusammengeführt. Kein Nanite für Laub (art bible 8.7), keine Kollision, damit das Dickicht den Ort nicht zusperrt.
- **Dichte**
  - **Wald:** 110.000 Lärchen von 250 m bis 3,8 km, flächengleichmäßig verteilt.
  - **Ort und Ortsrand:** etwa 85.000 Weiden und Junglärchen in Haufen.
  - **Höfe:** 2.150 Birken.
  - **Nachrechnung:** `scatter_vegetation.py` läuft ohne die fehlenden DEM-Kacheln über die Gelände-OBJ (`dem_to_obj.load_obj`). Der Abgleich mit der alten Verteilung ergibt 0,0 m im Mittel und 0,25 m maximal.
- **Farben** (`palette_2011.json`):
  - Boden olivgrün statt beige.
  - Ab etwa 1 km geht der Boden in dunklen Taiga-Boden über (`ColorForest`, `ForestAmount`).
  - Jede Laub-Instanz ist zufällig gelber oder dunkler (`PerInstanceRandom`, `Variation`).
- **Blätterkarten:** Die Blätter sitzen jetzt in 4–6 Büscheln an Zweigen und dünnen zum Rand aus. Vorher war das Kartenquadrat als Block sichtbar. `gen_textures.py` läuft dafür mit Blenders Python, mit einem eigenen PNG-Schreiber als Ersatz.
- **Details im Ort**
  - Schutt, Steine und Haufen sind unregelmäßige, gekippte Brocken (`rock`) mit Bewehrungsstahl.
  - Neu: 9 Ruinen abgerissener Plattenbauten. Stehende Wandplatten mit Fensterlöchern, Deckenplatten, Trümmerberg.
  - Neu: 19 Trafo- und Pumpenhäuschen an den Straßen.
  - Alle Positionen sind ANNAHME.
- **Innenräume am Start**
  - **ул. Ленина 8:** Story-Wohnung von Antonina Fjodorowna. Nachbarwohnung geplündert.
  - **ул. Ленина 7:** Wohnung von Brigadier Orlow, Nachbarwohnung mit eingestürzter Decke.
  - Story in `design/narrative/story-places.md`, Kanon-Status Provisional.
  - Der Notizbuch-Prototyp ist noch nicht angepasst.
- **Stollen 3 (Nordhang), begonnen** – FIKTION, Lage ANNAHME
  - **Lage:** steilster Hang nordwestlich, 540 m vom Kesselhaus.
  - **Gelände:** `mine_site.py` schneidet 5 × 5 Zellen aus dem 30-m-Gelände und setzt ein 0,5-m-Stück mit Einschnitt ein. Höhen auf den Originaldreiecken, damit die Naht bleibt.
  - **Bauwerk:** `build_mine.py` baut:
    - Portal mit Stützmauern
    - offenes Gittertor
    - 52 m Stollen mit Holz- und Stahlausbau
    - Gleis, Loren, Halde, Lampenhaus, Strommasten
    - einen Bruch am Ende
  - **Platzierung:** `place_mine.py`.
  - **Karte im Spiel:** Ein „Stollen 3“-Marker ist dazugekommen.
- **Prüfung (2026-11-08, ~03:25)**
  - **Lauftest im Spiel (`-KdkWalk`):** Alle 13 Wege kommen durch, darunter Antonina, Orlow und 40 m Stollen bis vor den Bruch.
    - Im Stollen hat der Test drei echte Fehler gefunden, alle behoben: eine Geländewand im Stollenmund, ein schräges Dreieck und Schienen 17 cm über dem Boden.
    - Toleranz der Wegpunkte im Test: 60 cm.
  - **Automation:** 5/5 bestanden.
  - **Belegbilder:** `production/qa/evidence/2026-11-08-*.png`
  - **Taschenlampe:** 800 lm statt 1200 lm, weil die Felswände auf Armlänge überstrahlt waren. Neues Material `MI_Ground_Rock`.
  - **Karte:** zeigt 8 Orte, der Ausschnitt schließt Orte außerhalb des Ortes ein. Die Beschriftungen am Startpunkt überlappen sich noch.

## 2026-11-08 (Vormittag) – Rückmeldung des Nutzers: Lampe, Wohnungen, Story-Führung, Schweben, Blinken

Nutzer: „lampe ist zu hell … gelblich, größerer Kegel aber dunkler“; „in den Wohnungen ist es kaum möglich sich zu
bewegen … Einrichtung macht keinen Sinn … viel zu einfach“; „man versteht die Story nicht … Missionsmarker und
interaktive Gegenstände“; „in einer Wohnung steht einfach eine Treppe im Raum“; „überall fliegende Strukturen“;
„die Schatten blinken“ (Video). Claude entscheidet die Technik (Memory „Claude decides tech“).

- **Schattenblinken – Ursache gemessen, nicht geraten**
  - **Aufzeichnung:** Die Sonne (`AKdkSkyCycleActor`) dreht alle 0,5 s ein Stück weiter. Jeder Schritt verwirft die gespeicherten Seiten der virtuellen Schattenkarte. Im Neuberechnungs-Bild fehlen dann viele Baum- und Buschschatten (Video des Nutzers: Blinker bei 0,93 / 1,93 / 2,46 s).
  - **Nachgestellt:** Vollbild, 40 m Flughöhe, Blick nach unten → 34 Blinker in 12 s, immer paarweise im 0,5-s-Takt. Mit angehaltener Sonne (`-KdkSkySpeed=0`) 0 Blinker. `r.Shadow.Virtual.NonNanite.UseHZB=0` half nicht (48).
  - **Fix:** `r.Shadow.Virtual.Cache=0` (Config/DefaultEngine.ini) → 0 Blinker in 12 s, weiterhin 60 FPS. Test: Skript `flicker_test.sh` (Fenster-Aufnahme + Bilddifferenz).
  - **Neue Dev-Hooks:** `-KdkStart` mit optionalem Pitch, Schwebehöhe und Start-Höhe für die Bodensuche; `-KdkSkySpeed=`.
- **Taschenlampe:** 220 lm statt 800 lm, Farbe (1, 0.74, 0.42) wie eine alte Glühbirne mit schwacher Batterie, Kegel 16°/40° statt 12°/28°.
- **Schwebende Objekte**
  - **Ursache:** Feste Objekte standen auf der Geländehöhe ihrer Mitte. Am Hang hing die Talseite in der Luft.
  - **Fix:** `scatter_vegetation.gfoot` setzt Häuschen, Ruinen, Garagen, Tanks, Autos, Haltestellen usw. auf den tiefsten Punkt ihrer Grundfläche. Die Hangseite sinkt ein.
  - Häuschenwände reichen 1 m in den Boden. Ruinen bekommen ein Streifenfundament (−1,5 m).
  - Die Stützmauern am Stollen sind jetzt durchgehend schräge Wände entlang der Geländelinie statt 1-m-Treppenstufen.
- **Wohnungen neu (interiors.py, story_rooms.py, furniture.py)**
  - **Tiefe:** Die drei Story-Abschnitte reichen jetzt durch den ganzen Block, 4 Achsen bis zur Rückfassade (`interiors.DEEP`). Pro Wohnung doppelte Fläche.
  - **Grundriss:**
    - vorne ein Wohnzimmer über beide Fenster (6 × 4,1 m)
    - in der Mitte Flur, Bad und WC
    - hinten Schlafzimmer und Küche
    - Türen 0,8–0,9 m
    - Innenwände treffen die Fassade nur zwischen zwei Fenstern
  - **Treppenhaus:** Vorraum mit Briefkästen und beiden Wohnungstüren. Ein Lauf führt zum Zwischenpodest an der Rückwand, darüber ist der Schacht offen (keine Decke über den hinteren Treppenzellen). Der Rücklauf ist in der Mitte eingestürzt, die Trümmer liegen darunter. So bleiben die oberen Etagen unerreichbar.
  - **Möbel:** echte Formen statt Kästen. Sofa mit Lehnen und Kissen, Bett mit Kopf- und Fußteil, Kleiderschrank mit Türen und Griffen, Küchenzeile mit Hängeschränken, Herd mit Backofentür und Knöpfen, ZIL-Kühlschrank, Röhrenfernseher, Bücherregal, Vorhänge, Läufer, Bad und WC.
  - **Schutt:** unregelmäßige Brocken (`chunk`) statt weißer Würfel.
  - Alles ANNAHME (Typenserie nicht dokumentiert).
- **Story im Spiel (FIKTION, Kanon weiter Provisional)**
  - **Ablauf:** 6 Aufgaben mit 16 Funden: Antonina → Orlow → Gorbunow → Kesselhaus → Telefonzentrale → Stollen 3.
  - **Bedienung:**
    - E zeigt einen Fund an (Text mit russischem Original und Übersetzung).
    - Oben links steht die Aufgabe.
    - Ein Marker mit Entfernung zeigt zum nächsten ungelesenen Fund. Ist der Fund weiter als 30 m entfernt, zeigt er zum Hauseingang.
    - Gelbe Ringe markieren die Funde in Sichtweite.
    - Ist eine Aufgabe erledigt, erscheint „Neue Erkenntnis“ mit der nächsten Aufgabe.
    - N öffnet das Notizbuch.
  - **Daten:** Texte und Reihenfolge stehen in `tools/research/story_data.py` und werden zu `Content/Kadykchan/Data/Story.json`. Die Positionen kommen aus den Gebäude- und Stollen-Skripten (`S.clue`).
  - **Code:** `FKdkStory` mit 3 Automation-Tests (`Kadyktschan.Story.*`), Anzeige `SKdkStoryHud`.
  - **Ende:** Der Vorschlag aus `story-places.md` ist umgesetzt. Am Bruch hängen die leere Halterung der Ehrentafel und Pjotrs Zettel. Pjotr geht nach Magadan, niemand stirbt. **Der Nutzer muss das noch bestätigen.**
  - **Bewusst weggelassen:** Speichern des Fortschritts. Funde einer späteren Aufgabe zählen, sobald die Story dort ankommt.
- **Taste E:** war im Flugmodus „hoch“. Jetzt geht es dort nur mit der Leertaste nach oben, E ist zum Ansehen frei.
- **Prüfung (2026-11-08, Nachmittag)**
  - **Lauftests im Spiel:** 19/19 Wege kommen durch. Das sind 3 Story-Wohnungen × Wohnzimmer, Küche, Schlafzimmer und Bad, dazu Treppenhaus bis zum Zwischenpodest, 2 Nachbarwohnungen, Kesselhaus, Telefonzentrale (2 Wege) und Stollen bis vor den Bruch.
  - **Erster Lauf: 9 echte Blockaden, alle behoben.**
    - Die offene Kühlschranktür stand in der Küchentür.
    - Die Badtür war mit 0,8 m zu eng für die Spielfigur (Breite 0,68 m), jetzt 0,95 m.
    - Im Weg standen außerdem Telefonablage, Kanister, Sessel und Umzugskartons.
  - **Automation:** 8/8, davon neu 3 Tests unter `Kadyktschan.Story.*`.
  - **Weidenbusch in Orlows Wohnzimmer:** Die tiefen Wohnungen ragen bis zu 1,5 m über das vereinfachte Blockout-Rechteck hinaus, und ein Weidenbusch direkt vor der Fassade wuchs durchs Fenster bis an den Schreibtisch. Fix: `scatter_vegetation.in_section` hält die eingerichteten Abschnitte plus 2 m frei.
  - **Bücherregal:** Die Bücher steckten in einem massiven Block. Jetzt hat das Regal eine offene Front.
  - **Marker:** Draußen zeigt er auf den Hauseingang, drinnen auf den nächsten Fund. „Drinnen“ heißt: deutlich näher am Fund als die Tür.
  - **Belegbilder:**
    - `2026-11-08-story-*.png`: Start, Hinweis, Text, Notizbuch, Orlow-Schlüssel, Gorbunow, Kesselhaus, Finale
    - `2026-11-08-shadow-blink-before.jpg`
    - Editor-Bilder der Räume, des Häuschens und des Stolleneingangs

## 2026-11-08 (Nachmittag 2) – Nutzer: dramatischere Story, echte Details, Fehler in den Häusern

- **Fehler aus dem Nutzer-Bild (Antoninas Wohnzimmer)**
  - Der Wandteppich lag 2 cm in der Wand und flackerte. Jetzt hängen alle Wandbilder vor der Wandfläche (−5,92).
  - Die Kissenpyramide schwebte 12 cm über der Matratze.
  - Die Griffe der niedrigen Anrichte standen über der Oberkante. Die Griffhöhe richtet sich jetzt nach der Schrankhöhe.
  - Der weiße Kalender war auf der weißen Wand unsichtbar.
- **Echte Bilder statt Kästen**
  - `story_textures.swift` (AppKit, kyrillische Schriften) zeichnet 15 Bilder:
    - beide Kalender
    - Brigadefoto: weich gezeichnet, sepia
    - Schlüsselbrett-Beschriftung
    - Zettel und Brief
    - Bescheid der Verwaltung
    - Schichtbuchseite
    - Stollenplan
    - Kesselbuch und Funk-Logbuch
    - Lidas Zeichnung
    - Familien- und Witwenfoto
  - **Material:** Material-Slot `Pic_<Name>` (optional `@90/180/270` für liegende Blätter) → `MI_Pic_<Name>` aus `M_Picture`.
  - **Bildkoordinaten:** Das Bild füllt die Fläche einmal, aufrecht und nicht gespiegelt (`build_t5_kit.pic_uv`).
  - **Schlüssel:** echte 3D-Schlüssel mit Ring, Schaft und Bart an Haken über der Beschriftung, der Torschlüssel fehlt.
- **Story dramatischer** (Details in `design/narrative/story-places.md`)
  - Räumungsbescheid, ein Winter bei −52 °C, Rettungshubschrauber, Einsturz im Stollen mit Funkstille.
  - Am Ende überlebt Pjotr und klettert durch den Wetterschacht hinaus.
  - **Neue Funde:** `gorbunov_order`, `orlow_plan`, `mine_vent`. Entfallen: `gorbunov_table`, ist jetzt Dekoration.
  - **Stollen:** Wetterschacht (Rahmen, Leiter, Handabdrücke), Feldtelefon mit Kabel in den Einsturz, Zettel als Bild.
- **Prüfung:** 19/19 Lauftests nach dem Umbau.
  - **Bilder im Spiel:** lesbar, aufrecht, nicht gespiegelt; liegende Blätter zeigen ihr Bild (Nahaufnahmen `story-page-close`, `story-note-close`).
  - **Korrektur:** Der Stollenplan hing halb hinter dem Bücherregal und hängt jetzt daneben.
  - **FBX:** wandelt `@` im Slotnamen in `_` um, `place_*` kennt beide Schreibweisen.

## 2026-11-09 – Nutzer: Englisch, Hauptmenü mit Titelbild, Einrichtung zu eckig

- **Englisch**
  - Alle Texte stehen als Paar Deutsch/Englisch im Code (`KdkLoc`).
  - **Schaltet die Sprache um:** Einstellungsmenü, Hauptmenü, Aufgabe, Hinweis, Textfenster, Notizbuch und Karte.
  - **Story:** Die Story-Texte bekommen `*_en`-Felder (`tools/research/story_data.py`), die Karte bekommt `name_en`.
  - Die Sprache wird gespeichert (`UKdkGameUserSettings::Language`) und lässt sich in Hauptmenü und Einstellungen umschalten.
  - **Bewusst nicht** über Unreals Localization-Dashboard: Für zwei Sprachen und einen Entwickler wäre das zu viel Aufwand.
- **Hauptmenü (`SKdkMainMenu`)**
  - **Titelbild:** das Bild des Nutzers, schwarzer Balken und FPS-Anzeige entfernt, Lärchen-Silhouetten an den Rändern und Gestrüpp im Vordergrund (`tools/asset-pipeline/title_image.swift` → `Content/Kadykchan/Data/UI/Title.png`).
  - **Menüpunkte:** Spiel starten, Einstellungen, Sprache, Beenden. Das Spiel ist pausiert, solange das Menü offen ist.
  - **FPS-Anzeige:** im Menü ausgeblendet.
  - **Dev-Läufe:** Mit `-KdkStart/Shot/Walk/Story` oder `-KdkNoMenu` startet das Spiel ohne Menü. `-KdkEnglish` stellt einen Lauf auf Englisch. Eine Option `-Lang=` blockierte den Engine-Start.
- **Einrichtung weniger eckig:** Alle Möbelmaterialien bekommen gefaste Kanten (`Part.bevel_box`, Stärke je Material in `interiors.BEVEL`).
  - Polster, Kissen und Matratzen sind stark gerundet (4–4,5 cm), Holz, Emaille und Heizkörper leicht (1–2,5 cm).
  - Wände, Böden und Bilder bleiben scharfkantig.
- **Prüfung:** Bilder `2026-11-08-story-menu*.png`, `-reader-en`, `-notebook-en`, `-sofa`.
  - **Aufnahmeskript:** nimmt jetzt nur das Fenster des eigenen Spielprozesses auf (`winid <pid>`), denn ein zweites Spielfenster des Nutzers lief parallel.

## 2026-11-09 — Inneneinrichtung: weichere Formen, Stoff und Furnier (Nutzerauftrag)

- **Auftrag:** Einrichtung weniger eckig und langweilig; fertige Assets ausdrücklich erlaubt.
- **Entscheidung:** Bestehende Möbel-Bauer überarbeiten, damit Größen und Fundpositionen erhalten bleiben. Gewölbte Polster, gefaltete Decken/Vorhänge, gebogene Stuhllehnen, verjüngte Tischbeine, erkennbare Nähmaschine und gewölbte TV-Bildschirme. Keine externen Assetpakete erforderlich.
- **Material-Ursache:** Sofa/Vorhänge nutzten Concrete_A, Schrankholz PaintWood_A. Eigene Fabric_A/Veneer_A erzeugt, jeweilige D/N/ORM; Farben bleiben aus der vorhandenen Palette.
- **Technik:** Markierte gekrümmte Flächen werden weich schattiert und beim Zusammenfügen erhalten. FBX-Import übernimmt Normalen. Runde Möbelteile benutzen jetzt die vorhandene Spiegelung von FlatView.
- **Übernahme:** tools/rebuild_interiors.sh und tools/editor/refresh_interiors.py für fünf betroffene Häuser; bestehende Assets werden vor dem Import gesichert. Kein vollständiger Welt-Neuaufbau nötig.
- **Geprüft:** 4 Geometrietests bestanden; alle 14 Gebäude-Fundpositionen vor/nachher gleich; vereinfachte Geometrievorschau angesehen. Beleg: production/qa/evidence/2026-11-09-furniture-geometry-comparison.png.
- **Status ausdrücklich offen:** Blender scheitert hier vor dem Bauen beim Metal-Start (Exit 139); Unreal-Start ebenfalls nicht verfügbar. Die neuen Möbel sind noch NICHT in die Spiel-uassets importiert, der Import-/Lauftest und die Leistung sind nicht verifiziert. Nutzer hat den Aktualisierungsbefehl fürs normale Terminal erhalten. Details: production/qa/interior-update-2026-11-09.md.
- **Rückweg:** Ausgangsquellen liegen separat unter /private/tmp/kadyktschan-interior-update/original; vor dem späteren Import gibt es zusätzlich Saved/InteriorUpdateBackups. Kein Commit.

## 2026-11-09 — Material-Import nach Nutzerlauf korrigiert
- Nutzer führte tools/rebuild_interiors.sh aus: BUILDINGS OK 5; alle fünf Gebäudemeshes und sechs Texturen wurden gespeichert. Danach RESULT FAILED bei der ersten Materialzuweisung.
- Ursache im installierten Engine-Quellcode bestätigt: UMaterialEditingLibrary::SetMaterialInstanceTextureParameterValue initialisiert bResult mit false und gibt es auch nach erfolgreicher Zuweisung unverändert zurück (MaterialEditingLibrary.cpp:1507). Mein Skript hatte diesen Rückgabewert als Erfolgskriterium verwendet.
- Korrektur: Textur muss geladen sein; nach dem Setzen wird der tatsächliche Parameterwert mit GetMaterialInstanceTextureParameterValue zurückgelesen und verglichen. Prüfung bleibt erhalten. Noch kein erfolgreicher erneuter Unreal-Lauf. Kein Commit.

- **Bestätigung nach erneutem Nutzerlauf (2026-11-09 ~14:49):** Importbericht RESULT OK, Blender BUILDINGS OK 5. Zwei Nutzerbilder bestätigen die neuen Formen und Holzoberflächen in Antoninas Wohnung. Kein vollständiger Lauf-/Leistungsnachweis. Belege: production/qa/evidence/2026-11-09-user-interior-{kitchen,living}.png.

## 2026-11-09 — Kulturhaus und Wege realistischer (Nutzerauftrag)
- Nutzer erlaubt weitere fertige Assets für Saal, Umgebung und Wege. Saal-Sitze, Vorhangreste, Putzschutt und Kronleuchter überarbeitet; Mittel-/Quergang freigehalten. Gebäude und Stadtlayout bleiben die bisherigen.
- Gewählte fertige Oberflächen: Poly Haven gravel_road, forest_floor, wood_floor; offizielle Seiten und CC0-Lizenz geprüft. Jeweils 2K-Diffuse/DirectX-Normal/Roughness. Holz wird matt/entsättigt. PBR-Originale ersetzen keine historischen Referenzfotos. Noch NICHT heruntergeladen.
- Wege variieren um maximal acht Prozent, bleiben am gerenderten Terrain. 120 kollisionsfreie Bodendetailflächen neben Straßen vorbereitet, keine neuen Bäume oder Gebäude.
- 5 Möbel-/Saaltests und 3 Umgebungsprüfungen bestanden. Vereinfachte Geometrievorschau angesehen; kein Spielbild. Aktualisierung: tools/rebuild_environment.sh, mit Sicherungen und frischem RESULT-OK-Bericht.
- Offen: Download scheitert hier an DNS, Blender/Unreal hier nicht nutzbar. Download, Import, Sicht-/Lauftest und Leistung stehen für diesen Ausbau aus. Bericht production/qa/environment-update-2026-11-09.md. Kein Commit.

## Nachtrag: erster Nutzerlauf

Alle neun Poly-Haven-Dateien wurden heruntergeladen; SHA-256 stimmt mit downloads.json überein. Blender meldet BUILDINGS OK 1 und der Kulturhaus-Mesh wurde importiert. Anschließend Abbruch in scanned_surfaces.apply: invalid material pin: Input. Im installierten UE-Quellcode bestätigt: UMaterialGraphNode::GetShortenPinName wandelt Input in NAME_None um (MaterialGraphNode.cpp:610). Die beiden betroffenen Verbindungen verwenden jetzt den ersten Eingang über den leeren Namen. Der Außenbericht übernimmt außerdem kein zwischenzeitliches RESULT OK des Saal-Importers mehr. Erneuter Import und vollständiges RESULT OK stehen aus.

## Erfolgreicher Nutzerlauf, 2026-11-09 ~16:59

Frischer Bericht refresh_environment_report.txt endet mit RESULT OK. Backups: EnvironmentUpdateBackups/20261109-165839-798699 und InteriorUpdateBackups/20261109-165840-520573. Download, Kulturhaus-Import, Scanmaterialien sowie Straßen-, Fußweg- und Wegesrand-Import sind durchgelaufen. Endgültige Darstellung, Begehbarkeit und Leistung im Spiel sind noch nicht durch neue Spielbilder/Lauftests bestätigt.

## 2026-11-09 — Asphalt statt glatter Bänder, differenzierter Bewuchs
- Nutzer verlangt nach seinem Spielbild ausdrücklich Asphalt, weiße Linien, Risse und Verwahrlosung; zwei Luftbilder als Vegetationsreferenz. Hauptstraßen erhalten Poly Haven Asphalt 02 (offizielle CC0-Seite geprüft), 14 OSM-Tracks bleiben unbefestigt. Eigene RoadWear-Masken für große Schäden und verblasste Markierungen; Markierungen sind eine nutzergewünschte Annahme.
- Drei zusätzliche Wuchsformen, neue Blattatlanten und Palette für verschiedene Buschhöhen; mehr niedriger Bewuchs in Gruppen, breitere Lärchenkronen. 876 niedrige Pflanzen rücken unter Gebäude-/Fluss-/Eingangsschutz an Straßenränder. Im Offline-Entwurf 200314 → 196875 Pflanzen, 19 → 28 Layer; Gras, Gebäude und Requisiten bleiben erhalten.
- 8 relevante Prüfungen bestanden, reale Straßen- und Verteilungsdaten offline geprüft, Material-/Geometrievorschauen angesehen. Noch NICHT in Unreal importiert oder im Spiel gesehen. Neue Downloads/Editorstart hier weiter nicht möglich.
- Neuer gezielter Aktualisierungsbefehl tools/rebuild_streets_nature.sh mit Quell-/Asset-Sicherungen. Details und Grenzen: production/qa/streets-nature-update-2026-11-09.md. Kein Commit.

## Erfolgreicher Nutzerlauf – 2026-11-09 ~17:38

refresh_streets_nature_report.txt endet mit RESULT OK (Backup StreetsNatureAssetBackups/20261109-173736-776050). NATURE MESHES OK 28, zwölf Scans vorhanden. Asphaltstraße MI_Road, unbefestigte Tracks und Fußwege MI_Path sowie Wegesrandflächen übernommen. 28 instanzierte Layer mit 196875 Pflanzen gespeichert; Gras-/Requisitenzellen wurden nicht ersetzt. Neue Spielbilder, Laufprüfung und Bildrate bleiben offen.


### 2026-11-09 — Maus und Trackpad: macOS-Eingabeweg
- Nutzer: Kamerabewegung fehlt; erneutes Einstecken hilft nur der externen Maus. Fehler bestand vor dem Straßen-/Vegetationsupdate.
- Codeprüfung: UE 5.8 nutzt standardmäßig `Slate.MacUseNewMouseControllerMovement=1` (GCMouse im High-Precision-Modus). `ProcessMouseMovedEvent` ignoriert dabei normale AppKit-Bewegungen, außer während der Wiederzuordnung. Das passt zum Fehlerbild, ist noch kein bestätigter Hardware-Nachweis.
- Änderung: `Config/Mac/MacEngine.ini` setzt den vorhandenen Startschalter auf 0. Dadurch läuft relative Bewegung über AppKit für Maus und Trackpad. Keine Engine-Änderung, keine Änderung der persönlichen Einstellungen.
- Prüfung: INI-Wert, vorhandener Engine-Schalter, AppKit-Fallback und Ladefolge vor Plattforminitialisierung geprüft. Kein C++-Build notwendig. Hardwaretest ausstehend; hier kein funktionierender interaktiver Unreal-Start.
- Abnahme: Spiel vollständig beenden und neu öffnen; Maus bereits vor dem Start anschließen. Nach Spielstart Maus und Trackpad einzeln prüfen, anschließend Einstellungen öffnen/schließen und nach App-Wechsel erneut prüfen. Empfindlichkeit kann sich mit dem Eingabeweg ändern.


### 2026-11-09 — Auftrag: Straßen beruhigen, Hindernisse beseitigen, Notstrom als Startmission
Ursachen anhand Generatoren gefunden: kombinierte Breiten-/Randwellen plus breite Opacity-Maske; Heizungsrohre wurden nur gegen Fassaden statt gegen alle Straßen geprüft. Breitenwellen auf Zentimeter reduziert, Randmaske eingegrenzt und Rohre an Kreuzungen getrennt.
Neues, ausdrücklich vom Nutzer gewünschtes fiktives Elektrizitätswerk nahe dem Start (E340/N75) mit Diesel-Notstromkreis und drei geordneten E-Interaktionen. Erst Abschluss schaltet warmgelbe Straßen-/Wohnungslampen frei. Langsame individuelle Aussetzer und dauerhaft defekte Leuchten; maximal 16 nahe Lichtquellen. Kein historischer Kraftwerksstandort behauptet. Vorhandene Story folgt auf die neue Aufgabe; Karte erweitert.
Quelländerungen vorbereitet, noch nicht in Unreal importiert. Zehn Offline-Tests und fünf native Zustandsprüfungen bestanden. C++-Gesamtbuild vor Kompilierung durch Sandbox-Zugriff auf UBT-Trace blockiert. Installation über tools/rebuild_power_roads.sh im normalen Terminal; keine Spielabnahme oder Leistung behauptet. Details und Abnahme: production/qa/power-roads-update-2026-11-09.md. Keine Git-Befehle, keine persönlichen Einstellungen überschrieben.


### 2026-11-09 — Elektrizitätswerk-Update erfolgreich gebaut und importiert
Nutzer führte tools/rebuild_power_roads.sh aus. Protokolle geprüft: C++ Result: Succeeded (9,71 s), POWER MESH OK 2149, VEGETATION OK (14 Gras-/17 Requisitenzellen, 28 instanzierte Schichten, 196822 Pflanzen), refresh_power_roads_report.txt endet RESULT OK. Straßen und Zugangswege importiert, Werk und Lichtmaterial gespeichert. Assetbackup: Saved/PowerRoadAssetBackups/20261109-180600-278644. Spielabnahme von Mission, Straßen, Licht und Leistung weiterhin offen; UE-Automation nicht ausgeführt.


### 2026-11-09 — Lampensichtweite und Dämmerung korrigiert
Nutzer meldet späte Lampenbeleuchtung sowie hellen Boden bei Dämmerung 100 %. Ursache im Code: AKdkTownPower aktivierte nur 16 nächste Lichtquellen innerhalb 100 m; AKdkSkyCycle dimmte das direkte Sonnenlicht, ließ die SkyLight-Intensität aber unverändert.
Änderung: Entfernungs-/Anzahlabschaltung entfernt, alle funktionierenden Leuchten folgen dem Stromzustand; normale Sichtfeld-/Größenprüfung des Renderers bleibt. r.MinScreenRadiusForLights von Engine-Standard 0,03 auf 0,01 reduziert. Keine Vergrößerung des physikalischen Lichtkegels oder Leuchtradius. Bei voller Dämmerung Sonne -4 Grad, direkte Intensität 3 %, Himmelslicht 4 %, Nebelluminanz 15 % des geladenen Tageswerts. Regler 0 bzw. Dämmerung aus stellt gespeicherte Tages-Basiswerte wieder her. Helligkeitsregler bleibt erhalten.
Prüfung: originale EvaluateSkyCycle-Funktion mit clang++ separat kompiliert, Tageswerte, Dämmerung, Zwischenwerte, Clamping und Rückkehr geprüft. UE-Automation SkyCycle.DuskDimsSunAndAmbient ergänzt; noch nicht ausgeführt. Entfernung/Anzahlabschaltung und gemeinsamer Zustand für Leuchtkörper/Lichtquelle statisch geprüft. UE-APIs gegen installierte Header geprüft.
Vollständiger UE-Build und Spielprüfung offen (bekannte Sandbox-Sperre für UBT-Trace). tools/play.sh kompiliert beim nächsten normalen Start automatisch; kein erneuter Asset-/Vegetationsimport nötig. Mehr gleichzeitig sichtbare Lichter können Bildrate kosten; tatsächliche Leistung und Dämmerung im Spiel noch prüfen. Keine Git-Befehle und keine persönlichen GameUserSettings geändert.


### 2026-11-09 — Wohnhäuser mehrgeschossig, Wald und Höfe detailliert
Nutzer wünscht dichteres Stadtumfeld und Wald, mehr ausgestattete Häuser mit mehreren möblierten Etagen, erkennbare Sperren vor unfertigen Bereichen und nachvollziehbare Einrichtung statt Stückzahl.
Vorbereitet: fünf bestehende Wohnhäuser (Lenina 7/8 EG–2. OG; Gorbunow und Schkolnaja 4/6 EG–1. OG), 24 Wohnungen mit sechs Haushaltsprofilen und erhaltenen Storyräumen. Vollständige Treppen, korrigierte Deckenöffnungen und Kopffreiheit, sichtbare Sperren an unfertigen Zugängen. Keine zusätzlichen Wohngebäude erfunden. Waldprobe rund 80.000 zusätzliche große Lärchen plus Unterwuchs, 71 Hofgruppen; Straßen/Zugänge/Stollen/Elektrizitätswerk frei. Neue Lampenpositionen aus den echten Leuchten exportiert, Spiegelung korrigiert.
Teilneubau aktualisiert nun das Manifest unter Erhalt anderer Häuser; zentrale Materialzuordnung und Glasimport ergänzt. Bestehende BUILDINGS-OK-Zählung kompatibel gehalten. Neues Update: tools/rebuild_neighbourhood.sh.
Offline: 18 unterschiedliche Tests sowie vollständige Gebäudezusammensetzung mit Treppen-/Deckenprüfung. Bestehende Story-Fundpositionen unverändert. Noch KEIN echter Blender-Export/Unreal-Import, kein Ingame-Lauftest und keine Leistungsmessung. Nächster Schritt: Nutzer führt Update bei geschlossenem Spiel/Editor aus; danach Saved/NeighbourhoodLogs und tools/editor/refresh_neighbourhood_report.txt prüfen.
Details: design/art/neighbourhood-interiors.md; production/qa/neighbourhood-update-2026-11-09.md; schematischer Grundrissbeleg production/qa/evidence/2026-11-09-residential-floorplans.svg (kein Spielbild). Keine Git-Aktionen oder Änderung persönlicher Einstellungen.


### 2026-11-10 — Nachweis des vorherigen Wohnhaus-/Waldimports
Vor der Kartenkorrektur aktuelle Protokolle geprüft: NeighbourhoodLogs/build.log Result: Succeeded; verification.txt RESULT OK (24 Wohnungen, 190723 Lärchen, 71 Hofgruppen). refresh_neighbourhood_report.txt RESULT OK, 292188 instanzierte Pflanzen, Assetbackup 20261109-222439-980075. Der Ausbau ist also bereits importiert; das aktuelle Nutzerbild bestätigt die zusätzlichen Kartenorte. Spielabnahme aller Wohnungen/Leistung weiterhin nicht vollständig erfolgt.


### 2026-11-10 — Kartenbeschriftung, Einrichtungskarte und Fernwald vorbereitet
Nutzerbild: schwebende/überlappende Namen; Wunsch nach genauer Einrichtungskarte in den Einstellungen und dichterem Wald auch aus der Ferne. Stadtkarte erhält nummerierte, kollisionsfrei angeordnete Markierungen mit Verbindungslinien und fester Namensliste. Einrichtungskarte als eigener pausierter Menübildschirm: fünf Häuser, offene Eingänge, Etagen und linke/rechte Haushalte; Zurück/Esc führt in die Einstellungen. Kartendaten aus realem Manifest; Orlows bisher falsch angenommener Eingang korrigiert und Story-Eingang synchronisiert.
Wald: höhere Blattflächenabdeckung der Fernmodelle, längere Sichtweite für Birken/junge Lärchen/Weiden/Erlen, spätere Mindestbildgrößen-Abschaltung und Alpha-Flächenerhalt in den vier Blatttexturen. Lärchen ohne feste Abschaltdistanz wie zuvor. Kein erneutes Verdichten oder Umbauen der Häuser.
C++-Syntaxprüfung mit echten UE-Headern für drei geänderte Implementierungen und Kartentests erfolgreich. Native Markerfunktion mit 5/11/30 Punkten geprüft; vier neue Offline-Tests und drei Nature-Regressionstests bestanden. Vollständiger Build/Link, Blender-Export, Import und Spielansicht offen. Nutzer führt tools/rebuild_map_forest.sh bei geschlossenem Spiel/Editor aus; danach Saved/MapForestLogs und tools/editor/refresh_map_forest_report.txt prüfen. QA: production/qa/map-forest-fix-2026-11-10.md. Mehr Fernvegetation kann Leistung kosten; noch nicht gemessen. Keine Git-Befehle, persönliche Einstellungen erhalten.


### 2026-11-11 — Dokumentation und Übergabeeinstieg aktualisiert
Nutzer fragt nach vollständiger Dokumentation für Claude Code. Entscheidungslog, aktive Chronik und QA-Berichte waren vorhanden; HANDOFF.md hatte jedoch weiterhin veraltete Status-/Auftragsangaben vom 2026-11-07. Aktuelle Übergabe production/session-state/handoff-2026-11-11.md erstellt und an den Anfang von HANDOFF.md sowie in CLAUDE.md verlinkt. Historie erhalten, überholte Einschränkungen von aktuellen Nutzeraufträgen unterschieden.
Aktuelle MapForest-Protokolle geprüft: C++ Succeeded, NATURE MESHES OK 28, Import RESULT OK (Backup 20261110-082516-873887), 292188 Instanzen. Das Update ist importiert; vollständige Spielabnahme und Bildratenmessung weiterhin offen. Keine Gameplay-/Assetänderung in diesem Dokumentationsschritt, keine Git-Befehle.


### 2026-11-11 — Shooter-Modus „Einsatz“ (Plan freigegeben, umgesetzt)
Nutzerauftrag: Shooter-Modus mit Gegnern, Leben über die Videokamera, Wohnungen mit Funktion, Bodycam-Gefühl, passende Hindernisse; Story bleibt. Nutzerentscheidung: Gegner = bewaffnete Plünderer + Maschinen (später evtl. eigene Maschinen bauen), Runde = Einsatz mit Aufträgen und Abholung. Design: design/gdd/shooter-mode.md.
- Gleiche Welt statt eigener Karte: AKdkShooterDirector erzeugt Hindernisse, Funde, Gegner und Navigationsbereich zur Laufzeit als eigene Komponenten und entfernt sie danach. Die Story-Karte und der Story-Fortschritt bleiben unberührt.
- Navigationsnetz nur zur Laufzeit (RecastNavMesh Dynamic) im Spielbereich; das Begrenzungsvolumen bekommt einen Box-Körper statt Editor-Pinselgeometrie. Erster Test: 0/24 Wohnungen erreichbar (19-cm-Raster und 34-cm-Radius fraßen Treppen und Türen auf) → 12 cm / 24 cm: 15/24, Aufbau 4–6 s. Schkolnaja 4/6: Außentreppen weiter nicht im Netz, Ursache offen (bekannte Grenze).
- Leben = Bildqualität: Verpixelung, Unschärfe (Tiefenschärfe mit großem virtuellen Sensor, weil 100°-Weitwinkel sonst alles scharf hält) und Kamerastärke wachsen ab den Reglerwerten des Nutzers; seine gespeicherten Einstellungen werden nie geändert.
- Funde nach Haushalt (residential.HOUSES): Verbandszeug/Verbandskasten/Munition/Weste; Verband bei vollem Leben bleibt liegen.
- Hindernisse aus vorhandenen Blender-Bauteilen (build_vegetation: Autowrack, Schrott, Schutt) plus neue: Plattenstapel, Betonzaun, LKW, Bus, Barrikade, Kabeltrommeln. Straßenslalom alle 17 m, Höfe im 20-m-Raster, Türen 5 m frei.
- Balance nach erstem Spieltest: Startpunkt lag neben Gegnern (Tod nach 5 s) → 55 m sicherer Radius; Plünderer 22 → 14 Schaden; Geschütz 16×6 → 11×5 (Warnton muss Zeit für Deckung lassen).
- Gegner-Optik ANNAHME: UE-Mannequin mit unbewaffneter Animation und angehängtem Gewehr (shortcut, im Code markiert), bis eigene Plünderer-Modelle kommen.
- Ethik: keine realen Personen, kein Story-Bezug, kein Blut. Das Konzept („Deduktion ohne Kampf“) gilt weiter für den Story-Modus; der Einsatz ist ein getrennter Modus auf Nutzerwunsch.
- Nachtrag nach Nutzertest (11.11.): klares Bild bei vollem Leben (Reglerwerte der Story gelten im Einsatz nicht, Fischauge entfernt); Fadenkreuz mit Streuungsabstand; Treffer- und Ausschaltmarker mit Klick; Deckung mit Q nach RDR2-Vorbild (niedrige Deckung: ducken, Rechtsklick taucht auf). Desktop-Build schlug fehl, weil die Unity-Bündelung zwei Dateien mit gleichnamigen Farbkonstanten zusammenlegte → bUseUnity = false im Build.cs.
- Zweiter Nutzertest (11.11.): Unschärfe beim Zielen war ein Fehler (enger Bildwinkel = längere Brennweite, schon kleiner Schaden machte alles unscharf) → Unschärfe ∝ D², Sensor mit tan(FOV/2) skaliert, pro Frame gesetzt. Regeneration Leben 1,5/s, Sicht 12/s nach 5 s; Treffer setzt Sicht auf Leben. Stirnlampen für Plünderer, Trefferrichtungs-Bögen (Fortnite), rote Aura, lautere geschichtete Schüsse mit Echo. Deckung neu: Kamera unter die Kante, Zielen schaut darüber bzw. seitlich vorbei; Gegner prüfen Kopf (Kamera) und Brust. Deckungsprüfung in drei Höhen (Plattenstapel haben Lücken).
- Dritter Nutzertest (11.11.): Gegnerlogik „grauenhaft“ (sehen und schießen sofort von weit weg, bleiben stehen). Neu: entfernungsabhängiges Bemerken, Feuer nur bis 32 m, Kampfstellen 12–26 m (Deckung mit Spähpunkt bevorzugt, verteilt), Verstecken/Herausschauen bzw. Seitschritte, Stellungswechsel mit Flankieren, höchstens zwei gleichzeitige Schützen, Suche bei Sichtverlust; Drohnen Zickzack bis 5–12 m. Kontakttest: Bemerken auf 41–51 m, Deckungen 13–18 m, ungedecktes Stehen verloren nach 26 s / 12 Treffern.
- Dynamische Grafik im Einsatz (Nutzerwunsch 11.11.): 4 Stufen (Auflösung, dann Schatten/Pflanzen, Reflexionen/Effekte/GI ≥ 1, Sichtweite), Ziel 45 FPS aus Shooter.json. Fehler im ersten Test: Die Engine speichert beim Beenden die aktuellen Grafikwerte → GameUserSettings.ini des Nutzers bekam Schatten 1 / Pflanzen 2. Sofort auf die beim Sitzungsbeginn gelesenen Werte (2 / 3) zurückgesetzt; UKdkGameUserSettings::SaveSettings schreibt seither während einer abgesenkten Stufe die Originalwerte. Zweiter Test: Datei unverändert.
- Nutzer 11.11.: Grafikstufen senken jetzt auch die Einstellungen ab Stufe 1 (relativ zu den eigenen, mit Untergrenzen; Schatten nie aus). Gegner, die treffen, werden 2 s markiert. Test: Stufe 1/2 mit Einstellungen, Einstellungsdatei unverändert, Markierung sichtbar.
- Nutzer 11.11.: „es wird nur alles unscharf und die Settings ändern sich nicht“. Ursache: die gespeicherten Grafikstufen sind mit Spieleinstellungs-Priorität geladen, Scalability::SetQualityLevels schreibt ohne bForce mit niedrigerer Priorität und wurde ignoriert; nur die Auflösung (eigener Weg) sank. Jetzt bForce, aktive Werte zurückgelesen und protokolliert; Auflösung erst ab Stufe 3 (0,85/0,75).
