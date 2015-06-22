import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

# FIXME:
# we could test the geometric embedding of the skeleton generated

class TestGrassfire(unittest.TestCase):
    def setUp(self):
        pass
 
    def test_simple_poly(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0, 0), (22,0), (14,10), (2,8), (0, 6.5), (0,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == 12
 
    def test_triangle(self):
        conv = ToPointsAndSegments()
        conv.add_point((10,0))
        conv.add_point((-2,8))
        conv.add_point((-2,-8))
        conv.add_segment((10,0), (-2,8))
        conv.add_segment((-2,8), (-2,-8))
        conv.add_segment((-2,-8), (10,0))
        skel = calc_skel(conv)
        assert len(skel.segments()) == 6
 
    def test_quad(self):
        conv = ToPointsAndSegments()
        #conv.add_point((8,2))
        conv.add_point((4,5))
        conv.add_point((-2,8))
        conv.add_point((-2,-8))
        conv.add_point((14,10))
        #conv.add_segment((8,2), (14,10))
        conv.add_segment((14,10), (-2,8))
        conv.add_segment((-2,8), (-2,-8))
        #conv.add_segment((-2,-8), (8,2))
        conv.add_segment((4,5), (14,10))
        conv.add_segment((-2,-8), (4,5))
        skel = calc_skel(conv)
        assert len(skel.segments()) == 9

    def test_split(self):
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
        skel = calc_skel(conv)
        assert len(skel.segments()) == 12

    def test_bottom_circle(self):
        # bottom circle
        from math import pi, cos, sin, degrees
        ring = []
        pi2 = 2 * pi
        ct = 8
        alpha = pi / ct 
        for i in range(ct+1):
            ring.append( (cos(pi+i*alpha), sin(pi+i*alpha)))
        ring.append(ring[0])
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv)
        assert len(skel.segments()) == (9+15)

    def test_poly(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == (8+13)

    def test_cocircular1(self):
        ok = (3.8,0.8) # this works
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0,1), (1,0), (3,0), ok, (4,3), (3,4), (1,4), (0,3), (0,1)]])
        # FIXME: works but wrong:
        # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
        skel = calc_skel(conv)

if __name__ == "__main__":
    unittest.main()