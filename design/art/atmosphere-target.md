# Atmosphären-Ziel (Vorgabe des Nutzers, 2026-11-07)

> Verbindlicher Endzustand. Jede Änderung an Licht, Gebäuden, Vegetation und Requisiten wird daran gemessen,
> ob sie dieses Gefühl verstärkt. Wörtlich übernommen; nicht kürzen oder umformulieren.
> Ersetzt in der Art Bible: „sonniger Sommertag“ → blasser, bedeckter Himmel, wenig direkte Sonne.

Die aktuelle Szene trifft das gewünschte Gefühl noch nicht. Sie wirkt eher wie eine ruhige Wohnsiedlung an einem sonnigen Tag. Ich möchte stattdessen eine bedrückende, aber faszinierende Atmosphäre: das Gefühl, allein vor den Überresten einer ganzen menschlichen Lebenswelt zu stehen.

Entscheidend ist nicht einfach „mehr Verfall“ oder „dunkleres Licht“. Entscheidend ist der Widerspruch zwischen der Größe dieser Stadt und ihrer völligen Menschenleere. Der Spieler sieht unzählige Fenster und begreift: Hinter jedem davon könnte einmal jemand gewohnt haben. Trotzdem bewegt sich nichts. Keine Stimmen, kein Verkehr, kein Licht in einer Wohnung. Die Gebäude sind noch da, aber ihr Zweck scheint verschwunden.

Die Stadt soll den Spieler durch ihre Ausmaße überwältigen. Vom Boden aus sollen hinter den nächsten Häusern weitere Häuser sichtbar sein und dahinter erneut Gebäude, deren Konturen langsam im Dunst verschwinden. Nicht alles auf einmal zeigen. Der Spieler soll nie sicher sein, wie weit diese verlassene Stadt noch reicht. Es geht nicht darum, eine riesige leere Landschaft um wenige Wohnblocks zu bauen, sondern um eine scheinbar endlose Folge menschenleerer Lebensräume.

Die Stimmung soll still, kalt und schwer wirken, aber nicht wie ein offensichtlicher Horrorfilm. Kein Gefühl von „gleich springt ein Monster hervor“, sondern eher: „Hier fehlt etwas unglaublich Großes, und ich kann diese Abwesenheit überall spüren.“

Dafür soll die Umgebung Spuren eines vergangenen Alltags tragen. Ein leerer Spielplatz ist nicht einfach Dekoration, sondern ein Ort, an dem eigentlich Kinder sein müssten. Eine Bushaltestelle verweist auf Menschen, die hier gewartet haben. Die vielen dunklen Fenster sollen nicht bloß eine Fassadentextur sein, sondern die Vorstellung von Hunderten verlassenen Wohnungen auslösen. Solche Details sollen sparsam eingesetzt werden, damit ihre Bedeutung in der Leere auffällt.

Das Licht soll diese Stimmung unterstützen: ein blasser, bedeckter Himmel, kühle und zurückhaltende Farben und wenig direkte Sonne. Die Szene soll trotzdem gut lesbar bleiben. Ich möchte die Größe und das Verlassensein sehen können, statt sie in Dunkelheit oder dichtem Nebel zu verstecken. Entfernte Gebäude dürfen im Dunst verblassen, müssen aber noch erahnen lassen, dass die Stadt dort weitergeht.

Auch die Natur soll nicht wie eine gepflegte grüne Wohnanlage wirken. Vegetation soll unregelmäßig durch Risse und an vernachlässigten Stellen wachsen. Unterschiedlicher Verfall, fleckige Fassaden und einzelne beschädigte Fenster sollen zeigen, dass Zeit vergangen ist, ohne die Stadt in eine beliebige Trümmerlandschaft zu verwandeln.

Das Zielgefühl ist: Ich stehe allein in einem riesigen Innenhof, schaue an den leeren Fensterreihen hinauf und merke erst jetzt, wie klein ich bin. Der Ort ist unheimlich, traurig und gleichzeitig beeindruckend. Ich will weitergehen, obwohl mich diese Stille bedrückt.

Beurteile jede Änderung danach, ob sie dieses Gefühl verstärkt. Mehr Objekte und mehr Schäden sind nicht automatisch besser. Wichtig sind die wahrgenommene Größe, die Spuren früherer Normalität und die auffällige Abwesenheit von Menschen.

## Nachtrag 2026-11-07 (Nutzer)

Nach echten Luftbildern soll es **grüner** und **heller** sein: aufgelockerte Wolken mit blauen Lücken, dichter gelbgrüner Bewuchs zwischen den Häusern, Taiga rundherum, Berge am Horizont. Das Zielgefühl oben gilt weiter; nur „blasser, bedeckter Himmel, wenig direkte Sonne“ ist dadurch abgelöst.

## Umsetzungsstand

| Baustein | Stand |
|---|---|
| Bedeckter, blasser Himmel, wenig direkte Sonne, kühle Farben | Stufe 1: `tools/editor/apply_atmosphere.py` |
| Dunst, in dem entfernte Gebäude verblassen | Stufe 1: Höhennebel in `apply_atmosphere.py` |
| Stadt wirkt endlos (Staffelung, Sichtachsen) | 15 im Satellitenbild belegte Gebäude ergänzt (NO-Viertel, Ostblöcke); Sichtachsen offen |
| Fleckige Fassaden, unterschiedlicher Verfall, einzelne kaputte Fenster | Stufe 1: Schmutz-Layer `T_Grime_A` + verblasste Farbe, verwitterte Rahmen; Fenster noch offen |
| Vegetation in Rissen und an vernachlässigten Stellen statt Rasen | Stufe 1: Gras in Flecken + Wandsaum, Boden grau-erdig; Risse in Wegen offen |
| Sparsame Alltagsspuren (Bushaltestelle, leerer Spielplatz) | offen |
| Häuser wirken nicht wie Rohbau (Vordächer, Schutt, Schweben) | Stufe 1: Beton-Vordach, flacher Schutt, geschlossener Sockel bis unter die Erde |
| Dunkle Fenster, die Wohnungen erahnen lassen (Vorhänge, Tiefe) | Stufe 1: zerbrochene Scheiben, vernagelte EG-Fenster, sparsame Vorhangreste |

**Hinweis 1:1-Regel:** Die echte Stadt hat laut OSM nur rund 34 erfasste Mehrgeschosser. Die „endlose“ Wirkung
entsteht deshalb aus Staffelung, Blickachsen und Dunst, nicht aus erfundenen Häusern. Zusätzliche Gebäude nur
mit Beleg (z. B. Satellitenbild) oder als ANNAHME markiert und mit Freigabe des Nutzers.
