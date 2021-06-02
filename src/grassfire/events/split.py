import logging
from tri.delaunay.tds import cw, ccw

from grassfire.events.lib import stop_kvertices, compute_new_kvertex, \
        update_circ, replace_kvertex, near_zero
from grassfire.events.parallel import handle_parallel_fan
from grassfire.events.lib import get_fan, is_infinitely_fast
from grassfire.line2d import WaveFrontIntersector



def compute_crossing_bisector(left, right, now):
    """given two wavefront lines and the time now compute 
    where these wavefronts would be at this moment
    intersect them 

    and from the original intersection point to this intersection
    point compute the vector that gives the bisector
    """
    from grassfire.vectorops import mul, make_vector
    from grassfire.line2d import LineLineIntersector, LineLineIntersectionResult

    intersect = LineLineIntersector(left, right)
    if intersect.intersection_type() == LineLineIntersectionResult.POINT:
        v = intersect.result

        with open("/tmpfast/wavefront_original_intersection.wkt", "w") as fh:
            fh.write("wkt")
            fh.write("\n")
            fh.write("POINT({0[0]} {0[1]})".format(v))
            fh.write("\n")

    else:
        raise NotImplementedError()

    bi = None
    left_translated = left.translated(mul(left.w, now))
    right_translated = right.translated(mul(right.w, now))
    intersect = LineLineIntersector(left_translated, right_translated)
    #
    # == 3 possible outcomes in 2D: ==
    #
    # 0. overlapping lines - always intersecting in a line
    # 1. crossing - point2
    # 2. parallel - no intersection
    #
    if intersect.intersection_type() == LineLineIntersectionResult.LINE:
        bi = tuple(left.w)
    elif intersect.intersection_type() == LineLineIntersectionResult.POINT:
        with open("/tmpfast/wavefront_intersection.wkt", "w") as fh:
            fh.write("wkt")
            fh.write("\n")
            fh.write("POINT({0[0]} {0[1]})".format(intersect.result))
            fh.write("\n")
        bi = make_vector(end=intersect.result, start=v)
    elif intersect.intersection_type() == LineLineIntersectionResult.NO_INTERSECTION:
        # print('no intersection, parallel wavefronts - not overlapping?')
        logging.warning('no intersection, parallel wavefronts - not overlapping?  -- should we rotate the unit vec?')
        bi = tuple(left.w)

    return bi
# ------------------------------------------------------------------------------
# Split event handler
def handle_split_event(evt, step, skel, queue, immediate, pause):
    """Handles a split event where a wavefront edge is hit on its interior
    This splits the wavefront in two pieces
    """
    t = evt.triangle

    logging.info("* split          :: tri>> #{} [{}]".format(id(t), t.info))

    logging.debug("{}".format(t.neighbours))
    assert len(evt.side) == 1
    e = evt.side[0]
    now = evt.time
    v = t.vertices[(e) % 3]
    n = t.neighbours[e]
    assert n is None
    v1 = t.vertices[(e + 1) % 3]
    v2 = t.vertices[(e + 2) % 3]

    logging.debug("v1 := {} [{}]".format(id(v1), v1.info))
    logging.debug("v2 := {} [{}]".format(id(v2), v2.info))


    assert v1.wfr is v2.wfl

    # ---- new use of wavefronts ------------------------------ #
    # split leads to 2 bisectors
    a = v.wfr
    b = v1.wfr
    assert v2.wfl is b
    c = v.wfl

    # TODO: are we having the correct bisectors here?
    intersector = WaveFrontIntersector(a, b)           #
    bi0 = intersector.get_bisector()
    # print(bi0)
    #
    intersector = WaveFrontIntersector(a, c)           #
    bi1 = intersector.get_bisector()
    # print(bi1)

    # the position of the node is witnessed by 3 pairs of wavefronts
    try:
        intersector = WaveFrontIntersector(a, b)
        pos_at_now = intersector.get_intersection_at_t(now)
    except ValueError:
        pass
    # print("POINT({0[0]} {0[1]})".format(pos_at_now))

    try:
        intersector = WaveFrontIntersector(a, c)
        pos_at_now = intersector.get_intersection_at_t(now)
        # print("POINT({0[0]} {0[1]})".format(pos_at_now))
    except ValueError:
        pass
    try:
        intersector = WaveFrontIntersector(b,c)
        pos_at_now = intersector.get_intersection_at_t(now)
        # print("POINT({0[0]} {0[1]})".format(pos_at_now))            #
    except ValueError:
        pass

    # ---- new use of wavefronts ------------------------------ #

    sk_node, newly_made = stop_kvertices([v], step, now)
    # add the skeleton node to the skeleton
    if newly_made:
        skel.sk_nodes.append(sk_node)
#     assert v1.right is v2
#     assert v2.left is v1

    assert v1.ur is v2.ul

    # pos_vr = v.right.position_at(now)
    # pos_v1 = v1.position_at(now)
    # from grassfire.vectorops import make_vector, mul, add, unit, norm
    # ha = add(v1.position_at(now), mul(make_vector(pos_vr, pos_v1), 0.5)) # pt halfway a

    # pos_vl = v.left.position_at(now)
    # pos_v2 = v2.position_at(now)
    # hb = add(v2.position_at(now), mul(make_vector(pos_vl, pos_v2), 0.5)) # pt halfway b

    # with open('/tmpfast/split_pts_halfway.wkt', 'w') as fh:
    #     fh.write('wkt')
    #     fh.write('\n')
    #     fh.write("POINT({0[0]} {0[1]})".format(v.position_at(now)))
    #     fh.write('\n')
    #     fh.write("POINT({0[0]} {0[1]})".format(ha))
    #     fh.write('\n')
    #     fh.write("POINT({0[0]} {0[1]})".format(hb))
    #     fh.write('\n')
    # print('written out points')

    # # the geometric bisector based on the position of the vertices
    # bi_b = make_vector(hb, v.position_at(now))
    # bi_a = make_vector(ha, v.position_at(now))

    # def sign(scalar):
    #     if scalar < 0:
    #         return -1
    #     elif scalar == 0:
    #         return 0
    #     else:
    #         return 1

    # the position of the stop_node can be computed by:
    # taking the original wavefronts and translate these lines to 'now'
    # then intersect them -> stop_node position
    # maybe this is more robust than relying on the direction vector and the velocity of the original point

    # a bisector based on the original line equations
    # BI = compute_crossing_bisector(v.ul, v2.ul, now)
    vb = compute_new_kvertex(v.ul, v2.ul, now, sk_node, len(skel.vertices) + 1, v.internal or v2.internal, pause)
    # FIXME: new wavefront
    vb.wfl = v.wfl
    vb.wfr = v2.wfl
#     logging.debug("""
# -- BISECTOR BI   {} 
#             bi_b {}
#             vb.v {}""".format(BI, bi_b, vb.velocity)
#     )
    skel.vertices.append(vb)

    # if not vb.inf_fast:
    #     if sign(vb.velocity[0]) != sign(bi_b[0]) or sign(vb.velocity[1]) != sign(bi_b[1]):
    #         vb.velocity = mul(unit(bi_b), norm(vb.velocity))

    if pause:
        logging.debug('split l.194 -- computed new vertex B')
        from grassfire.inout import interactive_visualize
        interactive_visualize(queue, skel, step, now)

    # BI = compute_crossing_bisector(v1.ur, v.ur, now)
    va = compute_new_kvertex(v1.ur, v.ur, now, sk_node, len(skel.vertices) + 1, v.internal or v1.internal, pause)
    va.wfl = v1.wfr
    va.wfr = v.wfr

#     logging.debug("""
# -- BISECTOR BI   {} 
#             bi_a {}
#             va.v {}""".format(BI, bi_a, va.velocity)
#     )
    skel.vertices.append(va)

    if pause:
        logging.debug('split l.211  -- computed new vertex A')
        interactive_visualize(queue, skel, step, now)

    # if not va.inf_fast:
    #     if sign(va.velocity[0]) != sign(bi_a[0]) or sign(va.velocity[1]) != sign(bi_a[1]):
    #         va.velocity = mul(unit(bi_a), norm(va.velocity))

    logging.debug("-- update circular list at B-side: {} [{}]".format(id(vb), vb.info))
    update_circ(v.left, vb, now)
    update_circ(vb, v2, now)

    # FIXME: why do these assertions not hold?
    assert vb.left.wfr is vb.wfl
    assert vb.right.wfl is vb.wfr

    logging.debug("-- update circular list at A-side: {} [{}]".format(id(va), va.info))
    update_circ(v1, va, now)
    update_circ(va, v.right, now)

    logging.debug("-- [{}]".format(va.info))
    logging.debug("   [{}]".format(va.right.info))
    logging.debug("   {}".format(va.right.wfl))
    logging.debug("   {}".format(va.wfr))

    # FIXME: why do these assertions not hold?
    assert va.left.wfr is va.wfl
    assert va.right.wfl is va.wfr

    # updates (triangle fan) at neighbour 1
    b = t.neighbours[(e + 1) % 3]
    assert b is not None
    b.neighbours[b.neighbours.index(t)] = None
    fan_b = replace_kvertex(b, v, vb, now, ccw, queue, immediate)

    if pause:
        logging.debug('split l.243 -- replaced vertex B')
        from grassfire.inout import interactive_visualize
        interactive_visualize(queue, skel, step, now)


    # updates (triangle fan) at neighbour 2
    a = t.neighbours[(e + 2) % 3]
    assert a is not None
    a.neighbours[a.neighbours.index(t)] = None
    fan_a = replace_kvertex(a, v, va, now, cw, queue, immediate)

    if pause:
        logging.debug('split l.255 -- replaced vertex A')
        from grassfire.inout import interactive_visualize
        interactive_visualize(queue, skel, step, now)

    t.stops_at = now

    # handle infinitely fast vertices
    if va.inf_fast:
        handle_parallel_fan(fan_a, va, now, cw, step, skel, queue, immediate, pause)
    if vb.inf_fast:
        handle_parallel_fan(fan_b, vb, now, ccw, step, skel, queue, immediate, pause)

#     # we "remove" the triangle itself

    # def is_infinitely_fast(fan):
    #     times = [tri.event.time if tri.event is not None else -1 for tri in fan]
    #     is_inf_fast = all(map(near_zero, [time - now for time in times]))
    #     if fan and is_inf_fast:
    #         return True
    #     else:
    #         return False
#    is_inf_fast_b = is_infinitely_fast(get_fan(b, v, ccw))
#    is_inf_fast_a = is_infinitely_fast(get_fan(a, v, cw))


    # double check: infinitely fast vertices
    # (might have been missed by adding wavefront vectors cancelling out)
#    if is_inf_fast_a and not va.inf_fast:
#        logging.debug("New kinetic vertex vA: ***Upgrading*** to infinitely fast moving vertex!")
#        va.inf_fast = True
#    if is_inf_fast_b and not vb.inf_fast:
#        logging.debug("New kinetic vertex vB: ***Upgrading*** to infinitely fast moving vertex!")
#        vb.inf_fast = True