import unittest
from grassfire.collapse import compute_event_2triangle, find_gt,\
    visualize_collapse
from grassfire.primitives import KineticTriangle, KineticVertex

class TestCollapseTime(unittest.TestCase):
    def setUp(self):
        self.triangle = KineticTriangle(
            KineticVertex((-0.583221775992843, -0.7777777777791053), 
                          (0.8502422723435449, 1.1193719054708335), 
                          (-0.12933918403800038, 0.9916004111901044), 
                          (0.9899494936613725, 0.14142135623586805)),
            KineticVertex((-0.5850066934405151, -0.7608210620269993), 
                          (1.1278459170135144, -0.8613604025707853), 
                          (0.9906788398454419, 0.1362183404776662), 
                          (0.12933918403880518, -0.9916004111899995)),
            KineticVertex((-69008181994845.11, -8996100425594.38), 
                          (8097106551877965.0, 1055561552148527.8), 
                          (0.12933918403880518, -0.9916004111899995), 
                          (-0.12933918403800038, 0.9916004111901044)), None, None, True)
        self.now = 0.008522573039234542999209587322

        for t in [0.]:#, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.0947089087]:
             visualize_collapse(self.triangle,T=t)
#             raw_input(str(t) + ' paused')

    def test_bug7(self):
        """ Tests to handle 
        https://bitbucket.org/bmmeijers/grassfire/issues/7/incorrect-event-time-calculation-leads-to
        """
        evt = compute_event_2triangle(self.triangle, now=self.now, sieve=find_gt)
        print evt
#         assert evt.time == 0.06249672560618784
#         assert 0.06044641870187 < evt.time < 0.062569415


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