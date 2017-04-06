"""
"""

from tri import ToPointsAndSegments
from grassfire import calc_skel

import timeit

if True:
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.WARN)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

from robustness89sfcgal import poly
with open('do.txt') as fh:
    wkt = fh.readline()
    from simplegeom.wkt import loads
    poly = loads(wkt)
    poly = poly[0]


# with open('bug_exterior.wkt') as fh:
#     fh.readline()  # skip header in file (line with "wkt")
#     wkt = fh.readline()
#     from simplegeom.wkt import loads
#     poly = loads(wkt)
#     poly = poly[0]


conv = ToPointsAndSegments()
for start, end in zip(poly[:-1], poly[1:]):
    conv.add_point(start)
    conv.add_point(end)
    conv.add_segment(start, end)

# -- add first / last point
#conv.add_point(poly[0])
#conv.add_point(poly[-1])
#conv.add_segment(poly[-1], poly[0])

start = timeit.default_timer()
# skeletonize / offset
skel = calc_skel(conv, pause=False, output=True, shrink=True)
now = timeit.default_timer()
print now - start, "sec(s)"