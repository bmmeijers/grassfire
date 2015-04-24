# -*- coding: utf-8 -*-
'''
Created on Oct 16, 2012

@author: martijn
'''

from triangulation.mesh import Mesh, Vertex, MovingVertex, PT_BOUNDARY
from triangulation.utils import MeshVisualizer
from angles import bisector_vectors
from predicates import orient2d
from math import hypot
#from oseq import OrderedSequence
from prio import PriorityQueue
from eventtime import Track, collapse_time
from epsilon import near

def pos(value):
    if near(value, 0):
        value = 0
    if value > 0:
        return True
    else:
        return False

def triangle(edge):
    return sorted([edge, edge.next, edge.next.next])[0]

class TriangleVisitor(object):
    def __init__(self, mesh):
        self.mesh = mesh
        
    def visit_all(self):
        self.triangles = []
        self.mesh.clear_flags()
        # start from large triangle
        edge, tp = self.mesh.locate(self.mesh.vertices[0])
        stack = set([edge])
        while stack:
            edge = stack.pop()
            # TODO: make exporting infinite triangles optional
            if edge.flag != 1:
                # do not add triangle if infinite triangle
                if edge.origin.type != PT_BOUNDARY and \
                    edge.next.origin.type != PT_BOUNDARY and \
                    edge.next.next.origin.type != PT_BOUNDARY: 
                    self.triangles.append(triangle(edge))
            # flag three edge's that form triangle as visited 
            edge.flag = 1
            edge.next.flag = 1
            edge.next.next.flag = 1
            # stack three neighboring triangles
            if edge.sibling is not None and edge.sibling.flag is None:
                stack.add(edge.sibling)
            if edge.next.sibling is not None and edge.next.sibling.flag is None:
                stack.add(edge.next.sibling)
            if edge.next.next.sibling is not None and edge.next.next.sibling.flag is None:
                stack.add(edge.next.next.sibling)

def dist(pa, pb):
    dx = pa[0] - pb[0]
    dy = pa[1] - pb[1]
    return hypot(dx, dy)

ring = [(0,0), (9,0), (9,10), 
        (5,10), (4.5, 5.), (4,10),
        (0,10), (0,0)]

fh = open("/tmp/pts.wkt", "w")
fh.write("# points\n")
for pt in ring[:-1]:
    fh.write("POINT({0[0]} {0[1]})\n".format(pt))
fh.close()

# fill the mesh
vertices = []
tri = Mesh()
for i, pt in enumerate(ring):
    cur = tri.insert(Vertex(*pt))
    vertices.append(cur)
    if i > 0:
        print prev, "-", cur
        tri.add_constraint(prev, cur)
    prev = cur

fh = open("/tmp/tris.wkt", "w")
fh.write("#triangle\n")
vis = MeshVisualizer(tri)
vis.list_triangles_wkt(fh)
fh.close()

fh = open("/tmp/traces.wkt", "w")
fh.write("#trace\n")
#for i in range(len(ring)-1):
#    # get trace i
#    pt = ring[i]
#    v = directions[i]
#    t = "LINESTRING({} {}, {} {})".format(pt[0], pt[1],
#                                    pt[0]+v[0]*s, pt[1]+v[1]*s)
#    fh.write(t+"\n")

# for every vertex compute bisector
directions = bisector_vectors(ring)

S = 0.25
for i, vertex in enumerate(vertices[:-1]):
    speed = directions[i]
    t = "LINESTRING({} {}, {} {})".format(vertex[0], vertex[1],
                                            vertex[0]+speed[0]*S, 
                                            vertex[1]+speed[1]*S)
    fh.write(t+"\n")
fh.close()

for v in tri.vertices:
    he = v.he
    assert he.origin is v

T = 0.1
# add initial moving vertices to the triangulation 
# into the combinatorial structure
for i, vertex in enumerate(vertices[:-1]):
    print "-" * 70
    speed = directions[i]
    moving = MovingVertex(vertex.x, vertex.y, directions[i])
    if vertex.x == 4.5 and vertex.y == 5:
        first_collapse = moving
    assert moving.he is None
    check = vertex.x + speed[0], vertex.y + speed[1]
    length = dist(vertex, check)
    print "to check", vertex, vertex.he, "->", check, length
#    assert not isinstance(vertex.he.origin, MovingVertex)  
#    print vertex.he, vertex.he.sibling
    cur = vertex.he
    nxt = cur.next.next.sibling
    closeness_eps = 0.08 # distance within 5 degrees of original direction
    for _ in xrange(len(tri.half_edges)):
        print "testing"
        print cur, "--", cur.sibling
        print nxt, "--", nxt.sibling
        
        positive = orient2d(vertex, cur.sibling.origin, check)
        negative = orient2d(vertex, nxt.sibling.origin, check)
        if positive >= 0 and negative <= 0:
            print "found surrounding legs"
            # area = (base * altitude) * 0.5
            # 2 * area = (base * altitude)
            # 2 * area / base = altitude
            pdist = dist(vertex, cur.sibling.origin)
            paltitude = abs(positive) / pdist
            ndist = dist(vertex, nxt.sibling.origin)
            naltitude = abs(negative) / ndist
#            print "cur leg", positive, paltitude, paltitude / length, pdist
#            print "nxt leg", negative, naltitude, naltitude / length, ndist
            print "cur leg", paltitude / length,
            close = 0
            if paltitude / length < 0.1:
                print "(*)close"
                close += 1
            else:
                print ""
            print "nxt leg", naltitude / length,
            if naltitude / length < 0.1:
                print "(*)close"
                close += 2
            else:
                print ""
            print "***"
            
            if close & 1 or close & 2:
#                tri.add_vertex24(cur, moving)
                if close & 1:
                    tri.add_vertex24(cur, moving)
                else:
                    # this seems to be correct...
                    tri.add_vertex24(nxt, moving)
            else:
                tri.add_vertex13(cur, moving)
                
            for v in tri.vertices:
                he = v.he
                print id(v), v
                assert he.origin is v, "{} {} {}".format(he.origin, "vs", v)
#            tri.add_vertex24(nxt, moving)
            break
        print ""
        cur = nxt
        nxt = cur.next.next.sibling


visitor = TriangleVisitor(tri)
visitor.visit_all()

def add_to_pq(he, pq, current = 0):
    """adds a tirangle to the priority queue, if it has
    a positive collapse time 
    
    (only first time it will
    collapse it is added to the queue)"""
    t = triangle(he)
    a, b, c = t, t.next, t.next.next
    if isinstance(a.origin, MovingVertex):
        ta = Track(a.origin.point, a.origin.velocity)
    else:
        ta = Track(a.origin.point, (0,0))
    if isinstance(b.origin, MovingVertex):
        tb = Track(b.origin.point, b.origin.velocity)
    else:
        tb = Track(b.origin.point, (0,0))
    if isinstance(c.origin, MovingVertex):
        tc = Track(c.origin.point, c.origin.velocity)
    else:
        tc = Track(c.origin.point, (0,0))
    C = collapse_time(ta, tb, tc)
    if C:
        C = filter(pos, C)
        print "+", a, b, c
        print "-->", C
        if C:
            pq.add(C[0]+current, a)


pq = PriorityQueue()
for he in visitor.triangles:
    add_to_pq(he, pq)

print len(pq), "events"
time, first = pq.popleft()

def longest_side(he, time):
    """Gets longest side of a triangle at a specific time
    """
    D = dist(he.origin.point_at(time), 
             he.sibling.origin.point_at(time))
    ret = he
    d = dist(he.next.origin.point_at(time), 
             he.next.sibling.origin.point_at(time))
    if d > D:
        ret = he.next
    d = dist(he.next.next.origin.point_at(time), 
             he.next.next.sibling.origin.point_at(time))
    if d > D:
        ret = he.next.next
    return ret

def str_triangle_time(he, time):
    C = "{0[0]:9.5f} {0[1]:9.5f}"
    a, b, _ = he, he.next, he.next.next
    return "Δ"+C.format(a.origin.point_at(time))+";"+\
        C.format(a.sibling.origin.point_at(time))+";"+\
        C.format(b.sibling.origin.point_at(time))
        
def print_pq():
    for p, o in pq:
        print round(p, 3), "--", str_triangle_time(o, time)

# Get the longest edge,
# this is the one that should be flipped
# if it is not a trace and it is not a constrained edge 
diagonal = longest_side(first, time)
pivot = diagonal.next.next.origin

print "=-+" * 18
print pivot
alpha, beta = diagonal.origin, diagonal.next.origin

print pivot.point_at(time), "->", alpha.point_at(time)
print pivot.point_at(time), "->", beta.point_at(time)
print "=-" * 8


#print first_collapse, first_collapse.he, first_collapse.he.sibling
#tri.flip22_event(diagonal) # diagonal

# what should happen now (crash event) ...
# - make vertex static, with current coordinates

# - "halting a moving vertex requires to re-schedule 
#   all triangles attached to this vertex" (mann, held, huber, 2012)

# - span off two new vertices
#   in their correct directions
#   to be able to compute this new direction
#   keep a cyclic double linked list on the vertices



## stop the moving vertex!
x,y = pivot.point_at(time)
print ">>> coords", (x,y)
pivot.x = x
pivot.y = y
pivot.velocity = (0,0)

#
print "=" * 60
print "TRIANGLES AROUND pivot", pivot.x, ",", pivot.y
cur = pivot.he
nxt = cur.next.next.sibling
for _ in xrange(len(tri.half_edges)):
    print str_triangle_time(cur, time)
    print pq.discard(triangle(cur))
    if nxt is pivot.he:
        break
    cur = nxt
    nxt = cur.next.next.sibling
print "=" * 60

tri.flip22_event(diagonal) # diagonal

print str_triangle_time(triangle(diagonal), time)
print str_triangle_time(triangle(diagonal.sibling), time)

add_to_pq(diagonal, pq)
add_to_pq(diagonal.sibling, pq)
print_pq()

if True:
    #
#    to_add = []
    to_add = [
     MovingVertex(x, y, (1.1049875621120888, 1.0)),
     MovingVertex(x, y, (-1.104987562112089, 1.0000000000000002))
    ]
    
    # important! only from now on move...
    for item in to_add:
        item.start = time
    
    for i, moving in enumerate(to_add):
        print "-" * 70
        check = moving.x + moving.velocity[0], moving.y + moving.velocity[1]
        length = dist(pivot.point_at(time), check)
        print "to check", pivot, pivot.he, "->", check, length
    #    assert not isinstance(vertex.he.origin, MovingVertex)  
    #    print vertex.he, vertex.he.sibling
        cur = pivot.he
        nxt = cur.next.next.sibling
        closeness_eps = 0.08 # distance within 5 degrees of original direction
        for _ in xrange(len(tri.half_edges)):
            print "testing"
            print cur, "--", cur.sibling
            print nxt, "--", nxt.sibling
            
            positive = orient2d(pivot.point_at(time), cur.sibling.origin, check)
            negative = orient2d(pivot.point_at(time), nxt.sibling.origin, check)
            if positive >= 0 and negative <= 0:
                print "found surrounding legs"
                # area = (base * altitude) * 0.5
                # 2 * area = (base * altitude)
                # 2 * area / base = altitude
                pdist = dist(pivot.point_at(time), cur.sibling.origin.point_at(time))
                paltitude = abs(positive) / pdist
                ndist = dist(pivot.point_at(time), nxt.sibling.origin.point_at(time))
                naltitude = abs(negative) / ndist
    #            print "cur leg", positive, paltitude, paltitude / length, pdist
    #            print "nxt leg", negative, naltitude, naltitude / length, ndist
                print "cur leg", paltitude / length,
                close = 0
                if paltitude / length < 0.1:
                    print "(*)close"
                    close += 1
                else:
                    print ""
                print "nxt leg", naltitude / length,
                if naltitude / length < 0.1:
                    print "(*)close"
                    close += 2
                else:
                    print ""
                print "***"
                
                if close & 1 or close & 2:
    #                tri.add_vertex24(cur, moving)
                    if close & 1:
                        tri.add_vertex24(cur, moving)
                        add_to_pq(cur, pq, time)
                        add_to_pq(cur.next.sibling, pq, time)
                        add_to_pq(cur.sibling, pq, time)
                        add_to_pq(cur.sibling.next.next.sibling, pq, time)
                    else:
                        # this seems to be correct...
                        tri.add_vertex24(nxt, moving)
                        add_to_pq(nxt, pq, time)
                        add_to_pq(nxt.next.sibling, pq, time)
                        add_to_pq(nxt.sibling, pq, time)
                        add_to_pq(nxt.sibling.next.next.sibling, pq, time)
                else:
                    tri.add_vertex13(cur, moving)
                    add_to_pq(cur, pq, time)
                    add_to_pq(cur.next.sibling, pq, time)
                    add_to_pq(cur.next.next.sibling, pq, time)
                print_pq()
                # FIXME: check can be removed 
                for v in tri.vertices:
                    he = v.he
                    assert he.origin is v, "{} {} {}".format(he.origin, "vs", v)
                break
            print ""
            cur = nxt
            nxt = cur.next.next.sibling
    #
    ##for vertex in tri.vertices:
    ##    print vertex.point_at(time)
    #
    ## reschedule triangles...
    ##for he in (first, first.sibling,):
    ##    a, b, c = he, he.next, he.next.next
    ##    print "Δ", a.origin, a.sibling.origin
    ##    print "_", b.origin, b.sibling.origin
    ##    print "_", c.origin, c.sibling.origin
    ##    if isinstance(a.origin, MovingVertex):
    ##        ta = Track(a.origin.point_at(time), a.origin.velocity)
    ##    else:
    ##        ta = Track(a.origin.point_at(time), (0,0))
    ##    if isinstance(b.origin, MovingVertex):
    ##        tb = Track(b.origin.point_at(time), b.origin.velocity)
    ##    else:
    ##        tb = Track(b.origin.point_at(time), (0,0))
    ##    if isinstance(c.origin, MovingVertex):
    ##        tc = Track(c.origin.point_at(time), c.origin.velocity)
    ##    else:
    ##        tc = Track(c.origin.point_at(time), (0,0))
    ##    C = collapse_time(ta, tb, tc)
    ##    if C:
    ##        C = filter(pos, C)
    ##        print "+", a, b, c
    ##        print "-->", C
    ##        if C:
    ##            oseq.add((C[0]+time, a))
    ##print "---"
    ##for item in oseq:
    ##    print item
    ##print "---"
    ##
    ##time, second = oseq.popleft()
    ##
    ##print ""
    ##print second.origin.point_at(time), second.sibling.origin.point_at(time), dist(second.origin.point_at(time), second.sibling.origin.point_at(time))
    ##print second.next.origin.point_at(time), second.next.sibling.origin.point_at(time), dist(second.next.origin.point_at(time), second.next.sibling.origin.point_at(time))
    ##print second.next.next.origin.point_at(time), second.next.next.sibling.origin.point_at(time), dist(second.next.next.origin.point_at(time), second.next.next.sibling.origin.point_at(time))
    ##
    ##print second.constraint
    ##print second.next.constraint
    ##print second.next.next.constraint
    ##
    ##diagonal = second.next.next
    ##tri.flip22_event(diagonal)
    ##for he in (diagonal, diagonal.sibling,):
    ##    a, b, c = he, he.next, he.next.next
    ##    print "Δ", a.origin, a.sibling.origin
    ##    print "_", b.origin, b.sibling.origin
    ##    print "_", c.origin, c.sibling.origin
    ##    if isinstance(a.origin, MovingVertex):
    ##        ta = Track(a.origin.point_at(time), a.origin.velocity)
    ##    else:
    ##        ta = Track(a.origin.point_at(time), (0,0))
    ##    if isinstance(b.origin, MovingVertex):
    ##        tb = Track(b.origin.point_at(time), b.origin.velocity)
    ##    else:
    ##        tb = Track(b.origin.point_at(time), (0,0))
    ##    if isinstance(c.origin, MovingVertex):
    ##        tc = Track(c.origin.point_at(time), c.origin.velocity)
    ##    else:
    ##        tc = Track(c.origin.point_at(time), (0,0))
    ##    C = collapse_time(ta, tb, tc)
    ##    if C:
    ##        C = filter(pos, C)
    ##        print "+", a, b, c
    ##        print "-->", C
    ##        if C:
    ##            oseq.add((C[0]+time, a))
    ##print "---"
    ##for item in oseq:
    ##    print item
    ##print "---"
    ##
    ##time, third = oseq.popleft()
    ##
    ##print ""
    ##print third.constraint
    ##print third.next.constraint
    ##print third.next.next.constraint
    ##print third.origin.point_at(time), third.sibling.origin.point_at(time), dist(third.origin.point_at(time), third.sibling.origin.point_at(time))
    ##print third.next.origin.point_at(time), third.next.sibling.origin.point_at(time), dist(third.next.origin.point_at(time), third.next.sibling.origin.point_at(time))
    ##print third.next.next.origin.point_at(time), third.next.next.sibling.origin.point_at(time), dist(third.next.next.origin.point_at(time), third.next.next.sibling.origin.point_at(time))
    ##
    ##diagonal = third.next
    ##
    ##print ">>> coords", third.origin.point_at(time)
    ## FIXME: Note that we flip away a constraint edge!!!!
    ##tri.flip22_event(diagonal)
    ## unconstrain the flipped diagonal
    ## constrain the two remaining edges
    ## replace the movingvertex by a static vertex
    ## then
    ## calculate for every inner angle the bisection
    ## introduce a MovingVertex for every point on 
    ## the bisector
    #
    ##time -= 0.01
    ##
    ##print first_collapse, first_collapse.he, first_collapse.he.sibling
    ##tri.flip22_event(first_collapse.he.next.next.sibling.next)
    ##time = 0.4975
    ##time = 0.50
    #
    #time += 0.2

if False:
    time, obj = pq.popleft()
    diagonal = longest_side(obj, time)
    print "collapsing:", str_triangle_time(diagonal, time)
    
    tri.flip22_event(diagonal) # diagonal
    
    print str_triangle_time(triangle(diagonal), time)
    print str_triangle_time(triangle(diagonal.sibling), time)
    
    add_to_pq(diagonal, pq)
    add_to_pq(diagonal.sibling, pq)
    
    print_pq()
    #

if False:
    time, obj = pq.popleft()
    diagonal = longest_side(obj, time)
    print ""
    print_pq()
    print str_triangle_time(obj, time)
    
    vertices_near = 0
    if near(dist(obj.origin.point_at(time), 
                 obj.next.origin.point_at(time)), 0):
        vertices_near += 1
    if near(dist(obj.next.origin.point_at(time), 
                 obj.next.next.origin.point_at(time)), 0):
        vertices_near += 2
    if near(dist(obj.next.next.origin.point_at(time), 
                 obj.origin.point_at(time)), 0):
        vertices_near += 4
    if vertices_near:
        print "WARNING: unhandled vertex crash", vertices_near
        if vertices_near == 1:
            raise NotImplementedError()
        elif vertices_near == 2:
            raise NotImplementedError()
        elif vertices_near == 4:
            x0, y0 = obj.next.next.origin.point_at(time) 
            x1, y1 = obj.origin.point_at(time)
            diagonal = obj.next.next
        print "crash at", (x0+x1)*0.5, (y0+y1)*0.5
    
        print "to delete"
        print diagonal.origin.point_at(time), diagonal
        print diagonal.sibling.origin.point_at(time), diagonal.sibling
    
        pivot = diagonal.sibling.origin
        
        
        # remove the triangles from pq
        print pq.discard(triangle(diagonal))
        print pq.discard(triangle(diagonal.sibling))
        print pq.discard(triangle(diagonal.next.next.sibling))
        
        tri.remove_he(diagonal.next.next)
        tri.remove_he(diagonal.sibling.next)
        tri.remove_he(diagonal)
         
        pivot.x = (x0+x1) * 0.5
        pivot.y = (y0+y1) * 0.5
        pivot.velocity = (0,0)
        pivot.start = time
    
    to_add = [MovingVertex(pivot.x, pivot.y, (-0.9999957061016951, -20.049871135434717))]
    for item in to_add:
        item.start = time
    
    for i, moving in enumerate(to_add):
        print "-" * 70
        check = moving.x + moving.velocity[0], moving.y + moving.velocity[1]
        length = dist(pivot.point_at(time), check)
        print "to check", pivot, pivot.he, "->", check, length
    #    assert not isinstance(vertex.he.origin, MovingVertex)  
    #    print vertex.he, vertex.he.sibling
        cur = pivot.he
        nxt = cur.next.next.sibling
        closeness_eps = 0.08 # distance within 5 degrees of original direction
        for _ in xrange(len(tri.half_edges)):
            print "testing"
            print cur, "--", cur.sibling
            print nxt, "--", nxt.sibling
            
            positive = orient2d(pivot.point_at(time), cur.sibling.origin, check)
            negative = orient2d(pivot.point_at(time), nxt.sibling.origin, check)
            if positive >= 0 and negative <= 0:
                print "found surrounding legs"
                # area = (base * altitude) * 0.5
                # 2 * area = (base * altitude)
                # 2 * area / base = altitude
                pdist = dist(pivot.point_at(time), cur.sibling.origin.point_at(time))
                paltitude = abs(positive) / pdist
                ndist = dist(pivot.point_at(time), nxt.sibling.origin.point_at(time))
                naltitude = abs(negative) / ndist
    #            print "cur leg", positive, paltitude, paltitude / length, pdist
    #            print "nxt leg", negative, naltitude, naltitude / length, ndist
                print "cur leg", paltitude / length,
                close = 0
                if paltitude / length < 0.1:
                    print "(*)close"
                    close += 1
                else:
                    print ""
                print "nxt leg", naltitude / length,
                if naltitude / length < 0.1:
                    print "(*)close"
                    close += 2
                else:
                    print ""
                print "***"
                
                if close & 1 or close & 2:
    #                tri.add_vertex24(cur, moving)
                    if close & 1:
                        tri.add_vertex24(cur, moving)
                        add_to_pq(cur, pq, time)
                        add_to_pq(cur.next.sibling, pq, time)
                        add_to_pq(cur.sibling, pq, time)
                        add_to_pq(cur.sibling.next.next.sibling, pq, time)
                    else:
                        # this seems to be correct...
                        tri.add_vertex24(nxt, moving)
                        add_to_pq(nxt, pq, time)
                        add_to_pq(nxt.next.sibling, pq, time)
                        add_to_pq(nxt.sibling, pq, time)
                        add_to_pq(nxt.sibling.next.next.sibling, pq, time)
                else:
                    tri.add_vertex13(cur, moving)
                    add_to_pq(cur, pq, time)
                    add_to_pq(cur.next.sibling, pq, time)
                    add_to_pq(cur.next.next.sibling, pq, time)
                print_pq()
                break
            print ""
            cur = nxt
            nxt = cur.next.next.sibling
    
    
    time, obj = pq.popleft()
    diagonal = longest_side(obj, time)
    print ""
    print_pq()
    print str_triangle_time(obj, time)
    
    vertices_near = 0
    if near(dist(obj.origin.point_at(time), 
                 obj.next.origin.point_at(time)), 0):
        vertices_near += 1
    if near(dist(obj.next.origin.point_at(time), 
                 obj.next.next.origin.point_at(time)), 0):
        vertices_near += 2
    if near(dist(obj.next.next.origin.point_at(time), 
                 obj.origin.point_at(time)), 0):
        vertices_near += 4
    if vertices_near:
        print "WARNING: unhandled vertex crash", vertices_near
        if vertices_near == 1:
            raise NotImplementedError()
        elif vertices_near == 2:
            x0, y0 = obj.next.origin.point_at(time) 
            x1, y1 = obj.next.next.origin.point_at(time)
            diagonal = obj.next
        elif vertices_near == 4:
            x0, y0 = obj.next.next.origin.point_at(time) 
            x1, y1 = obj.origin.point_at(time)
            diagonal = obj.next.next
        print "crash at", (x0+x1)*0.5, (y0+y1)*0.5
    
        print "to delete"
        print diagonal.origin.point_at(time), diagonal
        print diagonal.sibling.origin.point_at(time), diagonal.sibling
    
        pivot = diagonal.sibling.origin
        
        # remove the triangles from pq
        print pq.discard(triangle(diagonal))
        print pq.discard(triangle(diagonal.sibling))
        print pq.discard(triangle(diagonal.next.next.sibling))
        
        tri.remove_he(diagonal.next.next)
        tri.remove_he(diagonal.sibling.next)
        tri.remove_he(diagonal)
         
        pivot.x = (x0+x1) * 0.5
        pivot.y = (y0+y1) * 0.5
        pivot.velocity = (0,0)
        pivot.start = time
    
    print pivot.x, pivot.y
    
    to_add = [MovingVertex(pivot.x, pivot.y, 
                           (0.9999957061016943, -20.049871135434717)
                           )]
    for item in to_add:
        item.start = time
    
    for i, moving in enumerate(to_add):
        print "-" * 70
        check = moving.x + moving.velocity[0], moving.y + moving.velocity[1]
        length = dist(pivot.point_at(time), check)
        print "to check", pivot, pivot.he, "->", check, length
    #    assert not isinstance(vertex.he.origin, MovingVertex)  
    #    print vertex.he, vertex.he.sibling
        cur = pivot.he
        nxt = cur.next.next.sibling
        closeness_eps = 0.08 # distance within 5 degrees of original direction
        for _ in xrange(len(tri.half_edges)):
            print "testing"
            print cur, "--", cur.sibling
            print nxt, "--", nxt.sibling
            
            positive = orient2d(pivot.point_at(time), cur.sibling.origin, check)
            negative = orient2d(pivot.point_at(time), nxt.sibling.origin, check)
            if positive >= 0 and negative <= 0:
                print "found surrounding legs"
                # area = (base * altitude) * 0.5
                # 2 * area = (base * altitude)
                # 2 * area / base = altitude
                pdist = dist(pivot.point_at(time), cur.sibling.origin.point_at(time))
                paltitude = abs(positive) / pdist
                ndist = dist(pivot.point_at(time), nxt.sibling.origin.point_at(time))
                naltitude = abs(negative) / ndist
    #            print "cur leg", positive, paltitude, paltitude / length, pdist
    #            print "nxt leg", negative, naltitude, naltitude / length, ndist
                print "cur leg", paltitude / length,
                close = 0
                if paltitude / length < 0.1:
                    print "(*)close"
                    close += 1
                else:
                    print ""
                print "nxt leg", naltitude / length,
                if naltitude / length < 0.1:
                    print "(*)close"
                    close += 2
                else:
                    print ""
                print "***"
                
                if close & 1 or close & 2:
    #                tri.add_vertex24(cur, moving)
                    if close & 1:
                        tri.add_vertex24(cur, moving)
                        add_to_pq(cur, pq, time)
                        add_to_pq(cur.next.sibling, pq, time)
                        add_to_pq(cur.sibling, pq, time)
                        add_to_pq(cur.sibling.next.next.sibling, pq, time)
                    else:
                        # this seems to be correct...
                        tri.add_vertex24(nxt, moving)
                        add_to_pq(nxt, pq, time)
                        add_to_pq(nxt.next.sibling, pq, time)
                        add_to_pq(nxt.sibling, pq, time)
                        add_to_pq(nxt.sibling.next.next.sibling, pq, time)
                else:
                    tri.add_vertex13(cur, moving)
                    add_to_pq(cur, pq, time)
                    add_to_pq(cur.next.sibling, pq, time)
                    add_to_pq(cur.next.next.sibling, pq, time)
                print_pq()
                break
            print ""
            cur = nxt
            nxt = cur.next.next.sibling
    print "--" * 30
    print_pq()

print time
#time += 0.15
#time, obj = pq.popleft()
#time = 2.364
print "CURRENT TIME", time

fh = open("/tmp/tris_after.wkt", "w")
fh.write("#triangle\n")
vis = MeshVisualizer(tri)
vis.list_triangles_time(fh, time=time)
fh.close()

#print_pq()

# add every vertex again to triangulation
# which means, make a new vertex object
# make it a moving vertex and
# add it correctly in the combinatorial structure of the triangulation