"""Furniture pieces for the furnished flats (user 2026-11-08: "die Einrichtung ist viel zu einfach"): legs, doors,
handles, cushions and folds instead of single boxes. 1970s-80s Soviet catalogue shapes, ANNAHME.

Every piece is built in a local frame and placed with Place(S, x, y, rot): u runs along the wall it stands against,
v away from that wall into the room (the piece's back is at v = 0), z up from the floor. rot turns the frame in
90 degree steps: 0 = back on a wall at lower y (facing +y), 1 = back on a wall at higher x (facing -x),
2 = back on a wall at higher y (facing -y), 3 = back on a wall at lower x (facing +x).
"""
import math

N = 14  # cylinder segments


def ring_solid(S, ring0, ring1, mat):
    """Closed prism between two rings ordered counter-clockwise as seen from the ring1 end."""
    p = S.p
    if mat not in p.mats:
        p.mats.append(mat)
    m, b, n = p.mats.index(mat), len(p.verts), len(ring0)
    p.verts += ring0 + ring1
    for i in range(n):
        j = (i + 1) % n
        p.faces.append((b + i, b + j, b + n + j, b + n + i)); p.face_mat.append(m)
    p.faces.append(tuple(b + n + i for i in range(n))); p.face_mat.append(m)
    p.faces.append(tuple(b + i for i in reversed(range(n)))); p.face_mat.append(m)


def cyl(S, cx, cy, z0, z1, r, mat, r1=None):
    """Upright cylinder (or cone with top radius r1)."""
    r1 = r if r1 is None else r1
    ang = [2 * math.pi * k / N for k in range(N)]
    ring_solid(S, [(cx + r * math.cos(a), cy + r * math.sin(a), z0) for a in ang],
               [(cx + r1 * math.cos(a), cy + r1 * math.sin(a), z1) for a in ang], mat)


def hcyl(S, axis, a0, a1, c, z, r, mat):
    """Lying cylinder from a0 to a1 along 'x' or 'y'; c is the other horizontal coordinate, z the centre height."""
    ang = [2 * math.pi * k / N for k in range(N)]
    if axis == "x":
        ring = lambda a: [(a, c + r * math.cos(t), z + r * math.sin(t)) for t in ang]
    else:
        ring = lambda a: [(c - r * math.cos(t), a, z + r * math.sin(t)) for t in ang]
    ring_solid(S, ring(a0), ring(a1), mat)


def chunk(S, x, y, z, sx, sy, sz, mat, tilt=0.3):
    """Irregular broken piece (plaster, concrete, brick) instead of a clean cube: every corner pushed in or out, the
    top tipped, the whole piece turned (user 2026-11-08: "nicht einfach nur alles viereckig")."""
    r = S.rnd
    a = r.uniform(0, math.pi)
    ca, sa = math.cos(a), math.sin(a)
    def corner(u, v, w):
        u, v = u * sx * r.uniform(0.7, 1.15), v * sy * r.uniform(0.7, 1.15)
        return (x + u * ca - v * sa, y + u * sa + v * ca, z + w)
    tip = r.uniform(-tilt, tilt) * sz
    bottom = [corner(u, v, 0.0) for u, v in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))]
    top = []
    for k, (u, v) in enumerate(((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))):
        h = sz * r.uniform(0.55, 1.0) + (tip if k < 2 else -tip)
        top.append(corner(u * r.uniform(0.6, 0.95), v * r.uniform(0.6, 0.95), max(0.02, h)))
    ring_solid(S, bottom, top, mat)


class Place:
    """Local frame for one piece (see module doc)."""

    def __init__(self, S, x, y, rot=0):
        self.S, self.x, self.y, self.rot = S, x, y, rot % 4

    def xy(self, u, v):
        return {0: (self.x + u, self.y + v), 1: (self.x - v, self.y + u),
                2: (self.x - u, self.y - v), 3: (self.x + v, self.y - u)}[self.rot]

    def box(self, u0, u1, v0, v1, z0, z1, mat):
        (xa, ya), (xb, yb) = self.xy(u0, v0), self.xy(u1, v1)
        self.S.box(min(xa, xb), max(xa, xb), min(ya, yb), max(ya, yb), z0, z1, mat)

    def cyl(self, u, v, z0, z1, r, mat, r1=None):
        self.S.cyl(*self.xy(u, v), z0, z1, r, mat, r1)

    def hcyl_u(self, u0, u1, v, z, r, mat):
        """Lying cylinder along the piece's u axis."""
        (xa, ya), (xb, yb) = self.xy(u0, v), self.xy(u1, v)
        if abs(xa - xb) > abs(ya - yb):
            self.S.hcyl("x", min(xa, xb), max(xa, xb), ya, z, r, mat)
        else:
            self.S.hcyl("y", min(ya, yb), max(ya, yb), xa, z, r, mat)


def surface(P, verts, faces, mat):
    """Append a curved furniture surface, including flat B's reflection and outward winding."""
    S, p = P.S, P.S.p
    if mat not in p.mats:
        p.mats.append(mat)
    base, first = len(p.verts), len(p.faces)
    for u, v, z in verts:
        x, y = P.xy(u, v)
        p.verts.append((S.X(x) if getattr(S, "mirror", False) else x, y, z))
    mirror = getattr(S, "mirror", False)
    p.faces.extend(tuple(base + i for i in (f[::-1] if mirror else f)) for f in faces)
    p.face_mat.extend([p.mats.index(mat)] * len(faces))
    p.smooth_faces.update(range(first, len(p.faces)))


def cushion(P, u0, u1, v0, v1, z0, z1, mat="Sofa"):
    """Closed, softly crowned cushion; stays inside its old box so passages keep their width."""
    assert u1 > u0 and v1 > v0 and z1 > z0
    cx, cy, cz = (u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2
    rx, ry, rz = (u1 - u0) / 2, (v1 - v0) / 2, (z1 - z0) / 2
    verts, faces = [(cx, cy, z0)], []
    n, rows = 24, 9
    signed = lambda x: math.copysign(abs(x) ** 0.35, x)
    for j in range(1, rows):
        lat = -math.pi / 2 + math.pi * j / rows
        for i in range(n):
            a = 2 * math.pi * i / n
            r = math.cos(lat) ** 0.35
            verts.append((cx + rx * r * signed(math.cos(a)), cy + ry * r * signed(math.sin(a)),
                          cz + rz * math.copysign(abs(math.sin(lat)) ** 0.7, lat)))
    top = len(verts)
    verts.append((cx, cy, z1))
    for i in range(n):
        k = (i + 1) % n
        faces.append((0, 1 + k, 1 + i))
        for j in range(rows - 2):
            a, b = 1 + j * n, 1 + (j + 1) * n
            faces.append((a + i, a + k, b + k, b + i))
        a = 1 + (rows - 2) * n
        faces.append((a + i, a + k, top))
    surface(P, verts, faces, mat)


def blanket(P, u0, u1, v0, v1, z, drop=0.16):
    """Thin closed cloth with folds and a draped front hem, rather than a slab on the mattress."""
    nx, ny = 16, 12
    verts, faces = [], []
    for j in range(ny + 1):
        t = j / ny
        for i in range(nx + 1):
            s = i / nx
            fold = 0.014 * (0.5 + 0.5 * math.sin(s * 8 * math.pi + t * 2)) * math.sin(math.pi * t)
            height = z + fold - drop * max(0, (t - 0.82) / 0.18) ** 1.5
            verts.append((u0 + (u1 - u0) * s, v0 + (v1 - v0) * min(t / 0.82, 1.0), height))
    count = len(verts)
    verts += [(x, y, h - 0.006) for x, y, h in verts]
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            f = (a, a + 1, a + nx + 2, a + nx + 1)
            faces += [f, tuple(k + count for k in reversed(f))]
    rim = list(range(nx + 1)) + [j * (nx + 1) + nx for j in range(1, ny + 1)]
    rim += list(range(ny * (nx + 1) + nx - 1, ny * (nx + 1) - 1, -1))
    rim += [j * (nx + 1) for j in range(ny - 1, 0, -1)]
    for a, b in zip(rim, rim[1:] + rim[:1]):
        faces.append((a + count, b + count, b, a))
    surface(P, verts, faces, "Carpet")


def legs(P, u0, u1, v0, v1, h, mat, t=0.04):
    for u in (u0, u1 - t):
        for v in (v0, v1 - t):
            P.box(u, u + t, v, v + t, 0.0, h, mat)


def sofa(P, w=2.0, mat="Sofa", cushions=3, slumped=False):
    """Sofa-bed (диван-книжка): wooden legs, seat, back, two arms, loose cushions; slumped = sagging and torn."""
    legs(P, 0.08, w - 0.08, 0.08, 0.82, 0.12, "Wood", 0.05)
    P.box(0.02, w - 0.02, 0.05, 0.88, 0.12, 0.32, mat)
    P.box(0.08, w - 0.08, 0.87, 0.89, 0.15, 0.21, "Furniture")
    for u in (0.0, w - 0.13):
        cushion(P, u, u + 0.13, 0.0, 0.9, 0.22, 0.61, mat)
        P.box(u, u + 0.13, 0.06, 0.83, 0.6, 0.63, "Furniture")
    cw = (w - 0.26) / cushions
    for k in range(cushions):
        dz = -0.05 * (k == 1) if slumped else 0.0
        a, b = 0.14 + k * cw, 0.12 + (k + 1) * cw
        cushion(P, a, b, 0.19, 0.88, 0.31 + dz, 0.53 + dz, mat)
        cushion(P, a, b, 0.0, 0.23, 0.43 + dz, 0.88 + dz, mat)


def armchair(P, mat="Sofa"):
    legs(P, 0.06, 0.74, 0.06, 0.78, 0.15, "Wood", 0.04)
    P.box(0.0, 0.8, 0.05, 0.85, 0.15, 0.32, "Furniture")
    cushion(P, 0.1, 0.7, 0.0, 0.2, 0.36, 0.95, mat)
    for u in (0.0, 0.68):
        cushion(P, u, u + 0.12, 0.0, 0.85, 0.24, 0.62, mat)
        P.box(u, u + 0.12, 0.05, 0.78, 0.61, 0.64, "Furniture")
    cushion(P, 0.12, 0.68, 0.18, 0.82, 0.32, 0.52, mat)


def table(P, w, d, h=0.74, top="Furniture", leg="Furniture"):
    """Table with apron and four legs; u0 = 0, v0 = 0 is a corner (place it free in the room with rot 0)."""
    P.box(0.0, w, 0.0, d, h - 0.035, h, top)
    for v in (0.06, d - 0.085):
        P.box(0.06, w - 0.06, v, v + 0.025, h - 0.12, h - 0.035, leg)
    for u in (0.06, w - 0.085):
        P.box(u, u + 0.025, 0.06, d - 0.06, h - 0.12, h - 0.035, leg)
    for u in (0.085, w - 0.085):
        for v in (0.085, d - 0.085):
            P.cyl(u, v, 0.0, h - 0.035, 0.016, leg, r1=0.025)


def chair(P, mat="Furniture"):
    """Kitchen chair with tapered legs, open back and bowed plywood rail, inside a 40 cm square."""
    for u in (0.045, 0.355):
        for v in (0.045, 0.355):
            P.cyl(u, v, 0.0, 0.43, 0.013, mat, r1=0.02)
        P.cyl(u, 0.025, 0.43, 0.92, 0.016, mat, r1=0.013)
    cushion(P, 0.0, 0.4, 0.0, 0.4, 0.42, 0.46, mat)
    verts, faces = [], []
    for i in range(13):
        u = i / 12
        v = 0.012 + 0.035 * math.sin(u * math.pi)
        verts.extend([(u * 0.4, v, 0.7), (u * 0.4, v + 0.018, 0.7),
                      (u * 0.4, v + 0.018, 0.92), (u * 0.4, v, 0.92)])
        if i:
            a, b = (i - 1) * 4, i * 4
            faces.extend([(a + j, a + (j + 1) % 4, b + (j + 1) % 4, b + j) for j in range(4)])
    faces += [(3, 2, 1, 0), (48, 49, 50, 51)]
    surface(P, verts, faces, mat)


def wardrobe(P, w=1.2, h=2.0, d=0.58, open_leaf=False, mat="Furniture"):
    """Two-door wardrobe: plinth, carcass, doors with a joint, handles, cornice; open_leaf swings the right door."""
    P.box(0.03, w - 0.03, 0.03, d - 0.05, 0.0, 0.08, "BlackPlastic")         # recessed plinth
    P.box(0.0, w, 0.0, d - 0.03, 0.08, h, mat)                                # carcass
    P.box(-0.02, w + 0.02, -0.02, d + 0.01, h, h + 0.05, mat)                 # cornice
    half = w / 2
    P.box(0.004, half - 0.004, d - 0.03, d, 0.1, h - 0.02, mat)              # left door
    if open_leaf:
        P.box(w - 0.02, w, d, d + half - 0.01, 0.1, h - 0.02, mat)           # right door swung open
        P.box(0.03, w - 0.03, 0.05, d - 0.06, 0.1, h - 0.05, "BlackPlastic")  # dark inside
    else:
        P.box(half + 0.004, w - 0.004, d - 0.03, d, 0.1, h - 0.02, mat)
    hz = min(1.05, h * 0.5)                                                    # handles at hand height, inside low units
    for u in (half - 0.06, half + 0.04):
        if open_leaf and u > half:
            continue
        P.box(u, u + 0.02, d, d + 0.02, hz - 0.08, hz + 0.08, "Metal")


def bookshelf(P, w=0.9, h=1.8, d=0.32, fill=0.8, mat="Furniture"):
    P.box(0.0, w, 0.0, 0.02, 0.0, h, mat)                                      # back
    for u in (0.0, w - 0.02):
        P.box(u, u + 0.02, 0.0, d, 0.0, h, mat)                                # sides; the front stays open
    S = P.S
    for k in range(5):
        z = 0.06 + k * (h - 0.08) / 5
        P.box(0.0, w, 0.0, d + 0.005, z, z + 0.02, mat)                        # shelf boards
        u = 0.03
        while u < w - 0.06:
            bw = S.rnd.uniform(0.02, 0.05)
            if S.rnd.random() < fill:
                bh = S.rnd.uniform(0.17, 0.26)
                P.box(u, u + bw, 0.04, d - 0.03, z + 0.02, z + 0.02 + bh, S.rnd.choice(("Paper", "Mural_Red", "Furniture", "Sofa")))
            u += bw + 0.004
    P.box(0.0, w, 0.0, d + 0.01, h - 0.02, h, mat)


def bed(P, w=1.4, l=2.0, made=True, frame="Furniture", second_pillow=True, pillows=True):
    """Bed with its head against the wall: frame on legs, head and foot boards, mattress, pillows, blanket."""
    legs(P, 0.02, w - 0.02, 0.05, l - 0.02, 0.3, frame, 0.05)
    P.box(0.0, w, 0.0, l, 0.24, 0.32, frame)                                   # side rails
    P.box(0.0, w, 0.0, 0.05, 0.0, 1.0, frame)                                  # head board
    P.box(0.0, w, l - 0.05, l, 0.0, 0.62, frame)                               # foot board
    cushion(P, 0.03, w - 0.03, 0.05, l - 0.05, 0.32, 0.48)
    for u in ((0.08, w / 2 + 0.02) if (w > 1.0 and second_pillow) else (0.08,)) if pillows else ():
        cushion(P, u, u + min(0.6, w - 0.16), 0.1, 0.48, 0.46, 0.6, "Paper")
    if made:
        blanket(P, -0.02, w + 0.02, 0.55, l - 0.05, 0.49)
    else:
        blanket(P, 0.05, w - 0.05, l - 0.7, l - 0.08, 0.49, drop=0.04)


def nightstand(P, drawer_out=False):
    P.box(0.0, 0.45, 0.0, 0.4, 0.06, 0.55, "Furniture")
    legs(P, 0.02, 0.43, 0.02, 0.38, 0.06, "Furniture", 0.03)
    if drawer_out:
        P.box(0.04, 0.41, 0.4, 0.62, 0.36, 0.5, "Furniture")
    else:
        P.box(0.04, 0.41, 0.4, 0.41, 0.36, 0.5, "Furniture")
    P.box(0.19, 0.26, 0.41, 0.43 + (0.22 if drawer_out else 0.0), 0.42, 0.44, "Metal")


def lamp(P, u, v, z):
    """Table lamp: foot, stem, fabric shade."""
    P.cyl(u, v, z, z + 0.02, 0.07, "BlackPlastic")
    P.cyl(u, v, z + 0.02, z + 0.3, 0.012, "Metal")
    P.cyl(u, v, z + 0.25, z + 0.43, 0.15, "CurtainRed", r1=0.09)


def sewing_machine(P, z=0.75):
    """Treadle machine head: open sewing throat, needle, spool and a side handwheel."""
    P.box(0.0, 0.5, 0.0, 0.35, z, z + 0.025, "BlackPlastic")
    cushion(P, 0.34, 0.46, 0.08, 0.27, z + 0.02, z + 0.26, "BlackPlastic")
    cushion(P, 0.035, 0.44, 0.08, 0.23, z + 0.19, z + 0.28, "BlackPlastic")
    cushion(P, 0.025, 0.115, 0.08, 0.23, z + 0.09, z + 0.26, "BlackPlastic")
    P.hcyl_u(0.44, 0.48, 0.175, z + 0.17, 0.11, "Metal")
    P.hcyl_u(0.481, 0.485, 0.175, z + 0.17, 0.075, "BlackPlastic")
    P.cyl(0.07, 0.16, z + 0.025, z + 0.095, 0.002, "Metal")
    P.box(0.06, 0.1, 0.14, 0.18, z + 0.026, z + 0.03, "Metal")
    P.cyl(0.29, 0.16, z + 0.28, z + 0.325, 0.022, "Paper")


def kitchen_run(P, w, sink_at=None, wall_cupboards=True):
    """Kitchen units along a wall: plinth, carcasses with door joints and handles, worktop, wall cupboards above;
    sink_at = u of a steel sink bowl with a tap."""
    P.box(0.03, w - 0.03, 0.0, 0.52, 0.0, 0.1, "BlackPlastic")
    P.box(0.0, w, 0.0, 0.55, 0.1, 0.84, "Furniture")
    P.box(-0.01, w + 0.01, 0.0, 0.6, 0.84, 0.88, "Enamel")                    # worktop (enamel-white laminate)
    n = max(1, int(round(w / 0.5)))
    dw = w / n
    for k in range(n):
        u0 = k * dw
        P.box(u0 + 0.004, u0 + dw - 0.004, 0.55, 0.57, 0.12, 0.82, "Furniture")
        P.box(u0 + dw / 2 - 0.05, u0 + dw / 2 + 0.05, 0.57, 0.59, 0.72, 0.74, "Metal")
    if sink_at is not None:
        P.box(sink_at - 0.25, sink_at + 0.25, 0.08, 0.5, 0.7, 0.885, "Metal")   # bowl (sunk into the top)
        P.box(sink_at - 0.22, sink_at + 0.22, 0.11, 0.47, 0.72, 0.89, "BlackPlastic")
        P.cyl(sink_at, 0.05, 0.88, 1.15, 0.015, "Metal")                        # tap
        P.box(sink_at - 0.01, sink_at + 0.01, 0.05, 0.22, 1.12, 1.15, "Metal")
    if wall_cupboards:
        P.box(0.0, w, 0.0, 0.32, 1.45, 2.1, "Furniture")
        for k in range(n):
            u0 = k * dw
            P.box(u0 + 0.004, u0 + dw - 0.004, 0.32, 0.34, 1.47, 2.08, "Furniture")
            P.box(u0 + dw / 2 - 0.05, u0 + dw / 2 + 0.05, 0.34, 0.36, 1.5, 1.52, "Metal")


def stove(P, pot=False, kettle=False):
    """Electric stove (электроплита): body, oven door with window and handle, four hot plates, knob panel."""
    P.box(0.0, 0.5, 0.0, 0.6, 0.0, 0.85, "Enamel")
    P.box(0.05, 0.45, 0.6, 0.62, 0.12, 0.6, "Enamel")                          # oven door
    P.box(0.12, 0.38, 0.62, 0.625, 0.3, 0.5, "BlackPlastic")                  # oven window
    P.box(0.08, 0.42, 0.63, 0.66, 0.62, 0.64, "Metal")                         # handle
    for k in range(4):
        P.cyl(0.1 + k * 0.1, 0.61, 0.7, 0.72, 0.02, "BlackPlastic")             # knobs on the front
    for u, v in ((0.14, 0.17), (0.36, 0.17), (0.14, 0.42), (0.36, 0.42)):
        P.cyl(u, v, 0.85, 0.87, 0.085, "BlackPlastic")
    P.box(0.0, 0.5, 0.0, 0.03, 0.85, 1.05, "Enamel")                           # back panel
    if pot:
        P.cyl(0.14, 0.42, 0.87, 1.05, 0.11, "Metal")
        P.hcyl_u(0.25, 0.33, 0.42, 1.02, 0.01, "Metal")
    if kettle:
        P.cyl(0.36, 0.17, 0.87, 1.05, 0.1, "Enamel", r1=0.075)
        P.cyl(0.36, 0.17, 1.05, 1.08, 0.025, "BlackPlastic")


def fridge(P, open_door=False):
    """ZIL-style fridge: rounded top, chrome lever handle, emblem."""
    P.box(0.0, 0.6, 0.0, 0.6, 0.04, 1.4, "Enamel")
    P.hcyl_u(0.0, 0.6, 0.3, 1.4, 0.3, "Enamel")                                # rounded top
    P.box(0.04, 0.56, 0.0, 0.58, 0.0, 0.04, "BlackPlastic")
    if open_door:
        P.box(0.57, 0.6, 0.6, 0.92, 0.06, 1.5, "Enamel")                      # door ajar on the far hinge (the way stays free)
        P.box(0.04, 0.56, 0.54, 0.6, 0.1, 1.38, "BlackPlastic")                # empty dark inside
        for z in (0.45, 0.85):
            P.box(0.05, 0.55, 0.1, 0.58, z, z + 0.01, "Metal")                 # wire shelves
    else:
        P.box(0.01, 0.59, 0.6, 0.62, 0.08, 1.5, "Enamel")
        P.box(0.5, 0.54, 0.62, 0.66, 0.9, 1.2, "Metal")                        # lever handle
        P.box(0.2, 0.4, 0.62, 0.625, 1.25, 1.32, "Metal")                      # emblem


def tv(P, on_stand=True):
    """Tube TV (Рубин-style) on a four-legged stand, rabbit-ear antenna."""
    z = 0.0
    if on_stand:
        P.box(0.0, 0.75, 0.0, 0.45, 0.45, 0.5, "Furniture")
        legs(P, 0.03, 0.72, 0.03, 0.42, 0.45, "Wood", 0.03)
        z = 0.5
    P.box(0.05, 0.7, 0.03, 0.48, z, z + 0.52, "Furniture")                     # wooden cabinet
    cushion(P, 0.1, 0.52, 0.48, 0.52, z + 0.08, z + 0.44, "Screen")
    for k in range(3):
        P.cyl(0.6, 0.49, z + 0.15 + k * 0.1, z + 0.17 + k * 0.1, 0.02, "BlackPlastic")
    P.cyl(0.38, 0.25, z + 0.52, z + 0.56, 0.05, "BlackPlastic")
    for du in (-0.15, 0.15):
        P.box(0.38 + du * 0.1, 0.39 + du * 0.1, 0.24, 0.25, z + 0.56, z + 0.9, "Metal")


def curtains(S, x0, x1, y, toward=1, mat="CurtainRed", drawn=0.3):
    """Rod and folded curtains in front of a window in the wall plane y (toward = side of the room)."""
    d = 0.06 * toward
    S.box(x0 - 0.15, x1 + 0.15, min(y + d, y + d + 0.015 * toward), max(y + d, y + d + 0.015 * toward), 2.3, 2.32, "Metal")
    w = (x1 - x0 + 0.3) * drawn
    for a in (x0 - 0.15, x1 + 0.15 - w):
        verts, faces = [], []
        n = max(16, math.ceil(w / 0.02))
        for i in range(n + 1):
            u = i / n
            off = (0.035 + 0.015 * math.cos(u * 8 * math.pi)) * toward
            hem = 0.15 + 0.025 * (0.5 + 0.5 * math.sin(u * 7 * math.pi))
            verts += [(a + w * u, y + d + off, hem), (a + w * u, y + d + off + 0.004, hem),
                      (a + w * u, y + d + off + 0.004, 2.3), (a + w * u, y + d + off, 2.3)]
            if i:
                b = (i - 1) * 4
                faces.extend([(b + j, b + (j + 1) % 4, b + 4 + (j + 1) % 4, b + 4 + j) for j in range(4)])
        faces += [(3, 2, 1, 0), (n * 4, n * 4 + 1, n * 4 + 2, n * 4 + 3)]
        surface(Place(S, 0, 0), verts, faces, mat)


def rug(S, x0, x1, y0, y1, mat="Carpet"):
    S.box(x0, x1, y0, y1, 0.012, 0.022, mat)
    S.box(x0 + 0.08, x1 - 0.08, y0 + 0.08, y1 - 0.08, 0.022, 0.024, "Mural_Red")


def picture(S, x0, x1, y, z0, z1, toward=1, mat="Paper"):
    """Framed picture on the wall plane y."""
    d = 0.01 * toward
    S.box(x0, x1, min(y, y + 2 * d), max(y, y + 2 * d), z0, z1, "Furniture")
    S.box(x0 + 0.03, x1 - 0.03, min(y + 2 * d, y + 2.4 * d), max(y + 2 * d, y + 2.4 * d), z0 + 0.03, z1 - 0.03, mat)


def picture_x(S, x, y0, y1, z0, z1, toward=1, mat="Paper"):
    """Framed picture on the wall plane x."""
    d = 0.01 * toward
    S.box(min(x, x + 2 * d), max(x, x + 2 * d), y0, y1, z0, z1, "Furniture")
    S.box(min(x + 2 * d, x + 2.4 * d), max(x + 2 * d, x + 2.4 * d), y0 + 0.03, y1 - 0.03, z0 + 0.03, z1 - 0.03, mat)


def ceiling_lamp(S, x, y, ceil):
    """Glass bowl lamp on a short rod (плафон)."""
    S.cyl(x, y, ceil - 0.35, ceil, 0.01, "Metal")
    S.cyl(x, y, ceil - 0.5, ceil - 0.35, 0.08, "Glass", r1=0.2)
    base = S.S if hasattr(S, "S") else S
    if hasattr(base, "lights"):
        base.lights.append((S.X(x) if getattr(S, "mirror", False) else x, y, ceil-.43))


def bathtub(P, l=1.5):
    """Enamel tub on feet with a tap on the wall."""
    P.box(0.0, l, 0.0, 0.7, 0.1, 0.58, "Enamel")
    P.box(0.06, l - 0.06, 0.06, 0.64, 0.25, 0.585, "Metal")                    # inside (grey)
    for u in (0.08, l - 0.14):
        for v in (0.08, 0.56):
            P.box(u, u + 0.06, v, v + 0.06, 0.0, 0.1, "BlackPlastic")
    P.cyl(l / 2, 0.02, 0.75, 0.8, 0.03, "Metal")
    P.box(l / 2 - 0.01, l / 2 + 0.01, 0.0, 0.15, 0.78, 0.8, "Metal")


def washbasin(P):
    P.box(0.0, 0.5, 0.0, 0.42, 0.72, 0.85, "Enamel")
    P.box(0.05, 0.45, 0.05, 0.38, 0.75, 0.855, "Metal")
    P.cyl(0.25, 0.15, 0.0, 0.72, 0.06, "Enamel")                               # pedestal
    P.box(0.0, 0.5, 0.0, 0.02, 1.1, 1.6, "Glass")                              # mirror
    P.box(0.1, 0.4, 0.0, 0.14, 1.02, 1.04, "Glass")                            # glass shelf


def toilet(P):
    P.cyl(0.2, 0.35, 0.0, 0.38, 0.17, "Enamel", r1=0.2)
    P.box(0.04, 0.36, 0.0, 0.2, 0.38, 0.8, "Enamel")                           # cistern
    P.box(0.04, 0.36, 0.16, 0.56, 0.38, 0.41, "BlackPlastic")                  # seat
    P.cyl(0.32, 0.02, 0.8, 2.0, 0.02, "Metal")                                 # pipe up the wall
