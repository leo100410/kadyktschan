# Shooter-Modus „Einsatz“ — Prüfbericht 2026-11-11

Status: gebaut, eingespielt, automatisch getestet und im Spiel beobachtet (Mac, UE 5.8.4). Eine komplette Runde durch den Nutzer steht noch aus.

## Automatisch
- C++-Build KadyktschanEditor: Succeeded, ohne Warnungen.
- Unreal-Automation `Kadyktschan.`: 19/19 grün (7 neu `Kadyktschan.Shooter.*`, 12 alt). Der neue Test `BeginRoundIsSeededAndPicksFarthestExit` fand einen echten Fehler (Funkgerät und Haushaltsfund auf demselben Punkt bei nur einem Fundpunkt) und war vor der Korrektur rot.
- Python: test_shooter (5), test_power_update, test_map_forest, test_neighbourhood: OK.
- Import tools/editor/refresh_shooter_report.txt: 19 Modelle, 7 Geräusche, RESULT OK.
- Hinweis: Beim Hochfahren des Editors meldet die Engine zweimal „LogAutomationTest: Error: Condition failed“, bevor ein Projekttest läuft. Nicht aus den Projekttests.

## Im Spiel (Belege in evidence/, Start mit -KdkShooter=1 und Test-Schaltern)
| Prüfung | Ergebnis | Beleg |
|---|---|---|
| Menüeintrag, Rückkehr nach der Runde | ok | 2026-11-11-shooter-back-to-menu.png |
| Story unverändert, keine Einsatz-Objekte | ok | 2026-11-11-story-unchanged.png |
| Anzeige Auftrag/Magazin/Markierung, REC | ok, 40–57 FPS | 2026-11-11-shooter-hud-full.png |
| Kamerazerfall 50 % / 10 % Leben | deutlich gestuft | shooter-health-50.png, shooter-health-10.png |
| Fund in Wohnung (Lenina 8, EG links), E nimmt ihn | „[E] Verbandszeug“, Leben 50 → 85 | shooter-flat-pickup.png, shooter-flat-taken.png |
| Hindernisse im Hof und an der Straße | ok | shooter-obstacles-yard.png, shooter-looters.png |
| Plünderer entdecken den Spieler | auf 43–50 m; stehen bleiben → verloren nach 17 s, 8 Treffer | shooter-contact.png |
| Geschütz nur bei Strom | läuft auf 19 m an; danach Schaden gesenkt | Saved/ShooterLogs/shooter-turret.log |
| Navigation in Wohnungen | 15/24 erreichbar (Lenina 7, Lenina 8 ohne Antonina, Gorbunows Block, jeweils bis 2. OG); Schkolnaja 4/6 nicht | debug-nav-*.png, Saved/ShooterLogs/probe-nav.log |
| Persönliche Einstellungen | GameUserSettings.ini unverändert (Stand 10.11.) | — |

Netzaufbau zu Rundenbeginn: 3,3–5,9 s.

## Offen / bekannte Grenzen
- Schkolnaja 4/6: Außentreppen nicht im Navigationsnetz, Ursache nicht gefunden. Gegner folgen dort nicht hinein.
- Gegner nutzen die unbewaffnete Mannequin-Animation mit angehängtem Gewehr.
- Bäume ohne Kollision: Sicht und Schüsse gehen durch Laub.
- Einmal stand das Magazin auf einem Testbild bei 2/30, ohne dass geschossen werden sollte. Wahrscheinlich ein Klick ins Testfenster; nicht reproduziert.
- Bildrate mit vielen Gegnern und eine volle Runde (Spaß, Länge, Schwierigkeit) muss der Nutzer prüfen.
