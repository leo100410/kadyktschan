# Elektrizitätswerk, Beleuchtung und Straßen — 2026-11-09

Status: Quelländerungen und Daten vorbereitet. Unreal-Import und Spielabnahme AUSSTEHEND.

## Verhalten
- Asphaltgeometrie: Breitenverschleiß jetzt ±3 cm statt ±8 Prozent, zusätzliche Seitenabweichung ±1,5 cm statt ±9 Prozent. Die Straßenmitte bleibt auf den vorhandenen OSM-Linien.
- Straßenmaterial: Randmaske wesentlich schmaler (Stärke 32 statt 5, Störanteil 0,25 statt 1,8); Asphalt, Risse und Markierungen bleiben erhalten.
- Heizungsrohre werden vor Querstraßen und Zugangswegen getrennt. Weitere große Gegenstände und Laternen werden auf Abstand zur Fahrbahn geprüft. Keine pauschale Entfernung aller Requisiten.
- Fiktives Elektrizitätswerk bei Ost 340 m / Nord 75 m: Dieselaggregat, Schaltschränke mit Messgeräten, Werkbank und Ersatzsicherung, Abgasrohr, Kabeltrassen, beschädigte Fenster, Mauerwerk, offene Doppeltür und Rampe. Kein historischer Standort behauptet.
- Zugangsweg und Freifläche werden von Vegetation freigehalten. Bestehende Gebäude werden erhalten.
- Neue erste Aufgabe mit drei geordneten E-Interaktionen: prüfen, Sicherung einsetzen, Notstrom starten. Erst danach ist der Beleuchtungsring aktiv. Die sechs bisherigen Storyaufgaben folgen unverändert; Karte hat jetzt neun Orte.
- 122 Straßenleuchten und neun Lichtpositionen in den drei eingerichteten Wohnhäusern. Nicht jede Leuchte funktioniert. Warmgelb, vereinzelte langsame Aussetzer statt gleichzeitiges Blitzen. Höchstens 16 tatsächliche Lichtquellen in bis zu 100 m Entfernung aktiv; Wohnungslicht wirft Schatten gegen Durchleuchten. Das ist ein lokaler Notstromkreis, keine vollständige Wiederherstellung des historischen Stadtnetzes.
- Keine automatische Speicherung des Missionsfortschritts hinzugefügt; ein neuer Spielstart beginnt wie bisher von vorn.

## Prüfungen
- Vier neue Offline-Tests bestanden: Rohre kreuzen die Straße nicht / wiederholbarer Filter, begrenzte Randabweichung, Standort und Reparaturdaten, endliche Geometrie mit gültigen Indizes und freiem Eingang.
- Sechs vorhandene Environment-/Nature-Tests bestanden.
- Tatsächliche verbleibende 1530 Rohrsegmente an je 21 Punkten gegen alle Straßen geprüft; Zugangsweg an 101 Punkten gegen bestehende Gebäude geprüft.
- Neun Python-Dateien syntaktisch geprüft; beide veränderten Shell-Skripte mit zsh -n geprüft.
- Originale C++-Funktion LampOutput separat mit clang++ kompiliert und fünf Zustände geprüft: ohne Strom, defekt, stetig, Aussetzer und Rückkehr.
- Unreal-Automation `Kadyktschan.Power.RepairAndLampStates` ergänzt; hier noch nicht ausgeführt.
- Vollständiger C++-Build blockiert, bevor die Kompilierung beginnt: Sandbox verweigert UBT die Sicherung einer Trace-Datei unter ~/Library/Application Support/Epic/UnrealBuildTool. Auch ein eigenes -Log-Ziel behebt diesen Zugriff nicht. KEIN erfolgreicher Unreal-Build behauptet.
- Blender/Unreal lassen sich in dieser Sitzung nicht als normale interaktive Apps starten. Keine neuen Ingame-Bilder und keine Bildratenmessung.

## Installation und Abnahme
Spiel und Editor schließen. Im normalen Terminal:

```sh
zsh /Users/leolange/UnrealProjects/Kadyktschan/tools/rebuild_power_roads.sh
```

Das Skript baut C++, sichert erzeugte Quelldaten und Unreal-Assets, baut die Geometrie, aktualisiert Straße, Zugangswege, Vegetation/Requisiten sowie Werk und Lichtmaterial. Erfolg nur bei `RESULT OK` im abschließenden Importbericht. Ein Komplett-Neubau berücksichtigt das Werk ebenfalls.

Danach neu starten: Marker zum Werk verfolgen; vor Reparatur keine gelben Leuchten; Starthebel vor Sicherung darf nicht auslösen; nach drei Interaktionen Lampen an und Aufgabe Antonina aktiv; Mission/Notizbuch und Karte prüfen. Eingang, Werkbank und Schaltpult begehen, Rohrkreuzungen kontrollieren, Beleuchtung bei Dämmerung und in Wohnungen sowie Leistung auf dem tatsächlichen Mac prüfen.

Protokolle: Saved/PowerRoadLogs; Importbericht: tools/editor/refresh_power_roads_report.txt. Keine Git-Befehle, persönliche GameUserSettings nicht geändert.


### 2026-11-09 — Elektrizitätswerk-Update erfolgreich gebaut und importiert
Nutzer führte tools/rebuild_power_roads.sh aus. Protokolle geprüft: C++ Result: Succeeded (9,71 s), POWER MESH OK 2149, VEGETATION OK (14 Gras-/17 Requisitenzellen, 28 instanzierte Schichten, 196822 Pflanzen), refresh_power_roads_report.txt endet RESULT OK. Straßen und Zugangswege importiert, Werk und Lichtmaterial gespeichert. Assetbackup: Saved/PowerRoadAssetBackups/20261109-180600-278644. Spielabnahme von Mission, Straßen, Licht und Leistung weiterhin offen; UE-Automation nicht ausgeführt.
