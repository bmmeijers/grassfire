from tri import ToPointsAndSegments
from grassfire import calc_skel
#from simplegeom.wkt import loads

"""Centre in Goes
"""

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

conv = ToPointsAndSegments()
polygon = [[(0,3), (0.5,5), (9,8.5), (10,2), (6,4), (3.5,1), (0,3)]]  
conv.add_polygon(polygon)

skel = calc_skel(conv, pause=True, output=True, shrink=True)
# skeletonize / offset

