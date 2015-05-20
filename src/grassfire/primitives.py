from collections import namedtuple
from pprint import pprint

from tri import triangulate, ToPointsAndSegments
from tri.delaunay import TriangleIterator, output_triangles
from tri.delaunay import StarEdgeIterator, cw, ccw
from tri.delaunay import output_triangles, output_vertices, output_edges
from tri.delaunay import FiniteEdgeIterator
from tri.delaunay import orient2d
from tri.delaunay import apex, orig, dest

from angles import bisector
from angles import normalize, perp
from operator import add, sub, mul, truediv
from collections import deque

from warnings import warn
from math import atan2, pi
from math import sqrt, copysign

# 
import numpy

def output_kvertices(V, fh):
    """Output list of vertices as WKT to text file (for QGIS)"""
    fh.write("id;wkt;left cw;right ccw\n")
    for v in V:
        fh.write("{0};POINT({1});{2};{3}\n".format(id(v), v, id(v.left_ccw), id(v.right_cw)))


class Event(object):
    def __init__(self, when, tri, side = None, tp = None):
        self.time = when
        self.triangle = tri
        self.side = side
        self.tp = tp

    def __str__(self):
        return """
<<Event at {0}, 
           {1}, 
           {2},
           {3}>>
""".format(self.time, self.triangle, self.side, self.tp)

class Skeleton(object):
    """Represents a Straight Skeleton 
    """
    def __init__(self):
        # positions --> skeleton positions
        self.sk_nodes = []
        # kinetic primitives --> (traced) wavefront
        self.vertices = []
        self.triangles = []

Vector = namedtuple("Vector", "x y")

class SkeletonNode(object):
    def __init__(self, pos, info=None):
        self.pos = pos
        self.info = info # the info of the vertex in the triangulation


class KineticVertex(object):
    __slots__ = ("origin", "velocity", 
                 "left_ccw", "right_cw", 
                 "starts_at", "stops_at",
                 "start_node", "stop_node",
                 )
    def __init__(self):
        self.origin = None 
        self.velocity = None

        # next / prev pos
        # while looking in direction of bisector, see which 
        # kinetic vertex you see on the left, and which on the right
        self.left_ccw = None
        self.right_cw = None

        # floats
        self.starts_at = None
        self.stops_at = None

        # Skeleton nodes
        self.start_node = None
        self.stop_node = None

    def __str__(self):
        # FIXXME: make other method (dependent on time as argument)
        time = 4.5
        # 4.281470022378475
        return "{0[0]} {0[1]}".format(self.position_at(time))

    def distance2(self, other):
        """Cartesian distance *squared* to other point """
        # Used for distances in random triangle close to point
        return pow(self.origin[0] -other.origin[0], 2) + pow(self.origin[1] - other.origin[1], 2)

    def distance2_at(self, other, time):
        """Cartesian distance *squared* to other point """
        (sx,sy) = self.position_at(time)
        (ox,oy) = other.position_at(time)
        # Used for distances in random triangle close to point
        return pow(sx - ox, 2) + pow(sy - oy, 2)

    def position_at(self, time):
        return (self.origin[0] + time * self.velocity[0], 
                self.origin[1] + time * self.velocity[1])


class InfiniteVertex(object): # Stationary Vertex
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{0} {1}".format(self.x, self.y)


class KineticTriangle(object):
    def __init__(self):
        self.vertices = [None, None, None]
        self.neighbours = [None, None, None]

    def __str__(self):
        vertices = []
        for idx in range(3):
            v = self.vertices[idx]
            if v is not None:
                vertices.append(str(v))
#             else:
#                 orig_idx, dest_idx = (idx - 1) % 3, (idx + 1) % 3
#                 orig, dest = self.vertices[orig_idx], self.vertices[dest_idx]
#                 halfway = (orig.x + dest.x) * .5, (orig.y + dest.y) * .5
#                 d = orig.distance(dest)
#                 dx = dest.x - orig.x
#                 dx /= d
#                 dy = dest.y - orig.y
#                 dy /= d
#                 O = halfway[0] + dy, halfway[1] - dx 
#                 vertices.append("{0[0]} {0[1]}".format(O))
        if vertices:
            vertices.append(vertices[0])
        return "POLYGON(({0}))".format(", ".join(vertices))

    @property
    def type(self):
        """Returns how many 'constrained' / PSLG edges this triangle has
        """
        return self.neighbours.count(None)

    @property
    def finite(self):
        return all([isinstance(vertex, KineticVertex) for vertex in self.vertices])

def find_overlapping_triangle(E):
    """find overlapping triangle 180 degrees other way round
    of triangle edge of the first triangle

    it assumes that the edges are around a central vertex
    and that the first triangle has a constrained and other edges do not.

    returns index in the list of the triangle that overlaps  
    """
    first = E[0]
    t = first.triangle 
    mid = first.side
    begin = ccw(mid)
    P, Q = t.vertices[begin], t.vertices[mid]
    overlap = None
    idx = None
    for i, e in enumerate(E):
        t = e.triangle
        R = t.vertices[cw(e.side)]
        # if last leg of triangle makes left_ccw turn/straight, 
        # instead of right_cw turn previously
        # we have found the overlapping triangle
        if orient2d(P, Q, R) >= 0: # and overlap is None:
            overlap = e
            idx = i
            break
    assert overlap is not None
    return idx

def is_quad(L):
    assert len(L) == 5
    # check 3 orientations
    s = [orient2d(a, b, c) for a,b,c in zip(L[:-2], L[1:-1], L[2:])]
    # check whether they are all the same
    items = map(lambda x: x>=0, s)
    result = all(items[0] == item for item in items)
    return result

#     vec = tuple(map(sub, t.vertices[e], t.vertices[s]))
#     vec = perp(perp(vec))
#     opp_angle = atan2(vec[1], vec[0])
#     while opp_angle < 0:
#         opp_angle += 2 * pi
# 
#     print opp_angle
#     overlap = None
#     for e in E:
#         t = e.triangle 
#         start = e.side
#         end = ccw(start)
#         vec = tuple(map(sub, t.vertices[end], t.vertices[start]))
#         angle = atan2(vec[1], vec[0])
#         while angle <= 0:
#             angle += 2 * pi
#         print vec, angle
#         if angle >= opp_angle:
#             overlap = e
#             break
#     assert overlap is not None
#     print "overlap", e.triangle

def init_skeleton(dt):
    """Initialize a data structure that can be used for making the straight
    skeleton.
    """
    skel = Skeleton()

    # make skeleton nodes 
    # -> every triangulation vertex becomes a skeleton node
    nodes = {}
    for v in dt.vertices:
        if v.is_finite:
            nodes[v] = SkeletonNode(pos=(v.x, v.y), info=v.info)

    # make kinetic triangles, so that for every delaunay triangle we have
    # a kinetic counter part

    ktriangles = []         # all kinetic triangles
    triangle2ktriangle = {} # mapping from delaunay triangle to kinetic triangle 
#     vertex2kvertex = {}
    # for every delaunay triangle, make a kinetic triangle
    it = TriangleIterator(dt)
    next(it)# skip the external triangle (which is the first the iterator gives)
    # triangle -> kvertices triangle (position in ktriangles)
    for t in it:
        # skip the external triangle
        #if t is dt.external: 
        #    continue
        k = KineticTriangle()
        triangle2ktriangle[t] = k
        ktriangles.append(k)

    link_around = []
    # set up properly the neighbours of all kinetic triangles
    # blank out the neighbour, if a side is constrained
    #remove = []
    it = TriangleIterator(dt)
    next(it)# skip the external triangle (which is the first the iterator gives)
    for t in it:
        k = triangle2ktriangle[t]
        for j, n in enumerate(t.neighbours):
            # set neighbour pointer to None if constrained side
            if t.constrained[j]:
                continue
            # skip linking to the external triangle
            if n is dt.external or n is None:
                continue
            k.neighbours[j] = triangle2ktriangle[n]
        # if we found a triangle that has a None Neighbour -> triangle to remove
        #if any([n is None for n in k.neighbours]):
        #    remove.append(t)

    # make kinetic vertices
    # and link them to the kinetic triangles
    # also make sure that every kinetic vertex is related to a skeleton node
    kvertices = []
#     ktri_no_apex = []
    one_ktri_between = {}
#     with open("/tmp/bisectors.wkt", "w") as bisector_fh:
#         print >> bisector_fh, "wkt"
    for v in dt.vertices:
        assert v.is_finite, "infinite vertex found"
#             print ""
        it = StarEdgeIterator(v)
        around = [e for e in it]
#             with open("/tmp/vertexit.wkt", "w") as fh:
#                 output_triangles([e.triangle for e in around], fh)

        constraints = []
        for i, e in enumerate(around):
            if e.triangle.constrained[cw(e.side)]:
                constraints.append(i)
#             print "# of constraints:", len(constraints)

        # FIXME:
        # Check here how many constrained edges we have outgoing of
        # this vertex.
        #
        # In case 0: degenerate case, should not happen
        # In case 1: we should make two kvertices vertices
        #
        # We do not handle this properly at this moment.
        #
        # In case 2 or more the following is fine.
        if len(constraints) == 0:
            raise ValueError("Singular point found")
        else:
            # rotate the list of around triangles, 
            # so that we start with a triangle that has a constraint
            # side
            if constraints[0] != 0:
                shift = -constraints[0] # how much to rotate
                d = deque(around)
                d.rotate(shift)
                around = list(d)
                # also update which triangles have a constraint edge 
                constraints = [idx + shift for idx in constraints]

            # make two bisectors at a terminal vertex
            if len(constraints) == 1:
#                     print "central vertex", v

                assert constraints[0] == 0
                edge = around[0]
                start, end = v, edge.triangle.vertices[ccw(edge.side)]
                vec = normalize((end.x - start.x , end.y - start.y))

                # from segment over terminal vertex to this kinetic vertex, 
                # turns right_cw
                # (first bisector when going ccw at end)
                p2 = tuple(map(add, start, perp(vec)))
                p1 = v
                p0 = tuple(map(add, start, perp(perp(vec))))
                bi = bisector(p0, p1, p2)
#                 print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p1, map(add, p1, bi)) 
#                     print nodes[v]

                kvA = KineticVertex()
                kvA.origin = (p1.x, p1.y)
                kvA.velocity = bi
                kvA.start_node = nodes[v]
                kvertices.append(kvA)

                # from segment to this vertex, turns left_ccw
                # second bisector when going ccw at end
                p2 = tuple(map(add, start, perp(perp(vec))))
                p1 = v
                p0 = tuple(map(add, start, perp(perp(perp(vec)))))
                bi = bisector(p0, p1, p2)
#                 print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p1, map(add, p1, bi)) 
                # FIXME insert additional triangle at this side
#                     print nodes[v]

                kvB = KineticVertex()
                kvB.origin = (p1.x, p1.y)
                kvB.velocity = bi
                kvB.start_node = nodes[v]
                kvertices.append(kvB)

                groups = [around]

                split_idx = find_overlapping_triangle(around)

#                     print split_idx
#                     print len(around)
                # determine which triangles get an incidence with the
                # first and which with the second kvertices vertex

                # first go with kvA
                # second go with kvB
                first, second = around[:split_idx], around[split_idx+1:]
#                     print "first ", first
#                     print "second", second
                mid = around[split_idx]
#                     print "mid   ", mid

                # go with kvA
                for e in first:
                    ktriangle = triangle2ktriangle[e.triangle]
#                         print ktriangle
                    ktriangle.vertices[e.side] = kvA
                # go with kvB
                for e in second:
                    ktriangle = triangle2ktriangle[e.triangle]
#                         print ktriangle
                    ktriangle.vertices[e.side] = kvB

                # for the mid triangle it depends where it should go
                # based on adding an additional kvertices triangle into 
                # the triangulation here...

                # FIXME: the placement of points A and B should be
                # dependent on the distance between A and L or A and F
                # to not get False negatives out of the is_quad 
                # classification
                triangle = mid.triangle
#                     print "PIVOT POINT INDEX", mid.side
                first_leg = ccw(mid.side)
                last_leg = cw(mid.side)
                L = triangle.vertices[last_leg]
                F = triangle.vertices[first_leg]

                A = map(add, kvA.origin, kvA.velocity)
                B = map(add, kvB.origin, kvB.velocity)
                O = triangle.vertices[mid.side]
#                     print "first", first_leg,"|" , F, "(cw)", "last", last_leg, "|" ,L, "(ccw) around", O

                first_quad = [O, A, F, B, O]
                last_quad = [O, A, L, B, O]
                first_ok = is_quad(first_quad)
                last_ok = is_quad(last_quad)

                # if first is True and second False
                # assign ktriangles triangle to kvA/kvB and the corner to kvB

                # if both not ok, probably at convex hull overlapping with infinite triangle
                # only, so take guess and use the first leg
                if first_ok or (not first_ok and not last_ok):
                    ktriangle = triangle2ktriangle[mid.triangle]
                    ktriangle.vertices[mid.side] = kvB

                    knew = KineticTriangle()
                    knew.vertices[0] = kvB
                    knew.vertices[1] = kvA
                    knew.vertices[2] = None

                    X, Y = mid.triangle, mid.triangle.neighbours[ccw(first_leg)]
                    sideX = X.neighbours.index(Y)
                    sideY = Y.neighbours.index(X)

                    key = tuple(sorted([X, Y]))
                    if key not in one_ktri_between:
                        one_ktri_between[key] = [] 
                    one_ktri_between[key].append( (knew, triangle2ktriangle[Y], sideY, triangle2ktriangle[X], sideX) )

                # if first is false and second True
                # assign ktriangles triangle to kvA/kvB and the corner to kvA
                elif last_ok:
                    ktriangle = triangle2ktriangle[mid.triangle]
                    ktriangle.vertices[mid.side] = kvA

                    knew = KineticTriangle()
                    knew.vertices[0] = kvB
                    knew.vertices[1] = kvA
                    knew.vertices[2] = None
#                         ktri_no_apex.append(knew)

                    X, Y = mid.triangle, mid.triangle.neighbours[cw(last_leg)]
                    sideX = X.neighbours.index(Y)
                    sideY = Y.neighbours.index(X)

                    key = tuple(sorted([X, Y]))
                    if key not in one_ktri_between:
                        one_ktri_between[key] = [] 
                    one_ktri_between[key].append((knew, triangle2ktriangle[X], sideX, triangle2ktriangle[Y], sideY))

                # add 2 entries to link_around list
                # one for kvA and one for kvB
                # link kvA and kvB to point to each other directly
                kvA.left_ccw = kvB
                link_around.append( (None, kvA, (first[0].triangle, ccw(first[0].side))))
                kvB.right_cw = kvA
                link_around.append( ((second[-1].triangle, cw(second[-1].side)), kvB, None))

            # make bisectors
            else:
                assert len(constraints) >= 2
                # group the triangles around the vertex
                constraints.append(len(around))
                groups = []
                for lo, hi in zip(constraints[:-1], constraints[1:]):
                    groups.append(around[lo:hi])

                # per group make a bisector and KineticVertex
                for group in groups:
                    begin, end = group[0], group[-1]
                    p2 = begin.triangle.vertices[ccw(begin.side)] # the cw vertex
                    p1 = v
                    p0 = end.triangle.vertices[cw(end.side)]      # the ccw vertex
                    bi = bisector(p0, p1, p2)
#                     print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p1, map(add, p1, bi))
                    kv = KineticVertex()
                    kv.origin = (p1.x, p1.y)
                    kv.velocity = bi
                    kv.start_node = nodes[v]
                    for edge in group:
                        ktriangle = triangle2ktriangle[edge.triangle]
                        ktriangle.vertices[edge.side] = kv
                    kvertices.append(kv)
                    # link vertices to each other in circular list
                    link_around.append( ((end.triangle, cw(end.side)), kv, (begin.triangle, ccw(begin.side))))

    for left, curv, right in link_around: # left_ccw is cw, right_cw is ccw
        if left is not None:
            cwv = triangle2ktriangle[left[0]].vertices[left[1]]
            curv.left_ccw = cwv

        if right is not None:
            ccwv = triangle2ktriangle[right[0]].vertices[right[1]]
            curv.right_cw = ccwv

    # copy infinite vertices into the kinetic triangles
    # make dico of infinite vertices (lookup by coordinate value)
    infinites = {}
    for t in triangle2ktriangle:
        for i, v in enumerate(t.vertices):
            if not v.is_finite:
                infinites[(v[0], v[1])] = InfiniteVertex(v[0], v[1])
    assert len(infinites) == 3
    # link infinite triangles to the infinite vertex
    for (t, kt) in triangle2ktriangle.iteritems():
        for i, v in enumerate(t.vertices):
            if not v.is_finite:
                kt.vertices[i] = infinites[(v[0], v[1])]

    # deal with added kinetic triangles at terminal vertices 
    for val in one_ktri_between.itervalues():
        if len(val) == 1:
            knew, x, side_x, y, side_y, = val[0]
            knew.neighbours[0] = x
            knew.neighbours[1] = y
            knew.neighbours[2] = None
            x.neighbours[side_x] = knew
            y.neighbours[side_y] = knew
            knew.vertices[2] = x.vertices[ccw(side_x)]
            ktriangles.append(knew)
        elif len(val) == 2:
            for i, v in enumerate(val):
                # the other triangle between these 2 terminal vertices 
                # is the first value of the other tuple 
                kother = val[(i+1) % 2][0]
                knew, x, side_x, y, side_y, = v
                # link to each other and to neighbour x
                knew.neighbours[0] = x
                knew.neighbours[1] = kother 
                knew.neighbours[2] = None
                x.neighbours[side_x] = knew
                y.neighbours[side_y] = kother
                # link to vertex
                knew.vertices[2] = x.vertices[ccw(side_x)]
                ktriangles.append(knew)
        else:
            raise ValueError("Unexpected # kinetic triangles at terminal vertex")

    assert check_ktriangles(ktriangles)
    # INITIALIZATION FINISHES HERE


    # write bisectors to file
    with open("/tmp/bisectors.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt\n")
        for kvertex in kvertices:
            p1 = kvertex.origin
            bi = kvertex.velocity
            bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(p1, map(add, p1, bi)))

    # FIXME: SHOULD WE
    # remove the 3 kinetic/ infinite triangles, and link their two neighbours
    # that are not None for these triangles properly together!
    # ???????????????????????????????? 

    will_collapse = []
    for tri in ktriangles:
        print """
        """
        print id(tri)
        print "time"
        res = compute_collapse_time(tri)
        print "time >>>", res
        if res is not None:
            will_collapse.append(res)
    print ">>> will collapse", will_collapse
    for item in will_collapse:
        print id(item.triangle)

    will_collapse.sort(key=lambda x: x.time)
    print will_collapse
    for evt in will_collapse:
        print evt.time, evt.side, evt.tp, evt.triangle.type

    evt = will_collapse[0]
    # decide what to do based on event type
    if evt.tp == "edge":
        handle_edge_event(evt)
    elif evt.tp == "flip":
        pass
    elif evt.tp == "split":
        pass
#         try:
#             collapse_time_quadratic(tri)
#             
#         except AttributeError:
#             pass
#     for tri in ktriangles:
#         print tri
#         collapse_time_dot(tri)
    skel.triangles = ktriangles


    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles(ktriangles, fh)


    with open("/tmp/kvertices.wkt", "w") as fh:
        output_kvertices(kvertices, fh)

    return skel

def check_ktriangles(L):
    """Check whether kinetic triangles are all linked up properly
    """
    valid = True
    # check if neighbours are properly linked
    for ktri in L:
        for i in range(3):
            ngb = ktri.neighbours[i]
            if ngb is not None:
                if ktri not in ngb.neighbours:
                    valid = False
    # check if the sides of a triangle share the correct vertex at begin / end
    for ktri in L:
        for i in range(3):
            ngb = ktri.neighbours[i]
            if ngb is not None:
                j = ngb.neighbours.index(ktri)
                if not ngb.vertices[cw(j)] is ktri.vertices[ccw(i)]:
                    valid = False
                if not ngb.vertices[ccw(j)] is ktri.vertices[cw(i)]:
                    valid = False
    return valid

# ------------------------------------------------------------------------------
# Event handling

def stop_kvertices2(v1, v2, now):
    v1.stops_at = now
    v2.stops_at = now
    a = v1.position_at(now)
    b = v2.position_at(now)
    pos = tuple(map(lambda x: x*.5, map(add, a, b)))
    sk_node = SkeletonNode(pos)
    return sk_node

def stop_kvertices3(v0, v1, v2, now):
    a = v0.position_at(now)
    b = v1.position_at(now)
    c = v2.position_at(now)

    v0.stops_at = now
    v1.stops_at = now
    v2.stops_at = now

    x = sum([a[0], b[0], c[0]]) / 3.
    y = sum([a[1], b[1], c[1]]) / 3.
    pos = (x, y)
    sk_node = SkeletonNode(pos)
    return sk_node

def compute_new_kvertex(v1, v2, now, sk_node):
    kv = KineticVertex()

    kv.starts_at = now
    kv.start_node = sk_node

    print sk_node.pos

    kv.left_ccw = v1 # did not check whether correct
    kv.right_cw = v2 # did not check whether correct

    #velo = #map(lambda x: x*.5, ...) 
    velo = tuple(map(add, v1.velocity, v2.velocity)) # multiply with 0.5???
    # compute position at t=0
    negvelo = map(lambda x: -x, velo)
    pos_at_t0 = (sk_node.pos[0] + negvelo[0] * now,
                 sk_node.pos[1] + negvelo[1] * now)
    kv.origin = pos_at_t0
    kv.velocity = velo
    return kv

def replace_kvertex(t, v, newv, dir):
    while t is not None:
        side = t.vertices.index(v)
        t.vertices[side] = newv
        print "updated", id(t), "at", side
        print "new kinetic vertex:", id(newv)
        print "updated event", compute_collapse_time(t)
        t = t.neighbours[dir(side)]

def handle_edge_event(evt):
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
    #sk_node = stop_kvertices3(v0, v1, v2, now)
    sk_node = stop_kvertices2(v1, v2, now)
    kv = compute_new_kvertex(v1.left_ccw, v2.right_cw, now, sk_node)
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
    print "a.", a
    print "b.", b
    print "n.", n
    print "-" * 20
    if a is not None:
        print "changing neighbour a"
        a.neighbours[a.neighbours.index(t)] = b
        replace_kvertex(a, v2, kv, ccw)

    if b is not None:
        print "changing neighbour b"
        b.neighbours[b.neighbours.index(t)] = a
        replace_kvertex(b, v1, kv, cw)

    if n is not None:
        print "changing neighbour n"
        n.neighbours[n.neighbours.index(t)] = None
        # schedule_immediately(n)
        pass

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

# ------------------------------------------------------------------------------
# solve

def ignore_and_sort(L):
    """
    L = list of 2-tuples, e.g (time, side) or (length, side)
    
    first filters L where the first element should be positive value
    (note: this also filters None values)

    then sorts L based on first element of tuple
    """
    
    # FIXME: not sure if filtering 0 values always out is what we want
    # e.g. while doing length comparision, we probably want to keep a length
    # of 0????
    L = filter(lambda x: x[0]>0, L)
    L.sort(key=lambda x: x[0])
    return L

def compute_collapse_time(t):
    # compute when this triangle collapses
    collapses_at = None 
    collapses_side = None
    collapses_type = None
    if t.finite:
        # finite triangles
        tp = t.type
        print "TYPE", tp
        if tp == 0:
            a, b, c = t.vertices
            coeff = area_collapse_time_coeff(a, b, c)
            times = list(solve_quadratic(coeff[0], coeff[1], coeff[2]))
            times = filter(lambda x: x>0, times)
            time_det = min(times)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            print "   roots found by numpy", numpy.roots(coeff)
            print times
            times = []
            for side in range(3):
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                times.append((collapse_time_edge(v1, v2), side))
            times = filter(lambda x: x[0]>0, times)
            times.sort(key=lambda x: x[0])
            print "te [edge collapse time]", times
            if times:
                time_edge = times[0][0]
                if time_det < time_edge:
                    print "flip event of zero triangle"
                    collapses_at = time_det
                    # -> side_at = longest of these edges should flip
                    for side in range(3):
                        i, j = cw(side), ccw(side)
                        v1, v2 = t.vertices[i], t.vertices[j]
                        print "dist", side, v1.distance2(v2)
                else:
                    collapses_at = time_edge
                    side_at = times[0][1]
                    print "vertices crashing into each other, handle as edge event @side", side_at
        elif tp == 1: # FINISHED
            # 2 cases can happen:
            # a. the wavefront edge can collapse -> edge event
            # b. the vertex v opposite this edge can crash into
            #    this edge, or sweep over its supporting line -> split or flip event 

            side = t.neighbours.index(None)
            org, dst, apx = t.vertices[orig(side)], t.vertices[dest(side)], t.vertices[apex(side)]

            # 
            coeff = area_collapse_time_coeff(org, dst, apx)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            print "   roots found by numpy", numpy.roots(coeff)

            # 
            #print id(org), id(dst), id(apx)
            Mv = tuple(map(sub, apx.origin, org.origin))
            #print Mv
            #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + Mv[0], org.origin[1] + Mv[1])
            m =  map(sub, dst.origin, org.origin)
            #print m
            m = norm(m) # normalize m
            #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + m[0], org.origin[1] + m[1])
            #print m
            n = perp(m) # take perpendicular vector
            #print n
            #print "LINESTRING({0} {1}, {2} {3})".format(org.origin[0], org.origin[1], org.origin[0] + n[0], org.origin[1] + n[1])
            distance_v_e = dot(Mv, n)
            #print "dist", distance_v_e
            s = apx.velocity
            #print dot(s, n)
            t_v = distance_v_e / (1 - dot(s, n))
            #print crash_time
            print "tv [vertex crash time]:", t_v 

            t_e = collapse_time_edge(org, dst)
            print "te [edge collapse time]", t_e
            # given that we ignore negative times!!!
            if t_e <= t_v:
                collapses_at = t_e
                collapses_side = t.neighbours.index(None)
                collapses_type = "edge"
            else:
                print "tv strictly earlier than te -> split or flip"
                # compute side lengths of triangle at time tv
                print "should compute side lengths at time tv"
                lengths = []
                for side in range(3):
                    i, j = cw(side), ccw(side)
                    v1, v2 = t.vertices[i], t.vertices[j]
                    dist = v1.distance2_at(v2, t_v)
                    print "dist", side, dist
                    lengths.append((dist, side))
                lengths = ignore_and_sort(lengths)
                dist, side = lengths[0]
                print dist, side
                # if longest edge at time t_v is wavefronte edge -> split event
                if side == t.neighbours.index(None):
                    collapses_type = "split"
                # otherwise -> flip event
                else:
                    collapses_type = "flip"
                collapses_at = t_v
                collapses_side = side # FIXME: is that correct?
        elif tp == 2: # FINISHED
            # compute with edge collapse time
            # use earliest of the two edge collapse times
            # ignore times in the past
            a, b, c = t.vertices
            coeff = area_collapse_time_coeff(a, b, c)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            print "   roots found by numpy", numpy.roots(coeff)
            sides = []
            for i in range(3):
                if t.neighbours[i] is None:
                    sides.append(i)
            assert len(sides) == 2
            print sides
            times = []
            for side in sides:
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                times.append((collapse_time_edge(v1, v2), side))
            # remove times in the past, same as None values
            times = ignore_and_sort(times)
            if times:
                time, side = times[0]
                collapses_at = time
                collapses_side = side
                collapses_type = "edge"
                print "SIDE", side
#             times = filter(lambda x: x>0, times)
#             print times
#             print set(times)
#             if times:
#                 time = min(times)
#                 if time >= 0:
#                     collapses_at = time
        elif tp == 3:
            # compute with edge collapse time of all three edges
            a, b, c = t.vertices
            coeff = area_collapse_time_coeff(a, b, c)
            print "td [area zero time]", solve_quadratic(coeff[0], coeff[1], coeff[2])
            times = []
            for side in range(3):
                i, j = cw(side), ccw(side)
                v1, v2 = t.vertices[i], t.vertices[j]
                times.append((collapse_time_edge(v1, v2), side))
            # remove times in the past, same as None values
            times = ignore_and_sort(times)
            times = filter(lambda x: x>0, times)
            if times:
                collapses_at = times[0][0]
                collapses_side = times[0][1]
                collapses_type = "edge"
    else:
        # infinite triangles
        print "infinite triangle found"

    if collapses_at is not None:
        return Event(when=collapses_at, 
                     tri=t, 
                     side=collapses_side, 
                     tp=collapses_type)
    else:
        return None

def quadratic(x, a, b, c):
    """Returns y = a * x^2 + b * x + c for given x and a, b, c
    """
    a, b, c, x = float(a), float(b), float(c), float(x)
    return a * x**2 + b * x + c

def dot(v1, v2):
    return sum(p*q for p,q in zip(v1, v2))

def norm(v):
    L = sqrt(sum( [x**2 for x in v] ) )
    return tuple([x/L for x in v])

def collapse_time_edge(v1, v2):
    """Given 2 kinetic vertices compute the time when they will collide
    """
    s1 = v1.velocity
    s2 = v2.velocity
    o2 = v2.origin
    o1 = v1.origin
    denominator = dot(map(sub, s1, s2), map(sub, s1, s2))
    if denominator != 0.:
        nominator = dot(map(sub, s1, s2), map(sub, o2, o1))
        collapse_time = nominator / denominator
        return collapse_time
        # when positive, this is a correct collapse time
        # when negative, the vertices are now moving apart from each other
        # when denominator is 0, they move in parallel
    else:
        print "denominator 0"
        print "these two vertices move in parallel:",
        print v1, "|", v2
        return None

def collapse_time_dot(tri):
    """calculate whether an edge length becomes zero
    """
    for i in range(3):
        j = (i + 1) % 3
        v1, v2 = tri.vertices[i], tri.vertices[j]
        collapse_time_edge(v1, v2)

def collapse_time_quadratic(ktri):
    """Calculate collapse time of kinetic triangle by determinant method
    (when does area become 0.0 size)
    """
    # described in section 4.3.1
    v1, v2, v3 = ktri.vertices[0], ktri.vertices[1], ktri.vertices[2]

    # speeds
    s1 = v1.velocity
    s2 = v2.velocity
    s3 = v3.velocity
    s1x, s1y = s1[0], s1[1]
    s2x, s2y = s2[0], s2[1]
    s3x, s3y = s3[0], s3[1]

    # origins
    o1 = v1.origin
    o2 = v2.origin
    o3 = v3.origin
    o1x, o1y = o1[0], o1[1]
    o2x, o2y = o2[0], o2[1]
    o3x, o3y = o3[0], o3[1]

    # terms
    a = \
       -s1y*s2x + s1x*s2y + s1y*s3x - \
        s2y*s3x - s1x*s3y + s2x*s3y
    b = \
        o2y*s1x - o3y*s1x - o2x*s1y + \
        o3x*s1y - o1y*s2x + o3y*s2x + \
        o1x*s2y - o3x*s2y + o1y*s3x - \
        o2y*s3x - o1x*s3y + o2x*s3y
    c = \
       -o1y*o2x + o1x*o2y + o1y*o3x - \
        o2y*o3x - o1x*o3y + o2x*o3y
    print "quadratic solved", solve_quadratic(a, b, c)


def sign(x):
    """Sign function
    """
    if x == 0:
        return 0
    else:
        return copysign(1, x)


def discriminant(a, b, c):
    """Calculate discriminant
    """
    D = b**2 - 4.0*a*c
    # print >> sys.stderr, "D =", D
    return D


def solve_quadratic(a, b, c):
    """Solve quadratic equation, defined by a, b and c
    
    Solves  where y = 0.0 for y = a * x^2 + b * x + c, if a, b and c are given
    
    Returns tuple with two elements
    The result is a:
    (None, None) if imaginary solution
    (None, float) or (float, None) if only one root
    (float, float) if two roots (roots wil    print >> sys.stderr, "a =", a, ", b =", b, ", c =", cl be sorted from small to big)
    """
    x1, x2 = None, None

    a, b, c = float(a), float(b), float(c)
    D = discriminant(a, b, c)
#    print >> sys.stderr, "a =", a, ", b =", b, ", c =", c, "D =", D
    #if near(D, 0):
    #    print >> sys.stderr, "making D 0"
    #    D = 0

    # if discriminant == 0 -> only 1 solution, instead of two

    if D < 0:
        return (x1, x2)
    else:
        q = -0.5 * (b + sign(b) * D**0.5)
        # print >> sys.stderr, "q =", q
        # prevent division by zero if a == 0 or q == 0
        if a != 0: x1 = q / a
        if q != 0: x2 = c / q
        return list(sorted((x1, x2)))


def area_collapse_time_coeff(kva, kvb, kvc):
    """Returns coefficients of quadratic in t
    """
    pa = kva.origin
    shifta = kva.velocity
    pb = kvb.origin
    shiftb = kvb.velocity
    pc = kvc.origin
    shiftc = kvc.velocity
    xaorig, yaorig = pa[0], pa[1]
    xborig, yborig = pb[0], pb[1]
    xcorig, ycorig = pc[0], pc[1]
    dxa, dya = shifta[0], shifta[1]
    dxb, dyb = shiftb[0], shiftb[1]
    dxc, dyc = shiftc[0], shiftc[1]
#    area = .5 *(xaorig + dxa *t) *(yborig + dyb *t) - 0.5 *(xborig + dxb *t) *(yaorig + dya *t)  + 0.5 *(xborig + dxb *t) *(ycorig + dyc *t)  - 0.5 *(xcorig + dxc *t) *(yborig + dyb *t) + 0.5 *(xcorig + dxc *t)* (yaorig + dya *t) - 0.5 *(xaorig + dxa *t)* (ycorig + dyc *t)
#        C                           B               B                               A
#  0.5 * xaorig * yborig + 0.5 * xaorig * dyb * t + 0.5 * dxa * t * yborig + 0.5 * dxa * pow(t,2) * dyb \
#- 0.5 * xborig * yaorig - 0.5 * xborig * dya * t - 0.5 * dxb * t * yaorig - 0.5 * dxb * pow(t,2) * dya \
#+ 0.5 * xborig * ycorig + 0.5 * xborig * dyc * t + 0.5 * dxb * t * ycorig + 0.5 * dxb * pow(t,2) * dyc \
#- 0.5 * xcorig * yborig - 0.5 * xcorig * dyb * t - 0.5 * dxc * t * yborig - 0.5 * dxc * pow(t,2) * dyb \
#+ 0.5 * xcorig * yaorig + 0.5 * xcorig * dya * t + 0.5 * dxc * t * yaorig + 0.5 * dxc * pow(t,2) * dya \
#- 0.5 * xaorig * ycorig - 0.5 * xaorig * dyc * t - 0.5 * dxa * t * ycorig - 0.5 * dxa * pow(t,2) * dyc

    A = dxa * dyb - \
        dxb * dya + \
        dxb * dyc - \
        dxc * dyb + \
        dxc * dya - \
        dxa * dyc

    B = xaorig * dyb - \
        xborig * dya + \
        xborig * dyc - \
        xcorig * dyb + \
        xcorig * dya - \
        xaorig * dyc + \
        dxa * yborig - \
        dxb * yaorig + \
        dxb * ycorig - \
        dxc * yborig + \
        dxc * yaorig - \
        dxa * ycorig

    C = xaorig * yborig - \
        xborig * yaorig + \
        xborig * ycorig - \
        xcorig * yborig + \
        xcorig * yaorig - \
        xaorig * ycorig
#    print "coefficients", A, B, C
    return tuple(map(lambda x: x*0.5, [A, B, C]))


# ------------------------------------------------------------------------------
# output
def output_dt(dt):
    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    with open("/tmp/segments.wkt", "w") as fh:
        output_edges([e for e in FiniteEdgeIterator(dt, True)], fh)


# ------------------------------------------------------------------------------
# test cases
def test_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (10, 0), (11, -1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    dt = triangulate(conv.points, None, conv.segments)
    output_dt(dt)
    init_skeleton(dt)

def test_simple_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (22,0), (14,10), (2,8), (0, 6.5), (0,0)]])
    dt = triangulate(conv.points, None, conv.segments)
    output_dt(dt)
    init_skeleton(dt)

def test_single_line():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_segment((0, 0), (10,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_three_lines():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_point((-2, 8))
    conv.add_point((-2, -8))
    conv.add_segment((0, 0), (10,0))
    conv.add_segment((0, 0), (-2,8))
    conv.add_segment((0, 0), (-2,-8))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_arrow_four_lines():
    conv = ToPointsAndSegments()

    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_point((12,0.5))
    conv.add_point((8,5))
    conv.add_point((8,-5))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((8,5), (12,0.5))
    conv.add_segment((12,0.5), (8,-5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_single_point():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    dt = triangulate(conv.points, None, conv.segments)
    init_skeleton(dt)


def test_triangle():
    conv = ToPointsAndSegments()
    conv.add_point((10,0))
    conv.add_point((-2,8))
    conv.add_point((-2,-8))
    conv.add_segment((10,0), (-2,8))
    conv.add_segment((-2,8), (-2,-8))
    conv.add_segment((-2,-8), (10,0))
    dt = triangulate(conv.points, None, conv.segments)
    output_dt(dt)
    init_skeleton(dt)

def test_quad():
    conv = ToPointsAndSegments()
    conv.add_point((8,2))
    conv.add_point((-2,8))
    conv.add_point((-2,-8))
    conv.add_point((14,10))
    conv.add_segment((8,2), (14,10))
    conv.add_segment((14,10), (-2,8))
    conv.add_segment((-2,8), (-2,-8))
    conv.add_segment((-2,-8), (8,2))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_two_lines_par():
    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,1))
    conv.add_point((22,1))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,1), (22,1))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_polyline():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,-1))
    conv.add_point((22,1))
    conv.add_point((30,-5))

    conv.add_segment((0,0), (10,-1))
    conv.add_segment((10,-1), (22,1))
    conv.add_segment((22,1), (30,-5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_1_segment():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
#     conv.add_point((22,0))
#     conv.add_point((30,0))

    conv.add_segment((0,0), (10,0))
#     conv.add_segment((22,0), (30,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_2_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((22,0))
    conv.add_point((30,0))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((22,0), (30,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_2_perp_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,2))
    conv.add_point((12,10))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,2), (12,10))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_45_deg_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,2))
    conv.add_point((14,4))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,2), (14,4))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_30_deg_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,5))
    conv.add_point((9,0.5))
    conv.add_point((12,2))
    conv.add_point((14,4))

    conv.add_segment((0,5), (9,0.5))
    conv.add_segment((12,2), (14,4))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_4_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((22,0))
    conv.add_point((30,0))

    conv.add_point((16,-3))
    conv.add_point((16,-6))

    conv.add_point((16,2))
    conv.add_point((16,6))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((22,0), (30,0))
    conv.add_segment((16,-3), (16,-6))
    conv.add_segment((16,2), (16,6))

    conv.add_segment((0,0), (16,-6))
    conv.add_segment((16,-6), (30,0))
    conv.add_segment((30,0), (16,6))
    conv.add_segment((16,6), (0,0))


    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_cocircular_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,1))

    conv.add_point((3,0))
    conv.add_point((2,1))

    conv.add_point((0,3))
    conv.add_point((1,2))

    conv.add_point((3,3))
    conv.add_point((2,2))

    conv.add_segment((0,0), (1,1))
    conv.add_segment((3,0), (2,1))
    conv.add_segment((0,3), (1,2))
    conv.add_segment((3,3), (2,2))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_parallel_movement():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,0))
    conv.add_point((2,0))
    conv.add_point((3,0))

    conv.add_segment((0,0), (1,0))
    conv.add_segment((1,0), (2,0))
    conv.add_segment((2,0), (3,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_crash_vertex():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,0))


    conv.add_point((0,2))
    conv.add_point((0.5,1.5))
    conv.add_point((1,2))

    conv.add_segment((0,0), (1,0))
    conv.add_segment((0,2), (0.5,1.5))
    conv.add_segment((1,2), (0.5,1.5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test4_3_3():
    # make this a function
    # crash_time(tri)
    tri = KineticTriangle()

    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (-sqrt(2),sqrt(2))

    b = KineticVertex()
    b.origin = (1,0)
    b.velocity = (sqrt(2),sqrt(2))

    c = KineticVertex()
    c.origin = (0.5, 1.5)
    c.velocity = (0,-1)

    tri.vertices = [a, b, c]
    # a -> b constrained

    # FIXME: would this work with triangle at terminal vertex ?
    # the problem could be that there is no support line for the 'constrained' 
    # edge

    print tri
    Mv = tuple(map(sub, c.origin, a.origin))
    print Mv

    m =  map(sub, b.origin, a.origin)
    m = norm(m)
    print m
    # normalize m!
    n = perp(m)
    print n
    distance_v_e = dot(Mv, n)
    print "dist", distance_v_e
    s = c.velocity
    # different from section 4.3.3: we need to negate n, so that we obtain s' 
#     neg_n = tuple([-i for i in n])
    crash_time = distance_v_e / (1 - dot(s, n))
    print "time vertex crashes on edge:", crash_time 
    coeff = area_collapse_time_coeff(a, b, c)
    print solve_quadratic(coeff[0], coeff[1], coeff[2])
    import matplotlib.pyplot as plt
    print "roots", numpy.roots(coeff)
    x = range(-40, 100)
    y = [quadratic(y, coeff[0], coeff[1], coeff[2]) for y in x]
    plt.plot(x,y)
    plt.show()

    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_0():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (2,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (1, 3)
    c.velocity = (0,-1)
    tri.neighbours = [True, True, True] # make them not None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_1():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (2,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (1, 3)
    c.velocity = (0,-1)
    tri.neighbours = [True, True, None] # make them not None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_2():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (2,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (1, 3)
    c.velocity = (0,-1)
    tri.neighbours = [None, True, None] # make them None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_3():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (1,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (0.5, 1)
    c.velocity = (0,-1)
    tri.neighbours = [None, None, None] # make them None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)


def test_flip():
    """Flip 2 triangles
    """
    # the 2 to be flipped
    tri0 = KineticTriangle()
    tri1 = KineticTriangle()

    # surrounding neighbours
    tri2 = KineticTriangle()
    tri2.vertices = [None, "a", "c"]
    tri3 = KineticTriangle()
    tri3.vertices = [None, "b", "a"]
    tri4 = KineticTriangle()
    tri4.vertices = [None, "d", "b"]
    tri5 = KineticTriangle()
    tri5.vertices = [None, "c", "d"]

    tri2.neighbours[0] = tri0
    tri3.neighbours[0] = tri0
    tri4.neighbours[0] = tri1
    tri5.neighbours[0] = tri1

    tri0.vertices = ["a","b","c"]
    tri1.vertices = ["c","b","d"]

    tri0.neighbours = [tri1, tri2, tri3]
    tri1.neighbours = [tri4, tri5, tri0]

    assert tri1 in tri0.neighbours
    assert tri2 in tri0.neighbours
    assert tri3 in tri0.neighbours

    flip(tri0, 0, tri1, 2)

    assert tri0 in tri1.neighbours
    assert tri2 in tri1.neighbours
    assert tri5 in tri1.neighbours

    assert tri1 in tri0.neighbours
    assert tri3 in tri0.neighbours
    assert tri4 in tri0.neighbours

    assert "a" in tri0.vertices
    assert "b" in tri0.vertices
    assert "d" in tri0.vertices

    assert "a" in tri1.vertices
    assert "c" in tri1.vertices
    assert "d" in tri1.vertices

if __name__ == "__main__":
#     test_flip()
#     try:
#         test_single_point()
#     except:
#         pass
#     test_poly()
#     test_simple_poly()
#     test_1_segment()
#     test_single_line()
#     test_three_lines()
#     test_arrow_four_lines()
    test_triangle()
#     test_parallel_movement()
#     test_quad()
#     test_two_lines_par()
#     test_polyline()
#     test_2_segments()
#     test_2_perp_segments()
#     test_45_deg_segments()
#     test_30_deg_segments()
#     test_4_segments()
#     test_cocircular_segments()
#     test_crash_vertex()
#     test4_3_3()
#     test_compute_0()
#     test_compute_1()
#     test_compute_2()
#     test_compute_3()