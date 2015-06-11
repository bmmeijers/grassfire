import unittest

from tri.delaunay import cw, ccw
from tri import ToPointsAndSegments, triangulate

from grassfire.io import output_dt, output_offsets, output_skel
from grassfire.events import replace_kvertex
from grassfire.primitives import KineticTriangle, KineticVertex
from grassfire.initialize import init_skeleton

class TestRotateAndReplace(unittest.TestCase):

    def test_replace_kvertex(self):

        class QueueMock(object):
            """Mock for the priority queue
            """
            def add(self, one):
                pass
            def remove(self, one):
                pass
        # init skeleton structure
        conv = ToPointsAndSegments()
        polygon = [[(-2,-1), (-1,0), (1,0), (1.5,-.5), (1.2,.7), 
                    (.4,1.2), (-.6,1.1), (-1.7,.7), (-2,-1)]]
        conv.add_polygon(polygon)
        dt = triangulate(conv.points, None, conv.segments)
        output_dt(dt)
        skel = init_skeleton(dt)
        #
        queue = QueueMock()
        newv = KineticVertex()
        newv.origin = (1,0)
        newv.velocity = (0.5, 0.5)
        found = None
        for t in skel.triangles:
            if t.finite:
                if [v.position_at(0) for v in t.vertices] == [(1.0, 0.0), (0.4, 1.2), (-1.0, 0.0)]:
                    found = t
                    break
        assert found is not None
        a, b ,c = None, None, None
        for v in t.vertices:
            if v.position_at(0) == (-1,0):
                a = v
            if v.position_at(0) == (1,0):
                b = v
            if v.position_at(0) == (0.4,1.2):
                c = v
        assert a is not None
        assert b is not None
        assert c is not None
        # precondition:
        # no vertex equal to the new kinetic vertex
        for t in skel.triangles:
            assert newv not in t.vertices
        replace_kvertex(found, b, newv, 0, cw, queue)
        # postcondition
        # we should have replaced 3 vertices
        ct = 0
        for t in skel.triangles:
            if newv in t.vertices:
                ct+=1
        assert ct == 3
        newv = KineticVertex()
        newv.origin = (-1,0)
        newv.velocity = (-0.5, 0.5)
        # precondition:
        # no vertex equal to the new kinetic vertex
        for t in skel.triangles:
            assert newv not in t.vertices
        replace_kvertex(found, a, newv, 0, ccw, queue)
        # we should have replaced 4 vertices
        ct = 0
        for t in skel.triangles:
            if newv in t.vertices:
                ct+=1
        assert ct == 4

if __name__ == '__main__':
    unittest.main()