import unittest
from grassfire.collapse import compute_event_3triangle, find_gt,\
    visualize_collapse
from grassfire.primitives import KineticTriangle, KineticVertex

# class TestCollapseTime(unittest.TestCase):
#     def setUp(self):
#         #self.now = 0.0799482915
#         self.now = 0
#         self.triangle = KineticTriangle(KineticVertex((0.18574272786037482, 0.9621202327084679), (-0.7210435840113663, 0.7020586318694141), (-0.6335421012191131, 0.7737082176007122), (-0.7903334526709827, 0.6126769406376933)),
#             KineticVertex((0.1976185358758889, 0.9774396412411114), (-0.8695871963603679, 0.5104421726342845), (-0.7903334526709827, 0.6126769406376933), (-0.9202181035144049, 0.39140598100227336)),
#             KineticVertex((0.2026483516483515, 0.9892650290885584), (-0.9322352367623578, 0.36315300556537816), (-0.9202181035144049, 0.39140598100227336), (-0.9424964967844317, 0.3342160282647643)), None, True, None)
# 
#         for t in [0., 0.0799]:#, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.0947089087]:
#              visualize_collapse(self.triangle,T=t)
# #             raw_input(str(t) + ' paused')
# 
#     def test_bug(self):
#         evt = compute_event_2triangle(self.triangle, now=self.now, sieve=find_gt)
#         print evt


class TestCollapseTime(unittest.TestCase):
    def setUp(self):
        #self.now = 0.134576326
        self.now = 0
        self.triangle = KineticTriangle(KineticVertex((-5.586845556126167, 12.264500723992885), (42.96862677742887, -96.56675461024079), (-0.9097484670494593, -0.4151598808906743), (0.9174410515320596, 0.39787173431113276)),
            KineticVertex((0.07562289915966396, -0.792423319327731), (0.892367111503632, 0.45568901541445345), (0.9174410515320596, 0.39787173431113276), (0.8602330667847619, 0.5099010402127879)),
            KineticVertex((1.3619372870019553, -2.9625114016712693), (-8.665884533180343, 16.58102212313996), (0.8602330667847619, 0.5099010402127879), (-0.9097484670494593, -0.4151598808906743)), None, None, None)

        for t in [0., 0.13]:#, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.0947089087]:
             visualize_collapse(self.triangle,T=t)
#             raw_input(str(t) + ' paused')

    def test_bug(self):
        evt = compute_event_3triangle(self.triangle, now=self.now, sieve=find_gt)
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