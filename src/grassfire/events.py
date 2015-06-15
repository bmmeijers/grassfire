import logging

from operator import add

from tri.delaunay import apex, orig, dest, cw, ccw
from oseq import OrderedSequence

# from grassfire
from primitives import SkeletonNode, KineticVertex
from calc import perp, bisector, rotate180
from collapse import compute_collapse_time
from io import output_kdt

def is_similar(a, b):
    return abs(b - a) <= 1e-12

def compare_event_by_time(one, other):
    # compare by time
    if one.time < other.time: # lt
        return -1
    elif one.time > other.time: # gt
        return 1
    # in case times are equal, compare by id of triangle
    # to be able to find the correct triangle back
    else: # eq
        if -one.triangle.type < -other.triangle.type:
            return -1
        elif -one.triangle.type > -other.triangle.type:
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
    for tri in skel.triangles:
        res = compute_collapse_time(tri)
        print res
        if res is not None:
            q.add(res)
    return q


# ------------------------------------------------------------------------------
# Event handling

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
        msg = "UPDATING " + str( id(t)) + "" + str(v)
        logging.debug(msg)
        side = t.vertices.index(v)
        t.vertices[side] = newv
#         print "updated", id(t), "at", side
#         print "new kinetic vertex:", id(newv)
#         # FIXME: 
#         # Needed: 
#         # access to event list, to find the events for this triangles
#         # and replace them
#         print "removing", t.event
        queue.remove(t.event)
#         print id(t)
        e = compute_collapse_time(t, now)
        if e is not None:
#             print "added", e
            queue.add(e)
        else:
            raise NotImplementedError("not handled")
        t = t.neighbours[direction(side)]

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
#     print "TYPE", t.type
    e = evt.side
    now = evt.time
    v0 = t.vertices[(e) % 3]
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
#     print v0.position_at(now)
#     print v1.position_at(now)
#     print v2.position_at(now)
    if t.type == 3:
        sk_node = stop_kvertices3(v0, v1, v2, now)
        #
        kv = KineticVertex()
        kv.starts_at = now
        kv.start_node = sk_node
        # always stationary from begin
        kv.origin = sk_node.pos
        kv.velocity = (0,0)

        # add to skeleton structure
        skel.sk_nodes.append(sk_node)
        skel.vertices.append(kv)

    elif t.type == 2 and t.neighbours[e] is not None:
        # all 3 sides collapse at the same time
        raise NotImplementedError("problem")
#         sk_node = stop_kvertices3(v0, v1, v2, now)
#         kv = compute_new_kvertex(v2.left, v1.right, now, sk_node)
#         update_circ(kv, v1.right, v2.left, now)
#  
#         # add to skeleton structure
#         skel.sk_nodes.append(sk_node)
#         skel.vertices.append(kv)
#  
#         print kv.origin
#         print kv.velocity
#     #     print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.origin, kv.position_at(now))
#     #     print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.position_at(now),
#     #                                                             map(add, kv.position_at(now), kv.velocity))
#         print "neighbours"
#         print "-" * 20
#         a = t.neighbours[(e+1) % 3]
#         b = t.neighbours[(e+2) % 3]
#         n = t.neighbours[e]
#         print "a.", id(a)
#         print "b.", id(b)
#         print "n.", id(n)
#         print "-" * 20
#         if a is not None:
#             a_idx = a.neighbours.index(t)
#             print "changing neighbour a"
#             print "SIMILAR COLLAPSE TIME", is_similar(a.event.time, now)
#             a.neighbours[a_idx] = b
#             replace_kvertex(a, v2, kv, now, cw, queue)
#         if b is not None:
#             print "changing neighbour b"
#             print "SIMILAR COLLAPSE TIME", is_similar(b.event.time, now)
#             b_idx = b.neighbours.index(t)
#             b.neighbours[b_idx] = a
#             replace_kvertex(b, v1, kv, now, ccw, queue)
#         if n is not None:
#             print "changing neighbour n"
#             n_idx = n.neighbours.index(t)
#             print "ALSO DEAL WITH ", id(n)
#             print "SIMILAR COLLAPSE TIME", is_similar(n.event.time, now)
#             side = n.event.side
#             assert side == n_idx
#     #         tp = n.event.tp
#             # FIXME: schedule immediately
#             # means that we have to remove the triangle from the queue
#             # and for the two other neighbours exchange their two other sides
#             # similar to a/b neighbours above here...
#     #         from primitives import Event
#     #         new = Event(now, n, side, tp)
#             handle_immediately(n, n_idx, queue)
#     #         n.event = new
#     #         queue.add(new)
#     #         n.neighbours[n_idx] = None
#             # schedule_immediately(n) --> find triangle in the event queue!
#         print "updated neighbours"
#         if a is not None:
#             print "a.", a.neighbours[a_idx]
#         if b is not None:
#             print "b.", b.neighbours[b_idx]
#         if n is not None:
#             print "n.", n.neighbours[n_idx]
#         
#         kv = KineticVertex()
#         kv.starts_at = now
#         kv.start_node = sk_node
#         # always stationary from begin
#         kv.origin = sk_node.pos
#         kv.velocity = (0,0)
    
    else:
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
#     #     print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.origin, kv.position_at(now))
#     #     print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.position_at(now),
#     #                                                             map(add, kv.position_at(now), kv.velocity))
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
#             print "changing neighbour a"
#             print "SIMILAR COLLAPSE TIME", is_similar(a.event.time, now)
            a.neighbours[a_idx] = b
            replace_kvertex(a, v2, kv, now, cw, queue)
        if b is not None:
#             print "changing neighbour b"
#             print "SIMILAR COLLAPSE TIME", is_similar(b.event.time, now)
            b_idx = b.neighbours.index(t)
            b.neighbours[b_idx] = a
            replace_kvertex(b, v1, kv, now, ccw, queue)
        if n is not None:
#             print "changing neighbour n"
#             print "SIMILAR COLLAPSE TIME", is_similar(n.event.time, now)
            n_idx = n.neighbours.index(t)
#             print "ALSO DEAL WITH ", id(n)
            side = n.event.side
            assert side == n_idx
    #         tp = n.event.tp
            # FIXME: schedule immediately
            # means that we have to remove the triangle from the queue
            # and for the two other neighbours exchange their two other sides
            # similar to a/b neighbours above here...
    #         from primitives import Event
    #         new = Event(now, n, side, tp)
            handle_immediately(n, n_idx, queue)
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

def handle_immediately(triangle, side, queue):
    """Handle immediately the removal of this triangle as it collapses

    Link the two neighbours to each other
    """
    queue.remove(triangle.event)
    e = side
    t = triangle
    a = t.neighbours[(e+1) % 3]
    b = t.neighbours[(e+2) % 3]
    if a is not None:
        a_idx = a.neighbours.index(t)
        a.neighbours[a_idx] = b
    if b is not None:
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
    triangle.neighbours = [None, None, None]
    triangle.vertices = [None, None, None]

def handle_split_event(evt, skel, queue):
#     print "=" * 20
#     print "Processing split event"
#     print "=" * 20
#     print evt
    t = evt.triangle
    e = evt.side
    now = evt.time
    v = t.vertices[(e) % 3]
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
    sk_node = stop_kvertex(v, now)
    raw_input("Paused, key to continue >>> ")

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
    replace_kvertex(b, v, va, now, ccw, queue)

#     for v in skel.vertices:
#         print "v  ", str(id(v))[-7:]
#         print "v.l", str(id(v.left))[-7:]
#         print "v.r", str(id(v.right))[-7:]
#         print ""
#     output_kdt(skel, now+.1)

# ------------------------------------------------------------------------------
# Flip
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

def event_loop(queue, skel):
    print "=" * 80
    print "Event queue"
    print "=" * 80
    for i, e in enumerate(queue):
        print i, e
    print "=" * 80
#     evt = events[0]
    while queue:
        evt = queue.popleft()
        output_kdt(skel, evt.time-0.05)
        # decide what to do based on event type
        if evt.tp == "edge":
            handle_edge_event(evt, skel, queue)
        elif evt.tp == "flip":
            pass
#             print "SKIP FLIP"
        elif evt.tp == "split":
#             print "SKIP SPLIT"
            handle_split_event(evt, skel, queue)

        raw_input("handled  event, key to continue >>> ")

# if __name__ == "__main__":
#     test_replace_kvertex()