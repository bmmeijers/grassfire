from tri import ToPointsAndSegments, triangulate

from io import output_dt
from initialize import init_skeleton
from events import init_event_list, event_loop

# ------------------------------------------------------------------------------
# test cases
def test_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (10, 0), (11, -1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    dt = triangulate(conv.points, None, conv.segments)
    output_dt(dt)
    skel = init_skeleton(dt)
    el = init_event_list(skel)
    event_loop(el, skel)

def test_simple_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (22,0), (14,10), (2,8), (0, 6.5), (0,0)]])
    dt = triangulate(conv.points, None, conv.segments)
    output_dt(dt)
    skel = init_skeleton(dt)
    el = init_event_list(skel)
    event_loop(el, skel)

def test_single_line():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_segment((0, 0), (10,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

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

    output_dt(dt)

    init_skeleton(dt)


def test_arrow_four_lines():
    conv = ToPointsAndSegments()

    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_point((12,0.5))
    conv.add_point((8,5))
    conv.add_point((8,-5))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((8,5), (12,0.5))
    conv.add_segment((12,0.5), (8,-5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_single_point():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    dt = triangulate(conv.points, None, conv.segments)
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
    output_dt(dt)
    skel = init_skeleton(dt)
    el = init_event_list(skel)
    event_loop(el, skel)

    print skel.sk_nodes
    for node in skel.sk_nodes:
        print "POINT({0[0]} {0[1]})".format(node.pos)
    print skel.vertices
    for v in skel.vertices:
        print v.starts_at, v.stops_at

    output_offsets(skel)
    output_skel(skel)


def test_quad():
    conv = ToPointsAndSegments()
    #conv.add_point((8,2))
    conv.add_point((4,5))
    conv.add_point((-2,8))
    conv.add_point((-2,-8))
    conv.add_point((14,10))
    #conv.add_segment((8,2), (14,10))
    conv.add_segment((14,10), (-2,8))
    conv.add_segment((-2,8), (-2,-8))
    #conv.add_segment((-2,-8), (8,2))
    conv.add_segment((4,5), (14,10))
    conv.add_segment((-2,-8), (4,5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)
    skel = init_skeleton(dt)
    el = init_event_list(skel)
    event_loop(el, skel)

    print skel.sk_nodes
    for node in skel.sk_nodes:
        print "POINT({0[0]} {0[1]})".format(node.pos)
    print skel.vertices
    for v in skel.vertices:
        print v.starts_at, v.stops_at

    # FIXME: offsetting does not work like this for now ->
    # kinetic vertices get new neighbours, making the left / right
    # references in the circulair list invalid, i.e. they are time dependent
    # but no historical records are kept!
    output_offsets(skel)

    # Output the skeleton edges
    output_skel(skel)
    for v in skel.vertices:
        print "", id(v)
        for start, stop, kv in v._left:
            print "  left  ", start, stop, id(kv)
        for start, stop, kv in v._right:
            print "  right ", start, stop, id(kv)

def test_two_lines_par():
    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,1))
    conv.add_point((22,1))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,1), (22,1))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_polyline():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,-1))
    conv.add_point((22,1))
    conv.add_point((30,-5))

    conv.add_segment((0,0), (10,-1))
    conv.add_segment((10,-1), (22,1))
    conv.add_segment((22,1), (30,-5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_1_segment():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
#     conv.add_point((22,0))
#     conv.add_point((30,0))

    conv.add_segment((0,0), (10,0))
#     conv.add_segment((22,0), (30,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_2_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((22,0))
    conv.add_point((30,0))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((22,0), (30,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_2_perp_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,2))
    conv.add_point((12,10))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,2), (12,10))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_45_deg_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,2))
    conv.add_point((14,4))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,2), (14,4))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_30_deg_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,5))
    conv.add_point((9,0.5))
    conv.add_point((12,2))
    conv.add_point((14,4))

    conv.add_segment((0,5), (9,0.5))
    conv.add_segment((12,2), (14,4))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_4_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((22,0))
    conv.add_point((30,0))

    conv.add_point((16,-3))
    conv.add_point((16,-6))

    conv.add_point((16,2))
    conv.add_point((16,6))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((22,0), (30,0))
    conv.add_segment((16,-3), (16,-6))
    conv.add_segment((16,2), (16,6))

    conv.add_segment((0,0), (16,-6))
    conv.add_segment((16,-6), (30,0))
    conv.add_segment((30,0), (16,6))
    conv.add_segment((16,6), (0,0))


    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_cocircular_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,1))

    conv.add_point((3,0))
    conv.add_point((2,1))

    conv.add_point((0,3))
    conv.add_point((1,2))

    conv.add_point((3,3))
    conv.add_point((2,2))

    conv.add_segment((0,0), (1,1))
    conv.add_segment((3,0), (2,1))
    conv.add_segment((0,3), (1,2))
    conv.add_segment((3,3), (2,2))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)

def test_parallel_movement():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,0))
    conv.add_point((2,0))
    conv.add_point((3,0))

    conv.add_segment((0,0), (1,0))
    conv.add_segment((1,0), (2,0))
    conv.add_segment((2,0), (3,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test_crash_vertex():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,0))


    conv.add_point((0,2))
    conv.add_point((0.5,1.5))
    conv.add_point((1,2))

    conv.add_segment((0,0), (1,0))
    conv.add_segment((0,2), (0.5,1.5))
    conv.add_segment((1,2), (0.5,1.5))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)

    init_skeleton(dt)


def test4_3_3():
    # make this a function
    # crash_time(tri)
    tri = KineticTriangle()

    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (-sqrt(2),sqrt(2))

    b = KineticVertex()
    b.origin = (1,0)
    b.velocity = (sqrt(2),sqrt(2))

    c = KineticVertex()
    c.origin = (0.5, 1.5)
    c.velocity = (0,-1)

    tri.vertices = [a, b, c]
    # a -> b constrained

    # FIXME: would this work with triangle at terminal vertex ?
    # the problem could be that there is no support line for the 'constrained' 
    # edge

    print tri
    Mv = tuple(map(sub, c.origin, a.origin))
    print Mv

    m =  map(sub, b.origin, a.origin)
    m = norm(m)
    print m
    # normalize m!
    n = perp(m)
    print n
    distance_v_e = dot(Mv, n)
    print "dist", distance_v_e
    s = c.velocity
    # different from section 4.3.3: we need to negate n, so that we obtain s' 
#     neg_n = tuple([-i for i in n])
    crash_time = distance_v_e / (1 - dot(s, n))
    print "time vertex crashes on edge:", crash_time 
    coeff = area_collapse_time_coeff(a, b, c)
    print solve_quadratic(coeff[0], coeff[1], coeff[2])
    import matplotlib.pyplot as plt
    print "roots", numpy.roots(coeff)
    x = range(-40, 100)
    y = [quadratic(y, coeff[0], coeff[1], coeff[2]) for y in x]
    plt.plot(x,y)
    plt.show()

    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_0():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (2,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (1, 3)
    c.velocity = (0,-1)
    tri.neighbours = [True, True, True] # make them not None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_1():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (2,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (1, 3)
    c.velocity = (0,-1)
    tri.neighbours = [True, True, None] # make them not None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_2():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (2,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (1, 3)
    c.velocity = (0,-1)
    tri.neighbours = [None, True, None] # make them None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)

def test_compute_3():
    tri = KineticTriangle()
    a = KineticVertex()
    a.origin = (0,0)
    a.velocity = (sqrt(2),sqrt(2))
    b = KineticVertex()
    b.origin = (1,0)
    b.velocity = (-sqrt(2),sqrt(2))
    c = KineticVertex()
    c.origin = (0.5, 1)
    c.velocity = (0,-1)
    tri.neighbours = [None, None, None] # make them None for the test
    tri.vertices = [a, b, c]
    print compute_collapse_time(tri)
    with open("/tmp/ktris.wkt", "w") as fh:
        output_triangles([tri], fh)


def test_flip():
    """Flip 2 triangles
    """
    # the 2 to be flipped
    tri0 = KineticTriangle()
    tri1 = KineticTriangle()

    # surrounding neighbours
    tri2 = KineticTriangle()
    tri2.vertices = [None, "a", "c"]
    tri3 = KineticTriangle()
    tri3.vertices = [None, "b", "a"]
    tri4 = KineticTriangle()
    tri4.vertices = [None, "d", "b"]
    tri5 = KineticTriangle()
    tri5.vertices = [None, "c", "d"]

    tri2.neighbours[0] = tri0
    tri3.neighbours[0] = tri0
    tri4.neighbours[0] = tri1
    tri5.neighbours[0] = tri1

    tri0.vertices = ["a","b","c"]
    tri1.vertices = ["c","b","d"]

    tri0.neighbours = [tri1, tri2, tri3]
    tri1.neighbours = [tri4, tri5, tri0]

    assert tri1 in tri0.neighbours
    assert tri2 in tri0.neighbours
    assert tri3 in tri0.neighbours

    flip(tri0, 0, tri1, 2)

    assert tri0 in tri1.neighbours
    assert tri2 in tri1.neighbours
    assert tri5 in tri1.neighbours

    assert tri1 in tri0.neighbours
    assert tri3 in tri0.neighbours
    assert tri4 in tri0.neighbours

    assert "a" in tri0.vertices
    assert "b" in tri0.vertices
    assert "d" in tri0.vertices

    assert "a" in tri1.vertices
    assert "c" in tri1.vertices
    assert "d" in tri1.vertices



def test_split():
    conv = ToPointsAndSegments()
    #conv.add_point((8,2))
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_point((10, 20))
    close = (5,4)
    conv.add_point(close)
    conv.add_point((0, 20))
    #conv.add_segment((8,2), (14,10))
    conv.add_segment((0,0), (10,0))
    conv.add_segment((10,0), (10,20))
    conv.add_segment((10,20), close)
    conv.add_segment(close, (0,20))
    #conv.add_segment((-2,-8), (8,2))
    conv.add_segment((0,20), (0,0))

    dt = triangulate(conv.points, None, conv.segments)

    output_dt(dt)
    skel = init_skeleton(dt)
    el = init_event_list(skel)
    event_loop(el, skel)

    print skel.sk_nodes
    for node in skel.sk_nodes:
        print "POINT({0[0]} {0[1]})".format(node.pos)
    print skel.vertices
    for v in skel.vertices:
        print v.starts_at, v.stops_at

    # FIXME: offsetting does not work like this for now ->
    # kinetic vertices get new neighbours, making the left / right
    # references in the circulair list invalid, i.e. they are time dependent
    # but no historical records are kept!
    output_offsets(skel)
    output_skel(skel)

def test_left_right_for_vertex():
    kva = KineticVertex()
    kvb = KineticVertex()
    kvc = KineticVertex()
    kvb_ = KineticVertex()
    kvc_ = KineticVertex()

    kva.left = kvb, 0
    kva.right = kvc, 0
    print kva._left
    print kva._right

    kva.left = kvb_, 10
    kva.right = kvc_, 10
    print kva._left
    print kva._right

    assert kva.left_at(5) is kvb
    assert kva.left_at(15) is kvb_

    kva.left_at(-1)

def test_collinear_bisectors():
    a = (10,0)
    b = (0,0)
    c = (10.,0)
    d = (-10, 0)
    bi = bisector(a, b, c)
    print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(b, bi)
    bi = bisector(c, b, a)
    print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(b, bi)
    bi = bisector(d, b, a)
    print bi
    bi = bisector(a, b, d)
    print bi

def test_ordering():
    tri1 = ("1", )
    tri2 = ("2", )
    tri3 = ("3", )
    ea = Event(when = 1, tri = tri1)
    eb = Event(when = 1, tri = tri2)
    ec = Event(when = 2, tri = tri3)
    L = [ec, eb, ea]
    #for e in L:
    #    print e
    #print "--"
    #L.sort(cmp=compare_event_by_time)
    #for e in L:
    #    print e
    #print ""
    queue = OrderedSequence(cmp=compare_event_by_time)
    for e in L: queue.add(e)
    queue.remove(ec)
    queue.remove(Event(when=1, tri=tri1))
    while queue:
        e = queue.popleft()
        assert e.triangle is tri2
    assert len(queue) == 0

if __name__ == "__main__":
#     test_ordering()
#     test_collinear_bisectors()
#     test_left_right_for_vertex()
#     test_flip()
#     try:
#         test_single_point()
#     except:
#         pass
#     test_poly()
    test_simple_poly()
#     test_1_segment()
#     test_single_line()
#     test_three_lines()
#     test_arrow_four_lines()
#     test_triangle()
#     test_parallel_movement()
#     test_quad()
#     test_split()
#     test_two_lines_par()
#     test_polyline()
#     test_2_segments()
#     test_2_perp_segments()
#     test_45_deg_segments()
#     test_30_deg_segments()
#     test_4_segments()
#     test_cocircular_segments()
#     test_crash_vertex()
#     test4_3_3()
#     test_compute_0()
#     test_compute_1()
#     test_compute_2()
#     test_compute_3()