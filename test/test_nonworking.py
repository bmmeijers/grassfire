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

#     def test_star_cocircular(self):
#         from math import cos, sin, pi
# 
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
#         for n in range(len(pts)):
#             #print n, n+1
#             l.append((pts[n], pts[(n+1)%len(pts)]))
#         conv = ToPointsAndSegments()
#         for line in l:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv)

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



#     def test_quad(self):
#         ring = [(1,0), (0, 5), (1,10), (2, 5), (1,0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv)
#     def test_diamant(self):
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(-1,0), (0,-1), (1,0), (0,5), (-1,0)]])
#         skel = calc_skel(conv)
#         assert len(skel.segments()) == 8
 
#     def test_diamantlike(self):
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(-15,0), (-1,0), (0,-1), (1,0), (15,0), (0,15), (-15,0)]])
#         skel = calc_skel(conv)
#         assert len(skel.segments()) == (7+6)
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
# 
#     def test_poly(self):
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(0, 0), (10, 0), (11, -1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
#         skel = calc_skel(conv)
# 
#     def test_cocircular(self):
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(0,1), (1,0), (2,0), (3,1), (3,2), (2,3), (1,3), (0,2), (0,1)]])
#         skel = calc_skel(conv)
# 
#     def test_cocircular1(self):
#         fail = (4,1) # substitute with this and we get a lot of simultaneous events!
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(0,1), (1,0), (3,0), fail, (4,3), (3,4), (1,4), (0,3), (0,1)]])
#         # FIXME: works but wrong:
#         # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
#         skel = calc_skel(conv)
# 
#     def test_parallellogram(self):
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
#         skel = calc_skel(conv)
# 


if __name__ == "__main__":

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