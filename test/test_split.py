import unittest

from tri.delaunay import cw, ccw
from tri import ToPointsAndSegments, triangulate

from grassfire.io import output_dt, output_offsets, output_skel
from grassfire.primitives import KineticTriangle, KineticVertex
from grassfire.initialize import init_skeleton
from grassfire.events import handle_split_event

class TestSplice(unittest.TestCase):

    def test_splice(self):
        conv = ToPointsAndSegments()
        #conv.add_point((8,2))
        conv.add_point((0, 0))
        conv.add_point((10, 0))
        conv.add_point((10, 20))
        close = (5, 4)
        conv.add_point(close)
        conv.add_point((0, 20))
        #conv.add_segment((8,2), (14,10))
        conv.add_segment((0,0), (10,0))
        conv.add_segment((10,0), (10,20))
        conv.add_segment((10,20), close)
        conv.add_segment(close, (0,20))
        #conv.add_segment((-2,-8), (8,2))
        conv.add_segment((0,20), (0,0))
        dt = triangulate(conv.points, None, conv.segments)
        output_dt(dt)
        skel = init_skeleton(dt)
        found = None
        for v in skel.vertices:
            print v

        for t in skel.triangles:
            if t.finite:
                if [v.position_at(0) for v in t.vertices] == [(10.0, 0.0), (5.0, 4.0), (0.0, 0.0)]:
                    found = t
                    break
        assert found is not None
        handle_split_event(evt, skel, queue)

if __name__ == '__main__':
    unittest.main()