import unittest
from math import sqrt
from grassfire.collapse import compute_event
from grassfire.primitives import KineticTriangle, KineticVertex, InfiniteVertex
from tri.delaunay import cw, ccw, orient2d
from grassfire.calc import near_zero, all_close_clusters

import logging

class TestCollapseTime1Triangle(unittest.TestCase):
    """Split event, apex crashing into base"""
    def setUp(self):
        k = KineticTriangle()

        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., 1.)

        d = KineticVertex()
        d.origin = (10., 0.)
        d.velocity = (0, 1.)

        # vertex supposed to crash into base (the apex)
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (0., -1.)

        k.vertices = [o, d, a]
        k.neighbours = [True, True, None]
        self.tri = k

    def test_1triangle_split(self):
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        print evt
        assert evt.event_tp == "split"

class Test1TriangleFlipA(unittest.TestCase):
    """Flip event, apex misses the base"""
    def setUp(self):
        k = KineticTriangle()
        # base
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., 1.)
        #
        d = KineticVertex()
        d.origin = (4., 0.)
        d.velocity = (0, 1.)
        # vertex missing the base
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (2, -2.)
        k.vertices = [o, d, a]
        k.neighbours = [True, True, None]
        self.tri = k

    def test_1triangle_flip(self):
        # edge that has to flip == (apex, orig)
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        print evt
        print self.tri.str_at(0)
        assert evt.event_tp == "flip"
        assert evt.sides == (1,)


class Test1TriangleCollapseA(unittest.TestCase):
    """Collapse event, apex hits the destination"""
    def setUp(self):
        k = KineticTriangle()
        # base
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., 1.)
        #
        d = KineticVertex()
        d.origin = (4., 0.)
        d.velocity = (0, 1.)
        # vertex missing the base
        a = KineticVertex()
        a.origin = (4., 5.)
        a.velocity = (0, -2.)
        k.vertices = [o, d, a]
        k.neighbours = [True, True, None]
        self.tri = k
    def test_1triangle_collapse(self):
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        print evt
        print self.tri.str_at(0)
        assert evt.event_tp == "collapse"
        assert evt.how == "line"
        assert evt.sides == (0,)


class Test1TriangleCollapseB(unittest.TestCase):
    """Collapse event, apex hits the origin"""
    def setUp(self):
        k = KineticTriangle()
        # base
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., 1.)
        #
        d = KineticVertex()
        d.origin = (4., 0.)
        d.velocity = (0, 1.)
        # vertex missing the base
        a = KineticVertex()
        a.origin = (0., 5.)
        a.velocity = (0, -2.)
        k.vertices = [o, d, a]
        k.neighbours = [True, True, None]
        self.tri = k
    def test_1triangle_collapse(self):
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        print evt
        print self.tri.str_at(0)
        assert evt.event_tp == "collapse"
        assert evt.how == "line"
        assert evt.sides == (1,)


class Test1TriangleCollapseC(unittest.TestCase):
    """Collapse event, origin hits destination."""
    def setUp(self):
        k = KineticTriangle()
        # base
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (1., 1.)
        #
        d = KineticVertex()
        d.origin = (4., 0.)
        d.velocity = (-1, 1.)
        # vertex missing the base
        a = KineticVertex()
        a.origin = (0., 25.)
        a.velocity = (0, 2)
        k.vertices = [o, d, a]
        k.neighbours = [True, True, None]
        self.tri = k
    def test_1triangle_collapse(self):
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        print "**", evt
        print self.tri.str_at(0)
        assert evt.event_tp == "collapse"
        assert evt.how == "line"

class Test1TriangleCollapseD(unittest.TestCase):
    """Collapse event, origin hits destination."""
    def setUp(self):
        k = KineticTriangle()
        # base
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (1., 1.)
        #
        d = KineticVertex()
        d.origin = (4., 0.)
        d.velocity = (-1, 1.)
        # vertex missing the base
        a = KineticVertex()
        a.origin = (0., 25.)
        a.velocity = (0, -0.01)
        k.vertices = [o, d, a]
        k.neighbours = [True, True, None]
        self.tri = k
    def test_1triangle_collapse(self):
        evt = compute_event(self.tri, now=0.)
        assert evt != None
        print "**", evt
        print self.tri.str_at(0)
        assert evt.event_tp == "collapse"
        assert evt.how == "line"


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