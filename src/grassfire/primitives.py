from collections import namedtuple

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
        finite_txt = "finite"
        if not self.triangle.is_finite:
            finite_txt = "infinite"
        return """<Event ({3:5s}) at {0:.12f}, {4}-triangle: {1}, side: {2}, finite: {5}""".format(self.time, id(self.triangle), self.side, self.tp, self.triangle.type, finite_txt)

class Skeleton(object):
    """Represents a Straight Skeleton 
    """
    def __init__(self):
        # positions --> skeleton positions
        self.sk_nodes = []
        # kinetic primitives --> (traced) wavefront
        self.vertices = []
        self.triangles = []

    def segments(self):
        segments = []
        for v in self.vertices:
            if v.stops_at is not None:
                s = (v.position_at(v.starts_at), v.position_at(v.stops_at))
            else:
                s = (v.position_at(v.starts_at), v.position_at(1000))
            segments.append(s)
        return segments

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
    def __init__(self, origin=None, velocity=None):
        self.origin = origin
        self.velocity = velocity

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
        time = 0
        # 4.281470022378475
        return "{0[0]} {0[1]} ".format(self.position_at(time))
    
    def __repr__(self):
        # FIXXME: make other method (dependent on time as argument)
        time = 0
        # 4.281470022378475
        return "KineticVertex({0}, {1})".format(self.origin, self.velocity)

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
    def __init__(self, origin=None):
        self.origin = origin
        self.velocity = (0,0)

    def __repr__(self):
        return "InfiniteVertex({0})".format(self.origin)

    def __str__(self):
        return "{0[0]} {0[1]}".format(self.origin)

    def distance2_at(self, other, time):
        """Cartesian distance *squared* to other point """
        (sx,sy) = self.origin
        (ox,oy) = other.position_at(time)
        # Used for distances in random triangle close to point
        return pow(sx - ox, 2) + pow(sy - oy, 2)

    def position_at(self, time):
        """ """
        return self.origin

#     @property
#     def origin(self):
#         return self.origin

#     @property
#     def velocity(self):
#         return (0,0)

class KineticTriangle(object):
    def __init__(self, v0=None, v1=None, v2=None, n0=None, n1=None, n2=None):
        self.vertices = [v0, v1, v2]
        self.neighbours = [n0, n1, n2]
        self.event = None # point back to event, note this might prevent garbage collection (strong cycle)
        self.info = None

    def __repr__(self):
        """Get representation that we can use to make instance later

        Note that neighbours are not kept, but we represent wavefront edges
        with None and neighbours with True
        """
        n_s = []
        for n in self.neighbours:
            if n is None:
                n_s.append(None)
            else:
                n_s.append(True)
        #n_s = "n0={0[0]}, n1={0[1]}, n2={0[2]}".format(n_s) #
        n_s = ", ".join(map(str, n_s))
        v_s = ", ".join(map(repr, self.vertices))
        s = "KineticTriangle({0}, {1})".format(v_s, n_s)
        return s

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

    def str_at(self, t):
        vertices = []
#         if self.is_finite:
        for idx in range(3):
            v = self.vertices[idx]
            vertices.append("{0[0]} {0[1]}".format(v.position_at(t)))
#         else:
#             # -- find infinite vertex
#             for infinite in range(3):
#                 v = self.vertices[infinite]
#                 if isinstance(v, InfiniteVertex):
#                     break
#             # -- finite
#             for idx in range(3):
#                 if idx == infinite:
#                     # -- if infinite make halfway
#                     idx = infinite
#                     orig_idx, dest_idx = (idx - 1) % 3, (idx + 1) % 3
#                     orig, dest = self.vertices[orig_idx], self.vertices[dest_idx]
#                     ox, oy = orig.position_at(t) 
#                     dx, dy = dest.position_at(t)
#                     d2 = orig.distance2_at(dest, t)
#                     d = d2 ** 0.5
#                     halfway = (ox + dx) * .5, (oy + dy) * .5
#                     #d = orig.distance(dest)
#                     deltax = dx - ox
#                     deltay = dy - oy
#                     if d != 0: # prevent division by zero (resulting in triangles with undetermined direction)
#                         # normalize
#                         deltax /= d
#                         deltay /= d
#                         # multiply with distance multiplied with sqrt(3) / 2
#                         # (to get equilateral triangle)
#                         sqrt3div2 = 0.866025404
#                         deltax *= d * sqrt3div2
#                         deltay *= d * sqrt3div2
#                     print d
#                     O = halfway[0] + deltay, halfway[1] - deltax 
#                     vertices.append("{0[0]} {0[1]}".format(O))
#                 else:
#                     # -- finite vertex
#                     v = self.vertices[idx]
#     #                if v is not None:
#                     vertices.append("{0[0]} {0[1]}".format(v.position_at(t)))
        if vertices:
            vertices.append(vertices[0])
        return "POLYGON(({0}))".format(", ".join(vertices))

    @property
    def type(self):
        """Returns how many 'constrained' / PSLG edges this triangle has
        """
        return self.neighbours.count(None)

    @property
    def is_finite(self):
        return all([isinstance(vertex, KineticVertex) for vertex in self.vertices])


def test_perp():
    kt = KineticTriangle()
    kva, kvb, kvc = KineticVertex(), KineticVertex(), InfiniteVertex()
    kva.origin = (0., 0.)
    kvb.origin = (5., 0.)
    kvc.origin = (2.5, 4.330127019)
    kva.velocity = (0.,1.)
    kvb.velocity = (0.,1.)
    kvc.velocity = (0.,1.)
    kt.vertices = [kva, kvb, kvc]

    print kt.str_at(10)

# test_perp()
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


