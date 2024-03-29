import unittest
from grassfire.calc import is_close, close_cluster

class TestCloseToZero(unittest.TestCase):
    def test_close_to_zero(self):
        assert is_close(0.0, 1e-10, abs_tol=1e-8, rel_tol=1e-9, method="weak") == True
        assert is_close(1e-10, 0.0, abs_tol=1e-8, rel_tol=1e-9, method="weak") == True

    def test_equal_zero(self):
        assert is_close(0.0, 0.0, abs_tol=1e-8, rel_tol=1e-9, method="weak") == True
        assert is_close(0.0, 0.0, abs_tol=1e-8, rel_tol=1e-9, method="weak") == True

    def test_close_to_zero_no_tol(self):
        assert is_close(0.0, 1e-10, method="weak") == False
        assert is_close(1e-10, 0.0, method="weak") == False

class TestCluster(unittest.TestCase):
    def test_cluster(selfself):
        assert close_cluster([1,1,2,3,4,4]) == [1,2,3,4]

if __name__ == '__main__':
    unittest.main()