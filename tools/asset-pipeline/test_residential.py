"""Offline collision-clearance checks for the new room layouts and stacked stair geometry."""
import math
import random
import unittest
from test_furniture import Part
import test_furniture as furniture_checks
from interiors import Section, flat_shell, stairwell, DEEP
from residential import home, build, HOUSES, THEMES, vessel


def bounds(part):
    boxes=[]
    for face,mat in zip(part.faces,part.face_mat):
        v=[part.verts[i] for i in face]
        lo=tuple(min(p[a] for p in v) for a in range(3));hi=tuple(max(p[a] for p in v) for a in range(3))
        boxes.append((lo,hi,part.mats[mat]))
    return boxes


def obstruction(boxes,x,y,z):
    for lo,hi,mat in boxes:
        if hi[2]<=z+.35 or lo[2]>=z+1.92:continue
        dx=max(lo[0]-x,0,x-hi[0]);dy=max(lo[1]-y,0,y-hi[1])
        if dx*dx+dy*dy<.34**2-1e-7:return (lo,hi,mat)
    return None


def samples(route):
    for a,b in zip(route,route[1:]):
        count=max(1,math.ceil(math.dist(a,b)/.14))
        for k in range(count+1):yield tuple(a[i]+(b[i]-a[i])*k/count for i in range(3))


class ResidentialTest(unittest.TestCase):
    def test_open_vessels_are_closed_and_mirror_outward(self):
        from interiors import FlatView
        for mirror in (False,True):
            p=Part('cup');F=FlatView(Section(p,2.58,random.Random(8)),3,mirror)
            vessel(F,-2,9,.74)
            furniture_checks.FurnitureTest().assert_closed(p)

    def test_six_households_keep_room_doorways_and_routes_clear(self):
        for theme in THEMES:
            for mirror in (False,True):
                p=Part('flat');S=Section(p,2.58,random.Random(8))
                F=flat_shell(S,3,.3,11.7,mirror,'Wallpaper_Rose','Wallpaper_Green')
                home(F,theme)
                boxes=bounds(p)
                routes=[[(.5,5.05),(-1.9,5.05),(-1.75,4.9),(-1.75,3.5),(-2.7,2.9)],
                        [(-1.9,5.05),(-2.5,5.05),(-4.65,5.05)],
                        [(-2.5,5.05),(-2.5,6.7),(-4.7,6.7)],
                        [(-2.5,6.4),(-3.5,6.8),(-3.5,8.7),(-3.5,10)],
                        [(-2.5,6.4),(-1.15,6.7),(-1.15,8),(-1.2,9.5)]]
                for route in routes:
                    for x,y,z in samples([(F.X(x),y,.012) for x,y in route]):
                        self.assertIsNone(obstruction(boxes,x,y,z),(theme,mirror,(x,y,z),obstruction(boxes,x,y,z)))
                self.assertTrue(all(math.isfinite(c) for point in p.verts for c in point))

    def test_upper_landing_does_not_seal_return_stair(self):
        p=Part('stairs')
        from residential import append_floor
        for floor in range(3):
            q=Part('floor');S=Section(q,2.58,random.Random(8))
            stairwell(S,3,2.8,.3,11.7,floor<2,floor>0)
            append_floor(p,q,floor*2.8)
        boxes=bounds(p)
        for floor in (0,1):
            z=floor*2.8
            route=[(.72,6.35,z)]
            route += [(.72,6.6+(k+.5)*.28,z+(k+1)*1.4/9) for k in range(9)]
            route +=[(.72,9.55,z+1.4),(2.25,9.55,z+1.4)]
            route +=[(2.25,9.12-(k+.5)*.28,z+1.4+(k+1)*1.4/9) for k in range(9)]
            route +=[(2.25,6.35,z+2.8),(2.25,5.8,z+2.8),(1.5,5.05,z+2.8)]
            for x,y,zz in samples(route):
                self.assertIsNone(obstruction(boxes,x,y,zz),(x,y,zz,obstruction(boxes,x,y,zz)))

    def test_all_five_houses_build_with_real_upper_storeys(self):
        for label,(floors,kind,themes) in HOUSES.items():
            p=Part(label);result=build(p,label,3,2.8,.3)
            self.assertEqual(result.furnished_floors,floors)
            self.assertTrue(any(v[2]>(floors-1)*2.8+2 for v in p.verts))
            self.assertEqual(len(result.extra_views),6*(floors-(kind!='homes')))
            self.assertTrue(all(0<=i<len(p.verts) for face in p.faces for i in face))
            self.assertEqual(len(p.faces),len(p.face_mat))


if __name__=='__main__':unittest.main()
