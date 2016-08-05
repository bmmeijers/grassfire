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
                                      v.position_at(v.stops_at) )


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
        assert len(skel.segments()) == 24, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 13, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 10, len(not_stopped)
        assert len(stopped) == 14, len(stopped)
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
        assert len(skel.segments()) == 118, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 67, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(stopped) + len(not_stopped) == len(skel.segments())
        assert len(not_stopped) == 24, len(not_stopped)
        assert len(stopped) == 94, len(stopped)
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