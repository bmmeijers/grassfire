#from brep.geometry import Point
from predicates import orient2d, incircle
from intersector import coincident, intersecting, \
    NOT_INTERSECTING, \
    INTERSECTING_AT_END, INTERSECTING, \
    FULL_OVERLAP, PARTLY_OVERLAP

__license__ = "MIT license"

#cdef enum HE_TYPE:
HE_AUXILARY = 1
HE_BOUNDARY = 2
HE_CONSTRAINT = 4

#cdef enum PT_TYPE:
PT_INTERIOR = 1
PT_BOUNDARY = 2
PT_DELETED = 4
PT_TRANSLATED = 8
PT_XSECTION = 16
PT_BOUNDS = 32

#cdef enum FW_TYPE:
FW_COINCIDENT = 1
FW_CLOCKWISE = 2

## -- Mesh -------------------------------------------------------------------
class Mesh(object):
    def __init__(self, boundary = None):
        """Inits mesh and sets up large triangle in which triangulation should
        take place
        
        """
#        cdef Vertex pt1
#        cdef HalfEdge he1
#        cdef int i, s
        
        self.vertices = []
        self.half_edges = set()
        self.delaunay_queue = [] #set()
        # This is a large triangle surrounding vertices (**ccw**)
        # (implies linear scan over all vertices to be inserted)
        if boundary is None:
            inf = 1e9
            neginf = -inf
            boundary = [ Vertex(inf, neginf),  
                         Vertex(0, inf), 
                         Vertex(neginf, neginf)]
        s = len(boundary)
        link = []
        for i in xrange(s):
            pt1 = boundary[i]
            pt1.type = PT_BOUNDARY
            he1 = HalfEdge() 
            he1.origin = pt1
            he1.type = HE_BOUNDARY
            self.half_edges.add(he1)
            link.append(he1)
            pt1.he = he1
            self.vertices.append(pt1)
        # link outer halfhes (note: were inserted ordered into link)
        s = len(self.half_edges)
        for i in xrange(s):
            he1 = link[i]
            he1.next = link[(i + 1) % s]
        # del link

    def insert(self, vertex): # checked
        """Inserts a new vertex into triangulation structure
        """
#        cdef HalfEdge start
        walk = self.locate(vertex)
        start = walk[0]
        if coincident(vertex, start.origin):
#            start.origin.weights.extend(vertex.weights)
            return start.origin
        if coincident(vertex, start.next.origin):
#            start.next.origin.weights.extend(vertex.weights)
            return start.next.origin
        if coincident(vertex, start.next.next.origin):
#            start.next.next.origin.weights.extend(vertex.weights)
            return start.next.next.origin
        self.vertices.append(vertex)
        # split he or split face
        if walk[1] == FW_COINCIDENT:
            #if DEBUG: print "-- ***"
            self.flip12(walk[0], vertex)
        else:
            self.flip13(walk[0], vertex)
        # update delaunay
        self.update_delaunay()
        return vertex
    
    def locate(self, point):
#        cdef Vertex initial_pt
        # TODO: refactor so that this method also returns when point to be
        # located is on a point in the triangulation
        # That is now done as post check after this method in insert()
        
        # Find random close point to P 
        # (see Fast randomized point location, Mucke, 1999)

#        no = int(pow(len(self.vertices), 0.333333))
#        #if DEBUG: print "-- sample: ", no, "from", len(self.vertices), "vertices"
#        pts = sample(self.vertices, no)
#        assert len(pts) > 0
#        if len(pts) == 1:
#            initial_pt = pts[0]
#        else:
#            min_dist = dist(pts[0], point)
#            initial_pt = pts[0]
#            for pt in pts[1:]:
#                d = dist(pt, point)
#                if d < min_dist:
#                    min_dist = d
#                    initial_pt = pt
        # start from last insert pt
        initial_pt = self.vertices[-1]
        # face walk
        walk = self.walk_to_point(initial_pt.he, point)
        return walk

    def walk_to_point(self, half_he, point): # checked
        """Returns halfhe of triangle that contains given ``point''. 
        Walks the triangulation, starting at ``half_he''.
        """
#        cdef HalfEdge he0, he1, he2
#        cdef list 
        ccw = [0.0, 0.0, 0.0]
#        cdef int i
        
        he0 = half_he
        for _ in xrange(len(self.half_edges)):
            he1 = he0.next
            he2 = he1.next
            try:
                assert he2.next == he0, "found non-face"
            except AssertionError:
                raise
            # orient
            ccw[0] = orient2d(he0.origin, he1.origin, point)
            if ccw[0] < 0:
                he0 = he0.sibling
                continue
            ccw[1] = orient2d(he1.origin, he2.origin, point)
            if ccw[1] < 0:
                he0 = he1.sibling
                continue
            ccw[2] = orient2d(he2.origin, he0.origin, point)
            if ccw[2] < 0:
                he0 = he2.sibling
                continue
            #
            if ccw[0] == 0:
                return (he0, FW_COINCIDENT)
            if ccw[1] == 0:
                return (he1, FW_COINCIDENT)
            if ccw[2] == 0:
                return (he2, FW_COINCIDENT)
            #
            return (he0, FW_CLOCKWISE)
        else:
            raise ValueError("No face found, \
            insertion of [%s] outside large rectangle?" % point)

    def flip12(self, he, point):
        """Splits a halfhe in two and adds two extra hes into 
        quadrilateral. If no constraints, this could be solved with a 
        flip13 as well.
        """
#        cdef HalfEdge he1, he2, he3, he4, he_add1, he_add2, he_add3
        
        if he.type == HE_BOUNDARY:
            raise ValueError("Attempting to split boundary he")
        he1 = self.find_previous(he)
        he2 = he.sibling.next
        he3 = self.find_previous(he.sibling)
        he4 = he.next
        # split the halfhe
        he.origin = point
        point.he = he
        # add halfhes
        he_add1 = self.add_half_he(point, he1.origin)
        he_add2 = self.add_half_he(point, he2.origin)
        if he.type == HE_CONSTRAINT:
            self.constrain_he(he_add2)
        he_add3 = self.add_half_he(point, he3.origin)
        # link halfhes
        he_add1.next = he1
        he_add2.next = he2
        he_add3.next = he3
        #
        he4.next = he_add1.sibling
        he1.next = he_add2.sibling
        he2.next = he_add3.sibling
        #
        he_add1.sibling.next = he
        he_add2.sibling.next = he_add1
        he_add3.sibling.next = he_add2
        #
        he.sibling.next = he_add3
        # update the point->halfhe pointers
        self.update_half_he(he2)
        # add halfhes to delaunay test
#        self.delaunay_queue.add(he)
#        self.delaunay_queue.add(he1)
#        self.delaunay_queue.add(he2)
#        self.delaunay_queue.add(he3)
#        self.delaunay_queue.add(he4)
        self.delaunay_queue.append(he)
        self.delaunay_queue.append(he1)
        self.delaunay_queue.append(he2)
        self.delaunay_queue.append(he3)
        self.delaunay_queue.append(he4)

    def flip13(self, he1, point): # flip13 (start with 1 -> end up 3)
        """Performs insertion of the ``point'' inside a triangle 
        (given by ``he1'')
        """
#        cdef HalfEdge he2, he3, he1_add, he2_add, he3_add
        he2 = he1.next
        he3 = he2.next
        #
        he1_add = self.add_half_he(point, he1.origin)
        he2_add = self.add_half_he(point, he2.origin)
        he3_add = self.add_half_he(point, he3.origin)
        #
        point.he = he1_add
        #
        he1_add.next = he1
        he2_add.next = he2
        he3_add.next = he3
        #
        he1.next = he2_add.sibling
        he2.next = he3_add.sibling
        he3.next = he1_add.sibling
        #
        he1_add.sibling.next = he3_add
        he3_add.sibling.next = he2_add
        he2_add.sibling.next = he1_add
        #
#        self.delaunay_queue.add(he1_add)
#        self.delaunay_queue.add(he2_add)
#        self.delaunay_queue.add(he3_add)
#        #
#        self.delaunay_queue.add(he1)
#        self.delaunay_queue.add(he2)
#        self.delaunay_queue.add(he3)
        
        self.delaunay_queue.append(he3)
        self.delaunay_queue.append(he2)
        self.delaunay_queue.append(he1)

    def add_vertex13(self, he1, vertex):
        """Performs insertion of the ``vertex'' inside a triangle 
        (given by ``he1'')
        
        (start with 1 -> end up 3)
        """
        print "ADDING",vertex, "(vertex13)"
        self.vertices.append(vertex)
        he2 = he1.next
        he3 = he2.next
        #
        he1_add = self.add_half_he(vertex, he1.origin)
        he2_add = self.add_half_he(vertex, he2.origin)
        he3_add = self.add_half_he(vertex, he3.origin)
        #
        vertex.he = he1_add
        #
        he1_add.next = he1
        he2_add.next = he2
        he3_add.next = he3
        #
        he1.next = he2_add.sibling
        he2.next = he3_add.sibling
        he3.next = he1_add.sibling
        #
        he1_add.sibling.next = he3_add
        he3_add.sibling.next = he2_add
        he2_add.sibling.next = he1_add

    def add_vertex24(self, he1, vertex):
        """Performs insertion of the ``vertex'' in interior of he
        and making 
        
        (start with 2 -> end up 4 triangles)
        """
        self.vertices.append(vertex)
        print "ADDING",vertex, "(vertex24)"
        he2 = he1.next
        he3 = he2.next
        he4 = he1.sibling
        he5 = he4.next
        he6 = he5.next
        assert he6.next is he4
        
        print "1", he1.origin, he1.sibling.origin
        print "2", he2.origin, he2.sibling.origin
        print "3", he3.origin, he3.sibling.origin
        print "4", he4.origin, he4.sibling.origin, id(he4.origin)
        print "5", he5.origin, he5.sibling.origin
        print "6", he6.origin, he6.sibling.origin
        
        print "hea = "
        hea = self.add_half_he(vertex, he2.origin)
        print "heb ="
        heb = self.add_half_he(vertex, he3.origin)
        print "hec ="
        hec = self.add_half_he(he6.origin, vertex)
        
        print "o1", he1.origin, he1.origin.he
        print "o2", he2.origin, he2.origin.he
        print "o3", he3.origin, he3.origin.he
        print "o4", he4.origin, he4.origin.he
        print "o5", he5.origin, he5.origin.he
        print "o6", he6.origin, he6.origin.he
        
        vertex.he = heb
        he4.origin = vertex
        self.update_half_he(he4)
        print "***", 
        print he1.sibling.origin, he1.sibling.origin is vertex
        print hea.origin, hea.sibling.origin
        print he2.origin
        
#        print he4.origin, he4.origin.he, he4.origin.he.sibling
#        he4.origin = vertex
#        vertex.he = he4
#        print he2.origin, he2.origin.he
        print vertex.he
        # update 10 next pointers
        hea.next = he2
        hea.sibling.next = hec.sibling
        
        heb.next = he3
        heb.sibling.next = hea
        
        hec.next = he4
        hec.sibling.next = he6
        
        he1.next = heb
        he5.next = hec
        
        he6.next = hea.sibling
        he2.next = heb.sibling

        assert he1.next
        assert he1.sibling.next
        assert he2.next
        assert he2.sibling.next
        assert he3.next
        assert he3.sibling.next
        assert he4.next
        assert he4.sibling.next
        assert he5.next
        assert he5.sibling.next
        assert he6.next
        assert he6.sibling.next
        assert hea.next
        assert hea.sibling.next
        assert heb.next
        assert heb.sibling.next
        assert hec.next
        assert hec.sibling.next
        
    def split_constraint(self, he, p):
        """Splits a constraint in two, if newly inserted constraint 
        crosses constraint already there
        """
#        cdef Vertex p0
#        cdef HalfEdge he0, he_test
#        cdef int i
        #p0 = Vertex(p.x, p.y)
        p0 = Vertex(p.x, p.y)
#        p0.x = p.x
#        p0.y = p.y
        self.vertices.append(p0)
        he0 = self.add_half_he(p0, he.sibling.origin)
        self.constrain_he(he0)
        he.sibling.origin = p0
        p0.he = he0
        self.update_half_he(he0.sibling)
        # link halfhes
        he0.next = he.next
        he.next = he0
        he0.sibling.next = he.sibling
        # find halfhe pointing to he.sibling
        he_test = he.sibling
        for _ in xrange(len(self.half_edges)):
            if (he_test.next == he.sibling):
                he_test.next = he0.sibling
                break
            he_test = he_test.next

    def add_half_he(self, va, vb):
        """Adds two halfhes between ``va'' and ``vb''
        """
#        cdef HalfEdge he1, he2
        he1 = HalfEdge()
        he1.origin = va
        # FIXME:
        va.he = he1
        
        he2 = HalfEdge()
        he2.origin = vb
        #FIXME:
        vb.he = he2
        
        he1.sibling = he2
        he2.sibling = he1
        
        self.half_edges.add(he1)
        self.half_edges.add(he2)
        
        print "added", he1, he1.sibling
        print "added", he2, he2.sibling
        
        return he1

    def update_delaunay(self):
        """Checks if halfhes on delaunay_queue are Delaunay, if not, it flips
        them, which queues the related halfhes
        """
#        cdef HalfEdge he
#        cdef Vertex p1, p2, p3, p4
        while len(self.delaunay_queue) > 0:
            he = self.delaunay_queue.pop()
            if he.type == HE_AUXILARY:
                p1 = he.next.origin
                p2 = he.next.next.origin
                p3 = he.origin
                p4 = he.sibling.next.next.origin
                if incircle(p1, p2, p3, p4) > 0 or incircle(p3, p4, p1, p2) > 0:
                    self.flip22(he)

    def flip22_event(self, he):
        """Flips half edges inside quadrilateral
        
        E.g.:
           o
          /|\
         / | \
        o  |  o
         \ | /
          \|/
           o
        becomes:
           o
          / \
         /   \
        o-----o
         \   /
          \ /
           o
        """
#        cdef HalfEdge he1, he2, he3, he4
        # he is the diagonal that should be flipped
        assert he.type != HE_BOUNDARY, "Boundary is not allowed to flip"
        assert he.sibling.type != HE_BOUNDARY, "Boundary is not allowed to flip"
        he1 = he.next
        he2 = he1.next
        he3 = he.sibling.next
        he4 = he3.next
        # flip origins
        he.origin = he2.origin
        he.sibling.origin = he4.origin
        # update point->halfhe pointers
        self.update_half_he(he3)
        self.update_half_he(he1)
        # link he's
        he1.next = he
        he.next = he4
        he4.next = he1
        he3.next = he.sibling
        he.sibling.next = he2
        he2.next = he3


    def flip22(self, he):
        """Flips hes inside quadrilateral
        
        E.g.:
           o
          /|\
         / | \
        o  |  o
         \ | /
          \|/
           o
        becomes:
           o
          / \
         /   \
        o-----o
         \   /
          \ /
           o
        """
#        cdef HalfEdge he1, he2, he3, he4
        
        assert he.type != HE_BOUNDARY, "Boundary is not allowed to flip"
        assert he.sibling.type != HE_BOUNDARY, "Boundary is not allowed to flip"
        he1 = he.next
        he2 = he1.next
        he3 = he.sibling.next
        he4 = he3.next
        # flip origins
        he.origin = he2.origin
        he.sibling.origin = he4.origin
        # update point->halfhe pointers
        self.update_half_he(he3)
        self.update_half_he(he1)
        # link he's
        he1.next = he
        he.next = he4
        he4.next = he1
        he3.next = he.sibling
        he.sibling.next = he2
        he2.next = he3
        # add he's to delaunay test
#        self.delaunay_queue.add(he1)
#        self.delaunay_queue.add(he2)
#        self.delaunay_queue.add(he3)
#        self.delaunay_queue.add(he4)
        self.delaunay_queue.append(he4)
        self.delaunay_queue.append(he3)
    
    def update_half_he(self, he):
        if he.origin.type == PT_INTERIOR:
            he.origin.he = he

    def find_previous(self, he): # checked
        """Find previous halfhe of this one, even if other halfhes have 
        been removed (in case we are adding a constraint)
        """
#        cdef HalfEdge he_search
#        cdef int i
        assert he is not None
        he_search = he.next
        for _ in xrange(len(self.half_edges)):
            if he_search.next == he:
                break
            he_search = he_search.next
        return he_search
    
    def construct_polygon(self, he):
        """Returns list of halfhes that form polygon that has to be
        re-triangulated
        """
#        cdef HalfEdge he_search
#        cdef int i
#        cdef list polygon
        polygon = []
        polygon.append(he)
        he_search = he.next
        for _ in xrange(len(self.half_edges)):
            if he_search == he:
                break
            polygon.append(he_search)
            he_search = he_search.next
        return polygon

    def add_he(self, he1, he2, he1_prev, he2_prev):
        """Adds halfhe into the structure
        """
#        cdef HalfEdge he_add
        he_add = self.add_half_he(he1.origin, he2.origin)
        self.delaunay_queue.append(he_add)
        he_add.next = he2
        he1_prev.next = he_add
        he_add.sibling.next = he1
        he2_prev.next = he_add.sibling
        return he_add
    
    def constrain_he(self, he):
        """Changes type of ``he'' and its sibling to constraint
        """
        if he.type == HE_BOUNDARY:
            return False
        he.type = HE_CONSTRAINT
        he.sibling.type = HE_CONSTRAINT
        return True

    def fill_he_visible_polygon(self, he):
#        cdef list 
        polygon = self.construct_polygon(he)
        self.fill_he_visible_polygon_recurse(polygon)
        for he in polygon:
            self.delaunay_queue.append(he)

    def fill_he_visible_polygon_recurse(self, polygon):
#        cdef int i, s, c
#        cdef Vertex pa, pb, pc, p
#        cdef HalfEdge he0, he1, he2, he3, he_add
        s = len(polygon)
        if (s > 3):
            he0 = polygon[0]
            he1 = polygon[1]
            he2 = polygon[2]
            pa = he0.origin
            pb = he1.origin
            pc = he2.origin
            c = 2
            for i in xrange(3, s):
                he0 = polygon[i]
                p = he0.origin
                if (incircle(pa, pb, pc, p) > 0):
                    pc = p
                    c = i
            if (c < (s-1)):
                he0 = polygon[0]
                he1 = polygon[c]
                he2 = polygon[s-1]
                he3 = polygon[c-1]
                he_add = self.add_he(
                        he0,
                        he1,
                        he2,
                        he3)
                self.fill_he_visible_polygon_recurse(self.construct_polygon(he_add))
            if (c > 2):
                he0 = polygon[1]
                he2 = polygon[0]
                he3 = polygon[c-1]
                he1 = he3.next
                he_add = self.add_he(
                        he0,
                        he1,
                        he2,
                        he3)
                self.fill_he_visible_polygon_recurse(self.construct_polygon(he_add.sibling))

#    cpdef bint 
    def add_constraint(self, v_start, v_end):
#        cdef Vertex initial_pt, v_cmp, p
#        cdef HalfEdge he_close, he, he_start, he_start_prev, he_search
#        cdef int i
#        cdef INTERACT interaction, interact2

        initial_pt = self.vertices[len(self.vertices)-1]
        walk = self.walk_to_point(initial_pt.he, v_start)
        he_close = walk[0]
        for v_cmp in [he_close.origin, 
                       he_close.next.origin, 
                       he_close.next.next.origin]:
            if coincident(v_start, v_cmp):
                v_start = v_cmp
                break
        else:
            raise ValueError("Start point of constraint not in triangulation")
        walk = self.walk_to_point(initial_pt.he, v_end)
        he_close = walk[0]
        for v_cmp in [he_close.origin, 
                       he_close.next.origin, 
                       he_close.next.next.origin]:
            if coincident(v_end, v_cmp):
                v_end = v_cmp
                break
        else:
            raise ValueError("End point of constraint not in triangulation")
        walk = self.start_face_walk(v_start, v_end)
        if (walk[1] == FW_COINCIDENT):
            return self.constrain_he(walk[0])
        he_start = walk[0]
        he_start_prev = self.find_previous(he_start)
        he_search = he_start.next
        for _ in xrange(len(self.half_edges)):
            v_search0 = he_search.origin
            v_search1 = he_search.next.origin
            if v_search1 == v_end:
                break
            assert not coincident(v_search1, v_start)
            assert not coincident(v_search1, v_end)
            interaction = intersecting(v_start, v_end, v_search0, v_search1)
#            assert interaction != NOT_INTERSECTING
            if interaction is INTERSECTING and he_search.type is HE_AUXILARY:
                self.remove_he(he_search)
                he_search = he_search.sibling
            elif interaction in (INTERSECTING_AT_END, 
                INTERSECTING, FULL_OVERLAP, PARTLY_OVERLAP):
                raise ValueError("Intersection found, that we should not find")
            he_search = he_search.next
        else:
            raise ValueError('Too many iterations for adding constrained he')
        self.add_constraint_he(he_start,he_search.next,he_start_prev,he_search)
        self.update_delaunay()
        return True

    def add_constraint_he(self, he1, he2, he1_prev, he2_prev):
#        cdef HalfEdge he_add
        he_add = self.add_he(he1, he2, he1_prev, he2_prev)        
        self.constrain_he(he_add)
        self.fill_he_visible_polygon(he_add)
        self.fill_he_visible_polygon(he_add.sibling)

    def remove_he(self, he):
#        cdef HalfEdge he_prev, he_sib_prev
        assert he.type != HE_CONSTRAINT
        assert he.sibling.type != HE_CONSTRAINT
        he_prev = self.find_previous(he)
        he_sib_prev = self.find_previous(he.sibling)
        self.half_edges.remove(he)
        self.half_edges.remove(he.sibling)
        assert he not in self.half_edges
        assert he.sibling not in self.half_edges
        if he in self.delaunay_queue:
            self.delaunay_queue.remove(he)
        if he.sibling in self.delaunay_queue:
            self.delaunay_queue.remove(he.sibling)
        if he.sibling is he_prev:
            he.origin.he = None
            self.update_half_he(he.next)
        elif he.next is he.sibling:
            he.next.origin.he = None
            self.update_half_he(he.sibling.next)
        else:
            self.update_half_he(he.next)
            self.update_half_he(he.sibling.next)
        he_prev.next = he.sibling.next
        he_sib_prev.next = he.next

    def start_face_walk(self, p_start, p_end):
#        cdef HalfEdge he, he_prev
#        cdef Vertex p_trailing, p_leading
#        cdef double ccw_leading, ccw_trailing
#        cdef int i
        assert not coincident(p_start, p_end)
        he = p_start.he
        assert he is not None
        p_trailing = he.next.origin
        ccw_trailing = orient2d(p_start, p_end, p_trailing)
#        if (p_start.type == PT_BOUNDARY):
#            if (p_trailing == p_end):
#                return (he, FW_COINCIDENT)
#            if (ccw_trailing == 0):
#                if (between_proper(p_start, p_end, p_trailing) or \
#                    between_proper(p_start, p_trailing, p_end) ):
#                    return (he, FW_CLOCKWISE)
        for _ in xrange(len(self.half_edges)):
            assert he is not None
            he_prev = self.find_previous(he)
            p_trailing = he.next.origin
            p_leading = he_prev.origin
            if p_trailing == p_end:
                return (he, FW_COINCIDENT)
            elif p_leading == p_end:
                return (he_prev, FW_COINCIDENT)
            ccw_leading = orient2d(p_start,p_end,p_leading)
            if ccw_leading >= 0 and ccw_trailing < 0:
                return (he, FW_CLOCKWISE)
            ccw_trailing = ccw_leading
            he = he_prev.sibling
        raise ValueError("Face walk failed %d %d -- %s %s" % (ccw_leading, ccw_trailing, p_start, p_end))

    def clear_flags(self):
        for he in self.half_edges:
            he.flag = None

    def reset_flags(self, value):
        for he in self.half_edges:
            he.flag = value

## -- Vertex ------------------------------------------------------------------
class Vertex(object):
    """Vertex in Mesh, can return brep.geometry.Point
    """
    __slots__ = ('x', 'y', 'type', '_he', 'flag', 'label', 'gid', 'info')
    
    def __init__(self, x, y, info = None):
        self.gid = id(self)
        self.x = x
        self.y = y  
        self.type = PT_INTERIOR
        self._he = None
        
        self.flag = 0 # TODO: replace by using info field
        self.label = -1 # TODO: rename to visited?
#        self.weights = [] # replaced by using info field
        self.info = info


    def set_he(self, value):
        print "setting he", value, "for", self
        self._he = value

    def get_he(self):
        return self._he

    he = property(get_he, set_he)

    def __getitem__(self, which):
        if which == 0:
            return self.x
        elif which == 1:
            return self.y

#    def __hash__(self):
#        return hash((self.x, self.y))

    def __str__(self):
        return "<pt ({0} {1})>".format(self.x, self.y)

    @property
    def id(self):
        return id(self)
    
    @property
    def point(self):
        return (self.x, self.y)

class MovingVertex(Vertex):
    def __init__(self, x, y, velocity, info = None):
        super(MovingVertex, self).__init__(x,y,info)
        self.velocity = velocity
    def __str__(self):
        return "<ptm({0} {1}) *d:{2})>".format(self.x, self.y, self.velocity)
    
    def point_at(self, time):
        return (self.x + self.velocity[0] * time,
                self.y + self.velocity[1] * time)
    
## -- HalfEdge ---------------------------------------------------------------
class HalfEdge(object):
    """HalfEdge in Mesh
    """
    __slots__ = ('_origin', 'next', 'sibling', 'type', 'flag', 'label')

    def __init__(self):
        self._origin = None
        self.next = None
        self.sibling = None
        self.type = HE_AUXILARY
        self.label = -1
        self.flag = 0
    
    @property
    def id(self):
        return id(self)
    
    @property
    def constraint(self):
        """Returns whether this he is constrained.
        """
        return self.type is HE_CONSTRAINT

    def __str__(self):
        return "HE<%s>" % (self.origin)
    
    def set_origin(self, value):
        print "setting origin", value, "for", self
        self._origin = value

    def get_origin(self):
        return self._origin

    origin = property(get_origin, set_origin)