import unittest

from tri.delaunay.helpers import ToPointsAndSegments
from grassfire import calc_skel

# class TestWrongInput(unittest.TestCase):
#     def setUp(self):
#         pass
#  
#     def test_between(self):
#         """After initial conversion we cannot compute all events
#         """
#         segments = [
#             ( (0, 0), (10, 0) ),
#             ( (5.2, 1), (5, 10) ),
#         ]
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)


class TestWrongOffsetsButPassingTests(unittest.TestCase):
    # 2016-02-18
    # ==========
    # These tests pass, but the output generated is not really ok
    # e.g. resulting segments do intersect for example
    def setUp(self):
        pass
 
    def test_wrong_offsets(self):
        """Resulting segments do not form a planar graph
        """
        # FIXME this has wrong offsets generated
        # also the skeleton segments do not form a planar straight line graph
        import json
        s = """{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
                                                                                        
"features": [
{ "type": "Feature", "properties": { "id": 139664900038544.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.725310399997397, 391507.68993699998828 ], [ 51042.455319, 391516.15654599998379 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900067600.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51038.632411799997499, 391542.760162 ], [ 51039.83351180000318, 391542.923948 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900067600.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51039.83351180000318, 391542.923948 ], [ 51039.671322499998496, 391544.167399 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900067728.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51039.671322499998496, 391544.167399 ], [ 51041.540670499998669, 391544.37510499998461 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900067728.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.540670499998669, 391544.37510499998461 ], [ 51041.69552799999656, 391544.839677 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900067856.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.69552799999656, 391544.839677 ], [ 51046.507679299997108, 391545.34621899999911 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900069712.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.918327300001692, 391507.107457 ], [ 51044.982255199996871, 391506.68801799998619 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900069840.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.982255199996871, 391506.68801799998619 ], [ 51044.826051600000937, 391507.83351199998287 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900069840.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.826051600000937, 391507.83351199998287 ], [ 51043.725310399997397, 391507.68993699998828 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070160.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.455319, 391516.15654599998379 ], [ 51042.565606500000285, 391516.170332 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070288.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.473354800000379, 391516.453288 ], [ 51041.308878199997707, 391524.99278299999423 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070416.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.308878199997707, 391524.99278299999423 ], [ 51042.464014700002735, 391525.14345299999695 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070480.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.464014700002735, 391525.14345299999695 ], [ 51042.389055500003451, 391525.69883299997309 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070480.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.389055500003451, 391525.69883299997309 ], [ 51041.245075500002713, 391525.5081699999864 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070800.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.245075500002713, 391525.5081699999864 ], [ 51040.449382300001162, 391530.812791 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900070800.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51040.449382300001162, 391530.812791 ], [ 51040.220387200002733, 391530.78416699997615 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900071248.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 51040.220387200002733, 391530.78416699997615 ], [ 51039.75987090000126, 391535.619588 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900071248.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51039.75987090000126, 391535.619588 ], [ 51038.632411799997499, 391542.760162 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900144272.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.565606500000285, 391516.170332 ], [ 51042.535010500003409, 391516.46099499997217 ] ] } },
{ "type": "Feature", "properties": { "id": 139664900144272.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.535010500003409, 391516.46099499997217 ], [ 51042.473354800000379, 391516.453288 ] ] } }
]
}"""
        x = json.loads(s)
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
# # 
#     def test_tiny_v(self):
#        # MISSES AN EVENT SOMEHOW
#         """Tiny V at bottom of square, does miss an event"""
#         conv = ToPointsAndSegments()
#         polygon = [[(-10, 0), (-10., 100.), (100.,100.), (100.,0.), (2., 0.), (1,-1), (0,0), (-10,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == (10+7)
#         positions = [n.pos for n in skel.sk_nodes]
        
# #         additional: 
# #        check if last node geerated internally is at (50,50)
# # 
#     def test_missing_event(self):
#         """ Misses the event at the right side of the C"""
#         ring = [(82.9195, 34.8762), (82.9195, 36.123),
#         (82.8224828125, 37.4505816406), (82.53454375, 38.658784375), 
#         (82.0603515625, 39.7298449219), (81.404575, 40.646), 
#         (80.5718828125, 41.3894863281), (79.56694375, 41.942540625), 
#         (78.3944265625, 42.2873996094), (77.059, 42.4063),
#         (76.2952375244, 42.3687171631), (75.5838064453, 42.2585341797), 
#         (74.9242850342, 42.0795993408), (74.3162515625, 41.8357609375), 
#         (73.7592843018, 41.5308672607), (73.2529615234, 41.1687666016), 
#         (72.3905625, 40.2883375), (71.7256806641, 39.2252599609), 
#         (71.2549421875, 38.0103203125), (70.9749732422, 36.6743048828), 
#         (70.8824, 35.248), (70.9637001953, 33.823009375), 
#         (71.2144078125, 32.50744375), (71.6447333984, 31.3261375), 
#         (72.2648875, 30.303925), (73.0850806641, 29.465640625), 
#         (73.5733826904, 29.1232322266), (74.1155234375, 28.83611875), 
#         (74.7127792236, 28.6074044922), (75.3664263672, 28.44019375), 
#         (76.848, 28.3027), (77.9991910156, 28.3734771484), 
#         (79.058021875, 28.5858296875), (80.0117917969, 28.9397892578), 
#         (80.8478, 29.4353875), (81.5533457031, 30.0726560547), 
#         (82.115728125, 30.8516265625), (82.5222464844, 31.7723306641), 
#         (82.7602, 32.8348), (80.1098, 32.8348), (79.9671755859, 32.1632625), 
#         (79.7567359375, 31.59635), (79.4750064453, 31.1294125),
#         (79.1185125, 30.7578),(82.9195, 34.8762)]
#         # fixme; misses an event
#         # there is a triangle that should be split
#         # it is, but the direction of one of the 2 new vertices points to wrong side
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)#, pause=False, output=False)

if __name__ == "__main__":
    if True:
        import logging
        import sys
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
#         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
 
    unittest.main(verbosity=2)