"""Furnished residential landings. Fictional households; keep the central circulation clear."""
import math
import random
import furniture as fu
import interiors as ins
import story_rooms

# label: (accessible floors including ground, existing ground-floor story, household sequence)
HOUSES = {
    'PLA_Lenina_8': (3,'lenina8',('teacher','nurse','family','seamstress')),
    'PLA_Lenina_7': (3,'lenina7',('technician','retired','teacher','family')),
    'PLA_SAT_S_Block': (2,'family',('retired','seamstress')),
    'PLA_Shkolnaya_4': (2,'homes',('nurse','family','teacher','technician')),
    'PLA_Shkolnaya_6': (2,'homes',('retired','seamstress','nurse','family')),
}
THEMES = ('teacher','nurse','family','seamstress','technician','retired')


def vessel(F,x,y,z,r=.05,h=.12,mat='Enamel'):
    """Open cup/vase with a rim and an inner wall, rather than a solid cylinder."""
    count=18
    verts=[]
    for radius,height in ((r*.8,z),(r,z+h),(r-.008,z+h),(r*.8-.008,z+.012)):
        verts.extend((x+radius*math.cos(k*math.tau/count),y+radius*math.sin(k*math.tau/count),height) for k in range(count))
    faces=[]
    for ring in range(3):
        for k in range(count):
            j=(k+1)%count
            faces.append((ring*count+k,ring*count+j,(ring+1)*count+j,(ring+1)*count+k))
    faces.append(tuple(3*count+k for k in range(count)))
    faces.append(tuple(reversed(range(count))))
    fu.surface(F.place(0,0),verts,faces,mat)


def books(P,count=6,z=.74):
    for k in range(count):
        h=.17+.025*(k%3)
        P.box(k*.045,k*.045+.032,0,.14,z,z+h,('Carpet','Paper','WoodGrey')[k%3])


def home(F,theme,seed=0):
    """Shared plumbing plan, distinct use of the living room and small personal traces per household."""
    y0,y1=F.y0,F.y1
    fu.sofa(F.place(-5.88,3.6,3),2.0,cushions=2,slumped=theme=='retired')
    fu.blanket(F.place(-5.88,3.6,3),.15,1.0,.2,.7,.54)
    fu.bookshelf(F.place(-.12,.65,1),.95,fill=.9 if theme=='teacher' else .45)
    fu.tv(F.place(-.12,2.0,1))
    fu.table(F.place(-4.35,2.0),1.05,.6,h=.46)
    fu.rug(F,-4.8,-1.1,1.35,3.9)
    for x in (-5.2,-2.2):
        ins.radiator(F.box,x,x+1.4,y0+.05)
        fu.curtains(F,x,x+1.4,y0,1,drawn=.18+(seed%3)*.09)
    if theme in ('teacher','seamstress','technician'):
        desk=F.place(-3.9,.48)
        fu.table(desk,1.35,.62)
        fu.chair(F.place(-3.25,1.35,2))
        if theme=='teacher':
            books(desk,8)
            for k in range(4): desk.box(.55,.95,.15,.42,.74+k*.008,.746+k*.008,'Paper')
            fu.lamp(desk,1.1,.25,.74)
        elif theme=='seamstress':
            fu.sewing_machine(F.place(-3.8,.62))
            fu.blanket(desk,.85,1.3,.12,.55,.75,.2)
            for k in range(4): desk.cyl(.95+k*.07,.52,.75,.82,.025,'CurtainRed')
        else:
            desk.box(.12,.7,.12,.5,.74,1.0,'Furniture')
            for k in range(5): desk.cyl(.2+k*.09,.08,.79,.81,.025,'BlackPlastic')
            desk.hcyl_u(.8,1.12,.3,.77,.016,'Metal')
            for k in range(3): desk.box(.9,1.1,.42,.45,.75+k*.035,.77+k*.035,'Metal')
            books(F.place(-2.95,.55),3)
    else:
        if theme!='nurse': fu.armchair(F.place(-3.4,.55))
        vessel(F,-3.95,2.3,.46,.055,.1)
    if theme=='family':
        F.box(-4.0,-3.2,11.25,11.6,0,.38,'Furniture')
        for k in range(6):
            F.cyl(-3.85+k*.09,11.43,.38,.4+.04*(k%3),.035,'Mural_Red')
    elif theme=='retired':
        F.box(-5.94,-5.92,1.1,1.7,1.1,1.55,'Furniture')
        F.box(-5.915,-5.91,1.14,1.66,1.14,1.51,'Paper')
        vessel(F,-4.0,2.3,.46,.06,.17)
    elif theme=='nurse':
        desk=F.place(-3.7,.5)
        fu.table(desk,1.05,.55)
        desk.box(.1,.6,.1,.45,.74,1.0,'Enamel')
        desk.box(.29,.4,.095,.1,.79,.95,'Mural_Red')
        desk.box(.22,.47,.095,.1,.84,.89,'Mural_Red')
        for k in range(3): vessel(F,-2.95+k*.08,.85,.74,.025,.1,'Glass')
    # Bedroom: bed against party wall; uninterrupted approach from the hall door.
    fu.bed(F.place(-5.85,10.65,3),.95 if theme in ('teacher','nurse','retired') else 1.35,1.95,made=theme!='technician')
    fu.nightstand(F.place(-5.85,11.28,3),drawer_out=theme=='retired')
    fu.wardrobe(F.place(-5.9,ins.BACK+.12),1.15,open_leaf=False)
    ins.radiator(F.box,-5.2,-3.8,y1-.17)
    fu.curtains(F,-5.2,-3.8,y1,-1,drawn=.25)
    # Kitchen: contiguous work triangle on the plumbing wall; table beside the window.
    fu.fridge(F.place(-.1,ins.BACK+.15,1))
    fu.stove(F.place(-.1,ins.BACK+.86,1),pot=theme=='family',kettle=True)
    fu.kitchen_run(F.place(-.1,ins.BACK+1.52,1),1.8,sink_at=1.15)
    fu.table(F.place(-2.8,10.8),1.05,.65)
    fu.chair(F.place(-2.3,10.25,0))
    vessel(F,-2.5,11.1,.74)
    F.cyl(-2.15,11.1,.74,.76,.12,'Enamel')
    if theme=='family': vessel(F,-2.0,11.35,.74,.04,.085)
    for k in range(3): vessel(F,-.42,9.25+k*.2,.89,.055,.13,'Glass')
    ins.radiator(F.box,-2.2,-.8,y1-.17)
    # Entrance storage stays between, rather than in front of, the two rear doorways.
    F.box(-2.85,-1.95,7.07,7.32,0,.34,'Furniture')
    F.box(-2.85,-1.95,7.31,7.35,1.6,1.67,'Wood')
    for k in range(4): F.box(-2.75+k*.19,-2.72+k*.19,7.24,7.31,1.55,1.64,'Metal')
    bath=F.place(-5.92,ins.BATH_SPLIT-.1,3)
    fu.bathtub(bath,1.4)
    fu.washbasin(F.place(-4.6,ins.BATH_SPLIT-.08,2))
    fu.toilet(F.place(-5.92,6.5,3))
    F.box(-5.93,-5.91,5.0,5.45,1.2,1.65,'Glass')
    # Thin dust/debris stays at wall edges, outside door and stair circulation.
    for k in range(10):
        F.box(-5.8,-5.65,.55+k*.28,.66+k*.28,.013,.018,'Paper')


def append_floor(part,other,z):
    base,first=len(part.verts),len(part.faces)
    part.verts.extend((x,y,zz+z) for x,y,zz in other.verts)
    part.smooth_faces.update(first+i for i in other.smooth_faces)
    for face,mi in zip(other.faces,other.face_mat):
        mat=other.mats[mi]
        if mat not in part.mats: part.mats.append(mat)
        part.faces.append(tuple(base+i for i in face));part.face_mat.append(part.mats.index(mat))


def build(part,label,AX,ST,T,seed=8):
    floors,kind,themes=HOUSES[label]
    if kind=='homes':
        result=None
        first=0
    else:
        result=story_rooms.ROOMS[kind](part,AX,ST,T,seed)
        first=1
    views=[]
    for level in range(first,floors):
        p=type(part)('floor')
        S=ins.Section(p,ST-.22,random.Random(seed+level*17))
        y0,y1=T,ins.DEEP*AX-T
        ins.stairwell(S,AX,ST,y0,y1,connects_up=level<floors-1,has_lower=level>0)
        for side in range(2):
            theme=themes[(level-first)*2+side]
            F=ins.flat_shell(S,AX,y0,y1,bool(side),'Wallpaper_Rose' if side else 'Wallpaper_Green','Wallpaper_Green')
            home(F,theme,seed+level+side)
            X=F.X
            for room,x,y in (('living',-1.8,3.5),('kitchen',-1.6,9.7),('bedroom',-3.5,9)):
                views.append((f'floor{level}-flat{side+1}-{theme}-{room}',(X(x),y),(X(x-1),y+.3),level))
        append_floor(part,p,level*ST)
        if result is None:
            result=S
        else:
            result.lights.extend((x,y,z+level*ST) for x,y,z in S.lights)
    result.extra_views=views
    result.furnished_floors=floors
    return result
