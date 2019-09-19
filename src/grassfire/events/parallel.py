import logging

from tri.delaunay.tds import ccw, cw, Edge

from grassfire.events.lib import stop_kvertices, update_circ, \
    compute_new_kvertex, replace_kvertex, schedule_immediately
from grassfire.inout import visualize
from grassfire.calc import groupby_cluster, near_zero
from grassfire.primitives import KineticVertex
from grassfire.vectorops import dist


# Parallel
# -----------------------------------------------------------------------------
def handle_parallel_fan(fan, pivot, now, direction, skel, queue, immediate):
    """Dispatches to correct function for handling parallel wavefronts

    fan: list of triangles, sorted counter-clockwise
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

    logging.debug("""
# ---------------------------------------------------------
# -- PARALLEL event handler invoked                      --
# ---------------------------------------------------------
""")
    logging.debug(" -- {}".format(len(fan)))
    logging.debug(" -- triangles in the fan: {}".format([id(_) for _ in fan]))
    assert pivot.inf_fast
    opposing = [_.neighbours[_.vertices.index(pivot)] for _ in fan]
    is_closed_fan = all(map(lambda x: x is None, opposing))
    logging.debug('is closed fan: {}'.format(is_closed_fan))
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

    # stop all triangles in the fan
    for tri in fan:
        tri.stops_at = now 

    # ---------------------------------------------------------
    if len(fan) > 1:
        #
        # when there is multiple triangles in the fan:
        #
        # Get all intermediate kinetic vertices (not being v1 and v2 at end of the fan)
        # these vertices should be stopped in skeleton nodes and
        # connected to each other, by adding additional kinetic vertices, going
        # from the first, to the second, from the second to the third, etc.
        # [pivot] o----->{}----->{}----->o [v1,v2]
        #
        # For this, the following steps are executed:
        # - get the vertices at the side of the fan
        # - get a position for each kinetic vertex at time t=now
        #   -> check when we cluster them, 
        #      this leads to the same number as we have vertices
        # - make sure that we 'connect' the new kinetic vertices correctly
        #   (without overlap from pivot to v1/v2)
        #
        # post condition: the pivot vertex is at the end of the fan
        #
        if False:
            visualize(queue, skel, now-5e-3)

        V = []

        # make sure the vertices are correctly ordered along boundary
        # of the fan (this depends on how this fan was obtained:
        # either turning clockwise, or counter-clockwise)
        if direction is cw:
            dir1, dir2 = cw, ccw
        elif direction is ccw:
            dir2, dir1 = cw, ccw

        for i, tri in enumerate(fan[:-1]):
            logging.debug("at tri #{}".format(id(tri)))
            tmpidx = tri.vertices.index(pivot)
            if i == 0:
                V.append(tri.vertices[dir1(tmpidx)])
                logging.debug("{}".format(id(V[-1])))
            else:
                V.append(tri.vertices[dir1(tmpidx)])
                logging.debug("{}".format(id(V[-1])))
        logging.debug("***---*** vertices")
        for v in V:
            logging.debug(id(v))
        logging.debug("***---*** vertices")
        logging.debug(">> v1: {}".format(id(v1)))
        logging.debug(">> v2: {}".format(id(v2)))
        ## by looking at the geometric embedding,
        ## make sure we have all unique positions 
        positions = [v.position_at(now) for v in V]
        stops = groupby_cluster(positions)
        assert len(positions) == len(stops)
        # make a connection between the kinetic vertices
        # while stopping them
        V.reverse()
        while V:
            kv = V.pop()
            logging.debug("stopping: {} & {}".format(id(pivot), id(kv)))
            sk_node, newly_made = stop_kvertices([kv], now)
            if newly_made:
                skel.sk_nodes.append(sk_node)
            pivot.stop_node = sk_node
            pivot.stops_at = now
            update_circ(pivot, None, now)
            update_circ(None, pivot, now)
            # make a new pivot vertex 
            # that moves to the next vertex
            pivot = KineticVertex()
            pivot.starts_at = now
            pivot.start_node = sk_node
            pivot.velocity = (0, 0)
            pivot.inf_fast = True
            skel.vertices.append(pivot)

    # ----------------------------------------------------------
    # get neighbours around collapsing triangle
    n = last_tri.neighbours[idx]
    new_direction = None # potentially new fan, how does it turn?
    if unique_max_dists == 2:
        logging.debug("Equal sized legs")
        # stop the two vertices
        sk_node, newly_made = stop_kvertices([v1, v2], now)
        if newly_made:
            skel.sk_nodes.append(sk_node)
        last_tri.stops_at = now
        # let the infinite fast vertex stop in the newly created skeleton node
        # FIXME: not okay with multiple triangles in fan ... 
        # assert pivot.stop_node is None
        # assert pivot.stops_at is None
        pivot.stop_node = sk_node
        pivot.stops_at = now
        update_circ(pivot, None, now)
        update_circ(None, pivot, now)
        if not is_closed_fan:
            assert n is not None
            # kv = compute_new_kvertex(v2.ul, v1.ur, now, sk_node)
            # skel.vertices.append(kv)
            logging.debug("scheduling neighbour #{} for immediate processing ".format(id(n)))
            
            side = n.neighbours.index(last_tri)
            n.neighbours[side] = None
            # collapse_neighbour(n, side, now, skel, queue, immediate)
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
        # *Important:*
        # replace_kvertex should go after updating the neighbors
        # (as event that is determined looks at how many constrained
        # neighbors there are)
        if n is not None:
            n_idx = n.neighbours.index(last_tri)
            n.neighbours[n_idx] = None
        fan = replace_kvertex(n, v1, kv, now, cw, queue, immediate)
        new_direction = cw
        update_circ(v2, kv, now)
        update_circ(kv, v1.right, now)
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
        # *Important:*
        # replace_kvertex should go after updating the neighbors
        # (as event that is determined looks at how many constrained
        # neighbors there are)
        if n is not None:
            n_idx = n.neighbours.index(last_tri)
            n.neighbours[n_idx] = None
        fan = replace_kvertex(n, v2, kv, now, ccw, queue, immediate)
        new_direction = ccw
        update_circ(v2.left, kv, now)
        update_circ(kv, v1, now)
    # if the new kinetic vertex is infinitely fast again,
    # process the triangles as infinitely fast

    # FIXME: should we get this also from the times of the triangles
    # like in the edge and split handler!
    if kv.inf_fast:
        handle_parallel_fan(fan, kv, now, new_direction, skel, queue, immediate)
