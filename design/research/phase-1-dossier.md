# Phase 1 · Recherche-Dossier (Teil 1)

*Stand: 2026-11-07 · Status: **Freigegeben** (Nutzer, 2026-11-07)*
*Briefing: PDF V12 Phase 1 · Konzept: `design/gdd/game-concept.md`*

> **Kennzeichnung:** **BELEGT** = Quelle nennt es ausdrücklich · **ANNAHME** = abgeleitet oder
> unsicher, sichtbar markiert · **FIKTION** = bewusst erfunden.
> **Vertrauensgrad:** Hoch = Primärquelle oder mehrere Quellen · Mittel = eine Quelle oder
> Kartendaten ohne Abgleich · Niedrig = Ableitung.

Teil 1 deckt die ganze Stadt auf Kartenebene ab (alle in OpenStreetMap erfassten Gebäude)
und die Vertiefung für den Vertical-Slice-Block an der ул. Ленина. Teil 2 (Typenserien,
Achsmaße, Innengrundrisse) braucht Quellen, die frei im Netz nicht zu finden waren; siehe
Offene Fragen.

---

## 1. Ortsfakten

| Fakt | Wert | Kennz. | Vertrauen | Quelle |
|---|---|---|---|---|
| Name | Кадыкчан, ewenisch „kleine Schlucht, Enge“ | BELEGT | Hoch | PDF R1; ru.wikipedia |
| Lage | Oblast Magadan, Rajon Susuman, 65 km NW von Susuman | BELEGT | Hoch | PDF R1; ru/en.wikipedia |
| Koordinaten | 63°05′18″ N, 147°02′54″ E | BELEGT | Hoch | ru.wikipedia (Infobox) |
| Gegründet | 1943; Siedlung städtischen Typs ab 1964 | BELEGT | Mittel | ru.wikipedia (Infobox, Gründungskontext ohne Einzelnachweis) |
| Entstehung | Von Häftlingen gebaut (Gulag), Schalamow selbst war darunter | BELEGT | Hoch | ru.wikipedia nach Schalamow, „Новая книга“, Kap. „Кадыкчан“; en.wikipedia |
| Bergbau | Steinkohle unter Tage bis 400 m Tiefe, für das Kraftwerk Arkagala | BELEGT | Hoch | ru.wikipedia; PDF R1 |
| Schacht Nr. 10 | „градообразующая шахта (№ 10)“, umgeben von Neu-Kadyktschan | BELEGT | Hoch | ru.wikipedia |
| Schacht Nr. 7 („семёрка“) | im Osten, 1992 aufgegeben | BELEGT | Hoch | ru.wikipedia |
| Unglück 1996 | Explosion im November 1996, sechs Tote, danach Schließung | BELEGT | Hoch | ru.wikipedia; RFE/RL 15.11.1996 |
| Schacht des Unglücks | Nr. 10 | ANNAHME | Mittel | Ableitung: en.wikipedia „the other“ Grube als die 1992 geschlossene (Nr. 7) |
| Konservierung | 2001 Häuser von Wärme und Strom getrennt | BELEGT | Hoch | ru.wikipedia |
| Verlassen | 2010 vollständig entvölkert; 2012 noch ein Rentner | BELEGT | Hoch | ru.wikipedia |
| Einwohner | 1970: 3378 · 1979: 4764 · 1989: 5794 · 1996: 3211 · 2001: 1919 · 2009: 235 | BELEGT | Mittel | ru.wikipedia (Tabelle aus Rohtext gelesen); en nennt 1986: 10 270 (Widerspruch) |
| Große Gebäude gesprengt | „Major buildings were blown up.“ | BELEGT | Mittel | en.wikipedia, ohne Datum |
| Fluss am Ort | река Кадыкчан, nächster Punkt ca. 625 m NW des Ursprungs; Becken des Ajan-Jurjach | BELEGT | Mittel | OSM; PDF R1 / en.wikipedia |
| Trasse „Колыма“ | nächster Punkt ca. 2,1 km SW des Ursprungs | BELEGT | Mittel | OSM (passt zu „2–4 km von der Trasse“, ru.wikipedia) |
| Friedhof | Кадыкчанское кладбище, ca. 1,6 km W | BELEGT | Mittel | OSM |

**Ethik-Folge (Konzept, Zusatzregel):** Weil das Unglück von 1996 sehr wahrscheinlich in
Schacht Nr. 10 geschah, **benennt das Spiel den Zielschacht des fiktiven Mysteriums nicht als
Nr. 10 und lässt dort nichts Fiktives „geschehen“**. Vorschlag: Der reale Schacht Nr. 10
bleibt als belegte Industriekulisse (Förderturm, Gebäude) erhalten; der Mine-Eingang des
Finales ist ein als **FIKTION** markierter Stollen/Wetterschacht. Entscheidung offen (Frage 1).

## 2. Stadtstruktur und Zonen

| Zone | Was dort ist | Lage im Lageplan | Kennz. | Vertrauen | Quelle |
|---|---|---|---|---|---|
| Neuestes Kadyktschan | Hauptwohngebiet, 2–4 km von Trasse und Schacht | Gebäudecluster um den Ursprung (ca. 900 × 1000 m) | BELEGT (Beschreibung) / ANNAHME (Abgrenzung) | Mittel | ru.wikipedia; OSM |
| Neu-Kadyktschan | um Schacht Nr. 10, Industrie | Kandidat: großer Ruinencluster 0,6–1,1 km W (Grundrisse bis 119 × 32 m) | ANNAHME | Niedrig | OSM-Geometrie; Abstand passt nicht ganz zu „2–4 km“ |
| Alt-Kadyktschan | nächster Teil zur Trasse; später Gewächshäuser, Gärten, Ställe | Kandidat: Richtung SW zur Trasse; Ackerland ab 2,3 km S | ANNAHME | Niedrig | ru.wikipedia; OSM-Landnutzung |

**Ursprung (0,0,0):** Schwerpunkt aller 5- und 9-geschossigen Gebäude =
**63.085870 N, 147.050008 E** (ANNAHME für „Zentrum von Neuestem Kadyktschan“, PDF V3).
**Achsen:** UE +X = Norden, UE +Y = Osten, 1 UE = 1 cm (PDF V3).

### Belegte Straßen

| Straße | Quelle | Bemerkung |
|---|---|---|
| ул. Ленина | PDF R2; ru.wikipedia; OSM; Foto (Schablone „ЛЕНИНА 18“) | bis 2001 bewohnt |
| ул. Строителей | PDF R2; ru.wikipedia; OSM | bis 2001 bewohnt; in OSM ohne Hausnummern |
| ул. Школьная | PDF R2; ru.wikipedia; OSM | Telefonzentrale (АТС), Haus unbekannt |
| ул. Южная | PDF R2; ru.wikipedia; OSM | „das am weitesten vom Zentrum entfernte Haus“ |
| ул. Мира | PDF R2; ru.wikipedia; OSM | Poliklinik, Krankenhaus, Kommunaldienste. **Widerspruch:** ru.wikipedia „nur ein Haus“, OSM hat Nr. 1, 2, 7, 9 |
| ул. 50 лет Октября | nur OSM | **neu, nicht im PDF**; 7 Gebäude |
| ул. Пионерская | nur OSM | **neu, nicht im PDF**; ohne Hausnummern |

## 3. Gebäudekatalog (alle Gebäude in OSM, Stand 2026-11-07)

Grundrisse, Geschosszahl und Adressen aus OpenStreetMap (© OpenStreetMap-Mitwirkende,
ODbL). L × B = kleinstes umschließendes Rechteck der OSM-Kontur; Ausrichtung = Azimut der
Längsachse. Rohdaten: `design/research/data/osm-kadykchan-2026-11-07.json`; Tabelle neu
erzeugen mit `python3 -I tools/research/table.py`.

Alle Zeilen: Lage **BELEGT / Mittel** (Kartendaten, nicht gegen Satellitenbild abgeglichen),
Geschosszahl **BELEGT / Mittel** (OSM-Tag), Typ-Klasse **ANNAHME** (nach Geschosszahl).
In OSM tragen alle Wohngebäude `building=ruins` (verlassen, passt zu 2011).

| Adresse | Nr. | Asset-Name | Geschosse (OSM) | Typ-Klasse | Lat, Lon | UE X / Y (cm) | Grundriss L × B (m) | Ausrichtung | OSM |
|---|---|---|---|---|---|---|---|---|---|
| ул. 50 лет Октября | 1 | PLA_50LetOktyabrya_1 | 3 | T3 Wohnblock 3-geschossig | 63.08773, 147.04904 | 20 647 / -4 873 | 53.5 × 17.6 | 88° | way/170990555 |
| ул. 50 лет Октября | 2 | PLA_50LetOktyabrya_2 | 3 | T3 Wohnblock 3-geschossig | 63.08760, 147.04967 | 19 217 / -1 689 | 51.5 × 15.0 | 85° | way/170990189 |
| ул. 50 лет Октября | 3 | PLA_50LetOktyabrya_3 | 3 | T3 Wohnblock 3-geschossig | 63.08706, 147.04886 | 13 202 / -5 760 | 52.8 × 16.6 | 86° | way/170990139 |
| ул. 50 лет Октября | 4 | PLA_50LetOktyabrya_4 | 3 | T3 Wohnblock 3-geschossig | 63.08713, 147.04952 | 14 005 / -2 462 | 53.1 × 14.9 | 85° | way/170990140 |
| ул. 50 лет Октября | 6 | PLA_50LetOktyabrya_6 | 3 | T3 Wohnblock 3-geschossig | 63.08639, 147.04948 | 5 740 / -2 669 | 51.5 × 14.6 | 86° | way/170990128 |
| ул. 50 лет Октября | 7 | PLA_50LetOktyabrya_7 | 3 | T3 Wohnblock 3-geschossig | 63.08639, 147.04874 | 5 800 / -6 401 | 52.1 × 14.4 | 84° | way/170990131 |
| ул. 50 лет Октября | 8 | PLA_50LetOktyabrya_8 | 5 | T5 Plattenbau 5-geschossig | 63.08534, 147.04977 | -5 932 / -1 215 | 58.7 × 17.7 | 109° | way/170990141 |
| ул. Ленина | 7 | PLA_Lenina_7 | 5 | T5 Plattenbau 5-geschossig | 63.08615, 147.05461 | 3 128 / 23 176 | 61.1 × 22.3 | 38° | way/170990142 |
| ул. Ленина | 8 | PLA_Lenina_8 | 5 | T5 Plattenbau 5-geschossig | 63.08578, 147.05541 | -1 042 / 27 194 | 84.7 × 24.4 | 35° | way/170990130 |
| ул. Ленина | 9 | PLA_Lenina_9 | 2 | T2 2-geschossig | 63.08514, 147.05169 | -8 137 / 8 447 | 26.1 × 18.0 | 20° | way/1259762204 |
| ул. Мира | 1 | PLA_Mira_1 | 9 | T9 Plattenbau 9-geschossig | 63.08816, 147.04774 | 25 494 / -11 411 | 38.9 × 12.7 | 86° | way/170990848 |
| ул. Мира | 2 | PLA_Mira_2 | 9 | T9 Plattenbau 9-geschossig | 63.08770, 147.04758 | 20 338 / -12 205 | 37.7 × 14.1 | 86° | way/170990854 |
| ул. Мира | 7 | PLA_Mira_7 | 2 | T2 2-geschossig | 63.08754, 147.04712 | 18 548 / -14 516 | 33.5 × 29.9 | 175° | way/1259762205 |
| ул. Мира | 9 | PLA_Mira_9 | 2 | T2 2-geschossig | 63.08734, 147.05562 | 16 339 / 28 264 | 98.8 × 42.6 | 177° | way/170990359 |
| ул. Школьная | 1 | PLA_Shkolnaya_1 | 2 | T2 2-geschossig | 63.08693, 147.05204 | 11 813 / 10 208 | 65.5 × 14.1 | 175° | way/170990145 |
| ул. Школьная | 2 | PLA_Shkolnaya_2 | 5 | T5 Plattenbau 5-geschossig | 63.08712, 147.05093 | 13 953 / 4 652 | 68.5 × 16.7 | 84° | way/170990137 |
| ул. Школьная | 3 | PLA_Shkolnaya_3 | 5 | T5 Plattenbau 5-geschossig | 63.08623, 147.05089 | 4 033 / 4 439 | 51.0 × 15.3 | 86° | way/170990133 |
| ул. Школьная | 4 | PLA_Shkolnaya_4 | 5 | T5 Plattenbau 5-geschossig | 63.08559, 147.05131 | -3 165 / 6 554 | 52.6 × 15.0 | 114° | way/170990144 |
| ул. Школьная | 5 | PLA_Shkolnaya_5 | 5 | T5 Plattenbau 5-geschossig | 63.08756, 147.05058 | 18 835 / 2 891 | 53.6 × 15.3 | 86° | way/170990191 |
| ул. Школьная | 6 | PLA_Shkolnaya_6 | 5 | T5 Plattenbau 5-geschossig | 63.08559, 147.05037 | -3 093 / 1 823 | 59.2 × 18.2 | 110° | way/170990136 |
| ул. Школьная | 7 | PLA_Shkolnaya_7 | ? | unbekannt | 63.08748, 147.05201 | 17 873 / 10 062 | 56.4 × 14.9 | 85° | way/170990190 |
| ул. Школьная | 8 | PLA_Shkolnaya_8 | 2 | T2 2-geschossig | 63.08647, 147.05008 | 6 659 / 363 | 30.4 × 15.7 | 175° | way/170990143 |
| ул. Школьная | 9 | PLA_Shkolnaya_9 | 2 | T2 2-geschossig | 63.08663, 147.05322 | 8 423 / 16 157 | 38.8 × 22.4 | 85° | way/170990124 |
| ул. Школьная | 10 | PLA_Shkolnaya_10 | 2 | T2 2-geschossig | 63.08628, 147.05204 | 4 585 / 10 239 | 27.0 × 22.1 | 176° | way/170990135 |
| ул. Южная | 1 | PLA_Yuzhnaya_1 | 2 | T2 2-geschossig | 63.08649, 147.04768 | 6 874 / -11 738 | 34.4 × 20.9 | 173° | way/1259762208 |
| ул. Южная | 2 | PLA_Yuzhnaya_2 | 2 | T2 2-geschossig | 63.08600, 147.04640 | 1 472 / -18 163 | 25.9 × 11.4 | 173° | way/1259762209 |
| ул. Южная | 3 | PLA_Yuzhnaya_3 | 5 | T5 Plattenbau 5-geschossig | 63.08414, 147.04803 | -19 289 / -9 938 | 66.8 × 14.4 | 112° | way/170990127 |
| ул. Южная | 4 | PLA_Yuzhnaya_4 | 5 | T5 Plattenbau 5-geschossig | 63.08390, 147.04715 | -21 962 / -14 393 | 59.0 × 14.3 | 113° | way/170990138 |
| ул. Южная | 5 | PLA_Yuzhnaya_5 | 5 | T5 Plattenbau 5-geschossig | 63.08461, 147.04668 | -13 969 / -16 746 | 51.0 × 12.2 | 112° | way/170990122 |
| ул. Южная | 6 | PLA_Yuzhnaya_6 | 5 | T5 Plattenbau 5-geschossig | 63.08431, 147.04905 | -17 329 / -4 822 | 64.0 × 15.6 | 115° | way/170990125 |
| ул. Южная | 7 | PLA_Yuzhnaya_7 | 2 | T2 2-geschossig | 63.08236, 147.04739 | -38 993 / -13 156 | 66.4 × 25.6 | 110° | way/1259762206 |
| ул. Южная | 9 | PLA_Yuzhnaya_9 | 2 | T2 2-geschossig | 63.08181, 147.04560 | -45 145 / -22 169 | 48.4 × 37.7 | 109° | way/170991711 |
| ул. Южная | 10 | PLA_Yuzhnaya_10 | 1 | T1 1-geschossig | 63.08210, 147.04693 | -41 929 / -15 486 | 55.6 × 25.0 | 110° | way/170991718 |
| ул. Южная | 11 | PLA_Yuzhnaya_11 | 2 | T2 2-geschossig | 63.08204, 147.05204 | -42 581 / 10 212 | 78.3 × 37.5 | 52° | way/170991416 |
| — (ohne Adresse) |  | PLA_OSM_170990575 | ? | unbekannt | 63.08833, 147.05848 | 27 330 / 42 620 | 11.1 × 6.5 | 11° | way/170990575 |
| — (ohne Adresse) |  | PLA_OSM_170991186 | ? | unbekannt | 63.08677, 147.06722 | 9 993 / 86 612 | 17.7 × 14.6 | 150° | way/170991186 |
| — (ohne Adresse) |  | PLA_OSM_170991710 | ? | unbekannt | 63.08981, 147.03562 | 43 793 / -72 413 | 118.9 × 31.5 | 153° | way/170991710 |
| — (ohne Adresse) |  | PLA_OSM_170991713 | ? | unbekannt | 63.08990, 147.03771 | 44 820 / -61 890 | 31.8 × 25.5 | 54° | way/170991713 |
| — (ohne Adresse) |  | PLA_OSM_170991715 | ? | unbekannt | 63.08445, 147.03257 | -15 828 / -87 764 | 61.8 × 20.2 | 60° | way/170991715 |
| — (ohne Adresse) |  | PLA_OSM_170991719 | ? | unbekannt | 63.09052, 147.03787 | 51 754 / -61 091 | 47.7 × 20.3 | 46° | way/170991719 |
| — (ohne Adresse) |  | PLA_OSM_170991720 | ? | unbekannt | 63.08224, 147.02988 | -40 337 / -101 320 | 66.2 × 28.1 | 61° | way/170991720 |
| — (ohne Adresse) |  | PLA_OSM_654296774 | ? | unbekannt | 63.08701, 147.03152 | 12 704 / -93 050 | 43.4 × 12.0 | 56° | way/654296774 |
| — (ohne Adresse) |  | PLA_OSM_654296775 | ? | unbekannt | 63.08689, 147.02913 | 11 316 / -105 089 | 32.7 × 14.3 | 57° | way/654296775 |
| — (ohne Adresse) |  | PLA_OSM_654296776 | ? | unbekannt | 63.08761, 147.03152 | 19 382 / -93 054 | 25.1 × 17.2 | 152° | way/654296776 |
| — (ohne Adresse) |  | PLA_OSM_654296777 | ? | unbekannt | 63.08779, 147.03298 | 21 319 / -85 709 | 108.2 × 60.4 | 56° | way/654296777 |
| — (ohne Adresse) |  | PLA_OSM_1540985882 | ? | unbekannt | 63.08868, 147.04753 | 31 216 / -12 488 | 17.8 × 7.5 | 117° | way/1540985882 |
| — (ohne Adresse) |  | PLA_OSM_1540985885 | ? | unbekannt | 63.08808, 147.05379 | 24 532 / 19 015 | 9.2 × 6.1 | 178° | way/1540985885 |

**Nicht in OSM, aber belegt:** **ул. Ленина 18**, Foto Laika ac 2011 (Commons-Datei
„Laika ac Kadykchan (6480291063).jpg“): Hausnummer als Schablone auf Putz über einem
Holzfenster. Lage unbekannt. OSM kennt an der ул. Ленина nur die Nummern 7, 8, 9; die
Nummerierung in OSM ist also unvollständig oder falsch.

### Typ-Klassen und Typenprojekte

Das Briefing verlangt, jedes Haus einem sowjetischen Typenprojekt zuzuordnen. **Eine
belegte Serien-Nummer habe ich für kein Gebäude gefunden.** Bis dahin gelten diese
Klassen als ANNAHME:

| Klasse | Gebäude | Merkmale aus Fotos 2011 (Referenz) | Typenprojekt |
|---|---|---|---|
| T5 | ул. Ленина 7, 8; Школьная 2–6; Южная 3–6; 50 лет Октября 8 | Großplattenbau, 5 Geschosse, Loggien/Balkone, **auf Pfählen mit Luftraum** (Permafrost), Flachdach mit Dachrand; Fassaden weiß, mintgrün, altrosa, ocker | **ANNAHME: unbekannte nördliche Großplattenserie** (Frage 2) |
| T9 | ул. Мира 1, 2 | 9 Geschosse, Platte, Giebelwand mit Rentier-Mosaik (PDF R3) | ANNAHME, offen |
| T3 | 50 лет Октября 1–4, 6, 7 | 3 Geschosse, ca. 52 × 15 m, einheitliche Reihe | ANNAHME, offen (Ziegel oder Block, vermutlich älter) |
| T2 | Школьная 1, 8, 9, 10; Мира 7, 9; Южная 1, 2, 7, 9, 11; Ленина 9 | 2 Geschosse; Fotos zeigen u. a. Schule mit vertikalen Lisenen, rosa Verwaltungsbau, verputzte Bauten mit Walmdach | ANNAHME, offen |

**Geschosshöhe und Achsmaß:** nicht belegt. Briefing V4 verbietet Schätzen. Für den
Graybox-Blockout schlage ich als sichtbar markierte **ANNAHME** 2,8 m Geschosshöhe vor (für
sowjetische Plattenbauten üblich, aber keine Quelle für Kadyktschan) und ermittle das
Achsmaß aus Fenster-Zählung auf den Referenzfotos gegen die OSM-Länge.

### Einrichtungen (Zuordnung)

| Einrichtung | Beleg | Gebäude-Zuordnung | Kennz. |
|---|---|---|---|
| Telefonzentrale (АТС) | ru.wikipedia: an der ул. Школьная | eines der 2-geschossigen Häuser Школьная 1/8/9/10 | ANNAHME |
| Poliklinik + Krankenhaus + Kommunaldienste | ru.wikipedia, PDF R2: ул. Мира | Kandidat Мира 9 (2 Geschosse, 99 × 43 m) | ANNAHME |
| Schule | Commons-Fotos „School“, „School interior“ | Kandidat an der Школьная (Name); Fassade mit vertikalen Lisenen | ANNAHME |
| Verwaltungsgebäude („Government building“, rosa) | Commons-Fotos | unbekannt | ANNAHME |
| Kulturhaus mit Saal und Mosaik | PDF R4, V10 (Fotos Innenraum: Glasmosaik mit Rentieren) | unbekannt; evtl. gesprengt | ANNAHME |
| Kesselhaus (котельная) | ru.wikipedia: fiel aus | unbekannt | ANNAHME |
| Läden, Kantine, Kindergarten, Sporthalle | PDF V10 | nicht gefunden | offen |

## 4. Vertiefung: Vertical-Slice-Block ул. Ленина

| Punkt | Ergebnis | Kennz. | Vertrauen |
|---|---|---|---|
| Kandidat | **ул. Ленина 8**: einziges 5-geschossiges Haus der Straße mit Lage | BELEGT (OSM) | Mittel |
| Lage | 63.08578 N, 147.05541 E; ca. 270 m O / 10 m S des Ursprungs | BELEGT (OSM) | Mittel |
| Grundriss | OSM-Rechteck 84,7 × 24,4 m, Längsachse 35° | BELEGT (OSM) | Niedrig: 24 m Tiefe ist für einen Plattenbau ungewöhnlich, vermutlich grob gezeichnet oder mit Anbau |
| Nachbar | ул. Ленина 7: L-Form ca. 61 × 22 m, 5 Geschosse, bildet mit Nr. 8 einen Hof | BELEGT (OSM) | Mittel |
| Ленина 18 | per Foto belegt, Lage unbekannt; das PDF-Beispiel `PLA_Lenina_18` | BELEGT (Foto) | Hoch (Existenz) / – (Lage) |
| Typenprojekt | T5, Serie unbekannt | ANNAHME | Niedrig |
| Wohnungsgrundrisse (1-/2-/3-Zimmer) | nicht gefunden | offen | – |

**Vorschlag:** Der Slice nutzt den Hof aus ул. Ленина 7 + 8 (Lage belegt). Ленина 18 wird
zugeordnet, sobald die Lage per Satellitenbild (Editor-Referenz) geklärt ist.

## 5. Asset-Liste (geplant, aus diesem Dossier)

| Asset | Inhalt | Budget |
|---|---|---|
| `PLA_<Straße>_<Nr>` (34 Adressen, Tabelle oben) | ein Packed Level Actor pro Adresse | Blockout: Box-Meshes; später Nanite-Kits, Texturen 2K, 10,24 px/cm |
| `PLA_OSM_<id>` (13 Gebäude ohne Adresse) | Industrie / Nebengebäude | Blockout-Boxen |
| `PLA_Lenina_18` | belegt, Lage offen | – |
| Kit `Buildings/T5/` | Wandplatte, Fensterplatte, Balkon/Loggia, Eingang, Ecke, Sockel mit Pfahlreihe, Dachrand, Treppenhaus | 2 Mesh-Varianten + Decals (Konzept) |
| Landscape | Copernicus DEM GLO-30 | Grobform; Lizenz prüfen (Frage 4) |

Engine-Screenshots: Phase 1 ist Recherche. Vorhanden ist nur der Technik-Test
`production/qa/evidence/2026-11-07-toolchain-spike-mac.png` (Template-Level startet auf dem Mac).

## 6. Entscheidungen (2026-11-07)

- **Schacht Nr. 10:** bleibt reale Industriekulisse, dort geschieht nichts Fiktives. Das Finale spielt an einem als **FIKTION** markierten Stollen.
- **Zusätzliche Straßen:** ул. 50 лет Октября und ул. Пионерская werden aufgenommen (Pillar 1).
- **Typenserien:** bleiben vorerst ANNAHME; Proportionen werden aus den Referenzfotos gemessen.

## 7. Offene Fragen

1. **Schacht Nr. 10 und 1996:** Einverstanden, dass der reale Schacht Nr. 10 nur Kulisse bleibt
   und das Finale an einem als FIKTION markierten Stollen spielt?
2. **Typenserien:** Ohne Archivquelle (Bauakten, Typenkatalog, ehemalige Bewohner,
   kadykchan.ru-Archiv) bleibt jede Serie eine ANNAHME. Weiter recherchieren oder mit
   gemessenen Fotoproportionen arbeiten?
3. **Neue Straßen:** ул. 50 лет Октября und ул. Пионерская sind nicht im Briefing, aber in OSM.
   Aufnehmen? (Vorschlag: ja, Pillar 1.)
4. **Lizenzen:** Copernicus-DEM-Lizenz und Satellitenbild-Nutzungsbedingungen sind nicht
   geprüft.
5. **Einwohner 1986:** en.wikipedia nennt 10 270, ru.wikipedia hat für 1986 keinen Wert. Für das
   Spiel ohne Folge, solange keine Zahl im Spieltext erscheint.

## Quellen

- ru.wikipedia, „Кадыкчан“, abgerufen 2026-11-07 (letzte Bearbeitung 20.04.2026)
- en.wikipedia, „Kadykchan“, abgerufen 2026-11-07 (letzte Bearbeitung 23.09.2026)
- RFE/RL Newsline, 15.11.1996, https://www.rferl.org/a/1082467.html
- OpenStreetMap, Overpass-Abfrage 2026-11-07, Bbox 63.06–63.12 N / 146.98–147.12 E,
  © OpenStreetMap-Mitwirkende, ODbL 1.0
- Wikimedia Commons, Category:Kadykchan (71 Dateien), Fotos Laika ac, 14.07.2011,
  CC BY-SA 2.0. **Nur Referenz, keine Spieltexturen** (Harte Regel)
- Warlam Schalamow, „Новая книга“, Kap. „Кадыкчан“ (über ru.wikipedia, nicht selbst gelesen)
- Briefing-PDF „Kadyktschan – Bauanleitung für die KI“, Folien R1, R2, V3, V4, V10
