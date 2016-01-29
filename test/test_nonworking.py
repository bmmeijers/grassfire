import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

class TestSimultaneousEvents(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rocket(self):
        # FIXME: wrong while handling same event at other side of top of rocket
        # init skeleton structure
        conv = ToPointsAndSegments()
        polygon = [[(0., 10.), (1., 8.), (2.,10.), (2.1,3.), (1., 0.), (-.1,3), (0.,10.)]]
        conv.add_polygon(polygon)
        skel = calc_skel(conv)

###############################################################################
# PARALLEL EDGES IN THE INPUT, leading to problems 
# (e.g. nodes not on correct location)
###############################################################################

#     def test_cshape(self):
#         """Parallel c-shape wavefront"""
#         # FIXME: missing parallel piece of wavefront
#         # plus having a vertex too many
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, 0.0), (0.0, 3)]
#         l1 = [(0, 3), (5,3)]
#         l2 = [(0,0), (5,0)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)

############## FIXME:
## Last event is now 3-triangle, this leads to wrong skeleton!
#     def test_rect_extra_pt(self):
#         """" """
#         conv = ToPointsAndSegments()
#         polygon = [[(0, 0), (0., 10), (15,10), (15,0.), (2., 0.), (0,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv)

#     def test_tiny_v(self):
#         """Tiny V at bottom of square"""
#         conv = ToPointsAndSegments()
#         polygon = [[(-10, 0), (-10., 100.), (100.,100.), (100.,0.), (2., 0.), (1,-1), (0,0), (-10,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv)
#         assert len(skel.segments()) == (10+7)
#         positions = [n.pos for n in skel.sk_nodes]
#         # additional: 
#         # check if last node geerated internally is at (50,50)
#         assert (50,50) in positions
############## :FIXME

#     def test_2parallel_eq(self):
#         """2 parallel wavefront having equal size"""
#         conv = ToPointsAndSegments()
#         l0 = [(0, 0), (3,0)]
#         l1 = [(0, 1), (3,1)]
#         for line in l0, l1:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)

#     def test_2parallel_not_eq(self):
#         """2 parallel wavefront having different size"""
#         conv = ToPointsAndSegments()
#         l0 = [(0, 0), (3,0)]
#         l1 = [(1, 1), (2,1)]
#         for line in l0, l1:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)

# 
#     def test_3tris(self):
#         conv = ToPointsAndSegments()
#         polygons = [
#                     [[(0,0), (1,0), (0.5,-0.5), (0,0)]],
#                     [[(1,0.5), (2,0.5), (1.5,1), (1,0.5)]],
#                     [[(2,0), (3,0), (2.5,-0.5), (2,0)]],
#                     ]
# #         polygon = [[(0., 10.), (1., 8.), (2.,10.), (2.1,3.), (1., 0.), (-.1,3), (0.,10.)]]
#         for polygon in polygons:
#             conv.add_polygon(polygon)
#         skel = calc_skel(conv)

#     def test_3tris_infinte_flips(self):
#         """This configuration seems to lead to infinite series of events
#         """
#         conv = ToPointsAndSegments()
#         polygons = [
#                     [[(0,0), (1,0), (0.5,-0.5), (0,0)]],
#                     [[(1,3), (2,3), (1.5,3.5), (1,3)]],
#                     [[(2,0), (3,0), (2.5,-0.5), (2,0)]],
#                     ]
#         for polygon in polygons:
#             conv.add_polygon(polygon)
#         skel = calc_skel(conv)


#     def test_bottom_circle_top_square(self):
#         # bottom circle
#         from math import pi, cos, sin, degrees
#         ring = []
#         pi2 = 2 * pi
#         ct = 6
#         alpha = pi / ct 
#         print degrees(alpha)
#         for i in range(ct+1):
#             ring.append( (cos(pi+i*alpha), sin(pi+i*alpha)))
#         ring.extend([(1, 10), (-1,10)])
#         ring.append(ring[0])
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv)
#         assert len(skel.segments()) == 21
#         positions = [n.pos for n in skel.sk_nodes]
#         # additional: 
#         assert (0.,9.) in positions

#     def test_cross(self):
#         ring = [(0,0), (10, 0), (10,-10), (15, -10), (15,0), (25,0), (25,5), (15,5), (15,15), (10,15), (10,5), (0,5), (0,0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv)

#     def test_parallellogram(self):
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
#         skel = calc_skel(conv)
#         positions = [n.pos for n in skel.sk_nodes]
# #         # additional: 
#         assert (3.64128183429, 18.5688030572) in positions

if __name__ == "__main__":

    if True:
        import logging
        import sys
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    unittest.main()