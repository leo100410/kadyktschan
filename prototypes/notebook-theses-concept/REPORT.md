<!-- PROTOTYPE - NOT FOR PRODUCTION -->
<!-- Question: Macht das Verbinden von Funden zu einer These Spaß, und ist es fair statt Raten? -->
<!-- Date: 2026-11-07 -->
# Concept Prototype Report: Notizbuch-Thesen

> **Date**: 2026-11-07
> **Prototype Path**: HTML
> **Concept File**: design/gdd/game-concept.md

## Hypothesis
Wenn der Spieler die Funde einer Wohnung liest und eine These (Wer / Wo / Wann) ausfüllt, fühlt er sich klug statt geprüft. Messbar: These 2 in ≤ 3 Versuchen gelöst, Begründung nennt ≥ 2 passende Funde.

## Riskiest Assumption Tested
Neutrales Feedback („2 von 3 passen“) ohne Kosten verleitet zum Durchprobieren. Gemessen wird das über die Zahl der Versuche und die Zahl der Funde, die vor dem ersten Versuch gelesen wurden.

## Approach
Eine HTML-Seite, ca. 1 Stunde Arbeit. Zwei Thesen. These 1 öffnet das Schlafzimmer mit weiteren Funden, These 2 öffnet das Kesselhaus. Jede These hat absichtliche Ablenker.

**Path chosen:** HTML
**Reason for path:** Getestet wird die Logik und Fairness des Kombinierens, nicht Gefühl oder Grafik. Die Atmosphäre ist schon in der Engine belegt (Phase 3).

**Shortcuts taken (intentional):** keine 3D-Szene, Funde als Knöpfe, feste Werte, deutsche Lesehilfen in eckigen Klammern hinter kyrillischen Namen.

## Result
Noch nicht gespielt. Ein Skript hat geprüft, dass beide Thesen lösbar sind und alle 9 Funde erscheinen. Belegbild: `production/qa/evidence/2026-11-07-notebook-prototype.png`.

## Metrics
| Metric | Value |
|--------|-------|
| Path used | HTML |
| Iterations to playable | N/A |
| Prototype duration | ~1 h |
| Playtesters | 0 |
| Feel assessment | NOT ASSESSED |
| Hypothesis verdict | NOT ASSESSED |

## Recommendation: NOT ASSESSED — built but nobody has played it
Der nächste Schritt ist ein Spieldurchgang durch den Nutzer und möglichst durch eine weitere Person, die das Spiel nicht kennt. Danach folgt die Nachbesprechung (Phase 6 von `/prototype`).
