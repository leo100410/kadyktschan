"""Story rooms: few rooms, densely furnished for the story (user 2026-11-07: "lieber ein paar Räume mit detaillierter
Einrichtung, die zur Story passt"). Used by build_buildings.py like interiors.section: same section frame (x along the
facade, the entrance axis is 0..AX, y inward from the outer facade face, z from the ground-floor level).

Family, flat, adit and every object here are FIKTION (concept: Mysterium); layouts ANNAHME. The family lives in an
unaddressed satellite-traced block on purpose (ethics rule: no real address traceable to living people). The story
follows prototypes/notebook-theses-concept: Walja and Lida leave on the bus in October 2003, Pjotr stays and keeps
boiler 2 of the Kesselhaus running through winter 2003/04; the radio amateur at the telephone exchange taped it.

The flats use the deep plan of interiors.py (2026-11-08 rework). S.clue / F.clue mark the finds the player inspects
with E (texts and order: tools/research/story_data.py).
"""
import math
import random

import furniture as fu
from furniture import cyl as _cyl, hcyl as _hcyl
from interiors import (Section, radiator, wall_unit, stairwell, flat_shell, furnish_generic, FRONT, BACK, BATH_SPLIT,
                       DEEP)


def cyl(S, cx, cy, z0, z1, r, mat, r1=None):
    S.cyl(cx, cy, z0, z1, r, mat, r1) if hasattr(S, "cyl") else _cyl(S, cx, cy, z0, z1, r, mat, r1)


def hcyl(S, axis, a0, a1, c, z, r, mat):
    S.hcyl(axis, a0, a1, c, z, r, mat) if hasattr(S, "hcyl") else _hcyl(S, axis, a0, a1, c, z, r, mat)


def calendar(S, x, y0, z0, crossed, face=-1):
    """Wall calendar on the wall plane x (paper sheet + red day marks); face = side the wall is seen from."""
    d = 0.004 * face
    S.box(x, x + 2 * d, y0, y0 + 0.4, z0, z0 + 0.55, "Paper")
    for k in range(crossed):  # days struck through, 7 per row
        cy, cz = y0 + 0.03 + (k % 7) * 0.052, z0 + 0.4 - (k // 7) * 0.07
        S.box(x + 2 * d, x + 3 * d, cy, cy + 0.035, cz, cz + 0.035, "Mural_Red")


def chair(S, cx, cy, back_dir, mat="Furniture"):
    fu.chair(fu.Place(S, cx - 0.2, cy - 0.2) if back_dir < 0 else fu.Place(S, cx + 0.2, cy + 0.2, 2), mat)


def paper_heap(S, x0, x1, y0, y1, n, z=0.0):
    for _ in range(n):
        x, y = S.rnd.uniform(x0, x1), S.rnd.uniform(y0, y1)
        w, d = S.rnd.uniform(0.12, 0.25), S.rnd.uniform(0.1, 0.18)
        h = z + S.rnd.uniform(0.0, 0.04)
        S.box(x, x + w, y, y + d, h, h + 0.004, "Paper")


def deep_section(part, AX, ST, T, seed):
    S = Section(part, ST - 0.22, random.Random(seed))
    y0, y1 = T, DEEP * AX - T
    stairwell(S, AX, ST, y0, y1)
    return S, y0, y1


def bath_and_wc(F, water=False):
    fu.bathtub(F.place(-5.92, BATH_SPLIT - 0.1, 3), 1.4)
    fu.washbasin(F.place(-4.6, BATH_SPLIT - 0.08, 2))
    fu.toilet(F.place(-5.92, 6.5, 3))
    if water:  # the tub kept full while the pipes still ran, jugs beside it
        F.box(-5.85, -5.29, 4.55, 5.8, 0.3, 0.5, "Glass")
        for k in range(2):  # along the tub, clear of the door
            F.cyl(-5.1, 4.62 + k * 0.22, 0.0, 0.35, 0.08, "Glass", r1=0.05)


# --------------------------------------------------------------------------------------------------- family flat
def family(part, AX, ST, T, seed):
    """Stairwell + flat A of the Gorbunovs + flat B of the neighbours, cleared out (contrast: the story flat is full,
    the neighbour's is not)."""
    S, y0, y1 = deep_section(part, AX, ST, T, seed)
    gorbunov(flat_shell(S, AX, y0, y1, False, "Wallpaper_Rose", "Wallpaper_Green"), y0, y1)
    neighbours(flat_shell(S, AX, y0, y1, True, "Wallpaper_Green", "Wallpaper_Green", "Linoleum", "Linoleum"), y0, y1)
    return S


def gorbunov(F, y0, y1):
    """Pjotr alone in the flat since the bus on 10 October 2003: the parents' sofa bed slept in on one side, Lida's
    room left as she left it, the kitchen set for one."""
    # --- living room: wall unit (one photo frame emptied), sofa bed, TV, table, the letter in the drawer
    wall_unit(F.box, -5.92, y0 + 0.5, y0 + 3.3)
    fu.sofa(F.place(-2.4, FRONT - 0.08, 2), 2.0, cushions=2)
    fu.blanket(F.place(-4.3, FRONT - 0.15, 2), -1.8, 0.0, 0.0, 0.8, 0.54)     # folds over the seat, hem hangs down
    fu.cushion(F.place(-4.35, FRONT - 0.9), 0.0, 0.35, 0.0, 0.6, 0.52, 0.66, "Paper")
    F.box(-4.4, -2.4, FRONT - 0.1, FRONT - 0.09, 0.9, 2.2, "Carpet")            # wall carpet
    fu.tv(F.place(-0.2, 0.9, 1))
    fu.table(F.place(-3.6, 1.6), 1.1, 0.8)
    fu.rug(F, -4.2, -1.6, 1.0, 3.4)
    for wx in (-5.2, -2.2):
        radiator(F.box, wx, wx + 1.4, y0 + 0.05)
        fu.curtains(F, wx, wx + 1.4, y0, 1)
    fu.nightstand(F.place(-4.9, FRONT - 0.08, 2), drawer_out=True)             # beside the sofa, drawer pulled out
    F.box(-5.22, -5.02, FRONT - 0.34, FRONT - 0.08, 0.55, 0.553, "Pic_LetterGorbunov")       # the unsent letter, on top
    F.clue("gorbunov_letter", -5.12, FRONT - 0.21, 0.56)
    for k in range(2):                                                         # photo frames on the wall unit: one emptied
        y_ = 1.0 + k * 0.6
        F.box(-5.47, -5.45, y_, y_ + 0.36, 1.12, 1.4, "Furniture")
        if k == 0:
            F.box(-5.45, -5.447, y_ + 0.02, y_ + 0.34, 1.14, 1.38, "Pic_FamilyPhoto")
    # --- Lida's room (bedroom): her bed, the satchel, exercise books, the drawing taped to the wall, a doll
    fu.bed(F.place(-5.92, 10.6, 3), 0.9, 1.8, second_pillow=False)
    fu.nightstand(F.place(-5.92, 11.5, 3))
    fu.wardrobe(F.place(-5.9, BACK + 0.08, 0), 1.2, open_leaf=True)            # her clothes gone
    fu.table(F.place(-3.95, 10.7), 0.85, 0.55)                                 # school desk at the window
    chair(F, -3.55, 10.3, -1)
    F.box(-3.9, -3.6, 10.8, 11.1, 0.74, 1.0, "Carpet")                          # ranec (school satchel)
    for k in range(3):
        F.box(-3.5 + k * 0.03, -3.3 + k * 0.03, 10.75 + k * 0.05, 11.0 + k * 0.05, 0.74 + k * 0.006, 0.744 + k * 0.006, "Paper")
    F.box(-5.92, -5.912, 9.0, 9.42, 1.1, 1.52, "Pic_DrawingLida")              # the drawing "Lida, 7 Jahre"
    F.cyl(-5.6, 11.3, 0.55, 0.75, 0.06, "Sofa", r1=0.04)                       # doll on the nightstand
    radiator(F.box, -5.2, -3.8, y1 - 0.17)
    fu.curtains(F, -5.2, -3.8, y1, -1, drawn=0.4)
    # --- kitchen: set for one, the bus day circled on the calendar, empty tins along the wall, window half papered
    fu.fridge(F.place(-0.08, BACK + 0.15, 1), open_door=True)
    fu.stove(F.place(-0.08, BACK + 0.85, 1), kettle=True)
    fu.kitchen_run(F.place(-0.08, BACK + 1.4, 1), 1.8, sink_at=1.2)
    fu.table(F.place(-2.6, 10.1), 0.9, 0.7)
    chair(F, -2.15, 9.75, -1)
    F.box(-2.95, -2.65, 9.3, 9.7, 0.0, 0.46, "Furniture")                       # second chair pushed to the wall
    F.cyl(-2.15, 10.35, 0.74, 0.76, 0.12, "Enamel")                            # one plate
    F.cyl(-1.9, 10.6, 0.74, 0.84, 0.04, "Enamel")                              # one mug
    F.cyl(-2.4, 10.65, 0.74, 0.76, 0.06, "Metal")                              # ashtray, full
    for k in range(5):
        F.hcyl("x", -2.43 + k * 0.012, -2.39 + k * 0.012, 10.63 + k * 0.008, 0.765, 0.004, "Paper")
    F.box(-2.55, -2.25, 10.15, 10.35, 0.74, 0.745, "Paper")                     # newspaper
    F.box(-2.92, -2.912, 7.95, 8.37, 1.15, 1.71, "Pic_CalendarGorbunov")       # October 2003, the bus day circled
    F.clue("gorbunov_calendar", -2.9, 8.16, 1.45)
    F.box(-2.92, -2.912, 8.6, 9.02, 1.15, 1.71, "Pic_Order")                   # the order to leave, "Не поеду" on it
    F.clue("gorbunov_order", -2.9, 8.81, 1.45)
    for k in range(18):                                                        # empty tins along the bedroom wall
        row = 0 if k < 8 else (1 if k < 14 else (2 if k < 17 else 3))
        idx = [0, 8, 14, 17][row]
        F.cyl(-2.85, 7.7 + (k - idx) * 0.09 + row * 0.045, row * 0.11, row * 0.11 + 0.11, 0.04, "Metal")
    F.box(-2.2, -1.5, y1 - 0.02, y1 - 0.01, 0.85, 2.3, "Paper")                 # half the window papered over
    F.box(-2.9, -2.6, 11.0, 11.25, 1.6, 1.82, "Enamel")                         # wired radio (radiotochka)
    radiator(F.box, -2.2, -0.8, y1 - 0.17)
    # --- hall: miner's helmet on the hook, empty hooks, felt boots, mail pushed under the door, telephone
    F.box(-2.9, -1.8, BACK - 0.12, BACK - 0.08, 1.65, 1.7, "Wood")
    for k in range(5):
        F.box(-2.85 + k * 0.22, -2.83 + k * 0.22, BACK - 0.18, BACK - 0.12, 1.58, 1.66, "Metal")
    F.cyl(-2.8, BACK - 0.25, 1.42, 1.56, 0.15, "Enamel", r1=0.11)             # helmet
    F.cyl(-2.8, BACK - 0.39, 1.47, 1.52, 0.03, "Glass")
    for bx in (-2.5, -2.32):
        F.box(bx, bx + 0.12, BACK - 0.45, BACK - 0.15, 0.0, 0.1, "Sofa")
        F.box(bx, bx + 0.12, BACK - 0.24, BACK - 0.12, 0.1, 0.45, "Sofa")
    paper_heap(F, -0.8, -0.2, 4.6, 5.5, 30)                                     # letters pushed under the door
    F.box(-3.92, -3.62, 5.6, 6.05, 0.8, 0.83, "Furniture")                     # telephone shelf between the bath and WC doors,
    F.box(-3.88, -3.68, 5.7, 5.95, 0.83, 0.9, "BlackPlastic")                  # receiver off the hook
    F.hcyl("y", 5.55, 5.8, -3.55, 0.4, 0.025, "BlackPlastic")
    bath_and_wc(F)
    F.cyl(-4.75, 5.75, 0.86, 0.96, 0.03, "Glass")                              # one toothbrush glass
    F.debris(-5.8, -0.2, y0 + 0.2, y1 - 0.2, 25)


def neighbours(F, y0, y1):
    """Flat B: the Sakharovs moved out properly - floor, walls, a mattress, newspapers, nothing personal."""
    F.box(-4.6, -2.7, 1.0, 2.9, 0.0, 0.15, "Sofa")                              # mattress on the floor
    paper_heap(F, -5.5, -4.8, 0.6, 1.4, 25)
    for wx in (-5.2, -2.2):
        radiator(F.box, wx, wx + 1.4, y0 + 0.05)
    radiator(F.box, -5.2, -3.8, y1 - 0.17)
    radiator(F.box, -2.2, -0.8, y1 - 0.17)
    fu.kitchen_run(F.place(-0.08, BACK + 1.4, 1), 1.8, sink_at=1.2, wall_cupboards=False)
    fu.toilet(F.place(-5.92, 6.5, 3))
    F.debris(-5.8, -0.2, y0 + 0.2, y1 - 0.2, 70)


# --------------------------------------------------------------------------------------------------- boiler house
def boiler(part, AX, ST, T, seed):
    """Boiler hall: boiler 1 cold and opened, boiler 2 kept alive by Pjotr, his cot in the warm corner beside it."""
    S = Section(part, ST - 0.22, random.Random(seed))
    depth, y0 = 2 * AX, T
    y1 = depth - 0.08
    box = S.box
    for x in (-2 * AX, 3 * AX):
        S.wall_x(x, y0, y1, "Paint_OilBlue", "Lime")
    S.wall_y(depth, -2 * AX - 0.08, 3 * AX + 0.08, "Paint_OilBlue", "Lime", doors=[(-0.6, 0.4)])
    box(-2 * AX + 0.08, 3 * AX - 0.08, y0, y1, 0.0, 0.012, "Concrete")
    # two lying fire-tube boilers on brick plinths, axis inward
    for cx in (-4.2, 5.3):
        box(cx - 0.8, cx + 0.8, 1.4, 5.5, 0.0, 0.5, "Concrete")
        hcyl(S, "y", 1.5, 5.4, cx, 1.35, 0.85, "Metal")
        hcyl(S, "y", 1.42, 1.5, cx, 1.35, 0.88, "Metal")                # front ring
        box(cx - 0.3, cx + 0.3, 1.38, 1.42, 0.75, 1.2, "BlackPlastic")  # firebox opening
        cyl(S, cx, 4.6, 2.15, ST - 0.22, 0.12, "Metal")                    # riser to the ceiling header
        for gx in (-0.35, 0.35):                                           # pressure gauges
            hcyl(S, "y", 1.36, 1.42, cx + gx, 1.95, 0.08, "Enamel")
    box(-4.5, -3.9, 0.9, 1.4, 0.0, 0.03, "BlackPlastic")                   # boiler 1: its door lies on the floor
    hcyl(S, "x", -4.2, 5.3, 4.6, ST - 0.36, 0.1, "Metal")                  # header pipe along the hall
    hcyl(S, "x", 5.3, 8.9, 5.6, 0.25, 0.06, "Metal")                       # return pipe at the floor
    # coal: heap in the hall beside boiler 2, shovel in it, a wheelbarrow. The strip in front of the boilers stays
    # free: it is the only way from the door to Pjotr's corner (user 2026-11-07: "Weg blockiert")
    for k in range(60):
        r = 0.9 * math.sqrt(S.rnd.random())
        a = S.rnd.uniform(0, 2 * math.pi)
        x, y = 3.55 + r * math.cos(a) * 0.75, 3.9 + r * math.sin(a) * 1.2
        h = (1 - r / 0.9) * 0.55 + S.rnd.uniform(0.02, 0.08)
        box(x, x + S.rnd.uniform(0.08, 0.2), y, y + S.rnd.uniform(0.08, 0.2), 0.0, h, "BlackPlastic")
    box(3.2, 3.24, 3.0, 3.04, 0.2, 1.3, "Wood")                            # shovel handle
    box(3.1, 3.34, 2.9, 3.1, 0.15, 0.2, "Metal")
    box(3.4, 3.9, 2.0, 2.8, 0.3, 0.55, "Metal")                            # wheelbarrow tray
    hcyl(S, "x", 3.6, 3.7, 2.9, 0.15, 0.15, "BlackPlastic")                # its wheel
    # Pjotr's corner by the warm boiler: cot, crate as a table, kettle, mug, kerosene lamp, logbook, field phone
    box(8.15, 8.9, 2.6, 4.6, 0.38, 0.42, "Metal")                          # iron cot
    for lx in (8.16, 8.86):
        for ly in (2.61, 4.56):
            box(lx, lx + 0.03, ly, ly + 0.03, 0.0, 0.42, "Metal")
    box(8.18, 8.88, 2.65, 4.55, 0.42, 0.52, "Sofa")                        # mattress
    box(8.16, 8.9, 3.2, 4.4, 0.52, 0.58, "Carpet")                         # blanket
    box(8.3, 8.8, 2.68, 3.05, 0.52, 0.64, "Sofa")                          # pillow
    box(7.4, 7.95, 3.0, 3.5, 0.0, 0.5, "Wood")                             # crate
    cyl(S, 7.55, 3.15, 0.5, 0.6, 0.04, "Enamel")                           # mug
    cyl(S, 7.8, 3.35, 0.5, 0.66, 0.09, "Metal", r1=0.07)                   # kettle
    cyl(S, 7.55, 3.4, 0.5, 0.52, 0.05, "Metal")                            # kerosene lamp
    cyl(S, 7.55, 3.4, 0.52, 0.66, 0.04, "Glass", r1=0.03)
    box(7.62, 7.92, 3.02, 3.245, 0.5, 0.51, "Pic_KesselLog")               # open logbook, facing the chair
    S.clue("kessel_log", 7.78, 3.11, 0.52)
    chair(S, 7.65, 2.55, -1, mat="Wood")
    box(8.9, 8.82, 3.6, 3.85, 1.2, 1.45, "BlackPlastic")                   # field telephone to the exchange
    box(8.88, 8.9, 3.85, 3.87, 0.3, 1.25, "BlackPlastic")                  # its cable down to the floor
    S.clue("kessel_phone", 8.84, 3.72, 1.32)
    calendar(S, 8.92, 2.7, 1.3, 7 * 4 + 5, face=-1)                       # winter 2003/04, the days struck through
    box(8.91, 8.92, 3.95, 4.2, 1.5, 1.68, "Paper")                         # family photo nailed above the cot
    box(8.85, 8.9, 4.65, 5.0, 0.6, 1.4, "Sofa")                            # quilted jacket on a nail
    for bx in (7.9, 8.05):
        box(bx, bx + 0.12, 4.65, 4.95, 0.0, 0.42, "Sofa")                  # felt boots
    # firewood along the back wall, workbench with a vice
    for k in range(40):
        lx = 6.4 + (k % 10) * 0.24
        hcyl(S, "y", 5.35, 5.85, lx, 0.07 + (k // 10) * 0.13, 0.065, "Wood")
    box(0.6, 2.6, 5.3, 5.85, 0.85, 0.9, "Wood")
    for lx in (0.65, 2.5):
        box(lx, lx + 0.06, 5.35, 5.8, 0.0, 0.85, "Wood")
    box(0.8, 1.05, 5.3, 5.45, 0.9, 1.05, "Metal")
    S.debris(-5.6, 2.0, y0 + 0.2, 1.3, 40)
    return S


# --------------------------------------------------------------------------------------------------- telephone exchange
def radio(part, AX, ST, T, seed):
    """ATS: corridor on the entrance axis, relay hall to the left, the radio amateur's room to the right."""
    S = Section(part, ST - 0.22, random.Random(seed))
    ceil = ST - 0.22
    depth, y0 = 2 * AX, T
    y1 = depth - 0.08
    box = S.box
    for x in (-2 * AX, 3 * AX):
        S.wall_x(x, y0, y1, "Paint_OilBlue", "Lime")
    S.wall_y(depth, -2 * AX - 0.08, 3 * AX + 0.08, "Paint_OilBlue", "Lime")
    for x in (0.0, AX):
        S.wall_x(x, y0, y1, "Paint_OilBlue", "Lime", doors=[(3.0, 3.8)])
    box(-2 * AX + 0.08, 3 * AX - 0.08, y0, y1, 0.0, 0.012, "Linoleum")
    # relay hall: three rows of step-by-step switch racks, cable tray over them, panels pulled off
    for rx in (-5.1, -3.5, -1.9):
        box(rx, rx + 0.3, 1.0, 5.4, 0.0, 0.06, "BlackPlastic")
        for k in range(8):
            ry = 1.05 + k * 0.54
            box(rx, rx + 0.3, ry, ry + 0.5, 0.06, 2.25, "Metal")
            if S.rnd.random() < 0.75:
                for side in (rx - 0.01, rx + 0.3):
                    box(side, side + 0.01, ry + 0.03, ry + 0.47, 0.15, 2.15, "BlackPlastic")
        box(rx - 0.05, rx + 0.35, 1.0, 5.4, 2.35, 2.4, "Metal")             # cable tray
        for _ in range(4):                                                   # cable bundles hanging down
            cy = S.rnd.uniform(1.2, 5.2)
            box(rx + 0.1, rx + 0.16, cy, cy + 0.06, S.rnd.uniform(1.3, 2.0), 2.35, "BlackPlastic")
    for _ in range(5):
        px, py = S.rnd.uniform(-5.6, -0.6), S.rnd.uniform(0.6, 5.4)
        box(px, px + 0.45, py, py + 0.5, 0.0, 0.02, "BlackPlastic")         # panels on the floor
    paper_heap(S, -2.6, -0.4, 0.5, 2.0, 30)                                 # punched tickets and forms
    # radio room: desk along the party wall with transceiver, receiver, reel-to-reel recorder, key, microphone
    box(8.2, 8.9, 1.4, 4.6, 0.72, 0.76, "Furniture")
    for ly in (1.45, 4.5):
        box(8.25, 8.85, ly, ly + 0.05, 0.0, 0.72, "Furniture")
    box(8.3, 8.85, 1.6, 2.3, 0.76, 1.02, "BlackPlastic")                    # transceiver
    for k in range(4):
        hcyl(S, "x", 8.26, 8.3, 1.72 + k * 0.16, 0.88, 0.025, "Metal")     # knobs
    box(8.3, 8.29, 1.75, 2.1, 0.92, 0.98, "Screen")                         # dial window
    box(8.45, 8.9, 1.6, 2.3, 1.25, 1.28, "Furniture")                       # shelf with the receiver
    box(8.5, 8.88, 1.65, 2.25, 1.28, 1.5, "Metal")
    box(8.35, 8.85, 2.6, 3.4, 0.76, 0.9, "BlackPlastic")                    # reel-to-reel recorder
    for ry in (2.8, 3.2):
        cyl(S, 8.6, ry, 0.9, 0.92, 0.15, "Metal")
        cyl(S, 8.6, ry, 0.92, 0.93, 0.03, "BlackPlastic")
    box(8.4, 8.6, 3.6, 3.75, 0.76, 0.78, "Metal")                           # morse key
    box(8.48, 8.52, 3.66, 3.7, 0.78, 0.82, "BlackPlastic")
    cyl(S, 8.5, 4.1, 0.76, 0.78, 0.07, "Metal")                             # desk microphone
    cyl(S, 8.5, 4.1, 0.78, 1.0, 0.01, "Metal")
    cyl(S, 8.5, 4.1, 1.0, 1.08, 0.03, "BlackPlastic")
    for hy in (3.9, 4.12):                                                   # headphones on the desk
        hcyl(S, "y", hy, hy + 0.03, 8.35, 0.8, 0.045, "BlackPlastic")
    box(8.33, 8.37, 3.93, 4.12, 0.8, 0.85, "Metal")
    box(8.29, 8.5, 2.31, 2.59, 0.76, 0.77, "Pic_RadioLog@90")               # logbook, facing the chair
    S.clue("ats_log", 8.37, 2.45, 0.79)
    cyl(S, 8.3, 4.4, 0.76, 0.78, 0.06, "Metal")                             # ashtray
    chair(S, 7.75, 3.0, -1)
    box(8.9, 8.92, 1.5, 4.5, 1.3, 2.3, "Paper")                             # world map
    for k in range(22):                                                      # QSL cards pinned around it
        cy, cz = S.rnd.uniform(1.4, 4.45), S.rnd.uniform(1.1, 2.4)
        if 1.5 < cy < 4.4 and 1.25 < cz < 2.3:
            continue
        box(8.88, 8.895, cy, cy + 0.14, cz, cz + 0.09, S.rnd.choice(("Paper", "Paper", "Enamel")))
    # antenna feed from the transceiver up and along the ceiling to the window
    box(8.85, 8.88, 2.2, 2.23, 1.02, ceil - 0.05, "BlackPlastic")
    box(4.5, 8.88, 2.2, 2.23, ceil - 0.08, ceil - 0.05, "BlackPlastic")
    box(4.5, 4.53, y0 + 0.02, 2.23, ceil - 0.08, ceil - 0.05, "BlackPlastic")
    # tape shelf on the back wall: numbered boxes, one gap (tape 41 is missing - it lies in the boiler house)
    for b_ in range(4):
        z = 0.4 + b_ * 0.45
        box(3.3, 6.9, y1 - 0.32, y1 - 0.02, z, z + 0.025, "Furniture")
        for k in range(18):
            if b_ == 2 and k == 4:
                continue
            bx = 3.35 + k * 0.19
            box(bx, bx + 0.16, y1 - 0.3, y1 - 0.12, z + 0.025, z + 0.205, "Paper")
    for sx in (3.3, 6.88):
        box(sx, sx + 0.02, y1 - 0.32, y1 - 0.02, 0.0, 2.2, "Furniture")
    S.clue("ats_shelf", 4.19, y1 - 0.2, 1.42)
    radiator(box, 3.8, 5.2, y0 + 0.05)
    radiator(box, 6.8, 8.2, y0 + 0.05)
    # corridor: notice board, shift list
    box(-0.1, -0.08, 1.0, 2.0, 1.3, 2.0, "Furniture")
    paper_heap(S, 0.2, 2.8, 0.5, 5.5, 15)
    for k in range(5):
        box(-0.12, -0.1, 1.05 + k * 0.18, 1.2 + k * 0.18, 1.5 + (k % 2) * 0.2, 1.7 + (k % 2) * 0.2, "Paper")
    S.debris(0.2, 2.8, y0 + 0.2, y1 - 0.2, 30)
    return S


# --------------------------------------------------------------------------------------------------- the spawn houses
def lenina8(part, AX, ST, T, seed):
    """ул. Ленина 8, where the player starts: flat A of Antonina Fjodorowna, the widow who stayed until 2005 and whom
    Pjotr kept in coal through winter 2003/04; flat B looted."""
    S, y0, y1 = deep_section(part, AX, ST, T, seed)
    antonina(flat_shell(S, AX, y0, y1, False, "Wallpaper_Green", "Wallpaper_Rose"), y0, y1)
    furnish_generic(flat_shell(S, AX, y0, y1, True, "Wallpaper_Rose", "Wallpaper_Green", "Linoleum"), "widow")
    return S


def antonina(F, y0, y1):
    """She lived in the one room she could heat: the iron bed moved next to the burzhuika (iron stove), its pipe out
    through a tin plate in the window; the rest of the flat stands cold."""
    # --- living room
    P = F.place(-5.92, 4.2, 3)
    fu.bed(P, 0.9, 1.95, frame="Metal", pillows=False)
    for k, (w, h) in enumerate(((0.6, 0.15), (0.5, 0.14), (0.4, 0.13))):        # pillow pyramid on the mattress, lace on top
        z = 0.48 + sum((0.15, 0.14, 0.13)[:k])
        fu.cushion(F.place(-5.85, 3.75 - w / 2), 0.0, 0.42 - k * 0.06, 0.0, w, z - 0.01, z + h,
                   "Paper" if k == 2 else "Sofa")
    F.box(-5.92, -5.905, 3.0, 4.3, 0.7, 2.0, "Carpet")                          # wall carpet over the bed (in front of the wall)
    sx, sy = -4.5, 0.9                                                         # burzhuika under the first window
    F.box(sx - 0.25, sx + 0.25, sy - 0.2, sy + 0.2, 0.15, 0.7, "Metal")
    for lx in (-0.22, 0.19):
        for ly in (-0.17, 0.14):
            F.box(sx + lx, sx + lx + 0.03, sy + ly, sy + ly + 0.03, 0.0, 0.15, "Metal")
    F.box(sx - 0.12, sx + 0.12, sy + 0.2, sy + 0.21, 0.3, 0.5, "BlackPlastic")  # fire door (room side)
    F.cyl(sx, sy, 0.7, 2.05, 0.06, "Metal")                                    # flue up ...
    F.hcyl("y", y0 + 0.02, sy, sx, 2.05, 0.06, "Metal")                        # ... and out through the window
    F.box(sx - 0.25, sx + 0.25, y0, y0 + 0.02, 1.85, 2.25, "Metal")            # tin plate in place of the pane
    F.box(sx - 0.45, sx + 0.45, sy - 0.45, sy + 0.55, 0.0, 0.014, "Metal")     # fire sheet on the floor boards
    F.cyl(sx + 0.55, sy + 0.2, 0.0, 0.32, 0.15, "Metal", r1=0.17)              # coal bucket, heaped
    for k in range(10):
        a = k * 0.6
        F.chunk(sx + 0.55 + 0.07 * math.cos(a), sy + 0.2 + 0.07 * math.sin(a), 0.3, 0.07, 0.06, 0.05, "BlackPlastic")
    F.box(sx - 0.75, sx - 0.71, sy - 0.1, sy - 0.06, 0.0, 0.8, "Wood")         # poker leaning
    for k in range(12):                                                        # firewood stacked beside it
        F.hcyl("y", 0.5, 0.95, sx - 0.95 + (k % 4) * 0.13, 0.065 + (k // 4) * 0.12, 0.06, "Wood")
    fu.table(F.place(-3.4, 1.6), 0.8, 0.8, top="Mural_Red")                    # table with oilcloth
    F.cyl(-3.0, 1.85, 0.74, 0.86, 0.035, "Glass")                              # tea glass ...
    F.cyl(-3.0, 1.85, 0.74, 0.81, 0.04, "Metal")                               # ... in its holder
    F.cyl(-2.8, 2.15, 0.74, 0.82, 0.05, "Enamel")                              # sugar bowl
    F.box(-3.3, -3.15, 2.2, 2.25, 0.74, 0.755, "Metal")                        # reading glasses
    F.box(-3.3, -3.0, 1.7, 1.925, 0.74, 0.743, "Pic_NoteAntonina")            # "Петя, спасибо за уголь ..."
    F.clue("antonina_note", -3.15, 1.81, 0.76)
    chair(F, -3.0, 1.25, -1, mat="Wood")                                       # at the window side of the table
    F.box(-5.92, -5.912, 1.3, 1.72, 1.1, 1.66, "Pic_CalendarAntonina")         # Jan-Mar 2004, the coal days marked
    F.clue("antonina_calendar", -5.9, 1.51, 1.38)
    fu.table(F.place(-2.0, 0.5), 0.6, 0.45, h=0.75, leg="Metal")                # sewing machine on its treadle table
    fu.sewing_machine(F.place(-1.95, 0.55))
    F.box(-1.95, -1.45, 0.52, 0.92, 0.04, 0.08, "Metal")                       # treadle
    fu.wardrobe(F.place(-2.5, FRONT - 0.08, 2), 1.3, h=1.0, d=0.45)            # sideboard by the hall wall
    F.box(-3.52, -3.27, FRONT - 0.3, FRONT - 0.28, 1.05, 1.38, "Furniture")    # husband's photo with a black ribbon
    F.box(-3.5, -3.29, FRONT - 0.302, FRONT - 0.3, 1.07, 1.36, "Pic_Husband")
    F.box(-2.9, -2.6, FRONT - 0.4, FRONT - 0.2, 1.05, 1.22, "Furniture")       # radio on the sideboard
    for k in range(4):                                                        # pots with dry stems on the sill
        px = -2.0 + k * 0.33
        F.cyl(px, y0 + 0.15, 0.85, 0.98, 0.06, "Concrete", r1=0.075)
        F.box(px - 0.005, px + 0.005, y0 + 0.14, y0 + 0.16, 0.98, 1.2 + 0.05 * k, "Wood")
    fu.rug(F, -3.9, -1.4, 1.2, 3.3)
    radiator(F.box, -2.2, -0.8, y0 + 0.05)
    fu.curtains(F, -2.2, -0.8, y0, 1, drawn=0.35)
    # --- kitchen: no water since 2003 - two enamel buckets and a jerrycan, the dead stove, the window blanket
    fu.fridge(F.place(-0.08, BACK + 0.15, 1))
    fu.stove(F.place(-0.08, BACK + 0.85, 1), pot=True)
    fu.kitchen_run(F.place(-0.08, BACK + 1.4, 1), 1.8, sink_at=1.2)
    for k, by in enumerate((9.4, 9.8)):
        F.cyl(-1.0, by, 0.0, 0.32, 0.15, "Enamel", r1=0.17)
        F.cyl(-1.0, by, 0.25, 0.27, 0.14, "Glass")                             # water standing in it
    F.box(-1.45, -1.15, 10.2, 10.6, 0.0, 0.5, "Metal")                         # jerrycan
    F.clue("antonina_water", -1.0, 9.6, 0.35)
    fu.table(F.place(-2.6, 10.1), 0.9, 0.7)
    F.cyl(-2.2, 10.45, 0.74, 0.76, 0.05, "Metal")                              # kerosene lamp: base ...
    F.cyl(-2.2, 10.45, 0.76, 0.96, 0.04, "Glass", r1=0.025)                    # ... chimney
    chair(F, -2.15, 9.75, -1, mat="Wood")
    F.box(-2.3, -0.7, y1 - 0.05, y1 - 0.02, 0.8, 2.3, "Carpet")                # blanket nailed over the window
    radiator(F.box, -2.2, -0.8, y1 - 0.17)
    # --- bedroom: too cold to use - bed stripped, the blankets carried to the stove
    fu.bed(F.place(-5.92, 10.8, 3), 1.4, 2.0, made=False)
    fu.wardrobe(F.place(-5.9, BACK + 0.08, 0), 1.2)
    for k in range(3):
        F.box(-3.8 + k * 0.05, -3.3 + k * 0.05, 8.2, 8.7, k * 0.4, k * 0.4 + 0.38, "Paper")  # boxes of jars
    radiator(F.box, -5.2, -3.8, y1 - 0.17)
    fu.curtains(F, -5.2, -3.8, y1, -1, drawn=0.5)
    # --- hall: coat on the rack, felt boots, walking stick, shopping bag
    F.box(-2.9, -1.8, BACK - 0.12, BACK - 0.08, 1.65, 1.7, "Wood")
    F.box(-2.7, -2.3, BACK - 0.25, BACK - 0.12, 0.6, 1.65, "Sofa")             # coat
    for bx in (-2.1, -1.92):
        F.box(bx, bx + 0.12, BACK - 0.45, BACK - 0.15, 0.0, 0.45, "Sofa")
    F.box(-0.4, -0.37, BACK - 0.12, BACK - 0.09, 0.0, 0.9, "Wood")              # stick
    F.box(-1.5, -1.1, FRONT + 0.1, FRONT + 0.4, 0.0, 0.45, "Carpet")            # avoska / bag
    bath_and_wc(F, water=True)
    F.debris(-5.8, -0.2, y0 + 0.2, y1 - 0.2, 12)


def lenina7(part, AX, ST, T, seed):
    """ул. Ленина 7, across the courtyard from the start: flat A of Wassili Orlow, brigade leader of Stollen 3; flat B
    under a fallen ceiling slab."""
    S, y0, y1 = deep_section(part, AX, ST, T, seed)
    orlow(flat_shell(S, AX, y0, y1, False, "Wallpaper_Rose", "Wallpaper_Green"), y0, y1)
    B = flat_shell(S, AX, y0, y1, True, "Wallpaper_Green", "Wallpaper_Rose", "Linoleum")
    furnish_generic(B, "widow")
    collapsed(B, y0, ST)
    return S


def orlow(F, y0, y1):
    """The brigade leader's living room is his office: the plan of Stollen 3 on the wall, the brigade photo with
    Gorbunov in it, one torn-out shift-book page on the desk, the key board in the hall with the gate key missing."""
    # --- living room / office
    fu.table(F.place(-5.4, 0.45), 1.4, 0.7, h=0.76)                            # desk under the first window
    F.box(-5.0, -4.76, 0.5, 0.82, 0.76, 0.763, "Pic_ShiftPage@180")            # the shift-book page, facing the chair
    F.clue("orlow_page", -4.88, 0.66, 0.78)
    F.box(-4.45, -4.2, 0.6, 0.95, 0.76, 0.78, "Paper")                         # notes
    F.cyl(-5.15, 0.85, 0.76, 0.93, 0.14, "Enamel", r1=0.11)                   # helmet with lamp
    F.cyl(-5.15, 0.71, 0.86, 0.9, 0.035, "Glass")
    fu.lamp(F.place(-4.15, 0.55), 0.0, 0.0, 0.76)
    chair(F, -4.7, 1.45, 1)
    F.box(-5.92, -5.905, 0.35, 1.73, 1.12, 2.15, "Pic_AditPlan")               # adit plan on the party wall, beside the shelves
    F.clue("orlow_plan", -5.9, 1.04, 1.63)
    for k in range(2):                                                         # bookshelves of binders and manuals
        fu.bookshelf(F.place(-5.92, 3.6 - k * 0.92, 3), 0.9, 1.9, fill=0.9)
    F.box(-3.66, -2.94, FRONT - 0.1, FRONT - 0.08, 1.28, 1.86, "Furniture")    # brigade photo frame
    F.box(-3.62, -2.98, FRONT - 0.102, FRONT - 0.1, 1.33, 1.81, "Pic_Brigade")
    F.clue("orlow_photo", -3.3, FRONT - 0.1, 1.57)
    F.box(-2.8, -2.5, FRONT - 0.1, FRONT - 0.09, 1.4, 1.8, "Mural_Red")        # pennant "Лучшая бригада"
    fu.armchair(F.place(-0.15, FRONT - 0.08, 2))                              # in the corner, clear of the door
    fu.tv(F.place(-0.2, 0.9, 1))
    fu.rug(F, -4.0, -1.5, 1.6, 3.4)
    for wx in (-5.2, -2.2):
        radiator(F.box, wx, wx + 1.4, y0 + 0.05)
        fu.curtains(F, wx, wx + 1.4, y0, 1, drawn=0.3)
    # --- bedroom: sofa bed, packing boxes never sent, pit boots
    fu.sofa(F.place(-5.92, 10.9, 3), 2.0, cushions=2)
    for k in range(4):                                                         # by the window, clear of the door
        F.box(-4.5 + (k % 2) * 0.55, -4.0 + (k % 2) * 0.55, 10.7, 11.2, (k // 2) * 0.42, (k // 2) * 0.42 + 0.4, "Paper")
    F.box(-3.4, -3.1, 9.5, 9.85, 0.0, 0.5, "Sofa")                             # pit boots
    fu.wardrobe(F.place(-5.9, BACK + 0.08, 0), 1.2, open_leaf=True)
    radiator(F.box, -5.2, -3.8, y1 - 0.17)
    # --- kitchen: one bottle, one glass, an ashtray; the rest packed
    fu.fridge(F.place(-0.08, BACK + 0.15, 1), open_door=True)
    fu.stove(F.place(-0.08, BACK + 0.85, 1))
    fu.kitchen_run(F.place(-0.08, BACK + 1.4, 1), 1.8, sink_at=1.2)
    fu.table(F.place(-2.6, 10.1), 0.9, 0.7)
    F.cyl(-2.2, 10.4, 0.74, 1.04, 0.035, "Glass")
    F.cyl(-2.0, 10.6, 0.74, 0.84, 0.03, "Glass")
    F.cyl(-2.45, 10.6, 0.74, 0.76, 0.06, "Metal")
    chair(F, -2.15, 9.75, -1)
    radiator(F.box, -2.2, -0.8, y1 - 0.17)
    # --- hall: the key board, every hook labelled, the adit gate's hook empty; canvas work jacket
    F.box(-0.1, -0.08, 6.0, 6.7, 1.35, 1.61, "Wood")                          # key board (labels in the picture)
    F.box(-0.102, -0.1, 6.0, 6.7, 1.35, 1.61, "Pic_KeyBoard")
    for k in range(6):                                                         # hooks, keys on all but the adit gate's
        hy = 6.7 - (30 + k * 160.67 + 71) / 1024 * 0.7                         # hook holes in T_Pic_KeyBoard (seen from -x)
        F.box(-0.135, -0.1, hy - 0.006, hy + 0.006, 1.522, 1.532, "Metal")
        F.box(-0.135, -0.125, hy - 0.006, hy + 0.006, 1.532, 1.55, "Metal")
        if k != 4:
            F.hcyl("x", -0.135, -0.12, hy, 1.505, 0.014, "Metal")            # ring
            F.box(-0.13, -0.124, hy - 0.004, hy + 0.004, 1.42, 1.492, "Metal") # shaft
            F.box(-0.13, -0.124, hy, hy + 0.016, 1.43, 1.45, "Metal")          # bit
            F.box(-0.13, -0.124, hy, hy + 0.012, 1.455, 1.47, "Metal")
    F.clue("orlow_keys", -0.12, 6.35, 1.5)
    F.box(-2.9, -1.8, BACK - 0.12, BACK - 0.08, 1.65, 1.7, "Wood")
    F.box(-2.7, -2.3, BACK - 0.27, BACK - 0.12, 0.5, 1.65, "Sofa")             # canvas work jacket
    bath_and_wc(F)
    F.debris(-5.8, -0.2, y0 + 0.2, y1 - 0.2, 30)


def collapsed(F, y0, ST):
    """Flat B of Lenina 7: the ceiling slab of the living room came down at the party wall and lies tipped across the
    furniture, broken pieces and rebar around it."""
    S = F.S
    # one tipped slab: high at the hall wall, its far edge on the floor by the window (a single solid, not steps)
    xa, xb = F.X(-5.9), F.X(-3.2)
    xa, xb = min(xa, xb), max(xa, xb)
    fu.ring_solid(S, [(xa, y0 + 0.3, 0.0), (xb, y0 + 0.3, 0.0), (xb, FRONT - 0.3, 1.9), (xa, FRONT - 0.3, 1.9)],
                  [(xa, y0 + 0.3, 0.2), (xb, y0 + 0.3, 0.2), (xb, FRONT - 0.3, 2.1), (xa, FRONT - 0.3, 2.1)], "Concrete")
    for k in range(30):
        F.chunk(S.rnd.uniform(-5.9, -1.5), S.rnd.uniform(y0 + 0.2, FRONT - 0.3), 0.0,
                S.rnd.uniform(0.1, 0.6), S.rnd.uniform(0.1, 0.45), S.rnd.uniform(0.05, 0.3), S.rnd.choice(("Concrete", "Lime")))
    for k in range(6):
        x = S.rnd.uniform(-5.6, -3.5)
        F.box(x, x + 0.015, 2.0, 2.015, 1.9, 2.55, "Metal")                     # rebar hanging from the gap
    F.debris(-5.9, -0.2, y0 + 0.2, FRONT - 0.2, 60)


ROOMS = {"family": family, "boiler": boiler, "radio": radio, "lenina8": lenina8, "lenina7": lenina7}
DEEP_KINDS = {"family", "lenina8", "lenina7"}   # sections 4 axes deep (interiors.DEEP)
# camera views for the evidence shots: (name, from (along, inward), look-at (along, inward)), eye 1.6 m
FLAT_VIEWS = (("stairwell", (1.5, 1.0), (1.0, 9.0)), ("{p}-living", (-1.0, 3.9), (-5.0, 1.0)),
              ("{p}-kitchen", (-1.2, 7.9), (-2.0, 11.0)), ("{p}-bedroom", (-3.4, 7.9), (-5.0, 10.5)),
              ("{p}-hall", (-0.5, 5.0), (-3.5, 6.5)))
VIEWS = {
    "family": tuple((n.format(p="gorbunov"), a, b) for n, a, b in FLAT_VIEWS) + (("neighbours", (4.0, 3.9), (8.0, 1.0)),),
    "boiler": (("kessel-pjotr", (7.0, 0.8), (8.4, 3.6)), ("kessel-hall", (1.5, 0.7), (5.3, 1.2))),
    "radio": (("ats-radio", (4.0, 1.0), (8.7, 3.0)), ("ats-tapes", (7.5, 1.5), (4.5, 5.9)), ("ats-relays", (-2.55, 5.6), (-2.55, 0.5))),
    "lenina8": tuple((n.format(p="antonina"), a, b) for n, a, b in FLAT_VIEWS),
    "lenina7": tuple((n.format(p="orlow"), a, b) for n, a, b in FLAT_VIEWS) + (("collapsed", (1.6, 3.9), (6.5, 1.0)),),
}
