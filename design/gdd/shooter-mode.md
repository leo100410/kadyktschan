# Einsatz (Shooter-Modus)

Stand 2026-11-11 · Auftrag des Nutzers: Shooter-Modus mit Gegnern, Leben über die Videokamera, Funktion für die
eingerichteten Wohnungen, Bodycam-Gefühl, passende Hindernisse. Der Story-Modus bleibt unverändert.
Plan: `~/.claude/plans/optimized-greeting-lamport.md`. Daten: `tools/research/shooter_data.py` → `Content/Kadykchan/Data/Shooter.json`.

## 1. Overview

Ein eigener Modus im Hauptmenü („Einsatz (Shooter)“). Er läuft in derselben Welt wie die Story. Eine Runde dauert
etwa 10–15 Minuten: Der Spieler betritt das besetzte Zentrum mit einer Brustkamera, erfüllt drei zufällig gezogene
Aufträge und hält danach 30 Sekunden am Abholpunkt am anderen Stadtrand durch. Die Gegner sind Plünderer und ihre
Maschinen (Kettendrohnen, Geschütze). Es gibt keine Lebensanzeige: Die Videokamera zerfällt mit jedem Treffer.
Heilung und Ausrüstung liegen nur in den 24 eingerichteten Wohnungen, passend zum jeweiligen Haushalt.

## 2. Player Fantasy

„Ich bin allein mit einer Kamera auf der Brust in einer toten Stadt, und jede Kugel macht mich blinder.“ Der Spieler
fühlt sich verletzlich statt übermächtig. Er hört mehr, als er sieht, nutzt Deckung, schleicht durch Treppenhäuser
und entscheidet bewusst, ob er Licht (Strom) haben will, wenn dafür die Geschütze anlaufen. Gutes Spiel zeigt sich in
einem klaren Bild am Ende der Runde.

Fiktion und Ethik: Schrottdiebe 2011, keine realen Personen, kein Bezug zur Story oder zum Gulag, kein Blut, keine
Monster. Getroffene Plünderer fallen um (Animation), mehr nicht.

## 3. Detailed Rules

**Ablauf.** Hauptmenü → „Einsatz“. Der Spieler startet an einer zufälligen Straßenausfahrt des Spielbereichs (Zentrum
plus 30 m Rand). In den ersten Sekunden baut das Spiel das Navigationsnetz auf („VERBINDUNG WIRD AUFGEBAUT …“),
danach erscheinen die Gegner. Kein Gegner erscheint näher als 55 m am Startpunkt.

**Aufträge.** Drei von fünf, nacheinander (`AUFTRAG n / 3`), Markierung mit Entfernung wie in der Story:
- Funkgerät aus einer zufälligen Wohnung holen (Etage und Seite stehen im Auftrag; die Einrichtungskarte hilft).
- Notstrom im Elektrizitätswerk starten → Straßen- und Wohnungslicht an, aber die Geschütze laufen.
- Störsender in der Telefonzentrale anbringen → Drohnen und Geschütze 60 s blind.
- Werkstatt der Plünderer im Laden zerstören → keine neuen Drohnen mehr als Verstärkung.
- Lagekarte aus Orlows Wohnung holen → Plünderer im Umkreis von 80 m werden markiert.

Nach jedem erledigten Auftrag kommen zwei Plünderer (und eine Drohne, solange die Werkstatt steht) von der
Ausfahrt, die am weitesten vom Spieler entfernt ist. Nach dem letzten Auftrag: Abholpunkt (die Ausfahrt mit dem
größten Abstand zum Start). Wer dort im Umkreis von 8 m bleibt, lässt den 30-s-Zähler laufen. Beim ersten
Betreten kommt eine letzte Welle.

**Ende.** Gewonnen: „EINSATZ ERFÜLLT“. Verloren bei 0 Leben: „SIGNAL VERLOREN“. Beide zeigen Zeit, ausgeschaltete
Gegner und kassierte Treffer. Mit E geht es zurück ins Hauptmenü. Die Spielfigur steht danach wieder dort, wo die
Story sie verlassen hat, und alle Einsatz-Objekte sind entfernt.

**Steuerung.** Linke Maustaste: Feuer (Dauerfeuer). Rechte Maustaste: zielen (enger Bildwinkel, präziser).
R: nachladen. E: nehmen oder benutzen. Q: Deckung. Strg: ducken. Shift: rennen. L: Taschenlampe. K: Stadtkarte. Esc: Einstellungen.
F (Flug) und N (Notizbuch) sind im Einsatz gesperrt.

**Bodycam.** Bildwinkel 100°, Handkamera-Wackeln, Schrittbewegung beim Gehen, Ruck bei Treffern. Gewehr unten rechts,
folgt Drehungen verzögert. Die Runde beginnt mit klarem Bild (Nutzer 2026-11-11); Fischauge entfernt.

**Regeneration (Nutzer 2026-11-11).** Nach 5 s ohne Treffer kehren Leben langsam (1,5/s) und Sicht schnell (12/s)
zurück. Die Sicht kann über dem Leben liegen; der nächste Treffer setzt sie sofort auf das verbliebene Leben zurück.

**Wo die Gegner sind.** Plünderer tragen Stirnlampen, Drohnen ein Frontlicht. Treffer und Fehlschüsse bis 8 m neben
dem Spieler zeigen einen roten Bogen mit Pfeil um die Bildmitte in Richtung des Schützen (1,8 s, wie in Fortnite).
Ein roter Rand wächst mit verlorenem Leben. Wer den Spieler trifft, trägt 2 s lang einen roten Ring mit Spitze über
dem Kopf (auch durch Wände; außerhalb des Bildes zeigt der Bogen die Richtung).

**Dynamische Grafik (Nutzer 2026-11-11).** Während einer Runde wird die Bildrate jede Sekunde gemessen. 2 s unter
`target_fps − 3` (45) → eine Stufe runter, 6 s über `target_fps + 15` → eine hoch. Jede Stufe senkt Auflösung und
Einstellungen (Nutzer: „nicht nur die Auflösung“, „nur unscharf“): Auflösung erst ab Stufe 3 (×0,85 / 0,75); ab Stufe 1 Schatten,
Pflanzen, Effekte je eine Stufe pro Level, ab 2 Reflexionen und Nachbearbeitung, ab 3 Beleuchtung und Shading, ab 4
Sichtweite. Untergrenzen: Schatten 1, Pflanzen 1, Nachbearbeitung 1, Beleuchtung 1, Shading 1, Sichtweite 1. Ausgangspunkt
sind immer die Einstellungen des Spielers; sie werden nie überschrieben (auch beim Speichern/Beenden nicht) und nach der Runde wiederhergestellt. Meldung bei jedem Wechsel.

**Fadenkreuz und Treffer.** Vier Striche um die Bildmitte, der Abstand zeigt die aktuelle Streuung. Ein Treffer zeigt
kurz ein Kreuz um das Fadenkreuz und klickt, ein ausgeschalteter Gegner ein rotes Kreuz mit dumpferem Klang.

**Deckung (Q, wie RDR2).** Q heftet an die nächste Wand oder das nächste Hindernis im Umkreis von 1,6 m (erst
Blickrichtung, dann seitlich und hinten). Die Figur duckt sich, die Kamera sinkt 28 cm unter die Kante (niedrige
Deckung bis 1,55 m). Mit der rechten Maustaste schaut sie 18 cm über die Kante, an hohen Wänden 65 cm seitlich am
freien Rand vorbei; beim Loslassen wieder dahinter. Gegner sehen und treffen Kopf (Kamera) oder Brust nur, wenn
sie frei sind: versteckt ist man unsichtbar, beim Herausschauen nicht. A/D gleiten an der Deckung entlang und halten am Rand.
Q oder ein klarer Schritt weg löst die Deckung. Im Kopf der Anzeige steht „IN DECKUNG (Q)“.

**Wohnungen.** In jeder der 24 Wohnungen liegt mit 60 % Wahrscheinlichkeit ein Fund unter einer der
Deckenleuchten. Was es ist, bestimmt der Haushalt: Lehrerin, Familie und Schneiderin Verbandszeug, Pflegekraft und
Ruheständler Verbandskasten, Funktechniker Munition, Orlow eine Schutzweste. Verbandszeug wird bei vollem Leben
nicht verbraucht, es bleibt liegen. Drei Plünderer warten als Wachen in zufälligen Wohnungen.

**Gegner.**
- Plünderer (überarbeitet nach Nutzertest 2026-11-11): Streife zwischen Haustür und Straße. Sicht 140° bis 60 m;
  das Bemerken dauert entfernungsabhängig (≈2 s auf 60 m, 0,5 s unter 15 m). Danach sucht jeder eine Kampfstelle
  12–26 m vom Spieler: bevorzugt hinter einem Hindernis (vom Spieler aus verdeckt) mit einem Spähpunkt 1,7 m daneben,
  sonst freien Boden mit Sicht. Andere besetzte Stellen in 5 m Umkreis zählen dagegen (sie verteilen sich). Dort:
  in Deckung 1,5–3 s verstecken, 2,5–4 s heraustreten und feuern; ohne Deckung Seitschritte bis 2,8 m alle 1,2–2,5 s.
  Stellungswechsel nach 6–10 s, nach zwei Treffern oder wenn der Spieler das Band verlässt, zu 70 % flankierend.
  Feuer nur bis 32 m, mit Schussrecht (höchstens zwei Plünderer gleichzeitig), im Laufen und bei den ersten vier
  Schüssen nach dem Entdecken ungenauer. Nach 6 s ohne Sicht: Suche an der letzten bekannten Stelle. Kopftreffer 2,5×.
- Kettendrohne: schnell, laut (Motorgeräusch), fährt im Zickzack auf 5–12 m heran, wechselt alle 2–3 s die Stelle,
  feuert bis 16 m (ohne Schussrecht-Grenze), vom Störsender blind.
- Geschütz: steht an der Straße, nur bei Strom aktiv. Der Suchscheinwerfer schwenkt, sieht im 25°-Kegel. Vor dem
  ersten Feuerstoß läuft es 1,6 s hörbar an.

**Hindernisse (nur im Einsatz).** Plattenstapel, Betonzaun mit Rautenmuster, LKW- und Buswracks, Barrikaden aus
Türen und Möbeln, Kabeltrommeln, Schrott mit Blechwänden. Auf den Straßen stehen sie alle 17 m abwechselnd links
und rechts (Slalom, die Straße bleibt passierbar), in den Höfen in einem 20-m-Raster. Türen bleiben 5 m frei.
Gebäude, vorhandene Requisiten und Rohre werden gemieden.

## 4. Formulas

| Größe | Formel | Werte (Shooter.json) |
|---|---|---|
| Kamerazerfall D | `D = (1 − Leben / MaxLeben) ^ 0,8` | 0 = intakt, 1 = Signal weg |
| Verpixelung | `Pixel = lerp(0, 0,9, D)` (im Einsatz zählen die Story-Regler nicht); Renderauflösung `= lerp(100, 20, Pixel) · (1 − 0,6·D)` % | bei 10 % Leben ≈ 10 % Auflösung |
| Kamerastärke | `K = lerp(0, 1, D) / 0,75` (Sättigung, Korn, Farbsäume, Vignette, Bloom wie im Story-Modus) | |
| Unschärfe | B = D²; ab B > 0,01: Fokus 60 cm, Blende `lerp(16, 1,4, B)`, Sensor `lerp(24,6, 150, B) · tan(FOV/2) / tan(50°)` mm (gleich stark beim Zielen) | |
| Schutzweste | absorbiert `min(Weste, 0,6 · Schaden)` | Weste +50 |
| Spielerstreuung | `Streuung · (1 + Tempo / 450 cm/s)`; gezielt 0,6°, aus der Hüfte 2,2° | |
| Gegnerstreuung | `Streuung · (0,6 + Abstand / Reichweite) · (1 + Spielertempo / 500) · 0,75 (geduckt)` | |
| Kopftreffer | `Schaden · 2,5`, wenn der Treffer weniger als 30 cm unter dem Kapselscheitel liegt | |

Variablen: Leben 0–100, MaxLeben 100, CamPixelation/CamNoise 0–1 (Regler des Nutzers), D 0–1, Abstand/Reichweite in m.

Rechenbeispiel (Leben 50): D = 0,5^0,8 = 0,57 → Pixel = 0,9·0,57 = 0,52 →
Auflösung = (100 − 80·0,52)·(1 − 0,6·0,57) = 58,7·0,66 ≈ 39 %. Bei vollem Leben: D = 0, keine Störung. Ein Plünderer auf 40 m (Reichweite 55 m) gegen einen
stehenden Spieler: 4,5°·(0,6 + 0,73) = 6,0° Streukegel; geduckt 4,5°.

Die Exponenten und Faktoren wurden im ersten Spieltest am 2026-11-11 eingestellt (`production/qa/shooter-mode-2026-11-11.md`).

## 5. Edge Cases

- Shooter.json fehlt oder ist kaputt → Hinweis im Lesefenster, Story läuft weiter (`tools/rebuild_shooter.sh`).
- Navigationsnetz nach 60 s nicht fertig → Gegner erscheinen trotzdem und bleiben ggf. stehen.
- Wohnung mit nur einem Fundpunkt und Funkgerät darin → der Haushaltsfund entfällt (Test `PickupsHealCapped…`/`BeginRound…`).
- Magazin leer → Klicken, Hinweis „R: nachladen“. Reserve leer → kein Nachladen, Munitionskisten in den Wohnungen.
- Pause/Einstellungen → Runde, Schüsse und Gegner stehen still (Akteur-Tick pausiert).
- Spieler stirbt während der Abholung → verloren. Ein Abbruch über Esc → Hauptmenü ist nicht vorgesehen (Runde zu Ende spielen).
- Bekannte Grenze: Das Navigationsnetz erreicht 15 von 24 Wohnungen (Lenina 7 und 8 ohne Antoninas, Gorbunows Block).
  In Schkolnaja 4/6 kommen die Außentreppen nicht ins Netz, dorthin folgen Gegner nicht (Wachen drinnen bleiben drinnen).
- Bäume haben keine Kollision: Gegner sehen und schießen durch Laub.

## 6. Dependencies

Hauptmenü (`SKdkMainMenu`), Spieler-Controller (Videokamera `UpdateCamcorder`, Overlay `SKdkStoryHud`), Spielfigur
(`AKadyktschanCharacter`), Kameramanager (Bodycam), Notstrom/Lampen (`AKdkTownPower` über `IsTownPowerOn`),
Story-Daten (Fundorte für Telefonzentrale, Orlow, Notstromschalter), Stadtkarte/TownMap.json (Türen, Spielbereich),
Gebäudemanifest (Wohnungen, Deckenleuchten, Abschnittsrahmen), Blockout (Straßen, Gebäudeumrisse), Vegetationsdaten
(Requisiten und Rohre, die gemieden werden), UE-Mannequin mit Animationen, Engine-Navigation (Laufzeit-Navmesh).

## 7. Tuning Knobs

Alle in `tools/research/shooter_data.py` (`TUNING`, `ITEMS`, `THEME_ITEM`, `OBSTACLES`, `MARGIN`, `OBSTACLE_STEP`,
`YARD_STEP`, `DOOR_CLEAR`, `PROP_CLEAR`), danach `python3 tools/research/shooter_data.py`. Kein Neubau nötig.
Spieler: Leben, Magazin, Reserve, Schaden, Reichweite, Feuerrate, Streuung, Nachladezeit, Bildwinkel, Hörweite.
Je Gegnerart: Leben, Schaden, Feuerrate, Stoßlänge, Pause, Streuung, Reichweite, Sichtweite, Reaktionszeit, Tempo,
Deckungsschwelle. Runde: Aufträge pro Runde, Haltezeit, Fundanteil, Störsenderdauer, Verstärkung, sicherer Startradius,
Kameraexponent. Navigation: `Config/DefaultEngine.ini` (Zellgröße 12 cm, Agentenradius 24 cm).

| Stellwert | Jetzt | Sicherer Bereich | Wirkung |
|---|---|---|---|
| Plünderer-Schaden | 14 | 10–20 | Treffer bis „Signal verloren“ (≈7 bei 14) |
| Plünderer-Reaktionszeit | 0,9 s | 0,6–1,5 s | Zeit, um nach Entdeckung in Deckung zu gehen |
| Geschütz-Schaden / Stoß | 11 / 5 | 8–16 / 3–6 | Strafe für „Strom an“ |
| Kameraexponent | 0,8 | 0,6–1,2 | <1: frühe Treffer sichtbarer |
| Fundanteil | 0,6 | 0,4–0,9 | wie oft Wohnungen sich lohnen |
| sicherer Startradius | 55 m | 40–80 m | Zeit bis zum ersten Kontakt |
| Hindernisabstand Straße | 17 m | 12–25 m | Sichtlinien vs. freie Wege |
| Haltezeit Abholung | 30 s | 20–45 s | Spannung am Ende |

## 8. Acceptance Criteria

1. Das Hauptmenü zeigt „Einsatz (Shooter)“, die Runde startet, „Spiel starten“ führt weiter in die unveränderte Story. ✔ (Bilder `2026-11-11-shooter-back-to-menu.png`, `2026-11-11-story-unchanged.png`)
2. Bei 100 / 50 / 10 % Leben ist das Bild sichtbar zunehmend verpixelt und unscharf. ✔ (`shooter-hud-full`, `shooter-health-50`, `shooter-health-10`)
3. In einer Wohnung liegt ein haushaltsgerechter Fund; E nimmt ihn und heilt (50 → 85). ✔ (`shooter-flat-pickup`, `shooter-flat-taken`, Protokoll)
4. Plünderer entdecken den Spieler auf 40–50 m und treffen ihn. Ungedeckt stehen führt in etwa 15–20 s zu „SIGNAL VERLOREN“. ✔ (`shooter-contact`)
5. Das Geschütz läuft nur bei Strom an, mit hörbarer Warnung. ✔ (Protokoll „turret spins up at 19 m“)
6. Gegner erreichen Wohnungen über Treppenhäuser bis ins 2. OG. ✔ teilweise: 15/24 (siehe Edge Cases)
7. Nach der Runde sind keine Einsatz-Objekte mehr in der Welt, der Spieler steht wieder am Story-Ort. ✔ (Rückkehr-Lauf)
8. Automatische Tests `Kadyktschan.Shooter.*` (7) und `tools/research/test_shooter.py` (5) grün; alte Tests weiter grün. ✔
9. Offen für den Nutzer: eine komplette Runde selbst spielen (Spaß, Schwierigkeit, Länge), Bildrate mit 15+ Gegnern beobachten.
