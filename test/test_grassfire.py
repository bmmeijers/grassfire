import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

# FIXME:
# we could test the geometric embedding of the skeleton generated

class TestGrassfire(unittest.TestCase):
    def setUp(self):
        pass

    def test_quad(self):
        """Quad that works"""
        ring = [(1,0), (0, 5), (1,10), (2, 5), (1,0)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv)
 
    def test_diamant(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-1,0), (0,-1), (1,0), (0,5), (-1,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == 8, len(skel.segments())
  
    def test_diamantlike(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-15,0), (-1,0), (0,-1), (1,0), (15,0), (0,15), (-15,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == (7+6)
 
    def test_simple_poly(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0, 0), (22,0), (14,10), (2,8), (0, 6.5), (0,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == 12
  
    def test_simple_infinite(self):
        """1 segment with terminal vertices at convex hull
        """
        conv = ToPointsAndSegments()
        l0 = [(0.0, -1.0), (5.0, -1.0)]
        for line in l0,:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv)
        return
  
    def test_teeth(self):
        conv = ToPointsAndSegments()
        polygon = [[(-2,-1), (-1,0), (1,0), (1.5,-.5), (1.2,.7), 
                    (.4,1.2), (-.6,1.1), (-1.7,.7), (-2,-1)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv)
 
 
  
  
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
        conv.add_point((8,2))
        conv.add_point((4,5))
        conv.add_point((-2,8))
        conv.add_point((-2,-8))
        conv.add_point((14,10))
        conv.add_segment((8,2), (14,10))
        conv.add_segment((14,10), (-2,8))
        conv.add_segment((-2,8), (-2,-8))
        conv.add_segment((-2,-8), (8,2))
        conv.add_segment((4,5), (14,10))
        conv.add_segment((-2,-8), (4,5))
        skel = calc_skel(conv)
        assert len(skel.segments()) == 14

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
        skel = calc_skel(conv, pause = True)
        assert len(skel.segments()) == (8+13)
# # 
    def test_cocircular1(self):
        ok = (3.8,0.8) # this works
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0,1), (1,0), (3,0), ok, (4,3), (3,4), (1,4), (0,3), (0,1)]])
        skel = calc_skel(conv)
 
    def test_sharp_v(self):
        """Sharp V-shaped polyline
           
        Tests collapse of 2 triangle and handling of
        collapse of spoke
        """
        conv = ToPointsAndSegments()
#         l0 = [(0.0, -1.0), (5.0, -1.0)]
        l1 = [(0, 0.5), (1,1)]
        l2 = [(1,1), (0.5, 0)]
        for line in l1, l2:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv)
        assert len(skel.segments()) == (3+4)
        return

if __name__ == "__main__":
    import logging
    import sys
 
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
 
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    unittest.main()