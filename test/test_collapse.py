import unittest

from grassfire.collapse import compute_collapse_time
from grassfire.primitives import KineticTriangle, KineticVertex

class TestCollapseTime(unittest.TestCase):
    def setUp(self):
        """Initialize 3 infinite triangles and 1 finite 3-triangle.
        """
        self.triangles = {}
        triangles = self.triangles
        ### 139742234433616
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (2.0, 0.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, -8.0)
        v.velocity = (-1.0, -1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, 8.0)
        v.velocity = (-1.0, 1.8685170918213299)
        V.append(v)
        k.vertices = V
        triangles[ 139742234433616 ] = k
        ### 139742234433872
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (2.0, 0.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, 8.0)
        v.velocity = (-1.0, 1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (1.8027756377319946, -0.0)
        V.append(v)
        k.vertices = V
        triangles[ 139742234433872 ] = k
        ### 139742234434000
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (-2.0, -8.0)
        v.velocity = (-1.0, -1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (2.0, 0.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (1.8027756377319946, -0.0)
        V.append(v)
        k.vertices = V
        triangles[ 139742234434000 ] = k
        ### 139742234434064
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (-1.802775637731995, 0.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, 8.0)
        v.velocity = (1.0, -1.8685170918213299)
        V.append(v)
        v = KineticVertex()
        v.origin = (-2.0, -8.0)
        v.velocity = (1.0, 1.8685170918213299)
        V.append(v)
        k.vertices = V
        triangles[ 139742234434064 ] = k
        ### neighbours
        n = None, triangles[139742234433872], triangles[139742234434000]
        triangles[ 139742234433616 ].neighbours = list(n)
        n = None, triangles[139742234434000], triangles[139742234433616]
        triangles[ 139742234433872 ].neighbours = list(n)
        n = triangles[139742234433872], None, triangles[139742234433616]
        triangles[ 139742234434000 ].neighbours = list(n)
        n = None, None, None
        triangles[ 139742234434064 ].neighbours = list(n)

    def test_3triangle(self):
        evt = compute_collapse_time(self.triangles[139742234434064])#, now=0.)
        assert evt.time == 4.281470067903971

    def test_inf_triangle0(self):
        evt = compute_collapse_time(self.triangles[139742234434000])#, now=0.)
        assert evt is None

    def test_inf_triangle1(self):
        evt = compute_collapse_time(self.triangles[139742234433872])#, now=0.)
        assert evt is None

    def test_inf_triangle2(self):
        evt = compute_collapse_time(self.triangles[139742234433616])#, now=0.)
        assert evt is None

if __name__ == '__main__':
    unittest.main()