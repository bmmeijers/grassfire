import logging

from tri.delaunay import cw, ccw

from grassfire.events.lib import stop_kvertices, compute_new_kvertex, \
    update_circ, replace_kvertex, schedule_immediately
from grassfire.events.parallel import dispatch_parallel_fan


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
    kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node)
    logging.debug("new kinetic vertex {}".format(id(kv)))
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
        # fan is ordered counter clockwise
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
