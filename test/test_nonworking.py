import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

class TestSimultaneousEvents(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

#     def test_infinite2(self):
#         """2 segments with terminal vertices at convex hull
#         """
#         conv = ToPointsAndSegments()
# #         l0 = [(0.0, -1.0), (5.0, -1.0)]
#         l1 = [(5.86602540378, 0.5), (3.36602540378, 4.83012701892)]
#         l2 = [(1.63397459622, 4.83012701892), (-0.866025403784, 0.5)]
#         for line in l1, l2:#, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         return

#     def test_cocirculair_2(self):
#         """2 segments with terminal vertices at convex hull
#         """
#         conv = ToPointsAndSegments()
# #         l0 = [(0.0, -1.0), (5.0, -1.0)]
#         l1 = [(0, 0.5), (1,1)]
#         l2 = [(1,1), (0.5, 0)]
#            
#         l3 = [(2.5, 3), (2,2)]
#         l4 = [(2, 2), (3,2.5)]
#         for line in l1, l2, l3, l4:#, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         return

#     def test_cocirculair_3(self):
#         """
#         """
#         conv = ToPointsAndSegments()
# #         l0 = [(0.0, -1.0), (5.0, -1.0)]
#         l = [ 
#         [(0, 0.5), (1,1)],
#         [(1,1), (0.5, 0)],
#         [(2.5, 3), (2,2)],
#         [(2, 2), (3,2.5)],
#         [(0,2.5), (1,2)],
#         [(1,2), (0.5,3)],
#         ]
#         for line in l:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         return

#     def test_cocirculair_4(self):
#         """
#         """
#         conv = ToPointsAndSegments()
# #         l0 = [(0.0, -1.0), (5.0, -1.0)]
#         l = [ 
#         [(0, 0.5), (1,1)],
#         [(1,1), (0.5, 0)],
#         [(2.5, 3), (2,2)],
#         [(2, 2), (3,2.5)],
#         [(0,2.5), (1,2)],
#         [(1,2), (0.5,3)],
#         [(2.5,0),(2,1)],
#         [(2,1),(3, 0.5)],
#         ]
#         for line in l:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         return


#     def test_2_vshape(self):
#         from math import cos, sin, pi
#         # misses event
#         N = 20
#         inc = 2*pi / N
#         pts = []
#         for i in range(N):
#             if i %2:
#                 pt = cos(i * inc), sin(i *inc)
#             else:
#                 pt = 2*cos(i * inc), 2*sin(i *inc)
#             pts.append(pt)
#         l = []
#         for n in (0,1, 4,5):
#             l.append((pts[n], pts[(n+1)%len(pts)]))
#         conv = ToPointsAndSegments()
#         for line in l:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)

#     def test_star_cocircular(self):
#         """4 v-shape lines pointing towards center
#         """
#         from math import cos, sin, pi
#         N = 20
#         inc = 2*pi / N
#         pts = []
#         for i in range(N):
#             if i %2:
#                 pt = cos(i * inc), sin(i *inc)
#             else:
#                 pt = 2*cos(i * inc), 2*sin(i *inc)
#             pts.append(pt)
#         l = []
#         for n in (0,1, 4,5, 8,9, 12,13, 16,17):
#             l.append((pts[n], pts[(n+1)%len(pts)]))
#         conv = ToPointsAndSegments()
#         for line in l:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         assert len(skel.segments()) == 45
#         # FIXME: The central skeleton node is generated twice -> 
#         # this is because opposite 1 triangle collapses
#         # which does not share any vertex with earlier collapsed triangles
#         assert len(skel.sk_nodes) == 26, len(skel.sk_nodes)

#     def test_infinite3(self):
#         """3 segments with terminal vertices at convex hull
#         """
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, -1.0), (5.0, -1.0)]
#         l1 = [(5.86602540378, 0.5), (3.36602540378, 4.83012701892)]
#         l2 = [(1.63397459622, 4.83012701892), (-0.866025403784, 0.5)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)
#         return

#     def test_rocket(self):
#         # init skeleton structure
#         conv = ToPointsAndSegments()
#         polygon = [[(0., 10.), (1., 8.), (2.,10.), (2.1,3.), (1., 0.), (-.1,3), (0.,10.)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv)


#     def test_cshape(self):
#         """Parallel c-shape wavefront"""
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
#         """2 parallel wavefront having same size"""
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
#         """This configuration seems to lead to infinite flip events
#         """
#         conv = ToPointsAndSegments()
#         polygons = [
#                     [[(0,0), (1,0), (0.5,-0.5), (0,0)]],
#                     [[(1,3), (2,3), (1.5,3.5), (1,3)]],
#                     [[(2,0), (3,0), (2.5,-0.5), (2,0)]],
#                     ]
# #         polygon = [[(0., 10.), (1., 8.), (2.,10.), (2.1,3.), (1., 0.), (-.1,3), (0.,10.)]]
#         for polygon in polygons:
#             conv.add_polygon(polygon)
#         skel = calc_skel(conv)

# 
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
#         assert len(skel.segments()) == (7+6)
# 

#     def test_cross(self):
#         ring = [(0,0), (10, 0), (10,-10), (15, -10), (15,0), (25,0), (25,5), (15,5), (15,15), (10,15), (10,5), (0,5), (0,0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv)

    def test_parallellogram(self):
        conv = ToPointsAndSegments()
        conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
        skel = calc_skel(conv)
        positions = [n.pos for n in skel.sk_nodes]
#         # additional: 
        assert (3.64128183429, 18.5688030572) in positions

if __name__ == "__main__":

    if False:
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