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

class TestCollapseSameTime(unittest.TestCase):
    def setUp(self):
        self.triangles = {}
        triangles = self.triangles
        ### 139708485588816
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 1.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, -1.0)
        v.velocity = (-0.0, -1.414213562373095)
        V.append(v)
        v = KineticVertex()
        v.origin = (-1.0, 0.0)
        v.velocity = (-1.0855388459943132, -0.3286747163787818)
        V.append(v)
        k.vertices = V
        triangles[ 139708485588816 ] = k
        ### 139708485588880
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (-0.0, 5.099019513592779)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 1.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (-1.0, 0.0)
        v.velocity = (-1.0855388459943132, -0.3286747163787818)
        V.append(v)
        k.vertices = V
        triangles[ 139708485588880 ] = k
        ### 139708485589072
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 1.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (-0.0, 5.099019513592779)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.0, 0.0)
        v.velocity = (1.0855388459943134, -0.32867471637878193)
        V.append(v)
        k.vertices = V
        triangles[ 139708485589072 ] = k
        ### 139708485589136
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, -1.0)
        v.velocity = (-0.0, -1.414213562373095)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 1.0)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.0, 0.0)
        v.velocity = (1.0855388459943134, -0.32867471637878193)
        V.append(v)
        k.vertices = V
        triangles[ 139708485589136 ] = k
        ### 139708485589200 <<< this is the bottom internal
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (1.0, 0.0)
        v.velocity = (-1.0855388459943136, 0.328674716378782)
        V.append(v)
        v = KineticVertex()
        v.origin = (-1.0, 0.0)
        v.velocity = (1.0855388459943134, 0.32867471637878193)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, -1.0)
        v.velocity = (0.0, 1.4142135623730951)
        V.append(v)
        k.vertices = V
        triangles[ 139708485589200 ] = k
        ### 139708485589264 <<< this is the top internal
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (-1.0, 0.0)
        v.velocity = (1.0855388459943134, 0.32867471637878193)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.0, 0.0)
        v.velocity = (-1.0855388459943136, 0.328674716378782)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (0.0, -5.0990195135927845)
        V.append(v)
        k.vertices = V
        triangles[ 139708485589264 ] = k

        ### neighbour relationships
        n = [ None, triangles[139708485588880], triangles[139708485589136] ]
        triangles[ 139708485588816 ].neighbours = n
        n = [ triangles[139708485588816], None, triangles[139708485589072] ]
        triangles[ 139708485588880 ].neighbours = n
        n = [ None, triangles[139708485589136], triangles[139708485588880] ]
        triangles[ 139708485589072 ].neighbours = n
        n = [ triangles[139708485589072], None, triangles[139708485588816] ]
        triangles[ 139708485589136 ].neighbours = n
        n = [ None, None, triangles[139708485589264] ]
        triangles[ 139708485589200 ].neighbours = n
        n = [ None, None, triangles[139708485589200] ]
        triangles[ 139708485589264 ].neighbours = n

    def test_equal_sides(self):
        t = self.triangles[139708485589200]
        evt = compute_collapse_time(t)
        print evt

if __name__ == '__main__':
    unittest.main()