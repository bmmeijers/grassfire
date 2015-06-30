import unittest
from math import sqrt
from grassfire.collapse import compute_event
from grassfire.primitives import KineticTriangle, KineticVertex, InfiniteVertex
from tri.delaunay import cw, ccw, orient2d
from grassfire.calc import near_zero, all_close_clusters

import logging

class TestCollapseTime3TriangleAndSurroundings(unittest.TestCase):
    def setUp(self):
        """Initialize 3 infinite triangles and 1 finite 3-triangle.
        """
        self.triangles = {}
        triangles = self.triangles

        ### 139742234433616
        k = KineticTriangle()
        V = []
        v = InfiniteVertex()
        v.origin = (2.0, 0.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, -8.0)
        v.velocity = (-1.0, -1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, 8.0)
        v.velocity = (-1.0, 1.8685170918213299)
        V.append(v)
        k.vertices = V
        triangles[ 139742234433616 ] = k

        ### 139742234433872
        k = KineticTriangle()
        V = []
        v = InfiniteVertex()
        v.origin = (2.0, 0.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, 8.0)
        v.velocity = (-1.0, 1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (1.8027756377319946, -0.0)
        V.append(v)
        k.vertices = V
        triangles[ 139742234433872 ] = k

        ### 139742234434000
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (-2.0, -8.0)
        v.velocity = (-1.0, -1.8685170918213299)
        V.append(v)
        v = InfiniteVertex()
        v.origin = (2.0, 0.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (1.8027756377319946, -0.0)
        V.append(v)
        k.vertices = V
        triangles[ 139742234434000 ] = k

        ### 139742234434064 -- finite
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
        triangles[ 139742234434064 ] = k
        ### neighbours
        n = None, triangles[139742234433872], triangles[139742234434000]
        triangles[ 139742234433616 ].neighbours = list(n)
        n = None, triangles[139742234434000], triangles[139742234433616]
        triangles[ 139742234433872 ].neighbours = list(n)
        n = triangles[139742234433872], None, triangles[139742234433616]
        triangles[ 139742234434000 ].neighbours = list(n)
        n = None, None, None
        triangles[ 139742234434064 ].neighbours = list(n)

    def test_3triangle(self):
        tri = self.triangles[139742234434064]
        evt = compute_event(tri, now=0.)
        logging.debug(evt)
        logging.info(evt)
        assert orient2d(*[v.position_at(4) for v in tri.vertices]) >= 0
        assert evt.time == 4.281470067903971

    def test_3triangle_past(self):
        tri = self.triangles[139742234434064]
        evt = compute_event(tri, now=5.)
        logging.debug(evt)
        logging.info(evt)
        assert evt.time == None


def _enable_logging():
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
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