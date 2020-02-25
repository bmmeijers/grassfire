import logging

from tri.delaunay.tds import ccw, cw, Edge

from grassfire.events.lib import stop_kvertices, update_circ, \
    compute_new_kvertex, replace_kvertex, schedule_immediately
from grassfire.events.lib import get_fan
from grassfire.inout import visualize
from grassfire.calc import groupby_cluster, near_zero
from grassfire.primitives import KineticVertex
from grassfire.vectorops import dist

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


#LEFT_CCW = 0
#RIGHT_CW = 1


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

    logging.debug("""
# ---------------------------------------------------------
# -- PARALLEL event handler invoked                      --
# ---------------------------------------------------------
""")

#    visualize(queue, skel, now - 0.0005)
#    logging.debug(" -- {}".format(len(fan)))
#    logging.debug("    triangles in the fan: {}".format([(id(_), _.info) for _ in fan]))
#    logging.debug("    fan turns: {}".format(direction))
#    raw_input('pause @ start of parallel event')

    assert pivot.inf_fast

    first_tri = fan[0]
    last_tri = fan[-1]
    # special case, infinite fast vertex in 1 corner
    # no neighbours (3 wavefront edges)
    # -> let's collapse the edge opposite of the pivot
    if first_tri.neighbours.count(None) == 3:
        # FIXME: does it mean that there will be 1 line segment (2 different vertex locations)
        # can also be that there is two line segments (3 different vertex locations)
        # logging.debug('First tri **: {} is isolated = special case'.format(id(first_tri)))
        handle_parallel_edge_event_even_legs(first_tri, first_tri.vertices.index(pivot), pivot, now, skel, queue, immediate)
        return

    if first_tri is last_tri:
        assert len(fan) == 1

    if direction is cw:
        left = fan[0]
        right = fan[-1]
    else:
        assert direction is ccw
        left = fan[-1]
        right = fan[0]

    left_leg_idx = ccw(left.vertices.index(pivot))
    left_leg = Edge(left, left_leg_idx)
#    assert left.neighbours[left_leg_idx] is None
    if left.neighbours[left_leg_idx] is not None:
        logging.warning("inf-fast pivot, but not over wavefront edge? -- left side")
    left_dist = dist(*map(lambda x: x.position_at(now), left_leg.segment))

    right_leg_idx = cw(right.vertices.index(pivot))
    right_leg = Edge(right, right_leg_idx)
#    assert right.neighbours[right_leg_idx] is None
    if right.neighbours[right_leg_idx] is not None:
        logging.warning("inf-fast pivot, but not over wavefront edge? -- right side")
    right_dist = dist(*map(lambda x: x.position_at(now), right_leg.segment))


#    logging.debug('First tri **: #{} [{}]'.format(id(first_tri), first_tri.info))

#    v1 = first_tri.vertices[ccw(first_tri.vertices.index(pivot))] # FIXME: should be a vertex from first_tri!
#    v2 = first_tri.vertices[cw(first_tri.vertices.index(pivot))] # FIXME: should be a vertex from first_tri!

#    logging.debug(' kvertices:' )
#    logging.debug('  v1: #{} [{}]'.format(id(v1), v1.info) )
#    logging.debug('  v2: #{} [{}]'.format(id(v2), v2.info) )
#    v0_leg = Edge(first_tri, first_tri.vertices.index(pivot))

#    v2_leg = Edge(first_tri, ccw(first_tri.vertices.index(pivot)))
#    v1_leg = Edge(first_tri, cw(first_tri.vertices.index(pivot)))

#    v2_dist = dist(*map(lambda x: x.position_at(now), v2_leg.segment))
#    v1_dist = dist(*map(lambda x: x.position_at(now), v1_leg.segment))
#    dists = [v1_dist, v2_dist]
#    v0_dist = dist(*map(lambda x: x.position_at(now), v0_leg.segment))

    dists = [left_dist, right_dist]

    logging.debug('  distances: {}'.format(dists))
#    logging.debug('  DISTANCE v0: {}'.format(v0_dist))

    dists_sub_min = [near_zero(_ - min(dists)) for _ in dists]
    logging.debug(dists_sub_min)
    unique_dists = dists_sub_min.count(True)

    # raw_input(' just before handling parallel event')
    # ----------------------------------------------------------
    # get neighbours around collapsing triangle
    # n = first_tri.neighbours[first_tri.vertices.index(pivot)]
    # new_direction = None # potentially new fan, how does it turn?

    if unique_dists == 2:
        logging.debug("Equal sized legs")
        handle_parallel_edge_event_even_legs(first_tri, first_tri.vertices.index(pivot), pivot, now, skel, queue, immediate)
        # handle_parallel_edge_event(first_tri, cw(first_tri.vertices.index(pivot)), pivot,  now, skel, queue, immediate)

        # post condition: all triangles in the fan are stopped
        # when we have 2 equal sized legs -- does not hold for Koch-rec-level-3 ???
#        for t in fan:
#            assert t.stops_at is not None
    else:
        # check what is the shortest of the two distances
        shortest_idx = dists_sub_min.index(True)
        if shortest_idx == 1: # right is shortest, left is longest
            logging.debug("CW / left wavefront at pivot, ending at v2, is longest")
            handle_parallel_edge_event_shorter_leg(right_leg.triangle, right_leg.side, pivot,  now, skel, queue, immediate)
        elif shortest_idx == 0: # left is shortest, right is longest
            logging.debug("CCW / right wavefront at pivot, ending at v1, is longest")
            handle_parallel_edge_event_shorter_leg(left_leg.triangle, left_leg.side, pivot,  now, skel, queue, immediate)




def handle_parallel_edge_event_shorter_leg(t, e, pivot, now, skel, queue, immediate):
    """Handles triangle collapse, where exactly 1 edge collapses
    
    One of the vertices of the triangle moves *infinitely* fast.

    There are 2 cases handled in this function
    
    a. triangle with long left leg, short right leg
    b. triangle with long right leg, short left leg

    Arguments:
    t -- triangle that collapses
    e -- short side over which pivot moves inf fast

    """
    logging.debug('At start of handle_parallel_edge_event_shorter_leg')

    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))
    assert pivot.inf_fast
    # vertices, that are not inf fast, need to stop
    # FIXME: this is not necessarily correct ... 
    #  where they need to stop depends on the configuration
    #  -- now they are *always* snapped to same location

    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]
    logging.debug("* tri>> #{} [{}]".format(id(t), t.info))
    logging.debug("* pivot #{} [{}]".format(id(pivot), pivot.info))
    logging.debug("* v1 #{} [{}]".format(id(v1), v1.info))
    logging.debug("* v2 #{} [{}]".format(id(v2), v2.info))
    assert pivot is v1 or pivot is v2

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
        # we will update the circular list
        # at the pivot a little bit later
    else:
        logging.warn("Infinite fast pivot already stopped,"
                     " but should not be stopped(?)")
    # we "remove" the triangle itself
    t.stops_at = now
    # check that the edge that collapses is not opposite of the pivot
    # i.e. the edge is one of the two adjacent legs at the pivot
    assert t.vertices.index(pivot) != e
    kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1)
    logging.debug("Computed new kinetic vertex {} [{}]".format(id(kv), kv.info))
    if kv.inf_fast:
        logging.debug("New kinetic vertex moves infinitely fast!")
    # get neighbours around collapsing triangle
    a = t.neighbours[ccw(e)]
    b = t.neighbours[cw(e)]
    n = t.neighbours[e]
    # second check:
    # is vertex infinitely fast?
    # in this case, both sides of the new vertex 
    # should collapse to be infinitely fast!
    is_inf_fast_a = is_infinitely_fast(get_fan(a, v2, cw), now)
    is_inf_fast_b = is_infinitely_fast(get_fan(b, v1, ccw), now)
    if is_inf_fast_a and is_inf_fast_b:
        assert kv is not None
        if not kv.inf_fast:
            logging.debug("New kinetic vertex: ***Upgrading*** to infinitely fast moving vertex!")
            kv.inf_fast = True
    # append to skeleton structure, new kinetic vertex
    skel.vertices.append(kv)

    # update circular list of kinetic vertices
    logging.debug("-- update circular list for new kinetic vertex kv: {} [{}]".format(id(kv), kv.info))
    update_circ(v1.left, kv, now)
    update_circ(kv, v2.right, now)
    # update the triangle fans incident
    fan_a = []
    fan_b = []
    if a is not None:
        logging.debug("- replacing vertex for neighbours at side A {} [{}]".format(id(a), a.info))
        a_idx = a.neighbours.index(t)
        a.neighbours[a_idx] = b
        fan_a = replace_kvertex(a, v2, kv, now, cw, queue, immediate)
####        visualize(queue, skel, now) #-0.00001)
####        raw_input('replaced neighbour A')
    if b is not None:
        logging.debug("- replacing vertex for neighbours at side B {} [{}]".format(id(b), b.info))
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        fan_b = replace_kvertex(b, v1, kv, now, ccw, queue, immediate)
#####        visualize(queue, skel, now)#-0.00001)
#####        raw_input('replaced neighbour B')
    #
    logging.debug("*** neighbour n: {} ".format("schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"))
    if n is not None:
        n.neighbours[n.neighbours.index(t)] = None
        if n.event is not None and n.stops_at is None:
            schedule_immediately(n, now, queue, immediate)
    #visualize(queue, skel, now-1.0e-3)
    #raw_input('continue after parallel -- one of two legs')
    # process parallel fan
    if kv and kv.inf_fast:
        if fan_a:
            handle_parallel_fan(fan_a, kv, now, cw, skel, queue, immediate)
        if fan_b:
            handle_parallel_fan(fan_b, kv, now, ccw, skel, queue, immediate)







# Parallel -- both legs equally long
# -----------------------------------------------------------------------------
def handle_parallel_edge_event_even_legs(t, e, pivot, now, skel, queue, immediate):

    logging.debug('At start of handle_parallel_edge_event with same size legs')
    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))

    assert pivot is t.vertices[e]
    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]

    # stop the non-infinite vertices
    sk_node, newly_made = stop_kvertices([v1, v2], now)
    if newly_made:
        skel.sk_nodes.append(sk_node)

    # stop the pivot as well
    if pivot.stop_node is not None:
        logging.warn("Infinite fast pivot already stopped,"
                         " but should not be stopped(?)")
#    assert pivot.stop_node is None
#    assert pivot.stops_at is None
    pivot.stop_node = sk_node
    pivot.stops_at = now
    # this is not necessary, is it?
    ## update_circ(pivot, v1, now)
    ## update_circ(v2, pivot, now)

    # we "remove" the triangle itself
    t.stops_at = now

    # we are collapsing the edge opposite of the inf fast pivot vertex
    assert t.vertices.index(pivot) == e
    n = t.neighbours[e]
    msg = "schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"
    logging.debug("*** neighbour n: {} ".format(msg))
    if n is not None:
        n.neighbours[n.neighbours.index(t)] = None
        if n.event is not None and n.stops_at is None:
            logging.debug(n.event)
            schedule_immediately(n, now, queue, immediate)


































def unused_parallel_OLD_CODE(t, e, pivot, now, skel, queue, immediate):
    """Handles triangle collapse, where exactly 1 edge collapses
    
    One of the vertices of the triangle moves *infinitely* fast.

    There are 3 cases handled:
    
    1.a. triangle with long left leg, short right leg
    1.b. triangle with long right leg, short left leg

    2. triangle with 2 equal sized legs, edge collapsing between

    Cases 1a/1b can lead to new infinitely fast vertices, while
    Case 2 leads to having to process immediately a neighbouring triangle
    """

    raise NotImplementedError("OLD CODE -- DO NOT USE")

    logging.debug('At start of handle_parallel_edge_event')
    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))
    assert pivot.inf_fast

    # vertices, that are not inf fast, need to stop
    # FIXME: this is not necessarily correct ... 
    #  where they need to stop depends on the configuration
    #  -- now they are *always* snapped to same location
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
        kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1)
        logging.debug("Computed new kinetic vertex {} [{}]".format(id(kv), kv.info))
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
        logging.debug("*** neighbour n: {} ".format("schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"))
        if n is not None:
            n.neighbours[n.neighbours.index(t)] = None
            if n.event is not None and n.stops_at is None:
                schedule_immediately(n, now, queue, immediate)

        #visualize(queue, skel, now-1.0e-3)
        #raw_input('continue after parallel -- one of two legs')

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
        msg = "schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"
        logging.debug("*** neighbour n: {} ".format(msg))
        if n is not None:
            n.neighbours[n.neighbours.index(t)] = None
            if n.event is not None and n.stops_at is None:
                logging.debug(n.event)
                schedule_immediately(n, now, queue, immediate)

            #visualize(queue, skel, now-1.0e-3)
            #raw_input('continue after parallel --  opposite pivot')

