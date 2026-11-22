# Phase 3 · Vertical Slice (Stand Zwischenbericht)

*Stand: 2026-11-07 · Status: **Grafikteil vom Nutzer freigegeben (2026-11-07)**. Offen für den Abschluss von Phase 3: Mechanik (Notizbuch-Thesen, Lampe, Kälte), Story-Gerüst und Ende, Speichern, Stadtplan, Windows-Build.*

**Spielen:** `Kadyktschan.uproject` doppelklicken (UE 5.8) → Karte `Kadykchan_World` öffnet sich → Play. Du startest
vor dem mittleren Eingang von ул. Ленина 8; das Treppenhaus und die beiden Wohnungen links/rechts sind begehbar.
*Briefing: PDF V12 Phase 3 „ул. Ленина, ein Block, zwei Wohnungen, Kulturhaus-Saal“ · Art Bible freigegeben*

Auf Wunsch des Nutzers (2026-11-07) zuerst **Grafik und Assets**, Mechanik und Story später.

## Ergebnis

| Bereich | Stand | Beleg |
|---|---|---|
| Plattenbau-Kit T5 | 12 Teile per Blender-Skript (Wand-, Fenster-, Eingangsplatte offen/zu mit Treppe und Vordach, Sockelband, Pfahl, Dachrand, Lüfter, Decke, Ecke, Doppelfenster, Glas) | `tools/asset-pipeline/build_t5_kit.py` |
| Alle 34 Adressen | aus OSM-Grundriss gerastert (3-m-Achsen), 1–9 Geschosse, Farbschemata, Eingänge mit Treppen, Hausnummern in Kyrillisch, Pfahlgründung | `town-overview.png`, `shkolnaya-street.png`, `mira-9storey.png` |
| ул. Ленина 7/8 (Hof) | L-Form Nr. 7, Nr. 8 in Mint/Altrosa nach Foto, drei Eingänge zum Hof | `lenina-courtyard-wide.png`, `lenina8-entrance.png` |
| Innenräume | mittlere Sektion Nr. 8: Treppenhaus + 2 Wohnungen mit V5-Requisiten | `lenina8-stairwell.png`, `lenina8-flat*.png` |
| Materialien | 4 Master (Building, Ground, Foliage, Glass) + ~45 Instanzen aus der Art-Bible-Palette, alle Texturen prozedural (Putz, Beton, Holz, Tapete, Teppich, Dielen, Blätter) | `tools/editor/build_materials.py` |
| Boden, Vegetation | Tundra-Material; 420 Birken, 1 500 Sträucher, 2 600 Lärchen | `ingame-player-start.png` |
| Spielerstart | vor dem mittleren Eingang von Nr. 8; Belegbild aus dem laufenden Spiel | `ingame-player-start.png` |
| Kulturhaus-Saal | in ул. Южная 9 (ANNAHME, U-Grundriss): Saal 24 × 15 m doppelt hoch, Bleiglasfenster, Fries, Bühne, Klappstühle, Zugang vom Hofeingang | `kulturhaus-back.png`, `kulturhaus-stage.png` |
| Wandbild (R3) | Figur im Pelzmantel + springendes Rentier auf dem Giebel von ул. Мира 1 (Gebäude ANNAHME), stilisiert | `mira_1-mural.png` |
| Hausnummern | Kyrillisch über dem ersten Eingang jedes Hauses („ЛЕНИНА 8“ …) | `lenina_8-house-number.png` |
| Laden „МАГАЗИН“ | Erdgeschoss ул. Школьная 3 (ANNAHME): Theke, Waage, Kasse, Regale mit Gläsern/Dosen, Schild in Kyrillisch | `shkolnaya3-shop*.png` |
| Verfall | herausgebrochene Platten an 11 Häusern, eine eingestürzte Ecke (ул. 50 лет Октября 7), Schutt an den Wänden, 15 % ausgebaute Fenster | `collapse-50let-7.png` |
| Straßenausstattung | Fernwärmerohre auf Stützen, Rosttanks am Industriegelände, Garagenreihe, 134 Betonlaternen, Bänke an Eingängen, 6 Spielplätze (Klettergerüst, Schaukel) | `shkolnaya-street.png`, `courtyard-playground.png` |
| Gras | ~9 000 Grasbüschel in den Höfen (Blattkarten) | `courtyard-playground.png` |
| Loggien, Erker | Loggien an 11 Wohnblocks, rosa Erker an ул. Ленина 8 | `collapse-50let-7.png`, `lenina8-street-bays.png` |
| Schule | ул. Школьная 1 (ANNAHME): Lisenen-Fassade mit großen Sprossenfenstern, Schieferdach | `school-shkolnaya-1.png` |
| Dächer | Satteldächer (Wellasbest) auf schmalen 2-Geschossern, sonst Flachdach mit Lüftern | `school-shkolnaya-1.png`, `town-overview.png` |
| Licht-Zyklus | Sonne läuft in 90 min vom Tag (40° Süd) in die Weißnacht (4° Nord); C++ + Data Asset + 4 Unit-Tests (grün) | `ingame-day.png`, `ingame-white-night.png`, `production/qa/test-run-2026-11-07.md` |
| Klang | Wind-Loop überall, Tropfen in Treppenhaus/Wohnung/Kulturhaus (prozedural) | – (Audio, nicht im Bild prüfbar) |

Alle Bilder liegen in `production/qa/evidence/2026-11-07-*.png`.

## Neu bauen

`DEM_DIR=<Ordner mit den 2 Copernicus-Kacheln> PYTHON=<python mit numpy/tifffile/imagecodecs> tools/build_world.sh`
baut alles von den Quelldaten bis zur fertigen Karte. Belegbild aus dem Spiel: `tools/ingame_shot.sh <png>`.

## Annahmen und Abweichungen

Siehe `production/decision-log.md` (jede autonome Entscheidung mit Grund und Rücknahmeweg). Die wichtigsten:
- Bauserie, Geschosshöhe 2,8 m, Achsmaß 3,0 m, Tiefe 12 m: ANNAHME (Fotomessung bzw. typisch).
- Fassadenfarben je Haus und Wohnungsgrundriss: ANNAHME.
- Häuser als ein Mesh pro Adresse statt Packed Level Actor (zur Laufzeit gleichwertig; Packen später).
- Dielen statt Fischgrät-Parkett; Hausnummern und Wandbild als Geometrie statt Decal.
- **Nanite für Gebäude aus** (auf diesem Mac zerlegt Nanite dünne Teile); Glas liegt schon getrennt, damit Nanite auf Windows wieder angeschaltet werden kann.

## Performance (V11)

NOT ASSESSED – Messung nur auf Windows + RTX aussagekräftig. Vegetation ohne Nanite und ohne HLOD,
alle Actors „immer geladen“: das ist der größte bekannte Posten für die Messung.

## Offene Fragen an dich

1. Kulturhaus: Ich habe ул. Южная 9 festgelegt (ANNAHME). Passt das, oder kennst du die echte Lage?
2. Sollen Mechanik/Story (Notizbuch-Prototyp) jetzt folgen oder erst weitere Gebäude-Innenräume?
3. Commit: Der Stand ist noch nicht in Git gespeichert.

## Freigabe (2026-11-07)

- Nutzer: Grafik/Assets von Phase 3 freigegeben, erster Commit angewiesen, Mechanik beginnt jetzt mit dem Notizbuch-Prototyp.
- Zu Frage 1 gab es keine Antwort; ул. Южная 9 bleibt ANNAHME. Frage 2: Mechanik jetzt. Frage 3: Commit erledigt.
- Einige Abschnitte oben stammen aus dem Zwischenstand von 06:10. Spätere Änderungen (Videokamera, Regler, Nebel, Verfallsstufen) stehen in `production/decision-log.md`.
