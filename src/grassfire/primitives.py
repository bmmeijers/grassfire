from collections import namedtuple
from pprint import pprint

from tri import triangulate, ToPointsAndSegments
from tri.delaunay import TriangleIterator, output_triangles
from tri.delaunay import StarEdgeIterator, cw, ccw
from tri.delaunay import output_triangles, output_vertices

from angles import bisector
from angles import normalize, perp
from operator import add, sub, mul, truediv
from collections import deque

class Skeleton(object):
    """Represents a Straight Skeleton
    """
    def __init__(self):
        # positions
        self.sk_nodes = []
        # kinetic primitives
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


class KineticTriangle(object):
    def __init__(self):
        self.vertices = [None, None, None]
        self.neighbours = [None, None, None]


def init_skeleton(dt):
    """Initialize a data structure that can be used for making the straight
    skeleton.
    """
    skel = Skeleton()

    for v in dt.vertices:
        if v.is_finite:
            skel.sk_nodes.append(SkeletonNode(pos=(v.x, v.y), info=v.info))

    with open("/tmp/bisectors.wkt", "w") as bisector_fh:
        print >> bisector_fh, "wkt"
        for v in dt.vertices:
            if v.is_finite:
                it = StarEdgeIterator(v)
                around = [e for e in it]
                with open("/tmp/vertexit.wkt", "w") as fh:
                    output_triangles([e.triangle for e in around], fh)

                constraints = []
                for i, e in enumerate(around):
                    if e.triangle.constrained[cw(e.side)]:
                        constraints.append(i)
                print "# of constraints", len(constraints)

                # FIXME:
                # Check here how many constrained edges we have outgoing of
                # this vertex.
                #
                # In case 0: degenerate case, should not happen
                # In case 1: we should make two kinetic vertices
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
                        # also update which are constraint 
                        constraints = [idx + shift for idx in constraints]

                    if len(constraints) == 1:
                        edge = around[constraints[0]]
                        start, end = v, edge.triangle.vertices[ccw(edge.side)]
                        vec = normalize((end.x - start.x , end.y - start.y))
                        # first bisector when going ccw at end
                        p2 = tuple(map(add, start, perp(vec)))
                        p1 = v
                        p0 = tuple(map(add, start, perp(perp(vec))))
                        bi = bisector(p0, p1, p2)
                        print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format((p1.x, p1.y), map(add, p1, bi)) 
                        # second bisector when going ccw at end
                        p2 = tuple(map(add, start, perp(perp(vec))))
                        p1 = v
                        p0 = tuple(map(add, start, perp(perp(perp(vec)))))
                        bi = bisector(p0, p1, p2)
                        print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format((p1.x, p1.y), map(add, p1, bi)) 
                        # FIXME insert additional triangle at this side

                    else:
                        assert len(constraints) >= 2
                        # group the triangles around the vertex
                        constraints.append(len(around))
                        groups = []
                        for lo, hi in zip(constraints[:-1], constraints[1:]):
                            groups.append(around[lo:hi])
    
                        # per group make a bisector
                        for group in groups:
                            begin, end = group[0], group[-1]
                            p2 = begin.triangle.vertices[ccw(begin.side)] # the cw vertex
                            p1 = v
                            p0 = end.triangle.vertices[cw(end.side)]      # the ccw vertex
                            bi = bisector(p0, p1, p2)
                            print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format((p1.x, p1.y), map(add, p1, bi))


    # FIXME: for our small example this holds -> move to a unit test later
    # assert len(skel.sk_nodes) == 8

    it = TriangleIterator(dt)
    new = []
    lut = {}
    # triangle -> kinetic triangle (position in new)
    for t in it:
        # skip the external triangle
        if t is dt.external: 
            continue
        lut[t] = len(new)
        new.append(KineticTriangle())

    remove = []
    it = TriangleIterator(dt)
    for t in it:
        # skip the external triangle
        if t is dt.external:
            continue
        idx = lut[t]
        k = new[idx] # kinetic triangle
        for j, n in enumerate(t.neighbours):
            # skip linking to the external triangle
            if n is dt.external or n is None:
                continue
            k.neighbours[j] = new[lut[n]]
        # if we found a triangle that has a None Neighbour -> triangle to remove
        if any([n is None for n in k.neighbours]):
            remove.append(t)

    assert len(remove) == 3
    # FIXME: remove these 3 kinetic triangles, and link their two neighbours
    # that are not None for these triangles properly together!
    with open("/tmp/remove.wkt", "w") as fh:
        output_triangles(remove, fh)

    return skel

def test_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (10, 0), (11, 1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    dt = triangulate(conv.points, None, conv.segments)

    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    init_skeleton(dt)


def test_single_line():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_segment((0, 0), (10,0))

    dt = triangulate(conv.points, None, conv.segments)

    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

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

    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

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

    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    init_skeleton(dt)

def test_quad():
    conv = ToPointsAndSegments()
    conv.add_point((8,4))
    conv.add_point((-2,8))
    conv.add_point((-2,-8))
    conv.add_point((14,10))
    conv.add_segment((8,4), (14,10))
    conv.add_segment((14,10), (-2,8))
    conv.add_segment((-2,8), (-2,-8))
    conv.add_segment((-2,-8), (8,4))

    dt = triangulate(conv.points, None, conv.segments)

    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    init_skeleton(dt)

if __name__ == "__main__":
#     test_poly()
#     test_single_line()
#     test_three_lines()
    test_triangle()
#     test_quad()
