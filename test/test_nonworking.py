import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

class TestSimultaneousEvents(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

#     def test_bottom_circle_top_square(self):
#         """Bottom half is a circle, top is squarish, leading to parallel 
#         wavefronts.
#         """
#         # bottom circle
#         from math import pi, cos, sin, degrees
#         ring = []
#         pi2 = 2 * pi
#         ct = 6
#         alpha = pi / ct 
#         for i in range(ct+1):
#             ring.append( (cos(pi+i*alpha), sin(pi+i*alpha)))
#         ring.extend([(1, 10), (-1,10)])
#         ring.append(ring[0])
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=False, output=False)
#         assert len(skel.segments()) == 20
#         assert len(skel.sk_nodes) == 12
#         # geometric embedding
# #         positions = [n.pos for n in skel.sk_nodes]
# #         assert frozenset(positions) == frozenset([(-3.3399458158564173e-17, -1.0), (-0.18181818181818182, 1.0), (-0.18181818181818182, -0.8181818181818182), (-0.090909090909091, -0.9756409825062615), (0.15745916432444335, -0.9090909090909091), (0.18181818181818182, 1.0), (0.18181818181818182, -0.8181818181818182), (-0.15745916432444343, -0.9090909090909091), (0.09090909090909079, -0.9756409825062616), (1.4901620439059292e-16, -0.8181818181818185), (1.0547467917351273e-17, -0.7942450004386554), (0.0, 0.8181818181818182)])

#     def test_rocket(self):
#         """Two 2-triangles collapse at same time, sharing one vertex, that
#         should lead to 1 new skeleton node and only 1 new kinetic vertex
#         (3 original vertices are stopped, with 2 at same processing step)
#         """
#         ###################################################
#         # No parallel edges, but simultaneous event, 
#         # leading to infinite fast vertex, if not careful
#         ###################################################
#         conv = ToPointsAndSegments()
#         polygon = [[(0., 10.), (1., 8.), (2.,10.), (2.1,3.),
#                     (1., 0.), (-.1,3), (0.,10.)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv, output=True, pause=True)
#         assert len(skel.segments()) == 7+6
#         assert len(skel.sk_nodes) == 8

#     def test_koch_rec1(self):
#         ring = [(0.0, 0.0), (0.4999999999999999, 0.8660254037844387), (-3.3306690738754696e-16, 1.7320508075688772), (0.9999999999999997, 1.7320508075688776), (1.4999999999999993, 2.5980762113533165), (1.9999999999999991, 1.7320508075688776), (2.999999999999999, 1.7320508075688774), (2.499999999999999, 0.8660254037844389), (2.9999999999999987, 1.1102230246251565e-16), (1.9999999999999987, 2.33486982377251e-16), (1.4999999999999982, -0.8660254037844382), (0.9999999999999984, 5.551115123125783e-16), (0,0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)#, pause=False, output=True)

#     def test_koch_rec2(self):
#         ring = [(0.0, 0.0), (0.16666666666666663, 0.28867513459481287), (-1.1102230246251565e-16, 0.5773502691896257), (0.3333333333333332, 0.5773502691896258), (0.4999999999999998, 0.8660254037844388), (0.33333333333333304, 1.1547005383792517), (-2.7755575615628914e-16, 1.1547005383792517), (0.16666666666666635, 1.4433756729740645), (-3.885780586188048e-16, 1.7320508075688774), (0.3333333333333329, 1.7320508075688776), (0.4999999999999995, 2.0207259421636907), (0.6666666666666663, 1.732050807568878), (0.9999999999999996, 1.7320508075688783), (1.166666666666666, 2.020725942163691), (0.9999999999999993, 2.309401076758504), (1.3333333333333326, 2.309401076758504), (1.4999999999999991, 2.598076211353317), (1.6666666666666656, 2.309401076758504), (1.999999999999999, 2.309401076758504), (1.8333333333333321, 2.020725942163691), (1.9999999999999987, 1.7320508075688783), (2.333333333333332, 1.7320508075688783), (2.499999999999999, 2.020725942163691), (2.6666666666666656, 1.7320508075688783), (2.999999999999999, 1.7320508075688783), (2.833333333333332, 1.4433756729740654), (2.9999999999999987, 1.1547005383792526), (2.666666666666665, 1.1547005383792526), (2.4999999999999982, 0.8660254037844397), (2.6666666666666647, 0.5773502691896268), (2.9999999999999982, 0.5773502691896267), (2.8333333333333313, 0.2886751345948139), (2.999999999999998, 9.992007221626409e-16), (2.6666666666666643, 1.0400222821342193e-15), (2.4999999999999973, -0.2886751345948117), (2.333333333333331, 1.1657341758564144e-15), (1.9999999999999976, 1.2065557358279928e-15), (1.8333333333333308, -0.28867513459481153), (1.9999999999999973, -0.5773502691896245), (1.666666666666664, -0.5773502691896243), (1.4999999999999973, -0.866025403784437), (1.3333333333333308, -0.5773502691896242), (0.9999999999999976, -0.5773502691896242), (1.1666666666666643, -0.2886751345948113), (0.9999999999999976, 1.4988010832439613e-15), (0.6666666666666643, 1.5396226432155397e-15), (0.4999999999999975, -0.2886751345948112), (0.33333333333333093, 1.6653345369377348e-15), (0, 0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)#, pause=False, output=True)

#     def test_koch_rec3(self):
#         ring = [(0.0, 0.0), (0.05555555555555554, 0.09622504486493763), (-4.163336342344337e-17, 0.19245008972987523), (0.11111111111111106, 0.1924500897298753), (0.16666666666666657, 0.2886751345948129), (0.111111111111111, 0.3849001794597505), (-1.1102230246251565e-16, 0.3849001794597505), (0.05555555555555543, 0.4811252243246882), (-1.5265566588595902e-16, 0.5773502691896257), (0.11111111111111095, 0.5773502691896257), (0.16666666666666646, 0.6735753140545634), (0.22222222222222207, 0.5773502691896258), (0.33333333333333315, 0.5773502691896258), (0.3888888888888887, 0.6735753140545635), (0.3333333333333331, 0.769800358919501), (0.4444444444444442, 0.769800358919501), (0.4999999999999997, 0.8660254037844387), (0.44444444444444414, 0.9622504486493764), (0.33333333333333304, 0.9622504486493764), (0.38888888888888856, 1.058475493514314), (0.333333333333333, 1.1547005383792515), (0.22222222222222188, 1.1547005383792515), (0.16666666666666627, 1.058475493514314), (0.11111111111111074, 1.1547005383792515), (-3.608224830031759e-16, 1.1547005383792515), (0.05555555555555518, 1.250925583244189), (-4.0245584642661925e-16, 1.3471506281091266), (0.1111111111111107, 1.3471506281091266), (0.16666666666666624, 1.443375672974064), (0.11111111111111066, 1.5396007178390017), (-4.440892098500626e-16, 1.5396007178390017), (0.055555555555555095, 1.6358257627039392), (-4.85722573273506e-16, 1.7320508075688767), (0.11111111111111062, 1.7320508075688767), (0.16666666666666613, 1.8282758524338143), (0.22222222222222174, 1.7320508075688767), (0.3333333333333328, 1.7320508075688767), (0.38888888888888834, 1.8282758524338143), (0.33333333333333276, 1.9245008972987518), (0.44444444444444386, 1.9245008972987518), (0.4999999999999994, 2.0207259421636894), (0.555555555555555, 1.9245008972987518), (0.6666666666666661, 1.9245008972987518), (0.6111111111111106, 1.8282758524338143), (0.6666666666666662, 1.7320508075688767), (0.7777777777777772, 1.7320508075688767), (0.8333333333333328, 1.8282758524338143), (0.8888888888888884, 1.7320508075688767), (0.9999999999999996, 1.7320508075688767), (1.0555555555555551, 1.8282758524338143), (0.9999999999999996, 1.9245008972987518), (1.1111111111111107, 1.9245008972987518), (1.1666666666666663, 2.0207259421636894), (1.1111111111111107, 2.116950987028627), (0.9999999999999996, 2.116950987028627), (1.0555555555555551, 2.2131760318935645), (0.9999999999999996, 2.309401076758502), (1.1111111111111107, 2.309401076758502), (1.1666666666666663, 2.4056261216234396), (1.2222222222222219, 2.309401076758502), (1.333333333333333, 2.309401076758502), (1.3888888888888886, 2.4056261216234396), (1.333333333333333, 2.501851166488377), (1.4444444444444442, 2.501851166488377), (1.4999999999999998, 2.5980762113533147), (1.5555555555555554, 2.501851166488377), (1.6666666666666665, 2.501851166488377), (1.611111111111111, 2.4056261216234396), (1.6666666666666665, 2.309401076758502), (1.7777777777777777, 2.309401076758502), (1.8333333333333333, 2.4056261216234396), (1.8888888888888888, 2.309401076758502), (2.0, 2.309401076758502), (1.9444444444444444, 2.2131760318935645), (2.0, 2.116950987028627), (1.8888888888888888, 2.116950987028627), (1.8333333333333333, 2.0207259421636894), (1.8888888888888888, 1.9245008972987518), (2.0, 1.9245008972987518), (1.9444444444444444, 1.8282758524338143), (2.0, 1.7320508075688767), (2.111111111111111, 1.7320508075688767), (2.166666666666667, 1.8282758524338143), (2.2222222222222223, 1.7320508075688767), (2.3333333333333335, 1.7320508075688767), (2.3888888888888893, 1.8282758524338143), (2.333333333333334, 1.9245008972987518), (2.444444444444445, 1.9245008972987518), (2.500000000000001, 2.0207259421636894), (2.5555555555555562, 1.9245008972987518), (2.6666666666666674, 1.9245008972987518), (2.6111111111111116, 1.8282758524338143), (2.666666666666667, 1.7320508075688767), (2.777777777777778, 1.7320508075688767), (2.833333333333334, 1.8282758524338143), (2.8888888888888893, 1.7320508075688767), (3.0000000000000004, 1.7320508075688767), (2.9444444444444446, 1.6358257627039392), (3.0, 1.5396007178390017), (2.888888888888889, 1.5396007178390017), (2.833333333333333, 1.443375672974064), (2.8888888888888884, 1.3471506281091266), (2.9999999999999996, 1.3471506281091266), (2.9444444444444438, 1.250925583244189), (2.999999999999999, 1.1547005383792515), (2.888888888888888, 1.1547005383792515), (2.833333333333332, 1.058475493514314), (2.777777777777777, 1.1547005383792515), (2.6666666666666656, 1.1547005383792515), (2.61111111111111, 1.058475493514314), (2.666666666666665, 0.9622504486493763), (2.555555555555554, 0.9622504486493763), (2.4999999999999982, 0.8660254037844386), (2.5555555555555536, 0.7698003589195009), (2.6666666666666647, 0.7698003589195009), (2.611111111111109, 0.6735753140545633), (2.6666666666666643, 0.5773502691896256), (2.7777777777777755, 0.5773502691896256), (2.8333333333333313, 0.6735753140545632), (2.8888888888888866, 0.5773502691896255), (2.999999999999998, 0.5773502691896255), (2.944444444444442, 0.4811252243246879), (2.9999999999999973, 0.38490017945975025), (2.888888888888886, 0.38490017945975025), (2.8333333333333304, 0.28867513459481264), (2.8888888888888857, 0.19245008972987498), (2.999999999999997, 0.19245008972987493), (2.944444444444441, 0.09622504486493733), (2.9999999999999964, -3.191891195797325e-16), (2.8888888888888853, -3.055819329225397e-16), (2.8333333333333295, -0.0962250448649379), (2.777777777777774, -2.636779683484747e-16), (2.666666666666663, -2.500707816912819e-16), (2.611111111111107, -0.09622504486493784), (2.6666666666666625, -0.1924500897298755), (2.5555555555555514, -0.19245008972987546), (2.4999999999999956, -0.28867513459481303), (2.44444444444444, -0.1924500897298754), (2.333333333333329, -0.1924500897298754), (2.3888888888888844, -0.09622504486493777), (2.3333333333333286, -1.6653345369377348e-16), (2.2222222222222174, -1.5292626703658066e-16), (2.1666666666666616, -0.09622504486493774), (2.1111111111111063, -1.1102230246251565e-16), (1.9999999999999951, -9.741511580532284e-17), (1.9444444444444395, -0.09622504486493769), (1.9999999999999951, -0.19245008972987537), (1.888888888888884, -0.19245008972987532), (1.8333333333333284, -0.2886751345948129), (1.888888888888884, -0.3849001794597506), (1.9999999999999951, -0.3849001794597507), (1.9444444444444393, -0.48112522432468824), (1.9999999999999947, -0.577350269189626), (1.8888888888888835, -0.5773502691896258), (1.833333333333328, -0.6735753140545634), (1.7777777777777724, -0.5773502691896257), (1.6666666666666612, -0.5773502691896257), (1.6111111111111056, -0.6735753140545633), (1.6666666666666612, -0.7698003589195009), (1.55555555555555, -0.7698003589195008), (1.4999999999999944, -0.8660254037844384), (1.4444444444444389, -0.7698003589195007), (1.3333333333333277, -0.7698003589195007), (1.3888888888888833, -0.6735753140545631), (1.3333333333333277, -0.5773502691896255), (1.2222222222222165, -0.5773502691896255), (1.166666666666661, -0.6735753140545631), (1.1111111111111054, -0.5773502691896254), (0.9999999999999942, -0.5773502691896254), (1.0555555555555498, -0.48112522432468774), (0.9999999999999942, -0.38490017945975014), (1.1111111111111054, -0.3849001794597501), (1.166666666666661, -0.2886751345948124), (1.1111111111111054, -0.19245008972987482), (0.9999999999999942, -0.19245008972987482), (1.0555555555555498, -0.09622504486493719), (0.9999999999999942, 4.163336342344337e-16), (0.8888888888888831, 4.299408208916265e-16), (0.8333333333333275, -0.09622504486493716), (0.7777777777777719, 4.718447854656915e-16), (0.6666666666666607, 4.854519721228843e-16), (0.6111111111111052, -0.0962250448649371), (0.6666666666666606, -0.19245008972987476), (0.5555555555555496, -0.1924500897298747), (0.499999999999994, -0.2886751345948123), (0.4444444444444385, -0.19245008972987468), (0.3333333333333274, -0.19245008972987468), (0.3888888888888829, -0.09622504486493705), (0.3333333333333273, 5.551115123125783e-16), (0.22222222222221621, 5.687186989697711e-16), (0.1666666666666606, -0.09622504486493702), (0.11111111111110508, 6.106226635438361e-16), (0, 0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)#, pause=False, output=True)

#     def test_handle_fan_just_collapse(self):
#         import json
#         s = """{
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                    
# "features": [
#    
# { "type": "Feature", "properties": { "id": 140092307709904.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.95871967752, -0.627450761189 ], [ -0.98800624377, -0.432206986189 ] ] } },
# { "type": "Feature", "properties": { "id": 140092307712976.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.98800624377, -0.432206986189 ], [ -0.985872786033, -0.431940303972 ] ] } },
# { "type": "Feature", "properties": { "id": 140092307713104.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.993971487578, -0.378572900681 ], [ -1.02090042121, -0.181094054061 ] ] } },
# { "type": "Feature", "properties": { "id": 140092307782672.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.985872786033, -0.431940303972 ], [ -0.991522629252, -0.37826679339 ] ] } },
# { "type": "Feature", "properties": { "id": 140092307782672.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.991522629252, -0.37826679339 ], [ -0.993971487578, -0.378572900681 ] ] } },
#    
# { "type": "Feature", "properties": { "id": 140092307713104.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.02090042121, -0.181094054061 ], [5, 0] ] } },
# { "type": "Feature", "properties": { "id": 140092307709904.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.95871967752, -0.627450761189 ], [5,0]] } }
# ]
# }"""
#         x = json.loads(s)
#         # parse segments from geo-json
#         segments = []
#         for y in x['features']:
#             segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
#         # convert to triangulation input
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         # skeletonize / offset
#         skel = calc_skel(conv, pause=True, output=True)



#     def test_goes_church(self):
#         """ Church in Goes, Singelstraat """
#         import json
#         s = """{
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                     
# "features": [
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51076.45, 391503.5 ], [ 51075.45, 391503.4 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51075.45, 391503.4 ], [ 51075.25, 391504.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51075.25, 391504.65 ], [ 51073.85, 391504.45 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51085.65, 391504.8 ], [ 51084.55, 391504.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51076.25, 391504.9 ], [ 51076.45, 391503.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51073.85, 391504.45 ], [ 51073.7, 391505.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51090.35, 391507.3 ], [ 51086.8, 391506.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51091.2, 391506.4 ], [ 51090.4, 391506.4 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51086.8, 391506.5 ], [ 51085.5, 391506.3 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51091.1, 391507.45 ], [ 51091.2, 391506.4 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51086.8, 391506.85 ], [ 51086.8, 391506.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51090.4, 391506.4 ], [ 51090.35, 391507.3 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51084.55, 391504.7 ], [ 51084.45, 391506.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51084.45, 391506.05 ], [ 51076.25, 391504.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51073.7, 391505.55 ], [ 51075.0, 391505.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51085.5, 391506.3 ], [ 51085.65, 391504.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51092.6, 391507.7 ], [ 51091.1, 391507.45 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.9, 391511.9 ], [ 51046.75, 391512.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.75, 391512.9 ], [ 51047.95, 391513.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.55, 391511.0 ], [ 51048.2, 391510.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.2, 391510.95 ], [ 51048.05, 391512.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.55, 391511.9 ], [ 51053.55, 391511.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51100.15, 391508.6 ], [ 51099.65, 391508.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51049.9, 391510.95 ], [ 51048.95, 391510.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.95, 391510.0 ], [ 51072.75, 391511.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51074.4, 391510.2 ], [ 51072.95, 391510.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.95, 391510.8 ], [ 51048.55, 391511.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.6, 391511.7 ], [ 51049.9, 391510.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.75, 391511.5 ], [ 51074.2, 391511.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51075.0, 391505.7 ], [ 51074.4, 391510.2 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.45, 391512.5 ], [ 51050.6, 391511.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51053.55, 391511.75 ], [ 51053.4, 391512.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.05, 391512.05 ], [ 51046.9, 391511.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.4, 391513.05 ], [ 51054.55, 391511.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51053.4, 391512.9 ], [ 51050.45, 391512.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.5, 391513.4 ], [ 51063.45, 391513.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.6, 391512.7 ], [ 51058.55, 391512.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51058.55, 391512.55 ], [ 51058.4, 391513.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.45, 391513.8 ], [ 51059.6, 391512.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51058.4, 391513.6 ], [ 51054.4, 391513.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.4, 391515.7 ], [ 51046.3, 391516.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.9, 391520.8 ], [ 51045.7, 391520.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.65, 391520.65 ], [ 51109.95, 391520.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.35, 391521.0 ], [ 51109.95, 391520.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.15, 391520.45 ], [ 51109.35, 391521.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.55, 391521.75 ], [ 51046.7, 391521.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.7, 391520.65 ], [ 51045.55, 391521.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.6, 391524.7 ], [ 51109.85, 391521.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.65, 391520.65 ], [ 51109.85, 391521.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.6, 391524.7 ], [ 51111.85, 391524.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.75, 391526.2 ], [ 51111.85, 391524.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.75, 391526.2 ], [ 51110.6, 391526.1 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.6, 391526.1 ], [ 51110.45, 391527.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.5, 391527.8 ], [ 51110.45, 391527.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.4, 391528.95 ], [ 51110.55, 391528.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.5, 391527.8 ], [ 51111.4, 391528.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.95, 391513.05 ], [ 51047.55, 391515.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51073.75, 391514.95 ], [ 51072.2, 391514.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.2, 391514.75 ], [ 51072.05, 391515.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51099.65, 391508.5 ], [ 51098.0, 391514.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51091.75, 391514.2 ], [ 51092.6, 391507.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51074.2, 391511.7 ], [ 51073.75, 391514.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51098.5, 391519.3 ], [ 51100.15, 391508.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51063.45, 391513.25 ], [ 51063.3, 391514.3 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.35, 391514.55 ], [ 51064.5, 391513.4 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51063.3, 391514.3 ], [ 51059.45, 391513.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.45, 391514.15 ], [ 51068.45, 391514.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51098.0, 391514.6 ], [ 51091.75, 391514.2 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.3, 391515.3 ], [ 51069.45, 391514.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.45, 391514.05 ], [ 51068.3, 391515.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.3, 391515.05 ], [ 51064.35, 391514.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.05, 391515.65 ], [ 51069.3, 391515.3 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.55, 391515.85 ], [ 51046.4, 391515.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.45, 391516.8 ], [ 51046.9, 391520.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.3, 391516.65 ], [ 51047.45, 391516.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.1, 391519.3 ], [ 51106.75, 391519.2 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51106.75, 391519.2 ], [ 51106.6, 391520.2 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51106.6, 391520.2 ], [ 51098.5, 391519.3 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.1, 391519.3 ], [ 51108.15, 391520.45 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.6, 391535.0 ], [ 51043.5, 391536.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.5, 391536.05 ], [ 51044.6, 391536.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.1, 391538.6 ], [ 51042.95, 391539.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.35, 391540.9 ], [ 51044.5, 391541.35 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.5, 391541.35 ], [ 51045.45, 391541.45 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51049.25, 391541.65 ], [ 51050.35, 391541.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.05, 391539.7 ], [ 51043.9, 391540.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.95, 391539.55 ], [ 51044.05, 391539.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.5, 391540.15 ], [ 51049.45, 391540.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.9, 391540.85 ], [ 51044.35, 391540.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.4, 391540.75 ], [ 51046.5, 391540.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.45, 391541.45 ], [ 51046.4, 391540.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51049.45, 391540.55 ], [ 51049.25, 391541.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.35, 391541.8 ], [ 51050.5, 391540.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.15, 391543.1 ], [ 51060.25, 391543.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.3, 391542.75 ], [ 51064.15, 391543.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51065.3, 391542.95 ], [ 51068.15, 391543.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51065.15, 391544.05 ], [ 51065.3, 391542.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.15, 391543.9 ], [ 51065.15, 391544.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.0, 391544.5 ], [ 51069.5, 391544.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.5, 391543.9 ], [ 51109.45, 391543.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.15, 391543.55 ], [ 51068.0, 391544.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.5, 391543.9 ], [ 51108.4, 391546.1 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.4, 391546.1 ], [ 51109.15, 391546.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.5, 391544.7 ], [ 51069.1, 391547.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.1, 391547.8 ], [ 51067.65, 391547.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.0, 391547.5 ], [ 51109.15, 391546.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.25, 391541.55 ], [ 51109.6, 391542.3 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51055.45, 391541.45 ], [ 51059.35, 391541.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.35, 391541.25 ], [ 51054.2, 391542.35 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51055.3, 391542.5 ], [ 51055.45, 391541.45 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.25, 391541.55 ], [ 51108.35, 391539.35 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.5, 391540.7 ], [ 51054.35, 391541.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.2, 391542.35 ], [ 51055.3, 391542.5 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.35, 391541.95 ], [ 51059.15, 391543.1 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51060.25, 391543.25 ], [ 51060.35, 391542.2 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.6, 391542.3 ], [ 51109.45, 391543.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51060.35, 391542.2 ], [ 51064.3, 391542.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.35, 391537.05 ], [ 51110.0, 391537.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.6, 391536.25 ], [ 51044.25, 391538.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.9, 391538.3 ], [ 51110.0, 391537.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.25, 391538.75 ], [ 51043.1, 391538.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.9, 391538.3 ], [ 51109.85, 391538.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.85, 391538.6 ], [ 51108.35, 391539.35 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.8, 391533.55 ], [ 51110.55, 391533.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.25, 391530.85 ], [ 51045.35, 391531.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.35, 391531.0 ], [ 51044.8, 391535.15 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.2, 391532.6 ], [ 51109.8, 391533.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.4, 391529.85 ], [ 51044.25, 391530.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.6, 391530.05 ], [ 51044.4, 391529.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.2, 391532.6 ], [ 51109.55, 391530.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.7, 391521.9 ], [ 51045.6, 391530.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.55, 391528.85 ], [ 51109.55, 391530.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.55, 391533.8 ], [ 51110.35, 391534.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.8, 391535.15 ], [ 51043.6, 391535.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.65, 391534.95 ], [ 51110.35, 391534.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.35, 391537.05 ], [ 51109.65, 391534.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51066.75, 391553.8 ], [ 51066.6, 391555.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51088.2, 391551.9 ], [ 51094.7, 391552.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51076.9, 391557.8 ], [ 51078.05, 391557.95 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.95, 391555.2 ], [ 51067.8, 391556.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.1, 391555.35 ], [ 51077.1, 391556.6 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.8, 391549.25 ], [ 51068.2, 391554.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.85, 391555.05 ], [ 51103.45, 391553.75 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.2, 391554.0 ], [ 51066.75, 391553.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51087.65, 391557.55 ], [ 51088.2, 391551.9 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51066.6, 391555.0 ], [ 51067.95, 391555.2 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.9, 391556.7 ], [ 51069.1, 391555.35 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.8, 391556.55 ], [ 51068.9, 391556.7 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51078.25, 391556.65 ], [ 51087.65, 391557.55 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51077.1, 391556.6 ], [ 51076.9, 391557.8 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51078.05, 391557.95 ], [ 51078.25, 391556.65 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51104.05, 391549.0 ], [ 51104.15, 391549.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.65, 391547.6 ], [ 51067.45, 391549.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51095.35, 391547.85 ], [ 51104.05, 391549.0 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.0, 391547.5 ], [ 51113.35, 391548.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.45, 391549.05 ], [ 51068.8, 391549.25 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51094.7, 391552.0 ], [ 51095.35, 391547.85 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.85, 391555.05 ], [ 51113.35, 391548.05 ] ] } },
# { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51104.15, 391549.0 ], [ 51103.45, 391553.75 ] ] } }
# ]
# }"""
#         x = json.loads(s)
#         # parse segments from geo-json
#         segments = []
#         for y in x['features']:
#             segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
#         # convert to triangulation input
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         # skeletonize / offset
#         skel = calc_skel(conv, pause=False, output=True)



#     def test_does_this_break(self):
#         import json
#         s = """{
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                   
# "features": [
# { "type": "Feature", "properties": { "id": 139664900038544.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.725310399997397, 391507.68993699998828 ], [ 51042.455319, 391516.15654599998379 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900067600.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51038.632411799997499, 391542.760162 ], [ 51039.83351180000318, 391542.923948 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900067600.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51039.83351180000318, 391542.923948 ], [ 51039.671322499998496, 391544.167399 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900067728.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51039.671322499998496, 391544.167399 ], [ 51041.540670499998669, 391544.37510499998461 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900067728.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.540670499998669, 391544.37510499998461 ], [ 51041.69552799999656, 391544.839677 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900067856.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.69552799999656, 391544.839677 ], [ 51046.507679299997108, 391545.34621899999911 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900069712.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.918327300001692, 391507.107457 ], [ 51044.982255199996871, 391506.68801799998619 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900069840.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.982255199996871, 391506.68801799998619 ], [ 51044.826051600000937, 391507.83351199998287 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900069840.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.826051600000937, 391507.83351199998287 ], [ 51043.725310399997397, 391507.68993699998828 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070160.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.455319, 391516.15654599998379 ], [ 51042.565606500000285, 391516.170332 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070288.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.473354800000379, 391516.453288 ], [ 51041.308878199997707, 391524.99278299999423 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070416.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.308878199997707, 391524.99278299999423 ], [ 51042.464014700002735, 391525.14345299999695 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070480.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.464014700002735, 391525.14345299999695 ], [ 51042.389055500003451, 391525.69883299997309 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070480.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.389055500003451, 391525.69883299997309 ], [ 51041.245075500002713, 391525.5081699999864 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070800.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51041.245075500002713, 391525.5081699999864 ], [ 51040.449382300001162, 391530.812791 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900070800.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51040.449382300001162, 391530.812791 ], [ 51040.220387200002733, 391530.78416699997615 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900071248.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 51040.220387200002733, 391530.78416699997615 ], [ 51039.75987090000126, 391535.619588 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900071248.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51039.75987090000126, 391535.619588 ], [ 51038.632411799997499, 391542.760162 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900144272.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.565606500000285, 391516.170332 ], [ 51042.535010500003409, 391516.46099499997217 ] ] } },
# { "type": "Feature", "properties": { "id": 139664900144272.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.535010500003409, 391516.46099499997217 ], [ 51042.473354800000379, 391516.453288 ] ] } }
# ]
# }"""
#         x = json.loads(s)
#         # parse segments from geo-json
#         segments = []
#         for y in x['features']:
#             segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
#         # convert to triangulation input
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         # skeletonize / offset
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_church_goes_backwards(self):
#         import json
#         s = """{
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                 
# "features": [
# { "type": "Feature", "properties": { "id": 140617678876624.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.03211626131, -0.724784452109 ], [ -1.08729623971, -0.356917929421 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678877136.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.48254937906, 0.882090589183 ], [ -0.233248381804, 0.916086179723 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678877200.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.233248381804, 0.916086179723 ], [ -0.233459861296, 0.91735505667 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678877264.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.233459861296, 0.91735505667 ], [ 0.140866489239, 0.966180232834 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678877520.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.09086597347, 0.886294642843 ], [ 1.20638373187, 0.347211770298 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678877648.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.13829354329, -0.284616409211 ], [ 1.17779919729, -0.336467580082 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678877904.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.146358241315, -0.924533440835 ], [ -0.220196444276, -0.961188909385 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878032.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.220196444276, -0.961188909385 ], [ -0.224778045908, -0.932553899185 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878032.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.224778045908, -0.932553899185 ], [ -0.268448698292, -0.938792563812 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878160.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.717660282995, -0.720212899697 ], [ -0.857025389793, -0.742217916564 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878288.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.857025389793, -0.742217916564 ], [ -0.869627077784, -0.735917072567 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878288.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.869627077784, -0.735917072567 ], [ -0.997141880112, -0.754133472895 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878416.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.997141880112, -0.754133472895 ], [ -1.00168528179, -0.720815193913 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678878416.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.00168528179, -0.720815193913 ], [ -1.03211626131, -0.724784452109 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678879376.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.583468112093, -0.313619618256 ], [ -0.583953931975, -0.309894999159 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678879824.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.872983367568, 0.477416222987 ], [ -0.872983367568, 0.477416222987 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678880656.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.08479551005, -0.356605338213 ], [ -1.11400682659, -0.142389016868 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678880848.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.11400682659, -0.142389016868 ], [ -1.1252322352, -0.0675529594892 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678880848.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.1252322352, -0.0675529594892 ], [ -1.13518276927, -0.0687967762474 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881360.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.13518276927, -0.0687967762474 ], [ -1.15434575613, 0.132414585878 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881360.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.15434575613, 0.132414585878 ], [ -1.19629222453, 0.398075552404 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881424.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.19629222453, 0.398075552404 ], [ -1.16044587573, 0.402963690877 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881424.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.16044587573, 0.402963690877 ], [ -1.16526140432, 0.439882743398 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881552.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.16526140432, 0.439882743398 ], [ -1.08794893459, 0.448473017821 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881552.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.08794893459, 0.448473017821 ], [ -1.08346673202, 0.461919625518 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881680.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -1.08346673202, 0.461919625518 ], [ -0.880891578639, 0.483243325882 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678881744.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.880891578639, 0.483243325882 ], [ -0.872983367568, 0.477416222987 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678882576.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.518680701604, 0.835816672159 ], [ -0.478076219264, 0.841832151024 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678882576.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.478076219264, 0.841832151024 ], [ -0.48254937906, 0.882090589183 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678883472.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.484184059286, 0.535784445233 ], [ -0.484725763829, 0.539215240674 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678883472.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.589131043023, 0.520042397676 ], [ -0.484184059286, 0.535784445233 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678884176.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.01521078708, -0.482575801907 ], [ 0.778562928758, -0.50010527289 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678884176.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.778562928758, -0.50010527289 ], [ 0.81907694837, -0.762832551586 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678921872.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.08493864386, 0.139812940499 ], [ 1.09980519606, 0.14156194664 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678921936.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.07666384998, 0.183255608372 ], [ 1.08493864386, 0.139812940499 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678923600.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.140866489239, 0.966180232834 ], [ 0.147405257878, 0.923678236678 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678923600.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.147405257878, 0.923678236678 ], [ 0.423655660549, 0.950127743315 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678923664.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.423655660549, 0.950127743315 ], [ 0.440555845049, 0.776516757098 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678923664.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.440555845049, 0.776516757098 ], [ 0.527747625068, 0.777858169098 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678923728.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.527747625068, 0.777858169098 ], [ 0.524680514836, 0.798670702817 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678923792.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.524680514836, 0.798670702817 ], [ 1.09086597347, 0.886294642843 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678924368.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.0657391087, 0.329429116794 ], [ 1.07612362158, 0.23596850086 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678924368.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.20638373187, 0.347211770298 ], [ 1.0657391087, 0.329429116794 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678924496.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.07226645667, 0.233825631464 ], [ 1.07666384998, 0.183255608372 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678924496.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.07612362158, 0.23596850086 ], [ 1.07226645667, 0.233825631464 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678925136.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.11191324296, 0.0583274951578 ], [ 1.13829354329, -0.284616409211 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678925712.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.01758278652, -0.428019814814 ], [ 1.01521078708, -0.482575801907 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678925712.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.17779919729, -0.336467580082 ], [ 1.01758278652, -0.428019814814 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678946576.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.10707952431, 0.0579071717966 ], [ 1.11191324296, 0.0583274951578 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678946576.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 1.09980519606, 0.14156194664 ], [ 1.10707952431, 0.0579071717966 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678947664.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.81907694837, -0.762832551586 ], [ 0.554649547515, -0.815718031744 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678947664.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.554649547515, -0.815718031744 ], [ 0.558939157253, -0.860758933993 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678947792.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.558939157253, -0.860758933993 ], [ 0.397617317451, -0.860758933993 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678947792.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.397617317451, -0.860758933993 ], [ 0.400529150028, -0.889877259759 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678948112.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.400529150028, -0.889877259759 ], [ 0.144729432556, -0.913131779524 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678948112.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.144729432556, -0.913131779524 ], [ 0.146358241315, -0.924533440835 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678948560.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.311650169624, -0.652756410361 ], [ -0.448272667831, -0.672273910099 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678948560.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.294635085856, -0.780369538628 ], [ -0.311650169624, -0.652756410361 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678948688.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.290136451895, -0.779749037392 ], [ -0.294635085856, -0.780369538628 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678948688.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.268448698292, -0.938792563812 ], [ -0.290136451895, -0.779749037392 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678949584.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.442879031644, -0.292037416838 ], [ -0.443313840095, -0.288703885381 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678949712.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.335696915992, 0.17830435778 ], [ -0.334831748823, 0.173329646555 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678949904.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.481656674163, 0.539624452629 ], [ -0.518680701604, 0.835816672159 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678949904.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.484725763829, 0.539215240674 ], [ -0.481656674163, 0.539624452629 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678950032.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.588992874851, 0.518983108355 ], [ -0.589131043023, 0.520042397676 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678950032.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.738786818583, 0.498556661479 ], [ -0.588992874851, 0.518983108355 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678966992.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.738424849471, 0.496475339088 ], [ -0.738786818583, 0.498556661479 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678966992.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.873078448703, 0.478113484645 ], [ -0.738424849471, 0.496475339088 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678969168.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.448272667831, -0.672273910099 ], [ -0.479184210904, -0.676689844833 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678969232.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.479184210904, -0.676689844833 ], [ -0.479050775158, -0.677712852213 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678969296.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.479050775158, -0.677712852213 ], [ -0.710379608713, -0.712412177252 ] ] } },
# { "type": "Feature", "properties": { "id": 140617678969360.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.710379608713, -0.712412177252 ], [ -0.717660282995, -0.720212899697 ] ] } }
# ]
# }"""
#         x = json.loads(s)
#         # parse segments from geo-json
#         segments = []
#         for y in x['features']:
#             segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
#         # convert to triangulation input
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         # skeletonize / offset
#         skel = calc_skel(conv, pause=True, output=True)







#     def test_goes(self):
#         segments = (
# ( ( 51076.45, 391503.5 ), ( 51075.45, 391503.4 ) ),
# ( ( 51075.45, 391503.4 ), ( 51075.25, 391504.65 ) ),
# ( ( 51075.25, 391504.65 ), ( 51073.85, 391504.45 ) ),
# ( ( 51085.65, 391504.8 ), ( 51084.55, 391504.7 ) ),
# ( ( 51076.25, 391504.9 ), ( 51076.45, 391503.5 ) ),
# ( ( 51073.85, 391504.45 ), ( 51073.7, 391505.55 ) ),
# ( ( 51090.35, 391507.3 ), ( 51086.8, 391506.85 ) ),
# ( ( 51091.2, 391506.4 ), ( 51090.4, 391506.4 ) ),
# ( ( 51086.8, 391506.5 ), ( 51085.5, 391506.3 ) ),
# ( ( 51091.1, 391507.45 ), ( 51091.2, 391506.4 ) ),
# ( ( 51086.8, 391506.85 ), ( 51086.8, 391506.5 ) ),
# ( ( 51090.4, 391506.4 ), ( 51090.35, 391507.3 ) ),
# ( ( 51084.55, 391504.7 ), ( 51084.45, 391506.05 ) ),
# ( ( 51084.45, 391506.05 ), ( 51076.25, 391504.9 ) ),
# ( ( 51073.7, 391505.55 ), ( 51075.0, 391505.7 ) ),
# ( ( 51085.5, 391506.3 ), ( 51085.65, 391504.8 ) ),
# ( ( 51092.6, 391507.7 ), ( 51091.1, 391507.45 ) ),
# ( ( 51046.9, 391511.9 ), ( 51046.75, 391512.9 ) ),
# ( ( 51046.75, 391512.9 ), ( 51047.95, 391513.05 ) ),
# ( ( 51102.4, 391509.15 ), ( 51100.15, 391508.6 ) ),
# ( ( 51103.9, 391510.2 ), ( 51102.4, 391509.15 ) ),
# ( ( 51048.55, 391511.0 ), ( 51048.2, 391510.95 ) ),
# ( ( 51048.2, 391510.95 ), ( 51048.05, 391512.05 ) ),
# ( ( 51054.55, 391511.9 ), ( 51053.55, 391511.75 ) ),
# ( ( 51100.15, 391508.6 ), ( 51099.65, 391508.5 ) ),
# ( ( 51049.9, 391510.95 ), ( 51048.95, 391510.8 ) ),
# ( ( 51072.95, 391510.0 ), ( 51072.75, 391511.5 ) ),
# ( ( 51074.4, 391510.2 ), ( 51072.95, 391510.0 ) ),
# ( ( 51048.95, 391510.8 ), ( 51048.55, 391511.0 ) ),
# ( ( 51050.6, 391511.7 ), ( 51049.9, 391510.95 ) ),
# ( ( 51072.75, 391511.5 ), ( 51074.2, 391511.7 ) ),
# ( ( 51075.0, 391505.7 ), ( 51074.4, 391510.2 ) ),
# ( ( 51050.45, 391512.5 ), ( 51050.6, 391511.7 ) ),
# ( ( 51053.55, 391511.75 ), ( 51053.4, 391512.9 ) ),
# ( ( 51048.05, 391512.05 ), ( 51046.9, 391511.9 ) ),
# ( ( 51054.4, 391513.05 ), ( 51054.55, 391511.9 ) ),
# ( ( 51053.4, 391512.9 ), ( 51050.45, 391512.5 ) ),
# ( ( 51064.5, 391513.4 ), ( 51063.45, 391513.25 ) ),
# ( ( 51059.6, 391512.7 ), ( 51058.55, 391512.55 ) ),
# ( ( 51058.55, 391512.55 ), ( 51058.4, 391513.6 ) ),
# ( ( 51059.45, 391513.8 ), ( 51059.6, 391512.7 ) ),
# ( ( 51058.4, 391513.6 ), ( 51054.4, 391513.05 ) ),
# ( ( 51046.4, 391515.7 ), ( 51046.3, 391516.65 ) ),
# ( ( 51046.9, 391520.8 ), ( 51045.7, 391520.65 ) ),
# ( ( 51110.65, 391520.65 ), ( 51109.95, 391520.25 ) ),
# ( ( 51109.35, 391521.0 ), ( 51109.95, 391520.25 ) ),
# ( ( 51108.15, 391520.45 ), ( 51109.35, 391521.0 ) ),
# ( ( 51045.55, 391521.75 ), ( 51046.7, 391521.9 ) ),
# ( ( 51045.7, 391520.65 ), ( 51045.55, 391521.75 ) ),
# ( ( 51110.6, 391524.7 ), ( 51109.85, 391521.7 ) ),
# ( ( 51110.65, 391520.65 ), ( 51109.85, 391521.7 ) ),
# ( ( 51110.6, 391524.7 ), ( 51111.85, 391524.9 ) ),
# ( ( 51111.75, 391526.2 ), ( 51111.85, 391524.9 ) ),
# ( ( 51111.75, 391526.2 ), ( 51110.6, 391526.1 ) ),
# ( ( 51110.6, 391526.1 ), ( 51110.45, 391527.65 ) ),
# ( ( 51111.5, 391527.8 ), ( 51110.45, 391527.65 ) ),
# ( ( 51111.4, 391528.95 ), ( 51110.55, 391528.85 ) ),
# ( ( 51111.5, 391527.8 ), ( 51111.4, 391528.95 ) ),
# ( ( 51047.95, 391513.05 ), ( 51047.55, 391515.85 ) ),
# ( ( 51073.75, 391514.95 ), ( 51072.2, 391514.75 ) ),
# ( ( 51072.2, 391514.75 ), ( 51072.05, 391515.65 ) ),
# ( ( 51099.65, 391508.5 ), ( 51098.0, 391514.6 ) ),
# ( ( 51091.75, 391514.2 ), ( 51092.6, 391507.7 ) ),
# ( ( 51109.4, 391514.1 ), ( 51103.9, 391510.2 ) ),
# ( ( 51074.2, 391511.7 ), ( 51073.75, 391514.95 ) ),
# ( ( 51103.9, 391510.2 ), ( 51102.45, 391519.7 ) ),
# ( ( 51098.5, 391519.3 ), ( 51100.15, 391508.6 ) ),
# ( ( 51063.45, 391513.25 ), ( 51063.3, 391514.3 ) ),
# ( ( 51064.35, 391514.55 ), ( 51064.5, 391513.4 ) ),
# ( ( 51063.3, 391514.3 ), ( 51059.45, 391513.8 ) ),
# ( ( 51069.45, 391514.15 ), ( 51068.45, 391514.05 ) ),
# ( ( 51098.0, 391514.6 ), ( 51091.75, 391514.2 ) ),
# ( ( 51069.3, 391515.3 ), ( 51069.45, 391514.15 ) ),
# ( ( 51068.45, 391514.05 ), ( 51068.3, 391515.05 ) ),
# ( ( 51068.3, 391515.05 ), ( 51064.35, 391514.55 ) ),
# ( ( 51072.05, 391515.65 ), ( 51069.3, 391515.3 ) ),
# ( ( 51047.55, 391515.85 ), ( 51046.4, 391515.7 ) ),
# ( ( 51117.5, 391516.3 ), ( 51109.4, 391514.1 ) ),
# ( ( 51047.45, 391516.8 ), ( 51046.9, 391520.8 ) ),
# ( ( 51046.3, 391516.65 ), ( 51047.45, 391516.8 ) ),
# ( ( 51108.1, 391519.3 ), ( 51106.75, 391519.2 ) ),
# ( ( 51102.45, 391519.7 ), ( 51098.5, 391519.3 ) ),
# ( ( 51106.75, 391519.2 ), ( 51106.6, 391520.2 ) ),
# ( ( 51106.6, 391520.2 ), ( 51098.5, 391519.3 ) ),
# ( ( 51108.1, 391519.3 ), ( 51108.15, 391520.45 ) ),
# ( ( 51043.6, 391535.0 ), ( 51043.5, 391536.05 ) ),
# ( ( 51043.5, 391536.05 ), ( 51044.6, 391536.25 ) ),
# ( ( 51043.1, 391538.6 ), ( 51042.95, 391539.55 ) ),
# ( ( 51044.35, 391540.9 ), ( 51044.5, 391541.35 ) ),
# ( ( 51044.5, 391541.35 ), ( 51045.45, 391541.45 ) ),
# ( ( 51049.25, 391541.65 ), ( 51050.35, 391541.8 ) ),
# ( ( 51044.05, 391539.7 ), ( 51043.9, 391540.85 ) ),
# ( ( 51042.95, 391539.55 ), ( 51044.05, 391539.7 ) ),
# ( ( 51046.5, 391540.15 ), ( 51049.45, 391540.55 ) ),
# ( ( 51043.9, 391540.85 ), ( 51044.35, 391540.9 ) ),
# ( ( 51046.4, 391540.75 ), ( 51046.5, 391540.15 ) ),
# ( ( 51045.45, 391541.45 ), ( 51046.4, 391540.75 ) ),
# ( ( 51049.45, 391540.55 ), ( 51049.25, 391541.65 ) ),
# ( ( 51050.35, 391541.8 ), ( 51050.5, 391540.7 ) ),
# ( ( 51059.15, 391543.1 ), ( 51060.25, 391543.25 ) ),
# ( ( 51064.3, 391542.75 ), ( 51064.15, 391543.9 ) ),
# ( ( 51065.3, 391542.95 ), ( 51068.15, 391543.55 ) ),
# ( ( 51065.15, 391544.05 ), ( 51065.3, 391542.95 ) ),
# ( ( 51064.15, 391543.9 ), ( 51065.15, 391544.05 ) ),
# ( ( 51068.0, 391544.5 ), ( 51069.5, 391544.7 ) ),
# ( ( 51108.5, 391543.9 ), ( 51109.45, 391543.65 ) ),
# ( ( 51068.15, 391543.55 ), ( 51068.0, 391544.5 ) ),
# ( ( 51108.5, 391543.9 ), ( 51108.4, 391546.1 ) ),
# ( ( 51108.4, 391546.1 ), ( 51109.15, 391546.15 ) ),
# ( ( 51069.5, 391544.7 ), ( 51069.1, 391547.8 ) ),
# ( ( 51069.1, 391547.8 ), ( 51067.65, 391547.6 ) ),
# ( ( 51109.0, 391547.5 ), ( 51109.15, 391546.15 ) ),
# ( ( 51108.25, 391541.55 ), ( 51109.6, 391542.3 ) ),
# ( ( 51055.45, 391541.45 ), ( 51059.35, 391541.95 ) ),
# ( ( 51054.35, 391541.25 ), ( 51054.2, 391542.35 ) ),
# ( ( 51055.3, 391542.5 ), ( 51055.45, 391541.45 ) ),
# ( ( 51108.25, 391541.55 ), ( 51108.35, 391539.35 ) ),
# ( ( 51050.5, 391540.7 ), ( 51054.35, 391541.25 ) ),
# ( ( 51054.2, 391542.35 ), ( 51055.3, 391542.5 ) ),
# ( ( 51059.35, 391541.95 ), ( 51059.15, 391543.1 ) ),
# ( ( 51060.25, 391543.25 ), ( 51060.35, 391542.2 ) ),
# ( ( 51109.6, 391542.3 ), ( 51109.45, 391543.65 ) ),
# ( ( 51060.35, 391542.2 ), ( 51064.3, 391542.75 ) ),
# ( ( 51109.35, 391537.05 ), ( 51110.0, 391537.15 ) ),
# ( ( 51044.6, 391536.25 ), ( 51044.25, 391538.75 ) ),
# ( ( 51109.9, 391538.3 ), ( 51110.0, 391537.15 ) ),
# ( ( 51044.25, 391538.75 ), ( 51043.1, 391538.6 ) ),
# ( ( 51114.7, 391538.3 ), ( 51109.9, 391538.3 ) ),
# ( ( 51109.9, 391538.3 ), ( 51109.85, 391538.6 ) ),
# ( ( 51109.85, 391538.6 ), ( 51108.35, 391539.35 ) ),
# ( ( 51109.8, 391533.55 ), ( 51110.55, 391533.8 ) ),
# ( ( 51044.25, 391530.85 ), ( 51045.35, 391531.0 ) ),
# ( ( 51045.35, 391531.0 ), ( 51044.8, 391535.15 ) ),
# ( ( 51109.2, 391532.6 ), ( 51109.8, 391533.55 ) ),
# ( ( 51044.4, 391529.85 ), ( 51044.25, 391530.85 ) ),
# ( ( 51045.6, 391530.05 ), ( 51044.4, 391529.85 ) ),
# ( ( 51109.2, 391532.6 ), ( 51109.55, 391530.0 ) ),
# ( ( 51116.0, 391529.6 ), ( 51117.5, 391516.3 ) ),
# ( ( 51046.7, 391521.9 ), ( 51045.6, 391530.05 ) ),
# ( ( 51116.0, 391529.6 ), ( 51111.4, 391528.95 ) ),
# ( ( 51110.55, 391528.85 ), ( 51109.55, 391530.0 ) ),
# ( ( 51110.55, 391533.8 ), ( 51110.35, 391534.85 ) ),
# ( ( 51044.8, 391535.15 ), ( 51043.6, 391535.0 ) ),
# ( ( 51109.65, 391534.95 ), ( 51110.35, 391534.85 ) ),
# ( ( 51109.35, 391537.05 ), ( 51109.65, 391534.95 ) ),
# ( ( 51114.7, 391538.3 ), ( 51116.0, 391529.6 ) ),
# ( ( 51066.75, 391553.8 ), ( 51066.6, 391555.0 ) ),
# ( ( 51088.2, 391551.9 ), ( 51094.7, 391552.0 ) ),
# ( ( 51076.9, 391557.8 ), ( 51078.05, 391557.95 ) ),
# ( ( 51067.95, 391555.2 ), ( 51067.8, 391556.55 ) ),
# ( ( 51069.1, 391555.35 ), ( 51077.1, 391556.6 ) ),
# ( ( 51068.8, 391549.25 ), ( 51068.2, 391554.0 ) ),
# ( ( 51103.45, 391553.75 ), ( 51098.5, 391553.45 ) ),
# ( ( 51098.5, 391553.45 ), ( 51089.3, 391553.25 ) ),
# ( ( 51111.85, 391555.05 ), ( 51103.45, 391553.75 ) ),
# ( ( 51068.2, 391554.0 ), ( 51066.75, 391553.8 ) ),
# ( ( 51087.65, 391557.55 ), ( 51088.2, 391551.9 ) ),
# ( ( 51066.6, 391555.0 ), ( 51067.95, 391555.2 ) ),
# ( ( 51068.9, 391556.7 ), ( 51069.1, 391555.35 ) ),
# ( ( 51067.8, 391556.55 ), ( 51068.9, 391556.7 ) ),
# ( ( 51078.25, 391556.65 ), ( 51087.65, 391557.55 ) ),
# ( ( 51077.1, 391556.6 ), ( 51076.9, 391557.8 ) ),
# ( ( 51078.05, 391557.95 ), ( 51078.25, 391556.65 ) ),
# ( ( 51087.2, 391561.25 ), ( 51087.05, 391561.25 ) ),
# ( ( 51081.65, 391563.15 ), ( 51076.55, 391562.45 ) ),
# ( ( 51087.05, 391561.25 ), ( 51086.5, 391565.2 ) ),
# ( ( 51081.4, 391564.6 ), ( 51081.65, 391563.15 ) ),
# ( ( 51091.3, 391562.6 ), ( 51110.1, 391565.85 ) ),
# ( ( 51090.45, 391566.55 ), ( 51091.3, 391562.6 ) ),
# ( ( 51086.5, 391565.2 ), ( 51081.4, 391564.6 ) ),
# ( ( 51086.95, 391565.15 ), ( 51086.5, 391565.2 ) ),
# ( ( 51082.6, 391559.55 ), ( 51076.75, 391559.15 ) ),
# ( ( 51097.45, 391558.95 ), ( 51110.95, 391561.1 ) ),
# ( ( 51097.3, 391561.2 ), ( 51097.45, 391558.95 ) ),
# ( ( 51110.95, 391561.1 ), ( 51111.85, 391555.05 ) ),
# ( ( 51089.3, 391553.25 ), ( 51088.35, 391559.85 ) ),
# ( ( 51082.6, 391560.75 ), ( 51082.6, 391559.55 ) ),
# ( ( 51097.3, 391561.2 ), ( 51087.45, 391559.75 ) ),
# ( ( 51087.45, 391559.75 ), ( 51087.2, 391561.25 ) ),
# ( ( 51088.35, 391559.85 ), ( 51097.3, 391561.2 ) ),
# ( ( 51097.3, 391561.2 ), ( 51091.7, 391560.75 ) ),
# ( ( 51087.05, 391561.25 ), ( 51082.6, 391560.75 ) ),
# ( ( 51110.1, 391565.85 ), ( 51110.95, 391561.1 ) ),
# ( ( 51076.75, 391559.15 ), ( 51076.55, 391562.45 ) ),
# ( ( 51091.3, 391562.6 ), ( 51091.7, 391560.75 ) ),
# ( ( 51090.35, 391567.35 ), ( 51090.45, 391566.55 ) ),
# ( ( 51076.55, 391562.45 ), ( 51076.15, 391568.75 ) ),
# ( ( 51086.95, 391565.15 ), ( 51086.45, 391570.2 ) ),
# ( ( 51076.15, 391568.75 ), ( 51076.1, 391568.75 ) ),
# ( ( 51090.35, 391567.35 ), ( 51089.95, 391570.5 ) ),
# ( ( 51076.1, 391568.75 ), ( 51076.05, 391569.9 ) ),
# ( ( 51086.45, 391570.2 ), ( 51076.15, 391568.75 ) ),
# ( ( 51087.95, 391576.1 ), ( 51085.1, 391575.7 ) ),
# ( ( 51089.85, 391575.1 ), ( 51092.4, 391575.6 ) ),
# ( ( 51092.4, 391575.6 ), ( 51093.3, 391575.75 ) ),
# ( ( 51089.85, 391575.1 ), ( 51089.55, 391576.15 ) ),
# ( ( 51085.1, 391575.7 ), ( 51085.05, 391576.15 ) ),
# ( ( 51093.3, 391575.75 ), ( 51093.2, 391576.45 ) ),
# ( ( 51087.95, 391576.1 ), ( 51089.55, 391576.15 ) ),
# ( ( 51087.0, 391586.5 ), ( 51085.3, 391586.1 ) ),
# ( ( 51085.45, 391582.4 ), ( 51085.3, 391586.1 ) ),
# ( ( 51093.2, 391576.45 ), ( 51107.7, 391580.05 ) ),
# ( ( 51089.8, 391579.75 ), ( 51088.55, 391579.45 ) ),
# ( ( 51075.55, 391575.6 ), ( 51074.7, 391581.15 ) ),
# ( ( 51107.7, 391580.05 ), ( 51108.5, 391575.3 ) ),
# ( ( 51085.05, 391576.15 ), ( 51084.85, 391580.35 ) ),
# ( ( 51106.9, 391584.05 ), ( 51107.7, 391580.05 ) ),
# ( ( 51092.55, 391580.45 ), ( 51089.8, 391579.75 ) ),
# ( ( 51085.55, 391580.45 ), ( 51084.85, 391580.35 ) ),
# ( ( 51088.0, 391583.7 ), ( 51088.55, 391579.45 ) ),
# ( ( 51085.55, 391580.45 ), ( 51085.45, 391582.4 ) ),
# ( ( 51106.9, 391584.05 ), ( 51092.55, 391580.45 ) ),
# ( ( 51074.7, 391581.15 ), ( 51085.45, 391582.4 ) ),
# ( ( 51088.0, 391583.7 ), ( 51088.45, 391579.8 ) ),
# ( ( 51074.7, 391581.15 ), ( 51073.85, 391586.8 ) ),
# ( ( 51088.45, 391579.8 ), ( 51087.0, 391586.5 ) ),
# ( ( 51087.4, 391589.05 ), ( 51105.0, 391593.9 ) ),
# ( ( 51102.3, 391606.85 ), ( 51101.4, 391606.7 ) ),
# ( ( 51070.95, 391611.35 ), ( 51071.65, 391611.45 ) ),
# ( ( 51070.95, 391611.35 ), ( 51076.6, 391612.05 ) ),
# ( ( 51071.65, 391611.45 ), ( 51076.6, 391612.05 ) ),
# ( ( 51101.1, 391615.45 ), ( 51102.3, 391606.85 ) ),
# ( ( 51078.65, 391612.35 ), ( 51079.55, 391612.45 ) ),
# ( ( 51076.6, 391612.05 ), ( 51078.65, 391612.35 ) ),
# ( ( 51076.6, 391612.05 ), ( 51079.55, 391612.45 ) ),
# ( ( 51079.55, 391612.45 ), ( 51079.5, 391612.75 ) ),
# ( ( 51079.5, 391612.75 ), ( 51086.0, 391613.6 ) ),
# ( ( 51086.0, 391613.6 ), ( 51094.7, 391614.7 ) ),
# ( ( 51094.7, 391614.7 ), ( 51094.7, 391614.6 ) ),
# ( ( 51094.7, 391614.6 ), ( 51101.1, 391615.45 ) ),
# ( ( 51102.45, 391599.2 ), ( 51102.45, 391599.15 ) ),
# ( ( 51102.45, 391599.15 ), ( 51088.2, 391597.3 ) ),
# ( ( 51073.05, 391594.15 ), ( 51086.35, 391595.85 ) ),
# ( ( 51088.2, 391597.3 ), ( 51073.0, 391595.3 ) ),
# ( ( 51086.35, 391595.85 ), ( 51087.4, 391589.05 ) ),
# ( ( 51101.4, 391606.7 ), ( 51102.45, 391599.15 ) ),
# ( ( 51101.4, 391606.7 ), ( 51102.45, 391599.2 ) ),
# ( ( 51073.0, 391595.3 ), ( 51070.95, 391611.35 ) ),
# ( ( 51088.2, 391597.3 ), ( 51086.0, 391613.6 ) ),
# ( ( 51073.85, 391586.8 ), ( 51073.8, 391587.25 ) ),
# ( ( 51079.75, 391588.0 ), ( 51073.8, 391587.25 ) ),
# ( ( 51079.75, 391588.0 ), ( 51079.7, 391587.55 ) ),
# ( ( 51088.0, 391583.7 ), ( 51087.5, 391588.2 ) ),
# ( ( 51106.1, 391588.25 ), ( 51088.0, 391583.7 ) ),
# ( ( 51106.1, 391588.25 ), ( 51106.9, 391584.05 ) ),
# ( ( 51105.0, 391593.9 ), ( 51106.1, 391588.25 ) ),
# ( ( 51073.8, 391587.25 ), ( 51073.05, 391594.15 ) ),
# ( ( 51079.7, 391587.55 ), ( 51087.5, 391588.2 ) ),
# ( ( 51087.4, 391589.05 ), ( 51087.5, 391588.2 ) ),
# ( ( 51092.9, 391572.65 ), ( 51093.15, 391571.25 ) ),
# ( ( 51109.3, 391570.6 ), ( 51110.1, 391565.85 ) ),
# ( ( 51076.05, 391569.9 ), ( 51075.6, 391575.05 ) ),
# ( ( 51109.3, 391570.6 ), ( 51090.35, 391567.35 ) ),
# ( ( 51093.15, 391571.25 ), ( 51089.95, 391570.5 ) ),
# ( ( 51108.5, 391575.3 ), ( 51109.3, 391570.6 ) ),
# ( ( 51075.6, 391575.05 ), ( 51075.55, 391575.6 ) ),
# ( ( 51092.9, 391572.65 ), ( 51108.5, 391575.3 ) ),
# ( ( 51092.4, 391575.6 ), ( 51092.9, 391572.65 ) ),
# ( ( 51085.05, 391576.15 ), ( 51075.6, 391575.05 ) ),
# ( ( 51104.05, 391549.0 ), ( 51104.15, 391549.0 ) ),
# ( ( 51067.65, 391547.6 ), ( 51067.45, 391549.05 ) ),
# ( ( 51095.35, 391547.85 ), ( 51104.05, 391549.0 ) ),
# ( ( 51109.0, 391547.5 ), ( 51113.35, 391548.05 ) ),
# ( ( 51113.35, 391548.05 ), ( 51114.7, 391538.3 ) ),
# ( ( 51067.45, 391549.05 ), ( 51068.8, 391549.25 ) ),
# ( ( 51094.7, 391552.0 ), ( 51095.35, 391547.85 ) ),
# ( ( 51111.85, 391555.05 ), ( 51113.35, 391548.05 ) ),
# ( ( 51104.15, 391549.0 ), ( 51103.45, 391553.75 ) )
# )
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         print conv.points
#         skel = calc_skel(conv, pause=True, output=True)


#     def test_capital_T(self):
#         """Capital T, has more than one triangle in parallel fan"""
#         #    T
#         ring = [(15.5055, 28.7004), (20.8063, 28.7004), (20.8063, 44.1211), (26.7445, 44.1211), (26.7445, 47.8328), (9.5668, 47.8328), (9.5668, 44.1211), (15.5055, 44.1211), (15.5055, 28.7004)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)#, pause=False, output=True)

#     def test_missing_event(self):
#         [(82.9195, 34.8762), 
#          (82.9195, 36.123), 
#          (82.8224828125, 37.4505816406), 
#          (82.53454375, 38.658784375), 
#          (82.0603515625, 39.7298449219), 
#          (81.404575, 40.646), 
#          (80.5718828125, 41.3894863281), 
#          (79.56694375, 41.942540625), 
#          (78.3944265625, 42.2873996094), 
#          (77.059, 42.4063),
#           (76.2952375244, 42.3687171631), 
#           (75.5838064453, 42.2585341797), 
#           (74.9242850342, 42.0795993408), 
#           (74.3162515625, 41.8357609375), 
#           (73.7592843018, 41.5308672607), 
#           (73.2529615234, 41.1687666016), 
#           (72.3905625, 40.2883375), 
#           (71.7256806641, 39.2252599609), (71.2549421875, 38.0103203125), (70.9749732422, 36.6743048828), 
#           (70.8824, 35.248), (70.9637001953, 33.823009375), (71.2144078125, 32.50744375), 
#           (71.6447333984, 31.3261375), (72.2648875, 30.303925), (73.0850806641, 29.465640625), 
#           (73.5733826904, 29.1232322266), (74.1155234375, 28.83611875), (74.7127792236, 28.6074044922), 
#           (75.3664263672, 28.44019375), (76.848, 28.3027), (77.9991910156, 28.3734771484), 
#  
#         (79.058021875, 28.5858296875), (80.0117917969, 28.9397892578), (80.8478, 29.4353875), 
#         (81.5533457031, 30.0726560547), (82.115728125, 30.8516265625), (82.5222464844, 31.7723306641), 
#         (82.7602, 32.8348), (80.1098, 32.8348), (79.9671755859, 32.1632625), 
#         (79.7567359375, 31.59635), (79.4750064453, 31.1294125), 
#         (79.1185125, 30.7578),]
#         # fixme; misses an event


#     def test_half_U(self):
#         """Misses event, and has disconnected vertex"""
#         polys = [
#         [(38.3852, 32.0156), (39.2659501953, 32.0912681641), 
#          (42.1678701172, 35.1549208984), 
#          (42.2309, 35.9922), (42.2309, 47.834), 
#          (47.5316, 47.834), (47.5316, 35.7273), 
#          (47.4732092773, 34.7657740479), 
#          (47.3213726562, 33.8784173828),  
#          (38.3852, 32.0156)],
#         ]
#         conv = ToPointsAndSegments()
#         for ring in polys:
#             conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)#, pause=False, output=True)


#     def test_tudelft_logo(self):
#         polys = [
# #          # flame
# #         [(28.2387, 57.1504), (27.7545962891, 57.0337472656), (27.2828078125, 56.993484375), (26.8394935547, 57.0375167969), (26.4408125, 57.17375), (26.1029236328, 57.4100894531), (25.8419859375, 57.754440625), (25.6741583984, 58.2147089844), (25.6156, 58.7988), (25.6856849121, 59.2881812744), (25.8839386719, 59.7683330078), (26.1934848145, 60.2400170654), (26.597446875, 60.7039953125), (27.6211128906, 61.6118818359), (28.819925, 62.4980875), (30.0588714844, 63.3687072266), (31.202940625, 64.2298359375), (32.1171207031, 65.0875685547), (32.4458111816, 65.5170659912), (32.6664, 65.948), (32.8248125, 66.6851625), (32.7710109375, 66.9061765625), (32.6176, 66.9805), (32.5208703125, 66.9222546875), (32.4679125, 66.7729125), (32.3706484375, 66.5442390625), (32.141, 66.248), (31.1034759766, 65.3984353516), (29.9355515625, 64.7423015625), (28.6692482422, 64.2321388672), (27.3365875, 63.8204875), (24.6002796875, 63.1028796875), (23.2606755859, 62.7020037109), (21.9828, 62.2098), (20.9997419922, 61.7483013672), (19.7656484375, 61.0788734375), (18.4207775391, 60.1820806641), (17.1053875, 59.0384875), (16.5025784912, 58.3680671631), (15.9597365234, 57.6286583984), (15.4943938721, 56.8178317627), (15.1240828125, 55.9331578125), (14.8663356201, 54.9722071045), (14.7386845703, 53.9325501953), (14.7586619385, 52.8117576416), (14.9438, 51.6074), (15.122925, 50.8023), (15.252640625, 50.40393125), (15.3949, 50.2336), (15.5243578125, 50.3437421875), (15.5897375, 50.6433625), (15.6117, 51.6262), (15.6561465332, 52.3362411621), (15.8000691406, 52.9857136719), (16.031892334, 53.5809723145), (16.340040625, 54.128371875), (17.1390105469, 55.1050128906), (18.104375, 55.966475), (20.163871875, 57.547215625), (21.0727964844, 58.3681707031), (21.7777, 59.2773), (22.104725, 59.739675), (22.2554875, 59.862834375), (22.3512, 59.8191), (22.3023, 59.3027), (22.0503148438, 58.5393394531), (21.6885625, 57.836665625), (20.851325, 56.570375), (20.4836242188, 55.9852566406), (20.221725, 55.417821875), (20.1195195312, 54.8573199219), (20.2309, 54.293), (20.6030839844, 53.7075248047), (21.082534375, 53.4021359375), (21.6320488281, 53.3341009766), (22.214425, 53.4606875), (22.7924605469, 53.7391630859), (23.328953125, 54.1267953125), (23.7867003906, 54.5808517578), (24.1285, 55.0586), (24.368925, 55.470225), (24.465971875, 55.57165625), (24.5609, 55.5859), (24.6368625, 55.3106625), (24.5941, 54.791), (24.2621640625, 53.2469984375), (23.7833125, 51.9836375), (23.4592181641, 51.4272880859), (23.0629046875, 50.9052078125), (22.0063, 49.916), (21.566953125, 49.6562546875), (21.130475, 49.4675625), (20.815009375, 49.2970390625), (20.7395761719, 49.2020642578), (20.7387, 49.0918), (20.9814125, 49.0273125), (21.4195, 49.0469), (22.2465202881, 49.156970874), (23.0534919922, 49.3736341797), (23.8374688721, 49.6869346924), (24.5955046875, 50.0869171875), (26.0219681641, 51.1071072266), (27.3093125, 52.3545625), (28.4339677734, 53.7496412109), (29.3723640625, 55.2127015625), (30.1009314453, 56.6641017578), (30.5961, 58.0242), (30.6886375, 58.3597625), (30.6215, 58.5781), (30.509940625, 58.5979578125), (30.381, 58.5274875), (30.0922, 58.2668), (29.2161125, 57.616425), (28.2387, 57.1504)],
# #    T
# #         [(15.5055, 28.7004), (20.8063, 28.7004), (20.8063, 44.1211), (26.7445, 44.1211), (26.7445, 47.8328), (9.5668, 47.8328), (9.5668, 44.1211), (15.5055, 44.1211), (15.5055, 28.7004)],
# # #    U
#         [(38.3852, 32.0156), (39.2659501953, 32.0912681641), (40.0374453125, 32.3105390625), (40.6971646484, 32.6618123047), (41.2425875, 33.1334875), (41.6711931641, 33.7139642578), (41.9804609375, 34.3916421875), (42.1678701172, 35.1549208984), (42.2309, 35.9922), (42.2309, 47.834), (47.5316, 47.834), (47.5316, 35.7273), (47.4732092773, 34.7657740479), (47.3213726562, 33.8784173828), (47.081449707, 33.063555542), (46.7588, 32.3195140625), (46.3587831055, 31.6446184814), (45.8867585938, 31.0371943359), (45.3480860352, 30.4955671631), (44.748125, 30.0180625), (44.0922350586, 29.6030058838), (43.3857757812, 29.2487228516), (41.8425875, 28.7157796875), (40.1614367187, 28.4058373047), (38.3852, 28.3055), (36.6090451172, 28.4058373047), (34.9279234375, 28.7157796875), (33.3847244141, 29.2487228516), (32.6782488525, 29.6030058838), (32.0223375, 30.0180625), (31.4223515381, 30.4955671631), (30.8836521484, 31.0371943359), (30.4116005127, 31.6446184814), (30.0115578125, 32.3195140625), (29.6888852295, 33.063555542), (29.4489439453, 33.8784173828), (29.2970951416, 34.7657740479), (29.2387, 35.7273), (29.2387, 47.834), (34.5395, 47.834), (34.5395, 35.9922), (34.6025257812, 35.1549208984), (34.789925, 34.3916421875), (35.0991804687, 33.7139642578), (35.527775, 33.1334875), (36.0731914062, 32.6618123047), (36.7329125, 32.3105390625), (37.5044210937, 32.0912681641), (38.3852, 32.0156)],
# #         # D -- exterior
# #         [(55.4875, 45.5563), (59.4066, 45.5563), (60.2057835693, 45.5178564697), 
# #          (60.9454076172, 45.4051830078), (61.6265759033, 45.2222653076), 
# #          (62.2503921875, 44.9730890625), (62.8179602295, 44.6616399658), 
# #          (63.3303837891, 44.2919037109), (64.1942125, 43.3935125), 
# #          (64.8507083984, 42.3098009766), (65.3087015625, 41.0726546875), 
# #          (65.5770220703, 39.7139591797), (65.6645, 38.2656), 
# #          (65.5770220703, 36.8175103516), (65.3087015625, 35.4592765625), 
# #          (64.8507083984, 34.2227138672), (64.1942125, 33.1396375), 
# #          (63.3303837891, 32.2418626953), (62.8179602295, 31.8724056396), 
# #          (62.2503921875, 31.5612046875), (61.6265759033, 31.3122367432), 
# #          (60.9454076172, 31.1294787109), (60.2057835693, 31.0169074951), 
# #          (59.4066, 30.9785), (55.4875, 30.9785), 
# #          (55.4875, 45.5563)],
# #         # D -- interior
# #         [ 
# #          (52.8324, 28.7004), (59.4059, 28.7004), 
# #          (60.8560672363, 28.7788331543), 
# #          (62.1440332031, 29.0031808594), 
# #          (63.2792692871, 29.3570154785), (64.271246875, 29.823909375), (65.1294373535, 30.3874349121), (65.8633121094, 31.0311644531), (66.4823425293, 31.7386703613), (66.996, 32.493525), (67.4137559082, 33.2793007324), (67.7450816406, 34.0795699219), (68.186328125, 35.657878125), (68.3955105469, 37.0970285156), (68.4484, 38.2656), (68.3955105469, 39.4344525391), (68.186328125, 40.8740328125), (67.7450816406, 42.4528623047), (67.4137559082, 43.2534084717), (66.996, 44.0394625), (66.4823425293, 44.7945895752), (65.8633121094, 45.5023548828), (65.1294373535, 46.1463236084), (64.271246875, 46.7100609375), (63.2792692871, 47.1771320557), (62.1440332031, 47.5311021484), (60.8560672363, 47.7555364014), (59.4059, 47.834), (52.8324, 47.834), (52.8324, 28.7004)]
#         # e
#         # e -- outershell
#         #[(82.9195, 34.8762), (82.9195, 36.123), (82.8224828125, 37.4505816406), (82.53454375, 38.658784375), (82.0603515625, 39.7298449219), (81.404575, 40.646), (80.5718828125, 41.3894863281), (79.56694375, 41.942540625), (78.3944265625, 42.2873996094), (77.059, 42.4063),(76.2952375244, 42.3687171631), (75.5838064453, 42.2585341797), (74.9242850342, 42.0795993408), (74.3162515625, 41.8357609375), (73.7592843018, 41.5308672607), (73.2529615234, 41.1687666016), (72.3905625, 40.2883375), (71.7256806641, 39.2252599609), (71.2549421875, 38.0103203125), (70.9749732422, 36.6743048828), (70.8824, 35.248), (70.9637001953, 33.823009375), (71.2144078125, 32.50744375), (71.6447333984, 31.3261375), (72.2648875, 30.303925), (73.0850806641, 29.465640625), (73.5733826904, 29.1232322266), (74.1155234375, 28.83611875), (74.7127792236, 28.6074044922), (75.3664263672, 28.44019375), (76.848, 28.3027), (77.9991910156, 28.3734771484), (79.058021875, 28.5858296875), (80.0117917969, 28.9397892578), (80.8478, 29.4353875), (81.5533457031, 30.0726560547), (82.115728125, 30.8516265625), (82.5222464844, 31.7723306641), (82.7602, 32.8348), (80.1098, 32.8348), (79.9671755859, 32.1632625), (79.7567359375, 31.59635), (79.4750064453, 31.1294125), (79.1185125, 30.7578), (78.6837794922, 30.4768625), (78.1673328125, 30.28195), (77.5656978516, 30.1684125), (76.8754, 30.1316), (75.9894021484, 30.2347720703), (75.2544671875, 30.5276953125), (74.6604455078, 30.9854802734), (74.1971875, 31.5832375), (73.8545435547, 32.2960775391), (73.6223640625, 33.0991109375), (73.4904994141, 33.9674482422), (73.4488, 34.8762), (82.9195, 34.8762), (82.9195, 34.8762)],
#         # e -- innershell
#         #[(73.5055, 36.6262), (73.5694832031, 37.3917933594), (73.744890625, 38.118946875), (74.0270464844, 38.7880457031),  (74.411275, 39.379475), (74.8929003906, 39.8736199219), (75.467246875, 40.250865625), (76.1296386719, 40.4915972656), (76.8754, 40.5762), (77.7209189453, 40.4999767578), (78.4335015625, 40.2795953125), (79.0193740234, 39.9274880859), (79.4847625, 39.4560875), (79.8358931641, 38.8778259766), (80.0789921875, 38.2051359375), (80.2202857422, 37.4504498047), (80.266, 36.6262), (73.5055, 36.6262)],
#    
#         # l
#         #[(85.973, 28.6992), (88.49331, 28.6992), (88.49331, 47.834), (85.973, 47.834), (85.973, 28.6992), (85.973, 28.6992)],
#         #f
#         #[(96.3883, 28.7004), (96.3883, 40.2512), (99.4605, 40.2512), (99.4605, 42.0027), (96.3883, 42.0027), (96.3883, 44.1512), (96.4229054688, 44.6702857422), (96.52635625, 45.0817171875), (96.6981039062, 45.3973431641), (96.9376, 45.6290125), (97.2442960938, 45.7885740234), (97.61764375, 45.8878765625), (98.5621, 45.9531), (99.8336, 45.875), (99.8336, 47.9656), (98.9403125, 48.1487), (98.0309, 48.2313), (97.1673613281, 48.1749609375), (96.374484375, 48.004725), (95.6659777344, 47.7187640625), (95.05555, 47.31525), (94.5569097656, 46.7923546875), (94.183765625, 46.14825), (93.9498261719, 45.3811078125), (93.8688, 44.4891), (93.8688, 42.0027), (91.273, 42.0027), (91.273, 40.2512), (93.8688, 40.2512), (93.8688, 28.7004), (96.3883, 28.7004)],
#         # t
# #          [(100.908, 42.0027), (100.908, 40.2512), (103.188, 40.2512), (103.188, 31.7734), (103.250359375, 30.4847203125), (103.393189453, 29.8978896484), (103.668125, 29.3748875), (104.118419922, 28.9348306641), (104.787328125, 28.5968359375), (105.718103516, 28.3800201172), (106.954, 28.3035), (107.811, 28.3438375), (108.677, 28.4609), (108.677, 30.3953), (107.35, 30.2371), (106.713328125, 30.322746875), (106.191125, 30.58245), (105.837859375, 31.020353125), (105.708, 31.6406), (105.708, 40.2512), (108.782, 40.2512), (108.782, 42.0027), (105.708, 42.0027), (105.708, 45.634), (103.188, 44.8391), (103.188, 42.0012), (100.908, 42.0027)],
#         ]
#         conv = ToPointsAndSegments()
#         for ring in polys:
#             conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=False, output=True)#, pause=False, output=True)
#         assert len(skel.segments()) == 981
#         assert len(skel.sk_nodes) == 732, len(skel.sk_nodes)


#     def test_chishape(self):
#         # FIXME: goes wrong with infinite events!
#         ring = [(-0.12999106777200001,-0.32109517457699999),(-0.16826546739199999,-0.28581718751000001),(-0.166723188391,-0.18304326555799999),(-0.14428079224000001,-0.165036480131),(-0.0626940259892,-0.00761432147016),(-0.0519067121278,-0.10494115954700001),(0.000620341167536,-0.16142214118699999),(0.034134894903,-0.233656472664),(0.0175820094043,-0.15693554716999999),(-0.00042310504988,-0.00676775008218),(-0.0330913291091,0.0575304773025),(-0.0519892012015,0.08570153009170001),(-0.10887914106799999,0.0613865659042),(-0.17432707364800001,0.117041967082),(-0.197373592875,0.201184615491),(-0.22737971517300001,0.22772375476600001),(-0.286238242877,0.29353637718499997),(-0.0688830380876,0.28598413943399997),(-0.0189602933902,0.26492760793199999),(0.0082493390123,0.28888769157799998),(0.0481471400365,0.215794229472),(0.13562174756100001,0.0642602345078),(0.201996782273,0.00561982649704),(0.13399950275399999,-0.00504710753071),(0.160552210246,-0.21835213939299999),(0.18611593572999999,-0.30206901543800002),(0.151463066945,-0.341340054467),(0.126464904332,-0.36172471919799998),(0.0920053070572,-0.41642920433000002),(0.105205160836,-0.44778009140699998),(0.00495683765215,-0.551998270904),(-0.020125337515,-0.60919704696900001),(-0.0214362359418,-0.66467947604699995),(-0.12870796380899999,-0.76265467931800002),(-0.14729557673300001,-0.71923994053499996),(-0.24716578512000001,-0.79061490991799999),(-0.31149974888100002,-0.70754775130100001),(-0.34382727127700002,-0.61521826153500003),(-0.35888186908899999,-0.67317315268099998),(-0.38962851549100003,-0.70479586976899999),(-0.33494797050800001,-0.70374928059700004),(-0.38748547673200001,-0.80751666594100002),(-0.25781488341300002,-0.81288014327799996),(-0.28319340277400001,-0.85276537531399998),(-0.19895516143799999,-0.82587129221599997),(-0.144842483109,-0.84638645978799998),(-0.0554186697369,-0.91021588670300002),(-0.048826334165,-0.83481862743599999),(-0.0485086162308,-0.79172914355599999),(0.00195195896021,-0.73060797450000003),(0.0125467617639,-0.66191034185300002),(0.15196860556799999,-0.447134243195),(0.322039601989,-0.64599024901199997),(0.27086716766399999,-0.70942350345299998),(0.23249861449500001,-0.72683485553500005),(0.135139129868,-0.79710706465299996),(0.143526223914,-0.82367733837000001),(0.141920121127,-0.976921124059),(0.195602835527,-0.94152016784600001),(0.31193457825300003,-0.80030375390599995),(0.31746131940900002,-0.80173223735300003),(0.36570349918299999,-0.78722865795200003),(0.31741642090099997,-0.75437234181099999),(0.31552449370800001,-0.73991583559499996),(0.36219425490099999,-0.64913547424200002),(0.43966940786399999,-0.60517960729200004),(0.49800750045999997,-0.77708305831000002),(0.58166904750000004,-0.71014735383600003),(0.67923922663299996,-0.71102927640900004),(0.58833137470899999,-0.66141551308199997),(0.59370237665000003,-0.55322023610500004),(0.73191186053799995,-0.54112200709799996),(0.78142424442699998,-0.48783349913599999),(0.89254615769900003,-0.363233761913),(0.81797238219199997,-0.34311266294100001),(0.739885752058,-0.36116612418100003),(0.64851642331299997,-0.49804359472999998),(0.55603122297499996,-0.52041793502699996),(0.46485135630899999,-0.53781533480699995),(0.38202308473500002,-0.45056883179099999),(0.39321613570300001,-0.34810990114599999),(0.35366169466800002,-0.42361425177099998),(0.27176586342800002,-0.45254847919399999),(0.18251288806900001,-0.35485407871000002),(0.21970850709600001,-0.309800346896),(0.245277622221,-0.159921228405),(0.252640141042,-0.12795726707499999),(0.235989649927,-0.0121897210647),(0.27052274329199999,-0.0541435598898),(0.26254986394500002,-0.00971770823302),(0.29705056257099999,0.0128466495031),(0.43430988219599997,0.0527995950295),(0.52768564081400005,0.10012349218200001),(0.66270265694200003,-0.0813207165175),(0.55508043775100002,-0.16861626615700001),(0.70162045221400005,-0.145960079444),(0.89817517402799996,-0.16859081321399999),(0.93462294241199995,-0.116555920262),(0.90750782241899997,-0.0533694886527),(0.911867756709,-0.0833046747075),(0.82401430764299999,-0.09544019832179999),(0.718927675968,-0.0594287314564),(0.71311617868400001,0.0208603722082),(0.85966775963800002,0.15456094971699999),(0.855643307834,0.188335509481),(0.60649419536500004,0.16794188102900001),(0.50302839349200001,0.198944293552),(0.424398030649,0.14226075997900001),(0.35816770905700002,0.10863476471899999),(0.18525626613599999,0.12982327991000001),(0.26076377691399999,0.25951179218999998),(0.25719911799799999,0.30083962624900001),(0.218537736717,0.31128990402899998),(0.13420113015400001,0.35265889114999999),(0.0284172531529,0.30362713582700002),(-0.0379910903481,0.31596228088200001),(0.0498393764997,0.45467409027400002),(0.0600953605572,0.55522681030800003),(-0.131090369589,0.66957627387499996),(-0.0400643341379,0.667341818167),(-0.058404842527,0.68024289153700002),(-0.10948375437299999,0.75755608396200003),(-0.106442820635,0.82337126361699997),(0.0179776484812,0.78065482615000004),(0.12927506496999999,0.68122797123199996),(0.27473891286500002,0.69265593770300005),(0.200587337664,0.61076692087999995),(0.23173073210299999,0.51302890893300002),(0.30476198000999999,0.61723266677400002),(0.323260970594,0.59849069656999998),(0.33992696194200001,0.59402706306200004),(0.40140603789700002,0.63796427233499997),(0.35477193119599998,0.43769892740999999),(0.51488171905799995,0.37037089365999998),(0.60876862639999996,0.32717151772699998),(0.61225250330100001,0.321233872423),(0.62487344705600001,0.35304136813999998),(0.59284213148200005,0.48328829781100002),(0.61517803639299995,0.49947078574999998),(0.76791896233300005,0.45684256431100001),(0.86574092801699998,0.49775387774199997),(0.65897550151999995,0.58421560882599999),(0.65199537318900003,0.645912404138),(0.551994338566,0.55244952695600003),(0.47613543020799998,0.64805236451399995),(0.49715675939100001,0.71771002878300005),(0.52799256265700001,0.74418912283299998),(0.384784243197,0.78838271163700002),(0.34465830798500002,0.90533954381799997),(0.24254994106,0.82075018800199995),(0.21558963112000001,0.86359414417699998),(0.219431181733,0.95434701308299996),(0.19569317277000001,0.94576368431699998),(0.182117992521,0.86098631155500005),(0.155770003106,0.84767418481500001),(0.19416500544900001,0.80040685334600004),(0.0589396307635,0.81483014140300003),(-0.0577220539131,0.89116094574899996),(-0.11643399802,0.94338220137200002),(-0.17799776596799999,0.96162856980099998),(-0.180555761653,0.94986204938600005),(-0.137544123569,0.91744442202400001),(-0.14161698616499999,0.80637353194100003),(-0.16786357370300001,0.72485546116699995),(-0.174036935846,0.666804655952),(-0.33688802694600001,0.68639323222899995),(-0.36535969101400001,0.80754809235400005),(-0.45485862441800001,0.79556741373899997),(-0.385876352353,0.636184133747),(-0.53866136037099999,0.59823501872200002),(-0.54119399654800004,0.59656915043600001),(-0.50262421878899999,0.50411168741800005),(-0.34791655129999999,0.60950223303499995),(-0.36709062003999998,0.368070267502),(-0.38730733949899998,0.33782163062499998),(-0.38183191627200003,0.26733768045400003),(-0.32001779437400002,0.31393176982600002),(-0.28113860950899999,0.25636325711000002),(-0.22405967697699999,0.18654517031000001),(-0.21382475457299999,0.154157867635),(-0.243600582201,0.062996296526),(-0.34169523592599998,0.0258370804139),(-0.385026386868,0.00324134597771),(-0.421664651434,0.0616690672473),(-0.51041267720600003,0.14686099198200001),(-0.60816939688899996,0.14621945661499999),(-0.75981110425999998,0.328585842731),(-0.62772190456900001,0.30706097647000002),(-0.55455205027400001,0.31143710888800002),(-0.59633638224800001,0.32199336951000002),(-0.63696946456100001,0.40030164309600003),(-0.74216776569499998,0.36434414578800001),(-0.78588039780200003,0.51255123041399997),(-0.80767227779499995,0.54384075376300001),(-0.81494931033499995,0.42953799194300002),(-0.86760804829000004,0.344834063292),(-0.88740570215100001,0.33916177790399998),(-0.97820503743499998,0.161921304786),(-0.97926947903399997,0.11387234820599999),(-0.86331785824100005,0.125872971124),(-0.732198437185,0.0366675540027),(-0.76414307266500003,-0.10978517883699999),(-0.75745350301500003,-0.12633059565599999),(-0.67990655911800002,-0.13158805886899999),(-0.70437658004799997,-0.26485697053000001),(-0.75114815147299996,-0.28503007153100002),(-0.78489919064699998,-0.32511594389999998),(-0.875480713972,-0.26917957145299998),(-0.84019146953699997,-0.19220581767200001),(-0.88421402908400004,-0.27886737579100002),(-0.82843027917000001,-0.334338546633),(-0.78299512181399999,-0.33826363950499999),(-0.77447635266000003,-0.42230405216),(-0.72871451268200005,-0.47733153384299998),(-0.60659665896299997,-0.51825488145900001),(-0.661470957262,-0.61691615499999997),(-0.56815747057699995,-0.64200076744599999),(-0.51383752411600003,-0.60844810765000001),(-0.48251084036800002,-0.54375256183099996),(-0.44678729686599999,-0.45808852526600002),(-0.45018988347599997,-0.44340840711399998),(-0.49546071953100002,-0.45442913128599999),(-0.589583188772,-0.497284228592),(-0.62632124200200001,-0.46002948755599998),(-0.68079216493799999,-0.37790671891099997),(-0.64150861858599995,-0.317200343931),(-0.55999348236900004,-0.222056313028),(-0.49792032738699998,-0.27095937511500001),(-0.49830486694600001,-0.28830364457300001),(-0.48831943843699999,-0.26572144570400003),(-0.46353613852999997,-0.20760300475499999),(-0.60240696066499999,-0.18722825587899999),(-0.61967014826699995,-0.12863470121500001),(-0.65594401649900003,-0.114325467046),(-0.71073251992499997,-0.0571926425734),(-0.65739974234300003,0.0635636054481),(-0.40551506033000001,-0.0511595518414),(-0.39376327111699999,-0.0607718490811),(-0.246053676492,-0.0276599262734),(-0.22537624483499999,-0.14386854527000001),(-0.18751401372500001,-0.237711894639),(-0.23658636280500001,-0.26809503520200001),(-0.31669941126399997,-0.264323056582),(-0.30937335599299998,-0.31668772015000002),(-0.29687393094199999,-0.36767492574499999),(-0.210866969214,-0.396169963731),(-0.21098150751899999,-0.462050805846),(-0.192307066607,-0.56220026499099995),(-0.161231219511,-0.524196707185),(-0.08141306981679999,-0.36953378155099997),(-0.12999106777200001,-0.32109517457699999)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=False, output=True)
#         assert len(skel.segments()) == 981
#         assert len(skel.sk_nodes) == 732, len(skel.sk_nodes)

# ##############################################################################
# # PARALLEL EDGES IN THE INPUT, leading to problems 
# # (e.g. nodes not on correct location)
# ##############################################################################
# 
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
#         skel = calc_skel(conv,
#                          pause=True,
#                          output=True)
#         assert len(skel.segments()) == 10
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)

#     def test_flipped_cshape(self):
#         """Parallel c-shape wavefront"""
#         conv = ToPointsAndSegments()
#         l0 = [(5, 0.0), (5, 3)]
#         l1 = [(0, 3), (5,3)]
#         l2 = [(0,0), (5,0)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv,
#                          pause=True,
#                          output=True)
#         assert len(skel.segments()) == 10
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)

#     def test_cshape_bottom(self):
#         """Parallel c-shape wavefront with longer segment on bottom"""
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, 0.0), (0.0, 3)]
#         l1 = [(0, 3), (5,3)]
#         l2 = [(0,0), (10,0)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 10
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)


#     def test_cshape_top(self):
#         """Parallel c-shape wavefront with longer segment on top"""
#         # FIXME: missing piece of wavefront, after handling parallel fan
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, 0.0), (0.0, 3)]
#         l1 = [(0, 3), (10,3)]
#         l2 = [(0,0), (5,0)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 10
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)
#         # geometric embedding
#         positions = [n.pos for n in skel.sk_nodes]
#         assert frozenset(positions) == frozenset([(0.0, -0.3), (1.0, 0.3), (-1.0, 0.3), (-1.0, -0.3), (-0.7, 0.0), (0.3, 0.0)])


#     def test_rect_extra_pt(self):
#         """"Rectangle with extra point on straight (180 degrees) edge """
#         conv = ToPointsAndSegments()
#         polygon = [[(0, 0), (0., 10), (15,10), (15,0.), (2., 0.), (0,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 12
#         assert len(skel.sk_nodes) == 8, len(skel.sk_nodes)


#     def test_tiny_v(self):
#        # MISSES COMPLETE EVENT SOMEHOW
#         """Tiny V at bottom of square"""
#         conv = ToPointsAndSegments()
#         polygon = [[(-10, 0), (-10., 100.), (100.,100.), (100.,0.), (2., 0.), (1,-1), (0,0), (-10,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == (10+7)
#         positions = [n.pos for n in skel.sk_nodes]
        # additional: 
        #check if last node geerated internally is at (50,50)
        ############## :FIXME
# 
#     def test_2parallel_eq(self):
#         """2 parallel wavefront having equal size"""
#         conv = ToPointsAndSegments()
#         l0 = [(0, 0), (3,0)]
#         l1 = [(0, 1), (3,1)]
#         for line in l0, l1:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)
# 
#     def test_2parallel_not_eq(self):
#         """2 parallel wavefront having different size"""
#         conv = ToPointsAndSegments()
#         l0 = [(0, 0), (3,0)]
#         l1 = [(1, 1), (2,1)]
#         for line in l0, l1:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_2parallel_not_eq2(self):
#         """2 parallel wavefront having different size, other one above"""
#         conv = ToPointsAndSegments()
#         l0 = [(0, 0), (3,0)]
#         l1 = [(1, -1), (2,-1)]
#         for line in l0, l1:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)

# 


#     def test_church(self):
#         """church in naaldwijk
#         """
#         ring = [(74029.47599999999511056,445622.80800000001909211),(74022.8169999999954598,445622.11400000000139698),(74023.09900000000197906,445619.97800000000279397),(74021.96000000000640284,445619.86800000001676381),(74022.06500000000232831,445618.78100000001722947),(74023.11100000000442378,445618.88199999998323619),(74024.28500000000349246,445606.70799999998416752),(74024.5,445606.72899999999208376),(74024.98399999999674037,445601.71000000002095476),(74025.26700000000710133,445601.7370000000228174),(74025.43099999999685679,445600.02799999999115244),(74033.13599999999860302,445600.77100000000791624),(74033.26799999999639113,445599.39600000000791624),(74034.29600000000209548,445599.49499999999534339),(74034.16400000000430737,445600.86300000001210719),(74037.91899999999441206,445601.22499999997671694),(74038.05199999999604188,445599.84600000001955777),(74039.09900000000197906,445599.9469999999855645),(74038.96700000000419095,445601.32099999999627471),(74042.68099999999685679,445601.67999999999301508),(74042.8120000000053551,445600.32099999999627471),(74043.87600000000384171,445600.42300000000977889),(74043.74499999999534339,445601.78100000001722947),(74047.73099999999976717,445602.16499999997904524),(74048.09600000000500586,445598.37599999998928979),(74047.09299999999348074,445598.27899999998044223),(74047.19999999999708962,445597.1720000000204891),(74048.21899999999732245,445597.27100000000791624),(74048.31600000000617001,445596.2629999999771826),(74049.39500000000407454,445596.36700000002747402),(74049.29700000000593718,445597.38000000000465661),(74055.42600000000675209,445597.97100000001955777),(74055.52499999999417923,445596.94300000002840534),(74056.61999999999534339,445597.04899999999906868),(74056.52099999999336433,445598.0719999999855645),(74057.59600000000500586,445598.17599999997764826),(74057.4940000000060536,445599.23300000000745058),(74056.38800000000628643,445599.12599999998928979),(74056.05599999999685679,445602.56800000002840534),(74057.1190000000060536,445602.66999999998370185),(74056.9980000000068685,445603.92099999997299165),(74055.94000000000232831,445603.81800000002840534),(74055.66300000000046566,445606.68599999998696148),(74058.68499999999767169,445606.97700000001350418),(74058.76900000000023283,445606.09999999997671694),(74059.74599999999918509,445606.19400000001769513),(74059.65799999999580905,445607.106000000028871),(74062.35899999999674037,445607.36599999997997656),(74062.44800000000395812,445606.4469999999855645),(74063.42299999999522697,445606.54100000002654269),(74063.32499999999708962,445607.5590000000083819),(74066.11000000000058208,445607.9340000000083819),(74066.59100000000034925,445603.26099999999860302),(74065.60700000000360887,445603.15999999997438863),(74065.71199999999953434,445602.1379999999771826),(74066.66800000000512227,445602.2370000000228174),(74066.77300000000104774,445601.21600000001490116),(74067.73299999999289867,445601.31500000000232831),(74067.62900000000081491,445602.31900000001769513),(74070.46400000000721775,445602.61099999997531995),(74070.57499999999708962,445601.54200000001583248),(74071.51300000000628643,445601.63900000002468005),(74071.40799999999580905,445602.65799999999580905),(74072.27300000000104774,445602.74699999997392297),(74072.16599999999743886,445603.78999999997904524),(74071.26700000000710133,445603.6969999999855645),(74071.0059999999939464,445606.231000000028871),(74071.77899999999499414,445607.34999999997671694),(74071.67900000000372529,445608.32900000002700835),(74073.66300000000046566,445609.20000000001164153),(74074.42100000000209548,445608.67599999997764826),(74074.96000000000640284,445609.45699999999487773),(74074.32899999999790452,445609.93900000001303852),(74075.64800000000104774,445612.22700000001350418),(74076.4940000000060536,445611.94199999998090789),(74076.72800000000279397,445612.91399999998975545),(74075.7519999999931315,445613.26799999998183921),(74075.47599999999511056,445615.94599999999627471),(74076.3690000000060536,445616.33799999998882413),(74076.1889999999984866,445617.23200000001816079),(74075.14699999999720603,445616.83299999998416752),(74073.19599999999627471,445618.96000000002095476),(74073.7519999999931315,445619.76500000001396984),(74072.98699999999371357,445620.29300000000512227),(74072.50999999999476131,445619.60200000001350418),(74069.86000000000058208,445620.56199999997625127),(74069.76700000000710133,445621.46700000000419095),(74068.79700000000593718,445621.36700000002747402),(74068.88599999999860302,445620.50300000002607703),(74065.9330000000045402,445620.19900000002235174),(74065.84299999999348074,445621.07500000001164153),(74064.97999999999592546,445620.98599999997531995),(74065.07099999999627471,445620.09700000000884756),(74062.14100000000325963,445619.79399999999441206),(74062.04799999999522697,445620.69500000000698492),(74061.05299999999988358,445620.59299999999348074),(74061.14500000000407454,445619.69799999997485429),(74059.73399999999674037,445619.55200000002514571),(74059.3120000000053551,445623.64199999999254942),(74060.21499999999650754,445623.73499999998603016),(74060.11699999999837019,445624.68800000002374873),(74059.3129999999946449,445624.60499999998137355),(74059.24099999999452848,445625.31099999998696148),(74058.32000000000698492,445625.21600000001490116),(74058.38999999999941792,445624.54100000002654269),(74053.94599999999627471,445624.08199999999487773),(74053.65700000000651926,445626.89000000001396984),(74054.60099999999511056,445626.98800000001210719),(74054.48200000000360887,445628.143999999971129),(74053.52400000000488944,445628.04499999998370185),(74053.41199999999662396,445629.1379999999771826),(74052.39999999999417923,445629.03399999998509884),(74052.51099999999860302,445627.95400000002700835),(74046.24300000000221189,445627.30800000001909211),(74046.1220000000030268,445628.4870000000228174),(74045.08000000000174623,445628.38000000000465661),(74045.19899999999324791,445627.22100000001955777),(74044.29799999999522697,445627.12800000002607703),(74044.42200000000593718,445625.92599999997764826),(74045.34900000000197906,445626.02199999999720603),(74045.74199999999837019,445622.09999999997671694),(74041.92200000000593718,445621.73200000001816079),(74041.8139999999984866,445622.84999999997671694),(74040.81900000000314321,445622.75400000001536682),(74040.92500000000291038,445621.65500000002793968),(74036.96499999999650754,445621.27299999998649582),(74036.86199999999371357,445622.34499999997206032),(74035.79399999999441206,445622.24200000002747402),(74035.89599999999336433,445621.1840000000083819),(74032.09600000000500586,445620.81800000002840534),(74031.98900000000139698,445621.91800000000512227),(74030.92900000000372529,445621.8159999999916181),(74031.03399999999965075,445620.72499999997671694),(74029.6889999999984866,445620.59499999997206032),(74029.47599999999511056,445622.80800000001909211)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, output=True)

#     def test_inf(self):
#         """Contains 1 triangle that is only witnessed by infinite triangle event (edge collapse)
#         """
#         segments = [[(0.713628396143,0.28492915571299998),(0.605791703184,0.27382778264800001)],
#         [(0.71037832310799998,0.31648042652800001),(0.713628396143,0.28492915571299998)],
#         [(0.74580046742600004,0.32013219398300002),(0.71037832310799998,0.31648042652800001)],
#         [(0.74919661115900005,0.28708369850999998),(0.74580046742600004,0.32013219398300002)],
#         [(0.74919661115900005,0.28708369850999998),(0.84596844872900001,0.25202673093900002)],
#         [(0.84596844872900001,0.25202673093900002),(0.86338737949099997,0.27726044405599998)],
#         [(0.89132340052500003,0.25797911189200001),(0.86338737949099997,0.27726044405599998)],
#         [(0.89132340052500003,0.25797911189200001),(0.87101957347299996,0.22858238387499999)],
#         [(0.87101957347299996,0.22858238387499999),(0.94226555652900001,0.15090929009699999)],
#         [(0.94226555652900001,0.15090929009699999),(0.98031697341500001,0.16547984224500001)],
#         [(0.98689015483499998,0.13283304119200001),(0.98031697341500001,0.16547984224500001)],
#         [(0.98689015483499998,0.13283304119200001),(0.954279871457,0.118518112767)],
#         [(0.954279871457,0.118518112767),(0.96435874963400003,0.0207237803098)]]
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         print conv.points
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_segments(self):
#         segments =[[(0.74919661115900005, 0.28708369850999998), (0.84596844872900001, 0.25202673093900002)],
#                    [(0.84596844872900001, 0.25202673093900002), (0.86338737949099997, 0.27726044405599998)],
#          [(0.89132340052500003, 0.25797911189200001), (0.86338737949099997, 0.27726044405599998)],
#          [(0.89132340052500003, 0.25797911189200001), (0.87101957347299996, 0.22858238387499999)],
#          [(0.87101957347299996, 0.22858238387499999), (0.94226555652900001, 0.15090929009699999)]]
#  
#         conv = ToPointsAndSegments()
#         for line in segments:
#              
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         print conv.points
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_house1(self):
#         """House 1
#         """
#         ring = [(73293.27300000000104774,445228.5530000000144355),(73302.63499999999476131,445231.07000000000698492),(73301.72400000000197906,445234.67999999999301508),(73305.13199999999778811,445235.53999999997904524),(73305.53399999999965075,445233.94599999999627471),(73313.15300000000570435,445235.86800000001676381),(73311.83400000000256114,445241.09499999997206032),(73299.2440000000060536,445237.91800000000512227),(73299.54399999999441206,445236.73200000001816079),(73291.70799999999871943,445234.75500000000465661),(73293.27300000000104774,445228.5530000000144355)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, #pause=True, 
#                          output=True)

#     def test_house2(self):
#         ring = [(73220.912, 445241.233), (73218.453, 445250.0), (73218.252, 445250.715), (73215.704, 445250.0), (73214.981, 445249.797), (73214.924, 445250.0), (73214.366, 445251.99), (73208.627, 445250.38), (73208.734, 445250.0), (73211.762, 445239.205), (73216.446, 445240.519), (73216.56, 445240.112), (73217.103, 445240.264), (73217.779, 445239.427), (73220.181, 445240.101), (73220.429, 445241.097), (73220.912, 445241.233)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_cross(self):
#         # FIXME: Multiple skeleton nodes, because of fan that just collapses
#         ring = [(0,0), (10, 0), (10,-10), (15, -10), (15,0), (25,0), (25,5), (15,5), (15,15), (10,15), (10,5), (0,5), (0,0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)
#         # FIXME: are the following numbers correct?
#         assert len(skel.segments()) == 16+12, len(skel.segments())
#         assert len(skel.sk_nodes) == 17, len(skel.sk_nodes)


#     def test_parallelogram(self):
#         """Parallelogram with parallel wavefronts collapsing"""
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
#         skel = calc_skel(conv, pause=True, output=True)
#         positions = [n.pos for n in skel.sk_nodes]
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)
#         assert len(skel.segments()) == 9, len(skel.segments())



#     def test_multiple_parallel(self):
#         """Parallelogram with parallel wavefronts collapsing"""
#         # FIXME: Multiple skeleton nodes, because of fan that just collapses
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(0,0), (1,0), (2,0), (3,0), (4,0), (5,0),
#                            (5,1), (4,1), (3,1), (2,1), (1,1), (0, 1), (0,0)
#                            ]])
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)
#         assert len(skel.segments()) == 9, len(skel.segments())


#     def test_multiple_parallel2(self):
#         """Parallelogram with parallel wavefronts collapsing"""
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(0,0), (2,0), (4,0), (5,0),
#                            (5,1), (3,1), (1,1), (0, 1), (0,0)
#                            ]])
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)
#         assert len(skel.segments()) == 9, len(skel.segments())



# ##############################################################################
# # ...
# ##############################################################################
# 
# # 

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
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 24
#         assert len(skel.sk_nodes) == 16

# 
#     def test_3tris_handle_cw_ccw(self):
#         """Splitting and then handle the fan
#         """
#         conv = ToPointsAndSegments()
#         polygons = [
#                     [[(0,0), (1,0), (0.5,-0.5), (0,0)]],
#                     [[(1,3), (2,3), (1.5,3.5), (1,3)]],
#                     [[(2,0), (3,0), (2.5,-0.5), (2,0)]],
#                     ]
#         for polygon in polygons:
#             conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 24
#         assert len(skel.sk_nodes) == 16


#     def test_3tris_split_handle(self):
#         """One side that should just use handle and other side should handle_ccw
#         """
#         conv = ToPointsAndSegments()
#         polygons = [
#                     [[(1,0), (2,0), (1.5,-0.5), (1,0)]],
#                     [[(1,3), (2,3), (1.5,3.5), (1,3)]],
#                     [[(3,0), (4,0), (3.5,-0.5), (3,0)]],
#                     ]
#         for polygon in polygons:
#             conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 24
#         assert len(skel.sk_nodes) == 16



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

    unittest.main()