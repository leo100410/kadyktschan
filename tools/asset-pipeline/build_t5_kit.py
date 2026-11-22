"""Blender CLI: generate the T5 panel-block kit (art bible 8) as one FBX per part.

Run: blender --background --factory-startup --python tools/asset-pipeline/build_t5_kit.py -- <project root>
Writes assets/kits/T5/<SM_name>.fbx and assets/kits/T5/kit_manifest.json.

Part space (art bible 8.10): X along the facade, Y into the building (facade faces -Y), Z up,
pivot at the lower-left outer corner. UVs are box-projected in metres / 2, so one UV unit =
2 m = 2048 px at 10.24 px/cm. Material slot names are mapped to material instances in Unreal.
Only the 2011 "_Aged" state exists yet; "_Ruin" variants come later (art bible 8.3).
"""
import json, math, os, sys
import bpy

ROOT = os.environ.get("KDK_ROOT") or sys.argv[sys.argv.index("--") + 1]
G = json.load(open(os.path.join(ROOT, "tools/asset-pipeline/kit_grid.json")))["T5"]
BURY = 3.0  # m below the nominal ground line: footprints sit on slopes, the terrain hides the rest
OUT = os.path.join(ROOT, "assets/kits/T5")
AX, ST, T, J = G["axis"], G["storey_height"], G["panel_thickness"], G["joint"]
WIN = G["window"]
UV_SCALE = 0.5  # 1 UV = 2 m
MAT_UV = {"Crack": 0.125, "Spall": 0.125, "Rust": 0.125}  # facade decals tile every 8 m


class Part:
    """Collects boxes (with a material slot each) and builds one mesh object."""

    def __init__(self, name):
        self.name, self.verts, self.faces, self.face_mat, self.mats = name, [], [], [], []
        self.smooth_faces = set()

    def box(self, x0, x1, y0, y1, z0, z1, mat):
        if mat not in self.mats:
            self.mats.append(mat)
        b = len(self.verts)
        self.verts += [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
                       (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        # outward-facing quads (counter-clockwise seen from outside)
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.faces.append(tuple(b + i for i in f))
            self.face_mat.append(self.mats.index(mat))

    def bevel_box(self, x0, x1, y0, y1, z0, z1, mat, b):
        """Box with chamfered edges and corners (6 faces, 12 edge strips, 8 corner triangles): furniture with soft
        edges instead of hard cubes (user 2026-11-08: "die Inneneinrichtung sieht viel zu eckig aus")."""
        b = min(b, (x1 - x0) / 2.5, (y1 - y0) / 2.5, (z1 - z0) / 2.5)
        if b < 0.002:
            return self.box(x0, x1, y0, y1, z0, z1, mat)
        if mat not in self.mats:
            self.mats.append(mat)
        lo, hi = (x0, y0, z0), (x1, y1, z1)
        c = [(lo[a] + hi[a]) / 2 for a in range(3)]
        base = len(self.verts)
        idx = {}
        for i in (0, 1):
            for j in (0, 1):
                for k in (0, 1):
                    corner = (hi[0] if i else lo[0], hi[1] if j else lo[1], hi[2] if k else lo[2])
                    for ax in range(3):  # the corner point that belongs to the face normal to ax
                        pt = list(corner)
                        for o in range(3):
                            if o != ax:
                                pt[o] += -b if (i, j, k)[o] else b
                        idx[(i, j, k, ax)] = len(self.verts)
                        self.verts.append(tuple(pt))
        m = self.mats.index(mat)
        def poly(ids):
            pts = [self.verts[v] for v in ids]
            cen = [sum(p[a] for p in pts) / len(pts) for a in range(3)]
            n = [0.0, 0.0, 0.0]
            for q in range(len(pts)):
                p0, p1 = pts[q], pts[(q + 1) % len(pts)]
                n[0] += (p0[1] - p1[1]) * (p0[2] + p1[2]); n[1] += (p0[2] - p1[2]) * (p0[0] + p1[0]); n[2] += (p0[0] - p1[0]) * (p0[1] + p1[1])
            if sum(n[a] * (cen[a] - c[a]) for a in range(3)) < 0:
                ids = ids[::-1]
            self.faces.append(tuple(ids)); self.face_mat.append(m)
        for ax in range(3):                         # the six faces
            o1, o2 = [a for a in range(3) if a != ax]
            for side in (0, 1):
                ring = []
                for u, v in ((0, 0), (1, 0), (1, 1), (0, 1)):
                    key = [0, 0, 0]; key[ax] = side; key[o1] = u; key[o2] = v
                    ring.append(idx[tuple(key) + (ax,)])
                poly(ring)
        for ax in range(3):                         # edge strips along ax, between the faces of the other two axes
            o1, o2 = [a for a in range(3) if a != ax]
            for s1 in (0, 1):
                for s2 in (0, 1):
                    q = []
                    for along in (0, 1):
                        key = [0, 0, 0]; key[ax] = along; key[o1] = s1; key[o2] = s2
                        q.append((tuple(key) + (o1,), tuple(key) + (o2,)))
                    poly([idx[q[0][0]], idx[q[1][0]], idx[q[1][1]], idx[q[0][1]]])
        for i in (0, 1):                            # corner triangles
            for j in (0, 1):
                for k in (0, 1):
                    poly([idx[(i, j, k, 0)], idx[(i, j, k, 1)], idx[(i, j, k, 2)]])

    def build(self):
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.verts, [], self.faces)
        me.update()
        uv = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            poly.material_index = self.face_mat[poly.index]
            poly.use_smooth = poly.index in self.smooth_faces
            sc = MAT_UV.get(self.mats[self.face_mat[poly.index]], UV_SCALE)
            n = poly.normal
            axis = max(range(3), key=lambda i: abs(n[i]))  # box projection on the dominant axis
            name = self.mats[self.face_mat[poly.index]]
            if name.startswith("Pic_"):
                pic_uv(me, uv, poly, axis, n[axis] > 0, int(name.split("@")[1]) if "@" in name else 0)
                continue
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                u, v = {0: (co.y, co.z), 1: (co.x, co.z), 2: (co.x, co.y)}[axis]
                uv.data[li].uv = (u * sc, v * sc)
        # vertex colour = decay mask (art bible 8.6: R plaster loss, G soot, B moisture); start clean.
        # Without an explicit attribute Unreal fills white, which would read as "all plaster lost".
        col = me.color_attributes.new(name="Col", type="BYTE_COLOR", domain="CORNER")
        for c in col.data:
            c.color = (0.0, 0.0, 0.0, 1.0)
        for m in self.mats:
            me.materials.append(bpy.data.materials.get(m) or bpy.data.materials.new(m))
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(ob)
        return ob


def pic_uv(me, uv, poly, axis, positive, turn=0):
    """A story picture (material Pic_<Name>) fills its face once, upright and unmirrored as seen from the front:
    on a wall the image's right runs to the viewer's right, on a table its top points to +y; Pic_<Name>@90/180/270
    turns a lying picture so its top points to +x / -y / -x (towards whoever reads it)."""
    cos = [me.vertices[me.loops[li].vertex_index].co for li in poly.loop_indices]
    # (horizontal coordinate as seen by the viewer, its sign), vertical coordinate
    right, up = {0: ((1, 1 if positive else -1), 2), 1: ((0, -1 if positive else 1), 2), 2: ((0, 1 if positive else -1), 1)}[axis]
    (ra, rs), ua = right, up
    lo_r, hi_r = min(c[ra] for c in cos), max(c[ra] for c in cos)
    lo_u, hi_u = min(c[ua] for c in cos), max(c[ua] for c in cos)
    for li, c in zip(poly.loop_indices, cos):
        u = (c[ra] - lo_r) / ((hi_r - lo_r) or 1.0)
        u, v = (u if rs > 0 else 1.0 - u), (c[ua] - lo_u) / ((hi_u - lo_u) or 1.0)
        if axis == 2 and turn:
            u, v = {90: (1.0 - v, u), 180: (1.0 - u, 1.0 - v), 270: (v, 1.0 - u)}[turn]
        uv.data[li].uv = (u, v)


def panel_with_opening(p, w, h, ox, ow, oz0, oz1, mat):
    """Panel w x h with a rectangular opening (ox..ox+ow, oz0..oz1); joints leave a gap J/2 at each edge."""
    g = J / 2
    x0, x1, z0, z1 = g, w - g, g, h - g
    p.box(x0, x1, 0, T, z0, oz0, mat)                 # below the opening
    p.box(x0, x1, 0, T, oz1, z1, mat)                 # above
    p.box(x0, ox, 0, T, oz0, oz1, mat)                # left of
    p.box(ox + ow, x1, 0, T, oz0, oz1, mat)           # right of


def window_frame(p, ox, ow, oz0, oz1):
    """Soviet double wooden window: outer and inner frame, centre mullion, top vent (fortochka) rail."""
    f = 0.06
    for y0 in (WIN["reveal"], WIN["reveal"] + 0.16):  # two frames 16 cm apart (double glazing)
        y1 = y0 + 0.05
        p.box(ox, ox + ow, y0, y1, oz0, oz0 + f, "Wood")
        p.box(ox, ox + ow, y0, y1, oz1 - f, oz1, "Wood")
        p.box(ox, ox + f, y0, y1, oz0, oz1, "Wood")
        p.box(ox + ow - f, ox + ow, y0, y1, oz0, oz1, "Wood")
        mid = ox + ow / 2
        p.box(mid - f / 2, mid + f / 2, y0, y1, oz0, oz1, "Wood")
        rail = oz0 + (oz1 - oz0) * 0.72
        p.box(ox, mid, y0, y1, rail - f / 2, rail + f / 2, "Wood")
    p.box(ox - 0.03, ox + ow + 0.03, -0.06, WIN["reveal"], oz0 - 0.03, oz0, "Metal")  # sill flashing


def window_glass(p, ox, ow, oz0, oz1):
    for y in (WIN["reveal"] + 0.025, WIN["reveal"] + 0.185):
        p.box(ox + 0.06, ox + ow - 0.06, y, y + 0.004, oz0 + 0.06, oz1 - 0.06, "Glass")


def window_glass_broken(p, ox, ow, oz0, oz1):
    """Some panes left, one only as a lower shard (atmosphere-target.md: single damaged windows)."""
    f, mid, rail = 0.06, ox + ow / 2, oz0 + (oz1 - oz0) * 0.72
    y = WIN["reveal"] + 0.025
    p.box(ox + f, mid - f / 2, y, y + 0.004, oz0 + f, rail - f / 2, "Glass")            # outer lower-left intact
    p.box(mid + f / 2, ox + ow - f, y, y + 0.004, oz0 + f, oz0 + (oz1 - oz0) * 0.33, "Glass")  # outer right: shard
    y = WIN["reveal"] + 0.185
    p.box(ox + f, mid - f / 2, y, y + 0.004, rail + f / 2, oz1 - f, "Glass")            # inner fortochka


def window_boards(p, ox, ow, oz0, oz1):
    """Planks nailed over the opening from outside, uneven spacing."""
    for z0, h in ((oz0 - 0.05, 0.2), (oz0 + 0.3, 0.18), (oz0 + 0.62, 0.2), (oz0 + 1.0, 0.16), (oz1 - 0.12, 0.2)):
        p.box(ox - 0.12, ox + ow + 0.12, -0.035, -0.005, z0, z0 + h, "Wood")


def curtain_rag(p, ox, ow, oz0, oz1, mat):
    """Remnant of a curtain hanging inside the window on one side."""
    y = WIN["reveal"] + 0.45
    p.box(ox + 0.05, ox + 0.45, y, y + 0.012, oz0 + 0.25, oz1 + 0.05, mat)


def decal_layer(p, mat, y, hole=None):
    """Thin card on the outer face (outward = -y) carrying a masked decal; leaves the window opening free."""
    g, t = J / 2, 0.002
    if hole is None:
        p.box(g, AX - g, -y - t, -y, g, ST - g, mat)
        return
    ox, ow, oz0, oz1 = hole
    for x0, x1, z0, z1 in ((g, ox, g, ST - g), (ox + ow, AX - g, g, ST - g), (ox, ox + ow, g, oz0 - 0.04), (ox, ox + ow, oz1, ST - g)):
        p.box(x0, x1, -y - t, -y, z0, z1, mat)


WIN_OX = None  # set below: x of the window opening in a panel


def opening():
    ox = (AX - WIN["width"]) / 2
    return ox, WIN["width"], WIN["sill"], WIN["sill"] + WIN["height"]


def entrance(p, leaf):
    """Entrance panel with canopy and steps; leaf=False leaves the doorway open."""
    dw, dh = 1.2, 2.2
    dx = (AX - dw) / 2
    panel_with_opening(p, AX, ST, dx, dw, J / 2, dh, "Facade")
    if leaf:
        p.box(dx, dx + dw, 0.22, 0.27, 0, dh, "Wood")                             # closed door leaf, set back
    # cantilevered precast canopy slab; a thin sheet on two posts read as scaffolding (atmosphere-target.md)
    p.box(-0.25, AX + 0.25, -1.5, 0.0, 2.45, 2.62, "Concrete")
    rise_total = G["pile"]["crawl_height"] + G["plinth_band"]
    steps = 6
    p.box(dx - 0.3, dx + dw + 0.3, -1.2, 0.0, -0.2, 0.0, "Concrete")                    # landing
    # 6 risers down to the nominal ground, then 6 more below it: where the terrain falls away from the house the
    # flight keeps going instead of ending in a 1 m block (user 2026-11-07: "Weg blockiert"); on level ground the
    # extra steps sit under the terrain
    for k in range(steps - 1 + 6):
        y1 = -1.2 - 0.3 * k
        # solid down to BURY: on sloping ground the steps must not hang in the air
        p.box(dx - 0.1, dx + dw + 0.1, y1 - 0.3, y1, -rise_total - BURY, -rise_total * (k + 1) / steps, "Concrete")



def make_parts():
    global WIN_OX
    parts = {}
    ox, ow, oz0, oz1 = opening()
    WIN_OX = ox

    p = Part("SM_T5_WallPlate_A_Aged")
    p.box(J / 2, AX - J / 2, 0, T, J / 2, ST - J / 2, "Facade")
    parts[p.name] = p

    p = Part("SM_T5_WindowPlate_A_Aged")
    panel_with_opening(p, AX, ST, ox, ow, oz0, oz1, "Facade")
    parts[p.name] = p

    p = Part("SM_T5_WindowFrame_A_Aged")
    window_frame(p, ox, ow, oz0, oz1)
    parts[p.name] = p

    p = Part("SM_T5_WindowGlass_A")
    window_glass(p, ox, ow, oz0, oz1)
    parts[p.name] = p

    p = Part("SM_T5_WindowGlassBroken_A")
    window_glass_broken(p, ox, ow, oz0, oz1)
    parts[p.name] = p

    p = Part("SM_T5_WindowBoards_A_Aged")
    window_boards(p, ox, ow, oz0, oz1)
    parts[p.name] = p

    # ---- hero detail parts (fully dressed buildings at the player start, user request 2026-11-07)
    for mat, y in (("Spall", 0.004), ("Crack", 0.007)):
        p = Part("SM_Decal_Wall_" + mat)
        decal_layer(p, mat, y)
        parts[p.name] = p
        p = Part("SM_Decal_Window_" + mat)
        decal_layer(p, mat, y, (ox, ow, oz0, oz1))
        parts[p.name] = p
    p = Part("SM_Decal_RustSill")                     # run-off under the sill flashing
    p.box(ox - 0.05, ox + ow + 0.05, -0.012, -0.010, oz0 - 0.9, oz0 - 0.03, "Rust")
    parts[p.name] = p
    f = 0.055
    p = Part("SM_T5_SashOpen")                        # one casement, origin on its hinge (x=0, y=0)
    for x0, x1, z0, z1 in ((0, ow / 2, oz0, oz0 + f), (0, ow / 2, oz1 - f, oz1), (0, f, oz0, oz1), (ow / 2 - f, ow / 2, oz0, oz1)):
        p.box(x0, x1, 0, 0.045, z0, z1, "Wood")
    parts[p.name] = p
    p = Part("SM_T5_SashGlassShard")
    p.box(f, ow / 2 - f, 0.02, 0.024, oz0 + f, oz0 + (oz1 - oz0) * 0.45, "Glass")
    parts[p.name] = p
    p = Part("SM_T5_DoorAjar")                        # door leaf, origin on its hinge
    p.box(0, 1.2, 0, 0.05, 0.02, 2.18, "Wood")
    p.box(0.95, 1.05, -0.06, 0, 1.0, 1.04, "Metal")   # handle
    parts[p.name] = p
    p = Part("SM_T5_PipeSeg")                         # downpipe, one storey; origin on the wall face
    p.box(-0.06, 0.06, -0.2, -0.08, 0, ST - 0.05, "Metal")
    p.box(-0.08, 0.08, -0.22, -0.06, 1.1, 1.18, "Metal")  # collar
    p.box(-0.02, 0.02, -0.08, 0.0, 1.12, 1.16, "Metal")   # bracket
    parts[p.name] = p
    p = Part("SM_T5_PipeOutlet")
    p.box(-0.06, 0.06, -0.2, -0.08, 0.3, 0.9, "Metal")
    p.box(-0.06, 0.06, -0.55, -0.08, 0.18, 0.3, "Metal")
    parts[p.name] = p
    p = Part("SM_T5_PipeHead")                        # funnel under the roof edge
    p.box(-0.15, 0.15, -0.32, -0.02, -0.35, 0.0, "Metal")
    parts[p.name] = p
    p = Part("SM_T5_Antenna")                         # TV antenna on the roof: mast, boom, dipoles
    p.box(-0.025, 0.025, -0.025, 0.025, 0, 3.2, "Metal")
    p.box(-0.9, 0.9, -0.012, 0.012, 2.7, 2.73, "Metal")
    for k in range(7):
        x = -0.85 + k * 0.28
        p.box(x - 0.008, x + 0.008, -0.35 + k * 0.03, 0.35 - k * 0.03, 2.7, 2.72, "Metal")
    p.box(-0.3, 0.3, -0.012, 0.012, 3.0, 3.02, "Metal")
    parts[p.name] = p
    p = Part("SM_T5_AntennaFallen")                   # bent over, lying on the roof
    p.box(0, 3.0, -0.025, 0.025, 0.02, 0.07, "Metal")
    p.box(2.2, 2.25, -0.8, 0.8, 0.0, 0.03, "Metal")
    parts[p.name] = p
    p = Part("SM_T5_StovePipe")                       # rusty stove flue with a cap (barracks roofs, user photo 1)
    p.box(-0.14, 0.14, -0.14, 0.14, 0.0, 1.5, "Metal")
    p.box(-0.1, 0.1, -0.1, 0.1, 1.5, 2.2, "Metal")
    p.box(-0.22, 0.22, -0.22, 0.22, 2.2, 2.32, "Metal")
    parts[p.name] = p
    p = Part("SM_T5_LoggiaGlazing")                   # residents' own timber glazing on the loggia parapet
    for x in (0.1, 0.8, 1.5, 2.2, 2.85):
        p.box(x, x + 0.05, -1.17, -1.12, 1.0, ST - 0.14, "Wood")
    p.box(0.1, 2.9, -1.17, -1.12, ST - 0.2, ST - 0.14, "Wood")
    p.box(0.1, 2.9, -1.17, -1.12, 1.0, 1.05, "Wood")
    parts[p.name] = p
    p = Part("SM_T5_LoggiaGlazingGlass")              # only some panes left
    for x0, x1 in ((0.15, 0.8), (1.55, 2.2)):
        p.box(x0, x1, -1.15, -1.146, 1.05, ST - 0.2, "Glass")
    parts[p.name] = p
    p = Part("SM_T5_LoggiaClutter")                   # left behind: a crate, leaning boards, a washing line
    p.box(2.1, 2.6, -0.9, -0.5, 0.0, 0.4, "Furniture")
    for k in range(3):
        p.box(0.2 + k * 0.12, 0.3 + k * 0.12, -0.15, -0.1, 0.0, 1.6 - k * 0.2, "Wood")
    p.box(0.1, 2.9, -0.62, -0.61, 1.9, 1.91, "BlackPlastic")
    parts[p.name] = p
    for L in (1.6, 3.2, 4.8):                         # loose cable hanging down the facade
        p = Part("SM_T5_Cable_%d" % int(L * 10))
        p.box(-0.008, 0.008, -0.1, -0.084, -L, 0, "BlackPlastic")
        parts[p.name] = p

    for name, mat in (("SM_T5_CurtainRag_Red", "CurtainRed"), ("SM_T5_CurtainRag_Tulle", "Paper")):
        p = Part(name)
        curtain_rag(p, ox, ow, oz0, oz1, mat)
        parts[p.name] = p

    # entrance: door opening 1.2 x 2.2 m centred, concrete canopy slab, steps (photo 6480281023);
    # the "Open" variant has no door leaf and is used where an interior section can be entered
    for name, leaf in (("SM_T5_Entrance_A_Aged", True), ("SM_T5_Entrance_Open_A_Aged", False)):
        p = Part(name)
        entrance(p, leaf)
        parts[p.name] = p

    p = Part("SM_T5_PlinthBand_A_Aged")
    p.box(0, AX, -0.02, T, 0, G["plinth_band"], "Concrete")
    parts[p.name] = p

    # closed crawl-space skirt with one vent per axis, reaching BURY below grade so sloping terrain never shows a
    # gap: an open crawl space read as a building hovering on stilts (ANNAHME, user feedback 2026-11-07)
    p = Part("SM_T5_Skirt_A_Aged")
    ch, vx0, vx1, vz0, vz1 = G["pile"]["crawl_height"], AX / 2 - 0.2, AX / 2 + 0.2, 0.45, 0.65
    p.box(0, AX, 0.02, 0.2, -BURY, vz0, "Concrete")
    p.box(0, vx0, 0.02, 0.2, vz0, vz1, "Concrete")
    p.box(vx1, AX, 0.02, 0.2, vz0, vz1, "Concrete")
    p.box(0, AX, 0.02, 0.2, vz1, ch, "Concrete")
    parts[p.name] = p

    pile = G["pile"]["size"]
    p = Part("SM_T5_Pile_A_Aged")
    p.box(0, pile, 0, pile, -BURY, G["pile"]["crawl_height"], "Concrete")
    p.box(-0.05, pile + 0.05, -0.05, pile + 0.05, G["pile"]["crawl_height"] - 0.1, G["pile"]["crawl_height"], "Concrete")
    parts[p.name] = p

    p = Part("SM_T5_RoofEdge_A_Aged")
    p.box(J / 2, AX - J / 2, 0, T, 0, G["parapet"], "Facade")
    p.box(0, AX, -0.05, T + 0.05, G["parapet"], G["parapet"] + 0.03, "Metal")       # flashing cap
    parts[p.name] = p

    # roof/floor slab covering one axis x one axis (tiled over the footprint)
    p = Part("SM_T5_Slab_A_Aged")
    p.box(0, AX, 0, AX, -0.22, 0, "Concrete")
    parts[p.name] = p

    # bay window (Erker) projecting 0.75 m over one axis and one storey; windows on the front (photo 6480312099)
    p = Part("SM_T5_Bay_A_Aged")
    proj, side = 0.75, 0.12
    p.box(0.1, 0.1 + side, -proj, 0.0, 0.0, ST, "Facade")                       # side cheeks
    p.box(AX - 0.1 - side, AX - 0.1, -proj, 0.0, 0.0, ST, "Facade")
    bw = AX - 0.2 - 2 * side
    bx = 0.1 + side
    p.box(bx, bx + bw, -proj, -proj + T * 0.6, 0.0, WIN["sill"], "Facade")       # front parapet
    p.box(bx, bx + bw, -proj, -proj + T * 0.6, WIN["sill"] + WIN["height"], ST, "Facade")
    p.box(0.1, AX - 0.1, -proj, 0.0, ST - 0.12, ST, "Facade")                   # slab edge
    f = 0.06
    for k in range(4):  # three-part window, mullions
        x = bx + k * bw / 3
        p.box(x - f / 2, x + f / 2, -proj + 0.05, -proj + 0.11, WIN["sill"], WIN["sill"] + WIN["height"], "Wood")
    p.box(bx, bx + bw, -proj + 0.05, -proj + 0.11, WIN["sill"], WIN["sill"] + f, "Wood")
    p.box(bx, bx + bw, -proj + 0.05, -proj + 0.11, WIN["sill"] + WIN["height"] - f, WIN["sill"] + WIN["height"], "Wood")
    parts[p.name] = p

    # loggia: balcony door + window in the panel, projecting slab with a lime parapet (photo 6480281023)
    p = Part("SM_T5_Loggia_A_Aged")
    dx0, dx1 = 0.35, 2.65
    panel_with_opening(p, AX, ST, dx0, dx1 - dx0, J / 2, 2.2, "Facade")
    p.box(dx0, dx0 + 0.9, 0.12, 0.17, J / 2, 2.2, "Wood")                          # balcony door
    p.box(dx0 + 0.9, dx1, 0.12, 0.17, J / 2, 0.85, "Facade")                       # window parapet behind the loggia
    for x in (dx0 + 0.9, dx0 + 1.6, dx1 - 0.05):
        p.box(x - 0.03, x + 0.03, 0.12, 0.17, 0.85, 2.2, "Wood")                  # window frame posts
    p.box(0.0, AX, -1.2, 0.0, -0.12, 0.0, "Concrete")                             # projecting slab
    p.box(0.0, AX, -1.2, -1.1, 0.0, 1.0, "Parapet")                               # front parapet
    for x0 in (0.0, AX - 0.1):
        p.box(x0, x0 + 0.1, -1.2, 0.0, 0.0, 1.0, "Parapet")                       # side parapets
    parts[p.name] = p

    # school facade module (photo 6480300155 / briefing R3): large window between projecting vertical fins
    p = Part("SM_T5_SchoolWindow_A_Aged")
    sox, sow, soz0, soz1 = 0.45, 2.1, 0.6, 2.55
    panel_with_opening(p, AX, ST, sox, sow, soz0, soz1, "Facade")
    p.box(0.0, 0.3, -0.35, 0.0, 0.0, ST, "Fin")                                   # fin on the left edge of the axis
    fw = 0.06
    for k in range(4):
        x = sox + k * sow / 3
        p.box(x - fw / 2, x + fw / 2, 0.12, 0.17, soz0, soz1, "Wood")
    for z in (soz0, soz0 + (soz1 - soz0) * 0.62, soz1):
        p.box(sox, sox + sow, 0.12, 0.17, z - fw / 2, z + fw / 2, "Wood")
    parts[p.name] = p

    p = Part("SM_T5_RoofVent_A_Aged")  # ventilation block on the roof (photos: chimney-like stacks per section)
    p.box(0, 0.9, 0, 0.6, 0, 1.3, "Facade")
    p.box(-0.05, 0.95, -0.05, 0.65, 1.3, 1.36, "Metal")
    parts[p.name] = p

    p = Part("SM_T5_Corner_A_Aged")  # covers the outer corner joint over one storey
    p.box(-0.04, 0.0, -0.04, T, 0, ST, "Facade")
    p.box(-0.04, T, -0.04, 0.0, 0, ST, "Facade")
    parts[p.name] = p
    return parts


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    os.makedirs(OUT, exist_ok=True)
    manifest = {"grid": G, "parts": {}}
    for name, part in make_parts().items():
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob, do_unlink=True)
        ob = part.build()
        bpy.ops.object.select_all(action="DESELECT")
        ob.select_set(True)
        bpy.context.view_layer.objects.active = ob
        path = os.path.join(OUT, name + ".fbx")
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True, apply_unit_scale=True,
                                 apply_scale_options="FBX_SCALE_UNITS", mesh_smooth_type="FACE", colors_type="SRGB",
                                 add_leaf_bones=False, bake_anim=False)
        xs, ys, zs = zip(*part.verts)
        manifest["parts"][name] = {"tris": len(part.faces) * 2, "materials": part.mats,
                                   "bounds_m": [[min(xs), min(ys), min(zs)], [max(xs), max(ys), max(zs)]]}
    json.dump(manifest, open(os.path.join(OUT, "kit_manifest.json"), "w"), indent=1)
    print("KIT OK", len(manifest["parts"]), "parts ->", OUT)


if __name__ == "__main__":
    main()
