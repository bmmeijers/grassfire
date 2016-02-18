import unittest

from grassfire.calc import bisector_unit, angle, bisector
from math import sqrt, hypot, pi

class TestBisectorUnitVector(unittest.TestCase):
    def test_45degs0(self):
        """Test "V" points from left to right
        """
        bi = bisector_unit((0,1), (1,0), (2,1))
        assert bi == (0, 1)
    def test_45degs1(self):
        """Test "V" points from right to left
        """
        bi = bisector_unit((2,1), (1,0), (0,1))
        assert bi == (0, -1)
    def test_45degs2(self):
        """Test "V" points from bottom to top
        """
        bi = bisector_unit((0,0), (-1,1), (0,2))
        assert bi == (-1,0)
    def test_45degs3(self):
        """Test "V" points from top to bottom
        """
        bi = bisector_unit((0,2), (-1,1), (0,0))
        assert bi == (1,0)

class TestAngle(unittest.TestCase):
    def test_0deg(self):
        a, b, c = (0,0), (10,0), (0,0)
        assert angle(a, b, c) == 0.
    def test_90deg(self):
        a, b, c = (10,10), (10,0), (20,0)
        assert angle(a, b, c) == .5*pi
    def test_180deg(self):
        a, b, c = (0,0), (10,0), (20,0)
        assert angle(a, b, c) == pi
    def test_270deg(self):
        a, b, c = (0,0), (10,0), (10,-10)
        assert angle(a, b, c) == 1.5*pi

class TestStraightBisector(unittest.TestCase):
    def test_180degs(self):
        """Collinear points that go straight
        x--x--x
        """
        bi = bisector((0,0), (1,0), (2,0))
        assert bi == (0, 1), bi
        bi = bisector((2,0), (1,0), (0,0))
        assert bi == (0, -1)

class TestCollapsedBisector(unittest.TestCase):
    def test_near_0degs(self):
        """Folding back from p0 via p1 to p2
        x==x
        """
        bi = bisector_unit((0,0), (1,0), (0,0.000001))
        assert bi == (-0.999999999999875, 4.999999999998125e-07)
#   
    def test_nearly_0degs_left(self):
        """Bisector to the left
        """
        bi = bisector_unit((0,0), (1,0), (0, 1e-56))
        assert bi == (-1.0, 5e-57)

    def test_nearly_0degs_right(self):
        """Bisector to the right
        """
        bi = bisector_unit((0,1e-56), (1,0), (0,0))
        assert bi == (1.0, -5e-57)

    def test_exactly_0degs(self):
        """If points fold back from p0 via p1 to p2 should raise an error
        """
        self.assertRaises(ValueError, bisector, (1,0), (0,0), (1,0))


if __name__ == '__main__':
    unittest.main()