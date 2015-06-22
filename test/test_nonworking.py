import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

class TestSimultaneousEvents(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_diamant(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-1,0), (0,-1), (1,0), (0,5), (-1,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == 8
 
    def test_diamantlike(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-15,0), (-1,0), (0,-1), (1,0), (15,0), (0,15), (-15,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == (7+6)

    def test_bottom_circle_top_square(self):
        # bottom circle
        from math import pi, cos, sin, degrees
        ring = []
        pi2 = 2 * pi
        ct = 6
        alpha = pi / ct 
        print degrees(alpha)
        for i in range(ct+1):
            ring.append( (cos(pi+i*alpha), sin(pi+i*alpha)))
        ring.extend([(1, 10), (-1,10)])
        ring.append(ring[0])
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv)
        assert len(skel.segments()) == (7+6)

    def test_cross(self):
        ring = [(0,0), (10, 0), (10,-10), (15, -10), (15,0), (25,0), (25,5), (15,5), (15,15), (10,15), (10,5), (0,5), (0,0)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv)

    def test_poly(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0, 0), (10, 0), (11, -1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
        skel = calc_skel(conv)

    def test_cocircular(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0,1), (1,0), (2,0), (3,1), (3,2), (2,3), (1,3), (0,2), (0,1)]])
        skel = calc_skel(conv)

    def test_cocircular1(self):
        fail = (4,1) # substitute with this and we get a lot of simultaneous events!
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0,1), (1,0), (3,0), fail, (4,3), (3,4), (1,4), (0,3), (0,1)]])
        # FIXME: works but wrong:
        # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
        skel = calc_skel(conv)

    def test_parallellogram(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
        skel = calc_skel(conv)

    def test_teeth(self):
        # init skeleton structure
        conv = ToPointsAndSegments()
        polygon = [[(-2,-1), (-1,0), (1,0), (1.5,-.5), (1.2,.7), 
                    (.4,1.2), (-.6,1.1), (-1.7,.7), (-2,-1)]]
        conv.add_polygon(polygon)
        # FIXME: collapse time in the past!
        skel = calc_skel(conv)

if __name__ == "__main__":
    unittest.main()