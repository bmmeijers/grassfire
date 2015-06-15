# turn angle between two vectors... oriented away from same points
#
# atan2(v2.y, v2.x) - atan2(v1.y, v1.x)
# add 2pi until positive

from itertools import imap
from operator import add, sub, mul, truediv
from math import pi, atan2, degrees, hypot, sin
from pprint import pprint
from tri.delaunay import orient2d

#from math import pi, degrees
#PI2 = 2 * pi
#
#def sweep_angle(start_angle, end_angle, ccw = True):
#    # we expect input angles given by atan2, i.e. in range [-pi, pi)
#
#    # get angles in [0, PI2)    
#    if start_angle < 0:
#        start_angle += PI2
#    if end_angle < 0:
#        end_angle += PI2
#
#    # sweep is defined by two absolute angles
#    sweep_angle = end_angle - start_angle
#    
#    # if angles given are equal, we say that ccw is large sweep
#    if sweep_angle == 0: 
#        if ccw:
#            return PI2
#        else:
#            return 0
#    # turning ccw or cw
#    if not ccw:
#        sweep_angle *= -1
#    # needed :: seems not ??
#    sweep_angle = sweep_angle % PI2 
#    if sweep_angle < 0:
#        sweep_angle += PI2
#
#    return sweep_angle
#
#def test():
#    for i in xrange(-100, 100):
#        try:
#            a = sweep_angle(i/100.0*pi, 0.25*pi, ccw = True)
#            b = sweep_angle(i/100.0*pi, 0.25*pi, ccw = False)
#            assert a + b == PI2
#        except:
#            print "ERR", a, b, ">> %d" % ((a + b) * 10)
#
#    a = sweep_angle(-0.2*pi, 0.2*pi, ccw = True)
#    b = sweep_angle(-0.2*pi, 0.2*pi, ccw = False)
#    
#    print a, b, a + b == PI2
#
#    a = sweep_angle(0.2*pi, -0.2*pi, ccw = True)
#    b = sweep_angle(0.2*pi, -0.2*pi, ccw = False)
#    
#    print a, b, a + b == PI2
#
#    # b = sweep_angle(i/100.0*pi, 0.25*pi, ccw = False)


def vector(end, start):
    """Creates a vector from the start to the end.

    It calculates based on two points: end -(minus) start.
    """
    return tuple(map(sub, end, start))

def normalize(v):
    """Normalizes the length of the vector with 2 elements
    """
    lengthv = hypot(v[0], v[1])
    assert lengthv != 0, "Vector without length cannot be normalized: {0}".format(v)
    return tuple([i/lengthv for i in v])

def perp(v):
    # FIXME: 
    # rename to: rotate90ccw(v)
    # and make: rotate90cw(v)
    # Rotating a vector 90 degrees is particularily simple.
    # (x, y) rotated 90 degrees around (0, 0) is (-y, x).
    # If you want to rotate clockwise, 
    # you simply do it the other way around, getting (y, -x).
    """Rotate 2d vector 90 degrees counter clockwise
    """
    import warnings
    warnings.warn("deprecated")
    return rotate90ccw(v)

def rotate90ccw(v):
    """Rotate 2d vector 90 degrees counter clockwise
    """
    return (-(v[1]), v[0])

def rotate90cw(v):
    """Rotate 2d vector 90 degrees clockwise
    """
    return (v[1], -v[0])

def rotate180(v):
    return vector_mul_scalar(v, -1)

def outward_unit_p1(p0, p1, p2):
    """Gets two normalized (i.e. unit) vectors pointing from
    p1 to p0 and from p1 to p2
    
    Precondition: point p0 != p1 != p2
    """
    u = map(sub, p0, p1)
    v = map(sub, p2, p1)
    # print "u", u
    # print "v", v
    # FIXME: division by zero
    u = normalize(u)
    v = normalize(v)
    return u, v

# def angle(u, v):
#     """
#     u and v are vectors in common point p1 on boundary <p0-p1-p2>
#     when sweeping from u to v, returns angle that is swept when
#     going from p0 to p2, on left side, when looking from above
#     """
#     v1x, v1y, = u[0], u[1]
#     v2x, v2y, = v[0], v[1]
#     r = atan2(v1y, v1x) - atan2(v2y, v2x)
#     # print r
#     while r <= 0:
#         # print r
#         r += 2 * pi
#     return r

def bisector(p0, p1, p2):
    """Scaled bisector so that intersection point from segment p0-p1 and p1-p2
    lies 1 unit away from these segments.

    In case the vertex should have an infinite speed this method raises a
    ValueError.
    """
    # FIXME: 
    # should we do something with points that are collinear 
    # and therefore get 'infinite' speed?
    v = bisector_unit(p0, p1, p2)
    s = scaling_factor(p0, p1, p2)
    if s is None:
        raise ValueError("Infinite speed")
    return vector_mul_scalar(v, s)


def bisector_unit(p0, p1, p2): #1.0):
    """Calculates bisector unit vector that indicates direction of bisector
    (at half angle).

    The bisector that is generated lies on the left when you go from point
    p0 to p1 to p2, while looking from above.
    """
    # get two unit vectors, from p1 to p0 and p1 to p2
    u, v = outward_unit_p1(p0, p1, p2)
    # signed area covered by the points 
    z = orient2d(p0, p1, p2) 
    r = tuple([item * .5 for item in map(add, u, v)])
    bi = None
    # collinear / near collinear
    if r == (0., 0.):
        # r == (0,0) means they cancel out
        # hence vectors are pointing away from each other
        # print "collinear, opposite direction vectors!"
        v = vector(p2, p0)
        return normalize(rotate90ccw(v))
    elif z == 0.:
        # when that does not hold but z == 0 (no area covered)
        # we have vectors pointing in same direction!
        # print "collinear, similar direction vectors!"
        return normalize(vector(p1, p0))
    elif z < 0: 
        # points make turn to right
        bi = -r[0], -r[1]
    # points make turn to left
    elif z > 0: 
        bi = r
    return normalize(bi)


def angle(p0, p1, p2):
    """Returns angle in range [0,2pi> 

    The angle returned is swept when rotating around p1 going from p0 to p2
    (on left side, when looking from above), e.g.

     + p2
      \
       \
      R + p1
        |
        |
        + p0
    """
    u, v = outward_unit_p1(p0, p1, p2)
    r = atan2(u[1], u[0]) - atan2(v[1], v[0])
    while r < 0:
        r += 2 * pi
    return r

def scaling_factor(p0, p1, p2):
    """Give the scaling factor so that we can determine how much we have
    to scale a unit vector to end up at the point in the bisector, so that
    the point is 1 unit away from the segment p0 and p1.
    
    It returns None if the angle between the given points is 0 (folding back)
    """
    alpha = angle(p0, p1, p2) *.5
    if alpha == 0:
        return None
    else:
        return 1. / sin(alpha)

def vector_mul_scalar(v, s):
    """Multiply vector v with a scalar value s
    """
    return tuple([i * s for i in v])

def bisector_vectors(linearring):
    """Returns bisector unit vectors for given linearring
    """
    vecs = {}
    sz = len(linearring) - 1
    for i in range(0, sz):
        # set previous and next
        h = i - 1
        j = i + 1
        # wrap around at beginning and end of ring
        if h < 0:
            h += sz
        if j > sz:
            j = 0
        vecs[i] = bisector(linearring[h], linearring[i], linearring[j])
#    pprint(vecs)
    return vecs


def _test():
    from math import sqrt
    a,b,c = (0,0), (10,-10), (20,0)
    assert scaling_factor(a,b,c) == sqrt(2)
    #
#     print bisector((2,7), (2,3), (0,3))
#     print bisector((0,3), (2,3), (2,7))
#     print bisector((6,10), (5.5, 1), (5,10))

if __name__ == "__main__":
#     _test()
    _test()
#
#u, v = (-1, 1), (-1, -1)
#print degrees(angle(u, v))
#print degrees(angle(v, u))
#
#
#u, v = (-1, 1), (1, 1)
#print degrees(angle(u, v))
#print degrees(angle(v, u))
#
#
#p0 = (0, 1)
#p1 = (1, 0)
#p2 = (3, 2)
#
#print outward_unit_p1(p0, p1, p2)
#
#print bisector(p0, p1, p2)
#print bisector(p2, p1, p0)
#
##print bisector((0,0), (10,0), (20,0))
#print bisector((0, 0), (10, 0), (20,0))
#print bisector((20, 0), (10, 0), (0,0))
#
#print bisector((0,0), (10,0), (1, 0))
#
#
#poly = [(0.,0.), (10.,0.), #(12.5, 3.), (13, 6.3333), 
#        (15.,5.), (10.,10.), (0.,10.),]
#
#orig = open('/tmp/orig.wkt', 'w')
#new = open('/tmp/new.wkt', 'w')
#ring = open('/tmp/ring.wkt', 'w')
#
#orig.write("#wkt\n")
#new.write("#wkt\n")
#ring.write("#wkt\n")
#
#def do_poly(linearring, L = 5):
#    P = linearring[:]
#    P.extend(linearring[0:2])
#    vecs = []
#    for i in range(1, len(P)-1):
#        h = i - 1
#        j = i + 1
#        vecs.append(([P[h], P[i], P[j]], bisector(P[h], P[i], P[j])))
#        print >> orig, "POINT({0[0]} {0[1]})".format(P[i])
#    pprint(vecs)
#    line = [map(add, vecs[-1][0][1], vecs[-1][1])]
#    for pts, bi, in vecs:
#        #print pts[1], bi
#        print >> new, "POINT({0[0]} {0[1]})".format(map(add, pts[1], bi))
#        line.append(map(add, pts[1], bi))
#    print >> ring, "LINESTRING({})".format(", ".join(["{0[0]} {0[1]}".format(pt) for pt in line]))
#    if L > 0:
#        L -= 1
#        return do_poly(line[:-1], L)
#do_poly(poly, 15)
##b = do_poly(a)
##c = do_poly(b)
##d = do_poly(c)
##e = do_poly(d)
