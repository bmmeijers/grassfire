from collections import namedtuple
from pprint import pprint

from tri import triangulate, ToPointsAndSegments
from tri.delaunay import TriangleIterator, output_triangles
from tri.delaunay import StarEdgeIterator, cw, ccw
from tri.delaunay import output_triangles, output_vertices, output_edges
from tri.delaunay import FiniteEdgeIterator
from tri.delaunay import orient2d

from angles import bisector
from angles import normalize, perp
from operator import add, sub, mul, truediv
from collections import deque

from warnings import warn
from math import atan2, pi

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
    def __init__(self):
        self.origin = None 
        self.velocity = None

        # next / prev pos
        self.ccw_wavefront = None
        self.cw_wavefront = None

        # floats
        self.starts_at = None
        self.stops_at = None

        # Skeleton nodes
        self.start_node = None
        self.stop_node = None

    def __str__(self):
        # FIXXME: make other method (dependent on time as argument)
        time = 0.2
        return "{0} {1}".format(self.origin[0] + time * self.velocity[0], 
                                self.origin[1] + time * self.velocity[1])

class InfiniteVertex(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
#         self.origin = None 
#         self.velocity = None
# 
#         # next / prev pos
#         self.ccw_wavefront = None
#         self.cw_wavefront = None
# 
#         # floats
#         self.starts_at = None
#         self.stops_at = None
# 
#         # Skeleton nodes
#         self.start_node = None
#         self.stop_node = None

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
        # if last leg of triangle makes left turn/straight, 
        # instead of right turn previously
        # we have found the overlapping triangle
        if orient2d(P, Q, R) >= 0: # and overlap is None:
            overlap = e
            idx = i
            break
    assert overlap is not None
    print "overlap", overlap.triangle
    return idx

def is_quad(L):
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
    ktri_no_apex = []
    with open("/tmp/bisectors.wkt", "w") as bisector_fh:
        print >> bisector_fh, "wkt"
        for v in dt.vertices:
            assert v.is_finite, "infinite vertex found"
            print ""
            it = StarEdgeIterator(v)
            around = [e for e in it]
            with open("/tmp/vertexit.wkt", "w") as fh:
                output_triangles([e.triangle for e in around], fh)

            constraints = []
            for i, e in enumerate(around):
                if e.triangle.constrained[cw(e.side)]:
                    constraints.append(i)
            print "# of constraints:", len(constraints)

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
                    print "central vertex", v

                    assert constraints[0] == 0
                    edge = around[0]
                    start, end = v, edge.triangle.vertices[ccw(edge.side)]
                    vec = normalize((end.x - start.x , end.y - start.y))

                    # from segment over terminal vertex to this kinetic vertex, 
                    # turns right
                    # (first bisector when going ccw at end)
                    p2 = tuple(map(add, start, perp(vec)))
                    p1 = v
                    p0 = tuple(map(add, start, perp(perp(vec))))
                    bi = bisector(p0, p1, p2)
                    print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p1, map(add, p1, bi)) 
                    print nodes[v]

                    kvA = KineticVertex()
                    kvA.origin = (p1.x, p1.y)
                    kvA.velocity = bi
                    kvA.start_node = nodes[v]
                    kvertices.append(kvA)

                    # from segment to this vertex, turns left
                    # second bisector when going ccw at end
                    p2 = tuple(map(add, start, perp(perp(vec))))
                    p1 = v
                    p0 = tuple(map(add, start, perp(perp(perp(vec)))))
                    bi = bisector(p0, p1, p2)
                    print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p1, map(add, p1, bi)) 
                    # FIXME insert additional triangle at this side
                    print nodes[v]

                    kvB = KineticVertex()
                    kvB.origin = (p1.x, p1.y)
                    kvB.velocity = bi
                    kvB.start_node = nodes[v]
                    kvertices.append(kvB)

                    groups = [around]

                    split_idx = find_overlapping_triangle(around)

                    print split_idx
                    print len(around)
                    # determine which triangles get an incidence with the
                    # first and which with the second kvertices vertex

                    # first go with kvA
                    # second go with kvB
                    first, second = around[:split_idx], around[split_idx+1:]
                    print "first ", first
                    print "second", second
                    mid = around[split_idx]
                    print "mid   ", mid

                    # go with kvA
                    for e in first:
                        ktriangle = triangle2ktriangle[e.triangle]
                        print ktriangle
                        ktriangle.vertices[e.side] = kvA
                    # go with kvB
                    for e in second:
                        ktriangle = triangle2ktriangle[e.triangle]
                        print ktriangle
                        ktriangle.vertices[e.side] = kvB

                    # for the mid triangle it depends where it should go
                    # based on adding an additional kvertices triangle into 
                    # the triangulation here...

                    # FIXME: the placement of points A and B should be
                    # dependent on the distance between A and L or A and F
                    # to not get False negatives out of the is_quad 
                    # classification
                    triangle = mid.triangle
                    print "PIVOT POINT INDEX", mid.side
                    first_leg = ccw(mid.side)
                    last_leg = cw(mid.side)
                    L = triangle.vertices[last_leg]
                    F = triangle.vertices[first_leg]

                    A = map(add, kvA.origin, kvA.velocity)
                    B = map(add, kvB.origin, kvB.velocity)
                    O = triangle.vertices[mid.side]
                    print "first", first_leg,"|" , F, "(cw)", "last", last_leg, "|" ,L, "(ccw) around", O

                    first_quad = [O, A, F, B, O]
                    last_quad = [O, A, L, B, O]
                    first_ok = is_quad(first_quad)
                    last_ok = is_quad(last_quad)
                    print "first ok", first_ok
                    print "last ok", last_ok

                    # FIXME: update the overlapping triangle and add
                    # a ktriangles triangle at the right location
                    # and update all neighbouring relationships of the
                    # kvertices triangulation

                    # FIXME: 
                    # >>>> how to deal with the ktriangle its undetermined vertex <<<<

                    # how to decide where to go:

                    # if first is True and second True
                    # make ktriangles triangle at first leg
                    # and assign old corner to kvB
                    #
                    # if both not ok, probably at convex hull overlapping with infinite triangle
                    # only, so take guess and use the first leg

                    # if first is True and second False
                    # assign ktriangles triangle to kvA/kvB and the corner to kvB
                    if first_ok or (not first_ok and not last_ok):
                        ktriangle = triangle2ktriangle[mid.triangle]
                        ktriangle.vertices[mid.side] = kvB

                        knew = KineticTriangle()
                        knew.vertices[0] = kvB
                        knew.vertices[1] = kvA
                        knew.vertices[2] = None
                        ktri_no_apex.append(knew)

                        X, Y = mid.triangle, mid.triangle.neighbours[ccw(first_leg)]
                        sideX = X.neighbours.index(Y)
                        sideY = Y.neighbours.index(X)
                        print last_leg
                        print "BETWEEN", id(X), sideX, id(Y), sideY

                        if second: 
                            # could check whether first triangle of second group
                            # corresponds with triangle found
                            print id(second[0].triangle)

                        # FIXME: does this go correct with two adjacent inserted triangles???
                        # update surrounding kinetic triangles
                        kX = triangle2ktriangle[X]
                        kX.neighbours[sideX] = knew
                        kY = triangle2ktriangle[Y]
                        kY.neighbours[sideY] = knew

                        knew.neighbours[0] = kY
                        knew.neighbours[1] = kX

                    # if first is false and second True
                    # assign ktriangles triangle to kvA/kvB and the corner to kvA
                    elif last_ok:
                        ktriangle = triangle2ktriangle[mid.triangle]
                        ktriangle.vertices[mid.side] = kvA

                        knew = KineticTriangle()
                        knew.vertices[0] = kvB
                        knew.vertices[1] = kvA
                        knew.vertices[2] = None
                        ktri_no_apex.append(knew)

                        X, Y = mid.triangle, mid.triangle.neighbours[cw(last_leg)]
                        sideX = X.neighbours.index(Y)
                        sideY = Y.neighbours.index(X)
                        print last_leg
                        print "BETWEEN", id(X), sideX, id(Y), sideY

                        if second: 
                            # could check whether first triangle of second group
                            # corresponds with triangle found
                            print id(second[0].triangle)

                        # FIXME: does this go correct with two adjacent inserted triangles???
                        # update surrounding kinetic triangles
                        kX = triangle2ktriangle[X]
                        kX.neighbours[sideX] = knew
                        kY = triangle2ktriangle[Y]
                        kY.neighbours[sideY] = knew

                        knew.neighbours[0] = kX
                        knew.neighbours[1] = kY

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
                        print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p1, map(add, p1, bi))
                        print nodes[v]
                        kv = KineticVertex()
                        kv.origin = (p1.x, p1.y)
                        kv.velocity = bi
                        kv.start_node = nodes[v]
                        for edge in group:
                            ktriangle = triangle2ktriangle[edge.triangle]
                            print ktriangle
                            ktriangle.vertices[edge.side] = kv

    print len(kvertices), "kvertices vertices"
    for i, kv in enumerate(kvertices):
        print "=" * 10
        print "vertex", i
        print "=" * 10
        print kv.origin
        print kv.velocity
        print kv.start_node.pos
        print kv.ccw_wavefront
        print kv.cw_wavefront
        print ""

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

#     inf = next(infinites.iterkeys())
    for kt in ktri_no_apex:
        try:
            ngb = kt.neighbours[0]
            side = ngb.neighbours.index(kt)
            kt.vertices[2] = ngb.vertices[ccw(side)]
            ktriangles.append(kt)
        except ValueError:
            warn("Problematic case found")

    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles(ktriangles, fh)
    # assert len(remove) == 3
    # FIXME: remove these 3 kvertices triangles, and link their two neighbours
    # that are not None for these triangles properly together!
    #with open("/tmp/remove.wkt", "w") as fh:
#        output_triangles(remove, fh)

    return skel

def output_dt(dt):
    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    with open("/tmp/segments.wkt", "w") as fh:
        output_edges([e for e in FiniteEdgeIterator(dt, True)], fh)

def test_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (10, 0), (11, 1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
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
    # should raise
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

    conv.add_point((16,-2))
    conv.add_point((16,6))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((22,0), (30,0))
    conv.add_segment((16,-3), (16,-6))
    conv.add_segment((16,-2), (16,6))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


if __name__ == "__main__":
#     test_poly()
#     test_1_segment()

#     test_single_line()
#     test_three_lines()
#     test_arrow_four_lines()
#     test_triangle()
#     test_quad()
#     test_two_lines_par()
#     test_polyline()
#     test_2_segments()
    test_4_segments()
#     test_2_perp_segments()
#     test_45_deg_segments()
