from angles import bisector_vectors
from eventtime import collapse_time, Track, position
from epsilon import near
from math import hypot
from pprint import pprint

#ring = [(0,0), (8,0), (6,3), (2,2), (0,0)]
#triangles = [(0,2,3), (2,0,1)]

#ring = [(0, 0), (4, 0), (4, 7), (2, 7), (2, 3), (0, 3), (0, 0)] # convex

# First event is edge event (node collapses)
#ring = [(0, 0), (4, 0), (4, 7), (2, 7), (0, 3), (0, 0)]
#triangles = [(5,0,4), (4,0,1), (4,1,2), (4,2,3), (5,4,3)]

#ring = [(0,0), (10,0), (10,2), (0,2), (0,0)]
#triangles = [(0, 1, 3), (1, 2, 3)]

#ring = ((0,0), (10,0), (5,8), (0,0) )
#triangles = [(0,1,2)]

# First event is split event (edge is split)
        # 0    1       2        3       4        5       6   
#ring = [(0,0), (11,0), (11,10), (6,10), (5.5,1), (5,10), (0,10), (0,0)]
#triangles = [(0, 1, 4), (0, 4, 6), (4, 5, 6), (1,2,4), (4,2,3)]

ring = [(0,0), (9,0), (9,10), (5,10), (4.5, 5), (4,10), (0,10), (0,0)]
triangles = [(0,1,4)]

fh = open("/tmp/orig.wkt", "w")
fh.write("#x,y\n")
for S in ring:
    fh.write("{0}, {1}\n".format(S[0], S[1]))
fh.close()

#def dist(start, end):
#    dx = start[0] - end[0]
#    dy = start[1] - end[1]
#    return hypot(dx, dy)

def dist(start, end):
    """Returns squared distance
    """
    dx = start[0] - end[0]
    dy = start[1] - end[1]
    c = dx * dx    
    d = dy * dy
    return c + d

directions = bisector_vectors(ring)

#for idx, vec in bisector_vectors(ring).iteritems():
#    print idx, "->", ring[idx], "::", vec

# triangles = [(5,0,4), (0,1,4), (1,2,4), (2,3,4)]

def positive(value):
    if value >= 0:
        return True
    else:
        return False
    
fh = open("/tmp/traces.wkt", "w")
fh.write("#trace\n")
s = 0.5
for i in range(len(ring)-1):
    # get trace i
    pt = ring[i]
    v = directions[i]
    t = "LINESTRING({} {}, {} {})".format(pt[0], pt[1],
                                    pt[0]+v[0]*s, pt[1]+v[1]*s)
    fh.write(t+"\n")
fh.close()
times = []
for t, (a, b, c) in enumerate(triangles):
    a, b, c = sorted( (a, b, c) )
    print t, ":", a, b, c, "--", ring[a], ring[b], ring[c] 
    ta, tb, tc = Track(ring[a], directions[a]), \
                 Track(ring[b], directions[b]), \
                 Track(ring[c], directions[c])
    print "track a", ta
    print "track b", tb
    print "track c", tc
    C = collapse_time(ta, tb, tc)
    print "times", C, filter(positive, C)
    times.append((filter(positive, C), t))

times.sort()
print "times"
print "-" * 5
pprint(times)
print "-" * 5
at = times[0][0][0]

#stationary = (0, 0)
#print "degenerate"
#print collapse_time(Track((0,0), stationary),
#                    Track((10,0), stationary),
#                    Track((0,0), (1,1)))
#
#print collapse_time(Track((0,0), stationary),
#                    Track((10,0), (-1, 1)),
#                    Track((0,0), stationary))
print "t =", at, " collapsing triangle", times[0][1]

tris = open("/tmp/tris.wkt", "w")
fh = open("/tmp/wazaa.wkt", "w")
fh.write("#x,y\n")
tris.write("#triangle\n")
done = set()
#at = 2.5
#at = 0.4
for t, (a, b, c) in enumerate(triangles):
    print t, "::", a, b, c
    pts = []
    orig = []
    for i in (a, b, c,):
        S = position(Track(ring[i], directions[i]), at)
        if i not in done:
            fh.write("{0}, {1}\n".format(S[0], S[1]))
            done.add(i)
        pts.append(S)
        orig.append(ring[i])
    coords = ", ".join(["{} {}".format(pt[0], pt[1]) for pt in pts + [pts[0]]])
    tris.write("POLYGON(({}))\n".format(coords))
    for i, j, start_adj, end_adj, start, end in zip([a, b, c], [b, c, a], 
                                pts, pts[1:]+[pts[0]],
                                orig, orig[1:]+[orig[0]]):
        print i, "->", j,";", \
            start, "-", end, "->", \
            start_adj, "-", end_adj, "distance:", dist(start_adj, end_adj), near(dist(start_adj, end_adj), 0.)
            #"D:", dist(start, end), near(dist(start, end), 0.), \

tris.close()
fh.close()

# TODO:
# - use triangulation to start with
# - think of more robust way to deal with 'event types'
#   * edge event: distance between two vertices of the same triangle 
#     is about 0
#   * others -- how does that work anyway ???
