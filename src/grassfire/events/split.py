from tri.delaunay import cw, ccw

from grassfire.events.lib import stop_kvertices, compute_new_kvertex, \
    update_circ, replace_kvertex
from grassfire.events.parallel import handle_parallel_fan


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
    vb = compute_new_kvertex(v.ul, v2.ul, now, sk_node)
    skel.vertices.append(vb)
    va = compute_new_kvertex(v1.ur, v.ur, now, sk_node)
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
        handle_parallel_fan(fan_a, va, now, skel, queue)
    if vb.inf_fast:
        handle_parallel_fan(fan_b, vb, now, skel, queue)
