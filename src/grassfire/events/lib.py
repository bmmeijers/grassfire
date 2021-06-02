# -*- coding: utf-8 -*-
import logging

from grassfire.primitives import SkeletonNode, KineticVertex

from grassfire.collapse import compute_collapse_time, \
    compute_new_edge_collapse_event
from grassfire.calc import near_zero, is_close
from grassfire.vectorops import mul, add, bisector, dist
from grassfire.inout import notify_qgis, interactive_visualize

# ------------------------------------------------------------------------------
# Functions common for event handling


def is_infinitely_fast(fan, now):
    """Determine whether all triangles in the fan collapse
    at the same time, if so, the vertex needs to be infinitely fast"""
    times = [tri.event.time if tri.event is not None else -1 for tri in fan]
    is_inf_fast = all(map(near_zero, [time - now for time in times]))
    if fan and is_inf_fast:
        return True
    else:
        return False


def stop_kvertices(V, step, now, pos=None):
    """ Stop a list of kinetic vertices *V* at time *now*, creating a new node.

    If one of the vertices was already stopped before, at a node, use that
    skeleton node

    Returns tuple of (new node, False) in case all vertices are stopped for the
    first time, otherwise it returns (node, True) to indicate that were already
    stopped once.
    """
    # precondition:
    # the kinetic vertices that we are stopping should be
    # at more or less the same location
#     assert at_same_location(V, now)
    sk_node = None

    logging.debug("stopping kinetic vertices, @t:={}".format(now))
    for v in V:
        logging.debug(" - kv #{} [{}] inf-fast:={}".format(id(v), v.info, v.inf_fast))

    for v in V:
        stopped = v.stops_at is not None
        time_close = near_zero(v.starts_at - now)
        logging.debug("Vertex starts at same time as now: {}".format(time_close))
        logging.debug("Kinetic vertex is not stopped: {}".format(stopped))
        # vertex already stopped
        if stopped:
            logging.debug("Stop_node of vertex")
            sk_node = v.stop_node
        elif time_close:
            logging.debug("Time close")
            # FIXME: for the parallel case this code is problematic
            # as start and end point will be at same time
            assert not stopped
            sk_node = v.start_node
        else:
            v.stops_at = now
    if sk_node is not None:
        logging.debug("Skeleton node already there")
        for v in V:
            v.stop_node = sk_node
            v.stops_at = now
            # FIXME: it is not always true that vertices stopped this way
            # are at the same location (they are close, but because of
            # numerical issues can be on slightly different location
            # assert at_same_location([v, sk_node], now)
        is_new_node = False
    else:
        if pos is None:
            logging.debug("Make new skeleton node")
            l = [v.position_at(now) for v in V]
            ct = len(l)
            sumx, sumy = 0., 0.
            for x, y in l:
                sumx += x
                sumy += y
            pos = sumx / ct, sumy / ct
#        for x, y in l:
#            dx, dy = near_zero(x - pos[0]), near_zero(y - pos[1])
#            assert dx, x - pos[0]
#            assert dy, y - pos[1]
        else:
            logging.debug("Make new skeleton node - using external position: {}".format(pos))
        sk_node = SkeletonNode(pos, step)
        for v in V:
            v.stop_node = sk_node
        is_new_node = True
    # post condition
    # all vertices do have a stop node and are stopped at a certain time
    for v in V:
        assert v.stop_node is not None
        assert v.is_stopped == True
        assert v.stops_at == now

    logging.debug("POINT({0[0]} {0[1]});sknode_new_pos".format(sk_node.pos))

        # the geometric embedding of the vertex and its direction should correspond
        # only check when speed is relatively small
###        if abs(v.velocity[0]) < 100 and abs(v.velocity[1]) < 100:
###            d = dist(
###                v.stop_node.position_at(v.stops_at),
###                v.position_at(v.stops_at),
###            )
###            assert is_close(d, 0.0, rel_tol=1e-2, abs_tol=1e-2, method="weak"), \
###            "mis-match between position of skeleton and position of kinetic vertex at time:" \
###            " {}; vertex {} [{}]; dist:={}, v.velocity={}".format(v.stops_at, id(v), v.info, d, v.velocity)

        # FIXME:
        # should all segments in the skeleton have length
        # or do we keep a topological tree of events (where nodes
        # can be embedded at same location) ???
        # assert not at_same_location([v.start_node, v.stop_node], now), "stopped nodes should be different, but are not for {0}".format(id(v))
    return sk_node, is_new_node


def compute_new_kvertex(ul, ur, now, sk_node, info, internal, pause=False):
    """Based on the two wavefront directions and time t=now, compute the
    velocity and position at t=0 and return a new kinetic vertex

    Returns: KineticVertex
    """
    kv = KineticVertex()
    kv.info = info
    kv.starts_at = now
    kv.start_node = sk_node
    kv.internal = internal

    logging.debug('/=-= New vertex: {} [{}] =-=\\'.format(id(kv), kv.info))
    logging.debug('bisector calc')
    logging.debug(' ul: {}'.format(ul))
    logging.debug(' ur: {}'.format(ur))
    logging.debug(' sk_node.pos: {}'.format(sk_node.pos))

    # FIXME: only in pause mode!
    from grassfire.vectorops import angle_unit, add
    import math
    logging.debug(' >>> {}'.format(angle_unit(ul.w, ur.w)))
    u1, u2 = ul.w, ur.w
    direction = add(u1, u2)
    logging.debug(" direction: {}".format(direction))
    d, acos_d = angle_unit(u1, u2)

# FIXME: replace with new api: line.at_time(0).visualize()  //  line.at_time(t).visualize()
    if pause:
        with open('/tmpfast/support_lines.wkt', 'w') as fh:
            from grassfire.inout import interactive_visualize
            fh.write("wkt\tlr\toriginal")
            fh.write("\n")

            # -- bisector line --
            # b = ul.bisector(ur)
            b = ul.translated(mul(ul.w,now)).bisector( ur.translated(mul(ur.w,now)) )
            bperp = b.perpendicular(sk_node.pos)

            for l, lr, original in zip([ul, ur, ul.translated(mul(ul.w,now)), ur.translated(mul(ur.w,now)), b, bperp], ["l", "r", "l", "r", "b", "b"], [True, True, False, False, None, None]):
                fh.write(l.at_time(0).visualize())
                fh.write("\t")
                fh.write(lr)
                fh.write("\t")
                fh.write(str(original))
                fh.write("\n")


    # check for parallel wavefronts
    if all(map(near_zero, direction)) or near_zero(acos_d - math.pi) or d < math.cos(math.radians(179.999999)):
        logging.debug(" OVERRULED - vectors cancel each other out / angle ~180° -> parallel wavefront!")
        bi = (0, 0)
    else:
        from grassfire.line2d import LineLineIntersector, make_vector, LineLineIntersectionResult
        intersect = LineLineIntersector(ul, ur)
        tp = intersect.intersection_type()
        if tp == LineLineIntersectionResult.NO_INTERSECTION:
            bi = (0, 0)
        elif tp == LineLineIntersectionResult.POINT:
            pos_at_t0 = intersect.result
            ul_t = ul.translated(ul.w)
            ur_t = ur.translated(ur.w)
            intersect_t = LineLineIntersector(ul_t, ur_t)
            assert intersect_t.intersection_type() == 1
            bi = make_vector(end=intersect_t.result, start=pos_at_t0)
        elif tp == LineLineIntersectionResult.LINE:
            # this would mean original overlapping wavefronts... 
            # -> parallel at left / right of a kvertex
            # FIXME: would it be possible here to get to original position that defined the line?
            bi = tuple(ul.w[:])
            neg_velo = mul(mul(bi, -1.0), now)
            pos_at_t0 = add(sk_node.pos, neg_velo)

    kv.velocity = bi #was: bisector(ul, ur)
    logging.debug(' kv.velocity: {}'.format(kv.velocity))
    from grassfire.vectorops import norm
    magn_v = norm(kv.velocity)
    logging.debug(' magnitude of velocity: {}'.format(magn_v))
    logging.debug('\=-= New vertex =-=/')

    # if magn_v > 1000000:
    #     logging.debug(" OVERRULED - super fast vertex angle ~180° -> parallel wavefront!")
    #     kv.velocity = (0,0)

    
    # compute where this vertex would have been at time t=0
    # we set this vertex as infinitely fast, if velocity in one of the
    # directions is really high, or when the bisectors of adjacent
    # wavefronts cancel each other out
    if kv.velocity == (0, 0): ### or abs(kv.velocity[0]) > 100 or abs(kv.velocity[1]) > 100:
        kv.inf_fast = True
        kv.origin = sk_node.pos
    else:
#        neg_velo = mul(mul(kv.velocity, -1.0), now)
#        pos_at_t0 = add(sk_node.pos, neg_velo)
        kv.origin = pos_at_t0
    kv.ul = ul
    kv.ur = ur
    return kv


def get_fan(t, v, direction):
    """Gets a list of triangles that are the fan of 
    vertex *v*, while turning *direction*, starting at triangle *t*

    This function assumes that the fan is finite (i.e. passes
    a triangle that has as neighbour = None (wavefront))
    """
    fan = []
    start = t
    while t is not None:
        side = t.vertices.index(v)
        fan.append(t)
        t = t.neighbours[direction(side)]
        assert t is not start # prevent infinite loops
    return fan


def replace_kvertex(t, v, newv, now, direction, queue, immediate):
    """Replace kinetic vertex at incident triangles

    Returns fan of triangles that were replaced
    """
    logging.debug("replace_kvertex, start at: {0} [{1}] dir: {2}".format(id(t), t.info, direction))
    fan = []
    first = True
    while t is not None:
        # assert t.stops_at is None, "{}: {}".format(
        #     id(t), [id(n) for n in t.neighbours])
        logging.debug(" @ {} [{}]".format(id(t), t.info))
        # FIXME:
        # if we have an event with the same time as now,
        # we should actually handle it
        logging.debug(t.event)
        if t.event is not None and near_zero(now - t.event.time):
            logging.debug(near_zero(now - t.event.time))
            logging.debug(""" 
            
            SAME SAME TIME... ARE WE PARALLEL?
            
            """)
            if t.event.tp == 'flip':
                logging.debug(t.neighbours[t.event.side[0]]) # -- can have become None
                # raw_input
                # if t.neighbours.count(None) < 2:
                logging.error('Error with current event -- as we do not handle flip now, we run the risk of inconsistency -- in fan: {0} $'.format(t.event))
                    # raw_input('paused $$')

        side = t.vertices.index(v)
        fan.append(t)
        t.vertices[side] = newv
        logging.debug(
            "Placed vertex #{} [{}] (inf fast? {}) at side {} of triangle {} [{}]".format(
                # id(newv),
                #repr(newv),
                id(newv),
                newv.info,
                newv.inf_fast, 
                side,
                id(t),
                t.info
                # , repr(t)
                ))
        if newv.inf_fast and t.event is not None:  # infinitely fast
            queue.discard(t.event)
            if t.event in immediate:
                immediate.remove(t.event)
        else:  # vertex moves with normal speed
            replace_in_queue(t, now, queue, immediate)
        t = t.neighbours[direction(side)]
    return tuple(fan)


def replace_in_queue(t, now, queue, immediate):
    """Replace event for a triangle in the queue """
    if t.event is not None:
        queue.discard(t.event)
        if t.event in immediate:
            immediate.remove(t.event)
    else:
        logging.debug(
            "triangle #{0} without event not removed from queue".format(
                id(t)))

###    logging.debug(" collapse time computation for: {}".format(str(repr(t)).replace(",",",\n\t")))
    e = compute_collapse_time(t, now)
    if e is not None:
        # if t.info in (548,550):
        #     logging.debug("""
        #     >>>
        #     """)
        logging.debug("new event in queue {}".format(e))
        queue.add(e)
    else:
        logging.debug("no new events".format(e))
        return


def update_circ(v_left, v_right, now):
    """Update neighbour list of kinetic vertices (this is a circular list going
    around the wavefront edges

    Note that for a vertex often 2 sides need to be updated.
    """
    # update circular list, as follows:
    #                <-
    # v_left.right o    o v_right.left
    #                ->
    if v_left is not None:
        logging.debug("update_circ at right of #{} [{}] lies #{} [{}]".format(
                                                  id(v_left),
                                                  v_left.info,
                                                  id(v_right),
                                                  v_right.info if v_right is not None else ""))
        v_left.right = v_right, now
    if v_right is not None:
        logging.debug("update_circ at left  of #{} [{}] lies #{} [{}]".format(
                                                  id(v_right),
                                                  v_right.info,
                                                  id(v_left),
                                                  v_left.info if v_left is not None else ""))
        v_right.left = v_left, now


def schedule_immediately(tri, now, queue, immediate):
    """Schedule a triangle for immediate processing

    Computes a new event for the triangle, where we only check
    how the triangle collapses (look at side lengths at time=now);
    it is assumed that the triangle collapses (neighbor relations say so)!

    The original event is removed from the event queue and the new
    event is added to the immediate queue.

    """
    logging.debug("Scheduling triangle [{}] for direct collapse".format(tri.info))

    # FIXME: should we not look at just the other side of the triangle?
    # so, make explicit which side of this triangle now collapses?

    # remove from global queue
    queue.discard(tri.event)
    if tri.event in immediate:
        immediate.remove(tri.event)
    # compute new event and put in immediate queue
    E = compute_new_edge_collapse_event(tri, now)
    tri.event = E
    # if we have no neighbors around, then no matter what, all 3 sides will
    # collapse (overrides what is determined by compute_new_edge_collapse_event)
    ### FIXME: bug? disable?
    if tri.neighbours.count(None) == 3:
        tri.event.side = list(range(3))
    ###
    assert len(tri.event.side) > 0
    immediate.append(tri.event)
