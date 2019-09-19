import unittest

from tri.delaunay import ToPointsAndSegments
from grassfire import calc_skel
from grassfire.events import at_same_location

PAUSE = False
OUTPUT = False
LOGGING = False


class TestSimpleParallelEvents(unittest.TestCase):

    def setUp(self):
        pass

    def test_dent(self):
        """Simple parallel event
        """
        conv = ToPointsAndSegments()
   
        lines = [
            [[0., 0.], [10., 0.]],
            [[10., 0.], [10., 10.]],
            [[10., 10.], [1., 10.]],
            [[1., 10.], [1., 7.]],
            [[1., 7.], [3., 7.]],
            [[3., 7.], [3. , 6.5]],
            [[3., 6.5], [0., 6.5]],
            [[0., 6.5], [0., 0. ]]
        ]
        for line in lines:
            start, end = map(tuple, line)
            conv.add_point(start)
            conv.add_point(end)
            conv.add_segment(start, end)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT, shrink=True)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 23, len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 6, len(not_stopped)
        assert len(stopped) == 17, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )

    def test_handle_fan_cw(self):
        import json
        s = """{
"type": "FeatureCollection",
"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
                                                                                             
"features": [
             
{ "type": "Feature", "properties": { "id": 140092307709904.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.95871967752, -0.627450761189 ], [ -0.98800624377, -0.432206986189 ] ] } },
{ "type": "Feature", "properties": { "id": 140092307712976.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.98800624377, -0.432206986189 ], [ -0.985872786033, -0.431940303972 ] ] } },
{ "type": "Feature", "properties": { "id": 140092307713104.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.993971487578, -0.378572900681 ], [ -1.02090042121, -0.181094054061 ] ] } },
{ "type": "Feature", "properties": { "id": 140092307782672.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.985872786033, -0.431940303972 ], [ -0.991522629252, -0.37826679339 ] ] } },
{ "type": "Feature", "properties": { "id": 140092307782672.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.991522629252, -0.37826679339 ], [ -0.993971487578, -0.378572900681 ] ] } },
             
{ "type": "Feature", "properties": { "id": 140092307713104.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.02090042121, -0.181094054061 ], [5, 0] ] } },
{ "type": "Feature", "properties": { "id": 140092307709904.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.95871967752, -0.627450761189 ], [5,0]] } }
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
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 14, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 20, len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 5, len(not_stopped)
        assert len(stopped) == 15, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )



    def test_dent_unequal_wavefront_side(self):
        """Simple parallel event, starting from wavefront side
        """
        conv = ToPointsAndSegments()
   
        lines = [
            [[51046.4, 391515.7], [51046.3, 391516.65]],
            [[51047.95, 391513.05], [51047.55, 391515.85]],
            [[51047.55, 391515.85], [51046.4, 391515.7]],
            [[51047.45, 391516.8], [51046.9, 391520.8]],
            [[51046.3, 391516.65], [51047.45, 391516.8]],
            [[51055, 391521], [51057, 391514]],
            [[51046.9, 391520.8, ], [51055, 391521]],
            [[51047.95, 391513.05], [51057, 391514]]]
        for line in lines:
            start, end = map(tuple, line)
            conv.add_point(start)
            conv.add_point(end)
            conv.add_segment(start, end)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT, shrink=True)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 23, len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(
            filter(lambda v: v.stops_at is not None, skel.vertices)) == 13 + 4
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )


    def test_dent_unequal_wavefront_side_flipped_y(self):
        """Simple parallel event, starting from wavefront side
        """
        def flip_y(pt):
            return (pt[0], -pt[1])
        conv = ToPointsAndSegments()
        lines = [
            [[51046.4, 391515.7], [51046.3, 391516.65]],
            [[51047.95, 391513.05], [51047.55, 391515.85]],
            [[51047.55, 391515.85], [51046.4, 391515.7]],
            [[51047.45, 391516.8], [51046.9, 391520.8]],
            [[51046.3, 391516.65], [51047.45, 391516.8]],
            [[51055, 391521], [51057, 391514]],
            [[51046.9, 391520.8, ], [51055, 391521]],
            [[51047.95, 391513.05], [51057, 391514]]]
        for line in lines:
            start, end = map(tuple, map(flip_y, line))
            conv.add_point(start)
            conv.add_point(end)
            conv.add_segment(start, end)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT, shrink=True)
        #
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 23, len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(
            filter(lambda v: v.stops_at is not None, skel.vertices)) == 13 + 4
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )
  
  
    def test_square(self):
        conv = ToPointsAndSegments()
        polygon = [[(0,0), (10,0), (10,10), (0,10), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (4 + 4), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 5, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 4
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 4
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None:
                assert at_same_location((v.stop_node, v), v.stops_at)
  
  
    def test_rectangle(self):
        conv = ToPointsAndSegments()
        polygon = [[(0,0), (10,0), (10,5), (0,5), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (5 + 4), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 4
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 5
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )


    def test_dent_unequal_top(self):
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (10., 0), (10,20), (-0.5,20.), (-0.5,11.), (-1,11), (-1,10), (0,10), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (12 + 8), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 13, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 8
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 12
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )
  
  
    def test_dent_unequal_bottom(self):
        conv = ToPointsAndSegments()
        polygon = [[(-0.5, 0), (10., 0), (10,20), (0,20.), (0,11.), (-1,11), (-1,10), (-0.5,10), (-0.5,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (13 + 8), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 14, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 8
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 13
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


if __name__ == "__main__":
    if LOGGING:
        import logging
        import sys
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    unittest.main(verbosity=5)
