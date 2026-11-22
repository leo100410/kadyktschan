# Asphaltstraßen und gemischter Bewuchs – 2026-11-09

## Status

Quellen, Asphalt-Schadensmasken und zwei Blattatlanten fertig. Neue Geometrie und Verteilung offline geprüft. **Noch nicht in Unreal importiert.** Die zuletzt erfolgreich importierte Spielversion gilt weiter.

Run result: NOT VERIFIED — der neue Asphalt-Download ist in dieser Ausführungsumgebung nicht erreichbar (DNS). Blender und Unreal ließen sich hier zuvor ebenfalls nicht starten. Neue Materialdarstellung, Pflanzendarstellung, Begehbarkeit und Leistung bleiben bis zum Nutzerlauf offen.

## Nutzervorgabe und Befund

Aktuelles Spielbild 17:01: Die Straße wirkt wie ein glattes, gleichförmiges Band. Nutzer verlangt ausdrücklich Asphalt, weiße Linien, Risse und Verfall. Zwei bereitgestellte Luftbilder zeigen dichten Wald außerhalb und niedrigen, unregelmäßigen Bewuchs zwischen den Häusern. Sie dienen als Referenz, nicht als Texturen.

## Umsetzung

- 39 Straßenstreifen bekommen Asphalt; 14 als `track` erfasste Feldwege bleiben unbefestigt und werden als eigener Mesh/Actor übernommen. Fußpfade bleiben Kies/Erde.
- Gewähltes fertiges Material: **Asphalt 02 von Poly Haven**, CC0, https://polyhaven.com/a/asphalt_02 . Die offizielle Seite beschreibt verwitterten grauen Asphalt mit grober Körnung und feinen Rissen, physische Kachelgröße 3 m. Diffuse, DirectX-Normalen und Rauheit werden als 2K-JPEG geladen. Die bisherigen neun Dateien bleiben im Cache; insgesamt werden danach zwölf Scan-Dateien protokolliert.
- Eigener 2048×4096-RoadWear-Atlas für 64 m Fahrbahn: verzweigte Risse, ausgewaschene weiße Mittel-/Randmarkierungen, beschädigte Stellen und ausgebrochene Ränder. Körnung wird unabhängig davon mit 3-m-Weltkoordinaten abgetastet. Weiße Markierungen sind eine ausdrücklich gewünschte gestalterische Annahme, kein behaupteter historischer Beleg.
- Fahrbahnquerschnitt leicht gewölbt, Ränder seitlich ungleichmäßig und tiefer. Flächennormalen an Knicken nach oben korrigiert. Bodenhöhe stammt weiterhin vom gerenderten TerrainMesh. Die Schäden sind Materialdarstellung, keine tiefen Kollisionslöcher.
- Boden-Importer weist Mesh und Material auch ausdrücklich dem vorhandenen Actor zu und liest die Materialzuweisung zurück. Damit bleibt ein möglicher alter Component-Override nicht unbemerkt aktiv; ein solcher Override wurde im alten Spielbild nicht nachgewiesen.
- Drei zusätzliche Wuchsformen mit je drei Varianten und drei LODs: niedrige, breite Weide; aufrechtes, mehrstämmiges Gebüsch; kahle Zweige. Zusammen mit bestehender Weide, Zwergstrauch, jungen Lärchen und Birken ergibt das verschiedene Höhen und Silhouetten.
- Neue schmale/längliche und runde Blattatlanten sowie zwei gedeckte Grüntöne in der zentralen Palette. Die Wuchsformen sind gestalterische Annahmen, keine botanisch verifizierte Artenkartierung.
- 35-m-Gruppen mit durchmischtem Bewuchs und kleinen Lichtungen. In der Stadt weniger hohe Junglärchen; außen bleiben mehr stehen. 734 vorhandene sichere Jungbaumpositionen werden zu erwachsenen Lärchen. Bestehende Lärchenkronen breiter, damit der Wald geschlossener erscheint.
- 876 niedrige Pflanzen rücken an die Wegesränder. Die neuen Positionen beachten Straßenbreite, konservative Gebäudeumrisse, Flüsse und mindestens 9 m Abstand zu den gespeicherten Eingangspositionen. Verschiebungen erfolgen nur im Stadtradius bis 850 m; der Stollenbereich ist davon entfernt. Absichtlich erhöhte Dach-/Fassadenpflanzen bleiben erhalten.
- Vegetation insgesamt etwa gleich viel: **200314 → 196875 Pflanzen**. Gras, Requisiten, Gebäude und Story-Texte werden nicht neu erzeugt oder umgebaut. 19 → 28 instanzierte Varianten; keine C++-Änderung.

| Wuchsform | vorher | vorbereitet |
|---|---:|---:|
| larch | 110000 | 110734 |
| birch | 2179 | 2179 |
| sapling | 42542 | 11694 |
| willow | 43270 | 17421 |
| shrub | 2323 | 17572 |
| low_willow | 0 | 16939 |
| alder | 0 | 17117 |
| dry_shrub | 0 | 3219 |

## Prüfung

- 3 bestehende Umgebungsprüfungen bestanden.
- 3 neue Naturprüfungen bestanden: Requisiten/Dachpflanzen erhalten; deterministische Wiederholung; Straße/Eingang frei; unterschiedliche Höhen und gleichbleibende Materialslots über die LODs.
- 2 neue RoadWear-Prüfungen bestanden: deterministische, endliche Maskenkanäle und unterbrochene, ausgewaschene Markierungen.
- Reale neue Straßenobjekte in temporäre Dateien geschrieben: 39 Streifen, 79040 nach oben gerichtete Dreiecke; Feldwege: 14 Streifen, 14608 Dreiecke. Bestehende Spielmeshes dadurch noch nicht geändert.
- Reale Verteilung in einer temporären Kopie erzeugt: alle Requisiten unverändert; Wiederholung verändert nichts. Alle 876 versetzten Pflanzen liegen am Terrain (Abweichung ≤ 1,1 cm) und halten mindestens 8,9 m Abstand zu Eingängen nach Koordinatenrundung.
- Shader-Eingänge verwenden die aus der installierten Engine geprüften Namen; unäre Eingänge bleiben namenlos. Scan-Texturen müssen tatsächlich geladen sein. Keine neue Behauptung, dass dies einen Unreal-Lauf ersetzt.
- Python-/Shell-Syntax geprüft.
- Vorschauen aus den tatsächlichen Masken und Modellgeometrien angesehen und nachgebessert. **Keine Spielbilder:** `2026-11-09-road-wear-preview.png`, `2026-11-09-bush-forms-preview.png`.

## Übernehmen

Unreal schließen und im normalen Terminal ausführen:

```sh
zsh "/Users/leolange/UnrealProjects/Kadyktschan/tools/rebuild_streets_nature.sh"
```

Erwartet: SURFACES OK 12, NATURE MESHES OK 28, zuletzt `refresh_streets_nature_report.txt` mit `RESULT OK`.

Der Befehl sichert Scatter, Manifest, alte Instanzdateien und Straßendaten in `Saved/StreetsNatureSourceBackups`. Der Editor sichert Materialien, Gelände, Vegetationsassets, Map und externe Actors in `Saved/StreetsNatureAssetBackups`. Er importiert nur Straßen/Boden und die instanzierten Baum-/Buschvorlagen; Gebäude, Gras-/Requisitenzellen und Möbel werden nicht neu gebaut. Der Folien-Actor wird mit den neuen Layern ersetzt. Reguläre Welt-Neuaufbauten verwenden dieselben Quellen.

Nach dem Import: Straße des Nutzerbilds aus Spielhöhe ansehen; Asphaltkörnung, verblasste Linien und Schäden prüfen, dann Randbüsche, Innenhöfe und Waldrand. Eingänge und Stollen erneut begehen, Bildrate beobachten. Kein Sicht-/Lauf-/Leistungs-PASS vor diesen Beobachtungen.

Keine Git-Befehle/Commits, keine Änderung der Nutzereinstellungen.

## Erfolgreicher Nutzerlauf – 2026-11-09 ~17:38

refresh_streets_nature_report.txt endet mit RESULT OK (Backup StreetsNatureAssetBackups/20261109-173736-776050). NATURE MESHES OK 28, zwölf Scans vorhanden. Asphaltstraße MI_Road, unbefestigte Tracks und Fußwege MI_Path sowie Wegesrandflächen übernommen. 28 instanzierte Layer mit 196875 Pflanzen gespeichert; Gras-/Requisitenzellen wurden nicht ersetzt. Neue Spielbilder, Laufprüfung und Bildrate bleiben offen.
