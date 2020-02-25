import logging
from tri.delaunay.tds import cw, ccw

from grassfire.events.lib import stop_kvertices, compute_new_kvertex, \
        update_circ, replace_kvertex, near_zero
from grassfire.events.parallel import handle_parallel_fan
from grassfire.events.lib import get_fan


# ------------------------------------------------------------------------------
# Split event handler
def handle_split_event(evt, skel, queue, immediate):
    """Handles a split event where a wavefront edge is hit on its interior
    This splits the wavefront in two pieces
    """
    t = evt.triangle
    logging.debug("{}".format(t.neighbours))
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
    vb = compute_new_kvertex(v.ul, v2.ul, now, sk_node, len(skel.vertices) + 1)
    skel.vertices.append(vb)
    va = compute_new_kvertex(v1.ur, v.ur, now, sk_node, len(skel.vertices) + 1)
    skel.vertices.append(va)

    logging.debug("-- update circular list at B-side: {} [{}]".format(id(vb), vb.info))
    update_circ(v.left, vb, now)
    update_circ(vb, v2, now)
    logging.debug("-- update circular list at A-side: {} [{}]".format(id(va), va.info))
    update_circ(v1, va, now)
    update_circ(va, v.right, now)
    # updates (triangle fan) at neighbour 1
    b = t.neighbours[(e + 1) % 3]
    assert b is not None
    b.neighbours[b.neighbours.index(t)] = None

    def is_infinitely_fast(fan):
        times = [tri.event.time if tri.event is not None else -1 for tri in fan]
        is_inf_fast = all(map(near_zero, [time - now for time in times]))
        if fan and is_inf_fast:
            return True
        else:
            return False
    is_inf_fast_b = is_infinitely_fast(get_fan(b, v, ccw))

    fan_b = replace_kvertex(b, v, vb, now, ccw, queue, immediate)
    # updates (triangle fan) at neighbour 2
    a = t.neighbours[(e + 2) % 3]
    assert a is not None
    a.neighbours[a.neighbours.index(t)] = None

    is_inf_fast_a = is_infinitely_fast(get_fan(a, v, cw))

    fan_a = replace_kvertex(a, v, va, now, cw, queue, immediate)
#     # we "remove" the triangle itself
    t.stops_at = now

    # double check: infinitely fast vertices
    # (might have been missed by adding wavefront vectors cancelling out)
    if is_inf_fast_a and not va.inf_fast:
        logging.debug("New kinetic vertex vA: ***Upgrading*** to infinitely fast moving vertex!")
        va.inf_fast = True
    if is_inf_fast_b and not vb.inf_fast:
        logging.debug("New kinetic vertex vB: ***Upgrading*** to infinitely fast moving vertex!")
        vb.inf_fast = True

    # handle infinitely fast vertices
    if va.inf_fast:
        handle_parallel_fan(fan_a, va, now, cw, skel, queue, immediate)
    if vb.inf_fast:
        handle_parallel_fan(fan_b, vb, now, ccw, skel, queue, immediate)
