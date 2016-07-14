import unittest
 
from tri import ToPointsAndSegments
from grassfire import calc_skel
from grassfire.events import at_same_location


PAUSE = False
OUTPUT = False
LOGGING = False

class TestMoreAdvancedParallelEvents(unittest.TestCase):
    def setUp(self):
       pass


    def test_parallelogram(self):
        """Parallelogram with parallel wavefronts collapsing"""
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
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
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_mute_button_shape(self):
        conv = ToPointsAndSegments()
        polygon = [[(0,0), (3,0), (6,4), (10,4), (10,5), (6,5), (3,9), (0,9), (0,0)]]
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


    def test_butterfly_like(self):
        conv = ToPointsAndSegments()
        polygon = [[(0,0), (5,1), (10,0), (10,3), (5,2), (0,3), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (8 + 6), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 9, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 8
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )



    def test_butterfly_like2(self):
        conv = ToPointsAndSegments()
        polygon = [[(0,0), (5,1), (10,0), (10,1.5), (10,3), (5,2), (0,3), (0,0)]] #(0,1.5), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (9 + 7), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 10, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 7
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 9
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_corner_same(self):
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (10., 0), (10,20), (0,20.), (0.,11.), (-1,11), (-1,10), (0,10), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 13, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (12+8), len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 8
        assert len(
            filter(lambda v: v.stops_at is not None, skel.vertices)) == 12
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )


    def test_corner_same2(self):
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (10., 0), (10,20), (0,20.), (0.,11.), (-1,12), (-1,9), (0,10), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 15, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (16+6), len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(
            filter(lambda v: v.stops_at is not None, skel.vertices)) == 16
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )


    def test_corner_bottom_short(self):
        conv = ToPointsAndSegments()
        polygon = [[(-.5, 0), (10., 0), (10,20), (0,20.), (0.,11.), (-1,11), (-1,10), (-0.5,10), (-.5,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 14, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (13+8), len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 8
        assert len(
            filter(lambda v: v.stops_at is not None, skel.vertices)) == 13
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )


    def test_corner_top_short(self):
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (10., 0), (10,20), (-0.5,20.), (-0.5,11.), (-1,11), (-1,10), (0,10), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 13, len(skel.sk_nodes)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (12+8), len(skel.segments())
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 8
        assert len(
            filter(lambda v: v.stops_at is not None, skel.vertices)) == 12
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), "{} {} {}".format(id(v), v.stop_node.pos, v.position_at(v.stops_at) )


    def test_cross(self):
        # FIXME: Multiple skeleton nodes, because of fan that just collapses
        ring = [(0,0), (10, 0), (10,-10), (15, -10), (15,0), (25,0), (25,5), (15,5), (15,15), (10,15), (10,5), (0,5), (0,0)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (16 + 12), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 17, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 12
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 16
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
#         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
 
    unittest.main(verbosity=2)