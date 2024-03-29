from collections import namedtuple
from grassfire.calc import near_zero
from grassfire.vectorops import norm

import logging

class Event(object):
    """ """

    def __init__(self, when, tri, side=None, tp=None, tri_tp=-1):
        """ """
        self.time = when
        self.triangle = tri
        self.side = side
        self.tp = tp
        assert tri_tp != -1
        self.triangle_tp = tri_tp

    def __str__(self):
        """ """
        finite_txt = "finite"
        if not self.triangle.is_finite:
            finite_txt = "infinite"
        return """<Event ({3:5s}) at {0:.9g}, {4}-triangle: {1} [{6}], side: {2}, finite: {5}>""".format(
            self.time, id(self.triangle), self.side, self.tp, self.triangle.type, finite_txt, self.triangle.info)


class Skeleton(object):
    """Represents a Straight Skeleton
    """

    def __init__(self):
        """ """
        # positions --> skeleton positions
        self.sk_nodes = []
        # kinetic primitives --> (traced) wavefront
        self.vertices = []
        self.triangles = []
        # when we 'shrink' the geometry to get more floating point accuracy, 
        # we can get back with this object to the original location
        self.transform = None


    def segments(self):
        """ """
        segments = []
        for v in self.vertices:
            if v.stops_at is not None:
                if v.start_node is v.stop_node:
                    logging.info('skipping segment with same start / end node')
                    continue
                else:
                    if self.transform is not None:
                        pt = self.transform.backward(v.start_node.pos), self.transform.backward(v.stop_node.pos)
                    else:
                        pt = (v.start_node.pos, v.stop_node.pos)
                    s = (pt, (v.start_node.info, v.stop_node.info))
            else:
                s = ((v.start_node.pos, v.position_at(1000)), (v.start_node.info, None))
            segments.append(s)
        return segments


class SkeletonNode(object):
    __slots__ = ("pos", "step", "info",)

    def __init__(self, pos, step, info=None):
        self.pos = pos

        x, y = pos
        #assert -2.0 <= x <= 2.0, (x, "construct")
        #assert -2.0 <= y <= 2.0, (y, "construct")

        self.step = step
        self.info = info  # the info of the vertex in the triangulation

    def position_at(self, time):
        """Returns the position of this skeleton node
        (to have same interface as a vertex -> simplifies testing)
        """
        return self.pos


class KineticVertex(object):
    __slots__ = ("origin", "velocity",
                 "starts_at", "stops_at",
                 "start_node", "stop_node",
                 "_left", "_right", "info", "ul", "ur", "inf_fast", "internal", "wfl", "wfr", "turn"
                 )

    def __init__(self, origin=None, velocity=None, ul=None, ur=None):
        self.origin = origin
        self.velocity = velocity
        # next / prev pos
        # while looking in direction of bisector, see which
        # kinetic vertex you see on the left, and which on the right
        self._left = []  # (start, stop, vertex)
        self._right = []

        # floats
        self.starts_at = None
        self.stops_at = None

        # Skeleton nodes
        self.start_node = None
        self.stop_node = None

        self.ul = ul  # unit vector of wavefront to the left
        self.ur = ur  # or right

        self.wfl = None  # wavefront to the left of this vertex
        self.wfr = None

        self.info = id(self)
        self.inf_fast = False  # whether this vertex moves infinitely fast
        self.internal = False

        self.turn = None

    def __str__(self):
        # FIXME: make other method (dependent on time as argument)
        time = 0
        # 4.281470022378475
        return "{0[0]} {0[1]} @{1}".format(self.position_at(time), id(self))

    def __repr__(self):
        """ """
        return "KineticVertex({0}, {1}, {2}, {3})".format(
            self.origin, self.velocity, self.ul, self.ur)

    @property
    def is_stopped(self):
        return self.stop_node is not None

    def distance2(self, other):
        """Cartesian distance *squared* to other point """
        # Used for distances in random triangle close to point
        return pow(self.origin[0] - other.origin[0], 2) + \
            pow(self.origin[1] - other.origin[1], 2)

    def distance2_at(self, other, time):
        """Cartesian distance *squared* to other point """
        (sx, sy) = self.position_at(time)
        (ox, oy) = other.position_at(time)
        # Used for distances in random triangle close to point
        return pow(sx - ox, 2) + pow(sy - oy, 2)

    def position_at(self, time):
        if not self.inf_fast:
            return (self.origin[0] + time * self.velocity[0],
                self.origin[1] + time * self.velocity[1])
        else:
            return self.start_node.pos

    def visualize_at(self, time):
        if not self.inf_fast:
            ## -- if it is a high velocity vertex, render it at its start node
            # magn = norm(self.velocity)  
            # if magn > 10:
            #     return self.start_node.pos
            # else:
            return (self.origin[0] + time * self.velocity[0],
                    self.origin[1] + time * self.velocity[1])
        else:
            return self.start_node.pos

    @property
    def left(self):
        """ """
        if self._left:
            return self._left[-1][2]

    @property
    def right(self):
        """ """
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
        """ """
        ref, time, = v
        if len(self._right) > 0:
            self._right[-1] = self._right[-1][0], time, self._right[-1][2]
        self._right.append((time, None, ref))

    def left_at(self, time):
        """ """
        for item in self._left:
            if (item[0] <= time and item[1] is not None and item[1] > time) or \
                    (item[0] <= time and item[1] is None):
                return item[2]
        return None

    def right_at(self, time):
        """ """
        for item in self._right:
            if (item[0] <= time and item[1] is not None and item[1] > time) or \
                    (item[0] <= time and item[1] is None):
                return item[2]
        return None


class InfiniteVertex(object):  # Stationary Vertex

    def __init__(self, origin=None):
        """ """
        self.origin = origin
        self.velocity = (0, 0)
        # infinitevertex does not have circular thing
        self.left = None
        self.right = None
        self.internal = False
        self.info = id(self)

    def __repr__(self):
        return "InfiniteVertex({0})".format(self.origin)

    def __str__(self):
        return "{0[0]} {0[1]}".format(self.origin)

    def distance2_at(self, other, time):
        """Cartesian distance *squared* to other point """
        (sx, sy) = self.origin
        (ox, oy) = other.position_at(time)
        # Used for distances in random triangle close to point
        return pow(sx - ox, 2) + pow(sy - oy, 2)

    def position_at(self, time):
        """ """
        return self.origin
    def visualize_at(self, time):
        """ """
        return self.origin
#     @property
#     def origin(self):
#         return self.origin

#     @property
#     def velocity(self):
#         return (0,0)


class KineticTriangle(object):

    def __init__(self, v0=None, v1=None, v2=None,
                 n0=None, n1=None, n2=None):
        self.vertices = [v0, v1, v2]
        self.neighbours = [n0, n1, n2]
        self.wavefront_directions = [None, None, None]
        self.wavefront_support_lines = [None, None, None]
        self.event = None  # point back to event,
                           # note this might prevent
                           # garbage collection (strong cycle)
        self.info = None
        self.stops_at = None
        self.internal = False

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
        v_s = ",\n".join(map(repr, self.vertices))
        s = "KineticTriangle({0}, {1})".format(v_s, n_s)
        return s

    def __str__(self):
        """ """
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

    def position_at(self, t):
        """ """
        vertices = []
        for idx in range(3):
            v = self.vertices[idx]
            vertices.append("{0[0]} {0[1]}".format(v.position_at(t)))
        if vertices:
            vertices.append(vertices[0])
        return "POLYGON(({0}))".format(", ".join(vertices))

    def visualize_at(self, t):
        """ """
        vertices = []
#         if self.is_finite:
        for idx in range(3):
            v = self.vertices[idx]
            vertices.append("{0[0]} {0[1]}".format(v.visualize_at(t)))
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
        return all([isinstance(vertex, KineticVertex)
                    for vertex in self.vertices])


def test_perp():
    kt = KineticTriangle()
    kva, kvb, kvc = KineticVertex(), KineticVertex(), InfiniteVertex()
    kva.origin = (0., 0.)
    kvb.origin = (5., 0.)
    kvc.origin = (2.5, 4.330127019)
    kva.velocity = (0., 1.)
    kvb.velocity = (0., 1.)
    kvc.velocity = (0., 1.)
    kt.vertices = [kva, kvb, kvc]

    print(( kt.str_at(10)))

# test_perp()
#     vec = tuple(map(sub, t.vertices[e], t.vertices[s]))
#     vec = rotate90ccw(rotate90ccw(vec))
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
