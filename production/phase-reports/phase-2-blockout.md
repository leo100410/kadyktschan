# Phase 2 · Gelände, Lageplan und Blockout

*Stand: 2026-11-07 · Status: **Freigegeben** (Nutzer, 2026-11-07)*
*Briefing: PDF V3, V12 Phase 2 · Grundlage: `design/research/phase-1-dossier.md` (freigegeben)*

## Ergebnis

Die Karte `/Game/Kadykchan/Maps/Kadykchan_World` (World Partition) enthält die ganze Stadt im
Maßstab 1:1. Sie ist Start-Karte im Editor und im Spiel; man spawnt im Hof zwischen
ул. Ленина 7 und 8 und kann frei herumlaufen.

| Inhalt | Umfang | Quelle | Kennz. |
|---|---|---|---|
| Gelände | 8 × 8 km, 30-m-Raster, Höhen relativ zum Ursprung (803,9 m) | Copernicus DEM GLO-30 | BELEGT (Höhen) / ANNAHME (Bodenfilter, s. u.) |
| Straßen | 53 Linien: Trasse „Колыма“, alte Kolyma-Trasse, Stadtstraßen, Wege | OpenStreetMap | BELEGT / Mittel |
| Fluss | река Кадыкчан (2 Abschnitte) | OpenStreetMap | BELEGT / Mittel |
| Gebäude | 47 Blockout-Quader, je Adresse benannt (`PLA_Lenina_8` …), Ordner nach Straße | OSM-Grundrisse | Lage BELEGT / Höhe ANNAHME |
| Licht | Sonne (flach, Weißnacht-Sommer), Sky Atmosphere, Sky Light, Height Fog, Volumetric Clouds | PDF V7 | – |
| Spielerstart | Hof ул. Ленина 7/8 | – | – |

**Achsen:** UE +X = Norden, +Y = Osten, 1 UE = 1 cm; Ursprung 63.085870 N / 147.050008 E (Dossier).

## Annahmen in diesem Schritt

| Wert | Annahme | Warum |
|---|---|---|
| Geschosshöhe | 2,8 m | Typenserie unbelegt (Dossier Frage 2) |
| Pfahl-/Luftraum unter dem Haus | 1,2 m | auf Fotos sichtbar, nicht gemessen |
| Dachrand | 0,6 m | – |
| Gebäude ohne Geschossangabe | 2 Geschosse; Industrie ohne Adresse 8 m | – |
| Bodenhöhe | 3×3-Minimum über 30 m auf dem DEM | Copernicus ist ein Oberflächenmodell (Häuser, Bäume enthalten); ohne Filter lag der Hof über dem Spielerstart |

## Abweichungen vom Briefing (vorläufig)

| PDF V3 | Stand | Grund / Plan |
|---|---|---|
| Höhenmodell als **Landscape** | Gelände ist ein **Static Mesh** | Landscape-Import ist per Skript in UE 5.8 nicht belegt; für den Blockout reicht das Mesh. Umstellung auf Landscape vor dem Detailbau (Phase 4) |
| Satellitenbild als Decal | nicht eingebaut | nur Editor-Referenz erlaubt (Lizenz); Quelle noch nicht gewählt |
| Straßen als **Splines** | Straßen als ein Bänder-Mesh | 1000 Einzel-Actors vermieden; Splines folgen mit dem Straßen-Kit |
| Data Layers `DL_2011`, `DL_Interiors` | noch nicht angelegt | `DL_1986` entfällt (Konzept); `DL_Interiors` kommt mit den ersten Innenräumen (Phase 3) |
| PCG-Vegetation | noch nicht | Teil des Vertical Slice (Phase 3) |
| Water-Plugin (Fluss) | Plugin aktiviert, Fluss als Band | Water ist in 5.8 **Experimental**; Entscheidung im Vertical Slice |
| Ein Packed Level Actor pro Adresse | Quader tragen schon die `PLA_`-Namen | echte PLAs entstehen aus den Kits (Phase 3) |
| Spatial Loading | Blockout-Actors „immer geladen“ | sonst im Editor unsichtbar und Gelände nach dem Spawn gestreamt; als `shortcut:` im Skript markiert |

## Screenshots (Engine)

- `production/qa/evidence/2026-11-07-phase2-blockout-overview.png`: Vogelperspektive von SW
- `production/qa/evidence/2026-11-07-phase2-blockout-lenina-courtyard.png`: im Spiel, Spielerstart im Hof ул. Ленина 7/8
- `production/qa/evidence/2026-11-07-phase2-blockout-lenina-eye.png`: Editor, Augenhöhe an ул. Ленина 8

## Asset-Liste

| Asset | Pfad | Budget |
|---|---|---|
| `Kadykchan_World` (+ HLOD-Layer) | `Content/Kadykchan/Maps/` | – |
| `SM_Terrain_Blockout` | `Content/Kadykchan/Maps/Terrain/` | 71 000 Dreiecke, kein Nanite, Complex-Collision |
| `SM_Roads_Blockout` | dto. | 1 200 Dreiecke |
| `SM_Rivers_Blockout` | dto. | 786 Dreiecke |
| 47 × Blockout-Quader `PLA_*` | Actors in der Karte | Engine-Würfel |

## Reproduzierbar

Alle Schritte sind Skripte; neu bauen in dieser Reihenfolge:

1. `tools/research/dem_to_obj.py` (Gelände-OBJ aus den DEM-Kacheln)
2. `tools/research/blockout_data.py` (Gebäude, Straßen, Fluss → JSON)
3. `tools/research/lines_to_obj.py` (Straßen-/Fluss-Bänder)
4. `tools/editor/build_blockout.py` im Editor (Karte bauen)
5. `tools/editor/editor_shots.py` (Kontrollbilder)

Die DEM-Kacheln selbst (2 × 20 MB) liegen nicht im Projekt; Quelle:
`https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N63_00_E14{6,7}_00_DEM/`.

## Performance (PDF V11)

**NOT ASSESSED.** Unreal Insights lief nicht. Auf dem Mac gemessene Werte wären keine Aussage
über das Ziel (Windows + RTX, 1440p). Die Messung gehört in den Windows-Build.

## Bekannte Probleme

- **UE 5.8 stürzt auf macOS 27 beim Beenden des Editors ab** (Slate/ICU-Teardown). Daten sind
  vorher gespeichert; die Skripte laufen mit `-unattended`, damit kein Absturzdialog erscheint.
  macOS 27 ist von UE 5.8 offiziell nicht unterstützt.
- Die Geländelinien aus OSM verlaufen teils durch Hänge (30-m-Raster, Bänder ohne Einschnitt).

## Offene Fragen

1. Satellitenbild als Editor-Referenz: Welche Quelle soll ich nutzen? (Vorschlag: Sentinel-2,
   frei, aber nur 10 m/px; besser aufgelöste Bilder nur zum Ansehen, nicht ins Projekt.)
2. Lage von ул. Ленина 18 und den Einrichtungen (Kulturhaus, Kesselhaus) ist ohne Satellitenbild
   nicht zu klären.

## Quellen

- Copernicus DEM GLO-30, © DLR e.V. 2010–2014 und © Airbus Defence and Space GmbH 2014–2018,
  bereitgestellt unter COPERNICUS von EU und ESA (Lizenztext noch nicht geprüft, Dossier Frage 4)
- OpenStreetMap, © OpenStreetMap-Mitwirkende, ODbL 1.0 (Abfrage 2026-11-07)
