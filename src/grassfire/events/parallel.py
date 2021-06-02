import logging

from tri.delaunay.tds import ccw, cw, Edge

# flip dependencies
from tri.delaunay.tds import apex, orig, dest
# from grassfire.events.lib import replace_in_queue
#

from grassfire.events.lib import stop_kvertices, update_circ, \
    compute_new_kvertex, replace_kvertex, schedule_immediately, \
    is_infinitely_fast
from grassfire.events.lib import get_fan
# from grassfire.events.lib import notify_qgis
from grassfire.inout import interactive_visualize
from grassfire.calc import groupby_cluster, near_zero
from grassfire.primitives import KineticVertex
from grassfire.vectorops import dist



def flip(t0, side0, t1, side1):
    """Performs a flip of triangle t0 and t1

    If t0 and t1 are two triangles sharing a common edge AB,
    the method replaces ABC and BAD triangles by DCA and DBC, respectively.

    Pre-condition: input triangles share a common edge and this edge is known.
    """
    apex0, orig0, dest0 = apex(side0), orig(side0), dest(side0)
    apex1, orig1, dest1 = apex(side1), orig(side1), dest(side1)
    # side0 and side1 should be same edge
    assert t0.vertices[orig0] is t1.vertices[dest1]
    assert t0.vertices[dest0] is t1.vertices[orig1]
    # assert both triangles have this edge unconstrained
    assert t0.neighbours[apex0] is not None
    assert t1.neighbours[apex1] is not None
    # -- vertices around quadrilateral in ccw order starting at apex of t0
    A, B, C, D = t0.vertices[apex0], t0.vertices[
        orig0], t1.vertices[apex1], t0.vertices[dest0]
    # -- triangles around quadrilateral in ccw order, starting at A
    AB, BC, CD, DA = t0.neighbours[dest0], t1.neighbours[
        orig1], t1.neighbours[dest1], t0.neighbours[orig0]
    # link neighbours around quadrilateral to triangles as after the flip
    # -- the sides of the triangles around are stored in apex_around
    apex_around = []
    for neighbour, corner in zip([AB, BC, CD, DA],
                                 [A, B, C, D]):
        if neighbour is None:
            apex_around.append(None)
        else:
            apex_around.append(ccw(neighbour.vertices.index(corner)))
    # the triangles around we link to the correct triangle *after* the flip
    for neighbour, side, t in zip([AB, BC, CD, DA],
                                  apex_around,
                                  [t0, t0, t1, t1]):
        if neighbour is not None:
            neighbour.neighbours[side] = t
    # -- set new vertices and neighbours
    # for t0
    t0.vertices = [A, B, C]
    t0.neighbours = [BC, t1, AB]
    # for t1
    t1.vertices = [C, D, A]
    t1.neighbours = [DA, t0, CD]


# Parallel
# -----------------------------------------------------------------------------
def handle_parallel_fan(fan, pivot, now, direction, step, skel, queue, immediate, pause):
    """Dispatches to correct function for handling parallel wavefronts

    fan: list of triangles, sorted (in *direction* order)
    pivot: the vertex that is going infinitely fast
    now: time at which parallel event happens
    direction: how the fan turns

    skel: skeleton structure
    queue: event queue
    immediate: queue of events that should be dealt with when finished handling
    the current event

    pause: whether we should stop for interactivity
    """
    if not fan:
        raise ValueError("we should receive a fan of triangles to handle them")
        return

    logging.debug("""
# ---------------------------------------------------------
# -- PARALLEL event handler invoked                      --
# ---------------------------------------------------------
""")
    if pause:
        logging.debug(" -- {}".format(len(fan)))
        logging.debug("    triangles in the fan: {}".format([(id(_), _.info) for _ in fan]))
        logging.debug("    fan turns: {}".format(direction))
        logging.debug("    pivot: {} [{}]".format(id(pivot), pivot.info))
        interactive_visualize(queue, skel, step, now)

    assert pivot.inf_fast
    first_tri = fan[0]
    last_tri = fan[-1]
    # special case, infinite fast vertex in *at least* 1 corner
    # no neighbours (3 wavefront edges)
    # -> let's collapse the edge opposite of the pivot
    if first_tri.neighbours.count(None) == 3:
        assert first_tri is last_tri #FIXME: is this true?
        dists = []
        for side in range(3):
            edge = Edge(first_tri, side)
            d = dist(*map(lambda x: x.position_at(now), edge.segment))
            dists.append(d)
        dists_sub_min = [near_zero(_ - min(dists)) for _ in dists]
        if near_zero(min(dists)) and dists_sub_min.count(True) == 1:
            logging.debug(dists_sub_min)
            logging.debug("Smallest edge collapses? {}".format(near_zero(min(dists))))
            assert dists_sub_min.count(True) == 1
    #        assert dists_sub_min.index(True) == first_tri.vertices.index(pivot)
            side = dists_sub_min.index(True)
            pivot = first_tri.vertices[dists_sub_min.index(True)]
            handle_parallel_edge_event_even_legs(first_tri, first_tri.vertices.index(pivot), pivot, now, step, skel, queue, immediate)
            return
        else:
            handle_parallel_edge_event_3tri(first_tri, first_tri.vertices.index(pivot), pivot, now, step, skel, queue, immediate)
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
    if left.neighbours[left_leg_idx] is not None:
        logging.debug("inf-fast pivot, but not over wavefront edge? -- left side")
    left_dist = dist(*map(lambda x: x.position_at(now), left_leg.segment))
    right_leg_idx = cw(right.vertices.index(pivot))
    right_leg = Edge(right, right_leg_idx)
    if right.neighbours[right_leg_idx] is not None:
        logging.debug("inf-fast pivot, but not over wavefront edge? -- right side")
    right_dist = dist(*map(lambda x: x.position_at(now), right_leg.segment))
    dists = [left_dist, right_dist]
    logging.debug('  distances: {}'.format(dists))
    dists_sub_min = [near_zero(_ - min(dists)) for _ in dists]
    logging.debug(dists_sub_min)
    unique_dists = dists_sub_min.count(True)
    if unique_dists == 2:
        logging.debug("Equal sized legs")
        if len(fan) == 1:
            logging.debug("Calling handle_parallel_edge_event_even_legs for 1 triangle")
            handle_parallel_edge_event_even_legs(first_tri, first_tri.vertices.index(pivot), pivot, now, step, skel, queue, immediate)
        elif len(fan) == 2:

            # FIXME: even if the 2 wavefronts collapse and the sides are equal in size
            # some triangles can be partly inside the fan and partly outside
            # e.g. if quad collapses and 2 sides collapse onto each other, the spokes
            # can still stick out of the fan ->
            # result: triangles around these spokes should be glued together (be each others neighbours)
            #    =======================+
            #   +                       \\\\\\\\\\\\\\\\\
            # inf-----------------------------------------+
            #   +                       /////////////////
            #    =======================+

#            handle_parallel_edge_event_even_legs(first_tri, first_tri.vertices.index(pivot), pivot, now, skel, queue, immediate)
#            handle_parallel_edge_event_even_legs(last_tri, last_tri.vertices.index(pivot), pivot, now, skel, queue, immediate)
            logging.debug("Calling handle_parallel_edge_event_even_legs for *multiple* triangles")
            # raise NotImplementedError('multiple triangles #{} in parallel fan that should be stopped'.format(len(fan)))

            all_2 = True
            for t in fan:
                # FIXME: left = cw / right = ccw seen from the vertex
                left_leg_idx = ccw(t.vertices.index(pivot))
                left_leg = Edge(t, left_leg_idx)
                left_dist = dist(*map(lambda x: x.position_at(now), left_leg.segment))

                right_leg_idx = cw(t.vertices.index(pivot))
                right_leg = Edge(t, right_leg_idx)
                right_dist = dist(*map(lambda x: x.position_at(now), right_leg.segment))

                dists = [left_dist, right_dist]

                dists_sub_min = [near_zero(_ - min(dists)) for _ in dists]
                logging.debug("  {}".format([left_dist, right_dist]))
                logging.debug("  {}".format(dists_sub_min))
                unique_dists = dists_sub_min.count(True)
                if unique_dists != 2:
                    all_2 = False

            # assert unique_dists == 2
            if all_2 == True:
                for t in fan:
                    handle_parallel_edge_event_even_legs(t, t.vertices.index(pivot), pivot, now, step, skel, queue, immediate)
            else:
                # not all edges in the fan have equal length, so first flip the triangles
                # before continue handling them

                # unpack the 2 triangles from the fan and flip them
                t0 = fan[0]
                t1 = fan[1]
                side0 = t0.neighbours.index(t1)
                side1 = t1.neighbours.index(t0)
                flip(t0, side0, t1, side1)

                # now if a triangle has inf-fast vertex, handle the wavefront collapse
                t0_has_inf_fast = [v.inf_fast for v in t0.vertices]
                t1_has_inf_fast = [v.inf_fast for v in t1.vertices]
                logging.debug(t0_has_inf_fast)
                logging.debug(t1_has_inf_fast)

                if True in t0_has_inf_fast:
                    logging.debug("-- Handling t0 after flip event in parallel fan --")
                    handle_parallel_edge_event_even_legs(t0, t0.vertices.index(pivot), pivot, now, step, skel, queue, immediate)

                if True in t1_has_inf_fast:
                    logging.debug("-- Handling t1 after flip event in parallel fan --")
                    handle_parallel_edge_event_even_legs(t1, t1.vertices.index(pivot), pivot, now, step, skel, queue, immediate)

            if pause:
                interactive_visualize(queue, skel, step, now)
            # raise NotImplementedError('multiple triangles in parallel fan that should be *flipped*')

        else:
            raise NotImplementedError('More than 2 triangles in parallel fan with 2 equal sized legs on the outside -- does this exist?')

        # post condition: all triangles in the fan are stopped
        # when we have 2 equal sized legs -- does not hold for Koch-rec-level-3 ???
        if len(fan) == 1 or (len(fan) == 2 and all_2 == True):
            for t in fan:
                assert t.stops_at is not None
    else:
        # check what is the shortest of the two distances
        shortest_idx = dists_sub_min.index(True)
        if shortest_idx == 1: # right is shortest, left is longest
            logging.debug("CW / left wavefront at pivot, ending at v2, is longest")
            handle_parallel_edge_event_shorter_leg(right_leg.triangle, right_leg.side, pivot, now, step, skel, queue, immediate, pause)
        elif shortest_idx == 0: # left is shortest, right is longest
            logging.debug("CCW / right wavefront at pivot, ending at v1, is longest")
            handle_parallel_edge_event_shorter_leg(left_leg.triangle, left_leg.side, pivot, now, step, skel, queue, immediate, pause)


def handle_parallel_edge_event_shorter_leg(t, e, pivot, now, step, skel, queue, immediate, pause):
    """Handles triangle collapse, where exactly 1 edge collapses
    
    One of the vertices of the triangle moves *infinitely* fast.

    There are 2 cases handled in this function
    
    a. triangle with long left leg, short right leg
    b. triangle with long right leg, short left leg

    Arguments:
    t -- triangle that collapses
    e -- short side over which pivot moves inf fast

    """

    logging.info("* parallel|short :: tri>> #{} [{}]".format(id(t), t.info))
    logging.debug('At start of handle_parallel_edge_event_shorter_leg')

    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))
    assert pivot.inf_fast
    # vertices, that are not inf fast, need to stop
    # FIXME: this is not necessarily correct ... 
    #  where they need to stop depends on the configuration
    #  -- now they are *always* snapped to same location

    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]
    v3 = t.vertices[e]
    logging.debug("* tri>> #{} [{}]".format(id(t), t.info))
    logging.debug("* pivot #{} [{}]".format(id(pivot), pivot.info))
    logging.debug("* v1 #{} [{}]".format(id(v1), v1.info))
    logging.debug("* v2 #{} [{}]".format(id(v2), v2.info))
    logging.debug("* v3 #{} [{}]".format(id(v3), v3.info))
    assert pivot is v1 or pivot is v2

    to_stop = []
    for v in [v1, v2]:
        if not v.inf_fast:
            to_stop.append(v)

    # stop the non-infinite vertices
    sk_node, newly_made = stop_kvertices(to_stop, step, now)
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
        logging.debug("Infinite fast pivot already stopped,"
                     " but should not be stopped(?)")
    # we "remove" the triangle itself
    t.stops_at = now
    # check that the edge that collapses is not opposite of the pivot
    # i.e. the edge is one of the two adjacent legs at the pivot
    assert t.vertices.index(pivot) != e
    kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1, v1.internal or v2.internal, pause)
    # FIXME new wavefront -- update refs
    kv.wfl = v1.left.wfr
    kv.wfr = v2.right.wfl

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
    # is_inf_fast_a = is_infinitely_fast(get_fan(a, v2, cw), now)
    # is_inf_fast_b = is_infinitely_fast(get_fan(b, v1, ccw), now)
    # if is_inf_fast_a and is_inf_fast_b:
    #     assert kv is not None
    #     if not kv.inf_fast:
    #         logging.debug("New kinetic vertex: ***Not upgrading*** to infinitely fast moving vertex!")
            # we if the vertex is in a 90.0 degree angle for which both sides are inf-fast
            # kv.inf_fast = True
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
        if pause:
            logging.debug('replaced neighbour A')
            interactive_visualize(queue, skel, step, now)

    if b is not None:
        logging.debug("- replacing vertex for neighbours at side B {} [{}]".format(id(b), b.info))
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        fan_b = replace_kvertex(b, v1, kv, now, ccw, queue, immediate)
        if pause:
            logging.debug('replaced neighbour B')
            interactive_visualize(queue, skel, step, now)
    #
    logging.debug("*** neighbour n: {} ".format("schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"))
    if n is not None:
        n.neighbours[n.neighbours.index(t)] = None
        if n.event is not None and n.stops_at is None:
            schedule_immediately(n, now, queue, immediate)
    #visualize(queue, skel, now-1.0e-3)
    
    #raw_input('continue after parallel -- one of two legs')
    # process parallel fan, only if the fan has all un-dealt with triangles
    if kv and kv.inf_fast:
#        # fan - cw
#        if fan_a and all([t.stops_at is None for t in fan_a]):
#            handle_parallel_fan(fan_a, kv, now, cw, step, skel, queue, immediate, pause)
#            return
#        elif fan_a:
#            # we should have a fan in which all triangles are already stopped
#            assert all([t.stops_at is not None for t in fan_a])
#        # fan - ccw
#        if fan_b and all([t.stops_at is None for t in fan_b]):
#            handle_parallel_fan(fan_b, kv, now, ccw, step, skel, queue, immediate, pause)
#            return
#        elif fan_b:
#            # we should have a fan in which all triangles are already stopped
#            assert all([t.stops_at is not None for t in fan_b])

        if fan_a and fan_b:
            # combine both fans into 1
            fan_a = list(fan_a)
            fan_a.reverse()
            fan_a.extend(fan_b)
            handle_parallel_fan(fan_a, kv, now, ccw, step, skel, queue, immediate, pause)
            return
        elif fan_a:
            handle_parallel_fan(fan_a, kv, now, cw, step, skel, queue, immediate, pause)
            return
        elif fan_b:
            handle_parallel_fan(fan_b, kv, now, ccw, step, skel, queue, immediate, pause)
            return




# Parallel -- both legs equally long
# -----------------------------------------------------------------------------
def handle_parallel_edge_event_even_legs(t, e, pivot, now, step, skel, queue, immediate):

    logging.info("* parallel|even  :: tri>> #{} [{}]".format(id(t), t.info))

    logging.debug('At start of handle_parallel_edge_event with same size legs')
    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))

    # FIXME: pre-conditions for this handler
    # there should be 1 edge with zero length, and other 2 edges should have length?
    # can it also be that this handler deals with collapse to point ???

    # does not hold! -> 

    # triangle can also be like:
    # *-------------------------*
    #  `---------------*'''''''

    # we are collapsing the edge opposite of the inf fast pivot vertex
    # this assumes that v1 and v2 need to be on the same location!!!
    assert t.vertices.index(pivot) == e
    assert t.vertices[e] is pivot
#    assert pivot.inf_fast
    # stop the non-infinite vertices
    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]
    sk_node, newly_made = stop_kvertices([v1,v2], step, now)
    if newly_made:
        skel.sk_nodes.append(sk_node)

    # stop the pivot as well
    if pivot.stop_node is not None:
        logging.debug("Infinite fast pivot already stopped, but should not be stopped(?)")
#    assert pivot.stop_node is None
#    assert pivot.stops_at is None
    pivot.stop_node = sk_node
    pivot.stops_at = now
    # this is not necessary, is it?
    ## update_circ(pivot, v1, now)
    ## update_circ(v2, pivot, now)

    # we "remove" the triangle itself
    t.stops_at = now

    n = t.neighbours[e]
    msg = "schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"
    logging.debug("*** neighbour n: {} ".format(msg))
    if n is not None:
        n.neighbours[n.neighbours.index(t)] = None
        if n.event is not None and n.stops_at is None:
            logging.debug(n.event)
            schedule_immediately(n, now, queue, immediate)


def handle_parallel_edge_event_3tri(t, e, pivot, now, step, skel, queue, immediate):
    logging.info("* parallel|even#3 :: tri>> #{} [{}]".format(id(t), t.info))

    logging.debug('At start of handle_parallel_edge_event for 3 triangle')
    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))

    # triangle is like:
    # *-------------------------*
    #  `---------------*'''''''

    # we are collapsing the edge opposite of the inf fast pivot vertex
    # this assumes that v1 and v2 need to be on the same location!!!
    assert t.vertices.index(pivot) == e
    assert t.vertices[e] is pivot
#    assert pivot.inf_fast

    left_leg_idx = ccw(t.vertices.index(pivot))
    left_leg = Edge(t, left_leg_idx)
    left_dist = dist(*map(lambda x: x.position_at(now), left_leg.segment))
    v1 = t.vertices[ccw(e)]

    right_leg_idx = cw(t.vertices.index(pivot))
    right_leg = Edge(t, right_leg_idx)
    right_dist = dist(*map(lambda x: x.position_at(now), right_leg.segment))
    v2 = t.vertices[cw(e)]

    assert v1 is not pivot
    assert v2 is not pivot

    assert pivot in t.vertices
    assert v1 in t.vertices
    assert v2 in t.vertices

    from grassfire.vectorops import dot, norm
    logging.debug(v1.velocity)
    logging.debug(v2.velocity)
    magn_v1 = norm(v1.velocity)
    magn_v2 = norm(v2.velocity)

    logging.debug('  velocity magnitude: {}'.format([magn_v1, magn_v2]))

    dists = [left_dist, right_dist]
    logging.debug('  distances: {}'.format(dists))
    dists_sub_min = [near_zero(_ - min(dists)) for _ in dists]
    logging.debug(dists_sub_min)

    # stop the non-infinite vertices at the same location
    # use the slowest moving vertex to determine the location
    if magn_v2 < magn_v1:
        sk_node, newly_made = stop_kvertices([v2], step, now)
        if newly_made:
            skel.sk_nodes.append(sk_node)
        v1.stop_node = sk_node
        v1.stops_at = now
    else:
        sk_node, newly_made = stop_kvertices([v1], step, now)
        if newly_made:
            skel.sk_nodes.append(sk_node)
        v2.stop_node = sk_node
        v2.stops_at = now

    


    # FIXME:
    # make edge between v1 and v2

#    assert pivot.stop_node is None
#    assert pivot.stops_at is None

    #FIXME: wrong sk_node for pivot
    pivot.stop_node = sk_node
    pivot.stops_at = now
    # this is not necessary, is it?
    ## update_circ(pivot, v1, now)
    ## update_circ(v2, pivot, now)

    # we "remove" the triangle itself
    t.stops_at = now


    for kv in t.vertices:
        assert kv.stops_at is not None




















##def unused_parallel_OLD_CODE(t, e, pivot, now, skel, queue, immediate):
##    """Handles triangle collapse, where exactly 1 edge collapses
##    
##    One of the vertices of the triangle moves *infinitely* fast.

##    There are 3 cases handled:
##    
##    1.a. triangle with long left leg, short right leg
##    1.b. triangle with long right leg, short left leg

##    2. triangle with 2 equal sized legs, edge collapsing between

##    Cases 1a/1b can lead to new infinitely fast vertices, while
##    Case 2 leads to having to process immediately a neighbouring triangle
##    """

##    raise NotImplementedError("OLD CODE -- DO NOT USE")

##    logging.debug('At start of handle_parallel_edge_event')
##    logging.debug("Edge with inf fast vertex collapsing! {0}".format(t.neighbours[e] is None))
##    assert pivot.inf_fast

##    # vertices, that are not inf fast, need to stop
##    # FIXME: this is not necessarily correct ... 
##    #  where they need to stop depends on the configuration
##    #  -- now they are *always* snapped to same location
##    v1 = t.vertices[ccw(e)]
##    v2 = t.vertices[cw(e)]
##    to_stop = []
##    for v in [v1, v2]:
##        if not v.inf_fast:
##            to_stop.append(v)
##    # stop the non-infinite vertices
##    sk_node, newly_made = stop_kvertices(to_stop, now)
##    if newly_made:
##        skel.sk_nodes.append(sk_node)
##    if pivot.stop_node is None:
##        assert pivot.stop_node is None
##        assert pivot.stops_at is None
##        pivot.stop_node = sk_node
##        pivot.stops_at = now
##        # FIXME: is left/right "None" correct here ???
##        update_circ(pivot, None, now)
##        update_circ(None, pivot, now)
##    else:
##        logging.warn("Infinite fast pivot already stopped,"
##                     " but should not be stopped(?)")
##        # assert not newly_made
##        # print(sk_node.pos)
##        # print(pivot.position_at(now))
##        # assert sk_node.pos == pivot.position_at(now)

##    # we "remove" the triangle itself
##    t.stops_at = now

##    # the edge that collapses is not opposite of the pivot
##    # i.e. the edge is one of the two adjacent legs at
##    # the pivot
##    if t.vertices.index(pivot) != e:
##        kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1, v1.internal or v2.internal)
##        logging.debug("Computed new kinetic vertex {} [{}]".format(id(kv), kv.info))
##        if kv.inf_fast:
##            logging.debug("New kinetic vertex moves infinitely fast!")
##        # append to skeleton structure, new kinetic vertex
##        skel.vertices.append(kv)
##        # update circular list of kinetic vertices
##        update_circ(v1.left, kv, now)
##        update_circ(kv, v2.right, now)
##        # get neighbours around collapsing triangle
##        a = t.neighbours[ccw(e)]
##        b = t.neighbours[cw(e)]
##        n = t.neighbours[e]
##        # second check:
##        # is vertex infinitely fast?
##        def is_infinitely_fast(fan, now):
##            """Determine whether all triangles in the fan collapse
##            at the same time, if so, the vertex needs to be infinitely fast"""
##            times = [tri.event.time if tri.event is not None else -1 for tri in fan ]
##            logging.debug("edge {}".format(times))
##            is_inf_fast = all(map(near_zero, [time - now for time in times]))
##            logging.debug("edge {}".format(is_inf_fast))
##            if fan and is_inf_fast:
##                return True
##            else:
##                return False
##        # in this case, both sides of the new vertex 
##        # should collapse to be infinitely fast!
##        is_inf_fast_a = is_infinitely_fast(get_fan(a, v2, cw), now)
##        is_inf_fast_b = is_infinitely_fast(get_fan(b, v1, ccw), now)
##        if is_inf_fast_a and is_inf_fast_b:
##            assert kv is not None
##            if not kv.inf_fast:
##                logging.debug("New kinetic vertex: ***Upgrading*** to infinitely fast moving vertex!")
##                kv.inf_fast = True
##        fan_a = []
##        fan_b = []
##        if a is not None:
##            logging.debug("replacing vertex for neighbours at side A")
##            a_idx = a.neighbours.index(t)
##            a.neighbours[a_idx] = b
##            fan_a = replace_kvertex(a, v2, kv, now, cw, queue, immediate)
##        if b is not None:
##            logging.debug("replacing vertex for neighbours at side B")
##            b_idx = b.neighbours.index(t)
##            b.neighbours[b_idx] = a
##            fan_b = replace_kvertex(b, v1, kv, now, ccw, queue, immediate)
##        #
##        logging.debug("*** neighbour n: {} ".format("schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"))
##        if n is not None:
##            n.neighbours[n.neighbours.index(t)] = None
##            if n.event is not None and n.stops_at is None:
##                schedule_immediately(n, now, queue, immediate)

##        #visualize(queue, skel, now-1.0e-3)
##        #raw_input('continue after parallel -- one of two legs')

##        # process parallel fan
##        if kv and kv.inf_fast:
##            if fan_a:
##                handle_parallel_fan(fan_a, kv, now, cw, skel, queue, immediate)
##            if fan_b:
##                handle_parallel_fan(fan_b, kv, now, ccw, skel, queue, immediate)

##    else:
##        # we are collapsing the edge opposite of the inf fast pivot vertex
##        assert t.vertices.index(pivot) == e
##        n = t.neighbours[e]
##        msg = "schedule adjacent neighbour for *IMMEDIATE* processing" if n is not None else "no neighbour to collapse simultaneously"
##        logging.debug("*** neighbour n: {} ".format(msg))
##        if n is not None:
##            n.neighbours[n.neighbours.index(t)] = None
##            if n.event is not None and n.stops_at is None:
##                logging.debug(n.event)
##                schedule_immediately(n, now, queue, immediate)

##            #visualize(queue, skel, now-1.0e-3)
##            #raw_input('continue after parallel --  opposite pivot')

