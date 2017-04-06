"""Code for creating the grassfire logo
"""

from tri import ToPointsAndSegments
from grassfire import calc_skel

if True:
    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

conv = ToPointsAndSegments()
with open("segments.wkt") as fh:
    for line in fh:
        if line.startswith("LINESTRING"):
            seg = line[line.find("(")+1:-2]
            parta, partb = seg.split(",")
            start = tuple(map(float, parta.strip().split(" ")))
            end = tuple(map(float, partb.strip().split(" ")))
            conv.add_point(start)
            conv.add_point(end)
            conv.add_segment(start, end)

# skeletonize / offset
skel = calc_skel(conv, pause=False, output=True, shrink=True)
