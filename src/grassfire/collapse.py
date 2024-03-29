import logging
# import numpy
import bisect
import math

# from operator import sub, add
from tri.delaunay.tds import cw, ccw, Edge

###from geompreds import orient2d
###from grassfire.vectorops import norm, cross, dot, make_vector, unit, rotate90ccw, add, div

from grassfire.primitives import Event
from grassfire.calc import near_zero, get_unique_times
from grassfire.primitives import InfiniteVertex
from grassfire.inout import output_vertices_at_T, output_triangles_at_T, \
    output_edges_at_T
from grassfire.vectorops import dot, mul, add, sub, norm


# ------------------------------------------------------------------------------
# solve


def find_gt(a, x):
    """Find value greater than x, ignores None values"""
    # -- filter None values
    a = [x for x in a if x is not None]
    # -- filter values that are really close to x
    # (even if value is slightly greater)
    a = [v for v in a if not near_zero(v - x)]
    # -- sort the list
    L = sorted(a)
    # -- find leftmost value greater than x, if it is there
    i = bisect.bisect_right(L, x)
    if i != len(a):
        return L[i]
    else:
        return None


def find_gte(a, x):
    """Find greater than or equal to x, ignores None values"""
    logging.debug("gte a: {} ; x: {}".format(a,x))
    # -- filter None values and sort
    L = sorted([x for x in a if x is not None])
    i = bisect.bisect_left(L, x)
    if i != len(L):
        return L[i]
    else:
        return None


def vertex_crash_time(org, dst, apx):
    """Returns time when vertex crashes on edge

    This method assumes that velocity of wavefront is unit speed

    Input:
        org, dst: kinetic vertices incident with wavefront edge
        apx: kinetic vertex opposite of wavefront edge
    """
    Mv = tuple(sub(apx.origin, org.origin))
    logging.debug("Vector Mv: " + str(Mv))
    assert org.ur is not None
    assert org.ur == dst.ul, "#{} #{} :: {} vs {}".format(id(org), id(dst), org.ur, dst.ul)


    #logging.error("DISTANCE {}".format(org.ur.signed_distance(apx.position_at(0))))

#    print(org.ur)
#    print(dst.ul)
#    assert org.ur.w == dst.ul.w
#    n = org.ur.w[:]
    n = tuple(org.ur.w) # was: org.ur

    logging.debug("Vector n: " + str(n))
    # Normalize, to get unit vector
    s = apx.velocity
    logging.debug("Vector s: " + str(s))
    # Project Mv onto normalized unit vector pointing outwards of wavefront
    # edge this gives distance from vertex to wavefront edge
    dist_v_e = dot(Mv, n)
    logging.debug("Distance wavefront -- vertex: " + str(dist_v_e))
    # Speed vector of vertex v: s
    s_proj = dot(s, n)
    logging.debug(
        "Per time unit v travels (1 - s_proj := combined speed of approach) " +
        str(s_proj) +
        " " +
        str(1.0 - s_proj))
    logging.debug("Per time unit e travels " + str(norm(n)))
    # The distance between is traveled by each vertex that each move
    # this amount of units per time tick
    denom = 1.0 - s_proj
    #logging.error("DENOMINATOR {}".format(denom))
    if not near_zero(denom):
        # It takes this amount of time units to crash
        t_v = dist_v_e / denom
        #logging.error("DISTANCE t_v {}".format(org.ur.signed_distance(apx.position_at(t_v))))
        return t_v
    else:
        return None


def area_collapse_times(o, d, a):
    coeff = area_collapse_time_coeff(o, d, a)
    logging.debug(coeff)
    solution = solve_quadratic(coeff[0], coeff[1], coeff[2])
    # logging.debug("numpy solve: " + str(["{:.60f}".format(_) for _ in numpy.roots(coeff)]))
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

    times_area_collapse = area_collapse_times(o, d, a)
    for time in times_area_collapse:
        # as we are degenerate now, flip it, or if a spoke collapses handle as edge collapse
        if near_zero(abs(time-now)):
            dists = [d.distance2_at(a, now),
                     a.distance2_at(o, now),
                     o.distance2_at(d, now)]

            indices = []
            for i, _ in enumerate([math.sqrt(_) for _ in dists]):
                if near_zero(_):
                    indices.append(i)
            if len(indices) == 1:
                # spoke collapse, leading to split of wavefront
                # we handle this as an edge collapse (the neighbour is not None, we will schedule_immediately this neighbour)
                side = indices[0]
                tp = "edge"
                return Event(when=now, tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            elif len(indices) == 3:
                raise ValueError('0-triangle collapsing to point')
            else:
                largest_dist = max(dists)
                side = dists.index(largest_dist)
                return Event(when=now, tri=tri, side=(side,), tp="flip", tri_tp=tri.type)

    times_edge_collapse = [
        collapse_time_edge(o, d),
        collapse_time_edge(d, a),
        collapse_time_edge(a, o)
    ]
    logging.debug("times edge collapse {}".format(times_edge_collapse))

    dists = [o.distance2_at(d, times_edge_collapse[0]),
             d.distance2_at(a, times_edge_collapse[1]),
             a.distance2_at(o, times_edge_collapse[2])]

    logging.debug("dists^2 {}".format(dists))
    logging.debug("dists {}".format([math.sqrt(_) for _ in dists]))
    logging.debug("near_zero dists {}".format(
        [near_zero(math.sqrt(_)) for _ in dists]))
    indices = []
    for i, _ in enumerate([math.sqrt(_) for _ in dists]):
        if near_zero(_):
            indices.append(i)
    t_e_c = []
    for i in indices:
        t_e_c.append(times_edge_collapse[i])
    logging.debug("t e c {}".format(t_e_c))
    time_edge_collapse = sieve(t_e_c, now)
    time_area_collapse = sieve(times_area_collapse, now)
    logging.debug(">> time_edge_collapse: {0}".format(time_edge_collapse))
    logging.debug(">> time_area_collapse: {0}".format(time_area_collapse))

    # spoke can be overrun by vertex -- should be witnessed by (inaccurate) area collapse
    # vertex_crash_times = [
    #     vertex_crash_time(o, d, a),
    #     vertex_crash_time(a, o, d),
    #     vertex_crash_time(d, a, o)
    # ]
    # logging.debug("vertex crash times " + str(time_vertex_crash))
    # time_vertex_crash = sieve(vertex_crash_times, now)
    # logging.debug("time vertex crash " + str(time_vertex_crash))


    if time_edge_collapse is None and time_area_collapse is None:
        # if we do not have a time for either, no collapse will happen
        return None
    elif time_edge_collapse is not None and time_area_collapse is not None:
        if near_zero(abs(time_area_collapse - time_edge_collapse)):
            logging.debug("area == edge")
            time = time_edge_collapse
            dists = [d.distance2_at(a, time),
                     a.distance2_at(o, time),
                     o.distance2_at(d, time)]
            zeros = [near_zero(d - min(dists)) for d in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 3:
                return Event(
                    when=time,
                    tri=tri,
                    side=(0, 1, 2),
                    tp="edge", tri_tp=tri.type)
            elif sides_collapse == 1:
                side = zeros.index(True)
                return Event(
                    when=time,
                    tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            else:
                time = time_area_collapse
                dists = [d.distance2_at(a, time),
                        a.distance2_at(o, time),
                        o.distance2_at(d, time)]
                largest_dist = max(dists)
                side = dists.index(largest_dist)
                return Event(when=time, tri=tri, side=(side,), tp="flip", tri_tp=tri.type)
                # return None
#            return None
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
        elif time_edge_collapse is not None:
            logging.debug("edge collapse")
            time = time_edge_collapse
            dists = [d.distance2_at(a, time),
                     a.distance2_at(o, time),
                     o.distance2_at(d, time)]
            zeros = [near_zero(_) for _ in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 3:
                return Event(
                    when=time, tri=tri,
                    side=(0, 1, 2), tp="edge", tri_tp=tri.type)
            elif sides_collapse == 1:
                side = zeros.index(True)
                return Event(
                    when=time, tri=tri, side=(side,),
                    tp="edge", tri_tp=tri.type)
            else:
                raise ValueError('can this happen?')
                return None
#            return None


#     largest_dist = max(dists)
#     side = dists.index(largest_dist)
#     return Event(when=time, tri=tri, side = (side,), tp="flip", tri_tp=tri.type)
#     raise ValueError("0 triangle with 2 or 0 side collapse, while edge collapse time computed?")

    else:
        # FIXME: much duplication here with above
        if time_edge_collapse is not None:
            time = time_edge_collapse
            dists = [d.distance2_at(a, time),
                     a.distance2_at(o, time),
                     o.distance2_at(d, time)]
            zeros = [near_zero(_) for _ in dists]
            sides_collapse = zeros.count(True)
            if sides_collapse == 3:
                return Event(
                    when=time, tri=tri, side=(0, 1, 2), tp="edge",
                    tri_tp=tri.type)
            elif sides_collapse == 1:
                side = zeros.index(True)
                return Event(
                    when=time, tri=tri, side=(side,), tp="edge",
                    tri_tp=tri.type)
            else:
                #                 return None
                # print repr(tri)
                # logging.debug("TRIANGLE NOT OK: {}".format(id(tri)))
                # return None
                raise ValueError(
                    "0 triangle with 2 or 0 side collapse,"
                    "while edge collapse time computed?")
        elif time_area_collapse is not None:
            time = time_area_collapse
            dists = [d.distance2_at(a, time),
                     a.distance2_at(o, time),
                     o.distance2_at(d, time)]
            largest_dist = max(dists)
            side = dists.index(largest_dist)
            tp = "flip"
            return Event(
                when=time, tri=tri, side=(side,), tp=tp, tri_tp=tri.type)
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
    
    # vertex crash time of the opposite vertex into the wavefront edge
    times_vertex_crash = [vertex_crash_time(ow, dw, aw)]
    # check unhandled event flip/split event
    for time in times_vertex_crash:
        if time is None:
            continue
        if near_zero(abs(time-now)):
            # as we have a vertex on the support line of the triangle *now*
            # we will have to flip or split *right now*
            logging.debug("OVERWRITE VERTEX CRASH")
            time = now

            ## --\\ spoke_collapse
            dists = [d.distance2_at(a, now),
                     a.distance2_at(o, now),
                     o.distance2_at(d, now)]
            indices = []
            for i, _ in enumerate([math.sqrt(_) for _ in dists]):
                if near_zero(_):
                    indices.append(i)
            if len(indices) == 1:
                # spoke collapse, leading to split of wavefront
                # we handle this as an edge collapse (the neighbour is not None, we will schedule_immediately this neighbour)
                side = indices[0]
                tp = "edge"
                return Event(when=now, tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            ## --// spoke_collapse

            dists = [math.sqrt(d.distance2_at(a, time)),
                            math.sqrt(a.distance2_at(o, time)),
                            math.sqrt(o.distance2_at(d, time))]
            longest_side = dists.index(max(dists))
            if longest_side == wavefront_side:
                tp = "split"
            else:
                tp = "flip"
            return Event(when=time,
                            tri=tri,
                            side=(longest_side,),
                            tp=tp,
                            tri_tp=tri.type)
    time_vertex_crash = sieve(times_vertex_crash, now)
    logging.debug("time vertex crash " + str(time_vertex_crash))

    # area collapse times
    time_area_collapse = sieve(area_collapse_times(o, d, a), now)
    logging.debug("time area collapse " + str(time_area_collapse))
    # edge collapse times
    time_edge_collapse = sieve([collapse_time_edge(ow, dw)], now)
    logging.debug([collapse_time_edge(ow, dw),
                   collapse_time_edge(dw, aw),
                   collapse_time_edge(aw, ow)])
    logging.debug("time edge collapse " + str(time_edge_collapse))


    # FLIP FIX not working
    # if time_area_collapse is not None and time_edge_collapse is not None and time_vertex_crash is not None and time_area_collapse < time_edge_collapse and time_area_collapse < time_vertex_crash:
    #     time = time_area_collapse 
    #     sides = []
    #     for i, n in enumerate(tri.neighbours):
    #         if n is not None:
    #             sides.append(i)
    #     dists = [d.distance2_at(a, time),
    #                  a.distance2_at(o, time),
    #                  o.distance2_at(d, time)]
    #     new_dists = []
    #     for i, d in enumerate(dists):
    #         if i in sides:
    #             new_dists.append(d)
    #         else:
    #             new_dists.append(-1)
    #     sides = (new_dists.index(max(new_dists)),)
    #     return Event(
    #             when=time, tri=tri, side=sides, tp="flip", tri_tp=tri.type)

    if time_edge_collapse is None and time_vertex_crash is None:
        # -- No edge collapse time and no vertex crash time
        logging.debug(" case A")
        time = sieve(
            solve_quadratic(*area_collapse_time_coeff(*tri.vertices)),
            now)
        if time is None:
            return None
        elif near_zero(time-now) == True:
            #raise NotImplementedError("time of flip is now -- can also be vertex crash")
            
            # -- area collapses now
            # dependent on the geometric config we have several outcomes for a 1-triangle
            # -- one option is: the vertex opposite lies on the interior of the wavefront side
            #    --> split the wavefront in 2
            return Event(when=now,
                            tri=tri,
                            side=(wavefront_side,),
                            tp="split",
                            tri_tp=tri.type)
        else:
            
            # we assume a flip event because no edge, nor vertex crash time
            # but area collapse in the future
            # as we flip, take only the distances of unconstrained edges into account
            # (wavefront edges can not flip)
            dists = [d.distance2_at(a, time) if tri.neighbours[0] is not None else -1,
                     a.distance2_at(o, time) if tri.neighbours[1] is not None else -1,
                     o.distance2_at(d, time) if tri.neighbours[2] is not None else -1]
            logging.debug(" {}".format(dists))
            sides = (dists.index(max(dists)),)
            return Event(
                when=time, tri=tri, side=sides, tp="flip", tri_tp=tri.type)

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
        logging.debug(" case B, time vertex crash " + str(time_vertex_crash))

        if time_area_collapse is not None and time_area_collapse < time_vertex_crash:
            logging.debug(" flip witnessed by area collapse time is earlier than vertex crash time -> we use the area collapse time, instead of vertex crash time")
            time = time_area_collapse
            # dists = [math.sqrt(d.distance2_at(a, time)),
            #         math.sqrt(a.distance2_at(o, time)),
            #         math.sqrt(o.distance2_at(d, time))]
        else:
            time = time_vertex_crash

        dists = [math.sqrt(d.distance2_at(a, time)),
                 math.sqrt(a.distance2_at(o, time)),
                 math.sqrt(o.distance2_at(d, time))]
        unique_dists = [near_zero(_ - max(dists)) for _ in dists]
        logging.debug(unique_dists)
        unique_max_dists = unique_dists.count(True)
        logging.debug(
            "uniq max dists (needs to be 1 for split) -- " +
            str(unique_max_dists))
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
                sides = (dists.index(min(dists)),)  # shortest side
                return Event(
                    when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
            else:
#                sides = (dists.index(max(dists)),)  # longest side
### FIXME: ###
#                if time_area_collapse is not None and time_area_collapse < time:
#                    logging.debug(" flip witnessed by area collapse time is earlier than vertex crash time -> we use the area collapse time, instead of vertex crash time")
#                    time = time_area_collapse
#                    dists = [math.sqrt(d.distance2_at(a, time)),
#                             math.sqrt(a.distance2_at(o, time)),
#                             math.sqrt(o.distance2_at(d, time))]
                sides = (dists.index(max(dists)),)  # longest side
### END FIXME: ###
                return Event(
                    when=time, tri=tri, side=sides, tp="flip", tri_tp=tri.type)

    elif time_edge_collapse is not None and time_vertex_crash is None:
        # -- Only edge collapse time
        logging.debug(" case C")
        return Event(when=time_edge_collapse,
                     tri=tri,
                     side=(wavefront_side,),
                     tp="edge",
                     tri_tp=tri.type)

    elif time_edge_collapse is not None and time_vertex_crash is not None:
        # -- Both edge collapse time and vertex crash time
        logging.debug(" case D")
        if time_edge_collapse < time_vertex_crash or \
                time_edge_collapse == time_vertex_crash:
            logging.debug(
                "edge collapse time earlier than vertex crash or equal")
            # wavefront edge collapses, because edge collapse time is earlier
            # or equal to vertex crash time
            time = time_edge_collapse
            sides = [wavefront_side]
#            dists = [math.sqrt(d.distance2_at(a, time)),
#                     math.sqrt(a.distance2_at(o, time)),
#                     math.sqrt(o.distance2_at(d, time))]

            dists_squared = [d.distance2_at(a, time),
                             a.distance2_at(o, time),
                             o.distance2_at(d, time)]
#            logging.debug('dists squared {}'.format(dists_squared))


            # shortest edge at that time collapses
            sides = [dists_squared.index(min(dists_squared))]

            assert len(sides) == 1
            tp = "edge"
##            # the collapsing shortest edge should be a wavefront edge
#            if tri.neighbours[sides[0]] is None:
#                tp = "edge"
#            else:
#                logging.debug('split detected, as non-wavefront edge collapses')
#                tp = "split"
#                sides = (wavefront_side,)

#            assert len(sides) == 1

#            zeros = [near_zero(dist) for dist in dists]
#            logging.debug('zeros {}'.format(zeros))
#            if True not in zeros:
#                raise ValueError("no event?")
                # return None
#            sides = [zeros.index(True)]

            return Event(when=time, tri=tri, side=sides, tp=tp, tri_tp=tri.type)
        elif time_vertex_crash < time_edge_collapse:
            # wavefront edge is split
            logging.debug("vertex crash time strictly "
                          "earlier than time edge collapse")
            # can be either split or flip
            # take longest side, if that side is wavefront -> split
            time = time_vertex_crash
            dists = [math.sqrt(d.distance2_at(a, time)),
                     math.sqrt(a.distance2_at(o, time)),
                     math.sqrt(o.distance2_at(d, time))]
            logging.debug('dists {}'.format(dists))
            zeros = [near_zero(dist) for dist in dists]
            logging.debug('zeros {}'.format(zeros))
            if True in zeros and zeros.count(True) == 1:
                logging.debug("one edge that has no length -> edge event")
                tp = 'edge'
                sides = (zeros.index(True), )
#                if tri.neighbours[sides[0]] is None:
#                    tp = "edge"
#                else:
#                    logging.debug('split detected, as non-wavefront edge collapses')
#                    tp = "split"
#                    sides = (wavefront_side,)
            elif True in zeros and zeros.count(True) == 3:
                logging.debug("3 edges that have no length -> edge event")
                tp = 'edge'
                sides = list(range(3))
            else:
                max_dist = max(dists)
                max_dist_side = dists.index(max_dist)
                if tri.neighbours[max_dist_side] is None:
                    tp = "split"
                else:
                    tp = "flip"
                sides = (max_dist_side, )
            return Event(
                when=time, tri=tri, side=sides, tp=tp, tri_tp=tri.type)
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
    if tri.neighbours[2] is None:
        time = collapse_time_edge(o, d)
        times.append(time)
    if tri.neighbours[0] is None:
        time = collapse_time_edge(d, a)
        times.append(time)
    if tri.neighbours[1] is None:
        time = collapse_time_edge(a, o)
        times.append(time)
    times = get_unique_times(times)
    logging.debug("Unique times: " + str(times))
    time = sieve(times, now)
    logging.debug("Time found: " + str(time))
    if time is None:
        time = sieve(area_collapse_times(o, d, a), now)
##        if time is not None:
##            logging.warning("Area collapse detects collapse, while edge collapse time does not")
##            logging.warning("Infinite fast vertex in place ???")
##            logging.warning("Time found: " + str(time))
##            logging.warning("")

    if time is not None:
        dists = [math.sqrt(d.distance2_at(a, time)),
                 math.sqrt(a.distance2_at(o, time)),
                 math.sqrt(o.distance2_at(d, time))]
        dists = [d - min(dists) for d in dists]
        logging.debug("distances at time = {1}: {0}".format(dists, time))
        zeros = [near_zero(dist) for dist in dists]
        logging.debug("near_zero = {}".format(zeros))
        sides_collapse = zeros.count(True)
        if sides_collapse == 3:
            #             for side, _ in enumerate(tri.neighbours):
            #                 if _ is not None:
            #                     break
            # (side,) # take the side that is not None (has a neighbour)
            sides = tuple(range(3))
            return Event(
                when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
        elif sides_collapse == 2:
            # hopefully never happens --
            # or some weird robustness error did occur
            raise ValueError("This is not possible with this type of triangle [{}]".format(tri.info))
        elif sides_collapse == 1:
            smallest_dist = min(dists)
            side = dists.index(smallest_dist)
            sides = (side,)
            return Event(
                when=time, tri=tri, side=sides, tp="edge", tri_tp=tri.type)
        elif sides_collapse == 0:
            return None
            #raise ValueError("This is not possible with this type of triangle")
    else:
        # -- Triangle does not collapse in the future
        return None



###def signed_turn(u, v):
###    """turn angle at vertex going from head via mid to tail
###    angle in radians

###    + == left turn
###    - == right turn
###    0 == straight
###    """
###    return math.atan2(cross(u, v), dot(u, v))


###def unitvecs(head, mid, tail):
###    u = make_vector(mid, head)
###    v = make_vector(tail, mid)
###    return unit(u), unit(v)

###def bisector_3tri(tri):
###    """ from 3 points, around constrained triangle -- determine collapse event time """
###    p0, p1, p2 = tri
###    print(p0)
###    print(p1)
###    print(p2)
###    # pre-condition: triangle turns ccw -- i.e. is still valid now
###    assert orient2d(p0, p1, p2) >= 0

###    # walk around the 3 points of the triangle -> origin's of kinetic vertices
###    its = [p2, p0, p1], [p0, p1, p2], [p1, p2, p0]
###    for it in its:
####        print(it)
###        p0, p1, p2 = it
###        u, v = unitvecs(p0, p1, p2)
####        print(u, v)
###        theta = signed_turn(u,v) 
####        theta = signed_turn(p0, p1, p2)
####        assert theta == theta2  
####        print("theta:", theta, theta2)
###        alpha = 0.5 * (math.pi - theta)
###        magnitude = math.sin(alpha)
####        print(alpha, math.degrees(alpha), magnitude)
###        # unit left / right of point moving in correct direction
###        # FIXME: computed multiple times 
###        ul, ur = rotate90ccw(u), rotate90ccw(v)
###        direction = add(ul, ur)
###        # the 'velocity' of the kinetic vertices
###        bisector_vec = div(unit(direction), magnitude)
####        print("l / r", ul, ur, direction, bisector_vec)

###        print("LINESTRING({0[0]:.6f} {0[1]:.6f}, {1[0]:.6f} {1[1]:.6f})".format(p1, add(p1,bisector_vec)))


def compute_event_3triangle(tri, now, sieve):
    # a 3-triangle can:
    # - collapse to a point
    # - collapse to 2 line segments (split)

    # Calculate 3 edge collapse times
    # These should all be similar for collapsing to a point

###    bisector_3tri([v.position_at(now) for v in tri.vertices])

    a, o, d = tri.vertices
    t_e_c = [
        collapse_time_edge(o, d),
        collapse_time_edge(d, a),
        collapse_time_edge(a, o)
    ]
    logging.debug("times edge collapse {}".format(t_e_c))

    dists = [o.distance2_at(d, t_e_c[0]),
             d.distance2_at(a, t_e_c[1]),
             a.distance2_at(o, t_e_c[2])]

    logging.debug("dists^2 {}".format(dists))
    logging.debug("dists {}".format([math.sqrt(_) for _ in dists]))
    logging.debug("near_zero dists {}".format(
        [near_zero(math.sqrt(_)) for _ in dists]))
    indices = []
    for i, _ in enumerate([math.sqrt(_) for _ in dists]):
        if near_zero(_):
            indices.append(i)

    assert tri.neighbours.count(None) == 3

    time_edge_collapse = sieve(t_e_c, now)
    time_area_collapse = sieve(area_collapse_times(o, d, a), now)
    logging.debug(">> time_edge_collapse: {0}".format(time_edge_collapse))
    logging.debug(">> time_area_collapse: {0}".format(time_area_collapse))
#    o, d, a = tri.vertices
#    times = []
#    time = collapse_time_edge(o, d)
#    times.append(time)
#    time = collapse_time_edge(d, a)
#    times.append(time)
#    time = collapse_time_edge(a, o)
#    times.append(time)
#    logging.debug(sorted(times))
#    #
#    time = sieve(get_unique_times(times), now)
#    logging.debug(time)
#        raise NotImplementedError('not a poiint collapse')
#     dists = [math.sqrt(d.distance2_at(a, time)),
#              math.sqrt(a.distance2_at(o, time)),
#              math.sqrt(o.distance2_at(d, time))]
#     logging.debug(dists)
#     logging.debug(map(near_zero, dists))
#     # we should find at most 1 collapse time
# #     assert len(times) <= 1, times
#     # we take this event only when it is >= now (now or in the future)
#     zeros = map(near_zero, dists)
    if time_edge_collapse:  # and all(zeros):
        sides = tuple(indices)
        if len(sides) == 0:
            logging.error('3-triangle: override # of sides collapsing -- instead of 0!, we collapse all 3')
            sides = list(range(3))
        # somehow we missed 1 edge collapse (due to distance tolerance)
        if len(sides) == 2:
            logging.warning('3-triangle: override # of sides collapsing -- instead of 2, we collapse all 3')
            sides = list(range(3))
#        sides = range(3)
        return Event(
            when=time_edge_collapse , tri=tri, side=sides, tp="edge", tri_tp=tri.type)
    elif time_area_collapse:
        logging.error('3-triangle: using area collapse time as fall back not to miss out')
        sides = list(range(3))
        return Event(
            when=time_area_collapse , tri=tri, side=sides, tp="edge", tri_tp=tri.type)
#     elif time and zeros.count(True) == 1:
#         sides = (dists.index(max(dists)),)
#         return Event(
#             when=time, tri=tri, side=sides, tp="split", tri_tp=tri.type)
    else:
        return None
#        return Event(
#             when=now, tri=tri, side=tuple(range(3)), tp="edge", tri_tp=tri.type)


def compute_event_inftriangle(tri, now, sieve):
    for inf_idx, v in enumerate(tri.vertices):
        if isinstance(v, InfiniteVertex):
            break
    side = inf_idx
#    logging.debug(repr(tri))
    logging.debug("side " + str(side))
    o, d, a = tri.vertices[cw(side)], \
        tri.vertices[ccw(side)], \
        tri.vertices[side]
    logging.debug(o)
    logging.debug(d)
    if tri.neighbours[side] is None:  # wavefront edge on the hull that collapses
        assert tri.type == 1, tri.type
        # time of closest approach of the 2 points
        time = find_gt([collapse_time_edge(o, d)], now)
        logging.debug("time of closest approach {}".format(time))
        if time:
            dist = o.distance2_at(d, time)
            logging.debug(dist)
            if near_zero(dist):
                # collapsing edge!
                return Event(
                    when=time, tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            else:
                return None
                raise ValueError('problem?')
    else:
        time = sieve(area_collapse_times(o, d, a), now)
        logging.debug("time = {}".format(time))
        if time:
            dist = o.distance2_at(d, time)
            if near_zero(dist):
                return Event(
                    when=time, tri=tri, side=(side,), tp="edge", tri_tp=tri.type)
            else:
                tp = "flip"
                # Determine side to flip
                #
                # The flip of infinite triangle leads to
                # 1 finite and 1 infinite triangle
                #
                # compute dists for 2 legs incident with inf vertex
                # shortest leg of the two has to be flipped away
                dists = []
                for func in cw, ccw:
                    start, end = Edge(tri, func(side)).segment
                    dists.append(start.distance2_at(end, time))
                idx = dists.index(min(dists))
                min_dist_side = [cw, ccw][idx](side)
                return Event(
                    when=time, tri=tri, side=(min_dist_side,), tp=tp, tri_tp=tri.type)


def compute_collapse_time(tri, now=0, sieve=find_gte):
    """Computes Event that represents how a triangle collapses at a given time
    """
    event = None
    if tri.stops_at is not None:
        # we have a triangle that has been stopped already, return None
        return event
    if tri.is_finite:
        logging.debug("")
        logging.debug("=-=-= finite triangle #{} [{}]=-=-= ".format(id(tri), tri.info))
###########        logging.debug(repr(tri))
        # finite triangles
        tp = tri.type
        if tp == 0:
            logging.debug(" event for 0-triangle")
            event = compute_event_0triangle(tri, now, sieve)
        elif tp == 1:
            logging.debug(" event for 1-triangle")
            event = compute_event_1triangle(tri, now, sieve)
        elif tp == 2:
            logging.debug(" event for 2-triangle")
            event = compute_event_2triangle(tri, now, sieve)
        elif tp == 3:
            logging.debug(" event for 3-triangle")
            event = compute_event_3triangle(tri, now, sieve)

        # if we do not have any infinite fast vertices
        # the triangle halfway between now and when it will collapse according to the event
        # should have consistent orientation of its vertices
        if event is not None and all(not v.inf_fast for v in tri.vertices) == True:
            assert event is not None
            verts = [v.position_at(((event.time - now) * 0.5) + now) for v in tri.vertices]
            from geompreds import orient2d
            if orient2d(*verts) < 0:
                logging.warning("TRIANGLE TAKES POSSIBLY WRONG ORIENTATION -- we may miss out on handling an event -- triangle turns wrong way")
                # raise ValueError('wrongly turning triangle, we maybe will miss an event; New event: {}'.format(event))
        if event is None:
            verts = [v.position_at(now + 10) for v in tri.vertices]
            from geompreds import orient2d
            if orient2d(*verts) < 0:
                logging.error("TRIANGLE HAS WRONG ORIENTATION and will not collapse -- we missed out on handling an event -- triangle turns wrong way")
                # raise ValueError('triangle will not collapse, but turns wrongly :: we missed an event')

    else:
        # flip or collapse to point
        logging.debug("")
        logging.debug("=-=-= infinite triangle #{} [{}] =-=-=".format(id(tri), tri.info))
        event = compute_event_inftriangle(tri, now, sieve)
    if event is not None:
        tri.event = event
    logging.debug("{} --- {}".format(id(tri), event))


            # raise NotImplementedError('we missed an event as triangle is not valid until next event time')
    return event


# FIXME: Rename method
# it does not compute collapse time, it computes a new event
# at a given time, the triangle should collapse, but which sides ??
# also the type should probably be considered -> could lead to split of 2-triangle (parallel fan)
def compute_new_edge_collapse_event(tri, time):
    """Compute new edge event for triangle that collapse at time

    Somehow we know that one or more of the edges of this triangle do collapse at this moment
    """
    o, d, a = tri.vertices
    dists = list(map(math.sqrt, [d.distance2_at(a, time),
             a.distance2_at(o, time),
             o.distance2_at(d, time)]))
    logging.debug("distances at time = {1}: {0}".format(dists, time))
    zeros = [near_zero(dist - min(dists)) for dist in dists]
    logging.debug("near zero at time = {1}: {0}".format(zeros, time))
    sides = []
    for i, zero in enumerate(zeros):
        if zero is True:
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
    logging.debug("edge collapse time for v1 = {} [{}] and v2 = {} [{}]".format(id(v1), v1.info,
                                                                      id(v2), v2.info))
    s1 = v1.velocity
    s2 = v2.velocity
    o1 = v1.origin
    o2 = v2.origin
    dv = sub(s1, s2)
    denominator = dot(dv, dv)
#     logging.debug("denominator for edge collapse time {}".format(denominator))
    if not near_zero(denominator):
        w0 = sub(o2, o1)
        nominator = dot(dv, w0)
#         logging.debug("nominator for edge collapse time {}".format(nominator))
        collapse_time = nominator / denominator
        logging.debug("edge collapse time: " + str(collapse_time))
        return collapse_time
    else:
        logging.debug("denominator (close to) 0")
        logging.debug("these two vertices move in parallel:")
        logging.debug(str(v1) + "|" + str(v2))
        logging.debug("edge collapse time: None (near) parallel movement")
        # any time will do (we pick a time in the past, before the start of our event simulation)
        return -1.





def solve_quadratic_whatevery(A, B, C):
    if near_zero(A) and not near_zero(B):
        # A near zero, not a quadratic =>
        # we solve a linear equation:
        # B*x + C = 0
        # B*x = -C
        # x = -C / B
        return [-C / B]
    elif near_zero(A) and near_zero(B):
        # No solution, line parallel to the x-axis, not crossing the x-axis
        # raise NotImplementedError("Not done yet")
        return []
    try:
        d = math.sqrt(B*B-4*A*C)
    except ValueError:
        return []

    def div(n, d):
        """Divide, with a useful interpretation of division by zero."""
    #    try:
        return n/d
    #    except ZeroDivisionError:
    #        if n:
    #            return n*float('inf')
    #        return float('nan')

    if B > 0:
        return [div(2*C, (-B-d)), div((-B-d), 2*A)]
    else:
        return [div((-B+d), 2*A), div(2*C, (-B+d))]
 


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
        return [-C / B]
    elif near_zero(A) and near_zero(B):
        # No solution, line parallel to the x-axis, not crossing the x-axis
        # raise NotImplementedError("Not done yet")
        return []
    T = -B / A  # a + d
    D = C / A   # a*d - b*c
    centre = T * 0.5
    under = 0.25 * pow(T, 2) - D
    if near_zero(under):
        # -- one root
        return [centre]
    elif under < 0:
        # -- imaginary roots
        return []
    else:
        # return L1, L2 (the Eigen values of M)
        plus_min = math.sqrt(under)
        return [centre - plus_min, centre + plus_min]



##def solve_quadratic(A, B, C):
##    """Get the roots for quadratic equation, defined by A, B and C

##    The quadratic equation A*x^2 + B*x + C = 0 can be
##    described with its companion matrix M, where

##    M = [[a b], [c d]] == [[0 -C/A], [1 -B/A]]

##    The roots that we want to find are the eigenvalues L1, L2
##    of this 2x2 matrix.

##    L1 = 0.5*T + (0.25*T^2 - D)^0.5
##    L2 = 0.5*T - (0.25*T^2 - D)^0.5

##    with:

##    T = a + d
##    D = a*d - b*c

##    Note, if A == 0 and B != 0 gives the answer for B*x + C = 0
##    """
##    if near_zero(A) and not near_zero(B):
##        # A near zero, not a quadratic =>
##        # we solve a linear equation:
##        # B*x + C = 0
##        # B*x = -C
##        # x = -C / B
##        return [-C / B]
##    elif near_zero(A) and near_zero(B):
##        # No solution, line parallel to the x-axis, not crossing the x-axis
##        # raise NotImplementedError("Not done yet")
##        return []

##    elif B >= 0:
##        one = -B - math.sqrt(B * B - 4 * A * C)
##        x1 = one / 2 * A
##        x2 = 2 * C / one
##        roots = [x1, x2]
##        roots.sort()
##        return roots

##    elif B < 0:
##        one = -B + math.sqrt(B * B - 4 * A * C)
##        x1 = 2 * C / one
##        x2 = one / 2 * A
##        roots = [x1, x2]
##        roots.sort()
##        return roots

#    T = -B / A  # a + d
#    D = C / A   # a*d - b*c
#    centre = T * 0.5
#    under = 0.25 * pow(T, 2) - D
#    if near_zero(under):
#        # -- one root
#        return [centre]
#    elif under < 0:
#        # -- imaginary roots
#        return []
#    else:
#        # return L1, L2 (the Eigen values of M)
#        plus_min = pow(under, 0.5)
#        return [centre - plus_min, centre + plus_min]


## Investigate whether this works better:
##double a = 3.0, b = 1.0e9, c = 5.0;
##double d = b*b - 4.0*a*c;
##double r1 = (-b - sqrt(d))/(2.0*a);
##double r2 = -2.0*c/(b + sqrt(d));
## https://www.codeproject.com/Articles/25294/Avoiding-Overflow-Underflow-and-Loss-of-Precision

## also check: https://github.com/linebender/kurbo/pull/59
## linked from: https://math.stackexchange.com/questions/866331/numerically-stable-algorithm-for-solving-the-quadratic-equation-when-a-is-very

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
            bisector_fh.write(
                "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(
                    p1, add(p1, bi)))
    
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles_at_T([tri], T, fh)

    with open("/tmp/kvertices.wkt", "w") as fh:
        output_vertices_at_T(tri.vertices, T, fh)

    with open("/tmp/wavefront.wkt", "w") as fh:
        try:
            edges = []
            for i, n in enumerate(tri.neighbours):
                if n is None:
                    edges.append(Edge(tri, i))
            output_edges_at_T(edges, T, fh)
        except:
            pass

    with open("/tmp/rays.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt\n")
        for kvertex in tri.vertices:
            p1 = kvertex.origin
            bi = kvertex.velocity
            bineg = mul(bi, -10000.0)
            bipos = mul(bi, 10000.0)
            bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(add(p1, bipos),
                                                                                  add(p1, bineg)))


def test_compute_collapse_times():
    from grassfire.primitives import KineticTriangle, KineticVertex
    cases = [
        # infinite 0-triangle
        (0,
         KineticTriangle(InfiniteVertex((2., 4.)),
                         KineticVertex((2., 0.), (-0.5, -0.5)),
                         KineticVertex((1., 1.), (0.5, 0.)), True, True, True),
         (1.211102550928, "flip")
         ),
        # infinite 0-triangle
        (0,
         KineticTriangle(InfiniteVertex((1., 4.)),
                         KineticVertex((2., 0.), (-0.5, -0.5)),
                         KineticVertex((0., 0.), (0.5, -0.5)), True, True, True),
         (2.0, "edge")
            # None
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
                            KineticVertex((2., 0.), (0., +1)), None, True, True),
            (2.666666666667, "edge")),
        # finite 1-triangle
        (0,
         KineticTriangle(KineticVertex((1., 4.), (0., -0.5)),
                         KineticVertex((0., 0.), (0., 1.)),
                         KineticVertex((2., 0.), (0., 1.)), None, True, True),
         (2.666666666667, "split")),
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
         (2.666666666667, "flip")),
        # finite 1 triangle that should split
        # we miss the event
        (0,
         KineticTriangle(
             KineticVertex(
                 (11.1,
                  0.0),
                 (-0.41421356237309614,
                  1.0)),
             KineticVertex(
                 (14.0,
                  10.0),
                 (-0.41434397951188867,
                  -1.0828510849683515)),
             KineticVertex(
                 (-33.307692307692705,
                  2.115384615384554),
                 (9.300198345114286,
                  0.536239302469343)),
             None,
             True,
             True),
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
         KineticTriangle(
             KineticVertex(
                 (11.1, 0.0), (-0.41421356237309614, 1.0)), KineticVertex(
                 (9.0, 0.0), (0.024984394500786274, 1.0)), KineticVertex(
                 (11.0, -0.1), (-0.39329937395053033, 1.0209141884225659)), None, None, True),
            (4.781443007949, "edge")),

        (0,
         KineticTriangle(
             KineticVertex(
                 (-0.866025403784, 0.5), (0.3660254037831927, -1.3660254037847726)), KineticVertex(
                 (-0.866025403784, 0.5), (-1.3660254037847726, -0.3660254037831926)), InfiniteVertex(
                 (2.4999999999993334, 1.4433756729733331)), True, True, None),
            # None
            (0, "edge")
         ),

        (0,
         KineticTriangle(
             KineticVertex(
                 (3.36602540378, 4.83012701892), (-1.366025403784519, 0.366025403784139)), KineticVertex(
                 (1.63397459622, 4.83012701892), (1.3660254037847726, 0.366025403783193)), KineticVertex(
                 (5.86602540378, 0.5), (-0.366025403784139, -1.3660254037845188)), True, None, True),
            (0.6339745962123428, "edge")),

        (0,
         KineticTriangle(KineticVertex((-
                                        0.9510565162951535, 0.3090169943749475), (1.6827457682352098, -
                                                                                  0.5467572438521933)), KineticVertex((6.123233995736766e-17, 1.0), (-
                                                                                                                                                     2.3811458388420067e-16, -
                                                                                                                                                     1.7693436082961256)), KineticVertex((-
                                                                                                                                                                                          1.6180339887498947, 1.1755705045849465), (0.18250881904109725, 1.4023874396799996)), True, None, True),
         (0.56518134482820892, "edge")),

        (0,
         KineticTriangle(
             KineticVertex(
                 (-0.2, -0.06666666666666667), (1.8695058979924137, 0.04448684017361237)), KineticVertex(
                 (0.3333333333333333, -0.6), (-0.4142135623730951, 1.0)), KineticVertex(
                 (0.3333333333333333, 0.6), (-0.2506607793572, -1.0800962240008098)), True, True, True),
            (0.241024119, "flip")),

        (0,
         KineticTriangle(KineticVertex((-
                                        0.9872805569585875, 0.12537065799230004), (-
                                                                                   1.024866765183742, -
                                                                                   1.1114119702481062)), KineticVertex((-
                                                                                                                        0.8437938978984622, -
                                                                                                                        0.19040991430610052), (21.666935207544306, 44.860914394127434)), KineticVertex((-
                                                                                                                                                                                                        0.7653348342872799, -
                                                                                                                                                                                                        0.10537661431275783), (-
                                                                                                                                                                                                                               1.0428319428196307, -
                                                                                                                                                                                                                               0.08857245780155545)), True, True, True),
            (0.00242630813253, "flip")),

        (0,
         KineticTriangle(KineticVertex((-
                                        0.25, 0.75), (-
                                                      2.4142135623730945, -
                                                      0.9999999999999996)), KineticVertex((-
                                                                                           0.25, -
                                                                                           0.75), (2.4142135623730945, 0.9999999999999996)), KineticVertex((0.25, -
                                                                                                                                                            0.75), (-
                                                                                                                                                                    2.4142135623730945, 0.9999999999999996)), True, True, True),
            (0.103553390593274, "edge")
         ),
        (0.01,
         KineticTriangle(KineticVertex((-
                                        0.2514204545452013, -
                                        0.43678977272891734), (-
                                                               1.1213425200822953, 0.8653503174771875)), KineticVertex((-
                                                                                                                        0.39342794594029157, 0.34274872190648226), (1.1112498367417047, -
                                                                                                                                                                    0.7879730785326)), KineticVertex((-
                                                                                                                                                                                                      0.39346590909065293, 0.3430397727259427), (1.119825823231893, -
                                                                                                                                                                                                                                                 0.8537223082927444)), None, True, True),
            (0.019994907, "flip")
         ),
        (0,
         KineticTriangle(KineticVertex((0.4348145985280354, -
                                        0.45254225871408715), (-
                                                               0.9629719544552265, 0.27936526970827974)), KineticVertex((0.45503984798207725, -
                                                                                                                         0.35731302646132906), (-
                                                                                                                                                0.8099200307905356, 0.9999999999999997)), KineticVertex((0.31446758274483105, -
                                                                                                                                                                                                         0.6518477551830741), (-
                                                                                                                                                                                                                               1.413908790141726, -
                                                                                                                                                                                                                               0.02935869819935455)), True, True, None),
            None)
    ]
    do_test = True
    if do_test:
        for i, (now, tri, expected) in enumerate(cases, start=0):
            print()
            print(( "Case", i))
            print(( "=" * 10))
            visualize_collapse(tri, now)
            evt = compute_collapse_time(tri, now)
            print(( evt, expected))
            if evt is not None:
                if expected is None:
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
        print (evt)
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
    print((solve_quadratic(A, B, C) == []))

    A, B, C = 2.0, 0.0, 0.0
    print((solve_quadratic(A, B, C) == [0.0]))

    A, B, C = 1.0, 3.0, 2.0
    print((solve_quadratic(A, B, C) == [-2.0, -1.0]))


def main():
    # test_compute_collapse_times()
    test_one_collapse()


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

    #tri = KineticTriangle(KineticVertex((-0.25, 0.75), (-2.4142135623730945, -0.9999999999999996)), KineticVertex((-0.25, -0.75), (2.4142135623730945, 0.9999999999999996)), KineticVertex((0.25, -0.75), (-2.4142135623730945, 0.9999999999999996)), True, True, True)

    # infinite triangle that needs to flip (so around 0.14?
    #tri = KineticTriangle(InfiniteVertex((0.03563328767477883, -0.06225382499568152)), KineticVertex((0.8308871493803005, -0.35731302646132906), (1.248735516282837, 1.0000000000000002)), KineticVertex((0.7971434930656011, -0.5079794287841405), (0.9543989274069261, -0.3142213903649677)), None, True, True)
    # tri = KineticTriangle(KineticVertex((0.8534771264074428, -0.06782665418758393), (1.0, -1.0)), InfiniteVertex((0.03563328767477881, -0.06225382499568156)), KineticVertex((0.8534771264074428, 0.10897926770469894), (1.0, 0.03649041282240072)), True, None, True)

    #tri = KineticTriangle(KineticVertex((0.8308871493803005, -0.35731302646132906), (1.248735516282837, 1.0000000000000002)), InfiniteVertex((0.0356332876747788, -0.06225382499568155)), KineticVertex((0.8534771264074428, -0.06782665418758393), (1.0, -1.0)), True, True, True)

    # infinite 0-triangle should flip at: 0.14372166332027514
    # tri = KineticTriangle(KineticVertex((0.8308871493803005, -
    # 0.35731302646132906), (1.248735516282837, 1.0000000000000002)), InfiniteVertex((0.035633287674778816, -
#                                                                                                                          0.06225382499568152)), KineticVertex((0.8534771264074428, -
#                                                                                                                                                                0.06782665418758393), (1.0, -
#                                                                                                                                                                                       1.0)), True, True, True)
#
#     tri = KineticTriangle(KineticVertex((0.2, 0.1), (-0.5, -1.0), (-0.0, -1.0), (-0.8, -0.6000000000000001)),
# KineticVertex((0.2, -0.1), (-0.5, 1.0), (-0.8, 0.6000000000000001), (-0.0, 1.0)),
# KineticVertex((1.0, 0.1), (-0.9999999999999999, -0.9999999999999999), (-1.0, 0.0), (-0.0, -1.0)), True, None, True)




    # tri = KineticTriangle(KineticVertex((0.2, 0.1), (-0.5, -1.0), (-0.0, -1.0), (-0.8, -0.6000000000000001)),
    #                       KineticVertex((0.2, -0.1), (-0.5, 1.0),
    #                                     (-0.8, 0.6000000000000001), (-0.0, 1.0)),
    #                       KineticVertex((1.0, 0.1), (-0.9999999999999999, -0.9999999999999999), (-1.0, 0.0), (-0.0, -1.0)), True, None, True)
    # now = 0.  # 0.6339745962123428

#    def KineticVertex(origin=None, velocity=None, ul=None, ur=None)

##    tri = KineticTriangle(KineticVertex((-0.2941460749857284, -1.9944028440429675),
##        #(-31.916444710007777, 625.4387471202283),
##        (0, 0), # static
##        (-0.9987805884988515, -0.049369383608547396),
##        (0.998617829332686, 0.05255883311941421)),

##        KineticVertex((-0.3764671693980948, -0.4303110631701819),
##        (0.9986179074408387,
##        0.052557349064511094),
##        (0.998617829332686,
##        0.05255883311941421),
##        (0.9986179855445806,
##        0.05255586500937582)),

##        KineticVertex((-0.37147762485121205, -0.4299261332026524),
##        (-0.9986662884239297,
##        -0.05168176200486036),
##        (-0.9985412823874946,
##        -0.05399358635928628),
##        (-0.9987805884988515,
##        -0.049369383608547396)),
##        True,
##        None,
##        None)

    tri = KineticTriangle(KineticVertex((-0.25890832526488483,
    1.0),
    (0.8629392738894351,
    -1.2541589253803134),
    (-0.24881895085820574,
    -0.9685500140384191),
    (0.993509292081015,
    -0.11375098482510204)),

    KineticVertex((-0.4180575328215234,
    -0.3900206383088658),
    (-0.4172703730965519,
    -12.435602163414288),
    (0.993509292081015,
    -0.11375098482510204),
    (-0.9988997443815248,
    -0.04689670217109577)),

    KineticVertex((-0.4159764930624239,
    -0.4312893163239368),
    (-1.0459590484062025,
    0.9554664616505931),
    (-0.9988997443815248,
    -0.04689670217109577),
    (-0.04343900602459881,
    0.9990560808861507)),
    None,
    True,
    None)


#    tri = KineticTriangle(KineticVertex((0.2173277124280331, 0.698416760614311), (0.41124654232084884, 0.919545641592878), (0.29546368892668795, 0.9553539702779454), (0.5151235666701907, 0.8571159262672592)),
#KineticVertex((0.21178657399529294, 0.9831390013046308), (-0.18724127375184607, -0.9872847139880617), (-0.28216706807814973, -0.9593652827219572), (-0.08868469195702208, -0.9960597499209011)),
#KineticVertex((-1.07262137319989, 1.0973611594703172), (9.311325418444167, -1.8329944831033405), (-0.08868469195702208, -0.9960597499209011), (0.29546368892668795, 0.9553539702779454)), None, None, True)
#    now = 0.1304109494714286443528550308

    for info, v in enumerate(tri.vertices, start = 1):
        v.info = info

    now = 0.003107819648575184823952044511
    print(now)
    evt = compute_collapse_time(tri, now)
    print(evt)
    # 0.00242630813252781, 0.6340506109731798, 0.004284474881621788,
    # 0.0022096098886525, 0.22933526207436553]
    times = [now - 0.1, now+0, now+0.05, now+0.1]
    for time in sorted(times):
        visualize_collapse(tri, time)
        input("paused at " + str(time))


if __name__ == "__main__":

    import logging
    import sys
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)
    # -- logging
    # import logging
    # import sys
    # root = logging.getLogger()
    # root.setLevel(logging.DEBUG)

    # ch = logging.StreamHandler(sys.stdout)
    # ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter(
    #     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # ch.setFormatter(formatter)
    # root.addHandler(ch)
    # -- main function
    main()
    # test_compute_collapse_times()
