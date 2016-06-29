import logging
import sys
root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

from tri import ToPointsAndSegments
from grassfire import calc_skel

# # convert to triangulation input
# segments = [[(0, 0), (10, 0)],
#             [(10, 0), (10.1, 5.1)],
#             [(10.1, 5.1), (0, 5)],
#             [(0, 5), (0, 0)],
#             ]

# # convert to triangulation input
segments = [[(0, 0), (10, 0)],
            [(10, 0), (5, 10)],
            [(5, 10), (0, 0)],
            ]

conv = ToPointsAndSegments()
for line in segments:
    conv.add_point(line[0])
    conv.add_point(line[1])
    conv.add_segment(*line)
# skeletonize / offset
skel = calc_skel(conv, pause=True, output=True, shrink=True)
