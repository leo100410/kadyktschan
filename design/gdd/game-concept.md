# Game Concept: Kadyktschan (Кадыкчан)

*Created: 2026-11-06*
*Status: Draft*
*Quelle: Briefing „Kadyktschan – Bauanleitung für die KI“ (PDF, 21 Folien) + /brainstorm-Sitzung 2026-11-06*

> **Kennzeichnung (gilt im ganzen Projekt):** **BELEGT** = durch Quelle gestützt ·
> **ANNAHME** = unsichere Tatsache, sichtbar markiert · **FIKTION** = bewusste Erfindung
> für das Spiel (Figuren, Briefe, Schichtbuch-Inhalte).

---

## Elevator Pitch

> Ein ruhiges First-Person-Mystery, in dem du die echte, 1:1 nachgebaute sowjetische
> Geisterstadt Kadyktschan erkundest, Briefe, Tonbänder und Schichtbücher findest und sie
> im Notizbuch zu Erkenntnissen verbindest – Erkenntnisse, die dir Wohnungen, das
> Kesselhaus und schließlich den Eingang zur Kohlemine öffnen.

---

## Core Identity

| Aspect | Detail |
| ---- | ---- |
| **Genre** | First-Person-Mystery / Exploration („Walking Sim“) mit Deduktion |
| **Platform** | PC (Steam / Epic). Referenz für Look und Performance: Windows + Mittelklasse-RTX. Entwicklung hauptsächlich auf Mac (Apple M5) |
| **Target Audience** | Explorer / Storyteller, siehe Target Player Profile |
| **Player Count** | Single-player |
| **Session Length** | 45–90 min |
| **Monetization** | Premium (ANNAHME, nicht besprochen) |
| **Estimated Scope** | Large (V1.0 ca. 48–60 Monate, solo, < 10 h/Woche) |
| **Comparable Titles** | Gone Home, Return of the Obra Dinn, Firewatch |

---

## Core Fantasy

Du bist allein in einer echten, riesigen, leisen Stadt am Ende der Kolyma-Trasse – und
verstehst Schicht für Schicht, wer hier gelebt hat und was geschehen ist. Die Stadt ist
kein Schauplatz für Schrecken, sondern ein Archiv aus Beton, Ölfarbe und Birken. Hier kann
man etwas tun, was kein anderes Spiel bietet: einen realen, verlassenen sowjetischen Ort in
seinem belegten Zustand von 2011 frei begehen und ihn durch eigenes Kombinieren lesen.

---

## Unique Hook

Wie **Gone Home**, **und außerdem** in einer echten verlassenen Sowjetstadt im Maßstab 1:1,
in der jede Erkenntnis der Schlüssel zu einem echten Ort ist.

- In einem Satz erklärbar: ja.
- Mit der Core Fantasy verbunden: Echtheit des Orts + Verstehen als Fortschritt.
- Wirkt auf das Gameplay: Die These im Notizbuch, nicht der Zufallsfund, öffnet Türen.

---

## Mysterium (FIKTION, an echten Orten verankert)

- **Die Familie:** Eine fiktive Bergarbeiterfamilie hat die Stadt beim Auszug nicht wie die
  anderen verlassen; ihre Spur endet. Ihre Geschichte ist die emotionale Auflösung.
- **Das Schichtbuch:** Ein unvollständiges Schichtbuch aus dem Bergwerk; fehlende Seiten
  verteilen sich über die Stadt.
- **Das Radio:** Tonbänder eines Funkamateurs, der in der Telefonzentrale (ATS,
  ул. Школьная – Ort BELEGT laut PDF R2) arbeitete. Das Radio ist Werkzeug und Erinnerung,
  keine unheimliche Präsenz: keine Stimmen „aus dem Nichts“ ohne diegetische Erklärung.
- **Der Weg:** Zeugen-Wohnungen → Kesselhaus → Strom → Förderanlage → Mine-Eingang.
- **Ethik-Regeln:**
  - Das fiktive Mysterium bildet das reale Unglück von 1996 nicht nach, erklärt es nicht
    und deutet es nicht um. Die Mine ist der Ort, nicht die Pointe.
  - Die Familie wird keiner realen, auf lebende Personen rückführbaren Adresse zugeordnet.
  - Gulag-Geschichte erscheint nur als belegte, sachliche Schicht (Dokumente, Orte).
  - **Offen:** Welcher Schacht war 1996 betroffen? Ist es Nr. 10, wird der Spiel-Schacht
    umbenannt oder ausdrücklich als FIKTION markiert. Klärt das Recherche-Dossier.

---

## Player Experience Analysis (MDA Framework)

### Target Aesthetics (What the player FEELS)

| Aesthetic | Priority | How We Deliver It |
| ---- | ---- | ---- |
| **Discovery** | 1 | Frei begehbare echte Straßen und Wohnungen; Funde erzählen; neue Bereiche durch Erkenntnis |
| **Narrative** | 2 | Fiktive Familie, Schichtbuch, Tonbänder; Geschichte setzt sich aus Fragmenten zusammen |
| **Sensation** | 3 | Weite, flaches Weißnachtlicht, Wind in leeren Fenstern, ehrliche Patina |
| **Challenge** | 4 | Faire Deduktion: Thesen mit festen Antwortfeldern (Wer / Wo / Wann) |
| **Submission** | 5 | Kein Kampf, kein Tod, eigenes Tempo |
| **Fantasy** | 6 | Rolle eines stillen Besuchers / Spurensuchers |
| **Fellowship** | N/A | Singleplayer |
| **Expression** | 7 | Selbst beschrifteter Stadtplan, eigene Notizen |

### Key Dynamics (Emergent player behaviors)

- Spieler lesen Räume wie Indizien: Wer hat hier gewohnt? Was fehlt?
- Spieler markieren auf dem Stadtplan eigene Vermutungen und kehren gezielt zurück.
- Spieler planen Wege zwischen Wärmeräumen (Kälte als sanfter Taktgeber).
- Spieler erzählen einander, was sie über die Familie herausgefunden haben.

### Core Mechanics (Systems we build)

1. **Erkunden:** First-Person-Bewegung (Gehen statt Rennen), Interaktion über `BPI_Interactable` (Tür, Schublade, Schalter, Dokument).
2. **Finden:** Hinweis-Data-Assets (Briefe, Tonbänder, Fotos, Schichtbuchseiten), Taschenlampe mit Batterie (wird nie ganz schwarz).
3. **Verbinden:** Notizbuch mit wenigen Kernthesen und festen Antwortfeldern (Wer / Wo / Wann), Abgleich gegen die Lösung.
4. **Öffnen:** Gegenstände (Schlüssel, Sicherungen, Strom) öffnen Bereiche – aber ihren Ort oder Zweck findet man nur durch Verstehen.
5. **Kälte:** Folgen ohne Strafe (enger werdendes Sichtfeld, zitternde Hand, erschwertes Schreiben), danach sanfter Rücksprung in den letzten Wärmeraum. Kein Tod.

---

## Player Motivation Profile

### Primary Psychological Needs Served

| Need | How This Game Satisfies It | Strength |
| ---- | ---- | ---- |
| **Autonomy** | Freie Wegewahl durch die Stadt; eigene Reihenfolge der Spuren; eigener Stadtplan | Core |
| **Competence** | Richtige These öffnet einen echten Ort; das Gefühl „ich habe es verstanden“ | Core |
| **Relatedness** | Bindung an die fiktive Familie und die Spuren echter Alltagsleben | Supporting |

### Player Type Appeal (Bartle Taxonomy)

- [x] **Explorers** — Primär: echte Orte entdecken, Zusammenhänge verstehen, Geheimnisse finden.
- [x] **Achievers** — Sekundär: Thesen lösen, alle Hinweise einer Wohnung finden.
- [ ] **Socializers** — Kein Fokus (Singleplayer).
- [ ] **Killers/Competitors** — Bewusst ausgeschlossen.

Quantic-Foundry-Motivation: Story und Discovery stark, Destruction und Competition bewusst null.

### Flow State Design

- **Onboarding curve:** Die ersten 10 Minuten in einem Hof mit Treppenhaus: Taschenlampe, Interaktion, erster Fund, erste kleine These, die eine Wohnungstür öffnet.
- **Difficulty scaling:** Thesen bekommen mehr Felder und mehr Ablenker; Hinweise verteilen sich über mehrere Gebäude.
- **Feedback clarity:** Richtige These = sichtbarer, diegetischer Effekt (Tür, Strom, Licht). Falsche These: neutraler Hinweis, wie viele Felder stimmen (Details im GDD).
- **Recovery from failure:** Es gibt kein Scheitern mit Verlust. Kälte setzt in den Wärmeraum zurück; falsche Thesen kosten nichts außer Zeit.

---

## Core Loop

### Moment-to-Moment (30 seconds)

Gehen, schauen, mit der Taschenlampe absuchen, Gegenstände untersuchen. Befriedigend durch
dichte, ehrliche Räume (jedes Objekt ist Beleg), präzisen Klang und lesbare Akzente.

### Short-Term (5-15 minutes)

Eine Zeugen-Wohnung oder ein Gebäude auswerten, Hinweise ins Notizbuch übernehmen, eine
Vermutung auf dem Stadtplan markieren. Das „noch eine Wohnung“-Gefühl entsteht aus offenen
Fragen.

### Session-Level (30-120 minutes)

Eine Kernthese lösen (Wer / Wo / Wann). Das öffnet einen neuen Bereich (Wohnung, Keller,
Kesselhaus, Strom). Das ist ein natürlicher Haltepunkt mit einer offenen Frage als Haken.

### Long-Term Progression

Die Geschichte der Familie bis zum Mine-Eingang. Die Stadt öffnet sich Bereich für Bereich.
Das Spiel ist vorbei, wenn die Familie verstanden ist (V1.0: Finale am Mine-Eingang).

### Retention Hooks

- **Curiosity:** ungelöste Thesen, verschlossene Türen, fehlende Schichtbuchseiten.
- **Investment:** eigener Stadtplan, eigene Notizen, Bindung an die Familie.
- **Social:** keiner (Singleplayer); Gesprächsstoff über die Geschichte.
- **Mastery:** besseres Lesen von Räumen und Dokumenten.

---

## Game Pillars

### Pillar 1: Echte Orte, ehrliche Quellen

Jede Straße und jedes Haus ist BELEGT oder als ANNAHME markiert; Erfundenes ist als FIKTION
gekennzeichnet. Für den Spieler: Die Stadt fühlt sich glaubwürdig an, weil sie es ist.

*Design test*: Verlangt die Spielbarkeit eine Abweichung (z. B. eine Tür, die es nie gab),
weichen wir mit einem belegten sowjetischen Normteil ab und markieren es als ANNAHME, statt
ein Unikat zu erfinden.

### Pillar 2: Jede Wohnung ist ein Zeuge

Jeder begehbare Innenraum trägt eine Spielfunktion und eine eigene Geschichte. Standard ist
„Kulisse/verschlossen“; Zeugen-Räume haben ein festes Budget pro Viertel.

*Design test*: Ein Raum ohne Funktion und ohne Geschichte wird gestrichen oder bleibt
verschlossen.

### Pillar 3: Stille statt Schrecken

Spannung kommt aus Kälte, Weite und Unverständnis, nie aus Bedrohung.

*Design test*: Statt eines Schreckmoments bauen wir einen leisen Fund. Batterie und Kälte
haben Folgen, aber keine Strafe; die Lampe wird nie ganz schwarz.

### Pillar 4: Verstehen ist der Schlüssel

Fortschritt entsteht durch verknüpfte Erkenntnisse, nicht durch Inventar-Grind.

*Design test*: Gegenstände dürfen Türen öffnen, aber ihren Ort oder Zweck findet man nur
durch Verstehen (man weiß, wessen Schlüssel es ist und wo diese Person wohnte).

### Pillar 5: Die Stadt schweigt, die Dinge erzählen

Die Welt zeigt nur den verlassenen Zustand von 2011, wie auf den Referenzfotos. Die
Vergangenheit begegnet dem Spieler nur durch Funde und Ton (Briefe, Tonbänder, Fotos, Radio).

*Design test*: Wollen wir zeigen, wie es früher war, bauen wir einen Fund oder eine Aufnahme,
keinen zweiten Raumzustand.

### Zusatzregel: Geschichte ist Fundament, nicht Pointe

Gulag-Geschichte und reale Unglücke erscheinen nur als belegte, sachliche Schicht. Sie sind
nie Auflösung, Twist oder übernatürliches Motiv.

### Anti-Pillars (What This Game Is NOT)

- **NOT Kampf, Monster oder Jump-Scares:** würde Pillar 3 zerstören.
- **NOT Crafting oder Inventar-Grind:** würde Pillar 4 zu Sammeln statt Verstehen machen.
- **NOT reale Opfer von 1996 namentlich, keine Gulag-Ausschlachtung:** verletzt die Zusatzregel und die Würde realer Menschen.
- **NOT Fotos aus dem Briefing-Deck als Spieltexturen:** Lizenz und Pillar 1 (eigene, ehrliche Assets).
- **NOT westliche Bauteile statt sowjetischer Normteile:** verletzt Pillar 1.
- **NOT ein zweiter Zeitzustand (1986):** verletzt Pillar 5 und verdoppelt die Produktion.

---

## Visual Identity Anchor: „Die ehrliche Patina“

*Gate AD-CONCEPT-VISUAL: STRONG.*

**Regel:** Jede Oberfläche zeigt, wer sie gemacht und benutzt hat und was die Zeit mit ihr
getan hat. Nichts ist dekorativ, alles ist Beleg.

**Prinzipien:**
1. **Beleg vor Schmuck.** *Test:* Wenn man einen Riss, Fleck oder Gegenstand entfernt und die Szene nichts verliert, kommt er raus.
2. **Stille durch Weite.** Ruhige Flächen, wenig Kontrastlärm, kein Schreck-Licht. *Test:* Wirkt ein Screenshot ohne Ton noch „leise“? Höchstens ein Fokuspunkt?
3. **Lesbar vor realistisch.** Hinweise sind über Silhouette, Akzentfarbe und Licht lesbar. *Test:* Ein neuer Spieler findet das wichtige Objekt in einem Raum in unter 10 Sekunden, nur mit Fensterlicht und Taschenlampe.

**Formensprache:** Geometrisch und seriell (Plattenbau-Raster, Fugen, Fensterachsen). Das
Organische kommt nur von außen: Birken, Frostrisse, abblätternder Putz, eingefallene Decken.

**Farbphilosophie (PDF-Palette mit Bedeutung):**
- Mintgrün + Kalkweiß: ruhige Grundfläche (Fassaden, Treppenhäuser, Putz, Fugen).
- Altrosa: menschliche Ebene (Sockel, Ladenfronten).
- Ölfarbenblau: das Private (Innenwände, Paneele).
- Plakatrot und Rost: einzige Akzente. Rot = Ideologie (Rentiere, Losungen), Rost = Industrie und Zeit.
- Faustregel: höchstens eine Akzentfarbe pro Blickfeld, und nur mit Bedeutung.
- Hexwerte legt das Art Bible fest.

**Licht:** Sommer 2011 mit Weißnächten und flachem Licht (Elemente aus „Weißnacht-Elegie“ als
Stimmung). Innen nur Fensterlicht und Taschenlampe. Post-Process nur Belichtung, leichte
Vignette, Filmkorn.

---

## Inspiration and References

| Reference | What We Take From It | What We Do Differently | Why It Matters |
| ---- | ---- | ---- | ---- |
| Gone Home | Geschichte durch Gegenstände in einem verlassenen Zuhause | Eine ganze reale Stadt statt eines Hauses; Thesen als Fortschritt | Belegt, dass Funde allein ein Spiel tragen |
| Return of the Obra Dinn | Deduktion mit festen Antwortfeldern | Reduziert auf wenige Kernthesen; im 3D-Raum verortet | Belegt, dass faire Deduktion begeistert |
| Firewatch | Weite, Licht, Einsamkeit, ruhiger Ton | Keine Dialogpartner; die Stadt selbst erzählt | Belegt Markt für ruhige First-Person-Erzählung |
| Outer Wilds | Wissen als Fortschritt | Mit Gegenständen kombiniert (Schlüssel durch Verstehen) | Belegt die Kraft von „Verstehen ist der Schlüssel“ |

**Non-game inspirations:** Warlam Schalamow, *Erzählungen aus Kolyma* (Ton, Respekt vor der
Geschichte); Urbex-Fotografie von Kadyktschan (Laika ac, Wikimedia Commons, CC BY-SA 2.0,
nur als Referenz); sowjetische Möbelkataloge der 1970er–80er.

---

## Target Player Profile

| Attribute | Detail |
| ---- | ---- |
| **Age range** | 20–45 (ANNAHME) |
| **Gaming experience** | Mid-core |
| **Time availability** | 45–90-Minuten-Sessions abends und am Wochenende |
| **Platform preference** | PC |
| **Current games they play** | Gone Home, Return of the Obra Dinn, Firewatch, What Remains of Edith Finch |
| **What they're looking for** | Echte Orte und Geschichte statt Fantasie-Horror; Deduktion ohne Kampf |
| **What would turn them away** | Jump-Scares, Kampf, Grind, respektlose Ausschlachtung realer Tragödien |

---

## Technical Considerations

| Consideration | Assessment |
| ---- | ---- |
| **Recommended Engine** | Unreal Engine 5.8 (Vorgabe PDF + Nutzerwahl; installiert: UE 5.8.4). Version wird mit `/setup-engine` fixiert |
| **Key Technical Challenges** | Mac als Entwicklungsmaschine (Nanite/VSM Beta, HW-Lumen Experimental, kein DLSS, macOS 27 außerhalb offizieller UE-5.8-Unterstützung); große Welt mit World Partition/HLOD/`DL_Interiors`-Streaming; Asset-Volumen solo |
| **Art Style** | 3D realistisch („Die ehrliche Patina“) |
| **Art Pipeline Complexity** | High (eigenes 3D): modulare Kits mit Trim Sheets, 10,24 px/cm, 2K-Standard, 2 Mesh-Varianten + Decals/Vertex Paint |
| **Audio Needs** | Moderate: MetaSounds-Ambience (Wind, Frost, Tropfen, Folie, Hunde, Radiorauschen), sparsame Musik (Klavier, Streicher) |
| **Networking** | None |
| **Content Volume** | V1.0: Zone Neuestes Kadyktschan + Mine-Eingang, 8–15 begehbare Adressen, 2–4 Stunden Spielzeit |
| **Procedural Systems** | PCG für Tundra, Lärchen, Birken in Höfen, Schutt an Hauswänden |

**Technische Vorgaben (aus PDF V1/V3, mit Anpassungen):**
- First Person Template, Blueprint + C++; Lumen, Virtual Shadow Maps, Nanite; World Partition mit Data Layers (`DL_Interiors` getrennt streambar); PCG, Enhanced Input, MetaSounds, Water (Status in 5.8 UNGEPRÜFT, Fallback Spline-Mesh).
- 1 Unreal-Einheit = 1 cm; Ursprung (0,0,0) = Zentrum von Neuestem Kadyktschan.
- Landscape aus Copernicus DEM 30 m (Grobform; Mikro-Topologie von Hand).
- Ein Packed Level Actor pro Adresse (z. B. `PLA_Lenina_18`); Ordner und Präfixe nach PDF V2 (`Content/Kadykchan/…`).
- Budget: 60 fps in 1440p mit TSR/DLSS auf Mittelklasse-RTX (Startannahme, im Vertical Slice gemessen).

### Begründete Abweichungen vom Briefing-PDF

| PDF-Vorgabe | Entscheidung | Begründung |
| ---- | ---- | ---- |
| Zwei Zustände: bewohnt 1986, verlassen 2011 (Harte Regel); `DL_1986`; Phase 5 „Zustand 1986“ | Nur verlassen 2011; `DL_1986` und Zeitebenen-Umschaltung entfallen | Nutzerentscheidung 2026-11-06: das Verlassene ist das Faszinierende; Vergangenheit nur über Funde und Ton |
| Zwei Lichtstimmungen (Sommer, Winter) | Zum Release nur Sommer | Referenzfotos zeigen Sommer 2011 (Pillar 1); halbiert Licht- und Performance-Arbeit |
| Satellitenbild georeferenziert als Decal aufs Terrain | Nur als Editor-Referenz, nicht im Build | Nutzungsbedingungen von Google/Bing/Yandex erlauben die Auslieferung vermutlich nicht (Wortlaut UNGEPRÜFT) |
| Perforce bevorzugt | Git + Git LFS | Solo, kein Serverbetrieb; das PDF erlaubt beides |
| Je Kit-Teil intakt / beschädigt / zerstört | Zwei Meshes + Decals und Vertex Paint | Asset-Volumen solo |
| Alle Gebäude mit eingerichteten Innenräumen | Außen 1:1 (Positionen, Silhouetten); innen 8–15 begehbare Adressen, Rest verschlossen | Asset-Volumen solo (TD + Producer) |
| Phasen 4–5 im selben Release | V1.0 = Zone Neuestes + Mine-Eingang; Neu, Alt, Schacht = Erweiterung | Sicherer Release statt kaputtem Fallback (Producer) |
| Story in Phase 6 | Story-Skelett und Ende im Vertical Slice | Ein Mystery ohne Kampf wird von der Story getragen (Producer) |
| Phase 1 Recherche-Dossier komplett zuerst | Zweigeteilt: Mini-Dossier Block ул. Ленина vor dem MVP, volles Dossier vor dem Stadt-Blockout | MVP und Vertical Slice brauchen Typenprojekt und Grundrisse früh |

---

## Risks and Open Questions

### Design Risks
- Das Thesen-System kann unfair oder per Raten lösbar sein (größtes Designrisiko). → Papier- oder UMG-Prototyp mit 2–3 Thesen zuerst.
- Zu viele funktionale Wohnungen machen die Stadt zur Schnitzeljagd und untergraben Pillar 1. → Budget an Zeugen-Räumen pro Viertel.
- Die Kälte wirkt im Sommer schwächer. → Kälte vor allem nachts, in Kellern, Treppenhäusern und der Mine (Details im GDD).

### Technical Risks
- Mac als Hauptmaschine: Nanite/VSM Beta, HW-Lumen Experimental, kein DLSS, macOS 27 außerhalb der offiziellen Unterstützung von UE 5.8 (Quelle: Epic-Doku „macOS Development Requirements“; Gültigkeit für 5.8.4 auf M5 UNGEPRÜFT). → Windows-RTX als einzige Referenz; früher Toolchain-Test.
- Windows-Builds lassen sich von macOS aus nicht paketieren; CrossOver ersetzt keinen Windows-Rechner als Referenz. → Windows-PC für Builds und Profiling.
- Xcode 27.2 liegt im erlaubten Bereich, ist aber nicht die Referenzversion (26.1.1). → C++-Build sofort testen.
- Nanite für Vegetation, Lumen-Kosten außen, Streaming von `DL_Interiors`. → Profiling im Vertical Slice; Vorladen beim Annähern.
- Water-Plugin-Status in 5.8 UNGEPRÜFT. → Fallback Spline-Mesh.

### Market Risks
- Die Nische für ruhige Walking Sims ist klein. → Echtheit des Orts als klares Alleinstellungsmerkmal.
- Ein ernstes historisches Thema kann Kritik auslösen. → Ethik-Regeln, Sensitivity-/Historiker-Check vor dem Release (Entscheidung des Nutzers).

### Scope Risks
- Asset-Volumen eines 1:1-Nachbaus übersteigt die Kapazität einer Person. → Obergrenze 8–15 begehbare Adressen, modulare Kits.
- Erstes Spiel, < 10 h/Woche, Unreal-Einarbeitung. → V1.0 als Ziel, volle Stadt als Erweiterung.

### Open Questions
- Welcher Schacht war 1996 betroffen? → Recherche-Dossier (PDF-Phase 1).
- Typenprojekte und Grundrisse der Wohnblocks an der ул. Ленина. → Mini-Dossier vor dem MVP.
- Läuft UE 5.8.4 stabil auf macOS 27 mit Xcode 27.2? → Toolchain-Test.
- Gilt die Copernicus-DEM-Lizenz für kommerzielle Nutzung? → im Dossier prüfen.
- Monetarisierung und Preis. → später.

---

## MVP Definition

**Core hypothesis**: „Verstehen öffnet Türen“ in echten Plattenbau-Wohnungen trägt eine
Session von 30+ Minuten.

**Vorbedingungen:** Mini-Dossier für den Block an der ул. Ленина (Typenprojekt, Grundrisse,
Quelle, Vertrauensgrad); Toolchain-Test (C++-Projekt auf dem Mac bauen, auf Windows paketieren).

**Required for MVP**:
1. Ein Hof und ein Plattenbau mit Treppenhaus (Graybox, maßstäblich nach Typenprojekt)
2. Zwei Zeugen-Wohnungen mit Funden
3. Eine Kernthese (Wer / Wo / Wann) im Minimal-Notizbuch, die eine Tür öffnet
4. Taschenlampe mit Batterie
5. Kälte mit Wärmeraum
6. Interaktion (Tür, Schublade, Dokument)

**Explicitly NOT in MVP** (defer to later):
- Finale Assets, Materialien und Licht
- Stadtplan, Speichern
- Mehrere Gebäude, Gelände und Vegetation
- Radio und Tonbänder (außer als Platzhalter)

### Scope Tiers (if budget/time shrinks)

Zeiten bei < 10 h/Woche (ANNAHME), Producer-Schätzung skaliert.

| Tier | Content | Features | Timeline |
| ---- | ---- | ---- | ---- |
| **MVP** | Ein Hof, ein Block, 2 Zeugen-Wohnungen | Kernloop mit 1 These, Lampe, Kälte | 6–9 Monate |
| **Vertical Slice** | Block an der ул. Ленина in Final-Qualität, Kulturhaus-Saal | + Story-Skelett und Ende festgelegt, Speichern, Stadtplan, Windows-Build | +8–10 Monate |
| **V1.0 / Alpha** | Gelände und Silhouette der ganzen Stadt, Zone Neuestes komplett, Mine-Eingang als Finale | Alle Systeme, Story vollständig, eine Lichtstimmung (Sommer) | +30–36 Monate |
| **Full Vision** | Zonen Neu und Alt, Schacht Nr. 10, Polish | Erweiterung nach V1.0 | offen |

**Zuordnung der PDF-Phasen:** 1 Recherche-Dossier → vor MVP (Mini) und vor V1.0-Blockout
(voll) · 2 Gelände, Lageplan, Blockout → V1.0 · 3 Vertical Slice → Vertical Slice · 4 Zone
Neuestes → V1.0 · 5 Neu, Alt, Schacht → Full Vision · 6 Story, Polish, Performance →
Story-Skelett im Vertical Slice, Rest V1.0.

---

## Gate Results (2026-11-06)

| Gate | Verdict | Handling |
| ---- | ---- | ---- |
| CD-PILLARS | CONCERNS | Gelöst: P4-Regel, P5 neu gefasst, Ethik-Zusatzregel, BELEGT/ANNAHME/FIKTION, Batterie/Kälte ohne Strafe |
| AD-CONCEPT-VISUAL | STRONG | Richtung A „Die ehrliche Patina“ gewählt |
| TD-FEASIBILITY | CONCERNS | Notiert: Windows-RTX als Referenz, Toolchain-Test zuerst, Satellitenbild nur Referenz, Git LFS |
| PR-SCOPE | OPTIMISTIC | Anpassungen übernommen (Story früher, V1.0 begrenzt, Dossier zweigeteilt, weniger Varianten, Innenraum-Obergrenze) |

---

## Next Steps

- [ ] `/setup-engine` — Unreal Engine 5.8 fixieren, Engine-Referenz anlegen
- [ ] PDF-Phase 1 (Mini): Recherche-Dossier Block ул. Ленина
- [ ] Toolchain-Test: C++-Projekt Mac → Windows-Build
- [ ] `/art-bible` — Visual Identity Anchor ausarbeiten (Hexwerte, Verfallsgrad)
- [ ] `/design-review design/gdd/game-concept.md`
- [ ] `/prototype notebook-theses` — Thesen-System (Papier/UMG)
- [ ] `/map-systems`, dann `/design-system` je System
- [ ] `/create-architecture`, `/architecture-decision`, `/architecture-review`
- [ ] `/vertical-slice`, `/playtest-report`, `/gate-check`
