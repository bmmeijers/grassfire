"""Test to get bisectors of lines,
of which I think the straight skeleton is a subset.
"""

from math import hypot
from grassfire.calc import vector, vector_mul_scalar, normalize, rotate90cw, rotate90ccw,\
    is_close
from operator import add, mul

def perp_dot(v1, v2):
    # return the area of the parallelogram between the two vectors, 
    # this area is signed and can be used to determine whether rotating 
    # from V1 to V2 moves in an counter clockwise or clockwise direction. 
    # It should also be noted that this is the determinant of the 2x2 matrix 
    # built from these two vectors.
    return (v1[0]*v2[1]) - (v1[1]*v2[0])

def length(v):
    return hypot(v[0], v[1])

def xpoint(s0, e0, s1, e1):
    x1, y1 = s0
    x2, y2 = e0
    x3, y3 = s1
    x4, y4 = e1
    denominator = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denominator != 0:
        Px = (x1*y2 - y1*x2) * (x3 - x4) - (x1 - x2)*(x3* y4 - y3 *x4) / denominator
        Py = (x1*y2 - y1 *x2)*(y3-y4)-(y1-y2)*(x3 *y4-y3* x4) / denominator
        return (Px, Py)
    else:
        return None

def bisector_line(l0, l1, factor=10):
    s0, e0 = l0
    s1, e1 = l1
    v = normalize(vector(e0, s0))
    u = normalize(vector(e1, s1))
    vl = length(v)
    ul = length(u)
    r = map(add, vector_mul_scalar(v, ul), vector_mul_scalar(u, vl))
#     r = map(add, v, u)
    if is_close(perp_dot(v,u), 0, method='weak'): # parallel lines
        # get the intersection point on the second line
        # if we rotate the first line 90 degrees
        tmp = xpoint(s0, map(add, s0, rotate90cw(v)), s1, e1)
        # vector that points from start of line 1 to point half way
        hv = vector_mul_scalar(vector(tmp, s0), 0.5)
        # point that lies half way
        xpt = tuple(map(add, s0, hv))
        bi = v
    else:
        # we are not parallel so get cross point
        xpt = xpoint(s0, e0, s1, e1)
        bi = normalize(r)
    return [map(add, xpt, vector_mul_scalar(bi, -factor)),
            map(add, xpt, vector_mul_scalar(bi, factor))]
#     vlength = length(v)
#     ulength = length(u)
#     r = normalize(map(add, vectormulscalar(v, ulength), vectormulscalar(u, vlength)))
#     print r
#     return r

def line(l):
    return "LINESTRING({0[0][0]} {0[0][1]}, {0[1][0]} {0[1][1]})".format(l)


def do():
    from math import pi, cos, sin, degrees
    ring = []
    pi2 = 2 * pi
    ct = 8
    alpha = pi / ct 
    for i in range(ct+1):
        ring.append( (cos(pi+i*alpha), sin(pi+i*alpha)))
    ring.append(ring[0])
    l = []
    for pt in ring:
        l.append("{0[0]} {0[1]}".format(pt))
    print "LINESTRING({0})".format(", ".join(l))
#     ring = [(0,0), (10,0), (10,10), (0,10), (0,0)]
    segments = []
    for segment in zip(ring[:-1], ring[1:]+[ring[0]]):
        segments.append(segment)
    
    for i in range(len(segments)):
        for j in range(i+1, len(segments)):
            si = segments[i]
            sj = segments[j]
            print line(bisector_line(si, sj))


def do2():
    from math import pi, cos, sin, degrees
    ring = [(0,0), (10,0), (10,100), (0,100), (0,0)]
    l = []
    for pt in ring:
        l.append("{0[0]} {0[1]}".format(pt))
    print "LINESTRING({0})".format(", ".join(l))
#     ring = [(0,0), (10,0), (10,10), (0,10), (0,0)]
    segments = []
    for segment in zip(ring[:-1], ring[1:]+[ring[0]]):
        segments.append(segment)
    
    for i in range(len(segments)):
        for j in range(i+1, len(segments)):
            si = segments[i]
            sj = segments[j]
            print line(bisector_line(si, sj, 10000))

# https://www.wyzant.com/resources/blogs/246582/howtofindadistancebetweentwoparallellines


do2()