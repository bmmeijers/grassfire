from collections import namedtuple

from tri.delaunay import cw, ccw
from tri.delaunay import orient2d

class Event(object):
    def __init__(self, when, tri, side = None, tp = None):
        self.time = when
        self.triangle = tri
        self.side = side
        self.tp = tp

#     def __eq__(self, other):
#         return self.time == other.time
# 
#     def __lt__(self, other):
#         return self.time < other.time
# 
#     def __gt__(self, other):
#         return self.time > other.time

    def __str__(self):
        return """
<<Event at {0}, 
           {1}, 
           {2},
           {3}>>
""".format(self.time, id(self.triangle), self.side, self.tp)

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
    __slots__ = ("pos", "info",)
    def __init__(self, pos, info=None):
        self.pos = pos
        self.info = info # the info of the vertex in the triangulation


class KineticVertex(object):
    __slots__ = ("origin", "velocity", 
                 "starts_at", "stops_at",
                 "start_node", "stop_node",
                 "_left", "_right"
                 )
    def __init__(self):
        self.origin = None 
        self.velocity = None

        # next / prev pos
        # while looking in direction of bisector, see which 
        # kinetic vertex you see on the left, and which on the right
        #self.left = None
        #self.right = None

        self._left = [] # (start, stop, vertex)
        self._right = []

        # floats
        self.starts_at = None
        self.stops_at = None

        # Skeleton nodes
        self.start_node = None
        self.stop_node = None

    def __str__(self):
        # FIXXME: make other method (dependent on time as argument)
        time = 0.918
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

    @property
    def left(self):
        if self._left:
            return self._left[-1][2]

    @property
    def right(self):
        if self._right:
            return self._right[-1][2]

    @left.setter
    def left(self, v):
        """ 
        v is tuple of (reference, time)

        This new reference will super seed old neighbour at this time
        """
        ref, time, = v
        if len(self._left) > 0:
            self._left[-1] = self._left[-1][0], time, self._left[-1][2]
        self._left.append((time, None, ref))

    @right.setter
    def right(self, v):
        ref, time, = v
        if len(self._right) > 0:
            self._right[-1] = self._right[-1][0], time, self._right[-1][2]
        self._right.append((time, None, ref))

    def left_at(self, time):
        for item in self._left:
            if (item[0] <= time and item[1] > time) or \
                (item[0] <= time and item[1] is None):
                return item[2]
        return None

    def right_at(self, time):
        for item in self._right:
            if (item[0] <= time and item[1] > time) or \
                (item[0] <= time and item[1] is None):
                return item[2]
        return None

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
        self.event = None

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
        # if last leg of triangle makes left turn/straight, 
        # instead of right turn previously
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


#     with open("/tmp/kvertices.wkt", "w") as fh:
#         output_kvertices(skel.vertices, fh)

#         try:
#             collapse_time_quadratic(tri)
#             
#         except AttributeError:
#             pass
#     for tri in ktriangles:
#         print tri
#         collapse_time_dot(tri)


