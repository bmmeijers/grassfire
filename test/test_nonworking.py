import unittest

from tri import ToPointsAndSegments
from grassfire import calc_skel

class TestSimultaneousEvents(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

#     def test_chishape(self):
#         ring = [(-0.12999106777200001,-0.32109517457699999),(-0.16826546739199999,-0.28581718751000001),(-0.166723188391,-0.18304326555799999),(-0.14428079224000001,-0.165036480131),(-0.0626940259892,-0.00761432147016),(-0.0519067121278,-0.10494115954700001),(0.000620341167536,-0.16142214118699999),(0.034134894903,-0.233656472664),(0.0175820094043,-0.15693554716999999),(-0.00042310504988,-0.00676775008218),(-0.0330913291091,0.0575304773025),(-0.0519892012015,0.08570153009170001),(-0.10887914106799999,0.0613865659042),(-0.17432707364800001,0.117041967082),(-0.197373592875,0.201184615491),(-0.22737971517300001,0.22772375476600001),(-0.286238242877,0.29353637718499997),(-0.0688830380876,0.28598413943399997),(-0.0189602933902,0.26492760793199999),(0.0082493390123,0.28888769157799998),(0.0481471400365,0.215794229472),(0.13562174756100001,0.0642602345078),(0.201996782273,0.00561982649704),(0.13399950275399999,-0.00504710753071),(0.160552210246,-0.21835213939299999),(0.18611593572999999,-0.30206901543800002),(0.151463066945,-0.341340054467),(0.126464904332,-0.36172471919799998),(0.0920053070572,-0.41642920433000002),(0.105205160836,-0.44778009140699998),(0.00495683765215,-0.551998270904),(-0.020125337515,-0.60919704696900001),(-0.0214362359418,-0.66467947604699995),(-0.12870796380899999,-0.76265467931800002),(-0.14729557673300001,-0.71923994053499996),(-0.24716578512000001,-0.79061490991799999),(-0.31149974888100002,-0.70754775130100001),(-0.34382727127700002,-0.61521826153500003),(-0.35888186908899999,-0.67317315268099998),(-0.38962851549100003,-0.70479586976899999),(-0.33494797050800001,-0.70374928059700004),(-0.38748547673200001,-0.80751666594100002),(-0.25781488341300002,-0.81288014327799996),(-0.28319340277400001,-0.85276537531399998),(-0.19895516143799999,-0.82587129221599997),(-0.144842483109,-0.84638645978799998),(-0.0554186697369,-0.91021588670300002),(-0.048826334165,-0.83481862743599999),(-0.0485086162308,-0.79172914355599999),(0.00195195896021,-0.73060797450000003),(0.0125467617639,-0.66191034185300002),(0.15196860556799999,-0.447134243195),(0.322039601989,-0.64599024901199997),(0.27086716766399999,-0.70942350345299998),(0.23249861449500001,-0.72683485553500005),(0.135139129868,-0.79710706465299996),(0.143526223914,-0.82367733837000001),(0.141920121127,-0.976921124059),(0.195602835527,-0.94152016784600001),(0.31193457825300003,-0.80030375390599995),(0.31746131940900002,-0.80173223735300003),(0.36570349918299999,-0.78722865795200003),(0.31741642090099997,-0.75437234181099999),(0.31552449370800001,-0.73991583559499996),(0.36219425490099999,-0.64913547424200002),(0.43966940786399999,-0.60517960729200004),(0.49800750045999997,-0.77708305831000002),(0.58166904750000004,-0.71014735383600003),(0.67923922663299996,-0.71102927640900004),(0.58833137470899999,-0.66141551308199997),(0.59370237665000003,-0.55322023610500004),(0.73191186053799995,-0.54112200709799996),(0.78142424442699998,-0.48783349913599999),(0.89254615769900003,-0.363233761913),(0.81797238219199997,-0.34311266294100001),(0.739885752058,-0.36116612418100003),(0.64851642331299997,-0.49804359472999998),(0.55603122297499996,-0.52041793502699996),(0.46485135630899999,-0.53781533480699995),(0.38202308473500002,-0.45056883179099999),(0.39321613570300001,-0.34810990114599999),(0.35366169466800002,-0.42361425177099998),(0.27176586342800002,-0.45254847919399999),(0.18251288806900001,-0.35485407871000002),(0.21970850709600001,-0.309800346896),(0.245277622221,-0.159921228405),(0.252640141042,-0.12795726707499999),(0.235989649927,-0.0121897210647),(0.27052274329199999,-0.0541435598898),(0.26254986394500002,-0.00971770823302),(0.29705056257099999,0.0128466495031),(0.43430988219599997,0.0527995950295),(0.52768564081400005,0.10012349218200001),(0.66270265694200003,-0.0813207165175),(0.55508043775100002,-0.16861626615700001),(0.70162045221400005,-0.145960079444),(0.89817517402799996,-0.16859081321399999),(0.93462294241199995,-0.116555920262),(0.90750782241899997,-0.0533694886527),(0.911867756709,-0.0833046747075),(0.82401430764299999,-0.09544019832179999),(0.718927675968,-0.0594287314564),(0.71311617868400001,0.0208603722082),(0.85966775963800002,0.15456094971699999),(0.855643307834,0.188335509481),(0.60649419536500004,0.16794188102900001),(0.50302839349200001,0.198944293552),(0.424398030649,0.14226075997900001),(0.35816770905700002,0.10863476471899999),(0.18525626613599999,0.12982327991000001),(0.26076377691399999,0.25951179218999998),(0.25719911799799999,0.30083962624900001),(0.218537736717,0.31128990402899998),(0.13420113015400001,0.35265889114999999),(0.0284172531529,0.30362713582700002),(-0.0379910903481,0.31596228088200001),(0.0498393764997,0.45467409027400002),(0.0600953605572,0.55522681030800003),(-0.131090369589,0.66957627387499996),(-0.0400643341379,0.667341818167),(-0.058404842527,0.68024289153700002),(-0.10948375437299999,0.75755608396200003),(-0.106442820635,0.82337126361699997),(0.0179776484812,0.78065482615000004),(0.12927506496999999,0.68122797123199996),(0.27473891286500002,0.69265593770300005),(0.200587337664,0.61076692087999995),(0.23173073210299999,0.51302890893300002),(0.30476198000999999,0.61723266677400002),(0.323260970594,0.59849069656999998),(0.33992696194200001,0.59402706306200004),(0.40140603789700002,0.63796427233499997),(0.35477193119599998,0.43769892740999999),(0.51488171905799995,0.37037089365999998),(0.60876862639999996,0.32717151772699998),(0.61225250330100001,0.321233872423),(0.62487344705600001,0.35304136813999998),(0.59284213148200005,0.48328829781100002),(0.61517803639299995,0.49947078574999998),(0.76791896233300005,0.45684256431100001),(0.86574092801699998,0.49775387774199997),(0.65897550151999995,0.58421560882599999),(0.65199537318900003,0.645912404138),(0.551994338566,0.55244952695600003),(0.47613543020799998,0.64805236451399995),(0.49715675939100001,0.71771002878300005),(0.52799256265700001,0.74418912283299998),(0.384784243197,0.78838271163700002),(0.34465830798500002,0.90533954381799997),(0.24254994106,0.82075018800199995),(0.21558963112000001,0.86359414417699998),(0.219431181733,0.95434701308299996),(0.19569317277000001,0.94576368431699998),(0.182117992521,0.86098631155500005),(0.155770003106,0.84767418481500001),(0.19416500544900001,0.80040685334600004),(0.0589396307635,0.81483014140300003),(-0.0577220539131,0.89116094574899996),(-0.11643399802,0.94338220137200002),(-0.17799776596799999,0.96162856980099998),(-0.180555761653,0.94986204938600005),(-0.137544123569,0.91744442202400001),(-0.14161698616499999,0.80637353194100003),(-0.16786357370300001,0.72485546116699995),(-0.174036935846,0.666804655952),(-0.33688802694600001,0.68639323222899995),(-0.36535969101400001,0.80754809235400005),(-0.45485862441800001,0.79556741373899997),(-0.385876352353,0.636184133747),(-0.53866136037099999,0.59823501872200002),(-0.54119399654800004,0.59656915043600001),(-0.50262421878899999,0.50411168741800005),(-0.34791655129999999,0.60950223303499995),(-0.36709062003999998,0.368070267502),(-0.38730733949899998,0.33782163062499998),(-0.38183191627200003,0.26733768045400003),(-0.32001779437400002,0.31393176982600002),(-0.28113860950899999,0.25636325711000002),(-0.22405967697699999,0.18654517031000001),(-0.21382475457299999,0.154157867635),(-0.243600582201,0.062996296526),(-0.34169523592599998,0.0258370804139),(-0.385026386868,0.00324134597771),(-0.421664651434,0.0616690672473),(-0.51041267720600003,0.14686099198200001),(-0.60816939688899996,0.14621945661499999),(-0.75981110425999998,0.328585842731),(-0.62772190456900001,0.30706097647000002),(-0.55455205027400001,0.31143710888800002),(-0.59633638224800001,0.32199336951000002),(-0.63696946456100001,0.40030164309600003),(-0.74216776569499998,0.36434414578800001),(-0.78588039780200003,0.51255123041399997),(-0.80767227779499995,0.54384075376300001),(-0.81494931033499995,0.42953799194300002),(-0.86760804829000004,0.344834063292),(-0.88740570215100001,0.33916177790399998),(-0.97820503743499998,0.161921304786),(-0.97926947903399997,0.11387234820599999),(-0.86331785824100005,0.125872971124),(-0.732198437185,0.0366675540027),(-0.76414307266500003,-0.10978517883699999),(-0.75745350301500003,-0.12633059565599999),(-0.67990655911800002,-0.13158805886899999),(-0.70437658004799997,-0.26485697053000001),(-0.75114815147299996,-0.28503007153100002),(-0.78489919064699998,-0.32511594389999998),(-0.875480713972,-0.26917957145299998),(-0.84019146953699997,-0.19220581767200001),(-0.88421402908400004,-0.27886737579100002),(-0.82843027917000001,-0.334338546633),(-0.78299512181399999,-0.33826363950499999),(-0.77447635266000003,-0.42230405216),(-0.72871451268200005,-0.47733153384299998),(-0.60659665896299997,-0.51825488145900001),(-0.661470957262,-0.61691615499999997),(-0.56815747057699995,-0.64200076744599999),(-0.51383752411600003,-0.60844810765000001),(-0.48251084036800002,-0.54375256183099996),(-0.44678729686599999,-0.45808852526600002),(-0.45018988347599997,-0.44340840711399998),(-0.49546071953100002,-0.45442913128599999),(-0.589583188772,-0.497284228592),(-0.62632124200200001,-0.46002948755599998),(-0.68079216493799999,-0.37790671891099997),(-0.64150861858599995,-0.317200343931),(-0.55999348236900004,-0.222056313028),(-0.49792032738699998,-0.27095937511500001),(-0.49830486694600001,-0.28830364457300001),(-0.48831943843699999,-0.26572144570400003),(-0.46353613852999997,-0.20760300475499999),(-0.60240696066499999,-0.18722825587899999),(-0.61967014826699995,-0.12863470121500001),(-0.65594401649900003,-0.114325467046),(-0.71073251992499997,-0.0571926425734),(-0.65739974234300003,0.0635636054481),(-0.40551506033000001,-0.0511595518414),(-0.39376327111699999,-0.0607718490811),(-0.246053676492,-0.0276599262734),(-0.22537624483499999,-0.14386854527000001),(-0.18751401372500001,-0.237711894639),(-0.23658636280500001,-0.26809503520200001),(-0.31669941126399997,-0.264323056582),(-0.30937335599299998,-0.31668772015000002),(-0.29687393094199999,-0.36767492574499999),(-0.210866969214,-0.396169963731),(-0.21098150751899999,-0.462050805846),(-0.192307066607,-0.56220026499099995),(-0.161231219511,-0.524196707185),(-0.08141306981679999,-0.36953378155099997),(-0.12999106777200001,-0.32109517457699999)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)

# ##############################################################################
# # PARALLEL EDGES IN THE INPUT, leading to problems 
# # (e.g. nodes not on correct location)
# ##############################################################################
# 
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
#         skel = calc_skel(conv,
#                          pause=True,
#                          output=True)


#     def test_flipped_cshape(self):
#         """Parallel c-shape wavefront"""
#         # FIXME: missing parallel piece of wavefront
#         # plus having a vertex too many
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


#     def test_cshape_bottom(self):
#         """Parallel c-shape wavefront with longer segment on bottom"""
#         # FIXME: missing parallel piece of wavefront
#         # plus having a vertex too many
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, 0.0), (0.0, 3)]
#         l1 = [(0, 3), (5,3)]
#         l2 = [(0,0), (10,0)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_cshape_top(self):
#         """Parallel c-shape wavefront with longer segment on top"""
#         # FIXME: missing parallel piece of wavefront
#         # plus having a vertex too many
#         conv = ToPointsAndSegments()
#         l0 = [(0.0, 0.0), (0.0, 3)]
#         l1 = [(0, 3), (10,3)]
#         l2 = [(0,0), (5,0)]
#         for line in l0, l1, l2:
#             conv.add_point(line[0])
#             conv.add_point(line[1])
#             conv.add_segment(*line)
#         skel = calc_skel(conv, pause=True, output=True)


# 
#     ############## FIXME:
#     ## Last event is now 3-triangle, this leads to wrong skeleton!
#     def test_rect_extra_pt(self):
#         """" """
#         conv = ToPointsAndSegments()
#         polygon = [[(0, 0), (0., 10), (15,10), (15,0.), (2., 0.), (0,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
 
#     def test_tiny_v(self):
#         """Tiny V at bottom of square"""
#         conv = ToPointsAndSegments()
#         polygon = [[(-10, 0), (-10., 100.), (100.,100.), (100.,0.), (2., 0.), (1,-1), (0,0), (-10,0)]]
#         conv.add_polygon(polygon)
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == (10+7)
#         positions = [n.pos for n in skel.sk_nodes]
        # additional: 
        # check if last node geerated internally is at (50,50)
#     ############## :FIXME
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
#         skel = calc_skel(conv, pause=True, output=True)
#         assert len(skel.segments()) == 20
#         assert len(skel.sk_nodes) == 12
#         positions = [n.pos for n in skel.sk_nodes]

#     def test_church(self):
#         """church in naaldwijk
#         """
#         ring = [(74029.47599999999511056,445622.80800000001909211),(74022.8169999999954598,445622.11400000000139698),(74023.09900000000197906,445619.97800000000279397),(74021.96000000000640284,445619.86800000001676381),(74022.06500000000232831,445618.78100000001722947),(74023.11100000000442378,445618.88199999998323619),(74024.28500000000349246,445606.70799999998416752),(74024.5,445606.72899999999208376),(74024.98399999999674037,445601.71000000002095476),(74025.26700000000710133,445601.7370000000228174),(74025.43099999999685679,445600.02799999999115244),(74033.13599999999860302,445600.77100000000791624),(74033.26799999999639113,445599.39600000000791624),(74034.29600000000209548,445599.49499999999534339),(74034.16400000000430737,445600.86300000001210719),(74037.91899999999441206,445601.22499999997671694),(74038.05199999999604188,445599.84600000001955777),(74039.09900000000197906,445599.9469999999855645),(74038.96700000000419095,445601.32099999999627471),(74042.68099999999685679,445601.67999999999301508),(74042.8120000000053551,445600.32099999999627471),(74043.87600000000384171,445600.42300000000977889),(74043.74499999999534339,445601.78100000001722947),(74047.73099999999976717,445602.16499999997904524),(74048.09600000000500586,445598.37599999998928979),(74047.09299999999348074,445598.27899999998044223),(74047.19999999999708962,445597.1720000000204891),(74048.21899999999732245,445597.27100000000791624),(74048.31600000000617001,445596.2629999999771826),(74049.39500000000407454,445596.36700000002747402),(74049.29700000000593718,445597.38000000000465661),(74055.42600000000675209,445597.97100000001955777),(74055.52499999999417923,445596.94300000002840534),(74056.61999999999534339,445597.04899999999906868),(74056.52099999999336433,445598.0719999999855645),(74057.59600000000500586,445598.17599999997764826),(74057.4940000000060536,445599.23300000000745058),(74056.38800000000628643,445599.12599999998928979),(74056.05599999999685679,445602.56800000002840534),(74057.1190000000060536,445602.66999999998370185),(74056.9980000000068685,445603.92099999997299165),(74055.94000000000232831,445603.81800000002840534),(74055.66300000000046566,445606.68599999998696148),(74058.68499999999767169,445606.97700000001350418),(74058.76900000000023283,445606.09999999997671694),(74059.74599999999918509,445606.19400000001769513),(74059.65799999999580905,445607.106000000028871),(74062.35899999999674037,445607.36599999997997656),(74062.44800000000395812,445606.4469999999855645),(74063.42299999999522697,445606.54100000002654269),(74063.32499999999708962,445607.5590000000083819),(74066.11000000000058208,445607.9340000000083819),(74066.59100000000034925,445603.26099999999860302),(74065.60700000000360887,445603.15999999997438863),(74065.71199999999953434,445602.1379999999771826),(74066.66800000000512227,445602.2370000000228174),(74066.77300000000104774,445601.21600000001490116),(74067.73299999999289867,445601.31500000000232831),(74067.62900000000081491,445602.31900000001769513),(74070.46400000000721775,445602.61099999997531995),(74070.57499999999708962,445601.54200000001583248),(74071.51300000000628643,445601.63900000002468005),(74071.40799999999580905,445602.65799999999580905),(74072.27300000000104774,445602.74699999997392297),(74072.16599999999743886,445603.78999999997904524),(74071.26700000000710133,445603.6969999999855645),(74071.0059999999939464,445606.231000000028871),(74071.77899999999499414,445607.34999999997671694),(74071.67900000000372529,445608.32900000002700835),(74073.66300000000046566,445609.20000000001164153),(74074.42100000000209548,445608.67599999997764826),(74074.96000000000640284,445609.45699999999487773),(74074.32899999999790452,445609.93900000001303852),(74075.64800000000104774,445612.22700000001350418),(74076.4940000000060536,445611.94199999998090789),(74076.72800000000279397,445612.91399999998975545),(74075.7519999999931315,445613.26799999998183921),(74075.47599999999511056,445615.94599999999627471),(74076.3690000000060536,445616.33799999998882413),(74076.1889999999984866,445617.23200000001816079),(74075.14699999999720603,445616.83299999998416752),(74073.19599999999627471,445618.96000000002095476),(74073.7519999999931315,445619.76500000001396984),(74072.98699999999371357,445620.29300000000512227),(74072.50999999999476131,445619.60200000001350418),(74069.86000000000058208,445620.56199999997625127),(74069.76700000000710133,445621.46700000000419095),(74068.79700000000593718,445621.36700000002747402),(74068.88599999999860302,445620.50300000002607703),(74065.9330000000045402,445620.19900000002235174),(74065.84299999999348074,445621.07500000001164153),(74064.97999999999592546,445620.98599999997531995),(74065.07099999999627471,445620.09700000000884756),(74062.14100000000325963,445619.79399999999441206),(74062.04799999999522697,445620.69500000000698492),(74061.05299999999988358,445620.59299999999348074),(74061.14500000000407454,445619.69799999997485429),(74059.73399999999674037,445619.55200000002514571),(74059.3120000000053551,445623.64199999999254942),(74060.21499999999650754,445623.73499999998603016),(74060.11699999999837019,445624.68800000002374873),(74059.3129999999946449,445624.60499999998137355),(74059.24099999999452848,445625.31099999998696148),(74058.32000000000698492,445625.21600000001490116),(74058.38999999999941792,445624.54100000002654269),(74053.94599999999627471,445624.08199999999487773),(74053.65700000000651926,445626.89000000001396984),(74054.60099999999511056,445626.98800000001210719),(74054.48200000000360887,445628.143999999971129),(74053.52400000000488944,445628.04499999998370185),(74053.41199999999662396,445629.1379999999771826),(74052.39999999999417923,445629.03399999998509884),(74052.51099999999860302,445627.95400000002700835),(74046.24300000000221189,445627.30800000001909211),(74046.1220000000030268,445628.4870000000228174),(74045.08000000000174623,445628.38000000000465661),(74045.19899999999324791,445627.22100000001955777),(74044.29799999999522697,445627.12800000002607703),(74044.42200000000593718,445625.92599999997764826),(74045.34900000000197906,445626.02199999999720603),(74045.74199999999837019,445622.09999999997671694),(74041.92200000000593718,445621.73200000001816079),(74041.8139999999984866,445622.84999999997671694),(74040.81900000000314321,445622.75400000001536682),(74040.92500000000291038,445621.65500000002793968),(74036.96499999999650754,445621.27299999998649582),(74036.86199999999371357,445622.34499999997206032),(74035.79399999999441206,445622.24200000002747402),(74035.89599999999336433,445621.1840000000083819),(74032.09600000000500586,445620.81800000002840534),(74031.98900000000139698,445621.91800000000512227),(74030.92900000000372529,445621.8159999999916181),(74031.03399999999965075,445620.72499999997671694),(74029.6889999999984866,445620.59499999997206032),(74029.47599999999511056,445622.80800000001909211)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, output=True)

    def test_house1(self):
        """House 1
        """
        ring = [(73293.27300000000104774,445228.5530000000144355),(73302.63499999999476131,445231.07000000000698492),(73301.72400000000197906,445234.67999999999301508),(73305.13199999999778811,445235.53999999997904524),(73305.53399999999965075,445233.94599999999627471),(73313.15300000000570435,445235.86800000001676381),(73311.83400000000256114,445241.09499999997206032),(73299.2440000000060536,445237.91800000000512227),(73299.54399999999441206,445236.73200000001816079),(73291.70799999999871943,445234.75500000000465661),(73293.27300000000104774,445228.5530000000144355)]
        conv = ToPointsAndSegments()
        conv.add_polygon([ring])
        skel = calc_skel(conv, #pause=True, 
                         output=True)

#     def test_house2(self):
#         ring = [(73220.912, 445241.233), (73218.453, 445250.0), (73218.252, 445250.715), (73215.704, 445250.0), (73214.981, 445249.797), (73214.924, 445250.0), (73214.366, 445251.99), (73208.627, 445250.38), (73208.734, 445250.0), (73211.762, 445239.205), (73216.446, 445240.519), (73216.56, 445240.112), (73217.103, 445240.264), (73217.779, 445239.427), (73220.181, 445240.101), (73220.429, 445241.097), (73220.912, 445241.233)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)

#     def test_cross(self):
#         ring = [(0,0), (10, 0), (10,-10), (15, -10), (15,0), (25,0), (25,5), (15,5), (15,15), (10,15), (10,5), (0,5), (0,0)]
#         conv = ToPointsAndSegments()
#         conv.add_polygon([ring])
#         skel = calc_skel(conv, pause=True, output=True)
#         # FIXME: are the following numbers correct?
#         assert len(skel.segments()) == 16+12, len(skel.segments())
#         assert len(skel.sk_nodes) == 16, len(skel.sk_nodes)


#     def test_parallelogram(self):
#         """Parallelogram with parallel wavefronts collapsing"""
#         conv = ToPointsAndSegments()
#         conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
#         skel = calc_skel(conv, pause=True, output=True)
#         positions = [n.pos for n in skel.sk_nodes]
#         assert (3.6412818342935513, 18.568803057155918) in positions
#         assert len(skel.sk_nodes) == 6, len(skel.sk_nodes)
#         assert len(skel.segments()) == 9, len(skel.segments())



#     def test_multiple_parallel(self):
#         """Parallelogram with parallel wavefronts collapsing"""
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

# 
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
#         skel = calc_skel(conv,pause=True, output=True)


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