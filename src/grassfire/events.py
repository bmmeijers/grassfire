import logging

from time import sleep

from tri.delaunay import apex, orig, dest, cw, ccw, Edge
from oseq import OrderedSequence

from grassfire.primitives import SkeletonNode, KineticVertex
from grassfire.collapse import compute_collapse_time, find_gt, \
    compute_collapse_time_at_T

from grassfire.inout import output_triangles_at_T
import os

from collections import deque

from grassfire.vectorops import mul, bisector, add, dist
from grassfire.calc import near_zero
from grassfire.inout import visualize


def compare_event_by_time(one, other):
    """ Compare two events, first by time, in case they are equal
    by triangle type (first 2-triangle, then 1-triangle, then 0-triangle),
    as last resort by identifier of triangle.
    """
    # compare by time
    if one.time < other.time:  # lt
        return -1
    elif one.time > other.time:  # gt
        return 1
    # in case times are equal, compare by id of triangle
    # to be able to find the correct triangle back
    else:  # eq
        if -one.triangle_tp < -other.triangle_tp:
            return -1
        elif -one.triangle_tp > -other.triangle_tp:
            return 1
        else:
            if id(one.triangle) < id(other.triangle):
                return -1
            elif id(one.triangle) > id(other.triangle):
                return 1
            else:
                return 0


def init_event_list(skel):
    """Compute for all kinetic triangles when they will collapse and
    put them in an OrderedSequence, so that events are ordered properly
    for further processing
    """
    q = OrderedSequence(cmp=compare_event_by_time)
    logging.debug("Calculate initial events")
    logging.debug("=" * 80)
    for tri in skel.triangles:
        res = compute_collapse_time(tri, 0, find_gt)
        if res is not None:
            q.add(res)
    logging.debug("=" * 80)
    return q

# ------------------------------------------------------------------------------
# Event handling


def stop_kvertices(V, now):
    """ Stop a list of kinetic vertices at time t, creating a new node.

    If one of the vertices was already stopped before, at a node, use that
    skeleton node

    Returns tuple of (new node, False) in case all vertices are stopped for the
    first time, otherwise it returns (node, True) to indicate that were already
    stopped once.
    """
    # precondition:
    # the kinetic vertices that we are stopping should be
    # at more or less at the same location
#     assert at_same_location(V, now)
    sk_node = None
    for v in V:
        stopped = v.stops_at is not None
        time_close = near_zero(v.starts_at - now)
        logging.debug(
            "Vertex starts at same time as now: {}".format(time_close))
        logging.debug("Kinetic vertex is not stopped: {}".format(stopped))
        # vertex already stopped
        if stopped:
            logging.debug("Stop_node of vertex")
            sk_node = v.stop_node
        elif time_close:
            # FIXME: for the parallel case this code is problematic
            # as start and end point will be at same time
            assert not stopped
            sk_node = v.start_node
        else:
            v.stops_at = now
    if sk_node is not None:
        logging.debug("Skeleton node already there")
        for v in V:
            v.stop_node = sk_node
        return sk_node, False
    else:
        logging.debug("Make new skeleton node")
        l = [v.position_at(now) for v in V]
        ct = len(l)
        sumx, sumy = 0., 0.
        for x, y in l:
            sumx += x
            sumy += y
        pos = sumx / ct, sumy / ct
        sk_node = SkeletonNode(pos)
        for v in V:
            v.stop_node = sk_node
        return sk_node, True


def compute_new_kvertex(ul, ur, now, sk_node):
    """Based on the two wavefront directions and time t=now, compute the
    velocity and position at t=0 and return a new kinetic vertex

    Returns: KineticVertex
    """
    kv = KineticVertex()
    kv.starts_at = now
    kv.start_node = sk_node
    kv.velocity = bisector(ul, ur)
    if kv.velocity == (0, 0):
        kv.inf_fast = True
    kv.ul = ul
    kv.ur = ur
    # compute where this vertex would have been at time t=0
    neg_velo = mul(mul(kv.velocity, -1.0), now)
    pos_at_t0 = add(sk_node.pos, neg_velo)
    kv.origin = pos_at_t0
    return kv, True


def replace_kvertex(t, v, newv, now, direction, queue):
    """Replace kinetic vertex at incident triangles

    Returns fan of triangles that were replaced
    """
    logging.debug("replace_kvertex, start at: {0}".format(id(t)))
    fan = []
    while t is not None:
        assert t.stops_at is None, "{}: {}".format(
            id(t), [id(n) for n in t.neighbours])
        logging.debug(" @ {}".format(id(t)))
        side = t.vertices.index(v)
        fan.append(t)
        t.vertices[side] = newv
        logging.debug(
            "Placed vertex #{} at side {} of triangle {}".format(
                id(newv),
                # repr(newv),
                side,
                id(t)
                # , repr(t)
                ))
        if newv.inf_fast and t.event is not None:  # infintely fast
            queue.discard(t.event)
        else:  # vertex moves with normal speed
            replace_in_queue(t, now, queue)
        t = t.neighbours[direction(side)]
    return tuple(fan)


def at_same_location(V, now):
    """Checks whether all vertices are more or less at same location of first
    vertex in the list
    """
    P = [v.position_at(now) for v in V]
    p = P[0]
    for o in P[1:]:
        if not (near_zero(p[0]-o[0]) and near_zero(p[1]-o[1])):
            return False
    return True

# def replace_inffast_kvertex(t, v, newv, now, direction, queue):
#     """Replace kinetic vertex at incident triangles
# 
#     As the vertex we replace is infinitely fast, we walk 'along' the wavefront
#     until we find a wavefront edge that has length
# 
#     Returns:
#         fan of triangles that were replaced
#         vertices that were replaced 
#     """
#     logging.debug("replace_inffast_kvertex, start at: {0}".format(id(t)))
#     fan = []
#     while t is not None:
#         assert t.stops_at is None, id(t)
#         logging.debug(" @ {}".format(id(t)))
#         side = t.vertices.index(v)
#         fan.append(t)
#         # stop_kvertices([t.vertices[side]], now)
#         t.vertices[side] = newv
#         logging.debug("Placed infinitely fast vertex {} at side {} of triangle {} <{}>".format(repr(newv), side, id(t), repr(t)))
#         if t.event is not None:
#             queue.discard(t.event)
#         ngb = t.neighbours[direction(side)]
#         if ngb is None:
#             v = t.vertices[direction(direction(side))]
#             if at_same_location([newv, v], now):
#                 # replace other side of edge
#                 t.vertices[direction(direction(side))] = newv
#                 logging.debug("Placed infinitely fast vertex {}"
#                               " at side {} of triangle {} <{}>".
#                               format(
#                        repr(newv), 
#                        direction(direction(side)), 
#                        id(t), 
#                        repr(t)))
#                 t = t.neighbours[side]
#             else:
#                 return tuple(fan)
#         else:
#             t = ngb
#     return tuple(fan)


def replace_in_queue(t, now, queue):
    """Replace event for a triangle in the queue """
    if t.event is not None:
        queue.discard(t.event)
    else:
        logging.debug(
            "triangle #{0} without event not removed from queue".format(
                id(t)))
    e = compute_collapse_time(t, now)
    if e is not None:
        logging.debug("new event in queue {}".format(e))
        queue.add(e)
    else:
        logging.debug("no new events".format(e))
        return


def update_circ(v_left, v_right, now):
    """Update neighbour list of kinetic vertices (this is a circular list going
    around the wavefront edges

    Note that for a vertex often 2 sides need to be updated.
    """
    # update circular list, as follows:
    #               <-----
    # v_left.right o       o v_right.left
    #               ------>
    if v_left is not None:
        logging.debug("update_circ at right of #{} lies #{}".format(
                                                  id(v_left),
                                                  id(v_right)))
        v_left.right = v_right, now
    if v_right is not None:
        logging.debug("update_circ at left  of #{} lies #{}".format(
                                                  id(v_right),
                                                  id(v_left)))
        v_right.left = v_left, now


# ------------------------------------------------------------------------------
# Edge event handlers


def handle_edge_event(evt, skel, queue, immediate):
    t = evt.triangle
    logging.debug(evt.side)
    assert len(evt.side) == 1, len(evt.side)
    # take edge e
    e = evt.side[0]
    logging.debug(
        "wavefront edge collapsing? {0}".format(
            t.neighbours[e] is None))
    now = evt.time
    v1 = t.vertices[(e + 1) % 3]
    v2 = t.vertices[(e + 2) % 3]
    # stop the two vertices and make new skeleton node
    # replace 2 vertices with new kinetic vertex
    sk_node, newly_made = stop_kvertices([v1, v2], now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    kv, newly_made = compute_new_kvertex(v1.ul, v2.ur, now, sk_node)
    logging.debug("new kinetic vertex {}".format(id(kv)))
    if newly_made:
        skel.vertices.append(kv)
    update_circ(v1.left, kv, now)
    update_circ(kv, v2.right, now)
    if kv.inf_fast:
        logging.debug("New kinetic vertex moves infinitely fast!")
    # append to skeleton structure, kinetic vertices
    # get neighbours around collapsing triangle
    a = t.neighbours[(e + 1) % 3]
    b = t.neighbours[(e + 2) % 3]
    n = t.neighbours[e]

    fan_a = []
    fan_b = []
    if a is not None:
        logging.debug("replacing vertex for neighbour A")
        a_idx = a.neighbours.index(t)
        a.neighbours[a_idx] = b
        # fan_a
#         if inf_fast:
#             fan_a = replace_inffast_kvertex(a, v2, kv, now, cw, queue)
#         else:
        fan_a = replace_kvertex(a, v2, kv, now, cw, queue)
    #
    if b is not None:
        logging.debug("replacing vertex for neighbour B")
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        # fan_b
#         if inf_fast:
#             fan_b = replace_inffast_kvertex(b, v1, kv, now, ccw, queue)
#         else:
        fan_b = replace_kvertex(b, v1, kv, now, ccw, queue)
    #
    if n is not None:
        n.neighbours[n.neighbours.index(t)] = None
        if n.event is not None and n.stops_at is None:
            schedule_immediately(n, now, queue, immediate)
    # we "remove" the triangle itself
    t.stops_at = now
    # process parallel fan
    if kv.inf_fast:
        # raise NotImplementedError("parallel unhandled")
        fan = list(reversed(fan_a))
        fan.extend(fan_b)
        dispatch_parallel_fan(fan, kv, now, skel, queue)


def handle_edge_event_3sides(evt, skel, queue, immediate):
    """Handle a collapse of a triangle with 3 sides collapsing.
    It does not matter whether the 3-triangle has wavefront edges or not.

    The following steps are performed:
    - stop the 3 kinetic vertices of the triangle
    - optionally make a new skeleton node
    - schedule all neighbours for immediate processing
    """
    # FIXME: can we have new parallel events here???
    now = evt.time
    t = evt.triangle
    logging.debug(evt.side)
    assert len(evt.side) == 3
    # e = evt.side[0]
    # stop 3 vertices, not making a new kinetic vertex
    sk_node, newly_made = stop_kvertices(t.vertices, now)
    # update circ ????
    if newly_made:
        skel.sk_nodes.append(sk_node)
    # get neighbours around collapsing triangle
    for n in t.neighbours:
        if n is not None and n.event is not None and n.stops_at is None:
            n.neighbours[n.neighbours.index(t)] = None
            schedule_immediately(n, now, queue, immediate)
    # we "remove" the triangle itself
    t.stops_at = now


def schedule_immediately(tri, now, queue, immediate):
    """Schedule a triangle for immediate processing

    Computes a new event for the triangle, where we only check
    how the triangle collapses (look at side lengths at time=now);
    it is assumed that the triangle collapses (neighbor relations say so)!

    The original event is removed from the event queue and the new
    event is added to the immediate queue.
    """
    # remove from global queue
    queue.discard(tri.event)
    # compute new event and put in immediate queue
    E = compute_collapse_time_at_T(tri, now)
    tri.event = E
    # if we have no neighbors around, then no matter what, all 3 sides will
    # collapse (overrides what is determined by compute_collapse_time_at_T)
    if tri.neighbours.count(None) == 3:
        tri.event.side = range(3)
    immediate.append(tri.event)


# ------------------------------------------------------------------------------
# Split event handler
def handle_split_event(evt, skel, queue, immediate):
    """Handles a split event where a wavefront edge is hit on its interior
    This splits the wavefront in two pieces
    """
    t = evt.triangle
    assert len(evt.side) == 1
    e = evt.side[0]
    now = evt.time
    v = t.vertices[(e) % 3]
    n = t.neighbours[e]
    assert n is None
    v1 = t.vertices[(e + 1) % 3]
    v2 = t.vertices[(e + 2) % 3]
    sk_node, newly_made = stop_kvertices([v], now)
    # add the skeleton node to the skeleton
    if newly_made:
        skel.sk_nodes.append(sk_node)
#     assert v1.right is v2
#     assert v2.left is v1
    vb, newly_made = compute_new_kvertex(v.ul, v2.ul, now, sk_node)
    if newly_made:
        skel.vertices.append(vb)
    va, newly_made = compute_new_kvertex(v1.ur, v.ur, now, sk_node)
    if newly_made:
        skel.vertices.append(va)
    update_circ(v.left, vb, now)
    update_circ(vb, v2, now)
    update_circ(v1, va, now)
    update_circ(va, v.right, now)
    # updates (triangle fan) at neighbour 1
    b = t.neighbours[(e + 1) % 3]
    b.neighbours[b.neighbours.index(t)] = None
    fan_b = replace_kvertex(b, v, vb, now, ccw, queue)
    # updates (triangle fan) at neighbour 2
    a = t.neighbours[(e + 2) % 3]
    a.neighbours[a.neighbours.index(t)] = None
    fan_a = replace_kvertex(a, v, va, now, cw, queue)
#     # we "remove" the triangle itself
    t.stops_at = now
    # handle infinitely fast vertices
    if va.inf_fast:
        dispatch_parallel_fan(fan_a, va, now, skel, queue)
    if vb.inf_fast:
        dispatch_parallel_fan(fan_b, vb, now, skel, queue)

# ------------------------------------------------------------------------------
# Flip


def handle_flip_event(evt, skel, queue):
    """Take the two triangles that need to be flipped, flip them and replace
    their time in the event queue
    """
    now = evt.time
    assert len(evt.side) == 1
    t, t_side = evt.triangle, evt.side[0]
    n = t.neighbours[t_side]
    assert n is not None
    n_side = n.neighbours.index(t)
    flip(t, t_side, n, n_side)
    replace_in_queue(t, now, queue)
    replace_in_queue(n, now, queue)
    logging.debug("flip event handled")


def flip(t0, side0, t1, side1):
    """Performs a flip of triangle t0 and t1

    If t0 and t1 are two triangles sharing a common edge AB,
    the method replaces ABC and BAD triangles by DCA and DBC, respectively.

    Pre-condition: input triangles share a common edge and this edge is known.
    """
    apex0, orig0, dest0 = apex(side0), orig(side0), dest(side0)
    apex1, orig1, dest1 = apex(side1), orig(side1), dest(side1)
    # side0 and side1 should be same edge
    assert t0.vertices[orig0] is t1.vertices[dest1]
    assert t0.vertices[dest0] is t1.vertices[orig1]
    # assert both triangles have this edge unconstrained
    assert t0.neighbours[apex0] is not None
    assert t1.neighbours[apex1] is not None
    # -- vertices around quadrilateral in ccw order starting at apex of t0
    A, B, C, D = t0.vertices[apex0], t0.vertices[
        orig0], t1.vertices[apex1], t0.vertices[dest0]
    # -- triangles around quadrilateral in ccw order, starting at A
    AB, BC, CD, DA = t0.neighbours[dest0], t1.neighbours[
        orig1], t1.neighbours[dest1], t0.neighbours[orig0]
    # link neighbours around quadrilateral to triangles as after the flip
    # -- the sides of the triangles around are stored in apex_around
    apex_around = []
    for neighbour, corner in zip([AB, BC, CD, DA],
                                 [A, B, C, D]):
        if neighbour is None:
            apex_around.append(None)
        else:
            apex_around.append(ccw(neighbour.vertices.index(corner)))
    # the triangles around we link to the correct triangle *after* the flip
    for neighbour, side, t in zip([AB, BC, CD, DA],
                                  apex_around,
                                  [t0, t0, t1, t1]):
        if neighbour is not None:
            neighbour.neighbours[side] = t
    # -- set new vertices and neighbours
    # for t0
    t0.vertices = [A, B, C]
    t0.neighbours = [BC, t1, AB]
    # for t1
    t1.vertices = [C, D, A]
    t1.neighbours = [DA, t0, CD]


# Parallel
# -----------------------------------------------------------------------------
def dispatch_parallel_fan(fan, pivot, now, skel, queue):
    """Dispatches to correct function for handling parallel wavefronts"""
    logging.debug(" -------- dispatching parallel event --------")
    if len(fan) == 1:
        t = fan[0]
        if t.neighbours.count(None) == 3:
            handle_parallel_3sides(fan, pivot, now, skel)
        else:
            logging.debug("Number of 'None' neighbours {}".format(
                                                  t.neighbours.count(None)))
            handle_parallel_2sides(fan, pivot, now, skel, queue)
    else:
        raise NotImplementedError("Fan with multiple triangles, not yet there")


def handle_parallel_2sides(fan, pivot, now, skel, queue):
    """Handle parallel fan, 2 sides are wavefront, one is not"""
    assert len(fan) == 1
    t = fan[0]
    neighbours = map(lambda x: x is None, t.neighbours)
    pivot_idx = t.vertices.index(pivot)
    assert neighbours[pivot_idx] is False
    cw_idx = cw(pivot_idx)
    ccw_idx = ccw(pivot_idx)
    assert t.neighbours[cw_idx] is None
    assert t.neighbours[ccw_idx] is None
    left_wavefront = Edge(t, ccw_idx)
    right_wavefront = Edge(t, cw_idx)
    right_dist = dist(*map(lambda x: x.position_at(now),
                           right_wavefront.segment))
    left_dist = dist(*map(lambda x: x.position_at(now),
                          left_wavefront.segment))
    dists = [left_dist, right_dist]
    unique_dists = [near_zero(_ - max(dists)) for _ in dists]
    logging.debug(unique_dists)
    unique_max_dists = unique_dists.count(True)
    if unique_max_dists == 2:
        raise NotImplementedError("not there yet -- fan with equal sized legs")
    else:
        logging.debug(unique_dists)
        longest_idx = unique_dists.index(True)
        assert longest_idx >= 0
        if longest_idx == 0:
            logging.debug("CW / left wavefront at pivot is longest")
            v = t.vertices.index(pivot)
            logging.debug(
                "wavefront edge collapsing? {0}".format(
                                                    t.neighbours[v] is None))
            v1 = t.vertices[(v + 1) % 3]
            v2 = t.vertices[(v + 2) % 3]
            # get neighbours around collapsing triangle
            a = t.neighbours[(v + 1) % 3]
            b = t.neighbours[(v + 2) % 3]
            n = t.neighbours[v]
            assert a is None
            assert b is None
            assert n is not None
            # stop the two vertices
            sk_node, newly_made = stop_kvertices([v1], now)
            if newly_made:
                skel.sk_nodes.append(sk_node)
            # make the connection
            # let the infinite vertex stop in the newly created skeleton node
            pivot.stop_node = sk_node
            pivot.stops_at = now
            update_circ(pivot, None, now)
            update_circ(None, pivot, now)
            t.stops_at = now
            kv, newly_made = compute_new_kvertex(v2.ur, v1.ur, now, sk_node)
            if newly_made:
                skel.vertices.append(kv)
            fan = replace_kvertex(n, v1, kv, now, cw, queue)
            update_circ(v2, kv, now)
            update_circ(kv, v1.right, now)
            n_idx = n.neighbours.index(t)
            n.neighbours[n_idx] = None
        else:
            logging.debug("CCW / right wavefront at pivot is longest")
            #raise NotImplementedError("handle ccw here")
            v = t.vertices.index(pivot)
            logging.debug(
                "wavefront edge collapsing? {0}".format(
                                                    t.neighbours[v] is None))
            v1 = t.vertices[(v + 1) % 3]
            v2 = t.vertices[(v + 2) % 3]
            # get neighbours around collapsing triangle
            a = t.neighbours[(v + 1) % 3]
            b = t.neighbours[(v + 2) % 3]
            n = t.neighbours[v]
            assert a is None
            assert b is None
            assert n is not None
            # stop the two vertices
            sk_node, newly_made = stop_kvertices([v2], now)
            if newly_made:
                skel.sk_nodes.append(sk_node)
            # make the connection
            # let the infinite vertex stop in the newly created skeleton node
            pivot.stop_node = sk_node
            pivot.stops_at = now
            update_circ(pivot, None, now)
            update_circ(None, pivot, now)
            t.stops_at = now
            kv, newly_made = compute_new_kvertex(v2.ul, v1.ul, now, sk_node)
            if newly_made:
                skel.vertices.append(kv)
            fan = replace_kvertex(n, v2, kv, now, ccw, queue)
            update_circ(v2.left, kv, now)
            update_circ(kv, v1, now)
            n_idx = n.neighbours.index(t)
            n.neighbours[n_idx] = None


def handle_parallel_3sides(fan, pivot, now, skel):
    """Handle end of parallel fan, all 3 sides are wavefront"""
    assert len(fan) == 1
    t = fan[0]
    # take edge e
    e = t.vertices.index(pivot)
    logging.debug(
        "wavefront edge collapsing? {0}".format(t.neighbours[e] is None))
    v1 = t.vertices[(e + 1) % 3]
    v2 = t.vertices[(e + 2) % 3]
    # get neighbours around collapsing triangle
    a = t.neighbours[(e + 1) % 3]
    b = t.neighbours[(e + 2) % 3]
    n = t.neighbours[e]
    assert a is None
    assert b is None
    assert n is None
    # stop the two vertices
    sk_node, newly_made = stop_kvertices([v1, v2], now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    # make the connection
    # let the infinite vertex stop in the newly created skeleton node
    pivot.stop_node = sk_node
    pivot.stops_at = now
    t.stops_at = now


# Main event loop
# -----------------------------------------------------------------------------
def event_loop(queue, skel, pause=False):
    """ The main event loop """
    # -- clean out files for visualization
    for file_nm in [
        "/tmp/sknodes_progress.wkt",
        "/tmp/bisectors_progress.wkt",
        "/tmp/segments_progress.wkt",
        '/tmp/queue.wkt',
        # also contains next triangle to be visualised!
        "/tmp/vertices0_progress.wkt",
        "/tmp/vertices1_progress.wkt",
        '/tmp/ktri_progress.wkt',
    ]:
        with open(file_nm, 'w') as fh:
            pass
    # -- visualize
    NOW = prev_time = 1e-5 #5e-2
    if pause:
        visualize(queue, skel, prev_time)
        raw_input('paused at start')
    immediate = deque([])
    logging.debug("=" * 80)
    logging.debug("Immediate / Queue at start of process")
    logging.debug("=" * 80)
    for i, e in enumerate(immediate):
        logging.debug("{0:5d} {1}".format(i, e))
    logging.debug("-" * 80)
    for i, e in enumerate(queue):
        logging.debug("{0:5d} {1}".format(i, e))
    logging.debug("=" * 80)
    ct = 0
#     step = prev = 0.025
#     FILTER_CT = 220
    while queue or immediate:
#         if len(queue) < FILTER_CT:
#             pause = True
        ct += 1
#         if parallel:
#             evt = parallel.popleft()
#             # print edge, direction, now
#             handle_parallel_event(evt, skel, queue, immediate, parallel)
#             visualize(queue, skel, now)
#             raise NotImplementedError("stop here")
#         else:
        if immediate:
            evt = immediate.popleft()
        else:
            peek = next(iter(queue))
            NOW = peek.time
            if pause and False:  # visualize progressively
                #                 if peek.tp == "flip":
                #                     ct = 2
                #                 else:
                ct = 10
                # -- use this for getting progress visualization
                delta = NOW - prev_time
                if near_zero(delta):
                    ct = 1
                step_time = delta / ct
                for i in range(ct - 1):  # ct - 2): # stop 1 step before
                    print "."
                    prev_time += step_time
                    visualize(queue, skel, prev_time + step_time)
                    sleep(0.5)
            if pause and False:  # and (ct % 10) == 0:
                visualize(queue, skel, NOW)
                # import random
                # with open("/tmp/signal", "w") as fh:
                #    fh.write("{}".format(random.randint(0,1000)))
                os.system("touch /tmp/signal")
                sleep(2.)
#             if NOW > prev:
#                 visualize(queue, skel, NOW)
#                 prev += step
            evt = queue.popleft()
            prev_time = NOW
        if pause:
            visualize(queue, skel, NOW)
        # -- decide what to do based on event type
        logging.debug("Handling event " +
                      str(evt.tp) +
                      " " +
                      str(evt.triangle.type) +
                      " " +
                      str(id(evt.triangle)) +
                      " at time " +
                      "{0:.28g}".format(evt.time))
        # precondition: this triangle has not yet been dealt with before
        assert evt.triangle.stops_at is None
        if evt.tp == "edge":
            if len(evt.side) == 3:
                handle_edge_event_3sides(evt, skel, queue, immediate)
            else:
                handle_edge_event(evt, skel, queue, immediate)
        elif evt.tp == "flip":
            handle_flip_event(evt, skel, queue)
        elif evt.tp == "split":
            handle_split_event(evt, skel, queue, immediate)

#         check_ktriangles(skel.triangles, NOW)
        if pause:
            visualize(queue, skel, NOW)

        if True:  # len(queue) < FILTER_CT:
            logging.debug("=" * 80)
            logging.debug("Immediate / Queue at end of handling event")
            logging.debug("=" * 80)
            for i, e in enumerate(immediate):
                logging.debug("{0:5d} {1}".format(i, e))
            logging.debug("-" * 80)
            for i, e in enumerate(queue):
                if i > 5 and i < len(queue) - 5:
                    continue
                logging.debug("{0:5d} {1}".format(i, e))
                logging.debug(repr(e.triangle))
                if i == 5 and len(queue) > 5:
                    logging.debug("...")
        logging.debug("=" * 80)
        if pause:
            import random
            with open("/tmp/signal", "w") as fh:
                fh.write("{0}".format(random.randint(0, int(1e6))))
            raw_input("paused...")
#     if pause:
#         for t in range(3):
#             NOW += t
    if pause:
        visualize(queue, skel, NOW)
    return NOW
