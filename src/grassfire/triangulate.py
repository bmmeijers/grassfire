'''
Created on Oct 16, 2012

@author: martijn
'''

from triangulation.mesh import Mesh, Vertex, MovingVertex
from triangulation.utils import MeshVisualizer
from angles import bisector_vectors
from predicates import orient2d
from math import hypot

def dist(pa, pb):
    dx = pa[0] - pb[0]
    dy = pa[1] - pb[1]
    return hypot(dx, dy)

ring = [(0,0), (9,0), (9,10), 
        (5,10), (4.5, 5), (4,10),
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
                                    vertex[0]+speed[0]*S, vertex[1]+speed[1]*S)
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

print first_collapse, first_collapse.he, first_collapse.he.sibling
tri.flip22_event(first_collapse.he.next.next.sibling.next) # diagonal
print first_collapse, first_collapse.he, first_collapse.he.sibling
tri.flip22_event(first_collapse.he.next.next.sibling.next)
fh = open("/tmp/tris_after.wkt", "w")
fh.write("#triangle\n")
vis = MeshVisualizer(tri)
vis.list_triangles_time(fh, time=0.48)
fh.close()

# add every vertex again to triangulation
# which means, make a new vertex object
# make it a moving vertex and
# add it correctly in the combinatorial structure of the triangulation