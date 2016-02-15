import logging
import numpy
import bisect

from operator import sub, add
from tri.delaunay import cw, ccw
from tri.delaunay import Edge

from grassfire.primitives import Event
from grassfire.calc import rotate90ccw, near_zero, get_unique_times, normalize
from grassfire.calc import dot, vector_mul_scalar, length
from grassfire.primitives import InfiniteVertex
from grassfire.inout import output_vertices_at_T, output_triangles_at_T, output_edges_at_T

# ------------------------------------------------------------------------------
# solve

def find_gt(a, x):
    """Find leftmost value greater than x"""
    # -- filter None values
    a = filter(lambda x: x is not None, a)
    # -- filter values that are really close to x 
    # (even if value is slightly greater)
    a = filter(lambda v: not near_zero(v-x), a)
    # -- sort the list
    L = sorted(a)
    # -- find leftmost value greater than x, if it is there
    i = bisect.bisect_right(L, x)
    if i != len(a):
        return L[i]
    else:
        return None

def find_gte(a, x):
    """Find leftmost item greater than or equal to x"""
    # -- filter None values and sort
    L = sorted(filter(lambda x: x is not None, a))
    i = bisect.bisect_left(L, x)
    if i != len(L):
        return L[i]
    else:
        return None

def vertex_crash_time(org, dst, apx):
    """Returns time when vertex crashes on edge

    This method assumes that velocity of wavefront is unit speed (1!)

    input:
    org, dst: vertices incident with wavefront edge
    apx: vertex opposite of wavefront edge
    """
    Mv = tuple(map(sub, apx.origin, org.origin))
#     # if the two vertices are the same, the vector is undetermined!!!
#     # for terminal vertices this may be a problem! -> 
#     # the vector is known though (it is perpendicular to the original segment in this case!)
    logging.debug("Vector Mv: " + str(Mv))
    if org.origin == dst.origin:
        # wavefront does not have length:
        # we assume the two velocity vectors are perpendicular
        # as this then should be a 1-terminal vertex
        assert dot(org.velocity, dst.velocity) == 0
        # we add them and we normalize to get a unit vector
        n = normalize(map(add, org.velocity, dst.velocity))
    else:
        # get vector m from begin to end of wavefront
        m = map(sub, dst.origin, org.origin)
        # normalize m
        m = normalize(m)
        # take perpendicular vector to get normal to wavefront
        # that points in direction where wavefront is moving to
        n = rotate90ccw(m)

    # output wavefront normal for visualization
#     halfpt = vector_mul_scalar(map(add, org.origin, dst.origin), 0.5)
#     endpt = map(add, halfpt, n)
#     with open("/tmp/wavefront_normal.wkt", "w") as fh:
#         fh.write("wkt\n")
#         l = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(halfpt, endpt)
#         fh.write(l + "\n")

    logging.debug("Vector n: " + str(n))
    # Normalize, to get unit vector
#     nn = norm(n)
#     logging.debug("Vector nn (normalized n): " + str(nn))
    # project Mv onto normalized unit vector pointing outwards of wavefront edge
    # this gives distance from vertex to wavefront edge
    dist_v_e = dot(Mv, normalize(n))
    logging.debug("Distance wavefront -- vertex: " + str(dist_v_e))
    # Speed vector of vertex v: s
    s = apx.velocity
    # Unit vector of wavefront edge in opposite direction
    n_ = vector_mul_scalar(normalize(n), -1.0)
    # Length of projection of s onto nn
    s_proj = dot(s, n_)
    logging.debug("Per time unit v travels " + str(s_proj))
    logging.debug("Per time unit e travels " + str(length(n)))
    # The distance between is travelled by each vertex that each move
    # this amount of units per time tick
    denom = s_proj + length(n)
    if not near_zero(denom):
        # It takes this amount of time units to crash
        t_v = dist_v_e / denom
        return t_v
    else:
        return None


def area_collapse_times(o, d, a):
    coeff = area_collapse_time_coeff(o, d, a)
    logging.debug(coeff)
    solution = solve_quadratic(coeff[0], coeff[1], coeff[2])
    logging.debug("numpy solve: " + str(numpy.roots(coeff)))
    # solution = filter(lambda x: x != None, solution)
    solution.sort()
    # http://stackoverflow.com/questions/28081247/print-real-roots-only-in-numpy
    logging.debug("area collapse times: " + str(solution))
    return solution


def compute_event_0triangle(tri, now, sieve):
    # a 0-triangle can:
    # - flip
    # - collapse to a segment?
    # - collapse to a point? -- see circle

    # A triangle that is bounded only by spokes can either collapse
    # due to a flip event, that is, a vertex can sweep across its 
    # opposing spoke, or because one of its spokes collapses to zero length.
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
    # where the vanishing spoke was indeed an edge of the wavefront.
    assert tri.neighbours.count(None) == 0
    o, d, a = tri.vertices
    times_edge_collapse = [
        collapse_time_edge(o, d),
        collapse_time_edge(d, a),
        collapse_time_edge(a, o)
        ]
    logging.debug("times edge collapse {}".format(times_edge_collapse))

    dists = [o.distance2_at(d, times_edge_collapse[0]), 
             d.distance2_at(a, times_edge_collapse[1]), 
             a.distance2_at(o, times_edge_collapse[2])]
    logging.debug("dists {}".format(dists))
    indices = []
    for i, _ in enumerate(dists):
        if near_zero(_):
            indices.append(i)
    t_e_c = []
    for i in indices:
        t_e_c.append(times_edge_collapse[i])
    logging.debug("t e c {}".format(t_e_c))
    time_edge_collapse = sieve(t_e_c, now)
    time_area_collapse = sieve(area_collapse_times(o, d, a), now)
    logging.debug(">> time_edge_collapse: {}".format(time_edge_collapse))
    logging.debug(">> time_area_collapse: {}".format(time_area_collapse))
    
    if time_edge_collapse is None and time_area_collapse is None:
        # if we do not have a time for either, no collapse will happen
        return None
    elif time_edge_collapse is not None and time_area_collapse is not None:
        if near_zero(abs(time_area_collapse- time_edge_collapse)):
            logging.debug("area == edge")
            time = time_edge_collapse
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            zeros = [near_zero(_) for _ in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 3:
                return Event(when=time, tri=tri, side = (0, 1, 2), tp="edge", tri_tp=tri.type)
            elif sides_collapse == 1:
                side = zeros.index(True)
                return Event(when=time, tri=tri, side = (side,), tp="edge", tri_tp=tri.type)
            else:
                return None
        elif time_area_collapse < time_edge_collapse:
            logging.debug("area < edge")
            #
            time = time_area_collapse
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            largest_dist = max(dists)
            side = dists.index(largest_dist)
            tp = "flip"
            return Event(when=time, tri=tri, side=(side,), tp=tp, tri_tp=tri.type)
        elif time_edge_collapse != None:
            logging.debug("edge collapse")
            time = time_edge_collapse
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            zeros = [near_zero(_) for _ in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 3:
                return Event(when=time, tri=tri, side = (0, 1, 2), tp="edge", tri_tp=tri.type)
            elif sides_collapse == 1:
                side = zeros.index(True)
                return Event(when=time, tri=tri, side = (side,), tp="edge", tri_tp=tri.type)
            else:
                return None
#                 largest_dist = max(dists)
#                 side = dists.index(largest_dist)
#                 return Event(when=time, tri=tri, side = (side,), tp="flip", tri_tp=tri.type)
#                 raise ValueError("0 triangle with 2 or 0 side collapse, while edge collapse time computed?")

    else:
        # FIXME: much duplication here with above
        if time_edge_collapse != None:
            time = time_edge_collapse
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            zeros = [near_zero(_) for _ in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 3:
                return Event(when=time, tri=tri, side = (0, 1, 2), tp="edge", tri_tp=tri.type)
            elif sides_collapse == 1:
                side = zeros.index(True)
                return Event(when=time, tri=tri, side = (side,), tp="edge", tri_tp=tri.type)
            else:
#                 return None
                print repr(tri)
                logging.debug("TRIANGLE NOT OK: {}".format(id(tri)))
                return None
                raise ValueError("0 triangle with 2 or 0 side collapse, while edge collapse time computed?")
        elif time_area_collapse != None:
            time = time_area_collapse
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            largest_dist = max(dists)
            side = dists.index(largest_dist)
            tp = "flip"
            return Event(when=time, tri=tri, side=(side,), tp=tp, tri_tp=tri.type)
        else:
            raise ValueError("problem!!!")

def compute_event_1triangle(tri, now, sieve):
    # a 1-triangle can:
    # - collapse to a point
    # - collapse to a segment
    # - flip
    # - split its wavefront in two pieces

    # Collapses for triangles with exactly one wavefront edge e appear
    # in one of two forms:
    # 1. The wavefront edge can collapse, causing a classic edge
    # event.
    # 2. Consider the vertex v which lies opposite the wavefront
    # edge e. This vertex can crash into e or sweep across its
    # supporting line.
    #
    # In order to determine which of these two cases happens, we
    # compute both the edge collapse time te of e, as well as the ver-
    # tex crash time tv of v, using two of the procedures previously
    # discussed. As always, we ignore collapse times in the past.
    # If te is earlier than tv or if te equals tv , then this event is an edge
    # event, as e collapses at that time. If tv happens strictly earlier
    # than te, then this event is either a split event or a flip event. In
    # order to classify this event, we compute the length of all sides
    # of the triangle at time tv . If the longest edge is the wavefront
    # edge, it is a split event, otherwise it is a flip event.
    assert tri.neighbours.count(None) == 1
    wavefront_side = tri.neighbours.index(None)
    # ow, dw are the vertices incident with the wavefront
    # aw is vertex opposite of the wavefront
    o, d, a = tri.vertices
    ow, dw, aw = [tri.vertices[ccw(wavefront_side)],
                    tri.vertices[cw(wavefront_side)],
                    tri.vertices[wavefront_side]]
    # what are the times the triangle collapses
    logging.debug("time area collapse " + str(solve_quadratic(*area_collapse_time_coeff(*tri.vertices))))
    # edge collapse times
    time_edge_collapse = sieve([collapse_time_edge(ow, dw)], now)
    logging.debug([collapse_time_edge(ow, dw), 
                   collapse_time_edge(dw, aw), 
                   collapse_time_edge(aw, ow)])
    # vertex crash time of the opposite vertex into the wavefront edge
    time_vertex_crash = sieve([vertex_crash_time(ow, dw, aw)], now)
    logging.debug("time edge collapse " + str(time_edge_collapse))
    logging.debug("time vertex crash " + str(time_vertex_crash))
    if time_edge_collapse is None and time_vertex_crash is None:
        # -- No edge collapse time and no vertex crash time
        return None
    elif time_edge_collapse is None and time_vertex_crash is not None:
        # -- Only vertex crash time
        # check if longest edge is wavefront edge, then we are sure that 
        # we hit the wavefront edge
        # otherwise a spoke (connected to the approaching vertex)
        #  is longer at time of impact, 
        # so we do not hit the wavefront
        # also if we have two sides having same length we hit exactly the point
        # of the segment
        # NOTE, this logic might be numerically unstable (because depends on 
        # length calculations... 
        time = time_vertex_crash
        dists = [d.distance2_at(a, time), 
                 a.distance2_at(o, time),
                 o.distance2_at(d, time)]
        unique_dists = [near_zero(_ - max(dists)) for _ in dists]
        logging.debug(unique_dists)
        unique_max_dists = unique_dists.count(True)
        logging.debug("uniq max dists (needs to be 1 for split) -- " + str(unique_max_dists))
        logging.debug("wavefront side -- " + str(wavefront_side))
        logging.debug("longest side -- " + str(dists.index(max(dists))))
        longest = []
        for i, _ in enumerate(dists):
            if near_zero(_ - max(dists)):
                longest.append(i)
        if wavefront_side in longest and len(longest) == 1:
            return Event(when=time_vertex_crash,
                         tri=tri,
                         side=(wavefront_side,),
                         tp="split",
                         tri_tp=tri.type)
        else:
            zeros = [near_zero(_) for _ in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 1:
                sides = (dists.index(min(dists)),) # shortest side
                return Event(when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
            else:
                sides = (dists.index(max(dists)),) # longest side
                return Event(when=time, tri=tri, side=sides, tp="flip", tri_tp=tri.type)
    elif time_edge_collapse is not None and time_vertex_crash is None:
        # -- Only edge collapse time
        return Event(when=time_edge_collapse,
                         tri=tri,
                         side=(wavefront_side,),
                         tp="edge",
                         tri_tp=tri.type)
    elif time_edge_collapse is not None and time_vertex_crash is not None:
        # -- Both edge collapse time and vertex crash time
        if time_edge_collapse < time_vertex_crash or \
            time_edge_collapse == time_vertex_crash:
            logging.debug("edge collapse time earlier than vertex crash or equal")
            # wavefront edge collapses, because edge collapse time is earlier
            # or equal to vertex crash time
            time = time_edge_collapse
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            tp = "edge"
            zeros = [near_zero(dist) for dist in dists]
            sides = [zeros.index(True)]
            assert len(sides) == 1
            return Event(when=time, tri=tri, side=sides, tp=tp, tri_tp=tri.type)
        elif time_vertex_crash < time_edge_collapse:
            # wavefront edge is split
            logging.debug("vertex crash time earlier than time edge collapse")
            # can be either split or flip
            # take longest side, if that side is wavefront -> split
            time = time_vertex_crash
            dists = [d.distance2_at(a, time), 
                     a.distance2_at(o, time), 
                     o.distance2_at(d, time)]
            max_dist = max(dists)
            max_dist_side = dists.index(max_dist)
            if tri.neighbours[max_dist_side] == None:
                tp = "split"
            else:
                tp = "flip"
            sides = [max_dist_side]
            return Event(when=time, tri=tri, side=sides, tp=tp, tri_tp=tri.type)
        else:
            raise NotImplementedError("Problem, unforeseen configuration")
    raise NotImplementedError("Problem, unforeseen configuration")


def compute_event_2triangle(tri, now, sieve):
    # a 2-triangle can:
    # - collapse to a point
    # - collapse to a segment

    # A triangle with exactly two wavefront edges can collapse in two
    # distinct ways. Either exactly one of the two wavefront edges
    # collapses to zero length or all three of its sides collapse at the
    # same time.
    # To find the collapse times of these triangles, we use the earlier
    # of the two edge collapse times of the wavefront edges, ignoring
    # any times in the past.
    assert tri.neighbours.count(None) == 2
    o, d, a = tri.vertices
    times = []
    # edge collapse times
    # only for wavefront edges (not for spokes)
    if tri.neighbours[2] == None:
        time = collapse_time_edge(o, d)
        times.append(time)
    if tri.neighbours[0] == None:
        time = collapse_time_edge(d, a)
        times.append(time)
    if tri.neighbours[1] == None:
        time = collapse_time_edge(a, o)
        times.append(time)
    times = get_unique_times(times)
    time = sieve(times, now)
    if time != None:
        dists = [d.distance2_at(a, time), 
                 a.distance2_at(o, time), 
                 o.distance2_at(d, time)]
        logging.debug("distances at time = {1}: {0}".format(dists, time))
        zeros = [near_zero(dist) for dist in dists]
        logging.debug("near_zero = {}".format(zeros))
        sides_collapse = zeros.count(True)
        if sides_collapse == 3:
#             for side, _ in enumerate(tri.neighbours):
#                 if _ is not None:
#                     break
            sides = tuple(range(3)) # (side,) # take the side that is not None (has a neighbour)
            return Event(when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
        elif sides_collapse == 2:
            # hopefully never happens -- 
            # or some weird robustness error did occur
            raise ValueError("This is not possible with this type of triangle") 
        elif sides_collapse == 1:
            smallest_dist = min(dists)
            side = dists.index(smallest_dist)
            sides = (side,)
            return Event(when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
        elif sides_collapse == 0:
            return None
            #raise ValueError("This is not possible with this type of triangle") 
    else:
        # -- Triangle does not collapse
        return None


def compute_event_3triangle(tri, now, sieve):
    # a 3-triangle can:
    # - collapse to a point

    # Calculate 3 edge collapse times
    # These should all be similar
    assert tri.neighbours.count(None) == 3
    o, d, a = tri.vertices
    times = []
    time = collapse_time_edge(o, d)
    times.append(time)
    time = collapse_time_edge(d, a)
    times.append(time)
    time = collapse_time_edge(a, o)
    times.append(time)
    # 
    time = sieve(get_unique_times(times), now)
    # we should find at most 1 collapse time
#     assert len(times) <= 1, times
    # we take this event only when it is >= now (now or in the future)
    if time:
        #time = find_gte(times, now) # can raise ValueError if no value found
        sides = tuple(range(3))
#         pa = o.position_at(time)
#         pb = d.position_at(time)
#         pc = a.position_at(time)
#         dists = [d.distance2_at(a, time), 
#                  a.distance2_at(o, time), 
#                  o.distance2_at(d, time)]
# #         assert all_close(dists, abs_tol=1e-8)
#         avg = []
#         for i in range(2):
#             avg.append(sum(map(lambda x: x[i], (pa, pb, pc))) / 3.)
        return Event(when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
    else:
        return None

def compute_event_inftriangle(tri, now, sieve):
    for inf_idx, v in enumerate(tri.vertices):
        if isinstance(v, InfiniteVertex):
            break
    side = inf_idx
    logging.debug(repr(tri))
    logging.debug("side " + str(side))
    o, d, a = tri.vertices[cw(side)], tri.vertices[ccw(side)], tri.vertices[side]

#     print cw(side), "cw | o", repr(o)
#     print ccw(side), "ccw | d", repr(d)
#     print side, repr(a)
    logging.debug(o)
    logging.debug(d)
    if tri.neighbours[side] is None: # wavefront edge
        assert tri.type == 1
        # time of closest approach of the 2 points
        time = find_gt([collapse_time_edge(o, d)], now)
        logging.debug("time of closest approach {}".format(time))
        if time: 
            dist = o.distance2_at(d, time)
            from math import sqrt
            logging.debug(dist)
            if near_zero(dist):
                # collapsing edge!
                return Event(when=time, tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            else:
                raise ValueError('problem?')
#                 tp = "edge"
#                 return Event(when=time, tri=tri, side=(side,), tp=tp)
    time = sieve(area_collapse_times(o, d, a), now)
    # if time != None and not near_zero(time - now):
    if time:
        dist = o.distance2_at(d, time)
        if near_zero(dist):
            return Event(when=time, tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            # non-wavefront edge collapses
#             return Event(when=time, tri=tri, side=(side,), tp="edge")
        else:
            tp = "flip"
            # FIXME: side to flip depends on which side to rotate to
            # The flip of infinite triangle leads to finite and infinite triangle
            # The result should be that the finite triangle has a good orientation
            # which results in the triangle laying outside of the already swept domain
            # o->d = side
            # d->a = cw(side)
            # a->o = ccw(side)
#             print Edge(tri, cw(side)).segment
#             print Edge(tri, ccw(side)).segment

            # I think you need to flip away the shortest side of the two edges
            # that both are connected to the infinite vertex
            return None
            return Event(when=time, tri=tri, side=(None,), tp=tp, tri_tp=tri.type)

    return None
#     return NewEventType(
#             when=time, 
#             tri=tri, 
#             sides=sides, 
#             event_tp=tp, # collapse / flip / split 
#             how=how, # if collapse: point | line
#             where=where # if collapse: the geometry of point or segment
#         )

def compute_collapse_time(tri, now=0, sieve=find_gte):
    event = None
    if tri.stops_at is not None:
        # we have a triangle that has been stopped already, return None
        return event
    if tri.is_finite:
        logging.debug("=-=-= finite triangle {} =-=-= ".format(id(tri)))
        logging.debug(repr(tri))
        # finite triangles
        tp = tri.type
        if tp == 0:
            logging.debug("event for 0-triangle")
            event = compute_event_0triangle(tri, now, sieve)
        elif tp == 1:
            logging.debug("event for 1-triangle")
            event = compute_event_1triangle(tri, now, sieve)
        elif tp == 2:
            logging.debug("event for 2-triangle")
            event = compute_event_2triangle(tri, now, sieve)
        elif tp == 3:
            logging.debug("event for 3-triangle")
            event = compute_event_3triangle(tri, now, sieve)
    else:
        # flip or collapse to point
        logging.debug("=-=-= infinite triangle {} =-=-=".format(id(tri)))
        event = compute_event_inftriangle(tri, now, sieve)
    if event is not None:
        tri.event = event
    logging.debug("{} --- {}".format(id(tri), event))
    return event

def compute_collapse_time_at_T(tri, time):
    """Compute event for triangle that collapse at time
    Somehow we know that the triangle collapse at this moment
    """
    o, d, a = tri.vertices
    dists = [d.distance2_at(a, time), 
             a.distance2_at(o, time), 
             o.distance2_at(d, time)]
    logging.debug("distances at time = {1}: {0}".format(dists, time))
    zeros = [near_zero(dist) for dist in dists]
    sides = []
    for i, zero in enumerate(zeros):
        if zero == True:
            sides.append(i)
    return Event(when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)

def collapse_time_edge(v1, v2):
    """Returns the time when the given 2 kinetic vertices are closest to each
    other
 
    If the 2 vertices belong to a wavefront edge there are 3 options:
    - they cross each other in the past
    - they cross each other in the future
    - they run parallel, so they never meet
    Note, the distance between the two points is a linear function.
 
    If the 2 vertices do not belong to a wavefront edge,
    the distance between the two points can be a quadratic or linear function 
    - they cross each other in the past
    - they cross each other in the future
    - they run in parallel, so they never cross
    - they never cross, but there exists a point in time when they are closest
    """
#     logging.debug("edge collapse time for v1 = {} and v2 = {}".format(id(v1), id(v2)))
    s1 = v1.velocity
    s2 = v2.velocity
    o1 = v1.origin
    o2 = v2.origin
    dv = map(sub, s1, s2)
    denominator = dot(dv, dv)
#     logging.debug("denominator for edge collapse time {}".format(denominator))
    if not near_zero(denominator):
        w0 = map(sub, o2, o1)
        nominator = dot(dv, w0)
#         logging.debug("nominator for edge collapse time {}".format(nominator))
        collapse_time = nominator / denominator
#         logging.debug("edge collapse time: "+ str(collapse_time))
        return collapse_time
    else:
        logging.debug("denominator (close to) 0")
        logging.debug("these two vertices move in parallel:")
        logging.debug(str(v1) + "|" + str(v2))
        logging.debug("edge collapse time: None (near) parallel movement")
        # any time will do
        return -1.


def solve_quadratic(A, B, C):
    """Get the roots for quadratic equation, defined by A, B and C

    The quadratic equation A*x^2 + B*x + C = 0 can be 
    described with its companion matrix M, where

    M = [[a b], [c d]] == [[0 -C/A], [1 -B/A]]

    The roots that we want to find are the eigenvalues L1, L2 
    of this 2x2 matrix.

    L1 = 0.5*T + (0.25*T^2 - D)^0.5
    L2 = 0.5*T - (0.25*T^2 - D)^0.5

    with:

    T = a + d
    D = a*d - b*c

    Note, if A == 0 and B != 0 gives the answer for B*x + C = 0
    """
    if near_zero(A) and not near_zero(B):
        # A near zero, not a quadratic => 
        # we solve a linear equation:
        # B*x + C = 0
        # B*x = -C
        # x = -C / B
        return [-C/B]
    elif near_zero(A) and near_zero(B):
        # No solution, line parallel to the x-axis, not crossing the x-axis
        # raise NotImplementedError("Not done yet")
        return []
    T = -B / A  # a + d
    D = C / A   # a*d - b*c
    centre = T * 0.5
    under = 0.25 * pow(T, 2) - D
    if under < 0:
        # -- imaginary roots
        return []
    elif near_zero(under):
        # -- one root
        return [centre]
    else:
        # return L1, L2 (the eigen values of M)
        plus_min = pow(under, 0.5)
        return [centre - plus_min, centre + plus_min]


def area_collapse_time_coeff(kva, kvb, kvc):
    """Returns coefficients of quadratic in t
    """
    # points and velocity vectors
    pa, shifta = kva.origin, kva.velocity
    pb, shiftb = kvb.origin, kvb.velocity
    pc, shiftc = kvc.origin, kvc.velocity
    # for each point, original x- and y-coordinates
    xaorig, yaorig = pa[0], pa[1]
    xborig, yborig = pb[0], pb[1]
    xcorig, ycorig = pc[0], pc[1]
    # for each point, magnitude in each direction
    dxa, dya = shifta[0], shifta[1]
    dxb, dyb = shiftb[0], shiftb[1]
    dxc, dyc = shiftc[0], shiftc[1]
    # The area of the triangle with 3 moving vertices is function of time t
    # (i.e. calculate determinant based on position of the 3 vertices at time t):
    #
    # area(t) = .5 *(xaorig + dxa *t) *(yborig + dyb *t) - 0.5 *(xborig + dxb *t) *(yaorig + dya *t)  + 0.5 *(xborig + dxb *t) *(ycorig + dyc *t)  - 0.5 *(xcorig + dxc *t) *(yborig + dyb *t) + 0.5 *(xcorig + dxc *t)* (yaorig + dya *t) - 0.5 *(xaorig + dxa *t)* (ycorig + dyc *t)
    #
    # Take partial derivative with respect to t -- this leads to quadratic function in t:
    #        C                           B               B                               A
    #  0.5 * xaorig * yborig + 0.5 * xaorig * dyb * t + 0.5 * dxa * t * yborig + 0.5 * dxa * pow(t,2) * dyb \
    #- 0.5 * xborig * yaorig - 0.5 * xborig * dya * t - 0.5 * dxb * t * yaorig - 0.5 * dxb * pow(t,2) * dya \
    #+ 0.5 * xborig * ycorig + 0.5 * xborig * dyc * t + 0.5 * dxb * t * ycorig + 0.5 * dxb * pow(t,2) * dyc \
    #- 0.5 * xcorig * yborig - 0.5 * xcorig * dyb * t - 0.5 * dxc * t * yborig - 0.5 * dxc * pow(t,2) * dyb \
    #+ 0.5 * xcorig * yaorig + 0.5 * xcorig * dya * t + 0.5 * dxc * t * yaorig + 0.5 * dxc * pow(t,2) * dya \
    #- 0.5 * xaorig * ycorig - 0.5 * xaorig * dyc * t - 0.5 * dxa * t * ycorig - 0.5 * dxa * pow(t,2) * dyc
    # for solving we can factor out all 0.5*'s
    A = \
        dxa * dyb - dxb * dya + dxb * dyc - \
        dxc * dyb + dxc * dya - dxa * dyc
    B = xaorig * dyb - xborig * dya + \
        xborig * dyc - xcorig * dyb + \
        xcorig * dya - xaorig * dyc + \
        dxa * yborig - dxb * yaorig + \
        dxb * ycorig - dxc * yborig + \
        dxc * yaorig - dxa * ycorig
    C = xaorig * yborig - xborig * yaorig + \
        xborig * ycorig - xcorig * yborig + \
        xcorig * yaorig - xaorig * ycorig
    ret = (A, B, C)
    logging.debug("coefficients {0}".format(ret))
    return ret


def visualize_collapse(tri, T=0):
    with open("/tmp/bisectors.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt\n")
        for kvertex in tri.vertices:
            p1 = kvertex.position_at(T)
            bi = kvertex.velocity
            bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(p1, map(add, p1, bi)))

    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles_at_T([tri], T, fh)

    with open("/tmp/kvertices.wkt", "w") as fh:
        output_vertices_at_T(tri.vertices, T, fh)

    with open("/tmp/wavefront.wkt", "w") as fh:
        edges = []
        for i, n in enumerate(tri.neighbours):
            if n is None:
                edges.append(Edge(tri, i))
        output_edges_at_T(edges, T, fh)

    with open("/tmp/rays.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt\n")
        for kvertex in tri.vertices:
            p1 = kvertex.origin
            bi = kvertex.velocity
            bineg = vector_mul_scalar(bi, -10000.0)
            bipos = vector_mul_scalar(bi, 10000.0)
            bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(map(add, p1, bipos), 
                                                                                  map(add, p1, bineg)))

def test_compute_collapse_times():
    from grassfire.primitives import KineticTriangle, KineticVertex

    cases = [
    # infinite 0-triangle
    (0,
    KineticTriangle(InfiniteVertex((2., 4.)), 
                    KineticVertex((2., 0.), (-0.5, -0.5)), 
                    KineticVertex((1., 1.), (0.5, 0.)), True, True, True),
    #(1.211102550928, "flip")
    None
    ),

    # infinite 0-triangle
    (0,
    KineticTriangle(InfiniteVertex((1., 4.)), 
                    KineticVertex((2., 0.), (-0.5, -0.5)), 
                    KineticVertex((0., 0.), (0.5, -0.5)), True, True, True),
    (2.0, "edge")
    #None
    ),

    # infinite 0-triangle
    (0, 
    KineticTriangle(InfiniteVertex((2., 4.)), 
                    KineticVertex((4., 0.), (0.5, -0.5)), 
                    KineticVertex((0., 0.), (-0.5, -0.5)), True, True, True),
    None),

    # infinite 1-triangle
    (0, 
    KineticTriangle(InfiniteVertex((1., 4.)), 
                    KineticVertex((2., 0.), (-0.5, -0.5)), 
                    KineticVertex((0., 0.), (0.5, -0.5)), None, True, True),
    (2.0, "edge")
    ),

    # finite 1-triangle
    # miss edge
    (0, 
    KineticTriangle(KineticVertex((2., 4.), (0., -0.5)),
                    KineticVertex((0., 0.), (0., +1)), 
                    KineticVertex((2., 0.), (0., +1)),  None, True, True),
    (2.666666666667, "edge")),


    # finite 1-triangle
    (0, 
    KineticTriangle(KineticVertex((1., 4.), (0., -0.5)),  
                    KineticVertex((0., 0.), (0., 1.)), 
                    KineticVertex((2., 0.), (0., 1.)),None, True, True),
    ( 2.666666666667, "split")),

    # finite 1-triangle
    # rot-0
    (0, 
    KineticTriangle(KineticVertex((1., 4.), (0., -0.5)), 
                    KineticVertex((0., 0.), (0., +1.0)), 
                    KineticVertex((2., 0.), (0., +1.0)), 
                    None, True, True),
    (2.666666666666666666, "split")),

    # finite 1-triangle -- wavefront edge collapses
    (0, 
    KineticTriangle(KineticVertex((1., 4.), (0., -0.5)),
                    KineticVertex((0., 0.), (0.5, .5)),
                    KineticVertex((2., 0.), (-.5, .5)),
                    None, True, True),
    (2., "edge")),

    # finite 1-triangle -- apex misses the wavefront
    (0, 
    KineticTriangle(KineticVertex((3., 4.), (0., -0.5)), 
                    KineticVertex((0., 0.), (0., +1.0)), 
                    KineticVertex((2., 0.), (0., +1.0)), 
                    None, True, True),
    ( 2.666666666667, "flip")),

    # finite 1 triangle that should split
    # we miss the event 
    (0,
     KineticTriangle(KineticVertex((11.1, 0.0), (-0.41421356237309614, 1.0)), KineticVertex((14.0, 10.0), (-0.41434397951188867, -1.0828510849683515)), KineticVertex((-33.307692307692705, 2.115384615384554), (9.300198345114286, 0.536239302469343)), None, True, True),
     (4.569105324086005, "split")),

    # 3-triangle
    (0, 
    KineticTriangle(KineticVertex((0., 0.), (0.5, 0.5)), 
                    KineticVertex((2., 0.), (-0.5, 0.5)), 
                    KineticVertex((1., 1.), (0., -0.5)), 
                    None, None, None), 
    (1.2, "edge")),

    # 2-triangle collapse to point    
    (0,
     KineticTriangle(KineticVertex((11.1, 0.0), (-0.41421356237309614, 1.0)), KineticVertex((9.0, 0.0), (0.024984394500786274, 1.0)), KineticVertex((11.0, -0.1), (-0.39329937395053033, 1.0209141884225659)), None, None, True),
     (4.781443007949, "edge")),

    (0,
     KineticTriangle(KineticVertex((-0.866025403784, 0.5), (0.3660254037831927, -1.3660254037847726)), KineticVertex((-0.866025403784, 0.5), (-1.3660254037847726, -0.3660254037831926)), InfiniteVertex((2.4999999999993334, 1.4433756729733331)), True, True, None),
     #None
     (0, "edge")
     ),

    (0,
     KineticTriangle(KineticVertex((3.36602540378, 4.83012701892), (-1.366025403784519, 0.366025403784139)), KineticVertex((1.63397459622, 4.83012701892), (1.3660254037847726, 0.366025403783193)), KineticVertex((5.86602540378, 0.5), (-0.366025403784139, -1.3660254037845188)), True, None, True),
     (0.6339745962123428, "edge")),

    (0,
     KineticTriangle(KineticVertex((-0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -0.5467572438521933)), KineticVertex((6.123233995736766e-17, 1.0), (-2.3811458388420067e-16, -1.7693436082961256)), KineticVertex((-1.6180339887498947, 1.1755705045849465), (0.18250881904109725, 1.4023874396799996)), True, None, True),
     (0.56518134482820892, "edge")),

    (0,
     KineticTriangle(KineticVertex((-0.2, -0.06666666666666667), (1.8695058979924137, 0.04448684017361237)), KineticVertex((0.3333333333333333, -0.6), (-0.4142135623730951, 1.0)), KineticVertex((0.3333333333333333, 0.6), (-0.2506607793572, -1.0800962240008098)), True, True, True),
     (0.241024119, "flip")),

    (0,
     KineticTriangle(KineticVertex((-0.9872805569585875, 0.12537065799230004), (-1.024866765183742, -1.1114119702481062)), KineticVertex((-0.8437938978984622, -0.19040991430610052), (21.666935207544306, 44.860914394127434)), KineticVertex((-0.7653348342872799, -0.10537661431275783), (-1.0428319428196307, -0.08857245780155545)), True, True, True),
     (0.00242630813253, "flip")),
    
    (0,
     KineticTriangle(KineticVertex((-0.25, 0.75), (-2.4142135623730945, -0.9999999999999996)), KineticVertex((-0.25, -0.75), (2.4142135623730945, 0.9999999999999996)), KineticVertex((0.25, -0.75), (-2.4142135623730945, 0.9999999999999996)), True, True, True),
     (0.103553390593274, "edge")
     )
    ]
    do_test = True
    if do_test:
        for i, (now, tri, expected) in enumerate(cases, start = 0):
            print
            print "Case", i
            print "=" * 10
            visualize_collapse(tri, now)
            evt = compute_collapse_time(tri, now)
            print evt, expected
            if evt != None:
                if expected == None:
                    assert False, "incorrect None"

                else:
                    time, tp = expected
                    assert near_zero(evt.time - time)
                    assert evt.tp == tp
            else:
                assert evt is expected

    now = 0.
#     now = 4.781443007949
    tri = cases[-1][1]
 
    try:
        evt = compute_collapse_time(tri, now)
        print evt
    except:
        pass
    visualize_collapse(tri, now)
 
#     print solve_quadratic(*area_collapse_time_coeff(*tri.vertices))
#     print solve_quadratic_old(*area_collapse_time_coeff(*tri.vertices))
#     import matplotlib.pyplot as plt
#     areas = []
#     times = range(-30, 20)
#     for t in times:
#         area = orient2d(tri.vertices[0].position_at(t),
#                         tri.vertices[1].position_at(t), 
#                         tri.vertices[2].position_at(t)
#                     )
#         areas.append(area)
# 
#     def distance(p0, p1):
#         return sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)
#     distances = []
#     for t in [t/ 10. for t in times]:
#         distances.append(distance(tri.vertices[0].origin, tri.vertices[1].position_at(t)))
# 
#     plt.plot([t/ 10. for t in times], distances)
#     plt.grid(True)
#     plt.show()
# 
#     
#     if evt != None:
#         t = evt.time
#     else:
#         t = now
#     visualize_collapse(tri, 1.2111)


def test_solve():
    A, B, C = 3.0, 4.5, 9.0
    print solve_quadratic(A, B, C) == []

    A, B, C = 2.0, 0.0, 0.0
    print solve_quadratic(A, B, C) == [0.0]

    A, B, C = 1.0, 3.0, 2.0
    print solve_quadratic(A, B, C) == [-2.0, -1.0]

def main():
    test_compute_collapse_times()
#     test_one_collapse()

def test_one_collapse():
    
    from grassfire.primitives import KineticTriangle, KineticVertex
    # the vertex below should split the triangle in pieces!!!
    # -> we miss this event with our current calculation!!!
    
#     tri = KineticTriangle(KineticVertex((3.36602540378, 4.83012701892), (-1.366025403784519, 0.366025403784139)), KineticVertex((1.63397459622, 4.83012701892), (1.3660254037847726, 0.366025403783193)), KineticVertex((5.86602540378, 0.5), (-0.366025403784139, -1.3660254037845188)), True, None, True)
#     tri = KineticTriangle(KineticVertex((11.1, 0.0), (-0.41421356237309614, 1.0)), KineticVertex((14.0, 10.0), (-0.41434397951188867, -1.0828510849683515)), KineticVertex((-33.307692307692705, 2.115384615384554), (9.300198345114286, 0.536239302469343)), None, True, True)
    #tri = KineticTriangle(KineticVertex((-0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -0.5467572438521933)), KineticVertex((6.123233995736766e-17, 1.0), (-2.3811458388420067e-16, -1.7693436082961256)), KineticVertex((-1.6180339887498947, 1.1755705045849465), (0.18250881904109725, 1.4023874396799996)), True, None, True)
    # tri = KineticTriangle(KineticVertex((-0.587785252292473, 0.8090169943749475), (1.0399940791944127, -1.4314290480002558)), KineticVertex((-0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -0.5467572438521933)), KineticVertex((-0.5877852522924732, -0.8090169943749473), (1.0399940791944131, 1.4314290480002556)), True, True, True)
    
#     tri = KineticTriangle(KineticVertex([3.36092084343274, 4.81953957828363], (0, 0)), KineticVertex((0.0, 0.0), (1.0, 1.0)), KineticVertex((14.0, 10.0), (-0.41434397951188867, -1.0828510849683515)), True, None, None)
    # tri = KineticTriangle(KineticVertex((2.0, 0.5), (2.4142135623730945, -0.9999999999999996)), KineticVertex((1.0, 0.0), (2.4142135623730945, 0.9999999999999996)), KineticVertex((2.0, 0.0), (-2.4142135623730945, 0.9999999999999996)), True, True, True)
    #tri = KineticTriangle(KineticVertex((2.0, 0.5), (2.4142135623730945, -0.9999999999999996)), KineticVertex((1.0, 0.0), (2.4142135623730945, 0.9999999999999996)), KineticVertex((2.0, 0.0), (-2.4142135623730945, 0.9999999999999996)), True, True, True)

    #tri = KineticTriangle(KineticVertex((-0.2, -0.06666666666666667), (1.8695058979924137, 0.04448684017361237)), KineticVertex((0.3333333333333333, -0.6), (-0.4142135623730951, 1.0)), KineticVertex((0.3333333333333333, 0.6), (-0.2506607793572, -1.0800962240008098)), True, True, True)
    #tri = KineticTriangle(KineticVertex((-0.6388129767693403, -0.31936665619917365), (0.8030798568408047, -0.5996411436857993)), KineticVertex((-0.6231441738161808, -0.46672335701255496), (0.7799096015853287, 0.6333147760081715)), KineticVertex((-0.4881354888333025, -0.4609454744153349), (-0.3283637586937928, 0.94926819247684)), True, True, True)

    #tri = KineticTriangle(KineticVertex((-0.9872805569585875, 0.12537065799230004), (-1.024866765183742, -1.1114119702481062)), KineticVertex((-0.8437938978984622, -0.19040991430610052), (21.666935207544306, 44.860914394127434)), KineticVertex((-0.7653348342872799, -0.10537661431275783), (-1.0428319428196307, -0.08857245780155545)), True, True, True)
    
    #tri = KineticTriangle(KineticVertex((141.02031145318313, 15.11765139459854), (-1.09679614706904, 0.8919821935206798)), InfiniteVertex((0.17181892901794138, -0.016845276247151694)), KineticVertex((-0.11765994741487949, 0.576486269356072), (0.892675917072541, 1.09692483546051)), True, None, True)
    #tri = KineticTriangle(KineticVertex((141.02031145318313, 15.11765139459854), (-1.09679614706904, 0.8919821935206798)), InfiniteVertex((0.17181892901794127, -0.016845276247151646)), KineticVertex((-0.11765994741487949, 0.576486269356072), (0.892675917072541, 1.09692483546051)), True, None, True)
    #tri = KineticTriangle(KineticVertex((0.37664329535438995, -0.20429813029318875), (-1.0914440709287114, 0.8995592632828218)), KineticVertex((0.37941863862056496, 0.2502008472118177), (-0.8920557213641949, -1.0976424754293432)), KineticVertex((0.2307551855093853, -0.21963555360760362), (-1.0915314233653777, 0.8995177965775215)), True, True, True)
    
    tri = KineticTriangle(KineticVertex((-0.25, 0.75), (-2.4142135623730945, -0.9999999999999996)), KineticVertex((-0.25, -0.75), (2.4142135623730945, 0.9999999999999996)), KineticVertex((0.25, -0.75), (-2.4142135623730945, 0.9999999999999996)), True, True, True)
    now = 0. #0.6339745962123428
    evt = compute_collapse_time(tri, now)
#     print evt
    times = [0,]# 0.00242630813252781, 0.6340506109731798, 0.004284474881621788, 0.0022096098886525, 0.22933526207436553]
    for time in sorted(times):
        visualize_collapse(tri, time)
#         raw_input("paused at " + str(time))

if __name__ == "__main__":
    # -- logging
    import logging
    import sys
 
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
 
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    # -- main function
    main()
    
    #test_compute_collapse_times()
