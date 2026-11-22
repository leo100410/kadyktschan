# Wohnhäuser und Wald — Prüfstand 2026-11-09

Status: vorbereitet, noch NICHT in Unreal importiert oder im Spiel abgenommen.

## Umfang

- Fünf Wohnhäuser mit insgesamt 24 möblierten Wohnungen. Lenina 7/8 bis ins zweite Obergeschoss; Gorbunows Block und Schkolnaja 4/6 bis ins erste Obergeschoss.
- Bestehende Storyräume und ihre Fundpositionen erhalten; sechs neue Haushaltsprofile mit Küche, Schlafplatz, Bad/WC, Stauraum, Licht und passenden Alltagsgegenständen.
- Durchgehende Zweilauftreppen, offene Deckenausschnitte und sichtbare Abschlüsse oberhalb der eingerichteten Etagen.
- 114 vorbereitete Sperren vor unfertigen Hauseingängen. Die jeweils eingerichteten Zugänge und der bisherige mittlere Kulturhauszugang bleiben frei.
- Verteilungsprobe: große Lärchen 110.733 → 190.723; weitere kleine Bäume und Büsche; 71 Hofgruppen. Die Differenz zu genau 80.000 entsteht durch die bewusst freien Flächen um neue Hofdetails.
- 108 Deckenlampenpositionen in den fünf Häusern werden direkt aus der tatsächlichen Geometrie exportiert. Spiegelung der Deckenleuchten korrigiert. Die neue Beleuchtung hängt am bereits vorhandenen Reparaturauftrag.
- Zwei zusätzliche Kartenorte, angehängt an die bisherige Reihenfolge; bestehende Storyschritte unverändert.

## Nachweise und Grenzen

- Möbeltests: fünf bestehende Prüfungen.
- Wohnungsprüfungen: vier Tests, darunter geschlossene/offene Gefäßgeometrie mit richtiger Spiegelung, Wege durch alle sechs Haushaltsprofile in beiden gespiegelten Wohnungen, gestapelte Treppen mit freiem Rücklauf und der Aufbau aller fünf Häuser.
- Stadtumfeld: zwei Tests für sichere Verteilung, Freihalten von Straßen/Zugängen/Reservierungen, Wiederholbarkeit sowie Auswahl gesperrter Eingänge.
- Sieben bestehende Power-/Nature-Regressionstests bestanden.
- Insgesamt 18 unterschiedliche Offline-Tests; keine Aussage über bestandene Unreal-Automation.
- `verify_residential_assembly.py` prüft zusätzlich die tatsächlich zusammengesetzte Gebäudegeometrie einschließlich Decken und Standard-Trennwänden. Alle Treppenwege bis zur letzten eingerichteten Etage bestehen die Prüfung. Dabei werden Textglyphen, Blender-Export und Putzbemalung ausgelassen.
- Die Kollisionsprüfung verwendet geometrische Hüllflächen mit 34 cm Radius und 1,92 m Körperhöhe. Sie ersetzt keinen echten CharacterMovement-/Lauftest in Unreal.
- Alle bisherigen Story-Fundpositionen mit dem bisherigen Manifest verglichen: unverändert.
- Materialien der vorbereiteten Häuser gegen zentrale SLOT_MI-Zuordnung geprüft, WoodGrey ergänzt. Keine neue externe Assetabhängigkeit.
- Grundrissdarstellung: `evidence/2026-11-09-residential-floorplans.svg`, ausdrücklich kein Spielbild.
- Der echte Blender-Export, der Import und Leistung/Sichtwirkung wurden hier nicht geprüft. Bekannte Sandbox-Beschränkungen verhindern regulären Blender-/Unreal-Start und den UBT-Trace-Zugriff.

## Installation

Spiel und Editor schließen; im normalen Terminal:

```sh
zsh /Users/leolange/UnrealProjects/Kadyktschan/tools/rebuild_neighbourhood.sh
```

Das Skript prüft die Grundrisse, baut den aktuellen C++-Stand, sichert Quelldaten und importierte Assets, baut gezielt fünf Wohnhäuser und anschließend Vegetation/Requisiten. Bestehende andere Gebäude werden nicht neu gebaut. Abschließender Importbericht: `tools/editor/refresh_neighbourhood_report.txt`, muss mit `RESULT OK` enden. Logs: `Saved/NeighbourhoodLogs`.

Der Teilneubau aktualisiert jetzt auch das Gebäudemanifest und bewahrt die übrigen Einträge. Die gemeldete Anzahl `BUILDINGS OK` bleibt die Anzahl tatsächlich neu gebauter Häuser, damit bestehende Update-Befehle weiter funktionieren. Der Import berücksichtigt neue Materialslots und die zugehörigen Glasscheiben. Persönliche GameUserSettings werden nicht überschrieben; keine Git-Befehle ausgeführt.

## Spielabnahme nach dem Import

- In Lenina 7 und 8 vom Eingang bis 2. OG laufen; alle Wohnungs-, Bad- und Küchentüren ausprobieren und über dieselbe Treppe wieder hinuntergehen.
- Gorbunows Block sowie Schkolnaja 4/6 bis 1. OG prüfen. Die neuen Häuser stehen auf der Karte.
- Brettersperren an fertigen Treppenenden und an unfertigen Hauseingängen prüfen; bekannte Storyzugänge müssen frei bleiben.
- Reparaturmission und Fundpositionen weiterhin erreichbar; nach Notstromstart Lampen an den richtigen Deckenleuchten, auch in oberen Etagen.
- Wald und Hofdetails aus Spielerhöhe betrachten; Straßen und Fußwege frei, Gegenstände auf dem Boden.
- Bildrate bei dichter Vegetation und bei eingeschalteter Beleuchtung messen. Mehr Bäume und mehr Innenlichter erhöhen die Last.
