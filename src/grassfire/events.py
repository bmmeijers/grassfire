import logging

from operator import add, sub
from time import sleep

from tri.delaunay import apex, orig, dest, cw, ccw, Edge
from oseq import OrderedSequence

from grassfire.primitives import SkeletonNode, KineticVertex
from grassfire.calc import bisector, rotate180, vector_mul_scalar, near_zero,\
    length
from grassfire.collapse import compute_collapse_time, find_gt, \
    compute_collapse_time_at_T
from grassfire.inout import output_edges_at_T, output_triangles_at_T
from collections import deque


def compare_event_by_time(one, other):
    """ Compare two events, first by time, in case they are equal
    by triangle type (first 2-triangle, then 1-triangle, then 0-triangle),
    as last resort by identifier of triangle.
    """
    # compare by time
    if one.time < other.time: # lt
        return -1
    elif one.time > other.time: # gt
        return 1
    # in case times are equal, compare by id of triangle
    # to be able to find the correct triangle back
    else: # eq
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
    sk_node = None
    for v in V:
        stopped = v.stops_at is not None
        time_close = near_zero(v.starts_at - now)
        logging.debug("Vertex starts at same time as now: {}".format(time_close))
        logging.debug("Kinetic vertex is not stopped: {}".format(stopped))
        if stopped:
            logging.debug("Stop_node of vertex")
            sk_node = v.stop_node
        elif time_close:
            assert not stopped
            sk_node = v.start_node
#             raise NotImplementedError("this vertex should stay as kv and not stop!")
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
        pos = sumx/ct, sumy/ct
        sk_node = SkeletonNode(pos)
        for v in V:
            v.stop_node = sk_node
        return sk_node, True


def compute_new_kvertex(v1, v2, now, sk_node, V):
    """Based on the two kinetic vertices, time t=now and the skeleton node
    return a new kinetic vertex.
    """
    # if one of the two vertices just recently has been started -> do not
    # make a new kinetic vertex!
    for v in V:
        if near_zero(v.starts_at-now):
            return v, False
    # otherwise make new vertex
    kv = KineticVertex()
    kv.starts_at = now
    kv.start_node = sk_node
    p1 = v1.position_at(now)
    p2 = v2.position_at(now)
    # a side has zero length
    degenerate1 = near_zero(abs(p1[0] - sk_node.pos[0])) and \
                    near_zero(abs(p1[1] - sk_node.pos[1]))
    degenerate2 = near_zero(abs(p2[0] - sk_node.pos[0])) and \
                    near_zero(abs(p2[1] - sk_node.pos[1]))
    degenerate3 = near_zero(abs(p1[0] - p2[0])) and \
                    near_zero(abs(p1[1] - p2[1]))
    # degenerate4 = orient2d(p1, p2, sk_node.pos)

    # if degenerate1 == True or degenerate2 == True
    # then we also have degenerate4 == True
    # p1.sk-------------p2
    # p2.sk-------------p1
    # we do not have a parallel wavefront, per se (although it could)
    # --> rocket test case shows that we have simultaneous collapse
    #     where multiple triangles do collapse at same time

    # if we have:
    # sk-------p1.--.p2 collinear, so: 
    # degenerate1 == False and degenerate2 == False and degenerate4 == True
    # --> we have for sure 2 parallel wavefronts collapsing
    #     3 points are collinear

    if (degenerate1 or degenerate2) and (degenerate1 != degenerate2):
        if degenerate1:
            logging.debug("Updated p1")
            p1 = v1.left.position_at(now)
            assert not (near_zero(abs(p1[0] - sk_node.pos[0])) and \
                        near_zero(abs(p1[1] - sk_node.pos[1])))
#            could be:
#             while (near_zero(abs(p1[0] - sk_node.pos[0])) and \
#                    near_zero(abs(p1[1] - sk_node.pos[1]))):
#                 v1 = v1.left
#                 p1 = v1.position_at(now)
        elif degenerate2:
            logging.debug("Updated p2")
            p2 = v2.right.position_at(now)
            assert not (near_zero(abs(p2[0] - sk_node.pos[0])) and \
                        near_zero(abs(p2[1] - sk_node.pos[1])))
        velo = bisector(p1, sk_node.pos, p2)
        logging.debug("velo vector" + str(velo))
        # compute position at t=0, rotate bisector 180 degrees
        # and get the position 
        negvelo = rotate180(velo)
        pos_at_t0 = (sk_node.pos[0] + negvelo[0] * now,
                     sk_node.pos[1] + negvelo[1] * now)

    elif degenerate1 and degenerate2 and degenerate3: # or degenerate4:
        # 3 sides of triangle formed by the 3 kinetic vertices completely
        # collapsed
        pos_at_t0 = sk_node.pos
        velo = (0., 0.)
        logging.debug("INFINITELY FAST VERTEX")
    else:
        velo = bisector(p1, sk_node.pos, p2)
        # compute position at t=0, rotate bisector 180 degrees
        # and get the position 
        negvelo = rotate180(velo)
        pos_at_t0 = (sk_node.pos[0] + negvelo[0] * now,
                     sk_node.pos[1] + negvelo[1] * now)
    kv.origin = pos_at_t0
    kv.velocity = velo
    assert kv.velocity != (0.,0.)
    return kv, True

def replace_kvertex(t, v, newv, now, direction, queue):
    """Replace kinetic vertex at incident triangles

    Returns fan of triangles that were replaced 
    """
    tris = []
    while t is not None:
        side = t.vertices.index(v)
        tris.append((t, side))
        t.vertices[side] = newv
        logging.debug("Placed vertex {} at side {} of triangle {} <{}>".format(repr(newv), side, id(t), repr(t)))
        replace_in_queue(t, now, queue)
        t = t.neighbours[direction(side)]
    return tuple(tris)

def replace_in_queue(t, now, queue):
    """Replace event for a triangle in the queue """
    if t.event != None:
        queue.discard(t.event)
    else:
        logging.debug("triangle #{0} without event not removed from queue".format(id(t)))
    e = compute_collapse_time(t, now)
    if e is not None:
        logging.debug("new event in queue {}".format(e))
        queue.add(e)
    else:
        logging.debug("no new events".format(e))
        return

def update_circ(kv, v1, v2, now):
    """Update neighbour list of kinetic vertices (this is a circular list going
    around the wavefront edges
    """
    # update circular list:
    #               <-----v2
    #    <----- kv ----->       
    # v1 ---->    
    kv.left = v1, now
    kv.right = v2, now
    #
    v1.right = kv, now
    v2.left = kv, now


# ------------------------------------------------------------------------------
# Edge event handlers
def handle_edge_event(evt, skel, queue, immediate):
    t = evt.triangle
    logging.debug(evt.side)
    assert len(evt.side) == 1
    # take edge e
    e = evt.side[0]
    now = evt.time
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
    # stop the two vertices and make new skeleton node
    sk_node, newly_made = stop_kvertices([v1, v2], now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    # replace 2 vertices with new kinetic vertex
    kv, newly_made = compute_new_kvertex(v1.left, v2.right, now, sk_node, (v1, v2))
    if newly_made:
        skel.vertices.append(kv)
    # update circular list
    update_circ(kv, v1.left, v2.right, now)
    # append to skeleton structure, kinetic vertices
    # get neighbours around collapsing triangle
    a = t.neighbours[(e+1) % 3]
    b = t.neighbours[(e+2) % 3]
    n = t.neighbours[e]
    if a is not None:
        a_idx = a.neighbours.index(t)
        a.neighbours[a_idx] = b
        replace_kvertex(a, v2, kv, now, cw, queue)
    if b is not None:
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        replace_kvertex(b, v1, kv, now, ccw, queue)
    if n is not None:
        n.neighbours[n.neighbours.index(t)] = None
        if n.event != None and n.stops_at == None:
            schedule_immediately(n, now, queue, immediate)
    # we "remove" the triangle itself
    t.stops_at = now


def handle_edge_event_3sides(evt, skel, queue, immediate):
    """Handle a collapse of a triangle with 3 sides collapsing.
    It does not matter whether the 3-triangle has wavefront edges or not.

    The following steps are performed:
    - stop the 3 kinetic vertices of the triangle
    - optionally make a new skeleton node
    - schedule all neighbours for immediate processing
    """
    t = evt.triangle
    logging.debug(evt.side)
    assert len(evt.side) == 3
    # e = evt.side[0]
    now = evt.time
    # stop 3 vertices, not making a new kinetic vertex
    sk_node, newly_made = stop_kvertices(t.vertices, now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    # get neighbours around collapsing triangle
    for n in t.neighbours:
        if n is not None and n.event != None and n.stops_at == None:
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
    immediate.append(tri.event)


# ------------------------------------------------------------------------------
# Split event handler
def handle_split_event(evt, skel, queue):
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
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
    sk_node, newly_made = stop_kvertices([v], now)
    # add the skeleton node to the skeleton
    assert newly_made == True
    skel.sk_nodes.append(sk_node)
    assert v1.right is v2
    assert v2.left is v1
    vb, newly_made = compute_new_kvertex(v.left, v2, now, sk_node, (v1,v2))
    assert newly_made == True
    va, newly_made = compute_new_kvertex(v1, v.right,  now, sk_node, (v1,v2))
    assert newly_made == True
    # add the two kinetic vertices to the skeleton
    skel.vertices.append(va)
    skel.vertices.append(vb)
    # split circular list into 2 lists here
    update_circ(vb, v.left, v2, now)
    update_circ(va, v1, v.right, now)
    # updates (triangle fan) at neighbour 1
    b = t.neighbours[(e+1)%3]
    b.neighbours[b.neighbours.index(t)] = None
    replace_kvertex(b, v, vb, now, ccw, queue)
    # updates (triangle fan) at neighbour 2
    a = t.neighbours[(e+2)%3]
    a.neighbours[a.neighbours.index(t)] = None
    replace_kvertex(a, v, va, now, cw, queue)
    # we "remove" the triangle itself
    t.stops_at = now


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
    A, B, C, D = t0.vertices[apex0], t0.vertices[orig0], t1.vertices[apex1], t0.vertices[dest0]
    # -- triangles around quadrilateral in ccw order, starting at A
    AB, BC, CD, DA = t0.neighbours[dest0], t1.neighbours[orig1], t1.neighbours[dest1], t0.neighbours[orig0]
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


# Main event loop
# -----------------------------------------------------------------------------
def event_loop(queue, skel, pause=False):
    """ The main event loop """
    # -- clean out files for visualization
    for file_nm in [
            "/tmp/sknodes_progress.wkt",
            "/tmp/bisectors_progress.wkt",
            "/tmp/segments_progress.wkt",
            '/tmp/queue.wkt', # also contains next triangle to be visualised!
            "/tmp/vertices0_progress.wkt",
            "/tmp/vertices1_progress.wkt",
            '/tmp/ktri_progress.wkt',
        ]:
        with open(file_nm, 'w') as fh:
            pass
    # -- visualize
    NOW = prev_time = 0.01
    if pause:
        visualize(queue, skel, prev_time)
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
    while queue or immediate:
        if immediate:
            evt = immediate.popleft()
        else:
            peek = next(iter(queue))
            NOW = peek.time
            if pause and False: # visualize progressively
                if peek.tp == "flip":
                    ct = 1
                else:
                    ct = 5
                # -- use this for getting progress visualization
                delta = NOW - prev_time
                if near_zero(delta):
                    ct = 1
                step_time = delta / ct
                for i in range(ct - 2):
                    print "."
                    prev_time += step_time
                    visualize(queue, skel, prev_time + step_time)
                    sleep(1.)
            # visualize(queue, skel, prev_time)
            prev_time = NOW
#             logging.info("=" * 80)
#             for i, e in enumerate(queue):
#                 logging.info("{0:5d} {1}".format(i, e))
#             logging.info("=" * 80)
            evt = queue.popleft()
        # -- decide what to do based on event type
        logging.debug("Handling event " + str(evt.tp) + " " + str(evt.triangle.type) + " " + str(id(evt.triangle)) + " at time " + "{0:.28g}".format(evt.time))
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
            handle_split_event(evt, skel, queue)
#         check_ktriangles(skel.triangles, NOW)
        if pause:
            visualize(queue, skel, NOW)
        logging.debug("=" * 80)
        logging.debug("Immediate / Queue at end of handling event")
        logging.debug("=" * 80)
        for i, e in enumerate(immediate):
            logging.debug("{0:5d} {1}".format(i, e))
        logging.debug("-" * 80)
        for i, e in enumerate(queue):
            logging.debug("{0:5d} {1}".format(i, e))
        logging.debug("=" * 80)
    NOW += 100
    if pause:
        visualize(queue, skel, NOW)
    return NOW


def visualize(queue, skel, NOW):
    """ Visualize progress by writing geometry to WKT files to be viewed with
    QGIS """
    with open('/tmp/queue.wkt', 'w') as fh:
        fh.write("pos;wkt;evttype;evttime;tritype;id;n0;n1;n2;finite\n")
        for i, evt in enumerate(queue):
            fh.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}\n".format(
                    i,
                    evt.triangle.str_at(NOW),
                    evt.tp,
                    evt.time,
                    evt.triangle.type,
                    id(evt.triangle),
                    id(evt.triangle.neighbours[0]),
                    id(evt.triangle.neighbours[1]),
                    id(evt.triangle.neighbours[2]),
                    evt.triangle.is_finite,
                )
            )

    with open('/tmp/ktri_progress.wkt', 'w') as fh:
        output_triangles_at_T(skel.triangles, NOW, fh)

    with open("/tmp/sknodes_progress.wkt", 'w') as fh:
        fh.write("wkt\n")
        for node in skel.sk_nodes:
            fh.write("POINT({0[0]} {0[1]})\n".format(node.pos))

    with open("/tmp/bisectors_progress.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt\n")
        for kvertex in skel.vertices:
            if kvertex.stops_at is None:
                p1 = kvertex.position_at(NOW)
                bi = kvertex.velocity
                bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(p1, map(add, p1, vector_mul_scalar
                                                                                              (bi, 0.1))))
    with open("/tmp/segments_progress.wkt", "w") as fh:
        fh.write("wkt;finished;length\n")
        for kvertex in skel.vertices:
            if kvertex.start_node is not None and kvertex.stop_node is not None:
                start, end = kvertex.start_node.pos, kvertex.stop_node.pos
                fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3}\n".format(start, end, True, length (map(sub, start, end))
                                                                                                           ))
            elif kvertex.start_node is not None and kvertex.stop_node is None:
                start, end = kvertex.start_node.pos, kvertex.position_at(NOW)
                fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3}\n".format(start, end, False, length(map(sub, start, end)) 
                                                                                  ))

    with open("/tmp/vertices1_progress.wkt", 'w') as fh1:
        fh1.write("id;wkt\n")
        for kvertex in skel.vertices:
#             if kvertex.start_node is not None and kvertex.stop_node is not None:
#                 fh0.write("{1};POINT({0[0]} {0[1]})\n".format(kvertex.position_at(kvertex.starts_at), id(kvertex)))
#             else:
            if kvertex.stop_node is None:
                fh1.write("{1};POINT({0[0]} {0[1]})\n".format(kvertex.position_at(NOW), id(kvertex)))

    with open("/tmp/wavefront_edges_progress.wkt", "w") as fh:
        edges = []
        for tri in skel.triangles:
            if tri.stops_at is None:
                sides = []
                for i, ngb in enumerate(tri.neighbours):
                    if ngb is None:
                        sides.append(i)
                for side in sides:
                    edges.append(Edge(tri, side))
        output_edges_at_T(edges, NOW, fh)