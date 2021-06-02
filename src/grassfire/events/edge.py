# -*- coding: utf-8 -*- 
import logging

from tri.delaunay.tds import cw, ccw, Edge

from grassfire.events.lib import stop_kvertices, compute_new_kvertex, \
    update_circ, replace_kvertex, schedule_immediately, near_zero
from grassfire.events.lib import get_fan, is_infinitely_fast
from grassfire.events.parallel import handle_parallel_fan
from grassfire.line2d import WaveFrontIntersector


def signed_turn(head, mid, tail):
    from grassfire.vectorops import make_vector, cross, dot
    import math
    """turn angle at vertex going from head via mid to tail
    angle in radians

    + == left turn
    - == right turn
    0 == straight
    """
    u = make_vector(mid, head)
    v = make_vector(tail, mid)
    return math.atan2(cross(u, v), dot(u, v))


def get_bisector(head, mid, tail):
    from grassfire.vectorops import make_vector, cross, dot, mul, add, unit
    import math
    """turn angle at vertex going from head via mid to tail
    angle in radians

    + == left turn
    - == right turn
    0 == straight
    """
    logging.debug("head: {0[0]} {0[1]} mid: {1[0]} {1[1]}  tail: {2[0]} {2[1]} ".format(head, mid, tail))
    a = make_vector(tail, mid)
    b = make_vector(head, mid)
    logging.debug(a)
    logging.debug("should be tail: {}".format(add(mid, a)))
    
    logging.debug(b)
    logging.debug("should be head: {}".format(add(mid, b)))

    logging.debug(add(mid, a) == tail)
    logging.debug(add(mid, b) == head)
    
    res = add(unit(a), unit(b))
    logging.debug(res)
    return res


# ------------------------------------------------------------------------------
# Edge event handlers
def handle_edge_event(evt, step, skel, queue, immediate, pause):
    """Handles triangle collapse, where exactly 1 edge collapses"""
    t = evt.triangle
    logging.info("* edge           :: tri>> #{} [{}]".format(id(t), t.info))

    logging.debug(evt.side)
    assert len(evt.side) == 1, len(evt.side)
    # take edge e
    e = evt.side[0]
    logging.debug("wavefront edge collapsing? {0}".format(t.neighbours[e] is None))
    is_wavefront_collapse = t.neighbours[e] is None
#    if t.neighbours.count(None) == 2:
#        assert t.neighbours[e] is None
    now = evt.time
    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]

    # v1.
    logging.debug("v1 := {} [{}] -- stop_node: {}".format(id(v1), v1.info, v1.stop_node))
    logging.debug("v2 := {} [{}] -- stop_node: {}".format(id(v2), v2.info, v2.stop_node))

    # FIXME: assertion is not ok when this is triangle from spoke collapse?
    if is_wavefront_collapse and not v1.is_stopped and not v2.is_stopped:
        assert v1.right is v2
        assert v2.left is v1

    # stop the two vertices of this edge and make new skeleton node
    # replace 2 vertices with new kinetic vertex

    # +--- new use of wavefronts ------------------------------ #
    # ⋮
    a = v1.wfl
    b = v1.wfr
    if is_wavefront_collapse and not v1.is_stopped and not v2.is_stopped:
        assert v2.wfl is b
    c = v2.wfr
    #
    intersector = WaveFrontIntersector(a, c)
    bi = intersector.get_bisector()
    logging.debug(bi)
    # in general position the new position of the node can be constructed by intersecting 3 pairs of wavefronts
    # (a,c), (a,b), (b,c)
    # in case (a,c) are parallel, this is new infinitely fast vertex and triangles are locked between
    # or (a,c) are parallel due to spoke collapse (then new vertex is on straight line, splitting it in 2 times 90 degree angles)
    # in case (a,b) are parallel, then v1 is straight -- no turn
    # in case (b,c) are parallel, then v2 is straight -- no turn
    pos_at_now = None
    try:
        intersector = WaveFrontIntersector(a, c)
        pos_at_now = intersector.get_intersection_at_t(now)
        logging.debug("POINT({0[0]} {0[1]});a;c".format(pos_at_now))
    except ValueError:
        pass
    # iff the wavefronts wfl/wfr are parallel
    # then only the following 2 pairs of wavefronts can be properly intersected!
    # try:
    #     intersector = WaveFrontIntersector(a, b)
    #     pos_at_now = intersector.get_intersection_at_t(now)
    #     logging.debug("POINT({0[0]} {0[1]});a;b".format(pos_at_now))
    # except ValueError:
    #     pass
    # #
    # try:
    #     intersector = WaveFrontIntersector(b, c)
    #     pos_at_now = intersector.get_intersection_at_t(now)
    #     logging.debug("POINT({0[0]} {0[1]});b;c".format(pos_at_now))            #
    # except ValueError:
    #     pass
    # ⋮
    # +--- new use of wavefronts ------------------------------ #

    sk_node, newly_made = stop_kvertices([v1, v2], step, now, pos=pos_at_now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1, v1.internal or v2.internal, pause)

    # ---- new use of wavefronts ---------- #
    kv.wfl = v1.wfl                         #
    kv.wfr = v2.wfr                         #
    # ---- new use of wavefronts ---------- #

    logging.debug("Computed new kinetic vertex {} [{}]".format(id(kv), kv.info))
    logging.debug("v1 := {} [{}]".format(id(v1), v1.info))
    logging.debug("v2 := {} [{}]".format(id(v2), v2.info))
    # logging.debug(kv.position_at(now))
    # logging.debug(kv.position_at(now+1))
    # logging.debug("||| {} | {} | {} ||| ".format( v1.left.position_at(now), sk_node.pos, v2.right.position_at(now) ))
    # logging.debug("||| {} ||| ".format(signed_turn( v1.left.position_at(now), sk_node.pos, v2.right.position_at(now) )))
    # logging.debug("||| {} ||| ".format(get_bisector( v1.left.position_at(now), sk_node.pos, v2.right.position_at(now) )))



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

    # def sign(val):
    #     if val > 0:
    #         return +1
    #     elif val < 0:
    #         return -1
    #     else:
    #         return 0

    # bisector_check = get_bisector( v1.left.position_at(now), sk_node.pos, v2.right.position_at(now) )
    # if not kv.inf_fast:
    #     logging.debug("{} [{}]".format(v1.left, v1.left.info))
    #     logging.debug("{} [{}]".format(v2.right, v2.right.info))
    #     logging.debug("{0} vs {1}".format(bisector_check, kv.velocity))
    #     if sign(bisector_check[0]) == sign(kv.velocity[0]) and sign(bisector_check[1]) == sign(kv.velocity[1]):
    #         logging.debug('signs agree')
    #     else:
    #         logging.warning("""
            
            
            
    #         BISECTOR SIGNS DISAGREE
            
            
            
    #         """)
            
    #         kv.velocity = (sign(bisector_check[0]) * abs(kv.velocity[0]), sign(bisector_check[1]) * abs(kv.velocity[1]))
    #         raise ValueError('bisector signs disagree')

    # ---- new use of wavefronts ---------- #
    # post condition
    assert kv.wfl is kv.left.wfr
    assert kv.wfr is kv.right.wfl
    # ---- new use of wavefronts ---------- #


    # get neighbours around collapsing triangle
    a = t.neighbours[ccw(e)]
    b = t.neighbours[cw(e)]
    n = t.neighbours[e]
    # second check: is vertex infinitely fast?

#    is_inf_fast_a = is_infinitely_fast(get_fan(a, v2, cw), now)
#    is_inf_fast_b = is_infinitely_fast(get_fan(b, v1, ccw), now)
#    if is_inf_fast_a and is_inf_fast_b:
#        if not kv.inf_fast:
#            logging.debug("New kinetic vertex: ***Upgrading*** to infinitely fast moving vertex!")
#            kv.inf_fast = True
    #

    fan_a = []
    fan_b = []
    if a is not None:
        logging.debug("replacing vertex for neighbours at side A")
        a_idx = a.neighbours.index(t)
        a.neighbours[a_idx] = b
        fan_a = replace_kvertex(a, v2, kv, now, cw, queue, immediate)

        if fan_a:
            e = Edge(fan_a[-1], cw(fan_a[-1].vertices.index(kv)))
            orig, dest = e.segment
            import math
            if(near_zero(math.sqrt(orig.distance2_at(dest, now)))):
                logging.info("collapsing neighbouring edge, as it is very tiny -- cw")
                schedule_immediately(fan_a[-1], now, queue, immediate)
    if b is not None:
        logging.debug("replacing vertex for neighbours at side B")
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        fan_b = replace_kvertex(b, v1, kv, now, ccw, queue, immediate)
        if fan_b:
            e = Edge(fan_b[-1], ccw(fan_b[-1].vertices.index(kv)))
            orig, dest = e.segment
            import math
            if(near_zero(math.sqrt(orig.distance2_at(dest, now)))):
                logging.info("collapsing neighbouring edge, as it is very tiny -- ccw")
                schedule_immediately(fan_b[-1], now, queue, immediate) 

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


def handle_edge_event_3sides(evt, step, skel, queue, immediate):
    """Handle a collapse of a triangle with 3 sides collapsing.
    It does not matter whether the 3-triangle has wavefront edges or not.

    Important: The triangle vertices should collapse to 1 point.

    The following steps are performed:
    - stop the 3 kinetic vertices of the triangle
    - optionally make a new skeleton node
    - schedule all neighbours, if any, for immediate processing
      (these also collapse to the same point)
    """
    now = evt.time
    t = evt.triangle

    logging.info("* edge 3sides    :: tri>> #{} [{}]".format(id(t), t.info))

    logging.debug(evt.side)
    assert len(evt.side) == 3
    # we stop the vertices always at the same geometric location
    # This means that the triangle collapse leads to 1 point
    sk_node, newly_made = stop_kvertices(t.vertices, step, now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    # get neighbours around collapsing triangle, if any, and schedule them
    for n in t.neighbours:
        if n is not None and n.event is not None and n.stops_at is None:
            n.neighbours[n.neighbours.index(t)] = None
            schedule_immediately(n, now, queue, immediate)
    # we "remove" the triangle itself
    t.stops_at = now


def handle_edge_event_1side(evt, step, skel, queue, immediate, pause):
    """Handle a collapse of a triangle with 1 side collapsing.

    Important: The triangle collapses to a line segment.
    """
    t = evt.triangle

    logging.info("* edge 1side     :: tri>> #{} [{}]".format(id(t), t.info))


    logging.debug(evt.side)
    assert len(evt.side) == 1, len(evt.side)
    e = evt.side[0]
    logging.debug("wavefront edge collapsing? {0}".format(t.neighbours[e] is None))
    now = evt.time
    v0 = t.vertices[e]
    v1 = t.vertices[ccw(e)]
    v2 = t.vertices[cw(e)]
    # stop the two vertices of this edge and make new skeleton node
    # replace 2 vertices with new kinetic vertex
    sk_node, newly_made = stop_kvertices([v1, v2], step, now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    kv = compute_new_kvertex(v1.ul, v2.ur, now, sk_node, len(skel.vertices) + 1, v1.internal or v2.internal, pause)
    # FIXME: should we update the left and right wavefront line refs here?
    logging.debug("Computed new kinetic vertex {} [{}]".format(id(kv), kv.info))
    logging.debug("v1 := {} [{}]".format(id(v1), v1.info))
    logging.debug("v2 := {} [{}]".format(id(v2), v2.info))
    logging.debug(kv.position_at(now))
    logging.debug(kv.position_at(now+1))
    # append to skeleton structure, new kinetic vertex
    skel.vertices.append(kv)
    sk_node, newly_made = stop_kvertices([v0, kv], step, now)
    if newly_made:
        skel.sk_nodes.append(sk_node)
    # we "remove" the triangle itself
    t.stops_at = now

