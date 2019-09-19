import unittest
 
from tri.delaunay.helpers import ToPointsAndSegments
from grassfire import calc_skel
from grassfire.events import at_same_location


PAUSE = True
OUTPUT = True
LOGGING = True

class TestMoreAdvancedParallelEvents(unittest.TestCase):
    def setUp(self):
       pass

    def test_T_capital_T(self):
        """Capital T, has more than one triangle in parallel fan
        """
        #    T
        ring = [(15.5055, 28.7004), (20.8063, 28.7004), (20.8063, 44.1211), (26.7445, 44.1211), (26.7445, 47.8328), (9.5668, 47.8328), (9.5668, 44.1211), (15.5055, 44.1211), (15.5055, 28.7004)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 21, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 14, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 8, len(not_stopped)
        assert len(stopped) == 13, len(stopped)
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
 
    unittest.main(verbosity=2)