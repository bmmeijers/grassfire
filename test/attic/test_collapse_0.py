import unittest
from math import sqrt
from grassfire.collapse import compute_event
from grassfire.primitives import KineticTriangle, KineticVertex, InfiniteVertex
from tri.delaunay import cw, ccw, orient2d
from grassfire.calc import near_zero, all_close_clusters

import logging

class TestCollapseTime0TriangleSegment(unittest.TestCase):
    def setUp(self):
        """Initialize 3 infinite triangles and 1 finite 3-triangle.
        """
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0., 0)
        v.velocity = (1., 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (10., 0)
        v.velocity = (-1., 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.,15.)
        v.velocity = (0, -1.)
        V.append(v)
        k.vertices = V
        # mock the neighbours, 
        # to determine correctly the triangle type
        k.neighbours = [True, True, True]
        self.tri = k

    def test_0triangle_segment(self):
        evt = compute_event(self.tri)
        assert evt != None
        assert evt.time == 5.
        assert evt.how == "line"
        assert evt.event_tp == "collapse"
        assert evt.where != None


class TestCollapseTime0TrianglePoint(unittest.TestCase):
    def setUp(self):
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (-1.802775637731995, 0.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, 8.0)
        v.velocity = (1.0, -1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, -8.0)
        v.velocity = (1.0, 1.8685170918213299)
        V.append(v)
        k.vertices = V
        k.neighbours = [True, True, True]
        self.tri = k

    def test_0triangle_point(self):
        evt = compute_event(self.tri)
        assert evt != None
        assert evt.time == 4.2814700223784747
        assert evt.how == "point"
        assert evt.event_tp == "collapse"
        assert evt.where == (2.281470064911059, 0.0)


class TestCollapseTime0TriangleSpoke(unittest.TestCase):
    def setUp(self):
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (1., 0.)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 10.0)
        v.velocity = (1.0, 0.)
        V.append(v)
        v = KineticVertex()
        v.origin = (-1.0, 5.0)
        v.velocity = (5., 0.)
        V.append(v)
        k.vertices = V
        k.neighbours = [True, True, True]
        self.tri = k

    def test_0triangle_spoke(self):
        evt = compute_event(self.tri)
        assert evt != None
        assert evt.time == 0.25
        assert evt.event_tp == "flip"
        assert evt.how == "--"
        assert evt.where == None

    def test_0triangle_spoke_past(self):
        evt = compute_event(self.tri, now = 5)
        assert evt != None
        assert evt.time == None

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

if __name__ == '__main__':
    unittest.main()