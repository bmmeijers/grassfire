import unittest
from grassfire.collapse import compute_event_1triangle, find_gt,\
    visualize_collapse
from grassfire.primitives import KineticTriangle, KineticVertex

class TestCollapseTime(unittest.TestCase):
    def setUp(self):
        self.triangle = KineticTriangle(
          KineticVertex((-0.10754127621601216, -0.8518518518525637), (1.1277743405217686, -0.8539125853201076)),
          KineticVertex((-0.10754127621545964, -0.8518518518560583), (1.1227962916920335, -0.8545992124818665)),
          KineticVertex((0.09433524838987582, -0.9500459243279002), (-1.0906702065440808, 0.8568264443105804)),
          True, True, None)
        self.now = 0.01350521350551394522687687072

        for t in [0.]:#, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.0947089087]:
             visualize_collapse(self.triangle,T=t)
#             raw_input(str(t) + ' paused')

    def test_bug7(self):
        """ Tests to handle 
        https://bitbucket.org/bmmeijers/grassfire/issues/7/incorrect-event-time-calculation-leads-to
        """
        evt = compute_event_1triangle(self.triangle, now=self.now, sieve=find_gt)
        print evt
        assert evt.time == 0.06249672560618784
        assert 0.06044641870187 < evt.time < 0.062569415


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