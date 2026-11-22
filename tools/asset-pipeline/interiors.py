"""Ground-floor stair section with two furnished flats (briefing V5, PDF phase 3 "zwei Wohnungen").

Used by build_buildings.py. Everything is built in section space: x along the facade (walking
direction of the entrance edge, the stairwell occupies x 0..AX), y inward from the outer facade
face, z from the ground-floor level. Layout and furniture are ANNAHME: the type-series floor plans
are not documented (dossier question 2); props follow the V5 list and 1970s-80s catalogue shapes.

Flat A lies at x -2AX..0, flat B mirrored at x AX..3AX. Same plan, different lives (V5 rule).
"""
import random

WALL = 0.16          # interior wall thickness
PANEL = 1.5          # oil-paint panel height (art bible 4.3)


def section(part, AX, ST, T, seed):
    rnd = random.Random(seed)
    ceil = ST - 0.22
    depth = 2 * AX                    # facade to spine
    y0, y1 = T, depth - 0.08          # inner face of the facade .. spine face
    S = Section(part, ceil, rnd)

    # party walls and the spine closing the section (generic walls are skipped here; the generic spine has
    # gaps at the cell edges that let daylight through)
    for x in (-2 * AX, 3 * AX):
        S.wall_x(x, y0, y1, "Lime", "Lime")
    S.wall_y(depth, -2 * AX - 0.08, 3 * AX + 0.08, "Paint_Mint", "Lime")
    # stairwell walls with flat doors at the back (hall side)
    for x in (0.0, AX):
        S.wall_x(x, y0, y1, "Paint_Mint", "Lime", doors=[(depth - 1.6, depth - 0.7)])
    stairwell(S, AX, y0, y1)
    flat(S, AX, y0, y1, mirror=False, life="family")
    flat(S, AX, y0, y1, mirror=True, life="widow")


class Section:
    def __init__(self, part, ceil, rnd):
        self.p, self.ceil, self.rnd = part, ceil, rnd

    def box(self, x0, x1, y0, y1, z0, z1, mat):
        self.p.box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1, mat)

    def _wall(self, a0, a1, c0, c1, lower, upper, doors, along_x):
        """Wall from a0..a1 along one axis, thickness c0..c1 on the other; doors = [(a_from, a_to)]."""
        cuts = sorted(doors or [])
        spans, a = [], a0
        for d0, d1 in cuts:
            spans.append((a, d0)); a = d1
        spans.append((a, a1))
        for s0, s1 in spans:
            if s1 - s0 < 0.01:
                continue
            for z0, z1, m in ((0.0, PANEL, lower), (PANEL, self.ceil, upper)):
                if along_x:
                    self.box(s0, s1, c0, c1, z0, z1, m)
                else:
                    self.box(c0, c1, s0, s1, z0, z1, m)
        for d0, d1 in cuts:  # lintel above each door (doors 2.05 m)
            if along_x:
                self.box(d0, d1, c0, c1, 2.05, self.ceil, upper)
            else:
                self.box(c0, c1, d0, d1, 2.05, self.ceil, upper)

    def wall_x(self, x, y0, y1, lower, upper, doors=None):
        self._wall(y0, y1, x - WALL / 2, x + WALL / 2, lower, upper, doors, along_x=False)

    def wall_y(self, y, x0, x1, lower, upper, doors=None):
        self._wall(min(x0, x1), max(x0, x1), y - WALL / 2, y + WALL / 2, lower, upper, doors, along_x=True)

    def debris(self, x0, x1, y0, y1, n):
        """Fallen plaster and ceiling pieces (art bible 6: eingefallene Decken)."""
        for _ in range(n):
            x, y = self.rnd.uniform(x0, x1), self.rnd.uniform(y0, y1)
            w, d = self.rnd.uniform(0.05, 0.4), self.rnd.uniform(0.05, 0.35)
            self.box(x, x + w, y, y + d, 0.0, self.rnd.uniform(0.01, 0.05), "Lime")


def stairwell(S, AX, y0, y1):
    # floor: worn concrete; mailboxes on the wall; first flight to the half landing, blocked by collapsed debris
    S.box(0.08, AX - 0.08, y0, y1, 0.0, 0.01, "Concrete")
    for k in range(5):  # mailbox row (почтовые ящики), sheet metal
        S.box(0.1, 0.32, 1.0 + k * 0.34, 1.3 + k * 0.34, 1.25, 1.6, "Metal")
    steps, rise = 9, 1.3 / 9
    for k in range(steps):
        S.box(0.2, 1.4, 2.4 + k * 0.28, 2.4 + (k + 1) * 0.28, 0.0, rise * (k + 1), "Concrete")
    S.box(0.2, AX - 0.2, 2.4 + steps * 0.28, y1, 0.0, 1.3, "Concrete")          # half landing
    S.box(1.5, 1.55, 2.4, 2.4 + steps * 0.28, 0.0, 2.2, "Metal")               # railing post line
    for k in range(6):  # rubble heap where the second flight came down
        S.box(1.6 + S.rnd.uniform(0, 0.6), 2.6, 2.6 + k * 0.4, 3.0 + k * 0.4, 0.0, S.rnd.uniform(0.2, 0.9), "Concrete")
    S.debris(0.2, AX - 0.2, y0, 2.3, 25)


def flat(S, AX, y0, y1, mirror, life):
    """One flat: room (facade, outer axis), kitchen (facade, stair axis), hall + bath at the back."""
    X = (lambda x: x) if not mirror else (lambda x: AX - x)
    def box(x0, x1, ya, yb, z0, z1, m):
        S.box(X(x0), X(x1), ya, yb, z0, z1, m)
    front = 3.6                                  # front zone depth from the facade
    wp = "Wallpaper_Rose" if life == "family" else "Wallpaper_Green"
    floor_room = "FloorBoards" if life == "family" else "Linoleum"
    # floors
    box(-2 * AX + 0.08, -AX - 0.08, y0, front, 0.0, 0.012, floor_room)
    box(-AX + 0.08, -0.08, y0, front, 0.0, 0.012, "Linoleum")
    box(-2 * AX + 0.08, -0.08, front, y1, 0.0, 0.012, "Linoleum")
    # walls: room | kitchen, front zone | back zone (doors to room and kitchen), bathroom wall
    S.wall_x(X(-AX), y0, front, wp, wp)
    S.wall_y(front, X(-2 * AX), X(0.0), wp, wp, doors=[tuple(sorted((X(-4.6), X(-3.8)))), tuple(sorted((X(-1.6), X(-0.8))))])
    S.wall_x(X(-4.2), front, y1, "Paint_OilBlue", "Lime", doors=[(front + 0.7, front + 1.5)])
    # --- room: wall unit, wall carpet over the sofa, table, radiator under the window, TV, photos
    wall_unit(box, -2 * AX + 0.1, y0 + 0.3, y0 + 2.9)                                    # Schrankwand
    box(-AX - 0.1, -AX - 0.12, y0 + 0.7, y0 + 2.7, 0.9, 2.3, "Carpet")                   # Teppich an der Wand
    box(-AX - 0.95, -AX - 0.1, y0 + 0.8, y0 + 2.7, 0.0, 0.45, "Sofa")                    # sofa / bed
    box(-AX - 0.3, -AX - 0.1, y0 + 0.8, y0 + 2.7, 0.45, 0.85, "Sofa")
    box(-4.9, -4.1, y0 + 1.4, y0 + 2.2, 0.72, 0.76, "Furniture")                         # table top
    for lx, ly in ((-4.85, 1.45), (-4.15, 1.45), (-4.85, 2.15), (-4.15, 2.15)):
        box(lx - 0.02, lx + 0.02, y0 + ly - 0.02, y0 + ly + 0.02, 0.0, 0.72, "Furniture")
    if life == "family":
        for cx in (-4.75, -4.25):                                                        # two chairs
            box(cx - 0.2, cx + 0.2, y0 + 2.3, y0 + 2.7, 0.42, 0.46, "Furniture")
            box(cx - 0.2, cx + 0.2, y0 + 2.66, y0 + 2.7, 0.46, 0.95, "Furniture")
    else:
        box(-4.8, -4.4, y0 + 0.9, y0 + 1.3, 0.0, 0.05, "Furniture")                      # fallen chair
    radiator(box, -5.2, -3.8, y0 + 0.05)
    box(-5.4, -4.9, y0 + 2.75, y0 + 3.15, 0.0, 0.6, "Furniture")                          # TV stand, corner by the wall unit
    box(-5.35, -4.95, y0 + 2.75, y0 + 3.2, 0.6, 1.1, "BlackPlastic")                     # tube TV
    box(-5.3, -5.0, y0 + 2.72, y0 + 2.75, 0.68, 1.02, "Screen")
    for k in range(3):  # photos on the wall towards the back zone
        box(-5.3 + k * 0.45, -5.0 + k * 0.45, front - 0.1, front - 0.09, 1.5 + (k % 2) * 0.2, 1.85 + (k % 2) * 0.2, "Paper")
    # --- kitchen: electric stove, ZIL-style fridge, sink cabinet, table, calendar, radiator
    box(-0.65, -0.1, y0 + 2.6, y0 + 3.2, 0.0, 0.85, "Enamel")                            # Elektroherd
    for bx, by in ((-0.55, 2.7), (-0.3, 2.7), (-0.55, 2.95), (-0.3, 2.95)):
        box(bx, bx + 0.16, y0 + by, y0 + by + 0.16, 0.85, 0.87, "BlackPlastic")          # hot plates
    box(-1.3, -0.7, y0 + 2.6, y0 + 3.2, 0.0, 1.55, "Enamel")                             # Kühlschrank
    box(-2.9, -1.4, y0 + 2.7, y0 + 3.25, 0.0, 0.85, "Furniture")                         # sink cabinet
    box(-2.5, -2.0, y0 + 2.75, y0 + 3.15, 0.85, 0.87, "Metal")                           # steel sink
    box(-2.2, -1.4, y0 + 0.9, y0 + 1.6, 0.72, 0.76, "Furniture")                         # kitchen table
    radiator(box, -2.2, -0.8, y0 + 0.05)
    box(-0.11, -0.1, y0 + 1.2, y0 + 1.6, 1.4, 1.95, "Paper")                             # wall calendar (stair-side wall)
    # --- hall: dial telephone on a shelf, coat rack
    box(-0.5, -0.1, front + 0.4, front + 0.7, 0.9, 0.93, "Furniture")
    box(-0.4, -0.2, front + 0.45, front + 0.65, 0.93, 1.02, "BlackPlastic")              # Wählscheibentelefon
    box(-3.6, -2.6, y1 - 0.08, y1 - 0.05, 1.6, 1.65, "Furniture")                        # coat rail
    # --- bathroom: enamel bathtub, sink
    box(-5.9, -4.4, front + 0.1, front + 0.8, 0.0, 0.55, "Enamel")                       # Emaille-Wanne (rim)
    box(-5.8, -4.5, front + 0.2, front + 0.7, 0.2, 0.56, "Metal")                        # inside, darker
    box(-4.7, -4.35, y1 - 0.5, y1 - 0.1, 0.75, 0.9, "Enamel")                            # washbasin
    # --- decay: debris; the widow's flat was left in a hurry, more fallen ceiling
    xa, xb = sorted((X(-2 * AX + 0.2), X(-0.2)))
    S.debris(xa, xb, y0 + 0.2, y1 - 0.2, 40 if life == "family" else 90)


def radiator(box, x0, x1, y):
    """Cast-iron radiator (Gusseisen-Heizkörper) under a window: ribbed sections."""
    n = int((x1 - x0) / 0.1)
    for k in range(n):
        box(x0 + k * 0.1, x0 + k * 0.1 + 0.07, y, y + 0.12, 0.15, 0.72, "Radiator")


def wall_unit(box, x_back, y_from, y_to):
    """Soviet Schrankwand (catalogue type, 1970s-80s): 4 bays, plinth, glass display band, door joints, handles."""
    depth, h = 0.45, 2.2
    xf = x_back + depth
    box(x_back, xf - 0.02, y_from, y_to, 0.08, h, "Furniture")                    # carcass
    box(x_back + 0.03, xf - 0.05, y_from + 0.02, y_to - 0.02, 0.0, 0.08, "BlackPlastic")  # recessed plinth
    bays = 4
    bw = (y_to - y_from) / bays
    for k in range(bays):
        y0, y1 = y_from + k * bw + 0.006, y_from + (k + 1) * bw - 0.006
        # lower doors, glass display band, upper doors (fronts sit 2 cm proud; the joints read as gaps)
        box(xf - 0.02, xf, y0, y1, 0.1, 1.05, "Furniture")
        box(xf - 0.02, xf - 0.01, y0 + 0.03, y1 - 0.03, 1.1, 1.65, "Glass")
        box(xf - 0.02, xf, y0, y1, 1.7, h - 0.02, "Furniture")
        hy = y1 - 0.06 if k % 2 == 0 else y0 + 0.04                               # handles towards the joint
        box(xf, xf + 0.025, hy, hy + 0.02, 0.62, 0.78, "Metal")
        box(xf, xf + 0.025, hy, hy + 0.02, 1.82, 1.98, "Metal")


def shop(part, AX, ST, T, seed):
    """Ground-floor grocery (магазин, briefing V10 B): one open sales room over five axes, same section frame as
    section(): x along the facade (the entrance axis is 0..AX), y inward. Layout and fittings are ANNAHME."""
    rnd = random.Random(seed)
    ceil = ST - 0.22
    depth = 2 * AX
    y0, y1 = T, depth - 0.08
    S = Section(part, ceil, rnd)
    xa, xb = -2 * AX, 3 * AX
    for x in (xa, xb):
        S.wall_x(x, y0, y1, "Paint_OilBlue", "Lime")
    S.wall_y(depth, xa - 0.08, xb + 0.08, "Paint_OilBlue", "Lime", doors=[(xb - 1.6, xb - 0.7)])   # door to the store room
    S.box(xa + 0.08, xb - 0.08, y0, y1, 0.0, 0.012, "Linoleum")
    # L-shaped counter: long run parallel to the back wall, return towards the facade
    cy0, cy1 = y1 - 2.2, y1 - 1.5
    S.box(xa + 1.0, xb - 2.0, cy0, cy1, 0.0, 0.95, "Furniture")
    S.box(xa + 1.0, xb - 2.0, cy0 - 0.05, cy1 + 0.05, 0.95, 1.0, "Enamel")                   # counter top
    S.box(xb - 2.7, xb - 2.0, y0 + 1.6, cy0, 0.0, 0.95, "Furniture")
    S.box(xa + 2.0, xa + 2.5, cy0 + 0.1, cy0 + 0.5, 1.0, 1.15, "Metal")                      # scale
    S.box(xa + 2.1, xa + 2.4, cy0 + 0.2, cy0 + 0.4, 1.15, 1.5, "Enamel")
    S.box(xb - 3.4, xb - 2.9, cy0 + 0.1, cy0 + 0.5, 1.0, 1.25, "BlackPlastic")               # cash register
    # wall shelving behind the counter and along the party walls, with jars and tins
    for (sx0, sx1, sy0, sy1) in ((xa + 0.1, xb - 0.1, y1 - 0.45, y1 - 0.08), (xa + 0.1, xa + 0.45, y0 + 0.4, cy0 - 0.3)):
        S.box(sx0, sx1, sy0, sy1, 0.0, 0.08, "Furniture")
        for k in range(5):
            z = 0.45 + k * 0.42
            S.box(sx0, sx1, sy0, sy1, z, z + 0.03, "Furniture")
            for _ in range(int((sx1 - sx0 + sy1 - sy0) * 2.5)):
                if rnd.random() < 0.55:
                    continue  # mostly emptied
                px = rnd.uniform(sx0 + 0.05, sx1 - 0.12)
                py = rnd.uniform(sy0 + 0.02, sy1 - 0.12)
                h = rnd.uniform(0.1, 0.25)
                S.box(px, px + 0.08, py, py + 0.08, z + 0.03, z + 0.03 + h, rnd.choice(("Glass", "Metal", "Paper")))
    # a toppled shelf unit lying in the room, posters, fallen ceiling plaster
    S.box(xa + 4.5, xa + 6.6, y0 + 1.2, y0 + 1.6, 0.0, 0.35, "Furniture")
    for k in range(3):
        S.box(xa + 0.09 + 0.0, xa + 0.1, y0 + 0.8 + k * 0.9, y0 + 1.4 + k * 0.9, 1.4, 2.1, "Paper")  # faded posters
    S.debris(xa + 0.3, xb - 0.3, y0 + 0.3, cy0 - 0.2, 120)
