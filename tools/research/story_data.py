"""Story path for the game: objectives in order, the finds of each one (title + text the player reads with E) and
where they lie. Writes Content/Kadykchan/Data/Story.json for AKdkStoryDirector.

Usage: python3 -I tools/research/story_data.py
Reads the find positions the builders export (assets/buildings/buildings_manifest.json "clues",
assets/mine/mine_manifest.json "clues") and the entrances of Content/Kadykchan/Data/TownMap.json.

Canon: design/narrative/story-places.md (Provisional; the ending is a proposal Under Review). FIKTION throughout;
ethics rules of the concept: no deaths, nothing about 1996, the Gulag only as a factual layer.
"""
import json, os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")

STEPS = [
    ("antonina", "Antonina (Lenina 8)",
     "Sieh dich in Antoninas Wohnung um: ул. Ленина 8, der Eingang vor dir, im Treppenhaus die Tür links.",
     [("antonina_note", "Zettel auf dem Tisch",
       "„Петя, спасибо за уголь. Храни тебя Бог. Если увидишь Орлова — пусть заберёт меня отсюда. — А. Ф.“\n\n"
       "(Petja, danke für die Kohle. Gott schütze dich. Wenn du Orlow siehst – er soll mich hier rausholen.)\n\n"
       "Der Zettel wurde nie abgeholt."),
      ("antonina_calendar", "Wandkalender 2004",
       "Januar bis März 2004. Alle drei, vier Tage steht in zittriger Schrift „уголь“ – Kohle.\n\n"
       "Am 28., 29., 30. und 31. März steht dasselbe: „Пети нет“ – Petja ist nicht gekommen.\n"
       "Darunter: „Вода замёрзла. В печке последние дрова.“ – Das Wasser ist gefroren. Die letzten Scheite im Ofen."),
      ("antonina_water", "Eimer in der Küche",
       "Zwei Emailleeimer und ein Kanister. Seit dem 1. November 2003 gibt es in Kadyktschan weder Wasser noch Heizung.\n\n"
       "Das Wasser in den Eimern ist zu Eis gefroren. Ein Becher steckt darin fest.")],
     "Antonina lebte nach der Abschaltung allein im kalten Block. Petja brachte ihr Kohle – bis er Ende März 2004 "
     "nicht mehr kam. Sie wollte, dass Brigadier Orlow sie holt. Orlow wohnte gegenüber, in der ул. Ленина 7."),
    ("orlow", "Brigadier Orlow (Lenina 7)",
     "Wer ist Petja, und warum kam er nicht mehr? Durchsuche Brigadier Orlows Wohnung: ул. Ленина 7, Tür links.",
     [("orlow_photo", "Brigadefoto",
       "Zwölf Männer vor dem Portal von Stollen 3, Juli 1999. Einer ist mit Kuli eingekreist: „Петя“.\n\n"
       "Daneben der Wimpel „Лучшая бригада“ – beste Brigade."),
      ("orlow_page", "Seite aus dem Schichtbuch",
       "„15.11.2001. Letzte Schicht. Stollen auf Befehl geschlossen. Die Ehrentafel ist im Stollen geblieben, 42 m. "
       "Tor versiegeln. Der Schlüssel ist bei mir. — Orlow“\n\n"
       "Darunter die Adressen der Brigade. Rot unterstrichen: „Горбунов П. – дом без номера у Ленина, кв. 1“."),
      ("orlow_plan", "Plan von Stollen 3",
       "Grubenplan im Maßstab 1:500. Bei 42 m ist mit Bleistift die Ehrentafel eingetragen.\n\n"
       "Kurz davor, blau: „вент. ходок → выход на склон“ – ein alter Wetterschacht, Ausgang am Hang."),
      ("orlow_keys", "Schlüsselbrett",
       "Sechs Haken, jeder beschriftet. Unter dem fünften steht „штольня 3 – ворота“ – Stollen 3, Tor.\n\n"
       "Der Haken ist leer. Am Türrahmen der Wohnung sind frische Hebelspuren – jemand ist eingebrochen.")],
     "Petja ist Pjotr Gorbunow aus Orlows Brigade. Jemand ist in Orlows Wohnung eingebrochen und hat den Schlüssel "
     "zum Stollentor mitgenommen. Gorbunow wohnte im Block ohne Hausnummer an der ул. Ленина."),
    ("gorbunov", "Wohnung Gorbunow",
     "Finde Pjotr Gorbunows Wohnung: der Block ohne Hausnummer an der ул. Ленина (Karte Nr. 1), Tür links.",
     [("gorbunov_order", "Bescheid der Verwaltung",
       "„ПРЕДПИСАНИЕ. Wärme- und Stromversorgung werden am 01.11.2003 eingestellt. Alle Bewohner haben die Siedlung "
       "bis zum 31.10.2003 zu verlassen. Wer bleibt, bleibt auf eigene Verantwortung.“\n\n"
       "Quer darüber mit Kugelschreiber: „Не поеду. П. Г.“ – Ich fahre nicht."),
      ("gorbunov_calendar", "Küchenkalender",
       "Oktober 2003. Die Tage bis zum 9. sind abgestrichen. Der 10. ist rot eingekreist: "
       "„автобус 7:40 — Валя и Лида“.\n\nAn diesem Morgen fuhren seine Frau und seine Tochter nach Magadan. Ohne ihn."),
      ("gorbunov_letter", "Brief auf dem Nachttisch",
       "„Валя, родная! Я не могу уехать. В нашем доме остались старики … Если котёл встанет, они замёрзнут.“\n\n"
       "(Walja, Liebste! Ich kann nicht weg. In unserem Haus sind noch die Alten. Wenn der Kessel stehen bleibt, "
       "erfrieren sie. Die Verwaltung hat den Strom abgedreht, ich halte den Kessel mit Holz am Laufen. "
       "Im Frühjahr komme ich. Sag Lida: Papa ist nicht stur, Papa hat Dienst.)\n\nNie abgeschickt.")],
     "Pjotr hat sich der Räumung widersetzt und ist geblieben, um mit Kessel 2 im Kesselhaus die letzten Alten durch "
     "den Winter zu bringen. Das Kesselhaus liegt im Nordwesten (Karte Nr. 2)."),
    ("kessel", "Kesselhaus",
     "Geh zum Kesselhaus im Nordwesten (Karte Nr. 2). Pjotrs Ecke ist neben Kessel 2, ganz rechts.",
     [("kessel_log", "Pjotrs Kesselbuch",
       "Ein Winter in Zahlen: Druck fällt, die Kohle geht aus, er verheizt Bretter aus der Schule. 14.02.: „Stromleitung "
       "gekappt. Nur noch Holz.“ 27.02.: „−52 Grad draußen. Ich halte durch.“\n\n"
       "30.03.2004: „Котёл 2 погашен. Антонину забрал вертолёт МЧС. Греть больше некого. Иду в третью штольню за "
       "доской почёта. Ребята поедут со мной.“\n\n(Kessel 2 gelöscht. Antonina hat der Rettungshubschrauber geholt. "
       "Es gibt niemanden mehr zu wärmen. Ich gehe in Stollen 3, die Ehrentafel holen. Die Jungs fahren mit mir.)"),
      ("kessel_phone", "Feldtelefon",
       "Eine Leitung zur Telefonzentrale – und eine zweite, frisch verlegte, die den Hang hinauf führt.\n\n"
       "Auf Pappe daneben: „Шура – АТС, по полевому“. Schura, der Funkamateur, hörte mit.")],
     "Als die letzten Alten fort waren, löschte Pjotr den Kessel und ging in den gesperrten Stollen, um die Ehrentafel "
     "seiner Brigade herauszuholen. Schura in der Telefonzentrale hat alles mitgehört (Karte Nr. 3)."),
    ("ats", "Telefonzentrale",
     "Geh zur Telefonzentrale, ул. Школьная 8 (Karte Nr. 3). Der Funkraum ist rechts vom Flur.",
     [("ats_log", "Funk-Logbuch",
       "03.04.2004, 09:15: „Er ist drin. Tor mit Orlows Schlüssel geöffnet.“\n11:40: „Die Tafel ist bei ihm. Er kommt "
       "zurück.“\n11:52: „Грохот. Связь пропала.“ – Ein Donnern. Die Verbindung ist weg.\n\n"
       "In Rot: „12:30 Stille. 16:00 Stille. 04.04. 08:00 Stille. In Sussuman angerufen. Rettung erst im Frühjahr.“"),
      ("ats_shelf", "Tonbandregal",
       "Bänder 1 bis 72, sauber nummeriert. Nummer 41 fehlt.\n\n"
       "Auf dem leeren Platz ein Zettel: „41 – 03.04.2004, штольня. Отдать Орлову.“ – Für Orlow.")],
     "Im Stollen gab es einen Einsturz, während Pjotr mit der Tafel auf dem Rückweg war. Danach nur noch Stille. "
     "Niemand kam ihm zu Hilfe. Stollen 3 liegt oben am Nordhang (Karte Nr. 8)."),
    ("mine", "Stollen 3",
     "Steig zu Stollen 3 am Nordhang hinauf (Karte Nr. 8). Folge dem Kabel in den Stollen. Taschenlampe: L.",
     [("mine_gate", "Das Tor",
       "Das Gittertor steht offen, aufgeschlossen, nicht aufgebrochen. Am Boden läuft ein Telefonkabel hinein."),
      ("mine_board", "Leere Halterung",
       "Zwei Halterungen im Fels, dazwischen ein heller Fleck, wo zwanzig Jahre die Ehrentafel der Brigade hing. "
       "Sie ist abgeschraubt, nicht abgerissen.\n\nDahinter versperrt Geröll den Stollen. Das Kabel verschwindet darin."),
      ("mine_vent", "Der Wetterschacht",
       "Ein alter Holzrahmen, dahinter Sprossen, die steil nach oben ins Dunkel führen. "
       "Auf den Pfosten schwarze Handabdrücke aus Kohlenstaub – frisch, von innen nach oben."),
      ("mine_note", "Pjotrs Zettel",
       "„Завалило за мной. Выхожу через вент. ходок. Доска со мной. Ребята едут домой. Шура, Орлов — я живой. "
       "Валя, Лида — иду. — П. Г., 04.04.2004“\n\n(Hinter mir ist es eingestürzt. Ich gehe durch den Wetterschacht "
       "raus. Die Tafel habe ich. Die Jungs fahren nach Hause. Schura, Orlow – ich lebe. Walja, Lida – ich komme.)")],
     "Pjotr hat den Einsturz überlebt. Er kletterte durch den alten Wetterschacht hinaus, mit der Ehrentafel seiner "
     "Brigade, und machte sich auf den Weg nach Magadan, zu Walja und Lida.\n\n"
     "Ende dieser Version. Das Finale ist ein Vorschlag (design/narrative/story-places.md)."),
]


# English (user 2026-11-09): per step (place, goal, done) and per find (title, text); Russian quotes stay Russian
EN_STEPS = {
    "antonina": ("Antonina (Lenina 8)",
                 "Look around Antonina's flat: ul. Lenina 8, the entrance in front of you, in the stairwell the door on the left.",
                 "After the shutdown Antonina lived alone in the cold block. Petya brought her coal – until he stopped coming at "
                 "the end of March 2004. She wanted brigade leader Orlov to come for her. Orlov lived across the yard, at ul. Lenina 7."),
    "orlow": ("Brigade leader Orlov (Lenina 7)",
              "Who is Petya, and why did he stop coming? Search brigade leader Orlov's flat: ul. Lenina 7, door on the left.",
              "Petya is Pyotr Gorbunov from Orlov's brigade. Someone broke into Orlov's flat and took the key to the adit gate. "
              "Gorbunov lived in the block without a house number on ul. Lenina."),
    "gorbunov": ("Gorbunov's flat",
                 "Find Pyotr Gorbunov's flat: the block without a house number on ul. Lenina (map no. 1), door on the left.",
                 "Pyotr defied the evacuation and stayed, to keep boiler 2 in the boiler house running and get the last old people "
                 "through the winter. The boiler house is in the north-west (map no. 2)."),
    "kessel": ("Boiler house",
               "Go to the boiler house in the north-west (map no. 2). Pyotr's corner is next to boiler 2, on the far right.",
               "When the last old people were gone, Pyotr put out the boiler and went into the sealed adit to bring out his "
               "brigade's board of honour. Shura at the telephone exchange heard everything (map no. 3)."),
    "ats": ("Telephone exchange",
            "Go to the telephone exchange, ul. Shkolnaya 8 (map no. 3). The radio room is to the right of the corridor.",
            "The adit collapsed while Pyotr was on his way back with the board. After that, only silence. Nobody came to help. "
            "Adit 3 lies up on the northern slope (map no. 8)."),
    "mine": ("Adit 3",
             "Climb up to Adit 3 on the northern slope (map no. 8). Follow the cable into the adit. Flashlight: L.",
             "Pyotr survived the collapse. He climbed out through the old ventilation raise with his brigade's board of honour "
             "and set off for Magadan, to Valya and Lida.\n\nEnd of this version. The ending is a proposal."),
}
EN_FINDS = {
    "antonina_note": ("Note on the table",
                      "\u201eПетя, спасибо за уголь. Храни тебя Бог. Если увидишь Орлова — пусть заберёт меня отсюда. — А. Ф.\u201c\n\n"
                      "(Petya, thank you for the coal. God keep you. If you see Orlov – tell him to get me out of here.)\n\n"
                      "Nobody ever picked up the note."),
    "antonina_calendar": ("Wall calendar 2004",
                          "January to March 2004. Every three or four days, in shaky handwriting: \u201eуголь\u201c – coal.\n\n"
                          "On 28, 29, 30 and 31 March the same words: \u201eПети нет\u201c – Petya did not come.\n"
                          "Below: \u201eThe water has frozen. The last logs are in the stove.\u201c"),
    "antonina_water": ("Buckets in the kitchen",
                       "Two enamel buckets and a canister. Since 1 November 2003 Kadykchan has had neither water nor heating.\n\n"
                       "The water in the buckets has frozen solid. A mug is stuck in the ice."),
    "orlow_photo": ("Brigade photo",
                    "Twelve men in front of the portal of Adit 3, July 1999. One is circled in ballpoint: \u201eПетя\u201c.\n\n"
                    "Beside it the pennant \u201eЛучшая бригада\u201c – best brigade."),
    "orlow_page": ("Page from the shift log",
                   "\u201e15.11.2001. Last shift. Adit closed by order. The board of honour has stayed in the adit, 42 m. "
                   "Seal the gate. I have the key. — Orlov\u201c\n\n"
                   "Below, the brigade's addresses. Underlined in red: \u201eГорбунов П. – дом без номера у Ленина, кв. 1\u201c – "
                   "the block without a number on Lenina Street."),
    "orlow_plan": ("Plan of Adit 3",
                   "Mine plan, scale 1:500. At 42 m the board of honour is pencilled in.\n\n"
                   "Just before it, in blue: \u201eвент. ходок → выход на склон\u201c – an old ventilation raise, exit on the slope."),
    "orlow_keys": ("Key board",
                   "Six hooks, each labelled. Under the fifth: \u201eштольня 3 – ворота\u201c – Adit 3, gate.\n\n"
                   "The hook is empty. Fresh pry marks on the door frame – someone broke in."),
    "gorbunov_order": ("Order from the administration",
                       "\u201eORDER. Heating and electricity will be cut off on 01.11.2003. All residents must leave the settlement "
                       "by 31.10.2003. Those who stay do so at their own risk.\u201c\n\n"
                       "Scrawled across it in ballpoint: \u201eНе поеду. П. Г.\u201c – I am not going."),
    "gorbunov_calendar": ("Kitchen calendar",
                          "October 2003. The days up to the 9th are crossed out. The 10th is circled in red: "
                          "\u201eавтобус 7:40 — Валя и Лида\u201c.\n\nThat morning his wife and daughter left for Magadan. Without him."),
    "gorbunov_letter": ("Letter on the bedside table",
                        "\u201eВаля, родная! Я не могу уехать. В нашем доме остались старики … Если котёл встанет, они замёрзнут.\u201c\n\n"
                        "(Valya, my love! I can't leave. The old people are still in our building. If the boiler stops, they'll "
                        "freeze. The administration has cut the power, I keep the boiler going on wood. I'll come in spring. "
                        "Tell Lida: papa isn't stubborn, papa is on duty.)\n\nNever sent."),
    "kessel_log": ("Pyotr's boiler log",
                   "A winter in numbers: the pressure falls, the coal runs out, he burns planks from the school. 14.02: \u201ePower "
                   "line cut. Only wood now.\u201c 27.02: \u201e−52 degrees outside. Holding on.\u201c\n\n"
                   "30.03.2004: \u201eКотёл 2 погашен. Антонину забрал вертолёт МЧС. Греть больше некого. Иду в третью штольню за "
                   "доской почёта. Ребята поедут со мной.\u201c\n\n(Boiler 2 put out. The rescue helicopter took Antonina. There "
                   "is no one left to keep warm. I'm going into Adit 3 for the board of honour. The lads are coming with me.)"),
    "kessel_phone": ("Field telephone",
                     "One line to the telephone exchange – and a second, freshly laid, running up the slope.\n\n"
                     "On a piece of cardboard: \u201eШура – АТС, по полевому\u201c. Shura, the radio amateur, was listening."),
    "ats_log": ("Radio log",
                "03.04.2004, 09:15: \u201eHe is in. Gate opened with Orlov's key.\u201c\n11:40: \u201eHe has the board. He is "
                "coming back.\u201c\n11:52: \u201eГрохот. Связь пропала.\u201c – A roar. The line is dead.\n\n"
                "In red: \u201e12:30 silence. 16:00 silence. 04.04 08:00 silence. Called Susuman. No rescue before spring.\u201c"),
    "ats_shelf": ("Tape shelf",
                  "Tapes 1 to 72, neatly numbered. Number 41 is missing.\n\n"
                  "On the empty space a note: \u201e41 – 03.04.2004, штольня. Отдать Орлову.\u201c – For Orlov."),
    "mine_gate": ("The gate", "The barred gate stands open, unlocked, not forced. A telephone cable runs in along the floor."),
    "mine_board": ("Empty brackets",
                   "Two brackets in the rock, between them a pale patch where the brigade's board of honour hung for twenty "
                   "years. It was unscrewed, not torn off.\n\nBehind it, rubble blocks the adit. The cable disappears into it."),
    "mine_vent": ("The ventilation raise",
                  "An old timber frame, behind it rungs climbing steeply up into the dark. "
                  "On the posts, black handprints of coal dust – fresh, leading upwards."),
    "mine_note": ("Pyotr's note",
                  "\u201eЗавалило за мной. Выхожу через вент. ходок. Доска со мной. Ребята едут домой. Шура, Орлов — я живой. "
                  "Валя, Лида — иду. — П. Г., 04.04.2004\u201c\n\n(It caved in behind me. I'm getting out through the ventilation "
                  "raise. I have the board. The lads are going home. Shura, Orlov – I'm alive. Valya, Lida – I'm coming.)"),
}


def main():
    clues = {}
    for b in json.load(open(os.path.join(ROOT, "assets/buildings/buildings_manifest.json"))):
        clues.update(b.get("clues") or {})
    clues.update(json.load(open(os.path.join(ROOT, "assets/mine/mine_manifest.json"))).get("clues") or {})
    places = {p["name"]: p for p in json.load(open(os.path.join(ROOT, "Content/Kadykchan/Data/TownMap.json")))["places"]}
    out = []
    for sid, place, goal, finds, done in STEPS:
        missing = [c for c, _, _ in finds if c not in clues]
        assert not missing, "no position for %s (builders not re-run?)" % missing
        door_e, door_n = places[place]["door"]
        zs = [clues[c][2] for c, _, _ in finds]
        assert sid in EN_STEPS and all(c in EN_FINDS for c, _, _ in finds), "English text missing for " + sid
        p_en, g_en, d_en = EN_STEPS[sid]
        out.append({"id": sid, "place": place, "goal": goal, "done": done, "place_en": p_en, "goal_en": g_en, "done_en": d_en,
                    "door": [round(door_n, 2), round(door_e, 2), round(min(zs) - 1.5, 2)],
                    "clues": [{"id": c, "title": t, "text": x, "title_en": EN_FINDS[c][0], "text_en": EN_FINDS[c][1],
                               "pos": clues[c]} for c, t, x in finds]})
    power_site = os.path.join(ROOT, "assets/power/site.json")
    if os.path.exists(power_site):
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from power_update import power_step
        out.insert(0, power_step(json.load(open(power_site))))
    path = os.path.join(ROOT, "Content/Kadykchan/Data/Story.json")
    json.dump({"steps": out}, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("story: %d steps, %d finds -> %s" % (len(out), sum(len(s["clues"]) for s in out), path))


if __name__ == "__main__":
    main()
