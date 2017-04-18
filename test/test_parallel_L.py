from math import cos, sin, pi
from tri import ToPointsAndSegments
from grassfire import calc_skel
from grassfire.events import at_same_location

import logging
import sys
import unittest

PAUSE = False
OUTPUT = False
LOGGING = False


class TestMoreAdvancedParallelEvents(unittest.TestCase):
    def setUp(self):
       pass


    def test_L_0(self):
        poly = [[(0,0), (1,0), (2,0), (3,0), (4,0),
            (5,0),
            (5,-2),
            (5,-3),
            (5,-4), (5,-5), (6,-5), (6,1),
            (0,1), (0,0)
            ]]
        # convert to triangulation input
        conv = ToPointsAndSegments()
        conv.add_polygon(poly)
        # skeletonize / offset
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 39, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 27, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 33, len(filter(lambda v: v.stops_at is not None, skel.vertices))
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )
 
 
    def test_L_1(self):
        poly = [[(0,0), (1,0), (2,0), (3,0), (4,0), 
                 (5,0), 
                 (5,-1), 
                 (5,-2), 
                 (5,-3), 
                 (5,-4), (5,-5), (6,-5), (6,1), 
                 (0,1), (0,0)
                 ]]
        # convert to triangulation input
        conv = ToPointsAndSegments()
        conv.add_polygon(poly)
        # skeletonize / offset
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 42, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 29, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 42-6
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_L_2(self):
        poly = [[ 
        (5,0), (5,-1), (5,-2), (5,-3), (5,-4), (5,-5), (7,-5), (7,0), 
        (8,0), (9,0), (10,0), (11,0),
        (11,1), (5,1), (5,0)
        ]]
        # convert to triangulation input
        conv = ToPointsAndSegments()
        conv.add_polygon(poly)
        # skeletonize / offset
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 40, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 27, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 11
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 29
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
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
    unittest.main()