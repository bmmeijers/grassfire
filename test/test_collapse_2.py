import unittest
from math import sqrt
from grassfire.collapse import compute_event
from grassfire.primitives import KineticTriangle, KineticVertex, InfiniteVertex
from tri.delaunay import cw, ccw, orient2d
from grassfire.calc import near_zero, all_close_clusters

import logging

class TestCollapseTime2Triangle(unittest.TestCase):
    def setUp(self):
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (2.1889010593167346, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (-2.1889010593167346, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.5, 1.7320508075688772)
        v.velocity = (0.0, -1.5275252316519463)
        V.append(v)
        k.vertices = V
        k.neighbours = [None, None, True]
        self.tri = k

    def test_equilateral(self):
        evt = compute_event(self.tri)
        assert evt != None
        assert evt.time == 0.6852753776217848091789620, "{:.25f}".format(evt.time)
        assert evt.how == "point"
        assert evt.event_tp == "collapse"
        assert evt.where == (1.5, 0.6852753776217849)

class TestCollapseTime2TriangleOutwards(unittest.TestCase):
    def setUp(self):
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (-2.1889010593167346, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (2.1889010593167346, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.5, 1.7320508075688772)
        v.velocity = (0.0, 1.5275252316519463)
        V.append(v)
        k.vertices = V
        k.neighbours = [None, None, True]
        self.tri = k

    def test_equilateral(self):
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        # FIXME: WRONG, should be ignored (as is in the past)
        assert evt.time == None

    def test_equilateral_past(self):
        evt = compute_event(self.tri, now=-10.)
        assert evt != None
        # FIXME: WRONG, should be ignored (as is in the past)
        assert evt.time == -0.6852753776217849202012644
#         assert evt.how == "point"
#         assert evt.event_tp == "collapse"
#         assert evt.where == (1.5, 0.6852753776217849)

def _enable_logging():
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def perform_one():
#     tst = TestCollapseSameTime("test_equal_sides")
#     tst = TestEvent1Edge("test_0tri")
#     tst = VertexCrash("test_equilateral_outwards")
    # tst = TestCollapseTime0TriangleSegment("test_0triangle_segment")
    tst = TestCollapseTime0TriangleSpoke("test_0triangle_spoke")
#     tst = TestCollapseTime0TrianglePoint("test_0triangle_point")
#     tst = TestEvent1Edge("test_0tri")
#     tst = EdgeCollapse("test_crossing")
#     tst = EdgeCollapse("test_parallel_follower")
    suite = unittest.TestSuite()
    suite.addTests([tst])#, tst1])
    runner = unittest.TextTestRunner()
    runner.run(suite)


if __name__ == '__main__':
#     _enable_logging()
    unittest.main()
#     perform_one()