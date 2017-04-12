import logging
from tri.delaunay import ccw, cw, Edge
from grassfire.events.lib import stop_kvertices, update_circ, \
    compute_new_kvertex, replace_kvertex

from grassfire.events.check import at_same_location

from grassfire.calc import groupby_cluster, near_zero
from grassfire.primitives import KineticVertex
from grassfire.vectorops import dist

# Parallel
# -----------------------------------------------------------------------------
def dispatch_parallel_fan(fan, pivot, now, skel, queue):
    """Dispatches to correct function for handling parallel wavefronts
    
    fan: list of triangles, sorted counter-clockwise
    """
    logging.debug(" -------- dispatching parallel event --------")
    if len(fan) == 1:
        handle_parallel(fan, pivot, now, skel, queue)
    elif len(fan) > 1:
        # check whether all triangles opposite of the pivot vertex
        # are none, if this is the case, the fan is completely separated
        # from the rest of the triangulation and we should stop all
        # vertices at their current location
        opposing = [tri.neighbours[tri.vertices.index(pivot)] for tri in fan]
        is_closed_fan = all(map(lambda x: x is None, opposing))
        logging.debug(len(fan))
        if is_closed_fan:
            # vertices_to_stop = len(fan) + 2
            # 1 pivot + 1 more on other side of legs than there is triangles
            pos = []
            V = [pivot]
            for i, tri in enumerate(fan):
                idx = tri.vertices.index(pivot)
                if i == 0:
                    V.append(tri.vertices[ccw(idx)])
                    V.append(tri.vertices[ccw(ccw(idx))])
                else:
                    V.append(tri.vertices[ccw(ccw(idx))])
            assert len(fan) + 2 == len(V)
            for v in V:
                pos.append(v.position_at(now))
            stops = groupby_cluster(pos)
            # stop all triangles in the fan
            for tri in fan:
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
            for start_node, stop_node in zip(nodes[:-1], nodes[1:]):
                kv = KineticVertex()
                kv.starts_at = now
                kv.start_node = start_node
                kv.stops_at = now
                kv.stop_node = stop_node
                kv.origin = start_node.pos
                kv.velocity = (0, 0)
                kv.inf_fast = True
                skel.vertices.append(kv)
                update_circ(kv, None, now)
                update_circ(None, kv, now)
            return
        first_tri = fan[0]
        last_tri = fan[-1]
        first_pivot_idx = first_tri.vertices.index(pivot)
        last_pivot_idx = last_tri.vertices.index(pivot)
        last_ccw_idx = ccw(last_pivot_idx)
        first_cw_idx = cw(first_pivot_idx)
#         assert last_tri.neighbours[last_ccw_idx] is None
#         assert first_tri.neighbours[first_cw_idx] is None
        last_wavefront = Edge(last_tri, last_ccw_idx)
        first_wavefront = Edge(first_tri, first_cw_idx)
        last_dist = dist(*map(lambda x: x.position_at(now),
                              last_wavefront.segment))
        first_dist = dist(*map(lambda x: x.position_at(now),
                               first_wavefront.segment))
        dists = [last_dist, first_dist]
        unique_dists = [near_zero(_ - max(dists)) for _ in dists]
        logging.debug(unique_dists)
        unique_max_dists = unique_dists.count(True)
        if unique_max_dists == 2:
            logging.debug("legs are same length")
            raise NotImplementedError("Fan with multiple triangles, not yet there")
        else:
            # visualize(queue, skel, now)
            logging.debug(unique_dists)
            longest_idx = unique_dists.index(True)
            assert longest_idx >= 0
            if longest_idx == 0:
                logging.debug("CW / left wavefront at pivot is longest")
                logging.debug([str(id(_)) for _ in first_tri.neighbours])
                v1 = first_tri.vertices[ccw(first_pivot_idx)]
                v2 = last_tri.vertices[cw(last_pivot_idx)]
                n = first_tri.neighbours[first_pivot_idx]
                sk_node, newly_made = stop_kvertices([v1], now)
                if newly_made:
                    skel.sk_nodes.append(sk_node)
                # make the connection
                # let the infinite vertex stop in the newly created skeleton node
                pivot.stop_node = sk_node
                pivot.stops_at = now
                # FIXME: it is not always true that vertices stopped this way
                # are at the same location (they are close, but because of
                # numerical issues can be on slightly different location
                # assert at_same_location([pivot, sk_node], now)
                update_circ(pivot, None, now)
                update_circ(None, pivot, now)
                for t in fan:
                    t.stops_at = now
                kv = compute_new_kvertex(v2.ur, v1.ur, now, sk_node)
                skel.vertices.append(kv)
                new_fan = replace_kvertex(n, v1, kv, now, cw, queue)
                update_circ(v2, kv, now)
                update_circ(kv, v1.right, now)
                if n is not None:
                    n_idx = n.neighbours.index(first_tri)
                    n.neighbours[n_idx] = None
            else:
                logging.debug("CCW / right wavefront at pivot is longest")
                v1 = first_tri.vertices[ccw(first_pivot_idx)]
                v2 = last_tri.vertices[cw(last_pivot_idx)]
                n = last_tri.neighbours[last_pivot_idx]
                sk_node, newly_made = stop_kvertices([v2], now)
                if newly_made:
                    skel.sk_nodes.append(sk_node)
                # make the connection
                # let the infinite vertex stop in the newly created skeleton node
                pivot.stop_node = sk_node
                pivot.stops_at = now
                # FIXME: it is not always true that vertices stopped this way
                # are at the same location (they are close, but because of
                # numerical issues can be on slightly different location
                # -> see capital_T test case, which *randomly* comes here!
                # assert at_same_location([pivot, sk_node], now)
                update_circ(pivot, None, now)
                update_circ(None, pivot, now)
                for t in fan:
                    t.stops_at = now
                kv = compute_new_kvertex(v2.ul, v1.ul, now, sk_node)
                skel.vertices.append(kv)
                new_fan = replace_kvertex(n, v2, kv, now, ccw, queue)
                update_circ(v2.left, kv, now)
                update_circ(kv, v1, now)
                if n is not None:
                    n_idx = n.neighbours.index(last_tri)
                    n.neighbours[n_idx] = None
            assert not is_closed_fan
        # the newly created vertex again is infinitely fast
        if kv.inf_fast:
            dispatch_parallel_fan(new_fan, kv, now, skel, queue)
    else:
        return


def handle_parallel(fan, pivot, now, skel, queue):
    """Handle parallel fan with 1 triangle in the fan"""
    assert len(fan) == 1, len(fan)
    t = fan[0]
    if t.neighbours.count(None) == 3:
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
        if not pivot.inf_fast: 
            assert at_same_location([pivot, sk_node], now)
        t.stops_at = now
        return
    else:
        pivot_idx = t.vertices.index(pivot)
        neighbours = map(lambda x: x is None, t.neighbours)
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
            assert n is not None
            # stop the two vertices
            sk_node, newly_made = stop_kvertices([v1, v2], now)
            if newly_made:
                skel.sk_nodes.append(sk_node)
            # make the connection
            # let the infinite vertex stop in the newly created skeleton node
            pivot.stop_node = sk_node
            pivot.stops_at = now
            if not pivot.inf_fast: 
                assert at_same_location([pivot, sk_node], now)
            t.stops_at = now
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
                if not pivot.inf_fast: 
                    assert at_same_location([pivot, sk_node], now)
                update_circ(pivot, None, now)
                update_circ(None, pivot, now)
                t.stops_at = now
                kv = compute_new_kvertex(v2.ur, v1.ur, now, sk_node)
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
                # stop the vertex at the end of the shortest leg
                sk_node, newly_made = stop_kvertices([v2], now)
                if newly_made:
                    skel.sk_nodes.append(sk_node)
                # make the connection
                # let the infinite vertex stop in the newly created skeleton node
                pivot.stop_node = sk_node
                pivot.stops_at = now
                if not pivot.inf_fast:
                    assert at_same_location([pivot, sk_node], now)
                update_circ(pivot, None, now)
                update_circ(None, pivot, now)
                t.stops_at = now
                kv = compute_new_kvertex(v2.ul, v1.ul, now, sk_node)
                skel.vertices.append(kv)
                fan = replace_kvertex(n, v2, kv, now, ccw, queue)
                update_circ(v2.left, kv, now)
                update_circ(kv, v1, now)
                n_idx = n.neighbours.index(t)
                n.neighbours[n_idx] = None
            # the newly created vertex again is infinitely fast
            if kv.inf_fast:
                dispatch_parallel_fan(fan, kv, now, skel, queue)
