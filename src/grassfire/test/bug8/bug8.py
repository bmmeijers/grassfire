"""
"""


if True:
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.WARNING)
#     ch = logging.StreamHandler(sys.stdout)
#     ch.setLevel(logging.WARN)
#     formatter = logging.Formatter('%(asctime)s - %(message)s')
#     ch.setFormatter(formatter)
#     root.addHandler(ch)

from tri.delaunay.helpers import ToPointsAndSegments
from grassfire import calc_skel

import timeit



# -- large example, with multiple examples
with open('bug_exterior.wkt') as fh:
    fh.readline()  # skip header in file (line with "wkt")
    wkt = fh.readline()
    from simplegeom.wkt import loads
    poly = loads(wkt)
    poly = poly[0]


# -- small sample
# import json
# with open('bug8.geojson') as fh:
#     j = fh.read()
# x = json.loads(j)
# print x
# ## parse segments from geo-json
# y = x['features'][0]
# poly = map(tuple, y['geometry']['coordinates'][0])


conv = ToPointsAndSegments()
for start, end in zip(poly[:-1], poly[1:]):
    conv.add_point(start)
    conv.add_point(end)
    conv.add_segment(start, end)

# # -- add first / last point
# #conv.add_point(poly[0])
# #conv.add_point(poly[-1])
# #conv.add_segment(poly[-1], poly[0])
# 
start = timeit.default_timer()
# skeletonize / offset
print(start)
skel = calc_skel(conv, pause=False, output=True, shrink=True, internal_only=True)
now = timeit.default_timer()
print now - start, "sec(s)"