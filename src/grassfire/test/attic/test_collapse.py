import unittest
from math import sqrt
from grassfire.collapse import compute_collapse_time, all_close,\
    collapse_time_edge, vertex_crash_time, area_collapse_time_coeff,\
    solve_quadratic, area_collapse_times, get_unique_times
from grassfire.primitives import KineticTriangle, KineticVertex, InfiniteVertex
from tri.delaunay import orient2d, cw, ccw
from grassfire.calc import near_zero, all_close_clusters
import bisect

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
        bottom = compute_collapse_time(t)

        t = self.triangles[139708485589264]
        top = compute_collapse_time(t)

        print bottom.time == top.time

class TestAllEqual(unittest.TestCase):
    def test_all_equal0(self):
        assert all_close([10] * 3)

    def test_all_equal2(self):
        assert not all_close(range(10))

    def test_all_equal3(self):
        assert all_close([0.9212014878049224, 
            0.9212014878049224, 0.9212014878049225])


class TestEvent1Edge(unittest.TestCase):
    def setUp(self):
        self.triangles = {}
        triangles = self.triangles
        ### 139643876356304
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (4.0, 0.0)
        v.velocity = (-0.9049875621120889, -0.9999999999999999)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (0.6770329614269006, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356304 ] = k
        ### 139643876356368
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (0.6770329614269006, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (4.0, 0.0)
        v.velocity = (-0.9049875621120889, -0.9999999999999999)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (-0.5885834574042905, -4.164041047077979)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356368 ] = k
        ### 139643876356432
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (0.5885834574042905, 4.164041047077979)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (1.0, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (-0.6770329614269007, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356432 ] = k
        ### 139643876356496
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (0.5885834574042905, 4.164041047077979)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (1.0, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356496 ] = k
        ### 139643876356560
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (0.5885834574042905, 4.164041047077979)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356560 ] = k
        ### 139643876356624
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.0, 5.0)
        v.velocity = (-0.7807764064044151, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356624 ] = k
        ### 139643876356688
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 5.0)
        v.velocity = (-0.7807764064044151, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (4.0, 5.0)
        v.velocity = (0.7807764064044151, -1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356688 ] = k
        ### 139643876356752
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (0.0, 4.1231056256176615)
        V.append(v)
        v = KineticVertex()
        v.origin = (4.0, 5.0)
        v.velocity = (-0.7807764064044151, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 5.0)
        v.velocity = (0.7807764064044151, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356752 ] = k
        ### 139643876356816
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (1.0, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 5.0)
        v.velocity = (-0.7807764064044151, -1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356816 ] = k
        ### 139643876356880
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (1.0, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (1.0, -1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356880 ] = k
        ### 139643876356944
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (-0.9999999999999998, 0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (-0.9999999999999998, -0.9999999999999998)
        V.append(v)
        k.vertices = V
        triangles[ 139643876356944 ] = k
        ### 139643876357072
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 5.0)
        v.velocity = (-0.9999999999999998, 0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 5.0)
        v.velocity = (0.7807764064044151, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357072 ] = k
        ### 139643876357136
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 5.0)
        v.velocity = (0.7807764064044151, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (4.0, 5.0)
        v.velocity = (-0.7807764064044151, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357136 ] = k
        ### 139643876357200
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (4.0, 5.0)
        v.velocity = (-0.7807764064044151, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 5.0)
        v.velocity = (0.7807764064044151, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357200 ] = k
        ### 139643876357264
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 5.0)
        v.velocity = (0.7807764064044151, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (7.0, 5.0)
        v.velocity = (-0.7807764064044151, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357264 ] = k
        ### 139643876357328
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 5.0)
        v.velocity = (0.9999999999999998, 0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (7.0, 5.0)
        v.velocity = (-0.7807764064044151, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357328 ] = k
        ### 139643876357456
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (0.9999999999999998, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 5.0)
        v.velocity = (0.9999999999999998, 0.9999999999999998)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357456 ] = k
        ### 139643876357520
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (7.0, 0.0)
        v.velocity = (-0.7094810050208543, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (0.9999999999999998, -0.9999999999999998)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357520 ] = k
        ### 139643876357584
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.0, 0.0)
        v.velocity = (0.8611874208078342, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (7.0, 0.0)
        v.velocity = (-0.7094810050208543, -0.9999999999999998)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357584 ] = k
        ### 139643876357648
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (4.0, 0.0)
        v.velocity = (-0.9049875621120889, -0.9999999999999999)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 0.0)
        v.velocity = (0.8611874208078342, -0.9999999999999998)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357648 ] = k
        ### 139643876357712
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.0, 0.0)
        v.velocity = (-0.8611874208078343, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (0.5885834574042905, 4.164041047077979)
        V.append(v)
        v = KineticVertex()
        v.origin = (4.0, 0.0)
        v.velocity = (0.9049875621120889, 0.9999999999999999)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357712 ] = k
        ### 139643876357776
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.3, 2.0)
        v.velocity = (-0.3899868930592274, 4.141336851657371)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (0.5885834574042905, 4.164041047077979)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 0.0)
        v.velocity = (-0.8611874208078343, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357776 ] = k
        ### 139643876357840
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.3, 2.0)
        v.velocity = (-0.3899868930592274, 4.141336851657371)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.8, 2.0)
        v.velocity = (0.5885834574042905, 4.164041047077979)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357840 ] = k
        ### 139643876357904
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (-1.0, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.3, 2.0)
        v.velocity = (-0.3899868930592274, 4.141336851657371)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357904 ] = k
        ### 139643876357968
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 5.0)
        v.velocity = (-1.0, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (-1.0, 1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876357968 ] = k
        ### 139643876358032
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (-0.0, -4.123105625617657)
        V.append(v)
        v = KineticVertex()
        v.origin = (10.0, 5.0)
        v.velocity = (-1.0, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (7.0, 5.0)
        v.velocity = (0.7807764064044151, -1.0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876358032 ] = k
        ### 139643876358096
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (7.0, 5.0)
        v.velocity = (-0.7807764064044151, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 5.0)
        v.velocity = (0.7807764064044151, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.5, 3.0)
        v.velocity = (0.0, 4.1231056256176615)
        V.append(v)
        k.vertices = V
        triangles[ 139643876358096 ] = k
        ### 139643876358160
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (10.0, 0.0)
        v.velocity = (-1.0, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.3, 2.0)
        v.velocity = (-0.3899868930592274, 4.141336851657371)
        V.append(v)
        v = KineticVertex()
        v.origin = (7.0, 0.0)
        v.velocity = (0.7094810050208544, 0.9999999999999999)
        V.append(v)
        k.vertices = V
        triangles[ 139643876358160 ] = k
        ### 139643876358224
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (6.3, 2.0)
        v.velocity = (0.38998689305922796, -4.141336851657377)
        V.append(v)
        v = KineticVertex()
        v.origin = (6.0, 0.0)
        v.velocity = (0.8611874208078342, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (7.0, 0.0)
        v.velocity = (-0.7094810050208543, -0.9999999999999998)
        V.append(v)
        k.vertices = V
        triangles[ 139643876358224 ] = k
        ### 139643876358288
        k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (0.6770329614269006, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (-0.9999999999999998, -0.9999999999999998)
        V.append(v)
        v = KineticVertex()
        v.origin = (5.00625, 2.5)
        v.velocity = (0, 0)
        V.append(v)
        k.vertices = V
        triangles[ 139643876358288 ] = k
        ### neighbour relationships
        n = [ triangles[139643876358288], triangles[139643876357648], triangles[139643876356368] ]
        triangles[ 139643876356304 ].neighbours = n
        n = [ None, None, triangles[139643876356304] ]
        triangles[ 139643876356368 ].neighbours = n
        n = [ None, None, triangles[139643876356496] ]
        triangles[ 139643876356432 ].neighbours = n
        n = [ triangles[139643876356880], triangles[139643876356432], triangles[139643876356560] ]
        triangles[ 139643876356496 ].neighbours = n
        n = [ triangles[139643876357840], triangles[139643876356624], triangles[139643876356496] ]
        triangles[ 139643876356560 ].neighbours = n
        n = [ triangles[139643876356560], None, triangles[139643876356688] ]
        triangles[ 139643876356624 ].neighbours = n
        n = [ None, None, triangles[139643876356624] ]
        triangles[ 139643876356688 ].neighbours = n
        n = [ triangles[139643876357136], None, None ]
        triangles[ 139643876356752 ].neighbours = n
        n = [ None, None, triangles[139643876356880] ]
        triangles[ 139643876356816 ].neighbours = n
        n = [ triangles[139643876356816], None, triangles[139643876356496] ]
        triangles[ 139643876356880 ].neighbours = n
        n = [ triangles[139643876358288], None, triangles[139643876357072] ]
        triangles[ 139643876356944 ].neighbours = n
        n = [ None, triangles[139643876357136], triangles[139643876356944] ]
        triangles[ 139643876357072 ].neighbours = n
        n = [ triangles[139643876356752], triangles[139643876357200], triangles[139643876357072] ]
        triangles[ 139643876357136 ].neighbours = n
        n = [ None, triangles[139643876357264], triangles[139643876357136] ]
        triangles[ 139643876357200 ].neighbours = n
        n = [ triangles[139643876358096], triangles[139643876357328], triangles[139643876357200] ]
        triangles[ 139643876357264 ].neighbours = n
        n = [ triangles[139643876357264], None, triangles[139643876357456] ]
        triangles[ 139643876357328 ].neighbours = n
        n = [ triangles[139643876357328], None, triangles[139643876357520] ]
        triangles[ 139643876357456 ].neighbours = n
        n = [ triangles[139643876357456], None, triangles[139643876357584] ]
        triangles[ 139643876357520 ].neighbours = n
        n = [ triangles[139643876357520], triangles[139643876358224], triangles[139643876357648] ]
        triangles[ 139643876357584 ].neighbours = n
        n = [ triangles[139643876357584], None, triangles[139643876356304] ]
        triangles[ 139643876357648 ].neighbours = n
        n = [ None, None, triangles[139643876357776] ]
        triangles[ 139643876357712 ].neighbours = n
        n = [ triangles[139643876357712], None, triangles[139643876357840] ]
        triangles[ 139643876357776 ].neighbours = n
        n = [ triangles[139643876356560], triangles[139643876357776], triangles[139643876357904] ]
        triangles[ 139643876357840 ].neighbours = n
        n = [ triangles[139643876357840], triangles[139643876358160], triangles[139643876357968] ]
        triangles[ 139643876357904 ].neighbours = n
        n = [ triangles[139643876357904], None, triangles[139643876358032] ]
        triangles[ 139643876357968 ].neighbours = n
        n = [ None, None, triangles[139643876357968] ]
        triangles[ 139643876358032 ].neighbours = n
        n = [ None, None, triangles[139643876357264] ]
        triangles[ 139643876358096 ].neighbours = n
        n = [ None, None, triangles[139643876357904] ]
        triangles[ 139643876358160 ].neighbours = n
        n = [ triangles[139643876357584], None, None ]
        triangles[ 139643876358224 ].neighbours = n
        n = [ triangles[139643876356944], triangles[139643876356304], None ]
        triangles[ 139643876358288 ].neighbours = n

    def test_1tri(self):
        t = self.triangles[139643876357776]
        print t.str_at(2.5)
        evt = compute_collapse_time(t, now = 0)
        pos = [v.position_at(evt.time) for v in t.vertices]
        print "orientation", orient2d(*pos)
        assert evt is not None
        print evt

    def test_0tri(self):
        t = self.triangles[139643876356560]
        print t.str_at(0)
        print t.neighbours
        evt = compute_collapse_time(t, now = 0)
        print t.str_at(evt.time)
        pos = [v.position_at(evt.time) for v in t.vertices]
        for v in t.vertices:
            print v.origin
            print v.velocity
        times = []
#         for side in range(3):
#             i, j = cw(side), ccw(side)
#             v1, v2 = t.vertices[i], t.vertices[j]
#             times.append((collapse_time_edge(v1, v2), side))
        side = 0
        i, j = cw(side), ccw(side)
        v1, v2 = t.vertices[i], t.vertices[j]
        time = collapse_time_edge(v1, v2)
        times.append(time)
        side = 2
        i, j = cw(side), ccw(side)
        v1, v2 = t.vertices[i], t.vertices[j]
        with open("/tmp/cpa.csv","w") as fh:
            for i, inc in enumerate(range(100, 150), start=1):
                val = inc / 1000.
                v1.position_at(val)
                v2.position_at(val)
                print >>fh, val,";", sqrt(v1.distance2_at(v2, val))
        time = collapse_time_edge(v1, v2)
        times.append(time)
        for time in times:
            print "", time
        from datetime import datetime, timedelta
        
        with open("/tmp/kinetic.wkt","w") as fh:
            fh.write("start;end;wkt\n")
            prev = datetime(2015, 1, 1)
            #prev = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            for inc in range(100, 150):
                val = inc / 1000.
                cur = prev
                fh.write("{};{};{}\n".format(prev, cur, t.str_at(val)))
                prev = cur + timedelta(days=1)
        print "times", times
        print "orientation", orient2d(*pos)
        assert evt is not None
        print evt

class EdgeCollapse(unittest.TestCase):
    def setUp(self):
        pass

    def test_crossing(self):
        """2 vertices crossing each other"""
        u = KineticVertex()
        u.origin = (0., 0.)
        u.velocity = (1., 1.)

        v = KineticVertex()
        v.origin = (10., 0.)
        v.velocity = (-1., 1.)
        time = collapse_time_edge(u, v)
#         with open("/tmp/cpa.csv","w") as fh:
#             for i, inc in enumerate(range(100, 150), start=1):
#                 val = inc / 1000.
#                 u.position_at(val)
#                 v.position_at(val)
#                 print >>fh, val,";", sqrt(u.distance2_at(v, val))
        dist = u.distance2_at(v, time)
        assert near_zero(dist)

    def test_parallel(self):
        """2 vertices moving in parallel"""
        u = KineticVertex()
        u.origin = (0., 0.)
        u.velocity = (0., 1.)

        v = KineticVertex()
        v.origin = (10., 0.)
        v.velocity = (0., 1.)
        time = collapse_time_edge(u, v)
        assert time is None
#         dist = u.distance2_at(v, time)
#         assert dist == 100.

    def test_parallel_overlap(self):
        """2 vertices having the exact same track"""
        u = KineticVertex()
        u.origin = (0., 0.)
        u.velocity = (0., 1.)
        v = KineticVertex()
        v.origin = (0., 0.)
        v.velocity = (0., 1.)
        time = collapse_time_edge(u, v)
        assert time is None
#         dist = u.distance2_at(v, time)
#         assert dist == 0.

    def test_parallel_follower(self):
        """one vertex follows the other vertex on its track"""
        u = KineticVertex()
        u.origin = (0., 0.)
        u.velocity = (0., 1.)
        v = KineticVertex()
        v.origin = (0., -10.)
        v.velocity = (0., 1.)
        time = collapse_time_edge(u, v)
        assert time is None
#         dist = u.distance2_at(v, time)
#         assert dist == 100.

    def test_bump(self):
        """2 vertices that bump into each other half way"""
        u = KineticVertex()
        u.origin = (0., 0.)
        u.velocity = (1., 1.)

        v = KineticVertex()
        v.origin = (10., 10.)
        v.velocity = (-1., -1.)
        time = collapse_time_edge(u, v)
        assert time is not None
        dist = u.distance2_at(v, time)
        assert near_zero(dist)


class VertexCrash(unittest.TestCase):
    def test_crash(self):
        # base of triangle (from orig to dest)
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., 1.)

        d = KineticVertex()
        d.origin = (10., 0.)
        d.velocity = (0, 1.)

        # vertex supposed to crash into base (the apex)
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (0., -1.)
        times = []
        # vertex crash time
        time = vertex_crash_time(o, d, a)
        times.append(time)
        # edge collapse times
        time = collapse_time_edge(o, d)
        times.append(time)
        time = collapse_time_edge(d, a)
        times.append(time)
        time = collapse_time_edge(a, o)
        times.append(time)
        # area collapse time
        coeff = area_collapse_time_coeff(o, d, a)
        time = solve_quadratic(coeff[0], coeff[1], coeff[2])
        times.extend(time)
        times = get_unique_times(times)
        show_all_times(times, o, d, a)

    def test_opposite_crash(self):
        # base of triangle (from orig to dest)
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., -1.)

        d = KineticVertex()
        d.origin = (10., 0.)
        d.velocity = (0, -1.)

        # vertex supposed to crash into base (the apex)
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (0., 1.)

        # edge collapse times
        time = collapse_time_edge(o, d)
        time = collapse_time_edge(d, a)
        time = collapse_time_edge(a, o)
        # area collapse time
        coeff = area_collapse_time_coeff(o, d, a)
        times = solve_quadratic(coeff[0], coeff[1], coeff[2])

        times = get_unique_times(times)
        show_all_times(times, o, d, a)

    def test_perpendicular_crash(self):
        # base of triangle (from orig to dest)
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., -1.)

        d = KineticVertex()
        d.origin = (10., 0.)
        d.velocity = (0, -1.)

        # vertex supposed to crash into base (the apex)
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (-1., 0.)
        # edge collapse times
        times = []
        time = collapse_time_edge(o, d)
        times.append(time)
        time = collapse_time_edge(d, a)
        times.append(time)
        time = collapse_time_edge(a, o)
        times.append(time)
        # area collapse time
        coeff = area_collapse_time_coeff(o, d, a)
        solution = solve_quadratic(coeff[0], coeff[1], coeff[2])
        for time in solution:
            times.append(time)
        # vertex crash time
        time = vertex_crash_time(o, d, a)
        times.append(time)
        times = get_unique_times(times)
        show_all_times(times, o, d, a)

    def test_perpendicular2_crash(self):
        # base of triangle2 (from orig to dest)
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (0., 1.)

        d = KineticVertex()
        d.origin = (10., 0.)
        d.velocity = (0, 1.)

        # vertex supposed to crash into base (the apex)
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (1, 0)
        # edge collapse times
        times = []
        time = collapse_time_edge(o, d)
        times.append(time)
        time = collapse_time_edge(d, a)
        times.append(time)
        time = collapse_time_edge(a, o)
        times.append(time)
        # area collapse time
        area = area_collapse_times(o, d, a)
        times.extend(area)
        # vertex crash time
        time = vertex_crash_time(o, d, a)
        times.append(time)
        #
        times = get_unique_times(times)
        show_all_times(times, o, d, a)


    def test_central_crash(self):
        # base of triangle2 (from orig to dest)
        o = KineticVertex()
        o.origin = (0., 0.)
        o.velocity = (sqrt(2), sqrt(2))

        d = KineticVertex()
        d.origin = (10., 0.)
        d.velocity = (-sqrt(2), -sqrt(2))

        # vertex supposed to crash into base (the apex)
        a = KineticVertex()
        a.origin = (5, 5)
        a.velocity = (0, - sqrt(2))
        # edge collapse times
        times = []
        time = collapse_time_edge(o, d)
        times.append(time)
        time = collapse_time_edge(d, a)
        times.append(time)
        time = collapse_time_edge(a, o)
        times.append(time)
        # area collapse time
        area = area_collapse_times(o, d, a)
        times.extend(area)
        # vertex crash time
        time = vertex_crash_time(o, d, a)
        times.append(time)
        # filter None out of the times and see what is there...
        times = get_unique_times(times)
        show_all_times(times, o, d, a)

    def test_equilateral(self):
#         k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (2.1889010593167346, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (-2.1889010593167346, 1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.5, 1.7320508075688772)
        v.velocity = (0.0, -1.5275252316519463)
        V.append(v)
        o,d,a = V
        print o,d,a
#         k.vertices = V

        # edge collapse times
        times = []
        time = collapse_time_edge(o, d)
        times.append(time)
        time = collapse_time_edge(d, a)
        times.append(time)
        time = collapse_time_edge(a, o)
        times.append(time)
        # area collapse time
        area = area_collapse_times(o, d, a)
        times.extend(area)
        # vertex crash time
        time = vertex_crash_time(o, d, a)
        times.append(time)
        print times
        times = get_unique_times(times)
        show_all_times(times, o, d, a)

    def test_equilateral_outwards(self):
#         k = KineticTriangle()
        V = []
        v = KineticVertex()
        v.origin = (0.0, 0.0)
        v.velocity = (-2.1889010593167346, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (3.0, 0.0)
        v.velocity = (2.1889010593167346, -1.0)
        V.append(v)
        v = KineticVertex()
        v.origin = (1.5, 1.7320508075688772)
        v.velocity = (0.0, 1.5275252316519463)
        V.append(v)
        o,d,a = V
        print o,d,a
#         k.vertices = V

        # edge collapse times
        times = []
        time = collapse_time_edge(o, d)
        times.append(time)
        time = collapse_time_edge(d, a)
        times.append(time)
        time = collapse_time_edge(a, o)
        times.append(time)
        # area collapse times
        area = area_collapse_times(o, d, a)
        times.extend(area)
        # vertex crash time
        time = vertex_crash_time(o, d, a)
        times.append(time)
        #
        print times
        times = get_unique_times(times)
        show_all_times(times, o, d, a)
        self.assertRaises(ValueError, find_ge, times, 0)

def compute_all_collapse_times(o,d,a):
    # edge collapse times
    times = []
    time = collapse_time_edge(o, d)
    times.append(time)
    time = collapse_time_edge(d, a)
    times.append(time)
    time = collapse_time_edge(a, o)
    times.append(time)
    # area collapse times
    area = area_collapse_times(o, d, a)
    times.extend(area)
    # vertex crash time of the apex into the segment, orig -> dest
    time = vertex_crash_time(o, d, a)
    times.append(time)
    return times

def show_all_times(times, o, d, a):
    print ""
    print times
    for time in times:
        pa = o.position_at(time)
        pb = d.position_at(time)
        pc = a.position_at(time)
        collapse = near_zero(orient2d(pa, pb, pc))
        print time, collapse
        if collapse:
            dists = [o.distance2_at(d, time), d.distance2_at(a, time), a.distance2_at(o, time)]
            if all_close(dists, abs_tol=1e-8):
                print "point", pa, pb, pc
                avg = []
                for i in range(2):
                    avg.append(sum(map(lambda x: x[i], (pa, pb, pc))) / 3.)
                print " avg ", tuple(avg)
            else:
                print "line", pa, pb, pc
                # to a segment, two separate points
                # 1 distance is near_zero!
                # pa+pb = pc
                # pa+pc = pb
                # pb+pc = pa
                X = all_close_clusters([x for x, y in (pa, pb, pc)])
                Y = all_close_clusters([y for x, y in (pa, pb, pc)])
                print "     ", len(X)
                print "     ", len(Y)
                print "     ", X
                print "     ", Y
                # FIXME: by looking at the distances and knowledge on what
                # side is what, we should be able to reliable decide what 
                # is the event that happens to this triangle!
                if len(X) == 3 or len(Y) == 3:
                    print "flip/split", dists
                else:
                    assert len(X) == 2 or len(Y) == 2
                    print "collapse", dists
                #
                # to a line, three separate points
                # no distance is near_zero! 
                # -> could be flip or split event
    print ""

# possible actions:

# A triangle at time t
# --------------------
# - collapses to a point (all 3 sides collapse)
# - collapses to a segment
# - flips (to maintain correct orientation)
# - is split (collapses to a segment, and that segment is split into 2)


# a 3-triangle can:
# - collapse to a point

# a 2-triangle can:
# - collapse to a point
# - collapse to a segment

# a 1-triangle can:
# - collapse to a point
# - flip
# - be split

# a 0-triangle can:
# - flip
# - collapse to a segment?
# - collapse to a point? -- see circle

# an infinite triangle can:
# - flip
# - collapse to a point

def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect.bisect_left(a, x)
    if i != len(a):
        return a[i]
    raise ValueError("not there")

def perform_one():
#     tst = TestCollapseSameTime("test_equal_sides")
#     tst = TestEvent1Edge("test_0tri")
#     tst = VertexCrash("test_equilateral_outwards")
    tst = VertexCrash("test_equilateral")
#     tst = TestEvent1Edge("test_0tri")
#     tst = EdgeCollapse("test_crossing")
#     tst = EdgeCollapse("test_parallel_follower")
    suite = unittest.TestSuite()
    suite.addTests([tst])#, tst1])
    runner = unittest.TextTestRunner()
    runner.run(suite)

def _enable_logging():
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

if __name__ == '__main__':
    _enable_logging()
    unittest.main()
#     perform_one()