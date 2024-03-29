import unittest
 
from tri.delaunay.helpers import ToPointsAndSegments
from grassfire import calc_skel
from grassfire.events import at_same_location


PAUSE = False
OUTPUT = False
LOGGING = False

class TestMoreAdvancedParallelEvents(unittest.TestCase):
    def setUp(self):
       pass


    def test_capital_T(self):
        """Capital T, has more than one triangle in parallel fan
                
        Exhibits infinite event loop because of flipping; when all flip
        events are handled first inside the event loop
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

    def test_small_t(self):
        ring = [(100.908, 42.0027), (100.908, 40.2512), (103.188, 40.2512), (103.188, 31.7734), (103.250359375, 30.4847203125), (103.393189453, 29.8978896484), (103.668125, 29.3748875), (104.118419922, 28.9348306641), (104.787328125, 28.5968359375), (105.718103516, 28.3800201172), (106.954, 28.3035), (107.811, 28.3438375), (108.677, 28.4609), (108.677, 30.3953), (107.35, 30.2371), (106.713328125, 30.322746875), (106.191125, 30.58245), (105.837859375, 31.020353125), (105.708, 31.6406), (105.708, 40.2512), (108.782, 40.2512), (108.782, 42.0027), (105.708, 42.0027), (105.708, 45.634), (103.188, 44.8391), (103.188, 42.0012), (100.908, 42.0027)],
        conv = ToPointsAndSegments()
        conv.add_polygon(ring)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 89, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 64, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 10, len(not_stopped)
        self.assertEqual(len(stopped), 79)
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
#     def test_another_parallel(self):
#         j = """{
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                       
# "features": [
# { "type": "Feature", "properties": { "id": 21 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.673575314055, 0.166666666667 ], [ 0.866025403784, 0.166666666667 ] ] } },
# { "type": "Feature", "properties": { "id": 25 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.673575314055, -0.166666666667 ], [ 0.57735026919, -0.0 ] ] } },
# { "type": "Feature", "properties": { "id": 27 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.866025403784, -0.166666666667 ], [ 0.673575314055, -0.166666666667 ] ] } },
# { "type": "Feature", "properties": { "id": 32 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.57735026919, -0.0 ], [ 0.673575314055, 0.166666666667 ] ] } }
# ]
# }"""
#         import json
#         x = json.loads(j)
#          parse segments from geo-json
#         segments = []
#         for y in x['features']:
#             segments.append(tuple(map(tuple, y['geometry']['coordinates'])))
#          convert to triangulation input
#         conv = ToPointsAndSegments()
#         for line in segments:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#          skeletonize / offset
#         skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
# 
# 

# # # 
# # # 
# # # 

# 
#     def test_goes_backwards(self):
#         """ Backwards """
#         import json
#         s = """
# {
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                   
# "features": [
# { "type": "Feature", "properties": { "id": 139837494387920.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.683514927812, -0.965898400098 ], [ -0.71748146456, -0.739454821784 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388112.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.748142137672, -0.553743666202 ], [ -0.759958434594, -0.429672548517 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388112.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.759958434594, -0.429672548517 ], [ -0.785948285345, -0.265070160424 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388240.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.785948285345, -0.265070160424 ], [ -0.763489766712, -0.262007635155 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388240.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.763489766712, -0.262007635155 ], [ -0.766507673675, -0.238870348437 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388752.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.586154320712, -0.215676326008 ], [ -0.5828660885, -0.215227930706 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388880.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.498236806516, -0.203241344712 ], [ -0.49846422843, -0.201933668707 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494388880.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.582925827116, -0.214789847523 ], [ -0.498236806516, -0.203241344712 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494389136.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.360290252631, 0.00997489159772 ], [ -0.334809898799, 0.0137497588324 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494389136.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.334809898799, 0.0137497588324 ], [ -0.337617422344, 0.0390174707462 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494390352.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.337617422344, 0.0390174707462 ], [ -0.174312345657, 0.0612863440448 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494390352.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.174312345657, 0.0612863440448 ], [ -0.179478424108, 0.180106148433 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494390416.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.179478424108, 0.180106148433 ], [ -0.187294454259, 0.269556271262 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494390480.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.187294454259, 0.269556271262 ], [ -0.187878286313, 0.275978423863 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494390544.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.187878286313, 0.275978423863 ], [ -0.2025829896, 0.3719914865 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494390672.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.2025829896, 0.3719914865 ], [ -0.218077993356, 0.474987687936 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494394960.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.218077993356, 0.474987687936 ], [ -0.21920884215, 0.48516532708 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494395024.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.21920884215, 0.48516532708 ], [ -0.242380040932, 0.698340355884 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494395792.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.242380040932, 0.698340355884 ], [ -0.28298744088, 1.01626658474 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494395920.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.766507673675, -0.238870348437 ], [ -0.718823272293, -0.233572081612 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494395920.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.718823272293, -0.233572081612 ], [ -0.716010192022, -0.225132840802 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494396048.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.716010192022, -0.225132840802 ], [ -0.591156693313, -0.211990367249 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494396112.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.591156693313, -0.211990367249 ], [ -0.586154320712, -0.215676326008 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494396432.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.134572834673, 1.04195400369 ], [ 0.0896659427279, 1.07127753612 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494396496.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.0896659427279, 1.07127753612 ], [ 0.363524008481, 1.10590326858 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494396880.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.742836674715, -0.518684331281 ], [ 0.779930828904, -0.847585831751 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397136.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.0522328078103, -1.09193542446 ], [ -0.173404655063, -1.11449917074 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397264.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.173404655063, -1.11449917074 ], [ -0.17629841398, -1.09641317751 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397264.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.17629841398, -1.09641317751 ], [ -0.203682508102, -1.10032519096 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397392.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.489107842308, -0.96346158327 ], [ -0.575119174813, -0.977042319984 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397520.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.575119174813, -0.977042319984 ], [ -0.583019619349, -0.973092097716 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397520.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.583019619349, -0.973092097716 ], [ -0.661513833405, -0.984305556864 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397648.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.661513833405, -0.984305556864 ], [ -0.664364520136, -0.963400520837 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494397648.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.664364520136, -0.963400520837 ], [ -0.683514927812, -0.965898400098 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494398096.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.71594215456, -0.739262408033 ], [ -0.7346200948, -0.602290846274 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494398736.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.7346200948, -0.602290846274 ], [ -0.742017017808, -0.552978026219 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494398736.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.742017017808, -0.552978026219 ], [ -0.748142137672, -0.553743666202 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494405136.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.337024201923, -0.176153514066 ], [ -0.360290252631, 0.00997489159772 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494405136.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.338876402512, -0.176400474145 ], [ -0.337024201923, -0.176153514066 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494405264.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.404451022738, -0.189113686111 ], [ -0.404541862841, -0.188417245322 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494405264.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.49846422843, -0.201933668707 ], [ -0.404451022738, -0.189113686111 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494430416.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.52373504408, 0.746891951123 ], [ 0.565107394626, 0.534388514229 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494430544.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.565107394626, 0.534388514229 ], [ 0.579336454202, 0.459685951454 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494430544.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.579336454202, 0.459685951454 ], [ 0.593836136934, 0.387187537797 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494430864.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.593836136934, 0.387187537797 ], [ 0.608366977169, 0.300910673896 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494430928.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.608366977169, 0.300910673896 ], [ 0.62264631675, 0.21701955386 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494431056.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.652201074178, 0.0468991978764 ], [ 0.668001986794, -0.0593180480459 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494431056.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.668001986794, -0.0593180480459 ], [ 0.694887044697, -0.184781651591 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494431440.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.694887044697, -0.184781651591 ], [ 0.719436290171, -0.362081757792 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494431440.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.719436290171, -0.362081757792 ], [ 0.742836674715, -0.518684331281 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494477328.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.779930828904, -0.847585831751 ], [ 0.566338424494, -0.905598583566 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494477328.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.566338424494, -0.905598583566 ], [ 0.483144591664, -0.964590574117 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494477776.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.483144591664, -0.964590574117 ], [ 0.439943571247, -0.994831288409 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494477904.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.439943571247, -0.994831288409 ], [ 0.378451489401, -1.00986268619 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494478032.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.311542696901, -1.05160968452 ], [ 0.21017331046, -1.05160968452 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494478032.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.21017331046, -1.05160968452 ], [ 0.212025328206, -1.07012986198 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494478480.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.212025328206, -1.07012986198 ], [ 0.0512062864389, -1.08474977486 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494478480.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.0512062864389, -1.08474977486 ], [ 0.0522328078103, -1.09193542446 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494478928.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.2308185896, -0.920610265136 ], [ -0.31901751229, -0.933210111236 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494478928.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.220126648577, -1.00079982281 ], [ -0.2308185896, -0.920610265136 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494479056.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.217307179971, -1.00041093059 ], [ -0.220126648577, -1.00079982281 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494479056.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.203682508102, -1.10032519096 ], [ -0.217307179971, -1.00041093059 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494479184.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.31901751229, -0.933210111236 ], [ -0.340747110537, -0.936314339557 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494479248.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.340747110537, -0.936314339557 ], [ -0.340661171519, -0.936973205365 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494479312.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.340661171519, -0.936973205365 ], [ -0.48452650262, -0.958553005033 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494479376.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.48452650262, -0.958553005033 ], [ -0.489107842308, -0.96346158327 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494503056.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.338542168251, -0.178517291136 ], [ -0.338876402512, -0.176400474145 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494503056.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.404541862841, -0.188417245322 ], [ -0.338542168251, -0.178517291136 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494503888.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.378451489401, -1.00986268619 ], [ 0.308891739908, -1.02377463609 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494503888.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.308891739908, -1.02377463609 ], [ 0.311542696901, -1.05160968452 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494525072.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.62264631675, 0.21701955386 ], [ 0.636851638193, 0.132675457792 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494525072.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.636851638193, 0.132675457792 ], [ 0.652201074178, 0.0468991978764 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494548944.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.462313019605, 1.11799540513 ], [ 0.512320830173, 0.759606096061 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494549008.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.49867568417, 0.739986388874 ], [ 0.52373504408, 0.746891951123 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494549072.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.512320830173, 0.759606096061 ], [ 0.496302681955, 0.756936404692 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494549072.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.496302681955, 0.756936404692 ], [ 0.49867568417, 0.739986388874 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494550096.000000, "side": 0 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.363524008481, 1.10590326858 ], [ 0.363524008481, 1.10487498959 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494550096.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.363524008481, 1.10487498959 ], [ 0.462313019605, 1.11799540513 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494550416.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.28298744088, 1.01626658474 ], [ -0.166820821139, 1.03286181614 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494550480.000000, "side": 1 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.166820821139, 1.03286181614 ], [ -0.133726051289, 1.03687330339 ] ] } },
# { "type": "Feature", "properties": { "id": 139837494550480.000000, "side": 2 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.133726051289, 1.03687330339 ], [ -0.134572834673, 1.04195400369 ] ] } }
# ]
# }
# """
# #         s = """{
# # "type": "FeatureCollection",
# # "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
# #                                                                                             
# # "features": [
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51076.45, 391503.5 ], [ 51075.45, 391503.4 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51075.45, 391503.4 ], [ 51075.25, 391504.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51075.25, 391504.65 ], [ 51073.85, 391504.45 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51085.65, 391504.8 ], [ 51084.55, 391504.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51076.25, 391504.9 ], [ 51076.45, 391503.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51073.85, 391504.45 ], [ 51073.7, 391505.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51090.35, 391507.3 ], [ 51086.8, 391506.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51091.2, 391506.4 ], [ 51090.4, 391506.4 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51086.8, 391506.5 ], [ 51085.5, 391506.3 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51091.1, 391507.45 ], [ 51091.2, 391506.4 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51086.8, 391506.85 ], [ 51086.8, 391506.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51090.4, 391506.4 ], [ 51090.35, 391507.3 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51084.55, 391504.7 ], [ 51084.45, 391506.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51084.45, 391506.05 ], [ 51076.25, 391504.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51073.7, 391505.55 ], [ 51075.0, 391505.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51085.5, 391506.3 ], [ 51085.65, 391504.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51092.6, 391507.7 ], [ 51091.1, 391507.45 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.9, 391511.9 ], [ 51046.75, 391512.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.75, 391512.9 ], [ 51047.95, 391513.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.55, 391511.0 ], [ 51048.2, 391510.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.2, 391510.95 ], [ 51048.05, 391512.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.55, 391511.9 ], [ 51053.55, 391511.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51100.15, 391508.6 ], [ 51099.65, 391508.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51049.9, 391510.95 ], [ 51048.95, 391510.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.95, 391510.0 ], [ 51072.75, 391511.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51074.4, 391510.2 ], [ 51072.95, 391510.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.95, 391510.8 ], [ 51048.55, 391511.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.6, 391511.7 ], [ 51049.9, 391510.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.75, 391511.5 ], [ 51074.2, 391511.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51075.0, 391505.7 ], [ 51074.4, 391510.2 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.45, 391512.5 ], [ 51050.6, 391511.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51053.55, 391511.75 ], [ 51053.4, 391512.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51048.05, 391512.05 ], [ 51046.9, 391511.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.4, 391513.05 ], [ 51054.55, 391511.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51053.4, 391512.9 ], [ 51050.45, 391512.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.5, 391513.4 ], [ 51063.45, 391513.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.6, 391512.7 ], [ 51058.55, 391512.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51058.55, 391512.55 ], [ 51058.4, 391513.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.45, 391513.8 ], [ 51059.6, 391512.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51058.4, 391513.6 ], [ 51054.4, 391513.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.4, 391515.7 ], [ 51046.3, 391516.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.9, 391520.8 ], [ 51045.7, 391520.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.65, 391520.65 ], [ 51109.95, 391520.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.35, 391521.0 ], [ 51109.95, 391520.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.15, 391520.45 ], [ 51109.35, 391521.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.55, 391521.75 ], [ 51046.7, 391521.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.7, 391520.65 ], [ 51045.55, 391521.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.6, 391524.7 ], [ 51109.85, 391521.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.65, 391520.65 ], [ 51109.85, 391521.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.6, 391524.7 ], [ 51111.85, 391524.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.75, 391526.2 ], [ 51111.85, 391524.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.75, 391526.2 ], [ 51110.6, 391526.1 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.6, 391526.1 ], [ 51110.45, 391527.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.5, 391527.8 ], [ 51110.45, 391527.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.4, 391528.95 ], [ 51110.55, 391528.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.5, 391527.8 ], [ 51111.4, 391528.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.95, 391513.05 ], [ 51047.55, 391515.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51073.75, 391514.95 ], [ 51072.2, 391514.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.2, 391514.75 ], [ 51072.05, 391515.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51099.65, 391508.5 ], [ 51098.0, 391514.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51091.75, 391514.2 ], [ 51092.6, 391507.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51074.2, 391511.7 ], [ 51073.75, 391514.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51098.5, 391519.3 ], [ 51100.15, 391508.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51063.45, 391513.25 ], [ 51063.3, 391514.3 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.35, 391514.55 ], [ 51064.5, 391513.4 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51063.3, 391514.3 ], [ 51059.45, 391513.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.45, 391514.15 ], [ 51068.45, 391514.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51098.0, 391514.6 ], [ 51091.75, 391514.2 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.3, 391515.3 ], [ 51069.45, 391514.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.45, 391514.05 ], [ 51068.3, 391515.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.3, 391515.05 ], [ 51064.35, 391514.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51072.05, 391515.65 ], [ 51069.3, 391515.3 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.55, 391515.85 ], [ 51046.4, 391515.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51047.45, 391516.8 ], [ 51046.9, 391520.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.3, 391516.65 ], [ 51047.45, 391516.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.1, 391519.3 ], [ 51106.75, 391519.2 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51106.75, 391519.2 ], [ 51106.6, 391520.2 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51106.6, 391520.2 ], [ 51098.5, 391519.3 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.1, 391519.3 ], [ 51108.15, 391520.45 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.6, 391535.0 ], [ 51043.5, 391536.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.5, 391536.05 ], [ 51044.6, 391536.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.1, 391538.6 ], [ 51042.95, 391539.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.35, 391540.9 ], [ 51044.5, 391541.35 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.5, 391541.35 ], [ 51045.45, 391541.45 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51049.25, 391541.65 ], [ 51050.35, 391541.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.05, 391539.7 ], [ 51043.9, 391540.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51042.95, 391539.55 ], [ 51044.05, 391539.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.5, 391540.15 ], [ 51049.45, 391540.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51043.9, 391540.85 ], [ 51044.35, 391540.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.4, 391540.75 ], [ 51046.5, 391540.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.45, 391541.45 ], [ 51046.4, 391540.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51049.45, 391540.55 ], [ 51049.25, 391541.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.35, 391541.8 ], [ 51050.5, 391540.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.15, 391543.1 ], [ 51060.25, 391543.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.3, 391542.75 ], [ 51064.15, 391543.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51065.3, 391542.95 ], [ 51068.15, 391543.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51065.15, 391544.05 ], [ 51065.3, 391542.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51064.15, 391543.9 ], [ 51065.15, 391544.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.0, 391544.5 ], [ 51069.5, 391544.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.5, 391543.9 ], [ 51109.45, 391543.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.15, 391543.55 ], [ 51068.0, 391544.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.5, 391543.9 ], [ 51108.4, 391546.1 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.4, 391546.1 ], [ 51109.15, 391546.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.5, 391544.7 ], [ 51069.1, 391547.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.1, 391547.8 ], [ 51067.65, 391547.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.0, 391547.5 ], [ 51109.15, 391546.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.25, 391541.55 ], [ 51109.6, 391542.3 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51055.45, 391541.45 ], [ 51059.35, 391541.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.35, 391541.25 ], [ 51054.2, 391542.35 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51055.3, 391542.5 ], [ 51055.45, 391541.45 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51108.25, 391541.55 ], [ 51108.35, 391539.35 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51050.5, 391540.7 ], [ 51054.35, 391541.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51054.2, 391542.35 ], [ 51055.3, 391542.5 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51059.35, 391541.95 ], [ 51059.15, 391543.1 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51060.25, 391543.25 ], [ 51060.35, 391542.2 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.6, 391542.3 ], [ 51109.45, 391543.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51060.35, 391542.2 ], [ 51064.3, 391542.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.35, 391537.05 ], [ 51110.0, 391537.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.6, 391536.25 ], [ 51044.25, 391538.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.9, 391538.3 ], [ 51110.0, 391537.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.25, 391538.75 ], [ 51043.1, 391538.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.9, 391538.3 ], [ 51109.85, 391538.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.85, 391538.6 ], [ 51108.35, 391539.35 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.8, 391533.55 ], [ 51110.55, 391533.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.25, 391530.85 ], [ 51045.35, 391531.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.35, 391531.0 ], [ 51044.8, 391535.15 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.2, 391532.6 ], [ 51109.8, 391533.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.4, 391529.85 ], [ 51044.25, 391530.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51045.6, 391530.05 ], [ 51044.4, 391529.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.2, 391532.6 ], [ 51109.55, 391530.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51046.7, 391521.9 ], [ 51045.6, 391530.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.55, 391528.85 ], [ 51109.55, 391530.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51110.55, 391533.8 ], [ 51110.35, 391534.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51044.8, 391535.15 ], [ 51043.6, 391535.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.65, 391534.95 ], [ 51110.35, 391534.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.35, 391537.05 ], [ 51109.65, 391534.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51066.75, 391553.8 ], [ 51066.6, 391555.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51088.2, 391551.9 ], [ 51094.7, 391552.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51076.9, 391557.8 ], [ 51078.05, 391557.95 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.95, 391555.2 ], [ 51067.8, 391556.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51069.1, 391555.35 ], [ 51077.1, 391556.6 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.8, 391549.25 ], [ 51068.2, 391554.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.85, 391555.05 ], [ 51103.45, 391553.75 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.2, 391554.0 ], [ 51066.75, 391553.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51087.65, 391557.55 ], [ 51088.2, 391551.9 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51066.6, 391555.0 ], [ 51067.95, 391555.2 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51068.9, 391556.7 ], [ 51069.1, 391555.35 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.8, 391556.55 ], [ 51068.9, 391556.7 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51078.25, 391556.65 ], [ 51087.65, 391557.55 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51077.1, 391556.6 ], [ 51076.9, 391557.8 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51078.05, 391557.95 ], [ 51078.25, 391556.65 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51104.05, 391549.0 ], [ 51104.15, 391549.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.65, 391547.6 ], [ 51067.45, 391549.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51095.35, 391547.85 ], [ 51104.05, 391549.0 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51109.0, 391547.5 ], [ 51113.35, 391548.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51067.45, 391549.05 ], [ 51068.8, 391549.25 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51094.7, 391552.0 ], [ 51095.35, 391547.85 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51111.85, 391555.05 ], [ 51113.35, 391548.05 ] ] } },
# # { "type": "Feature", "properties": { }, "geometry": { "type": "LineString", "coordinates": [ [ 51104.15, 391549.0 ], [ 51103.45, 391553.75 ] ] } }
# # ]
# # }"""
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
#         skel = calc_skel(conv, pause=False, output=False)
# #    
# #    
# #   



 
    def test_goes(self):
        segments = [ ((51076.45,391503.5),(51075.45,391503.4)), ((51075.45,391503.4),(51075.25,391504.65)), ((51075.25,391504.65),(51073.85,391504.45)), ((51085.65,391504.8),(51084.55,391504.7)), ((51076.25,391504.9),(51076.45,391503.5)), ((51073.85,391504.45),(51073.7,391505.55)), ((51090.35,391507.3),(51086.8,391506.85)), ((51091.2,391506.4),(51090.4,391506.4)), ((51086.8,391506.5),(51085.5,391506.3)), ((51091.1,391507.45),(51091.2,391506.4)), ((51086.8,391506.85),(51086.8,391506.5)), ((51090.4,391506.4),(51090.35,391507.3)), ((51084.55,391504.7),(51084.45,391506.05)), ((51084.45,391506.05),(51076.25,391504.9)), ((51073.7,391505.55),(51075.0,391505.7)), ((51085.5,391506.3),(51085.65,391504.8)), ((51092.6,391507.7),(51091.1,391507.45)), ((51046.9,391511.9),(51046.75,391512.9)), ((51046.75,391512.9),(51047.95,391513.05)), ((51102.4,391509.15),(51100.15,391508.6)), ((51103.9,391510.2),(51102.4,391509.15)), ((51048.55,391511.0),(51048.2,391510.95)), ((51048.2,391510.95),(51048.05,391512.05)), ((51054.55,391511.9),(51053.55,391511.75)), ((51100.15,391508.6),(51099.65,391508.5)), ((51049.9,391510.95),(51048.95,391510.8)), ((51072.95,391510.0),(51072.75,391511.5)), ((51074.4,391510.2),(51072.95,391510.0)), ((51048.95,391510.8),(51048.55,391511.0)), ((51050.6,391511.7),(51049.9,391510.95)), ((51072.75,391511.5),(51074.2,391511.7)), ((51075.0,391505.7),(51074.4,391510.2)), ((51050.45,391512.5),(51050.6,391511.7)), ((51053.55,391511.75),(51053.4,391512.9)), ((51048.05,391512.05),(51046.9,391511.9)), ((51054.4,391513.05),(51054.55,391511.9)), ((51053.4,391512.9),(51050.45,391512.5)), ((51064.5,391513.4),(51063.45,391513.25)), ((51059.6,391512.7),(51058.55,391512.55)), ((51058.55,391512.55),(51058.4,391513.6)), ((51059.45,391513.8),(51059.6,391512.7)), ((51058.4,391513.6),(51054.4,391513.05)), ((51046.4,391515.7),(51046.3,391516.65)), ((51046.9,391520.8),(51045.7,391520.65)), ((51110.65,391520.65),(51109.95,391520.25)), ((51109.35,391521.0),(51109.95,391520.25)), ((51108.15,391520.45),(51109.35,391521.0)), ((51045.55,391521.75),(51046.7,391521.9)), ((51045.7,391520.65),(51045.55,391521.75)), ((51110.6,391524.7),(51109.85,391521.7)), ((51110.65,391520.65),(51109.85,391521.7)), ((51110.6,391524.7),(51111.85,391524.9)), ((51111.75,391526.2),(51111.85,391524.9)), ((51111.75,391526.2),(51110.6,391526.1)), ((51110.6,391526.1),(51110.45,391527.65)), ((51111.5,391527.8),(51110.45,391527.65)), ((51111.4,391528.95),(51110.55,391528.85)), ((51111.5,391527.8),(51111.4,391528.95)), ((51047.95,391513.05),(51047.55,391515.85)), ((51073.75,391514.95),(51072.2,391514.75)), ((51072.2,391514.75),(51072.05,391515.65)), ((51099.65,391508.5),(51098.0,391514.6)), ((51091.75,391514.2),(51092.6,391507.7)), ((51109.4,391514.1),(51103.9,391510.2)), ((51074.2,391511.7),(51073.75,391514.95)), ((51103.9,391510.2),(51102.45,391519.7)), ((51098.5,391519.3),(51100.15,391508.6)), ((51063.45,391513.25),(51063.3,391514.3)), ((51064.35,391514.55),(51064.5,391513.4)), ((51063.3,391514.3),(51059.45,391513.8)), ((51069.45,391514.15),(51068.45,391514.05)), ((51098.0,391514.6),(51091.75,391514.2)), ((51069.3,391515.3),(51069.45,391514.15)), ((51068.45,391514.05),(51068.3,391515.05)), ((51068.3,391515.05),(51064.35,391514.55)), ((51072.05,391515.65),(51069.3,391515.3)), ((51047.55,391515.85),(51046.4,391515.7)), ((51117.5,391516.3),(51109.4,391514.1)), ((51047.45,391516.8),(51046.9,391520.8)), ((51046.3,391516.65),(51047.45,391516.8)), ((51108.1,391519.3),(51106.75,391519.2)), ((51102.45,391519.7),(51098.5,391519.3)), ((51106.75,391519.2),(51106.6,391520.2)), ((51106.6,391520.2),(51098.5,391519.3)), ((51108.1,391519.3),(51108.15,391520.45)), ((51043.6,391535.0),(51043.5,391536.05)), ((51043.5,391536.05),(51044.6,391536.25)), ((51043.1,391538.6),(51042.95,391539.55)), ((51044.35,391540.9),(51044.5,391541.35)), ((51044.5,391541.35),(51045.45,391541.45)), ((51049.25,391541.65),(51050.35,391541.8)), ((51044.05,391539.7),(51043.9,391540.85)), ((51042.95,391539.55),(51044.05,391539.7)), ((51046.5,391540.15),(51049.45,391540.55)), ((51043.9,391540.85),(51044.35,391540.9)), ((51046.4,391540.75),(51046.5,391540.15)), ((51045.45,391541.45),(51046.4,391540.75)), ((51049.45,391540.55),(51049.25,391541.65)), ((51050.35,391541.8),(51050.5,391540.7)), ((51059.15,391543.1),(51060.25,391543.25)), ((51064.3,391542.75),(51064.15,391543.9)), ((51065.3,391542.95),(51068.15,391543.55)), ((51065.15,391544.05),(51065.3,391542.95)), ((51064.15,391543.9),(51065.15,391544.05)), ((51068.0,391544.5),(51069.5,391544.7)), ((51108.5,391543.9),(51109.45,391543.65)), ((51068.15,391543.55),(51068.0,391544.5)), ((51108.5,391543.9),(51108.4,391546.1)), ((51108.4,391546.1),(51109.15,391546.15)), ((51069.5,391544.7),(51069.1,391547.8)), ((51069.1,391547.8),(51067.65,391547.6)), ((51109.0,391547.5),(51109.15,391546.15)), ((51108.25,391541.55),(51109.6,391542.3)), ((51055.45,391541.45),(51059.35,391541.95)), ((51054.35,391541.25),(51054.2,391542.35)), ((51055.3,391542.5),(51055.45,391541.45)), ((51108.25,391541.55),(51108.35,391539.35)), ((51050.5,391540.7),(51054.35,391541.25)), ((51054.2,391542.35),(51055.3,391542.5)), ((51059.35,391541.95),(51059.15,391543.1)), ((51060.25,391543.25),(51060.35,391542.2)), ((51109.6,391542.3),(51109.45,391543.65)), ((51060.35,391542.2),(51064.3,391542.75)), ((51109.35,391537.05),(51110.0,391537.15)), ((51044.6,391536.25),(51044.25,391538.75)), ((51109.9,391538.3),(51110.0,391537.15)), ((51044.25,391538.75),(51043.1,391538.6)), ((51114.7,391538.3),(51109.9,391538.3)), ((51109.9,391538.3),(51109.85,391538.6)), ((51109.85,391538.6),(51108.35,391539.35)), ((51109.8,391533.55),(51110.55,391533.8)), ((51044.25,391530.85),(51045.35,391531.0)), ((51045.35,391531.0),(51044.8,391535.15)), ((51109.2,391532.6),(51109.8,391533.55)), ((51044.4,391529.85),(51044.25,391530.85)), ((51045.6,391530.05),(51044.4,391529.85)), ((51109.2,391532.6),(51109.55,391530.0)), ((51116.0,391529.6),(51117.5,391516.3)), ((51046.7,391521.9),(51045.6,391530.05)), ((51116.0,391529.6),(51111.4,391528.95)), ((51110.55,391528.85),(51109.55,391530.0)), ((51110.55,391533.8),(51110.35,391534.85)), ((51044.8,391535.15),(51043.6,391535.0)), ((51109.65,391534.95),(51110.35,391534.85)), ((51109.35,391537.05),(51109.65,391534.95)), ((51114.7,391538.3),(51116.0,391529.6)), ((51066.75,391553.8),(51066.6,391555.0)), ((51088.2,391551.9),(51094.7,391552.0)), ((51076.9,391557.8),(51078.05,391557.95)), ((51067.95,391555.2),(51067.8,391556.55)), ((51069.1,391555.35),(51077.1,391556.6)), ((51068.8,391549.25),(51068.2,391554.0)), ((51103.45,391553.75),(51098.5,391553.45)), ((51098.5,391553.45),(51089.3,391553.25)), ((51111.85,391555.05),(51103.45,391553.75)), ((51068.2,391554.0),(51066.75,391553.8)), ((51087.65,391557.55),(51088.2,391551.9)), ((51066.6,391555.0),(51067.95,391555.2)), ((51068.9,391556.7),(51069.1,391555.35)), ((51067.8,391556.55),(51068.9,391556.7)), ((51078.25,391556.65),(51087.65,391557.55)), ((51077.1,391556.6),(51076.9,391557.8)), ((51078.05,391557.95),(51078.25,391556.65)), ((51087.2,391561.25),(51087.05,391561.25)), ((51081.65,391563.15),(51076.55,391562.45)), ((51087.05,391561.25),(51086.5,391565.2)), ((51081.4,391564.6),(51081.65,391563.15)), ((51091.3,391562.6),(51110.1,391565.85)), ((51090.45,391566.55),(51091.3,391562.6)), ((51086.5,391565.2),(51081.4,391564.6)), ((51086.95,391565.15),(51086.5,391565.2)), ((51082.6,391559.55),(51076.75,391559.15)), ((51097.45,391558.95),(51110.95,391561.1)), ((51097.3,391561.2),(51097.45,391558.95)), ((51110.95,391561.1),(51111.85,391555.05)), ((51089.3,391553.25),(51088.35,391559.85)), ((51082.6,391560.75),(51082.6,391559.55)), ((51097.3,391561.2),(51087.45,391559.75)), ((51087.45,391559.75),(51087.2,391561.25)), ((51088.35,391559.85),(51097.3,391561.2)), ((51097.3,391561.2),(51091.7,391560.75)), ((51087.05,391561.25),(51082.6,391560.75)), ((51110.1,391565.85),(51110.95,391561.1)), ((51076.75,391559.15),(51076.55,391562.45)), ((51091.3,391562.6),(51091.7,391560.75)), ((51090.35,391567.35),(51090.45,391566.55)), ((51076.55,391562.45),(51076.15,391568.75)), ((51086.95,391565.15),(51086.45,391570.2)), ((51076.15,391568.75),(51076.1,391568.75)), ((51090.35,391567.35),(51089.95,391570.5)), ((51076.1,391568.75),(51076.05,391569.9)), ((51086.45,391570.2),(51076.15,391568.75)), ((51087.95,391576.1),(51085.1,391575.7)), ((51089.85,391575.1),(51092.4,391575.6)), ((51092.4,391575.6),(51093.3,391575.75)), ((51089.85,391575.1),(51089.55,391576.15)), ((51085.1,391575.7),(51085.05,391576.15)), ((51093.3,391575.75),(51093.2,391576.45)), ((51087.95,391576.1),(51089.55,391576.15)), ((51087.0,391586.5),(51085.3,391586.1)), ((51085.45,391582.4),(51085.3,391586.1)), ((51093.2,391576.45),(51107.7,391580.05)), ((51089.8,391579.75),(51088.55,391579.45)), ((51075.55,391575.6),(51074.7,391581.15)), ((51107.7,391580.05),(51108.5,391575.3)), ((51085.05,391576.15),(51084.85,391580.35)), ((51106.9,391584.05),(51107.7,391580.05)), ((51092.55,391580.45),(51089.8,391579.75)), ((51085.55,391580.45),(51084.85,391580.35)), ((51088.0,391583.7),(51088.55,391579.45)), ((51085.55,391580.45),(51085.45,391582.4)), ((51106.9,391584.05),(51092.55,391580.45)), ((51074.7,391581.15),(51085.45,391582.4)), ((51088.0,391583.7),(51088.45,391579.8)), ((51074.7,391581.15),(51073.85,391586.8)), ((51088.45,391579.8),(51087.0,391586.5)), ((51087.4,391589.05),(51105.0,391593.9)), ((51102.3,391606.85),(51101.4,391606.7)), ((51070.95,391611.35),(51071.65,391611.45)), ((51070.95,391611.35),(51076.6,391612.05)), ((51071.65,391611.45),(51076.6,391612.05)), ((51101.1,391615.45),(51102.3,391606.85)), ((51078.65,391612.35),(51079.55,391612.45)), ((51076.6,391612.05),(51078.65,391612.35)), ((51076.6,391612.05),(51079.55,391612.45)), ((51079.55,391612.45),(51079.5,391612.75)), ((51079.5,391612.75),(51086.0,391613.6)), ((51086.0,391613.6),(51094.7,391614.7)), ((51094.7,391614.7),(51094.7,391614.6)), ((51094.7,391614.6),(51101.1,391615.45)), ((51102.45,391599.2),(51102.45,391599.15)), ((51102.45,391599.15),(51088.2,391597.3)), ((51073.05,391594.15),(51086.35,391595.85)), ((51088.2,391597.3),(51073.0,391595.3)), ((51086.35,391595.85),(51087.4,391589.05)), ((51101.4,391606.7),(51102.45,391599.15)), ((51101.4,391606.7),(51102.45,391599.2)), ((51073.0,391595.3),(51070.95,391611.35)), ((51088.2,391597.3),(51086.0,391613.6)), ((51073.85,391586.8),(51073.8,391587.25)), ((51079.75,391588.0),(51073.8,391587.25)), ((51079.75,391588.0),(51079.7,391587.55)), ((51088.0,391583.7),(51087.5,391588.2)), ((51106.1,391588.25),(51088.0,391583.7)), ((51106.1,391588.25),(51106.9,391584.05)), ((51105.0,391593.9),(51106.1,391588.25)), ((51073.8,391587.25),(51073.05,391594.15)), ((51079.7,391587.55),(51087.5,391588.2)), ((51087.4,391589.05),(51087.5,391588.2)), ((51092.9,391572.65),(51093.15,391571.25)), ((51109.3,391570.6),(51110.1,391565.85)), ((51076.05,391569.9),(51075.6,391575.05)), ((51109.3,391570.6),(51090.35,391567.35)), ((51093.15,391571.25),(51089.95,391570.5)), ((51108.5,391575.3),(51109.3,391570.6)), ((51075.6,391575.05),(51075.55,391575.6)), ((51092.9,391572.65),(51108.5,391575.3)), ((51092.4,391575.6),(51092.9,391572.65)), ((51085.05,391576.15),(51075.6,391575.05)), ((51104.05,391549.0),(51104.15,391549.0)), ((51067.65,391547.6),(51067.45,391549.05)), ((51095.35,391547.85),(51104.05,391549.0)), ((51109.0,391547.5),(51113.35,391548.05)), ((51113.35,391548.05),(51114.7,391538.3)), ((51067.45,391549.05),(51068.8,391549.25)), ((51094.7,391552.0),(51095.35,391547.85)), ((51111.85,391555.05),(51113.35,391548.05)), ((51104.15,391549.0),(51103.45,391553.75)) ]
        conv = ToPointsAndSegments()
        for line in segments:
            conv.add_point(line[0])
            conv.add_point(line[1])
            conv.add_segment(*line)
        skel = calc_skel(conv, pause=PAUSE, output=OUTPUT)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 985, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 718, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        self.assertEqual(len(filter(lambda v: v.stops_at is None, skel.vertices)), 17)
        self.assertEqual(len(filter(lambda v: v.stops_at is not None, skel.vertices)), 968)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
            if v.stops_at is not None and not v.inf_fast:
                assert at_same_location((v.stop_node, v), v.stops_at), \
                    "{} {} {}".format(id(v),
                                      v.stop_node.pos,
                                      v.position_at(v.stops_at) )





#     def test_goes_gobackwards_20160303(self):
#         s = """
# {
# "type": "FeatureCollection",
# "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::28992" } },
#                                                                                  
# "features": [
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817155664.000000, "to": 140493816672936.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.133100733426, 0.282656616556 ], [ -0.148050438054, 0.380269393835 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817155904.000000, "to": 140493817155664.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.132355020073, 0.274453769672 ], [ -0.133100733426, 0.282656616556 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817156264.000000, "to": 140493817155904.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.124425641702, 0.183706439431 ], [ -0.132355020073, 0.274453769672 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817156504.000000, "to": 140493817156264.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.121501168335, 0.116443551985 ], [ -0.124425641702, 0.183706439431 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817158904.000000, "to": 140493817159384.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.553983773526, 0.291702685122 ], [ 0.568263113107, 0.207811565086 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817159384.000000, "to": 140493816748824.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.568263113107, 0.207811565086 ], [ 0.582507258649, 0.123236950932 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817176264.000000, "to": 140493816749784.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.640529242934, -0.194355587932 ], [ 0.664840953673, -0.369940165498 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493817176624.000000, "to": 140493817158904.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.539584850771, 0.377196288981 ], [ 0.553983773526, 0.291702685122 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816672936.000000, "to": 140493816674136.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.148050438054, 0.380269393835 ], [ -0.163375913628, 0.482138731472 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816673536.000000, "to": 140493816250928.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.183077060318, 0.6631881194 ], [ -0.182297614308, 0.663287747838 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816673776.000000, "to": 140493816673536.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.164381721724, 0.491191004336 ], [ -0.183077060318, 0.6631881194 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816674136.000000, "to": 140493816673776.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.163375913628, 0.482138731472 ], [ -0.164381721724, 0.491191004336 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816693536.000000, "to": 140493816693896.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.480975141943, 0.677895532379 ], [ 0.510945310226, 0.523957849833 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816693896.000000, "to": 140493816694256.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.510945310226, 0.523957849833 ], [ 0.525200742742, 0.449116829127 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816694256.000000, "to": 140493817176624.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.525200742742, 0.449116829127 ], [ 0.539584850771, 0.377196288981 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816694496.000000, "to": 140493815920952.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.446697902722, 0.713433930809 ], [ 0.446697902722, 0.668449815889 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816694856.000000, "to": 140493816694976.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.450269787031, 0.8051822885 ], [ 0.434227453755, 0.802508566288 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816694976.000000, "to": 140493816694496.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.434227453755, 0.802508566288 ], [ 0.446697902722, 0.713433930809 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816695456.000000, "to": 140493816694856.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.415257415039, 1.05610428778 ], [ 0.450269787031, 0.8051822885 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816695576.000000, "to": 140493816695456.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.308366800535, 1.04190787804 ], [ 0.415257415039, 1.05610428778 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816695936.000000, "to": 140493816695576.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.308366800535, 1.0433330301 ], [ 0.308366800535, 1.04190787804 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816696056.000000, "to": 140493816695936.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.0967013694352, 1.01657073422 ], [ 0.308366800535, 1.0433330301 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816709200.000000, "to": 140493816696056.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.0707741493383, 0.994670089456 ], [ 0.0967013694352, 1.01657073422 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816709800.000000, "to": 140493816226232.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.0713325311092, 0.988875228579 ], [ -0.0698446294759, 0.989092970282 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816710160.000000, "to": 140493816709800.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.159601229642, 0.978175992394 ], [ -0.0713325311092, 0.988875228579 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816710520.000000, "to": 140493816710160.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.221389561168, 0.969349087887 ], [ -0.159601229642, 0.978175992394 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816712200.000000, "to": 140493815919512.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.698618859107, -0.491966802989 ], [ -0.705210931729, -0.422750040464 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816712920.000000, "to": 140493816879056.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.704542595805, -0.2874819799 ], [ -0.67765666086, -0.284494653792 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816729680.000000, "to": 140493815893480.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.606655435305, -0.269083759995 ], [ -0.600865455417, -0.273350060965 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816730760.000000, "to": 140493816297424.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.156497578363, -0.015554576225 ], [ -0.111934761382, -0.00859142206911 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816731120.000000, "to": 140493816357784.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.275582274593, -0.223606591433 ], [ -0.273240156394, -0.223294309007 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816731600.000000, "to": 140493816297064.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.224709673355, -0.86402036886 ], [ -0.326817919445, -0.878607261159 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816731840.000000, "to": 140493816357304.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.172776052199, -0.938589288061 ], [ -0.183588343757, -0.857497101371 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816732080.000000, "to": 140493816822192.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.0294927618655, -1.0096290022 ], [ -0.0143637873812, -1.01577961581 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816732440.000000, "to": 140493816732080.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.0310901581828, -1.03119385248 ], [ 0.0294927618655, -1.0096290022 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816732560.000000, "to": 140493816732920.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.0105070042516, -1.04277709772 ], [ -0.127155059212, -1.05444190321 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816732920.000000, "to": 140493816896880.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.127155059212, -1.05444190321 ], [ -0.13040343446, -1.03413955791 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816733520.000000, "to": 140493816822072.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.248303391063, -0.969368261353 ], [ 0.250882840132, -0.996452476573 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816746184.000000, "to": 140493816410672.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.366488893059, -0.956005669538 ], [ 0.310666246195, -0.967170198908 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816746544.000000, "to": 140493816785928.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.262216376644, -0.853714914008 ], [ 0.276720919522, -0.96463200661 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816748824.000000, "to": 140493816896520.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.582507258649, 0.123236950932 ], [ 0.597763519865, 0.0379813735458 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816749784.000000, "to": 140493816857736.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.664840953673, -0.369940165498 ], [ 0.688138291933, -0.525853121539 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816767744.000000, "to": 140493816786408.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.542426143839, -0.854937813189 ], [ 0.451376749473, -0.919500111012 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816768224.000000, "to": 140493815919392.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.402353483721, -0.890452777355 ], [ -0.511727389338, -0.9068588632 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816769664.000000, "to": 140493816712920.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.701703304536, -0.309249879629 ], [ -0.704542595805, -0.2874819799 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816770384.000000, "to": 140493816295744.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.520821934369, -0.261988806009 ], [ -0.434091573458, -0.25016193861 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816783288.000000, "to": 140493817156504.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.119661462503, 0.116443551985 ], [ -0.121501168335, 0.116443551985 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816785928.000000, "to": 140493816733520.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.276720919522, -0.96463200661 ], [ 0.248303391063, -0.969368261353 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816786288.000000, "to": 140493815891320.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.156531168729, -1.03787209138 ], [ -0.170119695637, -0.938222894053 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816786408.000000, "to": 140493816822552.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.451376749473, -0.919500111012 ], [ 0.416792178104, -0.94370931097 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816786768.000000, "to": 140493816746544.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.279675282177, -0.852597544054 ], [ 0.262216376644, -0.853714914008 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816805688.000000, "to": 140493816244536.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.654549201639, -0.787174742311 ], [ -0.65333324616, -0.787022747877 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816819792.000000, "to": 140493816894360.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.298871285716, -0.0366852165948 ], [ -0.274116852895, -0.0330178932137 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816820032.000000, "to": 140493816730760.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.159925009388, 0.00758058319987 ], [ -0.156497578363, -0.015554576225 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816822072.000000, "to": 140493815893720.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.250882840132, -0.996452476573 ], [ 0.14922528172, -0.996452476573 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816822192.000000, "to": 140493816732560.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.0143637873812, -1.01577961581 ], [ -0.0105070042516, -1.04277709772 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816822552.000000, "to": 140493816746184.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.416792178104, -0.94370931097 ], [ 0.366488893059, -0.956005669538 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816840872.000000, "to": 140493816858216.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.566261978626, -0.91980328487 ], [ -0.573763380512, -0.916052583926 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816841352.000000, "to": 140493816769664.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.722680350863, -0.312110385947 ], [ -0.701703304536, -0.309249879629 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816841712.000000, "to": 140493816729680.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.674914760296, -0.276268952102 ], [ -0.606655435305, -0.269083759995 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816842432.000000, "to": 140493816820032.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.276856111355, -0.00836456707083 ], [ -0.159925009388, 0.00758058319987 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816856656.000000, "to": 140493816732440.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.151603840382, -1.02023806319 ], [ 0.0310901581828, -1.03119385248 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816856776.000000, "to": 140493816767744.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.719819179214, -0.806756988766 ], [ 0.542426143839, -0.854937813189 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816857736.000000, "to": 140493816856776.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.688138291933, -0.525853121539 ], [ 0.719819179214, -0.806756988766 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816858216.000000, "to": 140493816878456.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.573763380512, -0.916052583926 ], [ -0.614362494031, -0.921852457285 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816858456.000000, "to": 140493816893640.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.660680016052, -0.582117912949 ], [ -0.681354888155, -0.585563724966 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816878456.000000, "to": 140493816916160.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.614362494031, -0.921852457285 ], [ -0.617122275661, -0.901614058663 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816878816.000000, "to": 140493816897120.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.659103657501, -0.747848464811 ], [ -0.675256761564, -0.629392368346 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816879056.000000, "to": 140493816841712.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.67765666086, -0.284494653792 ], [ -0.674914760296, -0.276268952102 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816879416.000000, "to": 140493816296224.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.434318995372, -0.248854262606 ], [ -0.342664560563, -0.236355930584 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816879656.000000, "to": 140493816245136.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.342849550639, -0.234937673335 ], [ -0.275390862177, -0.224818870068 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816880016.000000, "to": 140493817176264.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.613702562266, -0.0691644114832 ], [ 0.640529242934, -0.194355587932 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816893640.000000, "to": 140493816299224.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.681354888155, -0.585563724966 ], [ -0.695453771838, -0.49157116708 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816894240.000000, "to": 140493816819792.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.283850446476, -0.156851930513 ], [ -0.298871285716, -0.0366852165948 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816894360.000000, "to": 140493816842432.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.274116852895, -0.0330178932137 ], [ -0.276856111355, -0.00836456707083 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816896520.000000, "to": 140493816880016.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.597763519865, 0.0379813735458 ], [ 0.613702562266, -0.0691644114832 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816896880.000000, "to": 140493816786288.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.13040343446, -1.03413955791 ], [ -0.156531168729, -1.03787209138 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816897120.000000, "to": 140493816897360.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.675256761564, -0.629392368346 ], [ -0.654661979557, -0.626706092432 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816897360.000000, "to": 140493816858456.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.654661979557, -0.626706092432 ], [ -0.660680016052, -0.582117912949 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816914600.000000, "to": 140493816783288.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.115499793047, 0.0508972580504 ], [ -0.119661462503, 0.116443551985 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816915680.000000, "to": 140493816840872.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.516471271698, -0.911941594301 ], [ -0.566261978626, -0.91980328487 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816915920.000000, "to": 140493816805688.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.636994499801, -0.904206087898 ], [ -0.654549201639, -0.787174742311 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816916160.000000, "to": 140493816915920.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.617122275661, -0.901614058663 ], [ -0.636994499801, -0.904206087898 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816410672.000000, "to": 140493816786768.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.310666246195, -0.967170198908 ], [ 0.279675282177, -0.852597544054 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816250928.000000, "to": 140493816710520.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.182297614308, 0.663287747838 ], [ -0.221389561168, 0.969349087887 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816226232.000000, "to": 140493816709200.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.0698446294759, 0.989092970282 ], [ -0.0707741493383, 0.994670089456 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816244536.000000, "to": 140493816298504.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.65333324616, -0.787022747877 ], [ -0.65747824195, -0.747645287868 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816245136.000000, "to": 140493816731120.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.275390862177, -0.224818870068 ], [ -0.275582274593, -0.223606591433 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816357304.000000, "to": 140493816298144.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.183588343757, -0.857497101371 ], [ -0.225020119861, -0.861640278982 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816357784.000000, "to": 140493815918912.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.273240156394, -0.223294309007 ], [ -0.282431615608, -0.156656229704 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816295744.000000, "to": 140493816879416.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.434091573458, -0.25016193861 ], [ -0.434318995372, -0.248854262606 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816296224.000000, "to": 140493816879656.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.342664560563, -0.236355930584 ], [ -0.342849550639, -0.234937673335 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816296584.000000, "to": 140493816770384.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.520762195752, -0.262426889195 ], [ -0.520821934369, -0.261988806009 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816297064.000000, "to": 140493816298744.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.326817919445, -0.878607261159 ], [ -0.402488539497, -0.889417349739 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816297424.000000, "to": 140493816914600.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.111934761382, -0.00859142206911 ], [ -0.115499793047, 0.0508972580504 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816298144.000000, "to": 140493816731600.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.225020119861, -0.861640278982 ], [ -0.224709673355, -0.86402036886 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816298504.000000, "to": 140493816878816.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.65747824195, -0.747645287868 ], [ -0.659103657501, -0.747848464811 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816298744.000000, "to": 140493816768224.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.402488539497, -0.889417349739 ], [ -0.402353483721, -0.890452777355 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493816299224.000000, "to": 140493816712200.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.695453771838, -0.49157116708 ], [ -0.698618859107, -0.491966802989 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815891320.000000, "to": 140493816731840.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.170119695637, -0.938222894053 ], [ -0.172776052199, -0.938589288061 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815893480.000000, "to": 140493816296584.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.600865455417, -0.273350060965 ], [ -0.520762195752, -0.262426889195 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815893720.000000, "to": 140493816856656.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.14922528172, -0.996452476573 ], [ 0.151603840382, -1.02023806319 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815918912.000000, "to": 140493816894240.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.282431615608, -0.156656229704 ], [ -0.283850446476, -0.156851930513 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815919392.000000, "to": 140493816915680.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.511727389338, -0.9068588632 ], [ -0.516471271698, -0.911941594301 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815919512.000000, "to": 140493816841352.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ -0.705210931729, -0.422750040464 ], [ -0.722680350863, -0.312110385947 ] ] } },
# { "type": "Feature", "properties": { "time": 0.050000, "from": 140493815920952.000000, "to": 140493816693536.000000 }, "geometry": { "type": "LineString", "coordinates": [ [ 0.446697902722, 0.668449815889 ], [ 0.480975141943, 0.677895532379 ] ] } }
# ]
# }
# """
#         import json
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



    def test_capital_U(self):
        polys = [
        [(38.3852, 32.0156), (39.2659501953, 32.0912681641), (40.0374453125, 32.3105390625), (40.6971646484, 32.6618123047), (41.2425875, 33.1334875), (41.6711931641, 33.7139642578), (41.9804609375, 34.3916421875), (42.1678701172, 35.1549208984), (42.2309, 35.9922), (42.2309, 47.834), (47.5316, 47.834), (47.5316, 35.7273), (47.4732092773, 34.7657740479), (47.3213726562, 33.8784173828), (47.081449707, 33.063555542), (46.7588, 32.3195140625), (46.3587831055, 31.6446184814), (45.8867585938, 31.0371943359), (45.3480860352, 30.4955671631), (44.748125, 30.0180625), (44.0922350586, 29.6030058838), (43.3857757812, 29.2487228516), (41.8425875, 28.7157796875), (40.1614367187, 28.4058373047), (38.3852, 28.3055), (36.6090451172, 28.4058373047), (34.9279234375, 28.7157796875), (33.3847244141, 29.2487228516), (32.6782488525, 29.6030058838), (32.0223375, 30.0180625), (31.4223515381, 30.4955671631), (30.8836521484, 31.0371943359), (30.4116005127, 31.6446184814), (30.0115578125, 32.3195140625), (29.6888852295, 33.063555542), (29.4489439453, 33.8784173828), (29.2970951416, 34.7657740479), (29.2387, 35.7273), (29.2387, 47.834), (34.5395, 47.834), (34.5395, 35.9922), (34.6025257812, 35.1549208984), (34.789925, 34.3916421875), (35.0991804687, 33.7139642578), (35.527775, 33.1334875), (36.0731914062, 32.6618123047), (36.7329125, 32.3105390625), (37.5044210937, 32.0912681641), (38.3852, 32.0156)],
        ]
        conv = ToPointsAndSegments()
        for ring in polys:
            conv.add_polygon([ring])
        skel = calc_skel(conv, pause=False, output=OUTPUT, shrink=True)#, pause=False, output=False)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 158, len(skel.segments())
        # check the amount of skeleton nodes
        self.assertEqual(len(skel.sk_nodes), 111)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 30, len(not_stopped)
        assert len(stopped) == 128, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
#             if v.stops_at is not None and not v.inf_fast:
#                 assert at_same_location((v.stop_node, v), v.stops_at), \
#                     "{} {} LINESTRING({} {})".format(id(v),
#                                     v.stop_node.pos,
#                                     v.position_at(v.starts_at),
#                                     v.position_at(v.stops_at) )


    def test_tudelft_logo(self):
        polys = [
        # flame
        [(28.2387, 57.1504), (27.7545962891, 57.0337472656), (27.2828078125, 56.993484375), (26.8394935547, 57.0375167969), (26.4408125, 57.17375), (26.1029236328, 57.4100894531), (25.8419859375, 57.754440625), (25.6741583984, 58.2147089844), (25.6156, 58.7988), (25.6856849121, 59.2881812744), (25.8839386719, 59.7683330078), (26.1934848145, 60.2400170654), (26.597446875, 60.7039953125), (27.6211128906, 61.6118818359), (28.819925, 62.4980875), (30.0588714844, 63.3687072266), (31.202940625, 64.2298359375), (32.1171207031, 65.0875685547), (32.4458111816, 65.5170659912), (32.6664, 65.948), (32.8248125, 66.6851625), (32.7710109375, 66.9061765625), (32.6176, 66.9805), (32.5208703125, 66.9222546875), (32.4679125, 66.7729125), (32.3706484375, 66.5442390625), (32.141, 66.248), (31.1034759766, 65.3984353516), (29.9355515625, 64.7423015625), (28.6692482422, 64.2321388672), (27.3365875, 63.8204875), (24.6002796875, 63.1028796875), (23.2606755859, 62.7020037109), (21.9828, 62.2098), (20.9997419922, 61.7483013672), (19.7656484375, 61.0788734375), (18.4207775391, 60.1820806641), (17.1053875, 59.0384875), (16.5025784912, 58.3680671631), (15.9597365234, 57.6286583984), (15.4943938721, 56.8178317627), (15.1240828125, 55.9331578125), (14.8663356201, 54.9722071045), (14.7386845703, 53.9325501953), (14.7586619385, 52.8117576416), (14.9438, 51.6074), (15.122925, 50.8023), (15.252640625, 50.40393125), (15.3949, 50.2336), (15.5243578125, 50.3437421875), (15.5897375, 50.6433625), (15.6117, 51.6262), (15.6561465332, 52.3362411621), (15.8000691406, 52.9857136719), (16.031892334, 53.5809723145), (16.340040625, 54.128371875), (17.1390105469, 55.1050128906), (18.104375, 55.966475), (20.163871875, 57.547215625), (21.0727964844, 58.3681707031), (21.7777, 59.2773), (22.104725, 59.739675), (22.2554875, 59.862834375), (22.3512, 59.8191), (22.3023, 59.3027), (22.0503148438, 58.5393394531), (21.6885625, 57.836665625), (20.851325, 56.570375), (20.4836242188, 55.9852566406), (20.221725, 55.417821875), (20.1195195312, 54.8573199219), (20.2309, 54.293), (20.6030839844, 53.7075248047), (21.082534375, 53.4021359375), (21.6320488281, 53.3341009766), (22.214425, 53.4606875), (22.7924605469, 53.7391630859), (23.328953125, 54.1267953125), (23.7867003906, 54.5808517578), (24.1285, 55.0586), (24.368925, 55.470225), (24.465971875, 55.57165625), (24.5609, 55.5859), (24.6368625, 55.3106625), (24.5941, 54.791), (24.2621640625, 53.2469984375), (23.7833125, 51.9836375), (23.4592181641, 51.4272880859), (23.0629046875, 50.9052078125), (22.0063, 49.916), (21.566953125, 49.6562546875), (21.130475, 49.4675625), (20.815009375, 49.2970390625), (20.7395761719, 49.2020642578), (20.7387, 49.0918), (20.9814125, 49.0273125), (21.4195, 49.0469), (22.2465202881, 49.156970874), (23.0534919922, 49.3736341797), (23.8374688721, 49.6869346924), (24.5955046875, 50.0869171875), (26.0219681641, 51.1071072266), (27.3093125, 52.3545625), (28.4339677734, 53.7496412109), (29.3723640625, 55.2127015625), (30.1009314453, 56.6641017578), (30.5961, 58.0242), (30.6886375, 58.3597625), (30.6215, 58.5781), (30.509940625, 58.5979578125), (30.381, 58.5274875), (30.0922, 58.2668), (29.2161125, 57.616425), (28.2387, 57.1504)],
         #T
        [(15.5055, 28.7004), (20.8063, 28.7004), (20.8063, 44.1211), (26.7445, 44.1211), (26.7445, 47.8328), (9.5668, 47.8328), (9.5668, 44.1211), (15.5055, 44.1211), (15.5055, 28.7004)],
        # U
        [(38.3852, 32.0156), (39.2659501953, 32.0912681641), (40.0374453125, 32.3105390625), (40.6971646484, 32.6618123047), (41.2425875, 33.1334875), (41.6711931641, 33.7139642578), (41.9804609375, 34.3916421875), (42.1678701172, 35.1549208984), (42.2309, 35.9922), (42.2309, 47.834), (47.5316, 47.834), (47.5316, 35.7273), (47.4732092773, 34.7657740479), (47.3213726562, 33.8784173828), (47.081449707, 33.063555542), (46.7588, 32.3195140625), (46.3587831055, 31.6446184814), (45.8867585938, 31.0371943359), (45.3480860352, 30.4955671631), (44.748125, 30.0180625), (44.0922350586, 29.6030058838), (43.3857757812, 29.2487228516), (41.8425875, 28.7157796875), (40.1614367187, 28.4058373047), (38.3852, 28.3055), (36.6090451172, 28.4058373047), (34.9279234375, 28.7157796875), (33.3847244141, 29.2487228516), (32.6782488525, 29.6030058838), (32.0223375, 30.0180625), (31.4223515381, 30.4955671631), (30.8836521484, 31.0371943359), (30.4116005127, 31.6446184814), (30.0115578125, 32.3195140625), (29.6888852295, 33.063555542), (29.4489439453, 33.8784173828), (29.2970951416, 34.7657740479), (29.2387, 35.7273), (29.2387, 47.834), (34.5395, 47.834), (34.5395, 35.9922), (34.6025257812, 35.1549208984), (34.789925, 34.3916421875), (35.0991804687, 33.7139642578), (35.527775, 33.1334875), (36.0731914062, 32.6618123047), (36.7329125, 32.3105390625), (37.5044210937, 32.0912681641), (38.3852, 32.0156)],
         # D -- exterior
        [(55.4875, 45.5563), (59.4066, 45.5563), (60.2057835693, 45.5178564697), 
         (60.9454076172, 45.4051830078), (61.6265759033, 45.2222653076), 
         (62.2503921875, 44.9730890625), (62.8179602295, 44.6616399658), 
         (63.3303837891, 44.2919037109), (64.1942125, 43.3935125), 
         (64.8507083984, 42.3098009766), (65.3087015625, 41.0726546875), 
         (65.5770220703, 39.7139591797), (65.6645, 38.2656), 
         (65.5770220703, 36.8175103516), (65.3087015625, 35.4592765625), 
         (64.8507083984, 34.2227138672), (64.1942125, 33.1396375), 
         (63.3303837891, 32.2418626953), (62.8179602295, 31.8724056396), 
         (62.2503921875, 31.5612046875), (61.6265759033, 31.3122367432), 
         (60.9454076172, 31.1294787109), (60.2057835693, 31.0169074951), 
         (59.4066, 30.9785), (55.4875, 30.9785), 
         (55.4875, 45.5563)],
        # D -- interior
        [ 
         (52.8324, 28.7004), (59.4059, 28.7004), 
         (60.8560672363, 28.7788331543), 
         (62.1440332031, 29.0031808594), 
         (63.2792692871, 29.3570154785), (64.271246875, 29.823909375), (65.1294373535, 30.3874349121), (65.8633121094, 31.0311644531), (66.4823425293, 31.7386703613), (66.996, 32.493525), (67.4137559082, 33.2793007324), (67.7450816406, 34.0795699219), (68.186328125, 35.657878125), (68.3955105469, 37.0970285156), (68.4484, 38.2656), (68.3955105469, 39.4344525391), (68.186328125, 40.8740328125), (67.7450816406, 42.4528623047), (67.4137559082, 43.2534084717), (66.996, 44.0394625), (66.4823425293, 44.7945895752), (65.8633121094, 45.5023548828), (65.1294373535, 46.1463236084), (64.271246875, 46.7100609375), (63.2792692871, 47.1771320557), (62.1440332031, 47.5311021484), (60.8560672363, 47.7555364014), (59.4059, 47.834), (52.8324, 47.834), (52.8324, 28.7004)],
#          #e
#          #e -- outershell
        [(82.9195, 34.8762), (82.9195, 36.123), (82.8224828125, 37.4505816406), (82.53454375, 38.658784375), (82.0603515625, 39.7298449219), (81.404575, 40.646), (80.5718828125, 41.3894863281), (79.56694375, 41.942540625), (78.3944265625, 42.2873996094), (77.059, 42.4063),(76.2952375244, 42.3687171631), (75.5838064453, 42.2585341797), (74.9242850342, 42.0795993408), (74.3162515625, 41.8357609375), (73.7592843018, 41.5308672607), (73.2529615234, 41.1687666016), (72.3905625, 40.2883375), (71.7256806641, 39.2252599609), (71.2549421875, 38.0103203125), (70.9749732422, 36.6743048828), (70.8824, 35.248), (70.9637001953, 33.823009375), (71.2144078125, 32.50744375), (71.6447333984, 31.3261375), (72.2648875, 30.303925), (73.0850806641, 29.465640625), (73.5733826904, 29.1232322266), (74.1155234375, 28.83611875), (74.7127792236, 28.6074044922), (75.3664263672, 28.44019375), (76.848, 28.3027), (77.9991910156, 28.3734771484), (79.058021875, 28.5858296875), (80.0117917969, 28.9397892578), (80.8478, 29.4353875), (81.5533457031, 30.0726560547), (82.115728125, 30.8516265625), (82.5222464844, 31.7723306641), (82.7602, 32.8348), (80.1098, 32.8348), (79.9671755859, 32.1632625), (79.7567359375, 31.59635), (79.4750064453, 31.1294125), (79.1185125, 30.7578), (78.6837794922, 30.4768625), (78.1673328125, 30.28195), (77.5656978516, 30.1684125), (76.8754, 30.1316), (75.9894021484, 30.2347720703), (75.2544671875, 30.5276953125), (74.6604455078, 30.9854802734), (74.1971875, 31.5832375), (73.8545435547, 32.2960775391), (73.6223640625, 33.0991109375), (73.4904994141, 33.9674482422), (73.4488, 34.8762), (82.9195, 34.8762), (82.9195, 34.8762)],
         #e -- innershell
        [(73.5055, 36.6262), (73.5694832031, 37.3917933594), (73.744890625, 38.118946875), (74.0270464844, 38.7880457031),  (74.411275, 39.379475), (74.8929003906, 39.8736199219), (75.467246875, 40.250865625), (76.1296386719, 40.4915972656), (76.8754, 40.5762), (77.7209189453, 40.4999767578), (78.4335015625, 40.2795953125), (79.0193740234, 39.9274880859), (79.4847625, 39.4560875), (79.8358931641, 38.8778259766), (80.0789921875, 38.2051359375), (80.2202857422, 37.4504498047), (80.266, 36.6262), (73.5055, 36.6262)],
#              
#          #l
        [(85.973, 28.6992), (88.49331, 28.6992), (88.49331, 47.834), (85.973, 47.834), (85.973, 28.6992), (85.973, 28.6992)],
#         #f
        [(96.3883, 28.7004), (96.3883, 40.2512), (99.4605, 40.2512), (99.4605, 42.0027), (96.3883, 42.0027), (96.3883, 44.1512), (96.4229054688, 44.6702857422), (96.52635625, 45.0817171875), (96.6981039062, 45.3973431641), (96.9376, 45.6290125), (97.2442960938, 45.7885740234), (97.61764375, 45.8878765625), (98.5621, 45.9531), (99.8336, 45.875), (99.8336, 47.9656), (98.9403125, 48.1487), (98.0309, 48.2313), (97.1673613281, 48.1749609375), (96.374484375, 48.004725), (95.6659777344, 47.7187640625), (95.05555, 47.31525), (94.5569097656, 46.7923546875), (94.183765625, 46.14825), (93.9498261719, 45.3811078125), (93.8688, 44.4891), (93.8688, 42.0027), (91.273, 42.0027), (91.273, 40.2512), (93.8688, 40.2512), (93.8688, 28.7004), (96.3883, 28.7004)],
         #t
        [(100.908, 42.0027), (100.908, 40.2512), (103.188, 40.2512), (103.188, 31.7734), (103.250359375, 30.4847203125), (103.393189453, 29.8978896484), (103.668125, 29.3748875), (104.118419922, 28.9348306641), (104.787328125, 28.5968359375), (105.718103516, 28.3800201172), (106.954, 28.3035), (107.811, 28.3438375), (108.677, 28.4609), (108.677, 30.3953), (107.35, 30.2371), (106.713328125, 30.322746875), (106.191125, 30.58245), (105.837859375, 31.020353125), (105.708, 31.6406), (105.708, 40.2512), (108.782, 40.2512), (108.782, 42.0027), (105.708, 42.0027), (105.708, 45.634), (103.188, 44.8391), (103.188, 42.0012), (100.908, 42.0027)],
        ]
        conv = ToPointsAndSegments()
        for ring in polys:
            conv.add_polygon([ring])
        skel = calc_skel(conv, pause=False, output=OUTPUT)#, pause=False, output=False)
        # check the amount of segments in the skeleton
        assert len(skel.segments()) == 1398, len(skel.segments())
        # check the amount of skeleton nodes
        assert len(skel.sk_nodes) == 1041, len(skel.sk_nodes)
        # check the amount of kinetic vertices that are (not) stopped
        not_stopped = filter(lambda v: v.stops_at is None, skel.vertices)
        stopped = filter(lambda v: v.stops_at is not None, skel.vertices)
        assert len(not_stopped) == 14, len(not_stopped)
        assert len(stopped) == 1384, len(stopped)
        # check cross relationship between kinetic vertices and skeleton nodes
        for v in skel.vertices:
            assert at_same_location((v.start_node, v), v.starts_at)
#             if v.stops_at is not None and not v.inf_fast:
#                 assert at_same_location((v.stop_node, v), v.stops_at), \
#                     "{} {} LINESTRING({} {})".format(id(v),
#                                       v.stop_node.pos,
#                                       v.position_at(v.starts_at),
#                                       v.position_at(v.stops_at) )


if __name__ == "__main__":
    if LOGGING:
        import logging
        import sys
        root = logging.getLogger()
        root.setLevel(logging.WARNING)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
#         formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatter = logging.Formatter('%(asctime)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)
 
    unittest.main(verbosity=2)