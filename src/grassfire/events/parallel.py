import logging
from tri.delaunay import ccw, cw, Edge
from grassfire.events.lib import stop_kvertices, update_circ, \
    compute_new_kvertex, replace_kvertex, schedule_immediately

from grassfire.inout import visualize

from grassfire.calc import groupby_cluster, near_zero
from grassfire.primitives import KineticVertex
from grassfire.vectorops import dist


# Parallel
# -----------------------------------------------------------------------------
def handle_parallel_fan(fan, pivot, now, skel, queue, immediate):
    """Dispatches to correct function for handling parallel wavefronts

    fan: list of triangles, sorted counter-clockwise
    pivot: the vertex that is going infinitely fast
    now: time at which parallel event happens
    skel: skeleton structure
    queue: event queue
    immediate: queue of events that should be dealt with when finished handling
    the current event
    """
    if not fan:
        return
    logging.debug(" -------- handling parallel event --------")
    logging.debug(" -- {}".format(len(fan)))
    assert pivot.inf_fast
    opposing = [_.neighbours[_.vertices.index(pivot)] for _ in fan]
    is_closed_fan = all(map(lambda x: x is None, opposing))
    logging.debug(is_closed_fan)
    last_tri = fan[-1]
    logging.debug('Last tri: {}'.format(id(last_tri)))
    idx = last_tri.vertices.index(pivot)
    cw_idx = cw(idx)
    ccw_idx = ccw(idx)
    # v = last_tri.vertices[idx]
    v1 = last_tri.vertices[ccw_idx]
    v2 = last_tri.vertices[cw_idx]
    left_leg = Edge(last_tri, ccw_idx)
    right_leg = Edge(last_tri, cw_idx)
    left_dist = dist(*map(lambda x: x.position_at(now),
                          left_leg.segment))
    right_dist = dist(*map(lambda x: x.position_at(now),
                           right_leg.segment))
    dists = [left_dist, right_dist]
    unique_dists = [near_zero(_ - max(dists)) for _ in dists]
    logging.debug(unique_dists)
    unique_max_dists = unique_dists.count(True)
    longest_idx = unique_dists.index(True)

    # ----------------------------------------------------------
    if len(fan) > 1:
        pos = []
        V = [pivot]
        for i, tri in enumerate(fan[:-1]):
            tmpidx = tri.vertices.index(pivot)
            # opposite_neighbour = tri.neighbours[tmpidx]
            # print "opposing pivot neighbor", id(opposite_neighbour)
            if i == 0:
                V.append(tri.vertices[cw(tmpidx)])
                V.append(tri.vertices[ccw(tmpidx)])
            else:
                V.append(tri.vertices[ccw(tmpidx)])
        for v in V:
            logging.debug("I will stop kvertex: {}".format(id(v)))
            pos.append(v.position_at(now))
        stops = groupby_cluster(pos)
        # stop all triangles in the fan
        for tri in fan[:-1]:
            tri.stops_at = now
        # create skeleton nodes at the cluster stops
        nodes = []
        for cluster in stops:
            sk_node, newly_made = stop_kvertices([V[i] for i in cluster],
                                                 now)
            if newly_made:
                skel.sk_nodes.append(sk_node)
            nodes.append(sk_node)
        # create infinitely fast vertices between stop nodes
        for i, (start_node, stop_node) in enumerate(zip(nodes[:-1], nodes[1:])):
            if i == 0:
                par_kv = pivot
            else:
                par_kv = KineticVertex()
                par_kv.starts_at = now
                par_kv.start_node = start_node
                par_kv.origin = start_node.pos
                skel.vertices.append(par_kv)
            par_kv.stops_at = now
            par_kv.stop_node = stop_node
            par_kv.velocity = (0, 0)
            par_kv.inf_fast = True
            update_circ(par_kv, None, now)
            update_circ(None, par_kv, now)
    if False:
        visualize(queue, skel, now-5e-2)
        raw_input('Paused halfway during parallel event - incomplete')
    # ----------------------------------------------------------
    # get neighbours around collapsing triangle
    n = last_tri.neighbours[idx]
    if unique_max_dists == 2:
        logging.debug("Equal sized legs")
        # stop the two vertices
        sk_node, newly_made = stop_kvertices([v1, v2], now)
        if newly_made:
            skel.sk_nodes.append(sk_node)
        last_tri.stops_at = now
        # let the infinite fast vertex stop in the newly created skeleton node
        # if it was not yet stopped above (multiple triangles in fan)
        if pivot.stop_node is None:
            pivot.stop_node = sk_node
            pivot.stops_at = now
            update_circ(pivot, None, now)
            update_circ(None, pivot, now)
        if n is not None:
            schedule_immediately(n, now, queue, immediate)
        return
    elif longest_idx == 0:
        # left longest
        logging.debug("CW / left wavefront at pivot is longest")
        # stop the two vertices
        sk_node, newly_made = stop_kvertices([v1], now)
        if newly_made:
            skel.sk_nodes.append(sk_node)
        # let the infinite fast vertex stop in the newly created skeleton node
        # if it was not yet stopped above (multiple triangles in fan)
        if pivot.stop_node is None:
            pivot.stop_node = sk_node
            pivot.stops_at = now
            update_circ(pivot, None, now)
            update_circ(None, pivot, now)
        last_tri.stops_at = now
        kv = compute_new_kvertex(v2.ur, v1.ur, now, sk_node)
        skel.vertices.append(kv)
        fan = replace_kvertex(n, v1, kv, now, cw, queue, immediate)
        update_circ(v2, kv, now)
        update_circ(kv, v1.right, now)
        if n is not None:
            n_idx = n.neighbours.index(last_tri)
            n.neighbours[n_idx] = None
    elif longest_idx == 1:
        logging.debug("CCW / right wavefront at pivot is longest")
        # right longest
        assert longest_idx == 1
        # stop the vertex at the end of the shortest leg
        sk_node, newly_made = stop_kvertices([v2], now)
        if newly_made:
            skel.sk_nodes.append(sk_node)
        # let the infinite fast vertex stop in the newly created skeleton node
        # if it was not yet stopped above (multiple triangles in fan)
        if pivot.stop_node is None:
            pivot.stop_node = sk_node
            pivot.stops_at = now
            update_circ(pivot, None, now)
            update_circ(None, pivot, now)
        last_tri.stops_at = now
        kv = compute_new_kvertex(v2.ul, v1.ul, now, sk_node)
        skel.vertices.append(kv)
        fan = replace_kvertex(n, v2, kv, now, ccw, queue, immediate)
        update_circ(v2.left, kv, now)
        update_circ(kv, v1, now)
        if n is not None:
            n_idx = n.neighbours.index(last_tri)
            n.neighbours[n_idx] = None
    # if the new kinetic vertex is infinitely fast again,
    # process the triangles as infinitely fast
    if kv.inf_fast:
        handle_parallel_fan(fan, kv, now, skel, queue, immediate)
