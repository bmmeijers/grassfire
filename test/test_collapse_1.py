import unittest
from math import sqrt
from grassfire.collapse import compute_event
from grassfire.primitives import KineticTriangle, KineticVertex, InfiniteVertex
from tri.delaunay import cw, ccw, orient2d
from grassfire.calc import near_zero, all_close_clusters

import logging

class TestCollapseTime1Triangle(unittest.TestCase):
    def setUp(self):
        pass

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