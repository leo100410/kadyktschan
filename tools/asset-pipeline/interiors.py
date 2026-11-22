"""Ground-floor stair section with two furnished flats (briefing V5, PDF phase 3 "zwei Wohnungen").

Used by build_buildings.py. Everything is built in section space: x along the facade (walking
direction of the entrance edge, the stairwell occupies x 0..AX), y inward from the outer facade
face, z from the ground-floor level. Layout and furniture are ANNAHME: the type-series floor plans
are not documented (dossier question 2); props follow the V5 list and 1970s-80s catalogue shapes.

2026-11-08 rework (user: "in den Wohnungen ist es kaum möglich sich zu bewegen", "in einer Wohnung steht einfach
eine Treppe im Raum"): the section runs through the whole block (4 axes deep, front to back facade), so each flat
has twice the floor area, and the stairwell is a real one: vestibule, flat doors left and right, a flight up to a
half landing at the back and a broken return flight to the first floor (the shaft above it is open).

Flat A lies at x -2AX..0, flat B mirrored at x AX..3AX. Plan of flat A (metres, see FLAT): living room across the
front (both front windows), a hall band in the middle with bath and WC, bedroom and kitchen at the back facade.
Interior walls meet the facades only at x = -AX, between two windows.
"""
import random

import furniture as fu

WALL = 0.16          # interior wall thickness
PANEL = 1.5          # oil-paint panel height (art bible 4.3)
DEEP = 4             # axes from the front to the back facade in the furnished sections
# edge rounding per material (metres; capped at 40 % of the thinnest side): upholstery puffy, wood and enamel soft
BEVEL = {"Sofa": 0.045, "Carpet": 0.012, "Furniture": 0.012, "Wood": 0.01, "Enamel": 0.025, "Radiator": 0.012,
         "BlackPlastic": 0.008, "Metal": 0.004, "Mural_Red": 0.008, "CurtainRed": 0.02, "Paper": 0.04}  # Paper: pillows

# flat A plan (x along the facade, y inward); the back facade's inner face is at depth - T
FRONT, BATH_SPLIT, BACK = 4.4, 6.0, 7.4      # living room | hall band (bath, WC) | bedroom + kitchen
DOOR_FLAT = (4.6, 5.5)                        # flat doors in the stairwell walls
DOOR_LIVING = (-2.2, -1.3)                    # hall -> living room (wall y = FRONT)
DOOR_BATH, DOOR_WC = (4.56, 5.5), (6.15, 7.25)  # hall -> bath / WC (wall x = -4); 0.8 m was too tight (walk check)
DOOR_BED, DOOR_KITCHEN = (-3.9, -3.1), (-1.6, -0.7)   # hall -> bedroom / kitchen (wall y = BACK)
STAIR_FOOT = 6.6                              # first step of the flight up (stairwell, along x 0.15..1.4)


def section(part, AX, ST, T, seed):
    rnd = random.Random(seed)
    S = Section(part, ST - 0.22, rnd)
    y0, y1 = T, DEEP * AX - T
    stairwell(S, AX, ST, y0, y1)
    furnish_generic(flat_shell(S, AX, y0, y1, False, "Wallpaper_Rose", "Wallpaper_Green"), "family")
    furnish_generic(flat_shell(S, AX, y0, y1, True, "Wallpaper_Green", "Wallpaper_Rose"), "widow")


class Section:
    def __init__(self, part, ceil, rnd):
        self.p, self.ceil, self.rnd = part, ceil, rnd
        self.clues = {}
        self.lights = []

    def box(self, x0, x1, y0, y1, z0, z1, mat):
        """Furniture materials get rounded (chamfered) edges, upholstery the softest; walls, floors and papers stay
        sharp (user 2026-11-08: "viel zu eckig")."""
        b = BEVEL.get(mat, 0.0)
        if b and hasattr(self.p, "bevel_box"):
            self.p.bevel_box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1, mat, b)
        else:
            self.p.box(min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), z0, z1, mat)

    def cyl(self, cx, cy, z0, z1, r, mat, r1=None):
        fu.cyl(self, cx, cy, z0, z1, r, mat, r1)

    def hcyl(self, axis, a0, a1, c, z, r, mat):
        fu.hcyl(self, axis, a0, a1, c, z, r, mat)

    def chunk(self, x, y, z, sx, sy, sz, mat, tilt=0.3):
        fu.chunk(self, x, y, z, sx, sy, sz, mat, tilt)

    def clue(self, name, x, y, z):
        """Where an interactive find lies (section space); build_buildings.py writes it to the manifest in world
        metres and tools/research/story_data.py puts it into Story.json."""
        self.clues[name] = (x, y, z)

    def _wall(self, a0, a1, c0, c1, lower, upper, doors, along_x, other=None):
        """Wall from a0..a1 along one axis, thickness c0..c1 on the other; doors = [(a_from, a_to)]; other = (lower,
        upper) for the far face (c1 side) when the two rooms are finished differently."""
        cuts = sorted(doors or [])
        spans, a = [], a0
        for d0, d1 in cuts:
            spans.append((a, d0)); a = d1
        spans.append((a, a1))
        layers = [(c0, c1, lower, upper)] if not other else [(c0, (c0 + c1) / 2, lower, upper), ((c0 + c1) / 2, c1) + tuple(other)]
        for s0, s1 in spans:
            if s1 - s0 < 0.01:
                continue
            for k0, k1, lo, up in layers:
                for z0, z1, m in ((0.0, PANEL, lo), (PANEL, self.ceil, up)):
                    if along_x:
                        self.box(s0, s1, k0, k1, z0, z1, m)
                    else:
                        self.box(k0, k1, s0, s1, z0, z1, m)
        for d0, d1 in cuts:  # lintel above each door (doors 2.05 m)
            if along_x:
                self.box(d0, d1, c0, c1, 2.05, self.ceil, upper)
            else:
                self.box(c0, c1, d0, d1, 2.05, self.ceil, upper)

    def wall_x(self, x, y0, y1, lower, upper, doors=None, other=None):
        """Wall in the plane x; 'lower, upper' face -x, 'other' (optional) faces +x."""
        self._wall(y0, y1, x - WALL / 2, x + WALL / 2, lower, upper, doors, along_x=False, other=other)

    def wall_y(self, y, x0, x1, lower, upper, doors=None, other=None):
        """Wall in the plane y; 'lower, upper' face -y, 'other' (optional) faces +y."""
        self._wall(min(x0, x1), max(x0, x1), y - WALL / 2, y + WALL / 2, lower, upper, doors, along_x=True, other=other)

    def debris(self, x0, x1, y0, y1, n):
        """Fallen plaster flakes (art bible 6: eingefallene Decken) and a few broken chunks."""
        for k in range(n):
            x, y = self.rnd.uniform(x0, x1), self.rnd.uniform(y0, y1)
            if k % 6 == 0:
                self.chunk(x, y, 0.0, self.rnd.uniform(0.08, 0.25), self.rnd.uniform(0.06, 0.2), self.rnd.uniform(0.03, 0.09), "Lime")
            else:
                w, d = self.rnd.uniform(0.05, 0.3), self.rnd.uniform(0.05, 0.25)
                self.box(x, x + w, y, y + d, 0.0, self.rnd.uniform(0.008, 0.025), "Lime")


class FlatView:
    """Section seen through a mirror for flat B (x -> AX - x); boxes and round parts stay exact under the mirror."""

    def __init__(self, S, AX, mirror):
        self.S, self.p, self.rnd, self.ceil, self.mirror = S, S.p, S.rnd, S.ceil, mirror
        self.X = (lambda x: x) if not mirror else (lambda x: AX - x)

    def box(self, x0, x1, y0, y1, z0, z1, mat):
        self.S.box(self.X(x0), self.X(x1), y0, y1, z0, z1, mat)

    def cyl(self, cx, cy, z0, z1, r, mat, r1=None):
        self.S.cyl(self.X(cx), cy, z0, z1, r, mat, r1)

    def hcyl(self, axis, a0, a1, c, z, r, mat):
        if axis == "x":
            a0, a1 = sorted((self.X(a0), self.X(a1)))
        else:
            c = self.X(c)
        self.S.hcyl(axis, a0, a1, c, z, r, mat)

    def chunk(self, x, y, z, sx, sy, sz, mat, tilt=0.3):
        self.S.chunk(self.X(x), y, z, sx, sy, sz, mat, tilt)

    def clue(self, name, x, y, z):
        self.S.clue(name, self.X(x), y, z)

    def wall_x(self, x, y0, y1, lower, upper, doors=None, other=None):
        if self.mirror and other:  # the faces swap sides under the mirror
            (lower, upper), other = other, (lower, upper)
        self.S.wall_x(self.X(x), y0, y1, lower, upper, doors, other)

    def wall_y(self, y, x0, x1, lower, upper, doors=None, other=None):
        a, b = sorted((self.X(x0), self.X(x1)))
        self.S.wall_y(y, a, b, lower, upper, [tuple(sorted((self.X(d0), self.X(d1)))) for d0, d1 in (doors or [])], other)

    def debris(self, x0, x1, y0, y1, n):
        a, b = sorted((self.X(x0), self.X(x1)))
        self.S.debris(a, b, y0, y1, n)

    def place(self, x, y, rot=0):
        return fu.Place(self, x, y, rot)


def stairwell(S, AX, ST, y0, y1, connects_up=True, has_lower=False):
    """Two full flights with a half landing; the last furnished floor ends in a visible locked barrier."""
    H, steps, go = ST/2, 9, 0.28
    rise, top = H/steps, STAIR_FOOT+steps*go
    S.box(0.08, AX-0.08, y0, STAIR_FOOT if has_lower else y1, 0, 0.01, "Concrete")
    for x, other in ((0.0, ("Paint_Mint", "Lime")), (AX, None)):
        S.wall_x(x,y0,y1,"Paint_Mint","Lime",doors=[DOOR_FLAT],other=other)
    for k in range(5):
        y=1.0+k*.34
        S.box(AX-.3,AX-.1,y,y+.3,1.2,1.55,"Metal")
        S.box(AX-.31,AX-.3,y+.05,y+.25,1.43,1.46,"BlackPlastic")
    if connects_up:
        # 1.32 m flights and a 2.84 m landing allow the player capsule to turn.
        for k in range(steps):
            S.box(.08,1.4,STAIR_FOOT+k*go,STAIR_FOOT+(k+1)*go,max(-.04,rise*(k+1)-.2),rise*(k+1),"Concrete")
            ya,yb=top-(k+1)*go,top-k*go
            z=H+rise*(k+1)
            S.box(1.6,AX-.08,ya,yb,z-.2,z,"Concrete")
            for x in (1.43,1.57):
                y=STAIR_FOOT+(k+.5)*go
                level=rise*(k+1) if x<1.5 else ST-rise*k
                S.box(x-.015,x+.015,y-.015,y+.015,level,level+.88,"Metal")
        S.box(.08,AX-.08,top,y1,H-.22,H,"Concrete")
        S.box(0,AX,6,STAIR_FOOT,ST-.22,ST,"Concrete")
        # Sloping rails follow the steps instead of a floating horizontal bar.
        for x,reverse in ((1.43,False),(1.57,True)):
            for k in range(steps-1):
                y=STAIR_FOOT+(k+.5)*go
                z=(ST-rise*k if reverse else rise*(k+1))+.88
                z2=z+(-rise if reverse else rise)
                verts=[(x-.025,y,z-.025),(x+.025,y,z-.025),(x+.025,y,z+.025),(x-.025,y,z+.025),
                       (x-.025,y+go,z2-.025),(x+.025,y+go,z2-.025),(x+.025,y+go,z2+.025),(x-.025,y+go,z2+.025)]
                fu.surface(fu.Place(S,0,0),verts,[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)],"Wood")
    else:
        # No stair beyond this floor: full-height closed partition with weathered horizontal planks.
        S.box(.08,1.48,6.35,6.5,0,S.ceil,"WoodGrey")
        S.box(1.45,1.55,6.35,9.12,0,1.15,"WoodGrey")
        for k in range(8):
            S.box(.12,1.44,6.29,6.34,.15+k*.29,.32+k*.29,"Wood")
        for x in (.35,1.25): S.box(x,x+.05,6.25,6.29,0,S.ceil,"Metal")
    fu.ceiling_lamp(S,1.5,2.5,ST-.22)


def flat_shell(S, AX, y0, y1, mirror, wp_living, wp_bed, floor_living="FloorBoards", floor_bed="FloorBoards"):
    """Floors, walls and doors of one flat (plan in the module doc); returns the FlatView to furnish it with."""
    F = FlatView(S, AX, mirror)
    xa = -2 * AX
    F.box(xa + 0.08, -0.08, y0, FRONT, 0.0, 0.012, floor_living)
    F.box(-4.0, -0.08, FRONT, BACK, 0.0, 0.012, "Linoleum")                   # hall
    F.box(xa + 0.08, -4.0, FRONT, BACK, 0.0, 0.012, "Linoleum")               # bath and WC
    F.box(xa + 0.08, -AX, BACK, y1, 0.0, 0.012, floor_bed)
    F.box(-AX, -0.08, BACK, y1, 0.0, 0.012, "Linoleum")                       # kitchen
    F.wall_x(xa, y0, y1, "Lime", "Lime")                                       # party wall to the next section
    hall = ("Paint_OilBlue", "Wallpaper_Green")
    F.wall_y(FRONT, xa, 0.0, wp_living, wp_living, doors=[DOOR_LIVING], other=hall)
    F.wall_x(-4.0, FRONT, BACK, "Paint_OilBlue", "Lime", doors=[DOOR_BATH, DOOR_WC], other=hall)
    F.wall_y(BATH_SPLIT, xa, -4.0, "Paint_OilBlue", "Lime")
    F.wall_y(BACK, xa, 0.0, "Paint_OilBlue", "Wallpaper_Green", doors=[DOOR_BED, DOOR_KITCHEN], other=(wp_bed, wp_bed))
    F.wall_x(-AX, BACK, y1, wp_bed, wp_bed, other=("Paint_Mint", "Lime"))
    F.y0, F.y1, F.AX = y0, y1, AX
    for x, y in ((-3.0, 2.3), (-2.0, 5.9), (-4.5, 9.5), (-1.5, 9.5)):
        fu.ceiling_lamp(F, x, y, F.ceil)
    return F


def furnish_generic(F, life):
    """A lived-in flat left behind: 'family' kept its furniture, 'widow' was looted (doors off, drawers out)."""
    y0, y1 = F.y0, F.y1
    looted = life != "family"
    # living room: wall unit on the party wall, sofa under the wall carpet, table, TV in the corner, rug, curtains
    wall_unit(F.box, -6.0 + 0.08, y0 + 0.5, y0 + 3.3)
    fu.sofa(F.place(-2.4, FRONT - 0.08, 2), 2.0, slumped=looted)         # back on the hall wall, clear of the door
    F.box(-4.4, -2.4, FRONT - 0.1, FRONT - 0.09, 0.9, 2.2, "Carpet")                 # carpet on the wall above it
    if not looted:
        fu.table(F.place(-3.6, 1.6), 1.1, 0.8)
        fu.tv(F.place(-0.2, 0.9, 1))
    else:
        F.chunk(-3.0, 1.9, 0.0, 1.0, 0.7, 0.12, "Furniture", tilt=0.6)               # table top kicked over
        F.box(-0.9, -0.3, 1.0, 1.5, 0.0, 0.05, "Glass")                               # smashed screen glass
    fu.rug(F, -4.2, -1.6, 1.0, 3.6)
    for wx in (-5.2, -2.2):
        radiator(F.box, wx, wx + 1.4, y0 + 0.05)
        fu.curtains(F, wx, wx + 1.4, y0, 1, drawn=0.25 if not looted else 0.12)
    # bedroom: bed with its head on the party wall, wardrobe by the door, nightstand
    fu.bed(F.place(-6.0 + 0.08, 10.8, 3), 1.4, 2.0, made=not looted)
    fu.nightstand(F.place(-6.0 + 0.08, 11.5, 3), drawer_out=looted)
    fu.wardrobe(F.place(-6.0 + 0.1, BACK + 0.08, 0), 1.2, open_leaf=looted)
    radiator(F.box, -5.2, -3.8, y1 - 0.17)
    # kitchen: units along the stairwell wall, stove, fridge, table at the window
    fu.fridge(F.place(-0.08, BACK + 0.15, 1), open_door=looted)
    fu.stove(F.place(-0.08, BACK + 0.85, 1), kettle=not looted)
    fu.kitchen_run(F.place(-0.08, BACK + 1.4, 1), 1.8, sink_at=1.2)
    fu.table(F.place(-2.6, 10.2), 0.9, 0.7)
    radiator(F.box, -2.2, -0.8, y1 - 0.17)
    # hall: coat rack between the bedroom and kitchen doors, shoe shelf, telephone
    F.box(-2.9, -1.8, BACK - 0.12, BACK - 0.08, 1.65, 1.7, "Wood")
    F.box(-2.8, -1.9, BACK - 0.4, BACK - 0.08, 0.0, 0.35, "Furniture")
    # bath and WC
    fu.bathtub(F.place(-6.0 + 0.08, BATH_SPLIT - 0.1, 3), 1.4)
    fu.washbasin(F.place(-4.6, BATH_SPLIT - 0.08, 2))
    fu.toilet(F.place(-6.0 + 0.08, 6.5, 3))
    F.debris(-5.8, -0.2, y0 + 0.2, y1 - 0.2, 40 if not looted else 90)


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
