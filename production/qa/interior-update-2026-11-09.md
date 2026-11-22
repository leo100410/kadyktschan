# Innenräume: Formen und Materialien, 2026-11-09

## Status

Quellen und sechs neue Texturdateien erstellt. Blender-/Unreal-Import **noch nicht erfolgreich**; im Spiel gelten weiterhin die bisherigen uassets. Keine Freigabe als fertiger Spielstand.

Run result: NOT VERIFIED — Blender 5.2.3 endet vor Ausführung des Bau-Skripts mit Exit 139 im Metal-Start (`MTLBackend::metal_is_supported`). Unreal startet in dieser Ausführungsumgebung ebenfalls nicht bis zur Karte. Daher kein neuer Spiel-/Lauf-/Leistungsnachweis.

## Änderung

- Geschlossene, gewölbte Polster für Sofa, Sessel, Matratzen und Kissen; weiche Normalen bleiben beim Zusammenfügen und FBX-Import erhalten.
- Dünne gefaltete Decken mit herunterhängendem Saum, durchgehende gewellte Vorhänge statt einzelner Balken.
- Stühle mit gebogener Lehne und schlanken Beinen, Tische mit verjüngten Beinen und offenem Untergestell.
- Antoninas Nähmaschine mit offenem Nähbereich, Nadel, Garnrolle und Handrad; gewölbte Röhrenfernseher-Bildschirme.
- Eigene deterministische Stoff- und Furniertexturen mit Normal- und Rauheitskarten. Polster/Vorhänge nutzen nicht mehr Beton als Detailtextur.
- Gespiegelte Wohnungen: Runde Bauteile bleiben nun beim Möbelstück. `Place.cyl` und `Place.hcyl_u` benutzen die vorhandenen spiegelnden Section-/FlatView-Methoden.
- Keine externen Assetpakete heruntergeladen; keine zusätzlichen Abhängigkeiten.

## Prüfung

- `python3 tools/asset-pipeline/test_furniture.py`: 4/4 Tests bestanden. Geschlossene Oberflächen, nach außen gerichtete Flächen auch nach Spiegelung/Drehung, begrenzte Polster-Grundfläche und Übernahme weicher Normalen in das Gebäude.
- Alle fünf betroffenen Raummodelle ohne Blender als Geometriearrays aus den tatsächlichen Bau-Funktionen erzeugt. Alle 14 Gebäude-Fundpositionen stimmen mit dem gesicherten Ausgangscode überein. Die vier Stollen-Funde sind nicht betroffen.
- Bestehende fünf Gebäude-uassets gegen die vorherige Testkopie verglichen: noch unverändert. Import steht aus.
- Python-Syntax der geänderten Skripte und `zsh -n tools/rebuild_interiors.sh` bestanden.
- Neuer Aktualisierungsbefehl hier ausgeführt: Geometrietests und Texturerzeugung erfolgreich; beim Blender-Start angehalten. Unreal-Import wurde dadurch nicht begonnen.
- Geometrievorschau tatsächlich angesehen: rundere Polster und ein herunterhängender Deckensaum sichtbar. Dies ist ein CPU-Render der erzeugten Geometrie mit vereinfachten Farben, keine Unreal-Aufnahme und kein Nachweis der endgültigen Materialien oder Beleuchtung.

| Raummodell | Dreiecke vorher | nachher |
|---|---:|---:|
| lenina8 | 27428 | 38792 |
| lenina7 | 37572 | 47576 |
| family | 24876 | 31016 |
| boiler | 8044 | 8576 |
| radio | 11316 | 11848 |

Die Zahlen gelten für die eingerichteten Sektionen, nicht für komplette Gebäude. Die Bildrate wurde nicht gemessen.

## Belege

- `production/qa/evidence/2026-11-09-furniture-geometry-comparison.png` (oben vorher, unten nachher; vereinfachte Geometrievorschau)
- `production/qa/evidence/2026-11-09-furniture-geometry-before.png`
- `production/qa/evidence/2026-11-09-furniture-geometry-after.png`
- `Saved/InteriorUpdateLogs/blender.log` (fehlgeschlagener Start)

## Übernehmen

Unreal schließen, dann im normalen Terminal:

```sh
zsh "/Users/leolange/UnrealProjects/Kadyktschan/tools/rebuild_interiors.sh"
```

Der Befehl baut Lenina 8, Lenina 7, Gorbunows Block, Kesselhaus und Telefonzentrale. `refresh_interiors.py` ersetzt nur die vorhandenen Gebäudemeshes und drei Materialbelegungen. Es löscht keine Map-Actors, setzt den Spawn nicht zurück und baut Gelände/Vegetation nicht neu. Vor dem Import werden bestehende betroffene uassets und zugehörige ubulk/uexp nach `Saved/InteriorUpdateBackups/<Zeit>` kopiert. Ein frischer Bericht muss mit `RESULT OK` enden.

Danach im Spiel insbesondere Antoninas Wohnzimmer, Orlows Sessel und Gorbunows Sofa prüfen; Türen und alle Fundinteraktionen erneut testen. Import-Skript und endgültige Kollisions-/Materialdarstellung sind hier noch nicht in Unreal verifiziert.

Keine Story-Texte oder Nutzereinstellungen geändert. Keine Git-Befehle oder Commits ausgeführt.

## Nachtrag nach dem Nutzerlauf

Der Nutzer führte den Aktualisierungsbefehl aus. Blender: BUILDINGS OK 5. Unreal-Log belegt das Speichern der fünf Gebäudemeshes und sechs Texturen. Der Materialschritt endete mit RESULT FAILED bei MI_Int_Furniture/Detail_D. Ursache: Der Engine-Setter liefert in UE 5.8 auch bei erfolgter Zuweisung false zurück. Skript korrigiert: geladene Textur und zurückgelesenen Parameterwert prüfen. Erneuter Lauf und abschließendes RESULT OK stehen aus. Damit sind die neuen Formen bereits importiert; die neuen Materialbelegungen sind noch nicht vollständig bestätigt.

## Erfolgreicher erneuter Nutzerlauf

refresh_interiors_report.txt: RESULT OK, Backup 20261109-134608-169546. Blender: BUILDINGS OK 5. Nutzerbilder von 14:49 zeigen im Spiel die runderen Kissen, gebogene Stuhllehne und neue Holzmaserung in Antoninas Wohnung. Belege: 2026-11-09-user-interior-kitchen.png und -living.png. Import erfolgreich. Vollständiger Lauf-/Interaktionstest und Leistungsmessung weiterhin offen; einzelne FPS-Anzeigen in Bildern sind kein Leistungsprofil.
