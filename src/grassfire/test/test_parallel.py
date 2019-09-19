import unittest

from tri.delaunay.helpers import ToPointsAndSegments
from grassfire import calc_skel
from grassfire.events import at_same_location
from grassfire.test.intersection import segments_intersecting


PAUSE = False
OUTPUT = False
LOGGING = False


class TestMoreAdvancedParallelEvents(unittest.TestCase):

    def test_split_event_from_top10nl(self):
        """Top10NL data with parallel set of events, if the
        wavefront is not updated before calculating the new events
        this crashes (as we get a split event, instead of edge event
        without neighbors present...
        """
        poly = [[(181538.174, 316924.981),
                 (181536.571, 316927.503),
                 (181528.111, 316921.634),
                 (181519.449, 316910.678),
                 (181515.552, 316905.749),
                 (181512.149, 316901.445),
                 (181513.118, 316900.678),
                 (181514.492, 316899.592),
                 (181517.905, 316903.909),
                 (181521.802, 316908.838),
                 (181524.631, 316912.416),
                 (181530.179, 316919.433),
                 (181538.174, 316924.981)]]
        conv = ToPointsAndSegments()
        conv.add_polygon(poly)
        # skeletonize / offset
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 37, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 26, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        obtained = len(filter(lambda v: v.stops_at is None, skel.vertices))
        assert obtained == 8, obtained
        obtained = len(filter(lambda v: v.stops_at is not None, skel.vertices))
        assert obtained == 29, obtained
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at))

    def test_simple_parallel(self):
        segments = [((0.673575314055, 0.166666666667), (0.866025403784, 0.166666666667)), ((0.673575314055, -0.166666666667), (0.5, -0.0)), ((0.866025403784, -0.166666666667), (0.673575314055, -0.166666666667)), ((0.5, -0.0), (0.673575314055, 0.166666666667)), ((0.866025403784, 0.166666666667), (1.25, -0.0)), ((0.866025403784, -0.166666666667), (1.25, -0.0))]
        # convert to triangulation input
        conv = ToPointsAndSegments()
        for line in segments:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        # skeletonize / offset
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 13, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 8, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 6
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 7
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at))

    def test_stairs(self):
        """Stairs like shape
        """
        ###################################################
        # No parallel edges, but simultaneous event,
        # leading to infinite fast vertex, if not careful
        ###################################################
        conv = ToPointsAndSegments()
        polygon = [[(0,10), (2,10),(2,12),(4,12),(4,13),(5,13),(5,14),(3,14),(3,13),(1,13),(1,11),(0,11),(0,10)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 29, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 18, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 12, len(not_stopped)
        assert len(stopped) == 17, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_multiple_parallel2(self):
        """Parallelogram with parallel wavefronts collapsing"""
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0,0), (2,0), (4,0), (5,0),
                           (5,1), (3,1), (1,1), (0, 1), (0,0)
                           ]])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 21, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 14, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 8, len(not_stopped)
        assert len(stopped) == 21-8, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_rocket(self):
        """Two 2-triangles collapse at same time, sharing one vertex, that
        should lead to 1 new skeleton node and only 1 new kinetic vertex
        (3 original vertices are stopped, with 2 at same processing step).
        
        This test has a vertex that is started and stopped at the same time!
        """
        ###################################################
        # No parallel edges, but simultaneous event, 
        # leading to infinite fast vertex, if not careful
        ###################################################
        conv = ToPointsAndSegments()
        polygon = [[(0., 10.), (1., 8.), (2.,10.), (2.1,3.),
                    (1., 0.), (-.1,3), (0.,10.)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 14, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 8, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 6, len(not_stopped)
        assert len(stopped) == 8, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_3tris_handle_cw_ccw(self):
        """Splitting and then handle the fan
        """
        conv = ToPointsAndSegments()
        polygons = [
                    [[(0,0), (1,0), (0.5,-0.5), (0,0)]],
                    [[(1,3), (2,3), (1.5,3.5), (1,3)]],
                    [[(2,0), (3,0), (2.5,-0.5), (2,0)]],
                    ]
        for polygon in polygons:
            conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 24, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 8, len(not_stopped)
        assert len(stopped) == 16, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_weird_dent(self):
        conv = ToPointsAndSegments()
        polygon = [[(0.6, 5), (1,4.5), (3,4.5), (3,0), (7,0), (7,10), (3,10), (3,5.5), (1,5.5), (0.6,5)]]
#         polygon = [[(0.6, 5), (1,4.5), (3,4.5), (3,5.5), (1,5.5), (0.6,5)]]
        conv.add_polygon(polygon)
        # skeletonize / offset
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 24, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 7, len(not_stopped)
        assert len(stopped) == 17, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )
# 
# 
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
# 
# 
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


    def test_dent_equal(self):
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (10., 0), (10,20), (0,20.), (0.,11.), (-1,11), (-1,10), (0,10), (0,0)]]
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


    def test_rect_extra_pt2(self):
        """"Rectangle with extra point on straight (180 degrees) edge """
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (5., 0.), (10,0), (10,6.), (0,6), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 12, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 8, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 5, len(not_stopped)
        assert len(stopped) == 7, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )





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


    def test_rect_extra_pt(self):
        """"Rectangle with extra point on straight (180 degrees) edge """
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (0., 10), (15,10), (15,0.), (2., 0.), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 12, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 8, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 5
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 7
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_bottom_circle_top_square(self):
        """Bottom half is a circle, top is squarish, leading to parallel 
        wavefronts.
        
        Test contains kinetic vertex that is generated at certain time
        and later ended at same time; This means that segment does not
        have any length

        If choose_next_event is set up to first handle split events,
        this test breaks. Apparently then one triangle is not processed
        properly and survives until the end of the process
        """
        # bottom circle
        from math import pi, cos, sin, degrees
        ring = []
        pi2 = 2 * pi
        ct = 7
        alpha = pi / ct 
        for i in range(ct+1):
            ring.append( (cos(pi+i*alpha), sin(pi+i*alpha)))
        ring.extend([(1, 10), (-1,10)])
        ring.append(ring[0])
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 25, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 15, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 12, len(not_stopped)
        assert len(stopped) == 13, len(stopped)
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


    def test_multiple_parallel(self):
        """Parallelogram with parallel wavefronts collapsing"""
        # FIXME: Multiple skeleton nodes, because of fan that just collapses
        conv = ToPointsAndSegments()
        conv.add_polygon([[(0,0), (1,0), (2,0), (3,0), (4,0), (5,0),
                           (5,1), (4,1), (3,1), (2,1), (1,1), (0, 1), (0,0)
                           ]])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (17 + 12), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 18, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 12
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 17
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_corner_same_inwards(self):
        conv = ToPointsAndSegments()
        polygon = [[(0, 0), (10., 0), (10,20), (0,20.), (0.,11.), (1,11), (1,10), (0,10), (0,0)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == (16 + 5), len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 14, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        assert len(filter(lambda v: v.stops_at is None, skel.vertices)) == 5
        assert len(filter(lambda v: v.stops_at is not None, skel.vertices)) == 16
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


class TestRandomlyBreaking(unittest.TestCase):
    def setUp(self):
       pass

    def test_3tris(self):
        conv = ToPointsAndSegments()
        polygons = [
                    [[(0,0), (1,0), (0.5,-0.5), (0,0)]],
                    [[(1,0.5), (2,0.5), (1.5,1), (1,0.5)]],
                    [[(2,0), (3,0), (2.5,-0.5), (2,0)]],
                    ]
        for polygon in polygons:
            conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 24, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 8, len(not_stopped)
        assert len(stopped) == 16, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_3tris_split_handle(self):
        """One side that should just use handle and other side should handle_ccw
        """
        conv = ToPointsAndSegments()
        polygons = [
                    [[(1,0), (2,0), (1.5,-0.5), (1,0)]],
                    [[(1,3), (2,3), (1.5,3.5), (1,3)]],
                    [[(3,0), (4,0), (3.5,-0.5), (3,0)]],
                    ]
        for polygon in polygons:
            conv.add_polygon(polygon)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 24, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(stopped) + len(not_stopped) == len(skel.segments())
        assert len(not_stopped) == 7, len(not_stopped)
        assert len(stopped) == 17, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_koch_rec2(self):
        """Koch curve
        
        Note, contains 4 segments without length
        """
        ring = [(0.0, 0.0), (0.16666666666666663, 0.28867513459481287), (-1.1102230246251565e-16, 0.5773502691896257), (0.3333333333333332, 0.5773502691896258), (0.4999999999999998, 0.8660254037844388), (0.33333333333333304, 1.1547005383792517), (-2.7755575615628914e-16, 1.1547005383792517), (0.16666666666666635, 1.4433756729740645), (-3.885780586188048e-16, 1.7320508075688774), (0.3333333333333329, 1.7320508075688776), (0.4999999999999995, 2.0207259421636907), (0.6666666666666663, 1.732050807568878), (0.9999999999999996, 1.7320508075688783), (1.166666666666666, 2.020725942163691), (0.9999999999999993, 2.309401076758504), (1.3333333333333326, 2.309401076758504), (1.4999999999999991, 2.598076211353317), (1.6666666666666656, 2.309401076758504), (1.999999999999999, 2.309401076758504), (1.8333333333333321, 2.020725942163691), (1.9999999999999987, 1.7320508075688783), (2.333333333333332, 1.7320508075688783), (2.499999999999999, 2.020725942163691), (2.6666666666666656, 1.7320508075688783), (2.999999999999999, 1.7320508075688783), (2.833333333333332, 1.4433756729740654), (2.9999999999999987, 1.1547005383792526), (2.666666666666665, 1.1547005383792526), (2.4999999999999982, 0.8660254037844397), (2.6666666666666647, 0.5773502691896268), (2.9999999999999982, 0.5773502691896267), (2.8333333333333313, 0.2886751345948139), (2.999999999999998, 9.992007221626409e-16), (2.6666666666666643, 1.0400222821342193e-15), (2.4999999999999973, -0.2886751345948117), (2.333333333333331, 1.1657341758564144e-15), (1.9999999999999976, 1.2065557358279928e-15), (1.8333333333333308, -0.28867513459481153), (1.9999999999999973, -0.5773502691896245), (1.666666666666664, -0.5773502691896243), (1.4999999999999973, -0.866025403784437), (1.3333333333333308, -0.5773502691896242), (0.9999999999999976, -0.5773502691896242), (1.1666666666666643, -0.2886751345948113), (0.9999999999999976, 1.4988010832439613e-15), (0.6666666666666643, 1.5396226432155397e-15), (0.4999999999999975, -0.2886751345948112), (0.33333333333333093, 1.6653345369377348e-15), (0, 0)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 120, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 71, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(stopped) + len(not_stopped) == len(skel.segments())
        assert len(not_stopped) == 26, len(not_stopped)
        assert len(stopped) == 94, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )


    def test_capital_T(self):
        """Capital T, has more than one triangle in parallel fan
               
        Exhibits infinite event loop because of flipping...
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


    def test_koch_rec3(self):
        """Koch snowflake curve with recursion depth of 3
        """
        # contains MULTIPLE TRIANGLES IN PARALLEL FAN
        ring = [(0.0, 0.0), (0.05555555555555554, 0.09622504486493763), (-4.163336342344337e-17, 0.19245008972987523), (0.11111111111111106, 0.1924500897298753), (0.16666666666666657, 0.2886751345948129), (0.111111111111111, 0.3849001794597505), (-1.1102230246251565e-16, 0.3849001794597505), (0.05555555555555543, 0.4811252243246882), (-1.5265566588595902e-16, 0.5773502691896257), (0.11111111111111095, 0.5773502691896257), (0.16666666666666646, 0.6735753140545634), (0.22222222222222207, 0.5773502691896258), (0.33333333333333315, 0.5773502691896258), (0.3888888888888887, 0.6735753140545635), (0.3333333333333331, 0.769800358919501), (0.4444444444444442, 0.769800358919501), (0.4999999999999997, 0.8660254037844387), (0.44444444444444414, 0.9622504486493764), (0.33333333333333304, 0.9622504486493764), (0.38888888888888856, 1.058475493514314), (0.333333333333333, 1.1547005383792515), (0.22222222222222188, 1.1547005383792515), (0.16666666666666627, 1.058475493514314), (0.11111111111111074, 1.1547005383792515), (-3.608224830031759e-16, 1.1547005383792515), (0.05555555555555518, 1.250925583244189), (-4.0245584642661925e-16, 1.3471506281091266), (0.1111111111111107, 1.3471506281091266), (0.16666666666666624, 1.443375672974064), (0.11111111111111066, 1.5396007178390017), (-4.440892098500626e-16, 1.5396007178390017), (0.055555555555555095, 1.6358257627039392), (-4.85722573273506e-16, 1.7320508075688767), (0.11111111111111062, 1.7320508075688767), (0.16666666666666613, 1.8282758524338143), (0.22222222222222174, 1.7320508075688767), (0.3333333333333328, 1.7320508075688767), (0.38888888888888834, 1.8282758524338143), (0.33333333333333276, 1.9245008972987518), (0.44444444444444386, 1.9245008972987518), (0.4999999999999994, 2.0207259421636894), (0.555555555555555, 1.9245008972987518), (0.6666666666666661, 1.9245008972987518), (0.6111111111111106, 1.8282758524338143), (0.6666666666666662, 1.7320508075688767), (0.7777777777777772, 1.7320508075688767), (0.8333333333333328, 1.8282758524338143), (0.8888888888888884, 1.7320508075688767), (0.9999999999999996, 1.7320508075688767), (1.0555555555555551, 1.8282758524338143), (0.9999999999999996, 1.9245008972987518), (1.1111111111111107, 1.9245008972987518), (1.1666666666666663, 2.0207259421636894), (1.1111111111111107, 2.116950987028627), (0.9999999999999996, 2.116950987028627), (1.0555555555555551, 2.2131760318935645), (0.9999999999999996, 2.309401076758502), (1.1111111111111107, 2.309401076758502), (1.1666666666666663, 2.4056261216234396), (1.2222222222222219, 2.309401076758502), (1.333333333333333, 2.309401076758502), (1.3888888888888886, 2.4056261216234396), (1.333333333333333, 2.501851166488377), (1.4444444444444442, 2.501851166488377), (1.4999999999999998, 2.5980762113533147), (1.5555555555555554, 2.501851166488377), (1.6666666666666665, 2.501851166488377), (1.611111111111111, 2.4056261216234396), (1.6666666666666665, 2.309401076758502), (1.7777777777777777, 2.309401076758502), (1.8333333333333333, 2.4056261216234396), (1.8888888888888888, 2.309401076758502), (2.0, 2.309401076758502), (1.9444444444444444, 2.2131760318935645), (2.0, 2.116950987028627), (1.8888888888888888, 2.116950987028627), (1.8333333333333333, 2.0207259421636894), (1.8888888888888888, 1.9245008972987518), (2.0, 1.9245008972987518), (1.9444444444444444, 1.8282758524338143), (2.0, 1.7320508075688767), (2.111111111111111, 1.7320508075688767), (2.166666666666667, 1.8282758524338143), (2.2222222222222223, 1.7320508075688767), (2.3333333333333335, 1.7320508075688767), (2.3888888888888893, 1.8282758524338143), (2.333333333333334, 1.9245008972987518), (2.444444444444445, 1.9245008972987518), (2.500000000000001, 2.0207259421636894), (2.5555555555555562, 1.9245008972987518), (2.6666666666666674, 1.9245008972987518), (2.6111111111111116, 1.8282758524338143), (2.666666666666667, 1.7320508075688767), (2.777777777777778, 1.7320508075688767), (2.833333333333334, 1.8282758524338143), (2.8888888888888893, 1.7320508075688767), (3.0000000000000004, 1.7320508075688767), (2.9444444444444446, 1.6358257627039392), (3.0, 1.5396007178390017), (2.888888888888889, 1.5396007178390017), (2.833333333333333, 1.443375672974064), (2.8888888888888884, 1.3471506281091266), (2.9999999999999996, 1.3471506281091266), (2.9444444444444438, 1.250925583244189), (2.999999999999999, 1.1547005383792515), (2.888888888888888, 1.1547005383792515), (2.833333333333332, 1.058475493514314), (2.777777777777777, 1.1547005383792515), (2.6666666666666656, 1.1547005383792515), (2.61111111111111, 1.058475493514314), (2.666666666666665, 0.9622504486493763), (2.555555555555554, 0.9622504486493763), (2.4999999999999982, 0.8660254037844386), (2.5555555555555536, 0.7698003589195009), (2.6666666666666647, 0.7698003589195009), (2.611111111111109, 0.6735753140545633), (2.6666666666666643, 0.5773502691896256), (2.7777777777777755, 0.5773502691896256), (2.8333333333333313, 0.6735753140545632), (2.8888888888888866, 0.5773502691896255), (2.999999999999998, 0.5773502691896255), (2.944444444444442, 0.4811252243246879), (2.9999999999999973, 0.38490017945975025), (2.888888888888886, 0.38490017945975025), (2.8333333333333304, 0.28867513459481264), (2.8888888888888857, 0.19245008972987498), (2.999999999999997, 0.19245008972987493), (2.944444444444441, 0.09622504486493733), (2.9999999999999964, -3.191891195797325e-16), (2.8888888888888853, -3.055819329225397e-16), (2.8333333333333295, -0.0962250448649379), (2.777777777777774, -2.636779683484747e-16), (2.666666666666663, -2.500707816912819e-16), (2.611111111111107, -0.09622504486493784), (2.6666666666666625, -0.1924500897298755), (2.5555555555555514, -0.19245008972987546), (2.4999999999999956, -0.28867513459481303), (2.44444444444444, -0.1924500897298754), (2.333333333333329, -0.1924500897298754), (2.3888888888888844, -0.09622504486493777), (2.3333333333333286, -1.6653345369377348e-16), (2.2222222222222174, -1.5292626703658066e-16), (2.1666666666666616, -0.09622504486493774), (2.1111111111111063, -1.1102230246251565e-16), (1.9999999999999951, -9.741511580532284e-17), (1.9444444444444395, -0.09622504486493769), (1.9999999999999951, -0.19245008972987537), (1.888888888888884, -0.19245008972987532), (1.8333333333333284, -0.2886751345948129), (1.888888888888884, -0.3849001794597506), (1.9999999999999951, -0.3849001794597507), (1.9444444444444393, -0.48112522432468824), (1.9999999999999947, -0.577350269189626), (1.8888888888888835, -0.5773502691896258), (1.833333333333328, -0.6735753140545634), (1.7777777777777724, -0.5773502691896257), (1.6666666666666612, -0.5773502691896257), (1.6111111111111056, -0.6735753140545633), (1.6666666666666612, -0.7698003589195009), (1.55555555555555, -0.7698003589195008), (1.4999999999999944, -0.8660254037844384), (1.4444444444444389, -0.7698003589195007), (1.3333333333333277, -0.7698003589195007), (1.3888888888888833, -0.6735753140545631), (1.3333333333333277, -0.5773502691896255), (1.2222222222222165, -0.5773502691896255), (1.166666666666661, -0.6735753140545631), (1.1111111111111054, -0.5773502691896254), (0.9999999999999942, -0.5773502691896254), (1.0555555555555498, -0.48112522432468774), (0.9999999999999942, -0.38490017945975014), (1.1111111111111054, -0.3849001794597501), (1.166666666666661, -0.2886751345948124), (1.1111111111111054, -0.19245008972987482), (0.9999999999999942, -0.19245008972987482), (1.0555555555555498, -0.09622504486493719), (0.9999999999999942, 4.163336342344337e-16), (0.8888888888888831, 4.299408208916265e-16), (0.8333333333333275, -0.09622504486493716), (0.7777777777777719, 4.718447854656915e-16), (0.6666666666666607, 4.854519721228843e-16), (0.6111111111111052, -0.0962250448649371), (0.6666666666666606, -0.19245008972987476), (0.5555555555555496, -0.1924500897298747), (0.499999999999994, -0.2886751345948123), (0.4444444444444385, -0.19245008972987468), (0.3333333333333274, -0.19245008972987468), (0.3888888888888829, -0.09622504486493705), (0.3333333333333273, 5.551115123125783e-16), (0.22222222222221621, 5.687186989697711e-16), (0.1666666666666606, -0.09622504486493702), (0.11111111111110508, 6.106226635438361e-16), (0, 0)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)#, pause=False, output=False)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) in (512, 513, 514), len(skel.segments())
        # check the amount of skeleton nodes
        # FIXME Sometimes this number differs by one!!!
        assert len(skel.sk_nodes) in (315, 316), len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) in (54,55), len(not_stopped)
        assert len(stopped) in (512-54, 513-54, 514-54), len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )
        # there should not be intersecting segments
        self.assertEqual(segments_intersecting(skel.segments()), False)


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