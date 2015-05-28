from math import copysign, sqrt
import numpy

from operator import sub
from tri.delaunay import cw, ccw
from tri.delaunay import orig, dest, apex

from primitives import Event
from grassfire.calc import perp

# ------------------------------------------------------------------------------
# solve

def ignore_lte_and_sort(L, val=0):
    """
    L = list of 2-tuples, e.g (time, side) or (length, side)
    
    first filters L where the first element should be positive value
    (note: this also filters None values)

    then sorts L based on first element of tuple
    """
    
    # FIXME: not sure if filtering 0 values always out is what we want
    # e.g. while doing length comparision, we probably want to keep a length
    # of 0????
    L = filter(lambda x: x[0]>val, L)
    L.sort(key=lambda x: x[0])
    return L

def compute_collapse_time(t, now=0):
    #
    # FIXME:
    # FILTER TIMES IN THE PAST depends on the current time of NOW
    #
    # compute when this triangle collapses
    collapses_at = None 
    collapses_side = None
    collapses_type = None
    if t.finite:
        # finite triangles
        tp = t.type
        print "TYPE", tp
        if tp == 0:
            a, b, c = t.vertices
            coeff = area_collapse_time_coeff(a, b, c)
            times = list(solve_quadratic(coeff[0], coeff[1], coeff[2]))
            times = filter(lambda x: x>0, times)
            time_det = min(times)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            print "   roots found by numpy", numpy.roots(coeff)
            print times
            times = []
            for side in range(3):
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                times.append((collapse_time_edge(v1, v2), side))
            times = filter(lambda x: x[0]>0, times)
            times.sort(key=lambda x: x[0])
            print "te [edge collapse time]", times
            if times:
                time_edge = times[0][0]
                if time_det < time_edge:
                    print "flip event of zero triangle"
                    collapses_at = time_det
                    # -> side_at = longest of these edges should flip
                    for side in range(3):
                        i, j = cw(side), ccw(side)
                        v1, v2 = t.vertices[i], t.vertices[j]
                        print "dist", side, v1.distance2(v2)
                else:
                    collapses_at = time_edge
                    collapses_side = times[0][1]
                    collapses_type = "edge"
                    print "vertices crashing into each other, handle as edge event @side", collapses_side
        elif tp == 1: # FINISHED
            # 2 cases can happen:
            # a. the wavefront edge can collapse -> edge event
            # b. the vertex v opposite this edge can crash into
            #    this edge, or sweep over its supporting line -> split or flip event 

            side = t.neighbours.index(None)
            org, dst, apx = t.vertices[orig(side)], t.vertices[dest(side)], t.vertices[apex(side)]

            # 
            coeff = area_collapse_time_coeff(org, dst, apx)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            print "   roots found by numpy", numpy.roots(coeff)

            # 
            #print id(org), id(dst), id(apx)
            Mv = tuple(map(sub, apx.origin, org.origin))
            #print Mv
            #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + Mv[0], org.origin[1] + Mv[1])
            m =  map(sub, dst.origin, org.origin)
            #print m
            m = norm(m) # normalize m
            #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + m[0], org.origin[1] + m[1])
            #print m
            n = perp(m) # take perpendicular vector
            #print n
            #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + n[0], org.origin[1] + n[1])
            distance_v_e = dot(Mv, n)
            #print "dist", distance_v_e
            s = apx.velocity
            #print dot(s, n)
            t_v = distance_v_e / (1 - dot(s, n))
            #print crash_time
            print "tv [vertex crash time]:", t_v 

            t_e = collapse_time_edge(org, dst)
            print "te [edge collapse time]", t_e
            # given that we ignore negative times!!!
            if t_e <= t_v:
                collapses_at = t_e
                collapses_side = t.neighbours.index(None)
                collapses_type = "edge"
            else:
                print "tv strictly earlier than te -> split or flip"
                # compute side lengths of triangle at time tv
                print "should compute side lengths at time tv"
                lengths = []
                for side in range(3):
                    i, j = cw(side), ccw(side)
                    v1, v2 = t.vertices[i], t.vertices[j]
                    dist = v1.distance2_at(v2, t_v)
                    print " dist", side, dist
                    lengths.append((dist, side))
                lengths = ignore_lte_and_sort(lengths)
                dist, side = lengths[-1] # take longest is last
                print dist, side
                # if longest edge at time t_v is wavefronte edge -> split event
                if side == t.neighbours.index(None):
                    collapses_type = "split"
                # otherwise -> flip event
                else:
                    collapses_type = "flip"
                collapses_at = t_v
                collapses_side = side # FIXME: is that correct?
        elif tp == 2: # FINISHED
            # compute with edge collapse time
            # use earliest of the two edge collapse times
            # ignore times in the past
            a, b, c = t.vertices
            coeff = area_collapse_time_coeff(a, b, c)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            print "   roots found by numpy", numpy.roots(coeff)
            sides = []
            for i in range(3):
                if t.neighbours[i] is None:
                    sides.append(i)
            assert len(sides) == 2
            print sides
            times = []
            for side in sides:
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                times.append((collapse_time_edge(v1, v2), side))
            # remove times in the past, same as None values
            times = ignore_lte_and_sort(times, now)
            if times:
                time, side = times[0]
                collapses_at = time
                collapses_side = side
                collapses_type = "edge"
                print "SIDE", side
#             times = filter(lambda x: x>0, times)
#             print times
#             print set(times)
#             if times:
#                 time = min(times)
#                 if time >= 0:
#                     collapses_at = time
        elif tp == 3:
            # compute with edge collapse time of all three edges
            a, b, c = t.vertices
            coeff = area_collapse_time_coeff(a, b, c)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            times = []
            for side in range(3):
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                times.append((collapse_time_edge(v1, v2), side))
            # remove times in the past, same as None values
            times = ignore_lte_and_sort(times, now)
            if times:
                collapses_at = times[0][0]
                collapses_side = times[0][1]
                collapses_type = "edge"
    else:
        # infinite triangles
        print "infinite triangle found"

    if collapses_at is not None:
        return Event(when=collapses_at, 
                     tri=t, 
                     side=collapses_side, 
                     tp=collapses_type)
    else:
        return None

def quadratic(x, a, b, c):
    """Returns y = a * x^2 + b * x + c for given x and a, b, c
    """
    a, b, c, x = float(a), float(b), float(c), float(x)
    return a * x**2 + b * x + c

def dot(v1, v2):
    return sum(p*q for p,q in zip(v1, v2))

def norm(v):
    L = sqrt(sum( [x**2 for x in v] ) )
    return tuple([x/L for x in v])

def collapse_time_edge(v1, v2):
    """Given 2 kinetic vertices compute the time when they will collide
    """
    s1 = v1.velocity
    s2 = v2.velocity
    o2 = v2.origin
    o1 = v1.origin
    denominator = dot(map(sub, s1, s2), map(sub, s1, s2))
    if denominator != 0.:
        nominator = dot(map(sub, s1, s2), map(sub, o2, o1))
        collapse_time = nominator / denominator
        return collapse_time
        # when positive, this is a correct collapse time
        # when negative, the vertices are now moving apart from each other
        # when denominator is 0, they move in parallel
    else:
        print "denominator 0"
        print "these two vertices move in parallel:",
        print v1, "|", v2
        return None

def collapse_time_dot(tri):
    """calculate whether an edge length becomes zero
    """
    for i in range(3):
        j = (i + 1) % 3
        v1, v2 = tri.vertices[i], tri.vertices[j]
        collapse_time_edge(v1, v2)

def collapse_time_quadratic(ktri):
    """Calculate collapse time of kinetic triangle by determinant method
    (when does area become 0.0 size)
    """
    # described in section 4.3.1
    v1, v2, v3 = ktri.vertices[0], ktri.vertices[1], ktri.vertices[2]

    # speeds
    s1 = v1.velocity
    s2 = v2.velocity
    s3 = v3.velocity
    s1x, s1y = s1[0], s1[1]
    s2x, s2y = s2[0], s2[1]
    s3x, s3y = s3[0], s3[1]

    # origins
    o1 = v1.origin
    o2 = v2.origin
    o3 = v3.origin
    o1x, o1y = o1[0], o1[1]
    o2x, o2y = o2[0], o2[1]
    o3x, o3y = o3[0], o3[1]

    # terms
    a = \
       -s1y*s2x + s1x*s2y + s1y*s3x - \
        s2y*s3x - s1x*s3y + s2x*s3y
    b = \
        o2y*s1x - o3y*s1x - o2x*s1y + \
        o3x*s1y - o1y*s2x + o3y*s2x + \
        o1x*s2y - o3x*s2y + o1y*s3x - \
        o2y*s3x - o1x*s3y + o2x*s3y
    c = \
       -o1y*o2x + o1x*o2y + o1y*o3x - \
        o2y*o3x - o1x*o3y + o2x*o3y
    print "quadratic solved", solve_quadratic(a, b, c)


def sign(x):
    """Sign function
    """
    if x == 0:
        return 0
    else:
        return copysign(1, x)


def discriminant(a, b, c):
    """Calculate discriminant
    """
    D = b**2 - 4.0*a*c
    # print >> sys.stderr, "D =", D
    return D


def solve_quadratic(a, b, c):
    """Solve quadratic equation, defined by a, b and c
    
    Solves  where y = 0.0 for y = a * x^2 + b * x + c, if a, b and c are given
    
    Returns tuple with two elements
    The result is a:
    (None, None) if imaginary solution
    (None, float) or (float, None) if only one root
    (float, float) if two roots (roots wil    print >> sys.stderr, "a =", a, ", b =", b, ", c =", cl be sorted from small to big)
    """
    x1, x2 = None, None

    a, b, c = float(a), float(b), float(c)
    D = discriminant(a, b, c)
#    print >> sys.stderr, "a =", a, ", b =", b, ", c =", c, "D =", D
    #if near(D, 0):
    #    print >> sys.stderr, "making D 0"
    #    D = 0

    # if discriminant == 0 -> only 1 solution, instead of two

    if D < 0:
        return (x1, x2)
    else:
        q = -0.5 * (b + sign(b) * D**0.5)
        # print >> sys.stderr, "q =", q
        # prevent division by zero if a == 0 or q == 0
        if a != 0: x1 = q / a
        if q != 0: x2 = c / q
        return list(sorted((x1, x2)))


def area_collapse_time_coeff(kva, kvb, kvc):
    """Returns coefficients of quadratic in t
    """
    pa = kva.origin
    shifta = kva.velocity
    pb = kvb.origin
    shiftb = kvb.velocity
    pc = kvc.origin
    shiftc = kvc.velocity
    xaorig, yaorig = pa[0], pa[1]
    xborig, yborig = pb[0], pb[1]
    xcorig, ycorig = pc[0], pc[1]
    dxa, dya = shifta[0], shifta[1]
    dxb, dyb = shiftb[0], shiftb[1]
    dxc, dyc = shiftc[0], shiftc[1]
#    area = .5 *(xaorig + dxa *t) *(yborig + dyb *t) - 0.5 *(xborig + dxb *t) *(yaorig + dya *t)  + 0.5 *(xborig + dxb *t) *(ycorig + dyc *t)  - 0.5 *(xcorig + dxc *t) *(yborig + dyb *t) + 0.5 *(xcorig + dxc *t)* (yaorig + dya *t) - 0.5 *(xaorig + dxa *t)* (ycorig + dyc *t)
#        C                           B               B                               A
#  0.5 * xaorig * yborig + 0.5 * xaorig * dyb * t + 0.5 * dxa * t * yborig + 0.5 * dxa * pow(t,2) * dyb \
#- 0.5 * xborig * yaorig - 0.5 * xborig * dya * t - 0.5 * dxb * t * yaorig - 0.5 * dxb * pow(t,2) * dya \
#+ 0.5 * xborig * ycorig + 0.5 * xborig * dyc * t + 0.5 * dxb * t * ycorig + 0.5 * dxb * pow(t,2) * dyc \
#- 0.5 * xcorig * yborig - 0.5 * xcorig * dyb * t - 0.5 * dxc * t * yborig - 0.5 * dxc * pow(t,2) * dyb \
#+ 0.5 * xcorig * yaorig + 0.5 * xcorig * dya * t + 0.5 * dxc * t * yaorig + 0.5 * dxc * pow(t,2) * dya \
#- 0.5 * xaorig * ycorig - 0.5 * xaorig * dyc * t - 0.5 * dxa * t * ycorig - 0.5 * dxa * pow(t,2) * dyc

    A = dxa * dyb - \
        dxb * dya + \
        dxb * dyc - \
        dxc * dyb + \
        dxc * dya - \
        dxa * dyc

    B = xaorig * dyb - \
        xborig * dya + \
        xborig * dyc - \
        xcorig * dyb + \
        xcorig * dya - \
        xaorig * dyc + \
        dxa * yborig - \
        dxb * yaorig + \
        dxb * ycorig - \
        dxc * yborig + \
        dxc * yaorig - \
        dxa * ycorig

    C = xaorig * yborig - \
        xborig * yaorig + \
        xborig * ycorig - \
        xcorig * yborig + \
        xcorig * yaorig - \
        xaorig * ycorig
#    print "coefficients", A, B, C
    return tuple(map(lambda x: x*0.5, [A, B, C]))

