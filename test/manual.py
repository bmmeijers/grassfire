"""Manual tests, check output manually in QGIS
"""

from grassfire import ToPointsAndSegments, calc_skel

def test_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (10, 0), (11, -1), (12,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    # FIXME: works but wrong:
    # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    calc_skel(conv)

def test_cocircular():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0,1), (1,0), (2,0), (3,1), (3,2), (2,3), (1,3), (0,2), (0,1)]])
    # FIXME: works but wrong:
    # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    calc_skel(conv)


def test_cocircular1():
    # FIXME: Point 
    ok = (3.8,0.8) # this works
    fail = (4,1) # substitute with this and we get a lot of simultaneous events!
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0,1), (1,0), (3,0), ok, (4,3), (3,4), (1,4), (0,3), (0,1)]])
    # FIXME: works but wrong:
    # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    calc_skel(conv)

def test_diamant():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(-1,0), (0,-1), (1,0), (0,5), (-1,0)]])
    # FIXME: works but wrong:
    # conv.add_polygon([[(0, 0), (9, 0), (11, -.1), (11.1,0), (22,0), (14,10), (2,8), (0, 5), (0,0)]])
    calc_skel(conv)

def test_diamantlike():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(-15,0), (-1,0), (0,-1), (1,0), (15,0), (0,15), (-15,0)]])
    calc_skel(conv)

def test_parallellogram():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(-15,0), (0,0), (15,25), (0, 25), (-15,0)]])
    calc_skel(conv)

def test_simple_poly():
    conv = ToPointsAndSegments()
    conv.add_polygon([[(0, 0), (22,0), (14,10), (2,8), (0, 6.5), (0,0)]])
    calc_skel(conv)

def test_single_line():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_segment((0, 0), (10,0))
    calc_skel(conv)

def test_three_lines():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    conv.add_point((10, 0))
    conv.add_point((-2, 8))
    conv.add_point((-2, -8))
    conv.add_segment((0, 0), (10,0))
    conv.add_segment((0, 0), (-2,8))
    conv.add_segment((0, 0), (-2,-8))
    calc_skel(conv)

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

    calc_skel(conv)


def test_single_point():
    conv = ToPointsAndSegments()
    conv.add_point((0, 0))
    calc_skel(conv)


def test_triangle():
    conv = ToPointsAndSegments()
    conv.add_point((10,0))
    conv.add_point((-2,8))
    conv.add_point((-2,-8))
    conv.add_segment((10,0), (-2,8))
    conv.add_segment((-2,8), (-2,-8))
    conv.add_segment((-2,-8), (10,0))
    calc_skel(conv)


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

    calc_skel(conv)

def test_two_lines_par():
    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,1))
    conv.add_point((22,1))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,1), (22,1))

    calc_skel(conv)

def test_polyline():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,-1))
    conv.add_point((22,1))
    conv.add_point((30,-5))

    conv.add_segment((0,0), (10,-1))
    conv.add_segment((10,-1), (22,1))
    conv.add_segment((22,1), (30,-5))

    calc_skel(conv)

def test_1_segment():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
#     conv.add_point((22,0))
#     conv.add_point((30,0))

    conv.add_segment((0,0), (10,0))
#     conv.add_segment((22,0), (30,0))

    calc_skel(conv)

def test_2_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((22,0))
    conv.add_point((30,0))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((22,0), (30,0))

    calc_skel(conv)


def test_2_perp_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,2))
    conv.add_point((12,10))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,2), (12,10))

    calc_skel(conv)

def test_45_deg_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((10,0))
    conv.add_point((12,2))
    conv.add_point((14,4))

    conv.add_segment((0,0), (10,0))
    conv.add_segment((12,2), (14,4))

    calc_skel(conv)

def test_30_deg_segments():

    conv = ToPointsAndSegments()

    conv.add_point((0,5))
    conv.add_point((9,0.5))
    conv.add_point((12,2))
    conv.add_point((14,4))

    conv.add_segment((0,5), (9,0.5))
    conv.add_segment((12,2), (14,4))

    calc_skel(conv)


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

    calc_skel(conv)

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

    calc_skel(conv)

def test_parallel_movement():

    conv = ToPointsAndSegments()

    conv.add_point((0,0))
    conv.add_point((1,0))
    conv.add_point((2,0))
    conv.add_point((3,0))

    conv.add_segment((0,0), (1,0))
    conv.add_segment((1,0), (2,0))
    conv.add_segment((2,0), (3,0))

    calc_skel(conv)


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

    calc_skel(conv)


def test_2triangle():
    from math import sqrt
    conv = ToPointsAndSegments()
    polygon = [[(1,0), 
                #(-5, 0), (-4.25, -6.65),# (-1,-0.9),
                (1, -10), (11,-10), 
                #(11,0), 
                (11, 10), (1,10), (1,2), (1-(sqrt(3)),1), (1,0)]]
    conv.add_polygon(polygon)
    calc_skel(conv)


def test_2triangle_eq_sides():
    from math import sqrt
    conv = ToPointsAndSegments()
    polygon = [[(1,0), 
                (-5, 0), (-4.25, -6.65),# (-1,-0.9),
                (1, -10), (11,-10), 
                #(11,0), 
                (11, 10), (1,10), (1,2), (1-(sqrt(3)),1), (1,0)]]
    conv.add_polygon(polygon)
    calc_skel(conv)

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
    close = (5, 4)
    conv.add_point(close)
    conv.add_point((0, 20))
    #conv.add_segment((8,2), (14,10))
    conv.add_segment((0,0), (10,0))
    conv.add_segment((10,0), (10,20))
    conv.add_segment((10,20), close)
    conv.add_segment(close, (0,20))
    #conv.add_segment((-2,-8), (8,2))
    conv.add_segment((0,20), (0,0))

    calc_skel(conv)

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
    from calc import bisector
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
    p1, p2, p3 = (-9.171572875253812, 2.4142135623730936), (0.0, 2.414213562373094), (9.171572875253812, 2.4142135623730936)
    print bisector(p1, p2, p3)
    print bisector(p3, p2, p1)

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

def helper_make_test_collapse_time():
    from math import sqrt
    from tri import triangulate, ToPointsAndSegments
    from grassfire import init_skeleton
#     conv = ToPointsAndSegments()
#     polygon = [[(1,0), 
#                 (-5, 0), (-4.25, -6.65),# (-1,-0.9),
#                 (1, -10), (11,-10), 
#                 #(11,0), 
#                 (11, 10), (1,10), (1,2), (1-(sqrt(3)),1), (1,0)]]
#     from simplegeom.wkt import loads
#     p = """
#     POLYGON((-2.28464419475655456 -0.62568847763824631,-1.01123595505618002 0.05287508261731655,0.54857898215465939 0.05287508261731655,1.50914298303591066 -0.63450099140779903,1.27561136814276255 0.76228244106631404,0.46045384445913173 1.20731438642872879,-0.69839171623705676 1.20731438642872879,-1.72945582727473024 0.77109495483586699,-2.28464419475655456 -0.62568847763824631))\
#     """
#     polygon = loads(p)
#     conv.add_polygon(polygon)
    conv = ToPointsAndSegments()
    conv.add_point((10,0))
    conv.add_point((-2,8))
    conv.add_point((-2,-8))
    conv.add_segment((10,0), (-2,8))
    conv.add_segment((-2,8), (-2,-8))
    conv.add_segment((-2,-8), (10,0))
    dt = triangulate(conv.points, None, conv.segments)
    skel = init_skeleton(dt)
    print "triangles = {}"
    for t in skel.triangles:
#         if t.finite:
        print "###", id(t)
        print "k = KineticTriangle()"
        print "V = []"
        for v in t.vertices:
            print "v = KineticVertex()"
            print "v.origin =", v.origin
            print "v.velocity =", v.velocity
            print "V.append(v)"
        print "k.vertices = V"
        print "triangles[",id(t),"] = k"
    print ""
    print "### neighbour relationships"
    for t in skel.triangles:
        print "n =", ", ".join(["triangles[{0}]".format(id(n)) if n is not None else "None" for n in t.neighbours])
        print "triangles[",id(t),"].neighbours = list(n)"

if __name__ == "__main__":
#     test_replace_kvertex()
#     helper_make_test_collapse_time()
# working tests
# -------------

#     test_split() 
#     test_simple_poly()
#     test_quad()
#     test_triangle()
#     try:
#         test_single_point()
#     except:
#         pass

# nearly working tests
# -------------
#     test_diamant() # RESULTS IN 5 lines, while this should be 4!!!


    test_cocircular1()
# not working
#     test_poly()

# unknown
# -------
#     test_diamantlike()

#     test_parallellogram() # Infinite speed problem

#     test_collinear_bisectors()
#     helper_make_test_collapse_time()
#     test_2triangle()
#     test_2triangle_eq_sides()
#     output_ktri()
# remainder
# -------------
#     test_crash_vertex()
#     test_ordering()
#     test_collinear_bisectors()
#     test_left_right_for_vertex()
#     test_flip()
#     test_1_segment()

#### LINES
#     test_single_line()
#     test_three_lines()
#     test_arrow_four_lines()
#     test_parallel_movement()
#     test_two_lines_par()
#     test_polyline()
#     test_2_segments()
#     test_2_perp_segments()
#     test_45_deg_segments()
#     test_30_deg_segments()
#     test_4_segments()
#     test_cocircular_segments()
####

#     test4_3_3()
#     test_compute_0()
#     test_compute_1()
#     test_compute_2()
#     test_compute_3()