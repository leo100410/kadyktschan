import copy
import math
import unittest
from neighbourhood_update import densify,blocked_doors


class NeighbourhoodTest(unittest.TestCase):
    def test_new_growth_keeps_roads_doors_and_reserved_sites_clear(self):
        layout={'roads':[{'width_m':6,'points_m':[[-2600,0,0],[2600,0,0]]}],
                'rivers':[],'buildings':[dict(east_m=100,north_m=100,axis_deg_from_east=0,length_m=30,width_m=12)]}
        manifest=[dict(label='PLA_Lenina_8',ground_m=0,entrances=[[86,100,0]],section_frame=[[92,98.5],[0,1],[1,0]])]
        power=dict(east_m=340,north_m=75)
        old={'larch':[[500,500,0,0,1]],'grass':[],'pipes':[]}
        data=densify(copy.deepcopy(old),layout,manifest,lambda e,n:e*.01+n*.02,power,(-680,975),targets=(160,60,30))
        count=0
        for kind in ('larch','birch','sapling','willow','alder','low_willow','shrub'):
            for e,n,z,*_ in data.get(kind,[]):
                if (e,n)==(500,500):continue
                count+=1
                self.assertGreater(abs(n),5)
                self.assertGreater(math.hypot(e-100,n-86),7.9)
                self.assertGreater(math.hypot(e-340,n-75),18)
                self.assertGreater(math.hypot(e+680,n-975),79)
                self.assertAlmostEqual(z,e*.01+n*.02,delta=.001)
        self.assertGreater(count,230)
        self.assertEqual(data,densify(copy.deepcopy(data),layout,manifest,lambda e,n:0,power,None,targets=(160,60,30)))

    def test_only_selected_furnished_entrance_stays_open(self):
        manifest=[dict(label='PLA_Lenina_8',ground_m=2,entrances=[[0,0,0],[0,20,0]],section_frame=[[6,18.5],[0,1],[1,0]]),
                  dict(label='Unfurnished',ground_m=0,entrances=[[100,100,0]],section_frame=None)]
        doors=blocked_doors(manifest)
        self.assertEqual(len(doors),2)
        self.assertAlmostEqual(doors[0][1],6.08)
        self.assertFalse(any(abs(d[0]-20)<.1 for d in doors))
        self.assertTrue(any(abs(d[0]-100)<.1 for d in doors))


if __name__=='__main__':unittest.main()
