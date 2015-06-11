from tri.delaunay import output_triangles, output_vertices, output_edges
from tri.delaunay import TriangleIterator, FiniteEdgeIterator
# ------------------------------------------------------------------------------
# output

def output_kdt(skel, time):
#     time = 0
    with open("/tmp/ktris.wkt", "w") as fh:
        fh.write("id;wkt;n0;n1;n2;v0;v1;v2\n")
        for t in skel.triangles:
            if not t.finite:
                continue
            valid = all([(v.starts_at <= time and v.stops_at >= time) or v.stops_at is None for v in t.vertices])
#         if v.stops_at is not None:
            if valid:
                L = []
                for v in t.vertices:
                    L.append("{0[0]} {0[1]}".format(v.position_at(time)))
                L.append(L[0])
                poly = "POLYGON(({0}))" .format(", ".join(L))
                if t is None:
                    continue
                fh.write("{0};{1};{2[0]};{2[1]};{2[2]};{3[0]};{3[1]};{3[2]}\n".format(id(t), poly, [id(n) for n in t.neighbours], [id(v) for v in t.vertices]))
            #fh.write("{0};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.position_at(t), id(v.left), id(v.right)))


    with open("/tmp/kvertices.wkt", "w") as fh:
        fh.write("id;wkt;left cw;right ccw\n")
        for v in skel.vertices:
#         if v.stops_at is not None:
            if (v.starts_at <= time and v.stops_at >= time) or v.stops_at is None:
                fh.write("{0};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.position_at(time), id(v.left), id(v.right)))

def output_kvertices(V, fh):
    """Output list of vertices as WKT to text file (for QGIS)"""
    fh.write("id;wkt;left cw;right ccw\n")
    for v in V:
#         if v.stops_at is not None:
            fh.write("{0};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.position_at(2.3), id(v.left), id(v.right)))

def output_dt(dt):
    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    with open("/tmp/segments.wkt", "w") as fh:
        output_edges([e for e in FiniteEdgeIterator(dt, True)], fh)

def output_offsets(skel):
    with open("/tmp/offsetsl.wkt", "w") as fh:
        fh.write("wkt\n")
        for t in range(0, 100):
            t *= .2
            for v in skel.vertices:
                if v.starts_at <= t and v.stops_at > t: # finite ranges only (not None is filtered out)
                    try:
                        s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.position_at(t), 
                                                                              v.left_at(t).position_at(t))
                        fh.write(s)
                        fh.write("\n")
                    except AttributeError:
                        print "FIXME: investigate"

    with open("/tmp/offsetsr.wkt", "w") as fh:
        fh.write("wkt\n")
        for t in range(0, 100):
            t *= .2
            for v in skel.vertices:
                if v.starts_at <= t and v.stops_at > t: # finite ranges only (not None is filtered out)
                    try:
                        s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.position_at(t), 
                                                                              v.right_at(t).position_at(t))
                        fh.write(s)
                        fh.write("\n")
                    except AttributeError:
                        print "FIXME: investigate"


def output_skel(skel):
    with open("/tmp/skel.wkt", "w") as fh:
        fh.write("wkt\n")
        for v in skel.vertices:
            if v.stops_at is not None:
                s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.position_at(v.starts_at), 
                                                                      v.position_at(v.stops_at))
                fh.write(s)
                fh.write("\n")

