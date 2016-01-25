import logging

from operator import add
from time import sleep

from tri.delaunay import apex, orig, dest, cw, ccw, Edge
from oseq import OrderedSequence

# from grassfire
from grassfire.primitives import SkeletonNode, KineticVertex
from grassfire.calc import perp, bisector, rotate180, vector_mul_scalar,\
    near_zero
from grassfire.collapse import compute_collapse_time, is_close, find_gt
from grassfire.inout import output_kdt, output_edges_at_T, output_triangles_at_T
from grassfire.initialize import check_ktriangles
from grassfire.calc import all_close


def compare_event_by_time(one, other):
    # compare by time
    if one.time < other.time: # lt
        return -1
    elif one.time > other.time: # gt
        return 1
    # in case times are equal, compare by id of triangle
    # to be able to find the correct triangle back
    else: # eq
        if -one.triangle_tp < -other.triangle_tp:
            return -1
        elif -one.triangle_tp > -other.triangle_tp:
            return 1
        else:
            if id(one.triangle) < id(other.triangle):
                return -1
            elif id(one.triangle) > id(other.triangle):
                return 1
            else:
                return 0


def init_event_list(skel):
    """Compute for all kinetic triangles when they will collapse and 
    put them in an OrderedSequence, so that events are ordered properly
    for further processing
    """
    q = OrderedSequence(cmp=compare_event_by_time)
    logging.debug("Calculate events")
    for tri in skel.triangles:
        res = compute_collapse_time(tri, 0, find_gt)
        if res is not None:
            q.add(res)
    return q


# ------------------------------------------------------------------------------
# Event handling

# FIXME: unify by making v a list of vertices?

def stop_kvertex_at_sk_node(v, now, sk_node):
    v.stops_at = now
    v.stop_node = sk_node
    return sk_node

def stop_kvertex(v, now):
    v.stops_at = now
    pos = v.position_at(now)
    sk_node = SkeletonNode(pos)
    v.stop_node = sk_node
    return sk_node

def stop_kvertices2(v1, v2, now):
    v1.stops_at = now
    v2.stops_at = now

    a = v1.position_at(now)
    b = v2.position_at(now)

    pos = tuple(map(lambda x: x*.5, map(add, a, b)))
    sk_node = SkeletonNode(pos)

    v1.stop_node = sk_node
    v2.stop_node = sk_node

    return sk_node

def stop_kvertices3(v0, v1, v2, now):
    # get positions of the 3 vertices
    # (these should be more or less similar!)
    a = v0.position_at(now)
    b = v1.position_at(now)
    c = v2.position_at(now)
    # these vertices stop at time t=now
    v0.stops_at = now
    v1.stops_at = now
    v2.stops_at = now
    # obtain position of new skeleton node
    x = sum([a[0], b[0], c[0]]) / 3.
    y = sum([a[1], b[1], c[1]]) / 3.
    pos = (x, y)
    # make this node
    sk_node = SkeletonNode(pos)
    v0.stop_node = sk_node
    v1.stop_node = sk_node
    v2.stop_node = sk_node
    return sk_node

def compute_new_kvertex(v1, v2, now, sk_node):
    """Based on the two kinetic vertices, time t=now and the skeleton node
    return a new kinetic vertex.
    """
    kv = KineticVertex()
    kv.starts_at = now
    kv.start_node = sk_node
    #
    # FIXME:
    # this makes it difficult to work with the skeleton vertices
    # once the skeleton is constructed completely
    #
    # FIX: we could replace the two kinetic vertices on the left and right
    # and not make a skeleton node --> just two vertices, but this would mean
    # having to update more triangles :(
    # as well and set the old two vertices their start / stop range here
    p1 = v1.position_at(now)
    p2 = v2.position_at(now)
    print "distance", v1.distance2_at(v2, now)
    
    degenerate1 = near_zero(abs(p1[0] - sk_node.pos[0])) and \
                    near_zero(abs(p1[1] - sk_node.pos[1]))
    
    degenerate2 = near_zero(abs(p2[0] - sk_node.pos[0])) and \
                    near_zero(abs(p2[1] - sk_node.pos[1]))

    degenerate3 = near_zero(abs(p1[0] - p2[0])) and \
                    near_zero(abs(p1[1] - p2[1]))

    print ">>>", p1, sk_node.pos, p2

    print p1[0] - sk_node.pos[0]
    print p1[1] - sk_node.pos[1]
    print p2[0] - sk_node.pos[0]
    print p2[1] - sk_node.pos[1]

    print degenerate1, degenerate2, degenerate3
    
    if degenerate1 or degenerate2 or degenerate3:
        pos_at_t0 = sk_node.pos
        velo = (0, 0)
    else:
        velo = bisector(p1, sk_node.pos, p2)
        # compute position at t=0, rotate bisector 180 degrees
        # and get the position 
        negvelo = rotate180(velo)
        pos_at_t0 = (sk_node.pos[0] + negvelo[0] * now,
                     sk_node.pos[1] + negvelo[1] * now)
    kv.origin = pos_at_t0
    kv.velocity = velo
    return kv

def replace_kvertex(t, v, newv, now, direction, queue):
    while t is not None:
        logging.debug("UPDATING " + str( id(t)) + " " + str(v))
        side = t.vertices.index(v)
        t.vertices[side] = newv
#         print "updated", id(t), "at", side
#         print "new kinetic vertex:", id(newv)
#         # FIXME: 
#         # Needed: 
#         # access to event list, to find the events for this triangles
#         # and replace them
#         print "removing", t.event
        replace_in_queue(t, now, queue)
        t = t.neighbours[direction(side)]

def replace_in_queue(t, now, queue):
    if t.event != None:
        queue.discard(t.event)
    else:
        logging.debug("triangle #{0} without event not removed from queue".format(id(t)))
    e = compute_collapse_time(t, now)
    if e is not None:
        queue.add(e)
    else:
        return

def update_circ(kv, v1, v2, now):
    # update circular list:
    #               <-----v2
    #    <----- kv ----->       
    # v1 ---->    
    kv.left = v1, now
    kv.right = v2, now

    v1.right = kv, now
    v2.left = kv, now

def handle_edge_event(evt, skel, queue):
#     print "=" * 20
#     print "Processing edge event"
#     print "=" * 20
#     print evt
    t = evt.triangle
#     if not t.is_finite:
#         logging.debug("skipping handling of infinite triangle")
#         return
#     print "TYPE", t.type
    logging.debug(evt.side)
    e = evt.side[0] # pick first side
    now = evt.time
    v0 = t.vertices[(e) % 3]
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
#     print v0.position_at(now)
#     print v1.position_at(now)
#     print v2.position_at(now)
    if t.type == 3:
        # add to skeleton structure
        sk_node = stop_kvertices3(v0, v1, v2, now)
        skel.sk_nodes.append(sk_node)
        # we could make a kinetic vertex, but it will not have any
        # circular references, making it slightly complicated for the
        # offsetting functions
        # Let's not generate it for now, and investigate later whether 
        # we would need a kinetic vertex (or that we should build the tree of
        # skeleton nodes in some different fashion)
        #kv = KineticVertex()
        #kv.starts_at = now
        #kv.start_node = sk_node
        # always stationary from begin
        #kv.origin = sk_node.pos
        #kv.velocity = (0,0)
        #skel.vertices.append(kv)

    elif len(evt.side) != 1:
        raise NotImplementedError("Problem with multiple sides collapsing not there yet")

    elif t.type == 2 and t.neighbours[e] is not None:
        logging.debug("handle event for 2 triangle that collapses completely")
        # all 3 sides collapse at the same time
#         raise NotImplementedError("problem")
        print "v0", id(v0)
        print "v1", id(v1)
        print "v2", id(v2)
        print "v1.right", id(v1.right)
        print "v2.left", id(v2.left)
        sk_node = stop_kvertices3(v0, v1, v2, now)
        print "POSITION", sk_node.pos
        kv = compute_new_kvertex(v2.left, v1.right, now, sk_node)
        update_circ(kv, v2.left, v1.right, now)
        # add to skeleton structure
        skel.sk_nodes.append(sk_node)

        # FIXME: No new vertex here that continues??? 
        # -> depends on type of the neighbour!
        # -> this should happen when neighbour is 0 or 1 triangle
        # but not when it is 2 triangle
        # skel.vertices.append(kv)

#         print kv.origin
#         print kv.velocity
#         print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.origin, kv.position_at(now))
#         print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.position_at(now),
#                                                                 map(add, kv.position_at(now), kv.velocity))
#         print "neighbours"
#         print "-" * 20
        a = t.neighbours[(e+1) % 3]
        b = t.neighbours[(e+2) % 3]
        n = t.neighbours[e]
        assert a is None
        assert b is None
        assert n is not None
        print "a.", id(a)
        print "b.", id(b)
        print "n.", id(n)
        n_idx = n.neighbours.index(t)
        if n.type == 0:
            if n.event != None:
                queue.discard(n.event)
            logging.debug("2-triangle, also dealing with 0-triangle neighbour")
            skel.vertices.append(kv)
            replace_kvertex(n, v1, kv, now, cw, queue)
            replace_kvertex(n, v2, kv, now, ccw, queue)
            # we have a neighbouring 0 triangle
            # that collapses at side `n_idx`
            n0 = n.neighbours[(n_idx) % 3]
            n1 = n.neighbours[(n_idx+1) % 3]
            n2 = n.neighbours[(n_idx+2) % 3]
            assert n0 is t
            n1_side = n1.neighbours.index(n)
            n2_side = n2.neighbours.index(n)
            n1.neighbours[n1_side] = n2
            n2.neighbours[n2_side] = n1
            n.neighbours = [None, None, None]
            n.vertices = [None, None, None]
            skel.triangles.remove(n)

        elif n.type == 2:
            # handle adjacent 2 triangle
            # as this is a 2 triangle, 
            # the neighbour 2-triangle also should collapse to point
            logging.debug("2-triangle, also dealing with 2-triangle neighbour")
            assert n.event != None
            queue.discard(n.event)
            # we have a neighbouring 2 triangle
            # that collapses at side `n_idx`
            n0 = n.neighbours[(n_idx) % 3]
            n1 = n.neighbours[(n_idx+1) % 3]
            n2 = n.neighbours[(n_idx+2) % 3]
            assert n0 is t
            assert n1 is None
            assert n2 is None
            # the vertex opposite of collapsed edge in neighbour
            still_moving = n.vertices[n_idx]
            stop_kvertex_at_sk_node(still_moving, now, sk_node)
            skel.triangles.remove(n)

        elif n.event != None:
            replace_in_queue(n, n.event.time, queue)
#             assert side == n_idx
    #         tp = n.event.tp
            # FIXME: schedule immediately
            # means that we have to remove the triangle from the queue
            # and for the two other neighbours exchange their two other sides
            # similar to a/b neighbours above here...
    #         from primitives import Event
    #         new = Event(now, n, side, tp)
            #handle_immediately(n, n_idx, queue)
    #         n.event = new
    #         queue.add(new)
    #         n.neighbours[n_idx] = None
            # schedule_immediately(n) --> find triangle in the event queue!
#         print "updated neighbours"
#         if a is not None:
#             print "a.", a.neighbours[a_idx]
#         if b is not None:
#             print "b.", b.neighbours[b_idx]
#         if n is not None:
#             print "n.", n.neighbours[n_idx]
        kv = KineticVertex()
        kv.starts_at = now
        kv.start_node = sk_node
        # always stationary from begin
        kv.origin = sk_node.pos
        kv.velocity = (0,0)

    else:
        # FIXME:
        # This part now handles type 2, type 1 and type 0 triangles
        #

        # assert t.type == 1
        # -- find out whether we have a wavefront edge that collapses
        # or a spoke that collapses. A spoke collapsing means that
        # we have to detach the neighbour and duplicate
        # the kinetic vertices... (see Figure 8 / 9 on page 19)
#         print "COMING HERE"
        sk_node = stop_kvertices2(v1, v2, now)
#         print "v1      ", id(v1)
#         print "v2      ", id(v2)
#         print "v1.left ", id(v1.left)
#         print "v2.right", id(v2.right)

        if False:
            P = [v1.position_at(now),
                 v2.position_at(now),
                 v1.left.position_at(now),
                 v2.right.position_at(now)]
            for p in P:
                dx = p[0] - sk_node.pos[0]
                dy = p[1] - sk_node.pos[1]
                print dx
                print dy

        kv = compute_new_kvertex(v1.left, v2.right, now, sk_node)
        # update circular list
        update_circ(kv, v1.left, v2.right, now)

        # add to skeleton structure
        skel.sk_nodes.append(sk_node)
        skel.vertices.append(kv)

#         print kv.origin
#         print kv.velocity
#         print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.origin, kv.position_at(now))
#         print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.position_at(now),
#                                                                 map(add, kv.position_at(now), kv.velocity))
#         print "neighbours"
#         print "-" * 20
        a = t.neighbours[(e+1) % 3]
        b = t.neighbours[(e+2) % 3]
        n = t.neighbours[e]
#         print "a.", id(a)
#         print "b.", id(b)
#         print "n.", id(n)
#         print "-" * 20
        if a is not None:
            a_idx = a.neighbours.index(t)
            print "changing neighbour a to", b
#             print "SIMILAR COLLAPSE TIME", is_similar(a.event.time, now)
            a.neighbours[a_idx] = b
            replace_kvertex(a, v2, kv, now, cw, queue)
        if b is not None:
#             print "changing neighbour b"
#             print "SIMILAR COLLAPSE TIME", is_similar(b.event.time, now)
            b_idx = b.neighbours.index(t)
            print "changing neighbour b to", a
            b.neighbours[b_idx] = a
            replace_kvertex(b, v1, kv, now, ccw, queue)
        if n is not None:
#             print "changing neighbour n"
#             print "SIMILAR COLLAPSE TIME", is_similar(n.event.time, now)
            n_idx = n.neighbours.index(t)
#             print "ALSO DEAL WITH ", id(n)
            print "SHOULD DO SOMETHING HERE (~ l.345)"
            print "neighbour = ", id(n), n.event
#             side = n.event.side
#             assert side == n_idx
    #         tp = n.event.tp
            # FIXME: schedule immediately
            # means that we have to remove the triangle from the queue
            # and for the two other neighbours exchange their two other sides
            # similar to a/b neighbours above here...
    #         from primitives import Event
    #         new = Event(now, n, side, tp)
#             handle_immediately(n, n_idx, queue)
    #         n.event = new
    #         queue.add(new)
#             n.neighbours[n_idx] = None
            schedule_immediately(n, now, queue)
#             handle_immediately(triangle, side, queue)# --> find triangle in the event queue!
#         print "updated neighbours"
#         if a is not None:
#             print "a.", a.neighbours[a_idx]
#         if b is not None:
#             print "b.", b.neighbours[b_idx]
#         if n is not None:
#             print "n.", n.neighbours[n_idx]
#     t.neighbours = [None, None, None]
#     t.vertices = [None, None, None]
    skel.triangles.remove(t)
#     raw_input("PAUSED (~l.391)")


def schedule_immediately(triangle, now, queue):
    """ Make sure that triangle is at top of event queue for next iteration"""
    if triangle.event != None:
        queue.remove(triangle.event)
        event = triangle.event
        event.time = now
        queue.add(triangle.event)
    else:
        logging.debug("No event for triangle {0} to schedule immediately!!!".format(id(triangle)))

# def handle_immediately(triangle, now, queue):
#     """Handle immediately the removal of this triangle as it collapses
# 
#     Link the two neighbours to each other
#     """
# #     print "handling immediately event", triangle.event
#     queue.remove(triangle.event)
#     event = triangle.event
#     event.time = now
#     queue.add(triangle.event)
# #     e = side
# #     t = triangle
# #     a = t.neighbours[(e+1) % 3]
# #     b = t.neighbours[(e+2) % 3]
# #     if a is not None:
# #         a_idx = a.neighbours.index(t)
# #         a.neighbours[a_idx] = b
# #     if b is not None:
# #         b_idx = b.neighbours.index(t)
# #         b.neighbours[b_idx] = a

def handle_split_event(evt, skel, queue):
#     print "=" * 20
#     print "Processing split event"
#     print "=" * 20
#     print evt
    t = evt.triangle
    assert len(evt.side) == 1
    e = evt.side[0]
    now = evt.time
    v = t.vertices[(e) % 3]
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
    sk_node = stop_kvertex(v, now)
#     raw_input("Paused, key to continue >>> ")

    assert v1.right is v2
    assert v2.left is v1

    vb = compute_new_kvertex(v.left, v2, now, sk_node)
#     print """
#     
#     
#     """
#     for pt in [vb.position_at(now), v.left.position_at(now), v2.position_at(now)]:
#         print "POINT({0[0]} {0[1]})".format(pt)
    va = compute_new_kvertex(v1, v.right,  now, sk_node)
#     print """
#     
#     
#     """
#     for pt in [va.position_at(now), v.right.position_at(now), v1.position_at(now)]:
#         print "POINT({0[0]} {0[1]})".format(pt)

    # splice circular list into 2 lists here
    update_circ(vb, v.left, v2, now)
    update_circ(va, v1, v.right, now)

    skel.sk_nodes.append(sk_node)
    skel.vertices.append(va)
    skel.vertices.append(vb)

    # update neighbours
    a = t.neighbours[(e+1)%3]
    a.neighbours[a.neighbours.index(t)] = None
    replace_kvertex(a, v, vb, now, ccw, queue)

    b = t.neighbours[(e+2)%3]
    b.neighbours[b.neighbours.index(t)] = None
    replace_kvertex(b, v, va, now, cw, queue)

    t.neighbours = [None, None, None]
    t.vertices = [None, None, None]
    skel.triangles.remove(t)

#     for v in skel.vertices:
#         print "v  ", str(id(v))[-7:]
#         print "v.l", str(id(v.left))[-7:]
#         print "v.r", str(id(v.right))[-7:]
#         print ""
#     output_kdt(skel, now+.1)

# ------------------------------------------------------------------------------
# Flip

def handle_flip_event(evt, skel, queue):
    """Take the two triangles that need to be flipped, flip them and replace
    their time in the event queue
    """
    now = evt.time
    assert len(evt.side) == 1
    t, s = evt.triangle, evt.side[0]
    n = t.neighbours[s]
    ns = n.neighbours.index(t)
    flip(t, s, n, ns)
    replace_in_queue(t, now, queue)
    replace_in_queue(n, now, queue)
    logging.debug("flip event handled")

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
    A, B, C, D = t0.vertices[apex0], t0.vertices[orig0], t1.vertices[apex1], t0.vertices[dest0]
    # -- triangles around quadrilateral in ccw order, starting at A
    AB, BC, CD, DA = t0.neighbours[dest0], t1.neighbours[orig1], t1.neighbours[dest1], t0.neighbours[orig0]

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
    # -- update coordinate to triangle pointers
#     for v in t0.vertices:
#         v.triangle = t0
#     for v in t1.vertices:
#         v.triangle = t1

def event_loop(queue, skel, pause=False):
    def visualize(queue, skel, NOW):
        with open('/tmp/queue.wkt', 'w') as fh:
            fh.write("pos;wkt;evttype;evttime;tritype;id;n0;n1;n2;finite\n")
            for i, evt in enumerate(queue):
                fh.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}\n".format(
                        i,
                        evt.triangle.str_at(NOW),
                        evt.tp,
                        evt.time,
                        evt.triangle.type,
                        id(evt.triangle),
                        id(evt.triangle.neighbours[0]),
                        id(evt.triangle.neighbours[1]),
                        id(evt.triangle.neighbours[2]),
                        evt.triangle.is_finite,
                    )
                )
        with open('/tmp/ktri_progress.wkt', 'w') as fh:
            output_triangles_at_T(skel.triangles, NOW, fh)
#             fh.write("pos;wkt;evttype;tritype;id;n0;n1;n2\n")
#             for i, triangle in enumerate(skel.triangles):
# #                 if not triangle.finite:
# #                     continue
#                 if triangle.event is None:
#                     continue
#                 if triangle.event.tp is None:
#                     continue
#                 fh.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(
#                         i,
#                         triangle.str_at(NOW),
#                         triangle.event.tp,
#                         triangle.type,
#                         id(triangle),
#                         id(triangle.neighbours[0]),
#                         id(triangle.neighbours[1]),
#                         id(triangle.neighbours[2]),
#                     )
#                 )
        with open("/tmp/sknodes_progress.wkt", 'w') as fh:
            fh.write("wkt\n")
            for node in skel.sk_nodes:
                fh.write("POINT({0[0]} {0[1]})\n".format(node.pos))
        with open("/tmp/bisectors_progress.wkt", "w") as bisector_fh:
            bisector_fh.write("wkt\n")
            for kvertex in skel.vertices:
                if kvertex.stops_at is None:
                    p1 = kvertex.position_at(NOW)
                    bi = kvertex.velocity
                    bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(p1, map(add, p1, vector_mul_scalar
                                                                                                  (bi, 0.1))))
        with open("/tmp/segments_progress.wkt", "w") as fh:
            fh.write("wkt;finished\n")
            for kvertex in skel.vertices:
                if kvertex.start_node is not None and kvertex.stop_node is not None:
                    start, end = kvertex.start_node.pos, kvertex.stop_node.pos
                    fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2}\n".format(start, end, True))
                elif kvertex.start_node is not None and kvertex.stop_node is None:
                    start, end = kvertex.start_node.pos, kvertex.position_at(NOW)
                    fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2}\n".format(start, end, False))
                    
#         with open("/tmp/vertices0_progress.wkt", 'w') as fh0:
        with open("/tmp/vertices1_progress.wkt", 'w') as fh1:
#             fh0.write("id;wkt\n")
            fh1.write("id;wkt\n")
            for kvertex in skel.vertices:
#                     if kvertex.start_node is not None and kvertex.stop_node is not None:
#                         fh0.write("{1};POINT({0[0]} {0[1]})\n".format(kvertex.position_at(kvertex.starts_at), id(kvertex)))
#                     else:
                if kvertex.stop_node is None:
                    fh1.write("{1};POINT({0[0]} {0[1]})\n".format(kvertex.position_at(NOW), id(kvertex)))
        with open("/tmp/wavefront_edges_progress.wkt", "w") as fh:
            edges = []
            for tri in skel.triangles:
                sides = []
                for i, ngb in enumerate(tri.neighbours):
                    if ngb is None:
                        sides.append(i)
                for side in sides:
                    edges.append(Edge(tri, side))
            output_edges_at_T(edges, NOW, fh)
    NOW = prev_time = 0.01
    visualize(queue, skel, prev_time)
    for e in queue:
            print e.time.as_integer_ratio(), e
    print "visualize start"
#     if pause:
#         raw_input("paused at start")
    while queue:
#         print queue
        peek = next(iter(queue))
#         print peek.time
        NOW = peek.time

        if pause:
            for file_nm in [
                    "/tmp/sknodes_progress.wkt",
                    "/tmp/bisectors_progress.wkt",
                    "/tmp/segments_progress.wkt",
                    '/tmp/queue.wkt', # also contains next triangle to be visualised!
                    "/tmp/vertices0_progress.wkt",
                    "/tmp/vertices1_progress.wkt",
                    '/tmp/ktri_progress.wkt',
                ]:
                with open(file_nm, 'w') as fh:
                    pass
#         visualize(queue, skel, NOW-0.001)
        # log what is in the queue
        
        if False:
            if peek.tp == "flip":
                ct = 1
            else:
                ct = 20
            # -- use this for getting progress visualization
            delta = NOW - prev_time
            if near_zero(delta):
                ct = 1
            step_time = delta / ct
            for i in range(ct -1):
                prev_time += step_time
                visualize(queue, skel, prev_time + step_time)
                sleep(1.)
        visualize(queue, skel, NOW)
        prev_time = NOW
        logging.info("=" * 80)
        for i, e in enumerate(queue):
            logging.info("{0:5d} {1}".format(i, e))
        logging.info("=" * 80)

#         if pause:
#             raw_input('paused before handling event: ' + str(NOW))
#         simultaneous = []
#         for i, evt in enumerate(queue):
#             positions = []
#             for v in evt.triangle.vertices:
#                 positions.append(v.position_at(peek.time))
#             X = [p[0] for p in positions]
#             Y = [p[1] for p in positions]
#             if all_close(X, rtol=0, atol=1e-5) and all_close(Y, rtol=0, atol=1e-5):
#                 print i, id(evt.triangle), "collapses to point", sum(X) / len(X), sum(Y) / len(Y)
#                 simultaneous.append((evt, (sum(X) / len(X), sum(Y) / len(Y))))
#         X = [pt[0] for _, pt in simultaneous]
#         Y = [pt[1] for _, pt in simultaneous]
#         if all_close(X, rtol=0, atol=1e-5) and all_close(Y, rtol=0, atol=1e-5):
#             print "all watching same event"
#             print (round(sum(X) / len(X), 9), round(sum(Y) / len(Y), 9))
#             print [evt for evt, _ in simultaneous]
# 
#         if pause:
#             peek = next(iter(queue))
#             with open('/tmp/queue.wkt', 'w') as fh:
#                 fh.write("pos;wkt;evttype;tritype;id;n0;n1;n2\n")
#                 for i, evt in enumerate(queue):
#                     fh.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(
#                             i,
#                             evt.triangle.str_at(peek.time),
#                             evt.tp,
#                             evt.triangle.type,
#                             id(evt.triangle),
#                             id(evt.triangle.neighbours[0]),
#                             id(evt.triangle.neighbours[1]),
#                             id(evt.triangle.neighbours[2]),
#                         )
#                     )
#             raw_input("Time: " + str(peek.time) + ", key to continue >>> ")
        evt = queue.popleft()
#         output_kdt(skel, evt.time-0.05)
        # decide what to do based on event type
        logging.debug("Handling event " +str(evt.tp) + " " + str(evt.triangle.type) + " " + str(id(evt.triangle)) + " at time " + "{0:.28g}".format(evt.time))
        if evt.tp == "edge":
            handle_edge_event(evt, skel, queue)
        elif evt.tp == "flip":
            handle_flip_event(evt, skel, queue)
#             print "SKIP FLIP"
        elif evt.tp == "split":
#             print "SKIP SPLIT"
            handle_split_event(evt, skel, queue)

#         print "Number of skel nodes", len(skel.sk_nodes)

#         try:
        check_ktriangles(skel.triangles, NOW)
        visualize(queue, skel, NOW)
        print NOW
        for e in queue:
            print e.time.as_integer_ratio(), e
        print "after"
#             raw_input("paused")
        #         except AssertionError:
#             print "PROBLEM"
#         except ValueError:
#             print "PROBLEM"
# if __name__ == "__main__":
#     test_replace_kvertex()
    visualize(queue, skel, NOW+10)