from math import copysign, sqrt, hypot
import logging
import numpy
import bisect

from operator import sub, add
from tri.delaunay import cw, ccw, orient2d
from tri.delaunay import orig, dest, apex
from tri.delaunay import Edge

from primitives import Event
from grassfire.calc import rotate90ccw, near_zero, get_unique_times
from grassfire.calc import is_close, all_close, vector_mul_scalar
from grassfire.primitives import InfiniteVertex
from grassfire.inout import output_vertices_at_T, output_triangles_at_T, output_edges_at_T

# ------------------------------------------------------------------------------
# solve

# def is_similar(a, b, eps=1e-12):
#     return abs(b - a) <= eps

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
    L = filter(lambda x: not x[0] <= val, L)
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
    L = filter(lambda x: not x <= val, L)
    L.sort()
    return L


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
        n = norm(map(add, org.velocity, dst.velocity))
    else:
        # get vector m from begin to end of wavefront
        m = map(sub, dst.origin, org.origin)
        # normalize m
        m = norm(m)
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
    dist_v_e = dot(Mv, norm(n))
    logging.debug("Distance wavefront -- vertex: " + str(dist_v_e))
    # Speed vector of vertex v: s
    s = apx.velocity
    # Unit vector of wavefront edge in opposite direction
    n_ = vector_mul_scalar(norm(n), -1.0)
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
    # front.
    assert tri.neighbours.count(None) == 0
    o, d, a = tri.vertices
    times_edge_collapse = [
        collapse_time_edge(o, d),
        collapse_time_edge(d, a),
        collapse_time_edge(a, o)
        ]
    time_edge_collapse = sieve(times_edge_collapse, now)
    time_area_collapse = sieve(area_collapse_times(o, d, a), now)
    if time_edge_collapse is None and time_area_collapse is None:
        # if we do not have a time for either, no collapse will happen
        return None
    elif time_edge_collapse is not None and time_area_collapse is not None:
        if time_area_collapse < time_edge_collapse:
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
            return None
#             time = time_edge_collapse
#             tp = "edge"
#             dists = [d.distance2_at(a, time), a.distance2_at(o, time), o.distance2_at(d, time)]
#             zeros = [near_zero(dist) for dist in dists]
#             sides_collapse = zeros.count(True)
#             if sides_collapse == 3:
#                 sides = tuple(range(3))
#                 return Event(when=time, tri=tri, side=sides, tp=tp)
#             elif sides_collapse == 2:
#                 # hopefully never happens -- 
#                 # or some weird robustness error did occur
#                 raise ValueError("This is not possible with a triangle")
#             elif sides_collapse == 1:
#                 smallest_dist = min(dists)
#                 sides = (dists.index(smallest_dist),)
#                 return Event(when=time, tri=tri, side=sides, tp=tp)
#             elif sides_collapse == 0:
#                 print "now", now
#                 print "t_e", time_edge_collapse
#                 print "t_a", time_area_collapse
#                 raise ValueError("This is not possible -- time_area_collapse should be smaller")
    else:
        if time_edge_collapse != None:
            return None
#             time = time_edge_collapse
#             tp = "edge"
#             dists = [d.distance2_at(a, time), a.distance2_at(o, time), o.distance2_at(d, time)]
#             zeros = [near_zero(dist) for dist in dists]
#             sides_collapse = zeros.count(True)
#             if sides_collapse == 3:
#                 sides = tuple(range(3))
#                 return Event(when=time, tri=tri, side=sides, tp=tp)
#             elif sides_collapse == 2:
#                 # hopefully never happens -- 
#                 # or some weird robustness error did occur
#                 raise ValueError("This is not possible with a triangle")
#             elif sides_collapse == 1:
#                 smallest_dist = min(dists)
#                 sides = (dists.index(smallest_dist),)
#                 return Event(when=time, tri=tri, side=sides, tp=tp)
#             elif sides_collapse == 0:
#                 print "now", now
#                 print "t_e", time_edge_collapse
#                 print "t_a", time_area_collapse
#                 raise ValueError("This is not possible -- time_area_collapse should be smaller")
        else:
            raise NotImplementedError("time_area_collapse not None, while time edge collapse is None")
#     if time != None:
#         dists = [d.distance2_at(a, time), a.distance2_at(o, time), o.distance2_at(d, time)]
#         zeros = [near_zero(dist) for dist in dists]
#         sides_collapse = zeros.count(True)
#         if sides_collapse == 3:
#             pa, pb, pc = (o.position_at(time), d.position_at(time), a.position_at(time))
#             avg = []
#             for i in range(2):
#                 avg.append(sum(map(lambda x: x[i], (pa, pb, pc))) / 3.)
#             tp = "collapse"
#             how = "point"
#             where = tuple(avg)
#             sides = tuple(range(3))
#             return Event(when=time, tri=tri, side=sides, tp="edge")
#         elif sides_collapse == 2:
#             # hopefully never happens -- 
#             # or some weird robustness error did occur
#             raise ValueError("This is not possible with a triangle") 
#         elif sides_collapse == 1:
#             smallest_dist = min(dists)
#             side = dists.index(smallest_dist)
#             tp = "collapse"
#             how = "line"
#             where = None
#             end = tri.vertices[side].position_at(time)
#             pts = tri.vertices[cw(side)].position_at(time), tri.vertices[ccw(side)].position_at(time)
#             start = []
#             for i in range(2):
#                 start.append(sum(map(lambda x: x[i], pts)) * .5)
#             where = (tuple(start), end)
#             sides = (side,)
#             return Event(when=time, tri=tri, side=sides, tp="edge")
#         elif sides_collapse == 0:
#             # no side collapsing? then points get closest as they can
#             # should flip the triangle
#             largest_dist = max(dists)
#             side = dists.index(largest_dist)
#             tp = "flip"
#             how = "--"
#             where = None
#             sides = (side,)
#             return Event(when=time, tri=tri, side=sides, tp="flip")
#     else:
#         sides = tuple()
#         tp = "--"
#         how = "--"
#         where = None
#         return None
#     return NewEventType(
#                     when=time, 
#                     tri=tri, 
#                     sides=sides, 
#                     event_tp=tp, # collapse / flip / split 
#                     how=how, # if collapse: point | line
#                     where=where # if collapse: the geometry of point or segment
#                 )

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
        sides_collapse = zeros.count(True)
        if sides_collapse == 3:
            for side, _ in enumerate(tri.neighbours):
                if _ is not None:
                    break
            sides = (side,) # take the side that is not None (has a neighbour)
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
            raise ValueError("This is not possible with this type of triangle") 
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
        pa = o.position_at(time)
        pb = d.position_at(time)
        pc = a.position_at(time)
        dists = [d.distance2_at(a, time), 
                 a.distance2_at(o, time), 
                 o.distance2_at(d, time)]
#         assert all_close(dists, abs_tol=1e-8)
        avg = []
        for i in range(2):
            avg.append(sum(map(lambda x: x[i], (pa, pb, pc))) / 3.)
        tp = "collapse"
        how = "point"
        where = tuple(avg)
        return Event(when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
    else:
        time = None
        sides = tuple()
        tp = "--"
        how = "--"
        where = None
        return None
#     return NewEventType(
#                     when=time, 
#                     tri=tri, 
#                     sides=sides, 
#                     event_tp=tp, # collapse / flip / split 
#                     how=how, # if collapse: point | line
#                     where=where # if collapse: the geometry of point or segment
#                 )

def compute_event_inftriangle(tri, now, sieve):
    # FIXME: negative collapse times are probably the times we are after 
    # here as the orientation of the triangle is in reverse as well
    for inf_idx, v in enumerate(tri.vertices):
        if isinstance(v, InfiniteVertex):
            break
    side = inf_idx
    logging.debug(tri.str_at(0))
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
        if time: 
            dist = o.distance2_at(d, time)
            if near_zero(dist):
                # collapsing edge!
                return None
#                 tp = "edge"
#                 return Event(when=time, tri=tri, side=(side,), tp=tp)
    time = sieve(area_collapse_times(o, d, a), now)
    # if time != None and not near_zero(time - now):
    if time:
        dist = o.distance2_at(d, time)
        if near_zero(dist):
            return None
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
    if tri.is_finite:
        logging.debug("=-=-= finite triangle {} =-=-= ".format(id(tri)))
        logging.debug(repr(tri))
        # finite triangles
        tp = tri.type
        if tp == 0:
            event = compute_event_0triangle(tri, now, sieve)
        elif tp == 1:
            event = compute_event_1triangle(tri, now, sieve)
        elif tp == 2:
            event = compute_event_2triangle(tri, now, sieve)
        elif tp == 3:
            event = compute_event_3triangle(tri, now, sieve)
    else:
        # flip or collapse to point
        logging.debug("=-=-= infinite triangle {} =-=-=".format(id(tri)))
        event = compute_event_inftriangle(tri, now, sieve)
    if event is not None:
        tri.event = event
    logging.debug("{} --- {}".format(id(tri), event))
    return event

def compute_collapse_time_old(t, now=0):
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
    #assert t.is_finite
    tp = t.type
    #logging.debug("type: {0}".format(tp))
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
        # where the vanishing spoke was indeed an edge of the wavefront.'' p. 33
        a, b, c = t.vertices
        coeff = area_collapse_time_coeff(a, b, c)
        times = ignore_lte_and_sort_list(solve_quadratic(coeff[0], coeff[1], coeff[2]))
        roots = numpy.roots(coeff)
        time_det = None
        if times:
#             print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
#             print "   roots found by numpy", numpy.roots(coeff)
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
        #print "all close?", all_close([_[0] for _ in times]), len(times)
#             print "te [edge collapse time]", times
        if times:
            time_edge = times[0][0]
            side = times[0][1]
#             for v in t.vertices:
#                 print v.position_at(time_edge)
#             if time_det is not None:
#                 for v in t.vertices:
#                     print v.position_at(time_det)
            i, j = cw(side), ccw(side)
            v1, v2 = t.vertices[i], t.vertices[j]
            # FIXME:
            # *Infinite* triangles should flip, so that an interior triangle
            # that starts to exist lies outside the area swept already
            # I have the suspicion that this means that infinite triangles 
            # should flip with their shortest edge, instead of the longest
            # The shortest edge here being the edge to the gravi-center of the 
            # graph
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
                # FIXME: branch shares much code with first
                # merge first branch with this one?
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
    elif tp == 1: # FINISHED
        # 2 cases can happen:
        # a. the wavefront edge can collapse -> edge event
        # b. the vertex v opposite this edge can crash into
        #    this edge, or sweep over its supporting line -> split or flip event 

        side = t.neighbours.index(None)
        org, dst, apx = t.vertices[orig(side)], t.vertices[dest(side)], t.vertices[apex(side)]

        t_e = collapse_time_edge(org, dst)
        logging.debug("te [edge collapse time]:" + str(t_e))
        # 
#         coeff = area_collapse_time_coeff(org, dst, apx)
#             print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
#             print "   roots found by numpy", numpy.roots(coeff)
        if dst.origin == org.origin: 
            # if the two vertices of this triangle are at same location
            # normalizing goes wrong 
            t_v = None
        else:
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
            dsn = dot(s, n)
            if dsn != 1.:
                t_v = distance_v_e / (1.0 - dsn)
            else:
                t_v = None
        #print crash_time
#             print "tv [vertex crash time]:", t_v 
        
#             print "te [edge collapse time]", t_e

        logging.debug("tv [vertex crash time]:" + str(t_v))
        

        # given that we ignore negative times we return that there is no
        # event for this triangle...

        # None < 0 == True
        if t_e <= now and t_v <= now:
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
            # if longest edge at time t_v is wavefront edge -> split event
            if side == t.neighbours.index(None):
                collapses_type = "split"
            # otherwise -> flip event
            else:
                collapses_type = "flip"
            collapses_at = t_v
            collapses_side = side # FIXME: is that correct?
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
                     side=[collapses_side], 
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

def length(v):
    return sqrt(sum( [x**2 for x in v] ) )

def norm(v):
    L = length(v)
    if L != 0:
        return tuple([x/L for x in v])
    else:
        return tuple([x for x in v])

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
    Note, the distance between the two points is a linear function.

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


def solve_quadratic_old(a, b, c):
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
        # A near zero, not a quadratic, but a linear equation to solve
        #         B*x + C = 0
        #         B*x = -C
        #         x = -C / B
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
        dxa * dyb - \
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
    #ret = tuple(map(lambda x: x*0.5, [A, B, C]))
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
            print bi
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
    (1.211102550928, "flip")),

    # infinite 0-triangle
    (0,
    KineticTriangle(InfiniteVertex((1., 4.)), 
                    KineticVertex((2., 0.), (-0.5, -0.5)), 
                    KineticVertex((0., 0.), (0.5, -0.5)), True, True, True),
    #(2.0, "edge")
    None
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
    #(2.0, "edge")
    None
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
     None),

    (0,
     KineticTriangle(KineticVertex((3.36602540378, 4.83012701892), (-1.366025403784519, 0.366025403784139)), KineticVertex((1.63397459622, 4.83012701892), (1.3660254037847726, 0.366025403783193)), KineticVertex((5.86602540378, 0.5), (-0.366025403784139, -1.3660254037845188)), True, None, True),
     (0.6339745962123428, "edge")),

    (0,
     KineticTriangle(KineticVertex((-0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -0.5467572438521933)), KineticVertex((6.123233995736766e-17, 1.0), (-2.3811458388420067e-16, -1.7693436082961256)), KineticVertex((-1.6180339887498947, 1.1755705045849465), (0.18250881904109725, 1.4023874396799996)), True, None, True),
     (0.56518134482820892, "edge")),

    ]
    do_test = True
    if do_test:
        for i, (now, tri, expected) in enumerate(cases, start = 0):
            print
            print "Case", i
            print "=" * 10
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
    tri = KineticTriangle(KineticVertex((-0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -0.5467572438521933)), KineticVertex((6.123233995736766e-17, 1.0), (-2.3811458388420067e-16, -1.7693436082961256)), KineticVertex((-1.6180339887498947, 1.1755705045849465), (0.18250881904109725, 1.4023874396799996)), True, None, True)
    # tri = KineticTriangle(KineticVertex((-0.587785252292473, 0.8090169943749475), (1.0399940791944127, -1.4314290480002558)), KineticVertex((-0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -0.5467572438521933)), KineticVertex((-0.5877852522924732, -0.8090169943749473), (1.0399940791944131, 1.4314290480002556)), True, True, True)
    now = 0. #0.6339745962123428
    evt = compute_collapse_time(tri, now)
    print evt
#     for time in sorted((4.17717264811, 4.56137104038, 4.569105324086005, 4.57086735787, 4.869780863249584)):
    visualize_collapse(tri, 0.)
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
