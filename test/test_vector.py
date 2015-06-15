import unittest
from math import sqrt

from grassfire.calc import vector, scaling_factor, vector_mul_scalar, bisector_unit,\
    rotate180, rotate90ccw, rotate90cw

class TestVector(unittest.TestCase):
    def test_vector0(self):
        pa = (0, 0)
        pb = (2, 0)
        assert vector(pb, pa) == (2,0)

    def test_vector1(self):
        pa = (0, 0)
        pb = (2, 0)
        assert vector(pa, pb) == (-2,0)

class TestScaling(unittest.TestCase):
    def test_sqrt2(self):
        a,b,c = (0,0), (10,-10), (20,0)
        assert scaling_factor(a,b,c) == sqrt(2)

    def test_one(self):
        a,b,c = (0,0), (10, 0), (20,0)
        assert scaling_factor(a,b,c) == 1

class TestRotate180(unittest.TestCase):
    def test_opposite(self):
        v = (10, -10)
        assert rotate180(v) == (-10, 10)

class TestRotate90(unittest.TestCase):
    def test_cw(self):
        v = (0, 1)
        assert rotate90cw(v) == (1,0)

    def test_ccw(self):
        v = (0, 1)
        assert rotate90ccw(v) == (-1, 0)

class TestVectorMulScaling(unittest.TestCase):
    def test_scalar_mul_one(self):
        a,b,c = (0,0), (10, 0), (20,0)
        v = bisector_unit(a,b,c)
        s = 1
        assert v == vector_mul_scalar(v, s)

    def test_scalar_mul_sqrt2(self):
        a,b,c = (0,0), (10, -10), (20,0)
        v = bisector_unit(a, b, c)
        s = sqrt(2)
        m = vector_mul_scalar(v, s)
        assert v != m # multiplied vector is not the same as input
        assert m[0] == 0 # dx == 0
        assert m[1] == s # dy == sqrt(2)

if __name__ == '__main__':
    unittest.main()