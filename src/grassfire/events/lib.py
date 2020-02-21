import logging

from grassfire.primitives import SkeletonNode, KineticVertex

from grassfire.collapse import compute_collapse_time, \
    compute_new_edge_collapse_event
from grassfire.calc import near_zero
from grassfire.vectorops import mul, add, bisector


# ------------------------------------------------------------------------------
# Functions common for event handling


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
    # at more or less the same location
#     assert at_same_location(V, now)
    sk_node = None

    logging.debug("stopping kinetic vertices:")
    for v in V:
        logging.debug(" - kv #{} [{}]".format(id(v), v.info))

    for v in V:
        stopped = v.stops_at is not None
        time_close = near_zero(v.starts_at - now)
        logging.debug("Vertex starts at same time as now: {}".format(time_close))
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
            v.stops_at = now
            # FIXME: it is not always true that vertices stopped this way
            # are at the same location (they are close, but because of
            # numerical issues can be on slightly different location
            # assert at_same_location([v, sk_node], now)
        is_new_node = False
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
        is_new_node = True
    # post condition
    # all vertices do have a stop node and are stopped at a certain time
    for v in V:
        assert v.stop_node is not None
        assert v.stops_at == now
        # FIXME:
        # should all segments in the skeleton have length
        # or do we keep a topological tree of events (where nodes
        # can be embedded at same location) ???
        # assert not at_same_location([v.start_node, v.stop_node], now), "stopped nodes should be different, but are not for {0}".format(id(v))
    return sk_node, is_new_node


def compute_new_kvertex(ul, ur, now, sk_node, info):
    """Based on the two wavefront directions and time t=now, compute the
    velocity and position at t=0 and return a new kinetic vertex

    Returns: KineticVertex
    """
    kv = KineticVertex()
    kv.info = info
    kv.starts_at = now
    kv.start_node = sk_node

    logging.debug('bisector calc')
    logging.debug(' ul: {}'.format(ul))
    logging.debug(' ur: {}'.format(ur))
    logging.debug(' sk_node.pos: {}'.format(sk_node.pos))
    kv.velocity = bisector(ul, ur)
    logging.debug(' kv.velocity: {}'.format(kv.velocity))


    # compute where this vertex would have been at time t=0
    # we set this vertex as infinitely fast, if velocity in one of the
    # directions is really high, or when the bisectors of adjacent
    # wavefronts cancel each other out
    if kv.velocity == (0, 0) or abs(kv.velocity[0]) > 500 or abs(kv.velocity[1]) > 500:
        kv.inf_fast = True
        kv.origin = sk_node.pos
    else:
        neg_velo = mul(mul(kv.velocity, -1.0), now)
        pos_at_t0 = add(sk_node.pos, neg_velo)
        kv.origin = pos_at_t0
    kv.ul = ul
    kv.ur = ur
    return kv


def get_fan(t, v, direction):
    """Gets a list of triangles that are the fan of 
    vertex *v*, while turning *direction*, starting at triangle *t*

    This function assumes that the fan is finite (i.e. passes
    a triangle that has as neighbour = None (wavefront))
    """
    fan = []
    start = t
    while t is not None:
        side = t.vertices.index(v)
        fan.append(t)
        t = t.neighbours[direction(side)]
        assert t is not start # prevent infinite loops
    return fan


def replace_kvertex(t, v, newv, now, direction, queue, immediate):
    """Replace kinetic vertex at incident triangles

    Returns fan of triangles that were replaced
    """
    logging.debug("replace_kvertex, start at: {0} [{1}] dir: {2}".format(id(t), t.info, direction))
    fan = []
    while t is not None:
        # assert t.stops_at is None, "{}: {}".format(
        #     id(t), [id(n) for n in t.neighbours])
        logging.debug(" @ {} [{}]".format(id(t), t.info))
        side = t.vertices.index(v)
        fan.append(t)
        t.vertices[side] = newv
        logging.debug(
            "Placed vertex #{} [{}] (inf fast? {}) at side {} of triangle {} [{}]".format(
                # id(newv),
                #repr(newv),
                id(newv),
                newv.info,
                newv.inf_fast, 
                side,
                id(t),
                t.info
                # , repr(t)
                ))
        if newv.inf_fast and t.event is not None:  # infinitely fast
            queue.discard(t.event)
            if t.event in immediate:
                immediate.remove(t.event)
        else:  # vertex moves with normal speed
            replace_in_queue(t, now, queue, immediate)
        t = t.neighbours[direction(side)]
    return tuple(fan)


def replace_in_queue(t, now, queue, immediate):
    """Replace event for a triangle in the queue """
    if t.event is not None:
        queue.discard(t.event)
        if t.event in immediate:
            immediate.remove(t.event)
    else:
        logging.debug(
            "triangle #{0} without event not removed from queue".format(
                id(t)))

    logging.debug(" collapse time computation for: {}".format(str(repr(t)).replace(",",",\n\t")))
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
    #                <-
    # v_left.right o    o v_right.left
    #                ->
    if v_left is not None:
        logging.debug("update_circ at right of #{} [{}] lies #{} [{}]".format(
                                                  id(v_left),
                                                  v_left.info,
                                                  id(v_right),
                                                  v_right.info if v_right is not None else ""))
        v_left.right = v_right, now
    if v_right is not None:
        logging.debug("update_circ at left  of #{} [{}] lies #{} [{}]".format(
                                                  id(v_right),
                                                  v_right.info,
                                                  id(v_left),
                                                  v_left.info if v_left is not None else ""))
        v_right.left = v_left, now


def schedule_immediately(tri, now, queue, immediate):
    """Schedule a triangle for immediate processing

    Computes a new event for the triangle, where we only check
    how the triangle collapses (look at side lengths at time=now);
    it is assumed that the triangle collapses (neighbor relations say so)!

    The original event is removed from the event queue and the new
    event is added to the immediate queue.

    """

    # FIXME: should we not look at just the other side of the triangle?
    # so, make explicit which side of this triangle now collapses?

    # remove from global queue
    queue.discard(tri.event)
    if tri.event in immediate:
        immediate.remove(tri.event)
    # compute new event and put in immediate queue
    E = compute_new_edge_collapse_event(tri, now)
    tri.event = E
    # if we have no neighbors around, then no matter what, all 3 sides will
    # collapse (overrides what is determined by compute_new_edge_collapse_event)
    ### FIXME: bug? disable?
    if tri.neighbours.count(None) == 3:
        tri.event.side = list(range(3))
    ###
    assert len(tri.event.side) > 0
    immediate.append(tri.event)
