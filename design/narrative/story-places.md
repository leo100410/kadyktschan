# Story-Orte (Stand 2026-11-08)

**Kanon-Status:** Provisional. Claude hat das autonom geschrieben, der Nutzer hat es noch nicht freigegeben. Die Gorbunow-Linie ist im Notizbuch-Prototyp bereits Established.

Alles hier ist **FIKTION** (Konzept: Mysterium). Die Orte liegen in echten Häusern von Kadyktschan.
Personen, Wohnungen, Stollen 3 und alle Gegenstände sind erfunden. Ethik-Regeln aus `design/gdd/game-concept.md` gelten:

- Das Unglück von 1996 wird nicht nachgebildet.
- Es gibt keine Toten und keine Schockmomente.
- Die Gulag-Geschichte kommt nur als sachliche Schicht vor.

Der Nutzer hat am 2026-11-08 gesagt, dass es ihm egal ist, ob ein Story-Haus eine echte Adresse hat.

## Die Geschichte in einem Absatz

Pjotr Gorbunow fährt bis zur Schließung am 15.11.2001 in **Stollen 3 (Nordhang)** ein, in der Brigade von **Wassili Orlow**.
Im Oktober 2003 fahren seine Frau Walja und seine Tochter Lida mit dem Bus nach Magadan. Pjotr bleibt.
Den Winter 2003/04 hält er allein Kessel 2 im **Kesselhaus** am Laufen. Er bringt der alten Nachbarin **Antonina Fjodorowna** Kohle für ihren Eisenofen.
Der **Funkamateur** in der Telefonzentrale nimmt die Gespräche mit dem Kesselhaus auf Band auf. Ein Band fehlt.
Am Ende führt die Spur über das Kesselhaus und die Stromleitung zum Tor von Stollen 3. Am Schlüsselbrett bei Orlow fehlt der Schlüssel dazu, und das Tor steht offen.

## Orte und was sie dem Spieler sagen

Die Reihenfolge folgt dem Weg aus dem Konzept: Zeugen-Wohnungen → Kesselhaus → Strom → Förderanlage → Stollen.

### 1. ул. Ленина 8, Wohnung A (Start) – Antonina Fjodorowna

- Eisenbett mit Kissenpyramide.
- **Burschuika** (kleiner Eisenofen), das Rohr führt durch eine Blechplatte im Fenster nach draußen. Daneben Kohleeimer und Schürhaken.
- Wandkalender Januar bis März 2004, mit „уголь“-Tagen markiert.
- Zettel auf dem Tisch: „Петя, спасибо за уголь …“
- Zwei Wassereimer und Kanister: Seit 2003 gibt es kein Wasser mehr.
- Petroleumlampe, Decke vor dem Küchenfenster.
- Foto ihres Mannes mit Trauerband.

**Aussage:** Jemand ist nach 2003 noch hier gewesen und hat geholfen. → Spur zum Kesselhaus.

### 2. ул. Ленина 8, Wohnung B

Geplündert (`interiors.flat`, „widow“). Gegenbild zu Antoninas bewohnter Wohnung.

### 3. ул. Ленина 7, Wohnung A – Brigadier Wassili Orlow

- **Plan von Stollen 3** an der Wand, die Strecken rot eingezeichnet.
- **Brigadefoto**, darauf Gorbunow. Wimpel „Лучшая бригада“.
- Auf dem Schreibtisch eine **herausgerissene Seite des Schichtbuchs**. Das ist eine der fehlenden Seiten aus dem Notizbuch-Prototyp.
- Grubenhelm mit Lampe, Ordner, gepackte Kisten, die nie abgeschickt wurden.
- **Schlüsselbrett:** Alle Haken sind beschriftet. Der Haken für das Stollentor ist leer.

**Aussage:** Der Stollen hat ein Tor, und jemand hat den Schlüssel.

### 4. ул. Ленина 7, Wohnung B

Eine Deckenplatte ist heruntergekommen. Der Raum ist nur von der Tür aus zu sehen und zeigt den Verfall.

### 5. Wohnung Gorbunow (Block ohne Hausnummer bei ул. Ленина)

Siehe `tools/asset-pipeline/story_rooms.py` (`family`): Küche für eine Person gedeckt, Kalender mit dem Abreisetag, Grubenhelm im Flur.

### 6. Kesselhaus

Siehe `story_rooms.boiler`: Pjotrs Ecke neben Kessel 2, Feldtelefon zur Telefonzentrale.

### 7. Telefonzentrale, ул. Школьная 8

Siehe `story_rooms.radio`: Funkraum, Tonbandregal, ein Band fehlt.

### 8. Stollen 3 (Nordhang)

Siehe `tools/research/mine_site.py` und `tools/asset-pipeline/build_mine.py`.

- **Lage:** 1,2 km nordwestlich der Ortsmitte, 540 m hangaufwärts vom Kesselhaus.
- **Eingang:** Betonportal im Einschnitt, mit Stützmauern. Das Gittertor steht offen.
- **Stollen:** 52 m lang. Auf den ersten 8 m Holzausbau, dann Stahlbögen. Schmalspurgleis, eine Lore steht im Stollen.
- **Ende:** Ein Bruch bei 44–52 m versperrt den Stollen. Davor hängen die leere Halterung der Ehrentafel, und auf einer Kiste liegt Pjotrs Zettel (gebaut 2026-11-08, nach dem Vorschlag unten).
- **Draußen:** Abraumhalde mit umgekippter Lore, Lampenhaus, Strommasten ins Tal.

**Offen:**

- Ob das Finale so bleibt (Vorschlag unten ist eingebaut). Vorgabe: kein Toter, keine Erklärung des Unglücks von 1996.
- Notizbuch-Thesen T3 und T4 (Wer hatte den Schlüssel? Wohin führt die Stromleitung?).
- Ein Stollenschild mit Schrift.

## Wahre Antwort (Under Review, Entscheidung beim Nutzer)

Vorschlag, der zu allen Funden passt:

- Pjotr nimmt im Frühjahr 2004 Orlows Schlüssel und geht in den Stollen.
- Dort holt er die Brigadetafel mit den Namen der Männer, die nicht mehr mitfahren konnten (FIKTION, kein Bezug auf 1996). Die Tafel lag vor dem Bruch.
- Danach verlässt er den Ort auf der Trasse nach Magadan zu Walja und Lida.
- Am Bruch findet der Spieler die leere Halterung der Tafel und Pjotrs Notiz.

Es gibt keinen Toten. Ob das so bleibt, entscheidet der Nutzer.

## Im Spiel (2026-11-08)

Die Geschichte ist als Aufgabenkette spielbar: 6 Aufgaben, 16 Funde (E = ansehen, N = Notizbuch, Marker zum nächsten
Ziel). Die Texte stehen in `tools/research/story_data.py`, die Positionen kommen aus den Raum-Skripten.

Reihenfolge: Antonina (Zettel, Kalender, Wassereimer) → Orlow (Brigadefoto, Schichtbuchseite, Schlüsselbrett) →
Gorbunow (Küchenkalender, Gedeck für eine Person, Brief) → Kesselhaus (Kesselbuch, Feldtelefon) → Telefonzentrale
(Tonbandregal, Funk-Logbuch) → Stollen 3 (Tor, leere Halterung, Pjotrs Zettel).

Neu erfunden für die Verbindungen (FIKTION, Provisional):

- die Adressliste der Brigade auf der Schichtbuchseite
- der Funkamateur heißt Schura, Gesprächstag ist Freitag
- Band 41 hat er Pjotr mitgegeben
- die Ehrentafel („доска почёта“) statt einer Tafel mit Namen von Verstorbenen

## Dramatischere Fassung (2026-11-08, Nutzer: „die Story kann ruhig etwas dramatischer sein als die echte, solange das Grundkonzept der Realität entspricht“)

**Reale Grundlage:** 2003 wurden in Kadyktschan Heizung und Strom abgestellt, und die Bewohner wurden zum Wegzug gedrängt. Die Ethik-Regeln gelten weiter: niemand stirbt, nichts zu 1996, keine Schockmomente.

1. **Antonina:** Petja bringt Kohle und Wasser, bis er Ende März 2004 nicht mehr kommt. Im Kalender steht „Пети нет“, das Wasser in den Eimern ist gefroren. Auf ihrem Zettel bittet sie: Orlow soll sie hier rausholen.
2. **Orlow:**
   - Auf dem Brigadefoto ist Petja eingekreist.
   - Die Schichtbuchseite sagt: Die Ehrentafel ist im Stollen geblieben, bei 42 m, der Schlüssel ist bei Orlow.
   - Der Stollenplan zeigt einen alten Wetterschacht.
   - Am Schlüsselbrett fehlt der Torschlüssel, die Wohnung wurde aufgebrochen.
3. **Gorbunow:**
   - Der Bescheid der Verwaltung ordnet die Räumung zum 31.10.2003 an. Pjotr hat quer darübergeschrieben: „Не поеду“ (ich fahre nicht).
   - Im Kalender ist der Abfahrtstag rot eingekreist: 10.10., der Bus mit Walja und Lida.
   - Sein Brief an Walja wurde nie abgeschickt.
4. **Kesselhaus:** Das Kesselbuch erzählt den Winter: −52 °C, die Stromleitung gekappt, er verheizt Bretter aus der Schule. Am 30.03. löscht er den Kessel; Antonina hat der Rettungshubschrauber geholt. Dann geht er in den Stollen, die Ehrentafel holen.
5. **Telefonzentrale:** Schura hört über das Feldtelefon mit. Pjotr hat die Tafel, dann gibt es ein Donnern, danach Stille. Band 41 fehlt.
6. **Stollen 3:**
   - Das Tor wurde aufgeschlossen, ein Kabel führt hinein.
   - Die Halterung der Tafel ist leer, dahinter liegt der Einsturz.
   - Im Wetterschacht sind Handabdrücke aus Kohlenstaub.
   - Pjotrs Zettel: Er lebt, ist durch den Schacht hinaus und auf dem Weg zu Walja und Lida.

Alle Personen, Daten und Texte sind FIKTION und Provisional. Die Bilder (Kalender, Fotos, Briefe) erzeugt `tools/asset-pipeline/story_textures.swift`.
