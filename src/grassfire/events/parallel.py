import logging

from tri.delaunay.tds import ccw, cw, Edge

from grassfire.events.lib import stop_kvertices, update_circ, \
    compute_new_kvertex, replace_kvertex, schedule_immediately
from grassfire.events.lib import get_fan
from grassfire.inout import visualize
from grassfire.calc import groupby_cluster, near_zero
from grassfire.primitives import KineticVertex
from grassfire.vectorops import dist


def handle_parallel_edge_event(t, e, pivot, now, skel, queue, immediate):
    """Handles triangle collapse, where exactly 1 edge collapses
    
    One of the vertices of the triangle moves *infinitely* fast.

    There are 3 cases handled:
    
    1.a. triangle with long left leg, short right leg
    1.b. triangle with long right leg, short left leg

    2. triangle with 2 equal sized legs, edge collapsing between

    Cases 1a/1b can lead to new infinitely fast vertices, while
    Case 2 leads to having to process immediately a neighbouring triangle
    """
    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))
    assert pivot.inf_fast

    # vertices, that are not inf fast, need to stop
    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]
    to_stop = []
    for v in [v1, v2]:
        if not v.inf_fast:
            to_stop.append(v)
    # stop the non-infinite vertices
    sk_node, newly_made = stop_kvertices(to_stop, now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    if pivot.stop_node is None:
        assert pivot.stop_node is None
        assert pivot.stops_at is None
        pivot.stop_node = sk_node
        pivot.stops_at = now
        # FIXME: is left/right "None" correct here ???
        update_circ(pivot, None, now)
        update_circ(None, pivot, now)
    else:
        logging.warn("Infinite fast pivot already stopped,"
                     " but should not be stopped(?)")
        # assert not newly_made
        # print(sk_node.pos)
        # print(pivot.position_at(now))
        # assert sk_node.pos == pivot.position_at(now)

    # we "remove" the triangle itself
    t.stops_at = now

    # the edge that collapses is not opposite of the pivot
    # i.e. the edge is one of the two adjacent legs at
    # the pivot
    if t.vertices.index(pivot) != e:
        kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node)
        logging.debug("Computed new kinetic vertex {}".format(id(kv)))
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
        # second check:
        # is vertex infinitely fast?
        def is_infinitely_fast(fan, now):
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
        # in this case, both sides of the new vertex 
        # should collapse to be infinitely fast!
        is_inf_fast_a = is_infinitely_fast(get_fan(a, v2, cw), now)
        is_inf_fast_b = is_infinitely_fast(get_fan(b, v1, ccw), now)
        if is_inf_fast_a and is_inf_fast_b:
            assert kv is not None
            if not kv.inf_fast:
                logging.debug("New kinetic vertex: ***Upgrading*** to infinitely fast moving vertex!")
                kv.inf_fast = True
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
        #
        logging.debug("*** neighbour n: {} ".format("schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else ""))
        if n is not None:
            n.neighbours[n.neighbours.index(t)] = None
            if n.event is not None and n.stops_at is None:
                schedule_immediately(n, now, queue, immediate)

        # visualize(queue, skel, now-1.0e-3)
        # raw_input('continue after parallel')

        # process parallel fan
        if kv and kv.inf_fast:
            if fan_a:
                handle_parallel_fan(fan_a, kv, now, cw, skel, queue, immediate)
            if fan_b:
                handle_parallel_fan(fan_b, kv, now, ccw, skel, queue, immediate)

    else:
        # we are collapsing the edge opposite of the inf fast pivot vertex
        assert t.vertices.index(pivot) == e
        n = t.neighbours[e]
        logging.debug("*** neighbour n: {} ".format("schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else ""))
        if n is not None:
            n.neighbours[n.neighbours.index(t)] = None
            if n.event is not None and n.stops_at is None:
                logging.debug(n.event)
                schedule_immediately(n, now, queue, immediate)

        # visualize(queue, skel, now-1.0e-3)
        # raw_input('continue after parallel')


# Parallel
# -----------------------------------------------------------------------------
def handle_parallel_fan(fan, pivot, now, direction, skel, queue, immediate):
    """Dispatches to correct function for handling parallel wavefronts

    fan: list of triangles, sorted (in *direction* order)
    pivot: the vertex that is going infinitely fast
    now: time at which parallel event happens
    direction: how the fan turns
    skel: skeleton structure
    queue: event queue
    immediate: queue of events that should be dealt with when finished handling
    the current event
    """
    if not fan:
        return

    # visualize(queue, skel, now-5e-2)
    # raw_input('pause @ start of parallel event')

    logging.debug("""
# ---------------------------------------------------------
# -- PARALLEL event handler invoked                      --
# ---------------------------------------------------------
""")

    logging.debug(" -- {}".format(len(fan)))
    logging.debug(" -- triangles in the fan: {}".format([id(_) for _ in fan]))

    assert pivot.inf_fast

    first_tri = fan[0]
    logging.debug('First tri **: {}'.format(id(first_tri)))

    v1 = first_tri.vertices[ccw(first_tri.vertices.index(pivot))] # FIXME: should be a vertex from first_tri!
    v2 = first_tri.vertices[cw(first_tri.vertices.index(pivot))] # FIXME: should be a vertex from first_tri!

    logging.debug(' kvertices:' )
    logging.debug('  v1: {}'.format(id(v1)) )
    logging.debug('  v2: {}'.format(id(v2)) )

    v2_leg = Edge(first_tri, ccw(first_tri.vertices.index(pivot)))
    v1_leg = Edge(first_tri, cw(first_tri.vertices.index(pivot)))

    v2_dist = dist(*map(lambda x: x.position_at(now),
                          v2_leg.segment))
    v1_dist = dist(*map(lambda x: x.position_at(now),
                           v1_leg.segment))
    dists = [v1_dist, v2_dist]

    logging.debug('  distances: {}'.format(dists))

    unique_dists = [near_zero(_ - max(dists)) for _ in dists]
    logging.debug(unique_dists)
    unique_max_dists = unique_dists.count(True)
    longest_idx = unique_dists.index(True)
    # raw_input(' just before handling parallel event')
    # ----------------------------------------------------------
    # get neighbours around collapsing triangle
    n = first_tri.neighbours[first_tri.vertices.index(pivot)]
    new_direction = None # potentially new fan, how does it turn?
    if unique_max_dists == 2:
        logging.debug("Equal sized legs")
        handle_parallel_edge_event(first_tri, first_tri.vertices.index(pivot), pivot, now, skel, queue, immediate)
    elif longest_idx == 1:
        # left longest
        logging.debug("CW / left wavefront at pivot, ending at v2, is longest")
        handle_parallel_edge_event(first_tri, cw(first_tri.vertices.index(pivot)), pivot,  now, skel, queue, immediate)
    elif longest_idx == 0:
        logging.debug("CCW / right wavefront at pivot, ending at v1, is longest")
        handle_parallel_edge_event(first_tri, ccw(first_tri.vertices.index(pivot)), pivot,  now, skel, queue, immediate)

