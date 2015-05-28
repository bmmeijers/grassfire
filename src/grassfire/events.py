from operator import add

from tri.delaunay import apex, orig, dest, cw, ccw
from oseq import OrderedSequence

# from grassfire
from primitives import SkeletonNode, KineticVertex
from calc import perp, bisector
from collapse import compute_collapse_time

def compare_event_by_time(one, other):
    # compare by time
    if one.time < other.time: # lt
        return -1
    elif one.time > other.time: # gt
        return 1
    # in case times are equal, compare by id of triangle
    # to be able to find the correct triangle back
    else: # eq
        if id(one.triangle) < id(other.triangle):
            return -1
        if id(one.triangle) > id(other.triangle):
            return 1
        else:
            return 0



def init_event_list(skel):
    # FIXME: SHOULD WE
    # remove the 3 kinetic/ infinite triangles, and link their two neighbours
    # that are not None for these triangles properly together!
    # ???????????????????????????????? 
#     will_collapse = []
    q = OrderedSequence(cmp=compare_event_by_time)
    for tri in skel.triangles:
        print """
        """
        print id(tri)
        print "time"
        res = compute_collapse_time(tri)
        print "time >>>", res
        if res is not None:
            q.add(res)
#             will_collapse.append(res)
#     print ">>> will collapse", will_collapse
#     for item in will_collapse:
#         print id(item.triangle)

    print "all events::"
    for evt in q:
        print evt
    return q
#     will_collapse.sort(key=lambda x: -x.time)
#     print will_collapse
#     for evt in will_collapse:
#         print evt.time, evt.side, evt.tp, evt.triangle.type
#     return will_collapse


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
    a = v0.position_at(now)
    b = v1.position_at(now)
    c = v2.position_at(now)

    print "a", a
    print "b", b
    print "c", c

    v0.stops_at = now
    v1.stops_at = now
    v2.stops_at = now

    x = sum([a[0], b[0], c[0]]) / 3.
    y = sum([a[1], b[1], c[1]]) / 3.
    pos = (x, y)
    sk_node = SkeletonNode(pos)

    v0.stop_node = sk_node
    v1.stop_node = sk_node
    v2.stop_node = sk_node

    return sk_node

def compute_new_kvertex(v1, v2, now, sk_node):
    kv = KineticVertex()

    kv.starts_at = now
    kv.start_node = sk_node

    print "Node POSITION", sk_node.pos

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
    print "new bisector:"
    print " LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(sk_node.pos, 
                                                            map(add, velo, sk_node.pos))
    # compute position at t=0
    # rotate bisector 180 degrees
    negvelo = perp(perp(velo))
    pos_at_t0 = (sk_node.pos[0] + negvelo[0] * now,
                 sk_node.pos[1] + negvelo[1] * now)
    print "AT ZERO:", pos_at_t0
    kv.origin = pos_at_t0
    kv.velocity = velo
    return kv

def replace_kvertex(t, v, newv, now, direction, queue):
    while t is not None:
        side = t.vertices.index(v)
        t.vertices[side] = newv
        print "updated", id(t), "at", side
        print "new kinetic vertex:", id(newv)
        # FIXME: 
        # Needed: 
        # access to event list, to find the events for this triangles
        # and replace them
        print "removing", t.event
        queue.remove(t.event)
        print id(t)
        e = compute_collapse_time(t, now)
        if e is not None:
            print "added", e
            queue.add(e)
        else:
            raise NotImplementedError("not handled")
        print "END TODO"
        t = t.neighbours[direction(side)]

def update_circ(kv, v1, v2, now):
    # update circular list
    kv.left = v1, now
    kv.right = v2, now

    v1.right = kv, now
    v2.left = kv, now

def handle_edge_event(evt, skel, queue):
    print "=" * 20
    print "Processing edge event"
    print "=" * 20
    print evt
    t = evt.triangle
    print "TYPE", t.type
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

    else:
        sk_node = stop_kvertices2(v1, v2, now)
        kv = compute_new_kvertex(v1.left, v2.right, now, sk_node)
        # update circular list
        update_circ(kv, v1.left, v2.right, now)

    # add to skeleton structure
    skel.sk_nodes.append(sk_node)
    skel.vertices.append(kv)

    print kv.origin
    print kv.velocity
#     print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.origin, kv.position_at(now))
#     print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(kv.position_at(now),
#                                                             map(add, kv.position_at(now), kv.velocity))
    print "neighbours"
    print "-" * 20
    a = t.neighbours[(e+1) % 3]
    b = t.neighbours[(e+2) % 3]

    n = t.neighbours[e]
    print "a.", id(a)
    print "b.", id(b)
    print "n.", id(n)
    print "-" * 20
    if a is not None:
        a_idx = a.neighbours.index(t)
        print "changing neighbour a"
        a.neighbours[a_idx] = b
        replace_kvertex(a, v2, kv, now, ccw, queue)
    if b is not None:
        print "changing neighbour b"
        b_idx = b.neighbours.index(t)
        b.neighbours[b_idx] = a
        replace_kvertex(b, v1, kv, now, cw, queue)
    if n is not None:
        print "changing neighbour n"
        n_idx = n.neighbours.index(t)
        n.neighbours[n_idx] = None
        # schedule_immediately(n) --> find triangle in the event queue!
    print "updated neighbours"
    if a is not None:
        print "a.", a.neighbours[a_idx]
    if b is not None:
        print "b.", b.neighbours[b_idx]
    if n is not None:
        print "n.", n.neighbours[n_idx]

def handle_split_event(evt, skel, queue):
    print "=" * 20
    print "Processing split event"
    print "=" * 20
    print evt
    t = evt.triangle
    print "TYPE", t.type
    e = evt.side
    now = evt.time
    v = t.vertices[(e) % 3]
    v1 = t.vertices[(e+1) % 3]
    v2 = t.vertices[(e+2) % 3]
    sk_node = stop_kvertex(v, now)

    assert v1.right is v2
    assert v2.left is v1

    vb = compute_new_kvertex(v.left, v2, now, sk_node)
    va = compute_new_kvertex(v1, v.right,  now, sk_node)

    # splice circular list into 2 lists here
    update_circ(vb, v.left, v2, now)
    update_circ(va, v1, v.right, now)

    skel.sk_nodes.append(sk_node)
    skel.vertices.append(va)
    skel.vertices.append(vb)

    # update neighbours
    a = t.neighbours[(e+1)%3]
    a.neighbours[a.neighbours.index(t)] = None
    replace_kvertex(a, v, va, now, ccw)

    b = t.neighbours[(e+2)%3]
    b.neighbours[b.neighbours.index(t)] = None
    replace_kvertex(b, v, vb, now, ccw)


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
    for i, e in enumerate(queue):
        print i, e
#     evt = events[0]
    while queue:
        evt = queue.popleft()
        # decide what to do based on event type
        if evt.tp == "edge":
            handle_edge_event(evt, skel, queue)
        elif evt.tp == "flip":
            print "SKIP FLIP"
        elif evt.tp == "split":
            print "SKIP SPLIT"
            handle_split_event(evt, skel, queue)

#         raw_input("handled  event " + str(evt))