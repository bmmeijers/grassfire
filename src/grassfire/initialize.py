from collections import deque
from operator import add

from tri.delaunay import TriangleIterator, StarEdgeIterator
from tri.delaunay import cw, ccw, orient2d

from grassfire.calc import bisector, normalize, perp
from primitives import Skeleton, SkeletonNode
from primitives import InfiniteVertex, KineticTriangle, KineticVertex

def find_overlapping_triangle(E):
    """find overlapping triangle 180 degrees other way round
    of triangle edge of the first triangle

    it assumes that the edges are around a central vertex
    and that the first triangle has a constrained edge and other edges are not.

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

def rotate_until_not_in_candidates(t, v, direction, candidates):
    seen = set()
    while t is not None and t not in seen:
        seen.add(t)
        side = t.vertices.index(v)
        t = t.neighbours[direction(side)]
        if t not in candidates:
            return t

def init_skeleton(dt):
    """Initialize a data structure that can be used for making the straight
    skeleton.
    """
    skel = Skeleton()

    # make skeleton nodes 
    # -> every triangulation vertex becomes a skeleton node
    nodes = {}
    avg_x = 0.
    avg_y = 0.
    for v in dt.vertices:
        if v.is_finite:
            nodes[v] = SkeletonNode(pos=(v.x, v.y), info=v.info)
            avg_x += v.x / len(dt.vertices)
            avg_y += v.y / len(dt.vertices)
    centroid = InfiniteVertex(avg_x, avg_y)
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
    unwanted = []
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
                unwanted.append(k)
                continue
            k.neighbours[j] = triangle2ktriangle[n]

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
                # FIXME: Replace perp with rotate90cw / rotate90ccw

                # from segment over terminal vertex to this kinetic vertex, 
                # turns right
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
                kvA.starts_at = 0
                kvertices.append(kvA)

                # from segment to this vertex, turns left
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
                kvB.starts_at = 0
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
                kvA.left = kvB,0
                link_around.append( (None, kvA, (first[0].triangle, ccw(first[0].side))))
                kvB.right = kvA,0
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
                    kv.starts_at = 0
                    for edge in group:
                        ktriangle = triangle2ktriangle[edge.triangle]
                        ktriangle.vertices[edge.side] = kv
                    kvertices.append(kv)
                    # link vertices to each other in circular list
                    link_around.append( ((end.triangle, cw(end.side)), kv, (begin.triangle, ccw(begin.side))))

    for left, curv, right in link_around: # left is cw, right is ccw
        if left is not None:
            cwv = triangle2ktriangle[left[0]].vertices[left[1]]
            curv.left = cwv, 0

        if right is not None:
            ccwv = triangle2ktriangle[right[0]].vertices[right[1]]
            curv.right = ccwv, 0

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

    # there are 3 infinite triangles that are supposed to be removed
    # these triangles were already stored in the unwanted list
    remove = []
    for kt in ktriangles:
        if [isinstance(v,InfiniteVertex) for v in kt.vertices].count(True) == 2:
            remove.append(kt)
    assert len(remove) == 3
    assert len(unwanted) == 3
    assert remove == unwanted
    # remove the 3 unwanted triangles and link their neighbours together
    link = []
    for kt in unwanted:
        v = kt.vertices[kt.neighbours.index(None)]
        assert isinstance(v, KineticVertex)
        neighbour_cw = rotate_until_not_in_candidates(kt, v, cw, unwanted)
        neighbour_ccw = rotate_until_not_in_candidates(kt, v, ccw, unwanted)
        side_cw = ccw(neighbour_cw.vertices.index(v))
        side_ccw = cw(neighbour_ccw.vertices.index(v))
        link.append(
            (neighbour_cw, side_cw, neighbour_ccw)
        )
        link.append(
            (neighbour_ccw, side_ccw, neighbour_cw)
        )
    for item in link:
        ngb, side,new_ngb , = item
        ngb.neighbours[side] = new_ngb
    for kt in unwanted:
        kt.vertices = [None, None, None]
        kt.neighbours = [None, None, None]
        ktriangles.remove(kt)
    # replace the infinite vertices by one point in the center of the PSLG
    # (this could be the origin (0,0) if we would scale input to [-1,1] range
    for kt in ktriangles:
        for i, v in enumerate(kt.vertices):
            if isinstance(v, InfiniteVertex):
                kt.vertices[i] = centroid
    assert check_ktriangles(ktriangles)

    skel.sk_nodes = nodes.values()
    skel.triangles = ktriangles
    skel.vertices = kvertices
    # INITIALIZATION FINISHES HERE

    return skel

def check_ktriangles(L, now=0):
    """Check whether kinetic triangles are all linked up properly
    """
    valid = True
    # check if neighbours are properly linked
    for ktri in L:
        for i in range(3):
            ngb = ktri.neighbours[i]
            if ngb is not None:
                if ktri not in ngb.neighbours:
                    print "non neighbouring triangles:", id(ktri), "and", id(ngb)
                    valid = False
        for i in range(3):
            v = ktri.vertices[i]
            if ktri.finite:
                if not ((v.starts_at <= now and v.stops_at > now) or (v.starts_at <= now and v.stops_at == None)):
                    print "triangle",id(ktri)," with invalid kinetic vertex", id(v)," for this time"
                    valid = False
    # check if the sides of a triangle share the correct vertex at begin / end
    for ktri in L:
        for i in range(3):
            ngb = ktri.neighbours[i]
            if ngb is not None:
                j = ngb.neighbours.index(ktri)
                if not ngb.vertices[cw(j)] is ktri.vertices[ccw(i)]:
                    print "something wrong with vertices 1"
                    valid = False
                if not ngb.vertices[ccw(j)] is ktri.vertices[cw(i)]:
                    print "something wrong with vertices 2"
                    valid = False
    return valid
