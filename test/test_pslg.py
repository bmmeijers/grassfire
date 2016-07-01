import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

# FIXME:
# we could test the geometric embedding of the skeleton generated
# as well (requires approximate comparisons for geometry that is generated)

PAUSE = False
OUTPUT = False


class TestPSLGGrassfire(unittest.TestCase):
    """Relatively simple test cases for Straight Skeleton with
    planar straight line graph as input (with terminal vertices)
    """

    def test_cshape(self):
        """Parallel c-shape wavefront"""
        conv = ToPointsAndSegments()
        l0 = [(0.0, 0.0), (0.0, 3)]
        l1 = [(0, 3), (5,3)]
        l2 = [(0,0), (5,0)]
        for line in l0, l1, l2:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv,
                         pause=True,
                         output=True)
        assert len(skel.segments()) == 10
        assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)

#     def test_simple_infinite(self):
#         """1 segment with terminal vertices at convex hull
#         """
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, -1.0), (5.0, -1.0)]
#         for line in l0, :
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         assert len(skel.segments()) == 4
#         assert len(skel.sk_nodes) == 2
    def test_sharp_v(self):
        """Sharp V-shaped polyline
 
        Tests collapse of 2 triangle and handling of
        collapse of spoke
        """
        conv = ToPointsAndSegments()
        l1 = [(0, 0.5), (1, 1)]
        l2 = [(1, 1), (0.5, 0)]
        for line in l1, l2:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == (3 + 4)
        assert len(skel.sk_nodes) == 4


 
    def test_infinite2(self):
        """2 segments with terminal vertices at convex hull
        """
        conv = ToPointsAndSegments()
        l1 = [(5.86602540378, 0.5), (3.36602540378, 4.83012701892)]
        l2 = [(1.63397459622, 4.83012701892), (-0.866025403784, 0.5)]
        for line in l1, l2:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == 11
        assert len(skel.sk_nodes) == 6
 
    def test_cocirculair_2(self):
        """2 segments with terminal vertices at convex hull
        """
        conv = ToPointsAndSegments()
        l1 = [(0, 0.5), (1, 1)]
        l2 = [(1, 1), (0.5, 0)]
        l3 = [(2.5, 3), (2, 2)]
        l4 = [(2, 2), (3, 2.5)]
        for line in l1, l2, l3, l4:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == 16
        assert len(skel.sk_nodes) == 9

 
    def test_2_vshape(self):
        from math import cos, sin, pi
        # misses event
        N = 20
        inc = 2 * pi / N
        pts = []
        for i in range(N):
            if i % 2:
                pt = cos(i * inc), sin(i * inc)
            else:
                pt = 2 * cos(i * inc), 2 * sin(i * inc)
            pts.append(pt)
        l = []
        for n in (0, 1, 4, 5):
            l.append((pts[n], pts[(n + 1) % len(pts)]))
        conv = ToPointsAndSegments()
        for line in l:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == 17
        assert len(skel.sk_nodes) == 10


 
    def test_cocirculair_3(self):
        """
        """
        conv = ToPointsAndSegments()
        l = [
            [(0, 0.5), (1, 1)],
            [(1, 1), (0.5, 0)],
            [(2.5, 3), (2, 2)],
            [(2, 2), (3, 2.5)],
            [(0, 2.5), (1, 2)],
            [(1, 2), (0.5, 3)],
        ]
        for line in l:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == 26


 
    def test_cocirculair_4(self):
        """
        """
        conv = ToPointsAndSegments()
        l = [
            [(0, 0.5), (1, 1)],
            [(1, 1), (0.5, 0)],
            [(2.5, 3), (2, 2)],
            [(2, 2), (3, 2.5)],
            [(0, 2.5), (1, 2)],
            [(1, 2), (0.5, 3)],
            [(2.5, 0), (2, 1)],
            [(2, 1), (3, 0.5)],
        ]
        for line in l:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv)
        assert len(skel.sk_nodes) == 21
        assert len(skel.segments()) == 36


 
    def test_star_cocircular(self):
        """4 v-shape lines pointing towards center
        """
        from math import cos, sin, pi
        N = 20
        inc = 2 * pi / N
        pts = []
        for i in range(N):
            if i % 2:
                pt = cos(i * inc), sin(i * inc)
            else:
                pt = 2 * cos(i * inc), 2 * sin(i * inc)
            pts.append(pt)
        l = []
        for n in (0, 1, 4, 5, 8, 9, 12, 13, 16, 17):
            l.append((pts[n], pts[(n + 1) % len(pts)]))
        conv = ToPointsAndSegments()
        for line in l:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv)
        assert len(skel.segments()) == 45
        assert len(skel.sk_nodes) == 26, len(skel.sk_nodes)


 
    def test_infinite3(self):
        """3 segments with terminal vertices at convex hull
        """
        conv = ToPointsAndSegments()
        l0 = [(0.0, -1.0), (5.0, -1.0)]
        l1 = [(5.86602540378, 0.5), (3.36602540378, 4.83012701892)]
        l2 = [(1.63397459622, 4.83012701892), (-0.866025403784, 0.5)]
        for line in l0, l1, l2:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == 18
        assert len(skel.sk_nodes) == 10


    def test_segments(self):
        segments = [[(0.74919661115900005, 0.28708369850999998), (0.84596844872900001, 0.25202673093900002)],
                    [(0.84596844872900001, 0.25202673093900002),
                     (0.86338737949099997, 0.27726044405599998)],
                    [(0.89132340052500003, 0.25797911189200001),
                     (0.86338737949099997, 0.27726044405599998)],
                    [(0.89132340052500003, 0.25797911189200001),
                     (0.87101957347299996, 0.22858238387499999)],
                    [(0.87101957347299996, 0.22858238387499999), (0.94226555652900001, 0.15090929009699999)]]
        conv = ToPointsAndSegments()
        for line in segments:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        assert len(skel.segments()) == 15, len(skel.segments())
        assert len(skel.sk_nodes) == 9, len(skel.sk_nodes)

#     def test_another_parallel4(self):
#         j = """{
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                          
# "features": [
# { "type": "Feature", "properties": { "id": 19 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.481125224325, 0.5 ], [ 0.288675134595, 0.5 ] ] } },
# { "type": "Feature", "properties": { "id": 20 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.288675134595, 0.5 ], [ 0.19245008973, 0.666666666667 ] ] } },
# { "type": "Feature", "properties": { "id": 24 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.19245008973, 0.666666666667 ], [ 0.288675134595, 0.833333333333 ] ] } },
# { "type": "Feature", "properties": { "id": 44 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.5773502692, 0.666666666667 ], [ 0.481125224325, 0.5 ] ] } }
# ]
# }"""
#         import json
#         x = json.loads(j)
#         # parse segments from geo-json
#         segments = []
#         for y in x['features']:
#             segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
#         # convert to triangulation input
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         # skeletonize / offset
#         skel = calc_skel(conv, pause=True, output=True)

    def test_inf(self):
            """Contains 1 triangle that is only witnessed by infinite triangle event (edge collapse)
            """
            segments = [[(0.713628396143, 0.28492915571299998), (0.605791703184, 0.27382778264800001)],
                        [(0.71037832310799998, 0.31648042652800001),
                         (0.713628396143, 0.28492915571299998)],
                        [(0.74580046742600004, 0.32013219398300002),
                         (0.71037832310799998, 0.31648042652800001)],
                        [(0.74919661115900005, 0.28708369850999998),
                         (0.74580046742600004, 0.32013219398300002)],
                        [(0.74919661115900005, 0.28708369850999998),
                         (0.84596844872900001, 0.25202673093900002)],
                        [(0.84596844872900001, 0.25202673093900002),
                         (0.86338737949099997, 0.27726044405599998)],
                        [(0.89132340052500003, 0.25797911189200001),
                         (0.86338737949099997, 0.27726044405599998)],
                        [(0.89132340052500003, 0.25797911189200001),
                         (0.87101957347299996, 0.22858238387499999)],
                        [(0.87101957347299996, 0.22858238387499999),
                         (0.94226555652900001, 0.15090929009699999)],
                        [(0.94226555652900001, 0.15090929009699999),
                         (0.98031697341500001, 0.16547984224500001)],
                        [(0.98689015483499998, 0.13283304119200001),
                         (0.98031697341500001, 0.16547984224500001)],
                        [(0.98689015483499998, 0.13283304119200001),
                         (0.954279871457, 0.118518112767)],
                        [(0.954279871457, 0.118518112767), (0.96435874963400003, 0.0207237803098)]]
            conv = ToPointsAndSegments()
            for line in segments:
                conv.add_point(line[0])
                conv.add_point(line[1])
                conv.add_segment(*line)
            skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
            assert len(skel.segments()) == 47, len(skel.segments())
            assert len(skel.sk_nodes) == 33, len(skel.sk_nodes)

    def test_another_parallel3(self):
        j = """{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
                                                                                      
"features": [
{ "type": "Feature", "properties": { "id": 19 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.481125224325, 0.5 ], [ 0.288675134595, 0.5 ] ] } },
{ "type": "Feature", "properties": { "id": 20 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.288675134595, 0.5 ], [ 0.19245008973, 0.666666666667 ] ] } },
{ "type": "Feature", "properties": { "id": 24 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.19245008973, 0.666666666667 ], [ 0.288675134595, 0.833333333333 ] ] } },
{ "type": "Feature", "properties": { "id": 44 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.57735026919, 0.666666666667 ], [ 0.481125224325, 0.5 ] ] } }
]
}"""
        import json
        x = json.loads(j)
        # parse segments from geo-json
        segments = []
        for y in x['features']:
            segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
        # convert to triangulation input
        conv = ToPointsAndSegments()
        for line in segments:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        # skeletonize / offset
        skel = calc_skel(conv, pause=True, output=True)
 
    def test_another_parallel1(self):
        j = """{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
                                                                                     
"features": [
{ "type": "Feature", "properties": { "id": 21 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.673575314055, 0.166666666667 ], [ 0.866025403784, 0.166666666667 ] ] } },
{ "type": "Feature", "properties": { "id": 25 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.673575314055, -0.166666666667 ], [ 0.5, -0.0 ] ] } },
{ "type": "Feature", "properties": { "id": 27 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.866025403784, -0.166666666667 ], [ 0.673575314055, -0.166666666667 ] ] } },
{ "type": "Feature", "properties": { "id": 32 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.5, -0.0 ], [ 0.673575314055, 0.166666666667 ] ] } }
]
}"""
        import json
        x = json.loads(j)
        # parse segments from geo-json
        segments = []
        for y in x['features']:
            segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
        # convert to triangulation input
        conv = ToPointsAndSegments()
        for line in segments:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        # skeletonize / offset
        skel = calc_skel(conv, pause=True, output=True)



if __name__ == "__main__":
    if True:
        import logging
        import sys
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
    unittest.main()