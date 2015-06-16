import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

class TestGrassfire(unittest.TestCase):

    def test_diamant(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-1,0), (0,-1), (1,0), (0,5), (-1,0)]])
        skel = calc_skel(conv)
        assert len(skel.segments()) == 8

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

if __name__ == "__main__":
    unittest.main()