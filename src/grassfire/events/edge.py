import logging

from tri.delaunay.tds import cw, ccw

from grassfire.events.lib import stop_kvertices, compute_new_kvertex, \
    update_circ, replace_kvertex, schedule_immediately, near_zero
from grassfire.events.lib import get_fan
from grassfire.events.parallel import handle_parallel_fan


# ------------------------------------------------------------------------------
# Edge event handlers
def handle_edge_event(evt, skel, queue, immediate, pause):
    """Handles triangle collapse, where exactly 1 edge collapses"""
    t = evt.triangle
    logging.debug(evt.side)
    assert len(evt.side) == 1, len(evt.side)
    # take edge e
    e = evt.side[0]
    logging.debug("wavefront edge collapsing? {0}".format(t.neighbours[e] is None))
#    if t.neighbours.count(None) == 2:
#        assert t.neighbours[e] is None
    now = evt.time
    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]
    # stop the two vertices of this edge and make new skeleton node
    # replace 2 vertices with new kinetic vertex
    sk_node, newly_made = stop_kvertices([v1, v2], now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1)
    logging.debug("Computed new kinetic vertex {} [{}]".format(id(kv), kv.info))
    logging.debug("v1 := {} [{}]".format(id(v1), v1.info))
    logging.debug("v2 := {} [{}]".format(id(v2), v2.info))
    logging.debug(kv.position_at(now))
    logging.debug(kv.position_at(now+1))

    if v1.left:
        logging.debug(v1.left.position_at(now))
    else:
        logging.warning("no v1.left")
    if v2.right:
        logging.debug(v2.right.position_at(now))
    else:
        logging.warning("no v2.right")
    if kv.inf_fast:
        logging.debug("New kinetic vertex moves infinitely fast!")
    # append to skeleton structure, new kinetic vertex
    skel.vertices.append(kv)
    # update circular list of kinetic vertices
    update_circ(v1.left, kv, now)
    update_circ(kv, v2.right, now)
    # get neighbours around collapsing triangle
    a = t.neighbours[ccw(e)]
    b = t.neighbours[cw(e)]
    n = t.neighbours[e]
    # second check: is vertex infinitely fast?
    def is_infinitely_fast(fan):
        """Determine whether all triangles in the fan collapse
        at the same time, if so, the vertex needs to be infinitely fast"""
        times = [tri.event.time if tri.event is not None else -1 for tri in fan ]
        logging.debug("edge {}".format(times))
        is_inf_fast = all(map(near_zero, [time - now for time in times]))
        logging.debug("edge {}".format(is_inf_fast))
        if fan and is_inf_fast:
            return True
        else:
            return False
    is_inf_fast_a = is_infinitely_fast(get_fan(a, v2, cw))
    is_inf_fast_b = is_infinitely_fast(get_fan(b, v1, ccw))
    if is_inf_fast_a and is_inf_fast_b:
        if not kv.inf_fast:
            logging.debug("New kinetic vertex: ***Upgrading*** to infinitely fast moving vertex!")
            kv.inf_fast = True
    #
    fan_a = []
    fan_b = []
    if a is not None:
        logging.debug("replacing vertex for neighbours at side A")
        a_idx = a.neighbours.index(t)
        a.neighbours[a_idx] = b
        fan_a = replace_kvertex(a, v2, kv, now, cw, queue, immediate)
    if b is not None:
        logging.debug("replacing vertex for neighbours at side B")
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        fan_b = replace_kvertex(b, v1, kv, now, ccw, queue, immediate)
    
    if n is not None:
        logging.debug("*** neighbour n: schedule adjacent neighbour for *IMMEDIATE* processing")
        n.neighbours[n.neighbours.index(t)] = None
        if n.event is not None and n.stops_at is None:
            schedule_immediately(n, now, queue, immediate)

#    if t.info == 134:
#        raise NotImplementedError('problem: #134 exists now')

    # we "remove" the triangle itself
    t.stops_at = now

    # process parallel fan
    if kv.inf_fast:
        if fan_a:
            handle_parallel_fan(fan_a, kv, now, cw, skel, queue, immediate, pause)
        if fan_b:
            handle_parallel_fan(fan_b, kv, now, ccw, skel, queue, immediate, pause)


def handle_edge_event_3sides(evt, skel, queue, immediate):
    """Handle a collapse of a triangle with 3 sides collapsing.
    It does not matter whether the 3-triangle has wavefront edges or not.

    Important: The triangle vertices should collapse to 1 point.

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
    # FIXME: this method stops the vertices always at the same geometric location
    # This means that the triangle collapse leads to 1 point
    # HOWEVER, 3-triangles can also collapse to a segment (2 points)
    # In this case, this handler should *not* be used (but is at the moment, 2019-09-16)
    sk_node, newly_made = stop_kvertices(t.vertices, now)
    # update circ ????
    if newly_made:
        skel.sk_nodes.append(sk_node)

    # def tmp():
    #     print(now, [n.event.time for n in t.neighbours if n is not None and n.event is not None and n.stops_at is None])
    #     times = [tri.event.time for tri in t.neighbours if tri is not None and tri.event is not None]
    #     print("edge3", times)
    #     if any(map(near_zero, [time - now for time in times])):
    #         print("*************************************************")
    #         print("* i am close to zero!!!!                        *")
    #         print("*************************************************")
    # tmp()

    # get neighbours around collapsing triangle
    for n in t.neighbours:
        if n is not None and n.event is not None and n.stops_at is None:
            n.neighbours[n.neighbours.index(t)] = None
            schedule_immediately(n, now, queue, immediate)

    # we "remove" the triangle itself
    t.stops_at = now
