from math import copysign, sqrt, hypot
import logging
import numpy

from operator import sub
from tri.delaunay import cw, ccw
from tri.delaunay import orig, dest, apex

from primitives import Event
from grassfire.calc import rotate90ccw, near_zero
from grassfire.calc import is_close, all_close
# ------------------------------------------------------------------------------
# solve

# def is_similar(a, b, eps=1e-12):
#     return abs(b - a) <= eps

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
    L = filter(lambda x: x[0]>=val, L)
    L.sort(key=lambda x: x[0])
    return L

def ignore_lte_and_sort_list(L, val=0):
    """
    L = list of values

    first filters L where the value should be positive
    (note: this also filters None values)

    then sorts L based value
    """
    # FIXME: not sure if filtering 0 values always out is what we want
    # e.g. while doing length comparision, we probably want to keep a length
    # of 0????
    L = filter(lambda x: x>=val, L)
    L.sort()
    return L

def new_compute_collapse(t):
    times = []
    for side in range(3):
        i, j = cw(side), ccw(side)
        v1, v2 = t.vertices[i], t.vertices[j]
        time = collapse_time_edge(v1, v2)
        if time >= 0:
            times.append(time)
        else:
            times.append(None)
    return times

def collapses_to_pt(tri, times):
    a, b, c = tri.vertices
    coeff = area_collapse_time_coeff(a, b, c)
#     print "[quadratic]", solve_quadratic(coeff[0], coeff[1], coeff[2])
    pts = []
    dists = []
    for i, t in enumerate(times):
        if t is not None:
            a, b, c  = tri.vertices[cw(i)], tri.vertices[ccw(i)], tri.vertices[i]
            p0 = a.position_at(t)
            p1 = b.position_at(t)
            p2 = c.position_at(t)
#             if is_close(p0[0], p1[0], abs_tol=1e-5, rel_tol=0) and is_close(p0[1], p1[1], abs_tol=1e-5, rel_tol=0):
#                 pts.append( (p0, p1, p2) )
#             else:
#                 pts.append(None)
            pts.append((p0, p1, p2))
            dists.append( (
                hypot(p1[1] - p0[1], p1[0] - p0[0]),
                hypot(p2[1] - p1[1], p2[0] - p1[0]),
                hypot(p0[1] - p2[1], p0[0] - p2[0]),
            ) )
        else:
            pts.append(None)
    return pts, dists


def vertex_crash_time(org, dst, apx):
    """Returns time when vertex crashes on edge
    """
    #print id(org), id(dst), id(apx)
    Mv = tuple(map(sub, apx.origin, org.origin))
    #print Mv
    #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + Mv[0], org.origin[1] + Mv[1])
    m =  map(sub, dst.origin, org.origin)
    #print m
    m = norm(m) # normalize m
    #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + m[0], org.origin[1] + m[1])
    #print m
    n = rotate90ccw(m) # take perpendicular vector
    #print n
    #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + n[0], org.origin[1] + n[1])
    dist_v_e = dot(Mv, n)
    #print "dist", distance_v_e
    s = apx.velocity
    #print dot(s, n)
    logging.debug("dist_v_e " + str(dist_v_e))
    d_sn = dot(s, n)
    logging.debug("dot(s,n) " + str(d_sn))
    # Problem when d_sn == 1!
    if not is_close(d_sn, 1.0, abs_tol=1e-12, rel_tol=0, method="strong"):
        t_v = dist_v_e / (1.0 - d_sn)
    else:
        t_v = None
    logging.debug("vertex crash time: " + str(t_v))
    return t_v

def area_collapse_times(o,d,a):
    coeff = area_collapse_time_coeff(o, d, a)
    logging.debug(coeff)
    solution = solve_quadratic(coeff[0], coeff[1], coeff[2])
    logging.debug(numpy.roots(coeff))
    solution = filter(lambda x: x != None, solution)
    solution.sort()
    # http://stackoverflow.com/questions/28081247/print-real-roots-only-in-numpy
    logging.debug("area collapse times: " + str(solution))
    return solution

def compute_collapse_time(t, now=0):
    #
    # FIXME:
    # FILTER TIMES IN THE PAST depends on the current time of NOW
    #
    # compute when this triangle collapses
    collapses_at = None 
    collapses_side = None
    collapses_type = None
#     if t.finite:
    # finite triangles
    tp = t.type
    logging.debug("type: {0}".format(tp))
    if tp == 0:
        # ``A triangle that is bounded only by spokes can either collapse
        # due to a flip event, that is, a vertex can sweep across its oppos-
        # ing spoke, or because one of its spokes collapses to zero length.
        # For each edge of a triangle we compute its collapse time, if
        # it exists. We also compute the time when the triangle's area
        # becomes zero using the determinant approach.
        # If the time obtained from the determinant approach is earlier
        # than any edge collapses this triangle will cause a flip event at
        # that time.
        # In the other case two opposing vertices will crash into each
        # other as a spoke collapses. Some authors, such as Huber in
        # [Hub12], define this to be a split event because it involves at
        # least one reflex wavefront vertex. For our purposes we will still
        # call this an edge event since its handling is identical to the case
        # where the vanishing spoke was indeed an edge of the wave-
        # front.'' p. 33
        a, b, c = t.vertices
        coeff = area_collapse_time_coeff(a, b, c)
        times = ignore_lte_and_sort_list(solve_quadratic(coeff[0], coeff[1], coeff[2]))
        roots = numpy.roots(coeff)
        time_det = None
        print roots
        if times:
#             print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
#             print "   roots found by numpy", numpy.roots(coeff)
            print times
            time_det = min(times)
        if time_det != None and time_det < now:
            time_det = None
        times = []
        for side in range(3):
            i, j = cw(side), ccw(side)
            v1, v2 = t.vertices[i], t.vertices[j]
            time = collapse_time_edge(v1, v2)
            if time != None:
                times.append((time, side))
        times = ignore_lte_and_sort(times, now)
        print "all close?", all_close([_[0] for _ in times]), len(times)
#             print "te [edge collapse time]", times
        if times:
            time_edge = times[0][0]
            side = times[0][1]
            print time_edge
#             for v in t.vertices:
#                 print v.position_at(time_edge)
#             if time_det is not None:
#                 for v in t.vertices:
#                     print v.position_at(time_det)
            i, j = cw(side), ccw(side)
            v1, v2 = t.vertices[i], t.vertices[j]
            if (time_det is not None and time_det < time_edge):
#                     print "flip event of zero triangle"
                collapses_at = time_det
                # -> side_at = longest of these edges should flip
                dists = []
                for side in range(3):
                    i, j = cw(side), ccw(side)
                    v1, v2 = t.vertices[i], t.vertices[j]
                    dist = v1.distance2_at(v2, time_det)
                    dists.append( (dist, side) )
                dists.sort(key=lambda x: -x[0])
                collapses_side = dists[0][1]
                collapses_type = "flip"
            elif not near_zero(v1.distance2_at(v2, time_edge)):
                collapses_at = time_edge
                dists = []
                for side in range(3):
                    i, j = cw(side), ccw(side)
                    v1, v2 = t.vertices[i], t.vertices[j]
                    dist = v1.distance2_at(v2, time_edge)
                    dists.append( (dist, side) )
                dists.sort(key=lambda x: -x[0])
                collapses_side = dists[0][1]
                collapses_type = "flip"
            else:
                collapses_at = time_edge
                collapses_side = times[0][1]
                collapses_type = "edge"
#                     print "vertices crashing into each other, handle as edge event @side", collapses_side
    elif tp == 1: # FINISHED
        # 2 cases can happen:
        # a. the wavefront edge can collapse -> edge event
        # b. the vertex v opposite this edge can crash into
        #    this edge, or sweep over its supporting line -> split or flip event 

        side = t.neighbours.index(None)
        org, dst, apx = t.vertices[orig(side)], t.vertices[dest(side)], t.vertices[apex(side)]

        # 
        coeff = area_collapse_time_coeff(org, dst, apx)
#             print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
#             print "   roots found by numpy", numpy.roots(coeff)

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
        n = rotate90ccw(m) # take perpendicular vector
        #print n
        #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + n[0], org.origin[1] + n[1])
        distance_v_e = dot(Mv, n)
        #print "dist", distance_v_e
        s = apx.velocity
        #print dot(s, n)
        t_v = distance_v_e / (1.0 - dot(s, n))
        #print crash_time
#             print "tv [vertex crash time]:", t_v 
        t_e = collapse_time_edge(org, dst)
#             print "te [edge collapse time]", t_e

        logging.debug("tv [vertex crash time]:" + str(t_v))
        logging.debug("te [edge collapse time]:" + str(t_e))

        # given that we ignore negative times we return that there is no
        # event for this triangle...
        if t_e < now and t_v < now:
            # FIXME: if both are None this would also return here...
            return None
        elif (t_v < now) or (t_e >= now and t_e <= t_v): # also true if t_e = None and t_v has a value!
            collapses_at = t_e
            collapses_side = t.neighbours.index(None)
            collapses_type = "edge"
        else:
#                 print "tv strictly earlier than te -> split or flip"
#                 # compute side lengths of triangle at time tv
#                 print "should compute side lengths at time tv"
            lengths = []
            for side in range(3):
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                dist = v1.distance2_at(v2, t_v)
#                     print " dist", side, dist
                lengths.append((dist, side))
            lengths = ignore_lte_and_sort(lengths)
            dist, side = lengths[-1] # take longest is last
#                 print dist, side
            # if longest edge at time t_v is wavefronte edge -> split event
            if side == t.neighbours.index(None):
                collapses_type = "split"
            # otherwise -> flip event
            else:
                collapses_type = "flip"
            collapses_at = t_v
            collapses_side = side # FIXME: is that correct?
        print collapses_at
    elif tp == 2: # FINISHED
        # ``A triangle with exactly two wavefront edges can collapse in two
        # distinct  ways. Either exactly one of the two wavefront edges
        # collapses to zero length or all three of its sides collapse at the
        # same time.''

        # compute with edge collapse time
        # use earliest of the two edge collapse times
        # ignore times in the past
        a, b, c = t.vertices
        coeff = area_collapse_time_coeff(a, b, c)
        logging.debug("td [area zero time] {0}".format(solve_quadratic(coeff[0], coeff[1], coeff[2])))
        logging.debug("roots found by numpy")
        logging.debug(numpy.roots(coeff))
        sides = []
        for i in range(3):
            if t.neighbours[i] is None:
                sides.append(i)
        assert len(sides) == 2
#             print sides
        times = []
        for side in sides:
#         for side in range(3):
            i, j = cw(side), ccw(side)
            v1, v2 = t.vertices[i], t.vertices[j]
            times.append((collapse_time_edge(v1, v2), side))
        # remove times in the past, same as None values
        logging.debug(times)
        times = ignore_lte_and_sort(times, now)
#         print all_close([_[0] for _ in times])
#             print len(times), "->", len(set([xx for xx, _ in times])), "NUMBER OF TIMES"
        logging.debug(times)
        if times:
            time, side = times[0]
            collapses_at = time
            collapses_side = side
            collapses_type = "edge"
#                 print "SIDE", side
            if all_close([_[0] for _ in times]):
                for i, _ in enumerate(t.neighbours):
                    if _ is not None:
                        collapses_side = i
#                         print "MODIFY SIDE TO", collapses_side
                        break
    elif tp == 3:
        # compute with edge collapse time of all three edges
        a, b, c = t.vertices
        coeff = area_collapse_time_coeff(a, b, c)
#             print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
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
#     else:
#         # infinite triangles
# #         print "infinite triangle found"
#         pass

    if collapses_at is not None:
        assert collapses_side is not None
        assert collapses_type is not None

        # HACK
        assert collapses_at >= now, "{0} {1}".format(collapses_at, now)
#         if collapses_at < now:
#             collapses_at = now
        # /HACK

        if collapses_type == "flip" and t.type == 2:
            assert False, "Problem: flipping 2 triangle not allowed" 
        e = Event(when=collapses_at, 
                     tri=t, 
                     side=collapses_side, 
                     tp=collapses_type)
        t.event = e # weakref.ref(e)
        return e
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

# def collapse_time_edge(tri, side):
#     i, j = cw(side), ccw(side)
#     v1, v2 = tri.vertices[i], tri.vertices[j]
#     time = closest_time_of_approach(v1, v2)
#     dist = v1.distance2_at(v2, time)
#     if near_zero(dist):
#         return time
#     else:
#         return None
# 
# def closest_time_of_approach(v1, v2):

def collapse_time_edge(v1, v2):
    """Returns the time when the given 2 kinetic vertices are closest to each
    other

    If the 2 vertices belong to a wavefront edge there are 3 options:
    - they cross each other in the past
    - they cross each other in the future
    - they run parallel, so they never meet
    The distance between the two points is a linear function.

    If the 2 vertices do not belong to a wavefront edge,
    the distance between the two points can be a quadratic or linear function 
    - they cross each other in the past
    - they cross each other in the future
    - they run in parallel, so they never cross
    - they never cross, but there exists a point in time when they are closest
    """
    s1 = v1.velocity
    s2 = v2.velocity
    o2 = v2.origin
    o1 = v1.origin
    dv = map(sub, s1, s2)
    denominator = dot(dv, dv)
    if not near_zero(denominator):
        w0 = map(sub, o2, o1)
        nominator = dot(dv, w0)
        collapse_time = nominator / denominator
        logging.debug("edge collapse time: "+ str(collapse_time))
        return collapse_time
    else:
        logging.debug("denominator (close to) 0")
        logging.debug("these two vertices move in parallel:")
        logging.debug(str(v1) + "|" + str(v2))
        logging.debug("edge collapse time: None (near) parallel movement")
        # any time will do
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
    logging.info("quadratic solved" + str(solve_quadratic(a, b, c)))


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
        return [x1, x2]
    else:
        q = -0.5 * (b + sign(b) * D**0.5)
        # print >> sys.stderr, "q =", q
        # prevent division by zero if a == 0 or q == 0
        if a != 0: x1 = q / a
        if q != 0: x2 = c / q
        return list(sorted((x1,x2)))
        #return list(sorted(filter(lambda x: x is not None, (x1, x2))))


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
