from tri.delaunay import output_triangles, output_vertices, output_edges, Edge
from tri.delaunay import TriangleIterator, FiniteEdgeIterator
import logging

from grassfire.vectorops import mul, dist, bisector, add
# ------------------------------------------------------------------------------
# output

def output_edges_at_T(edges, T, fh):
    fh.write("id;side;wkt\n")
    for e in edges:
        segment = e.segment
        s = segment[0].position_at(T), segment[1].position_at(T)
        fh.write("{0};{1};LINESTRING({2[0][0]} {2[0][1]}, {2[1][0]} {2[1][1]})\n".format(id(e.triangle), e.side, s))

def output_triangles_at_T(tri, T, fh):
    """Output list of triangles as WKT to text file (for QGIS)"""
    fh.write("id;time;wkt;n0;n1;n2;v0;v1;v2;finite;info\n")
    for t in tri:
        if t is None:
            continue
        if t.stops_at == None:
            fh.write("{0};{6};{1};{2[0]};{2[1]};{2[2]};{3[0]};{3[1]};{3[2]};{4};{5}\n".format(id(t), t.str_at(T), [id(n) for n in t.neighbours], [id(v) for v in t.vertices], t.is_finite, t.info, T))
        else:
            # we skip the triangle if it has a timestamp associated
            pass

def output_kdt(skel, time):
    """ """
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

def output_vertices_at_T(V, T, fh):
    """Output list of vertices as WKT to text file (for QGIS)"""
    fh.write("id;wkt;left cw;right ccw\n")
    for v in V:
#         if v.stops_at is not None:
        fh.write("{0};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.position_at(T), id(v.left), id(v.right)))

def output_dt(dt):
    """ """
    with open("/tmp/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmp/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    with open("/tmp/segments.wkt", "w") as fh:
        output_edges([e for e in FiniteEdgeIterator(dt, True)], fh)

def output_offsets(skel, now=1000):
    """ """
    logging.debug("offsets for t= {}".format(now))
    now = 10
    ct = 100
    inc = 0.05 # now / float(ct)
    #times = [0.0276]#[0.075] #[0.0375] #[0.15] #[0.075] #
    times = [t*inc for t in range(ct)]
    with open("/tmp/offsetsl.wkt", "w") as fh:
        fh.write("wkt;time;from;to\n")
        for t in times:
            for v in skel.vertices:
                if (v.starts_at <= t and v.stops_at > t) or \
                    (v.starts_at <= t and v.stops_at is None): 
                    try:
                        s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{4}".format(v.position_at(t), 
                                                                              v.left_at(t).position_at(t),
                                                                              t,
                                                                              id(v), id(v.left_at(t)))
                        fh.write(s)
                        fh.write("\n")
                    except AttributeError:
                        #print "*"
                        pass

    with open("/tmp/offsetsr.wkt", "w") as fh:
        fh.write("wkt;time;from;to\n")
        for t in times:
            for v in skel.vertices:
                if v.starts_at <= t and v.stops_at > t or \
                    (v.starts_at <= t and v.stops_at is None):
                # finite ranges only (not None is filtered out)
                    try:
                        s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{4}".format(v.position_at(t), 
                                                                              v.right_at(t).position_at(t),
                                                                              t,
                                                                              id(v), id(v.right_at(t)))
                        fh.write(s)
                        fh.write("\n")
                    except AttributeError:
                        #print "FIXME: investigate"
                        pass


def output_skel(skel):
    """ """
    with open("/tmp/skel.wkt", "w") as fh:
        fh.write("wkt\n")
        for v in skel.vertices:
            if v.stops_at is not None:
                s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.start_node.pos,
                                                                      v.stop_node.pos
                                                                      #v.position_at(v.starts_at), 
                                                                      #v.position_at(v.stops_at)
                                                                      )
                fh.write(s)
                fh.write("\n")
            else:
                s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.position_at(v.starts_at), 
                                                                      v.position_at(5))
                fh.write(s)
                fh.write("\n")

    with open("/tmp/skelnodes.wkt", "w") as fh:
        fh.write("wkt\n")
        for n in skel.sk_nodes:
            fh.write("POINT({0[0]} {0[1]})\n".format(n.pos))



def visualize(queue, skel, NOW):
    """ Visualize progress by writing geometry to WKT files to be viewed with
    QGIS """
    with open('/tmp/queue.wkt', 'w') as fh:
        fh.write("pos;wkt;evttype;evttime;tritype;id;n0;n1;n2;finite\n")
        for i, evt in enumerate(queue):
            fh.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}\n".format(
                i,
                evt.triangle.str_at(NOW),
                evt.tp,
                evt.time,
                evt.triangle.type,
                id(evt.triangle),
                id(evt.triangle.neighbours[0]),
                id(evt.triangle.neighbours[1]),
                id(evt.triangle.neighbours[2]),
                evt.triangle.is_finite,
            )
            )

    with open('/tmp/ktri_progress.wkt', 'w') as fh:
        output_triangles_at_T(skel.triangles, NOW, fh)

    with open("/tmp/sknodes_progress.wkt", 'w') as fh:
        fh.write("wkt\n")
        for node in skel.sk_nodes:
            fh.write("POINT({0[0]} {0[1]})\n".format(node.pos))

    with open("/tmp/bisectors_progress.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt\n")
        for kvertex in skel.vertices:
            if kvertex.stops_at is None:
                p1 = kvertex.position_at(NOW)
                bi = kvertex.velocity
                bisector_fh.write(
                    "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(
                        p1, add(p1,
                                mul(bi, 0.1)
                                )))
    with open("/tmp/segments_progress.wkt", "w") as fh:
        fh.write("wkt;finished;length\n")
        for kvertex in skel.vertices:
            if kvertex.start_node is not None and kvertex.stop_node is not None:
                start, end = kvertex.start_node.pos, kvertex.stop_node.pos
                fh.write(
                    "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3}\n".format(
                        start,
                        end,
                        True,
                        dist(
                            start,
                            end)))
            elif kvertex.start_node is not None and kvertex.stop_node is None:
                start, end = kvertex.start_node.pos, kvertex.position_at(NOW)
                fh.write(
                    "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3}\n".format(
                        start,
                        end,
                        False,
                        dist(
                            start,
                            end)))

    with open("/tmp/vertices1_progress.wkt", 'w') as fh1:
        fh1.write("id;wkt;leftid;rightid\n")
        for kvertex in skel.vertices:
            #             if kvertex.start_node is not None and kvertex.stop_node is not None:
            #                 fh0.write("{1};POINT({0[0]} {0[1]})\n".format(kvertex.position_at(kvertex.starts_at), id(kvertex)))
            #             else:
            left = kvertex.left_at(NOW)
            right = kvertex.right_at(NOW)
            if left is None:
                left_id = ""
            else:
                left_id = id(left)
            if right is None:
                right_id = ""
            else:
                right_id = id(right)
            if kvertex.stop_node is None:
                fh1.write(
                    "{1};POINT({0[0]} {0[1]});{2};{3}\n".format(
                        kvertex.position_at(NOW),
                        id(kvertex),
                        left_id,
                        right_id))

    with open("/tmp/wavefront_edges_progress.wkt", "w") as fh:
        edges = []
        for tri in skel.triangles:
            if tri.stops_at is None:
                sides = []
                for i, ngb in enumerate(tri.neighbours):
                    if ngb is None:
                        sides.append(i)
                for side in sides:
                    edges.append(Edge(tri, side))
        output_edges_at_T(edges, NOW, fh)
