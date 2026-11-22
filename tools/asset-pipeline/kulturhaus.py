"""Kulturhaus hall (Дом культуры, briefing V10 priority A / PDF phase 3 "Kulturhaus-Saal").

Which building was the Kulturhaus is not documented (dossier §3); ул. Южная 9 is the ANNAHME (squarish
two-storey block). The hall is double height on the street facade: tall windows with coloured glass
(photo R4: stained-glass wall), a red ornament frieze under the ceiling (photo R4), a stage with
proscenium and curtain remnants, rows of folding seats - some missing or knocked over - and fallen
ceiling plaster. Built directly in building (Blender) coordinates by build_buildings.py.
"""
import math
import random
import furniture as fu
from interiors import Section

HALL_AXES, HALL_ROWS = 8, 5      # 24 m x 15 m (ANNAHME)
STAGE_DEPTH = 5.0


def tall_window(part, AX, height, glass, rnd):
    """Two-storey window panel for one axis: frame grid in wood, panes in clear or coloured glass (some broken)."""
    from build_t5_kit import panel_with_opening
    ow, oz0, oz1 = 2.2, 0.9, height - 0.5
    ox = (AX - ow) / 2
    panel_with_opening(part, AX, height, ox, ow, oz0, oz1, "Facade")
    f, y0, y1 = 0.06, 0.12, 0.2
    cols, rows = 4, 8
    for c in range(cols + 1):
        x = ox + c * ow / cols
        part.box(x - f / 2, x + f / 2, y0, y1, oz0, oz1, "Wood")
    for r in range(rows + 1):
        z = oz0 + r * (oz1 - oz0) / rows
        part.box(ox, ox + ow, y0, y1, z - f / 2, z + f / 2, "Wood")
    for c in range(cols):
        for r in range(rows):
            if rnd.random() < 0.3:
                continue  # broken pane
            slot = rnd.choice(("Glass_StainBlue", "Glass_StainBlue", "Glass_StainRed", "Glass_StainCyan", "Glass"))
            x0, x1 = ox + c * ow / cols + f / 2, ox + (c + 1) * ow / cols - f / 2
            z0, z1 = oz0 + r * (oz1 - oz0) / rows + f / 2, oz0 + (r + 1) * (oz1 - oz0) / rows - f / 2
            glass.box(x0, x1, 0.155, 0.16, z0, z1, slot)


def hall_cells(nu, nv, street_n):
    i0 = max(0, (nu - HALL_AXES) // 2)
    rows = range(nv - HALL_ROWS, nv) if street_n == (0, -1) else range(0, HALL_ROWS)
    return {(i, j) for i in range(i0, min(nu, i0 + HALL_AXES)) for j in rows}


def build_hall(acc, x0, x1, y0, y1, facade_y, z0, ceil, seed, door=None):
    """Hall interior in the box x0..x1, y0..y1 (Blender space); facade_y is the facade side (y0 or y1);
    door = (x_from, x_to) opening in the back wall where the corridor from the entrance arrives."""
    rnd = random.Random(seed)
    inner_y0 = y0 + (0.3 if facade_y == y0 else 0.1)
    inner_y1 = y1 - (0.3 if facade_y == y1 else 0.1)
    yc = (inner_y0 + inner_y1) / 2
    box = acc.box
    from build_t5_kit import Part
    props = Part("hall_furniture")
    S = Section(props, ceil - z0, random.Random(seed + 1))
    # walls on the three interior sides (the facade side is the window wall), oil-paint panel + lime
    for (wx0, wx1, wy0, wy1) in ((x0 - 0.1, x0 + 0.1, y0, y1), (x1 - 0.1, x1 + 0.1, y0, y1)):
        box(wx0, wx1, wy0, wy1, z0, z0 + 1.5, "Paint_OilBlue")
        box(wx0, wx1, wy0, wy1, z0 + 1.5, ceil, "Lime")
    back_y = y1 if facade_y == y0 else y0
    spans = [(x0, door[0]), (door[1], x1)] if door else [(x0, x1)]
    for sx0, sx1 in spans:
        box(sx0, sx1, back_y - 0.1, back_y + 0.1, z0, z0 + 1.5, "Paint_OilBlue")
        box(sx0, sx1, back_y - 0.1, back_y + 0.1, z0 + 1.5, ceil, "Lime")
    if door:
        box(door[0], door[1], back_y - 0.1, back_y + 0.1, z0 + 2.4, ceil, "Lime")  # lintel over the hall door
    # ornament frieze under the ceiling on the inner faces (photo R4)
    fz0, fz1 = ceil - 0.9, ceil - 0.35
    box(x0 + 0.1, x0 + 0.13, inner_y0, inner_y1, fz0, fz1, "Carpet")
    box(x1 - 0.13, x1 - 0.1, inner_y0, inner_y1, fz0, fz1, "Carpet")
    by = back_y - 0.13 if back_y > yc else back_y + 0.1
    box(x0 + 0.1, x1 - 0.1, by, by + 0.03, fz0, fz1, "Carpet")
    # parquet floor
    box(x0 + 0.1, x1 - 0.1, inner_y0, inner_y1, z0, z0 + 0.015, "FloorBoards")
    # stage at the +x end: platform, steps, proscenium, curtain remnants
    sx = x1 - 0.1 - STAGE_DEPTH
    box(sx, x1 - 0.1, inner_y0, inner_y1, z0, z0 + 0.9, "FloorBoards")
    for k in range(3):
        box(sx - 0.3 * (k + 1), sx - 0.3 * k, yc - 1.2, yc + 1.2, z0, z0 + 0.9 - 0.3 * (k + 1) + 0.3, "FloorBoards")
    portal_w = 1.6
    box(sx - 0.25, sx, inner_y0, inner_y0 + portal_w, z0 + 0.9, ceil, "Lime")
    box(sx - 0.25, sx, inner_y1 - portal_w, inner_y1, z0 + 0.9, ceil, "Lime")
    box(sx - 0.25, sx, inner_y0, inner_y1, z0 + 0.9 + 4.2, ceil, "Lime")
    box(sx - 0.3, sx - 0.25, inner_y0 + portal_w, inner_y1 - portal_w, z0 + 0.9 + 3.9, z0 + 0.9 + 4.2, "Carpet")
    # Real folds, with uneven hems; geometry stays behind the proscenium and clear of the stage steps.
    for cy in (inner_y0 + portal_w + 0.2, inner_y1 - portal_w - 1.0):
        verts, faces = [], []
        for i in range(25):
            t = i / 24
            x = sx + 0.14 + 0.045 * math.cos(t * 10 * math.pi)
            bottom = 0.95 + 0.25 * (0.5 + 0.5 * math.sin(t * 7 * math.pi))
            verts += [(x, cy + t * 0.8, bottom), (x + 0.008, cy + t * 0.8, bottom),
                      (x + 0.008, cy + t * 0.8, 4.95), (x, cy + t * 0.8, 4.95)]
            if i:
                a = (i - 1) * 4
                faces.extend([(a + j, a + 4 + j, a + 4 + (j + 1) % 4, a + (j + 1) % 4) for j in range(4)])
        faces += [(0, 1, 2, 3), (99, 98, 97, 96)]
        fu.surface(fu.Place(S, 0, 0), verts, faces, "CurtainRed")
    # folding seats, centre aisle; some missing, some knocked over
    rows_x = []
    x = x0 + 2.2
    while x < sx - 1.6:
        rows_x.append(x)
        x += 0.95
    aisle = 0.7
    for rx in rows_x:
        y = inner_y0 + 0.8
        while y < inner_y1 - 0.8:
            if abs(y + 0.25 - yc) > aisle and (not door or not door[0] - 0.6 < rx < door[1] + 0.6):
                r = rnd.random()
                if r < 0.3:
                    pass                                                           # missing
                elif r < 0.45:
                    fu.cushion(fu.Place(S, rx - 0.2, y), 0, 0.45, 0, 0.48, 0.02, 0.07, "Furniture")
                else:
                    P = fu.Place(S, rx - 0.24, y + 0.46, 3)
                    for u in (0.035, 0.405):
                        P.cyl(u, 0.24, 0, 0.46, 0.018, "Metal")
                        P.box(u - 0.025, u + 0.025, 0.06, 0.44, 0, 0.025, "Metal")
                        P.box(u - 0.014, u + 0.014, 0.03, 0.058, 0.3, 0.82, "Metal")
                    fu.cushion(P, 0, 0.44, 0, 0.06, 0.48, 0.88, "Furniture")
                    if r > 0.9:  # an empty chair left with its hinged seat up
                        fu.cushion(P, 0.02, 0.42, 0.07, 0.13, 0.43, 0.79)
                    else:
                        fu.cushion(P, 0.02, 0.42, 0.06, 0.46, 0.42, 0.49)
                    P.hcyl_u(0.0, 0.44, 0.09, 0.43, 0.018, "Metal")
            y += 0.55
    # fallen ceiling plaster and a dropped chandelier ring
    for _ in range(260):
        px, py = rnd.uniform(x0 + 0.3, sx - 0.3), rnd.uniform(inner_y0 + 0.2, inner_y1 - 0.2)
        w, d = rnd.uniform(0.05, 0.6), rnd.uniform(0.05, 0.5)
        # Keep the centre aisle free; small irregular fragments belong beside the seat rows.
        if abs(py - yc) > 0.9 and (not door or abs(px - sum(door) / 2) > 1.0):
            S.chunk(px, py, 0.016, w, d, rnd.uniform(0.01, 0.06), "Lime", tilt=0.15)
    cx = (x0 + sx) / 2
    cy = inner_y0 + 1.4  # dropped chandelier beside the aisle
    verts, faces = [], []
    for i in range(48):
        a = 2 * math.pi * i / 48
        for j in range(8):
            b = 2 * math.pi * j / 8
            r = 0.7 + 0.022 * math.cos(b)
            verts.append((cx + r * math.cos(a), cy + r * math.sin(a), 0.065 + 0.022 * math.sin(b)))
            faces.append((i * 8 + j, ((i + 1) % 48) * 8 + j, ((i + 1) % 48) * 8 + (j + 1) % 8, i * 8 + (j + 1) % 8))
    fu.surface(fu.Place(S, 0, 0), verts, faces, "Metal")
    for i in range(8):
        a = 2 * math.pi * i / 8
        P = fu.Place(S, cx + 0.7 * math.cos(a), cy + 0.7 * math.sin(a))
        P.cyl(0, 0, 0.07, 0.13, 0.025, "Metal")
        P.cyl(0, 0, 0.13, 0.23, 0.07, "Enamel", r1=0.1)
    acc.add(props, 0, 0, 0, z0, {})
    return {"back": (x0 + 1.2, yc, z0 + 1.7, 0.0), "stage": (x1 - 2.0, yc + 2.0, z0 + 0.9 + 1.7, 200.0)}
