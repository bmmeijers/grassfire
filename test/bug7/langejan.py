import unittest
from grassfire.collapse import compute_event_1triangle, find_gt,\
    visualize_collapse
from grassfire.primitives import KineticTriangle, KineticVertex

class TestCollapseTime(unittest.TestCase):
    def setUp(self):
        self.triangle = KineticTriangle(KineticVertex((0.7535965796935182, 0.41537586304902124), 
                                                      (1.20214406777568, -0.6838702949507468), 
                                                      (0.9700438684136995, 0.24292981157730573), 
                                                      (0.28688406971441127, -0.957965307589005)),
                                        KineticVertex((0.793056201639544, 0.32270148647248165),
                                                      (-0.13094220113388658, 1.1449829817969648),
                                                      (0.39524394070149405, 0.9185761957174559),
                                                      (-0.592426467909283, 0.8056245280032946)),
                                        KineticVertex((0.7872824597246767, 0.3184556903101898),
                                                      (0.12436918194296205, 1.3327295257957255),
                                                      (-0.592426467909283, 0.8056245280032946),
                                                      (0.731259583557203, 0.682099275366677)),
                                        None, True, True)

        self.now = 0.04331079000480406865358773416

        for t in [0.]:#, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.0947089087]:
             visualize_collapse(self.triangle,T=t)
#             raw_input(str(t) + ' paused')

    def test_bug_flip(self):
        evt = compute_event_1triangle(self.triangle, now=self.now, sieve=find_gt)
        print evt

if __name__ == "__main__":
    if True:
        import logging
        import sys
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
#         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
 
    unittest.main(verbosity=2)