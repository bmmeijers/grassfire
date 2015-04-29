from collections import namedtuple
from pprint import pprint

from tri import triangulate, ToPointsAndSegments
from tri.delaunay import TriangleIterator, output_triangles
from tri.delaunay import StarEdgeIterator, cw, ccw
from tri.delaunay import output_triangles, output_vertices

from angles import bisector

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
                starts = []
                for i, e in enumerate(around):
                    if e.triangle.constrained[cw(e.side)]:
                        starts.append(i)
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
                assert len(starts) >= 2
                starts.append(starts[0])
                for lo, hi in zip(starts[:-1], starts[1:]):
                    print lo, ":",hi
                    begin, end = around[lo], around[hi]
                    p0 = begin.triangle.vertices[ccw(begin.side)]
                    p1 = v
                    p2 = end.triangle.vertices[ccw(end.side)]
                    p0, p1, p2
                    vec = bisector((p0.x, p0.y), (p1.x, p1.y), (p2.x, p2.y))
                    print >> bisector_fh, "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format((p1.x, p1.y), (p1.x + vec[0], p1.y + vec[1])) 
#                 print begin
#                 print end
#                
#             if starts[0] == 0:
#                 # easy
#                 starts.append(len(around))
#                 groups = []
#                 for lo, hi in zip(starts[:-1], starts[1:]):
#                     groups.append(around[lo:hi])
#             else:
#                 # hard, wrap around
#                 starts = [0] + starts + [len(around)]
#                 print "***"
#                 groups = []
#                 for lo, hi in zip(starts[:-1], starts[1:]):
#                     groups.append(around[lo:hi])
#                 groups[-1].extend(groups[0])
#                 del groups[0]
#             
#             for group in groups:
                
            #break

    # FIXME: for our small example this holds -> move to a unit test later
    assert len(skel.sk_nodes) == 8

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

def main():
    v = Vector(5, 5)
    print type(v)

    t = KineticTriangle()
    t.vertices = [KineticVertex(), KineticVertex(), KineticVertex()]

    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (10, 0), (11, 1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    dt = triangulate(conv.points, None, conv.segments)

    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    init_skeleton(dt)

if __name__ == "__main__":
    main()