from tri.delaunay.inout import output_triangles, output_vertices, output_edges
from tri.delaunay.tds import Edge
from tri.delaunay.iter import TriangleIterator, FiniteEdgeIterator
import logging

from grassfire.vectorops import mul, dist, add, unit, norm

# ------------------------------------------------------------------------------
# output


def output_edges_at_T(edges, T, fh):
    fh.write("id;info;side;wkt\n")
    for e in edges:
        segment = e.segment
        s = segment[0].visualize_at(T), segment[1].visualize_at(T)
        fh.write("{0};{3};{1};LINESTRING({2[0][0]} {2[0][1]}, {2[1][0]} {2[1][1]})\n".format(id(e.triangle), e.side, s, e.triangle.info))


def output_triangles_at_T(tri, T, fh):
    """Output list of triangles as WKT to text file (for QGIS)"""
    fh.write("id;time;wkt;n0;n1;n2;v0;v1;v2;finite;info;wavefront_directions\n")
    for t in tri:
        if t is None:
            continue
        if t.stops_at is None:
            fh.write("{0};{6};{1};{2[0]};{2[1]};{2[2]};{3[0]};{3[1]};{3[2]};{4};{5};{7}\n".format(
                id(t),
                t.visualize_at(T),
                [(id(n), n.info if n is not None and n is not True else "") for n in t.neighbours],
                [(id(v), v.info if v is not None else "") for v in t.vertices],
                t.is_finite,
                t.info,
                t.event.time if t.event is not None else "-1",
                t.wavefront_directions))
        else:
            # we skip the triangle if it has a timestamp associated
            pass


def output_kdt(skel, time):
    """ """
#     time = 0
    with open("/tmpfast/ktris.wkt", "w") as fh:
        fh.write("id;wkt;n0;n1;n2;v0;v1;v2\n")
        for t in skel.triangles:
            if not t.finite:
                continue
            valid = all([(v.starts_at <= time and v.stops_at >= time) or v.stops_at is None for v in t.vertices])
#         if v.stops_at is not None:
            if valid:
                L = []
                for v in t.vertices:
                    L.append("{0[0]} {0[1]}".format(v.visualize_at(time)))
                L.append(L[0])
                poly = "POLYGON(({0}))" .format(", ".join(L))
                if t is None:
                    continue
                fh.write("{0};{1};{2[0]};{2[1]};{2[2]};{3[0]};{3[1]};{3[2]}\n".format(id(t), poly, [id(n) for n in t.neighbours], [id(v) for v in t.vertices]))
            #fh.write("{0};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.visualize_at(t), id(v.left), id(v.right)))
    with open("/tmpfast/kvertices.wkt", "w") as fh:
        fh.write("id;wkt;left cw;right ccw\n")
        for v in skel.vertices:
#         if v.stops_at is not None:
            if (v.starts_at <= time and v.stops_at >= time) or v.stops_at is None:
                fh.write("{0};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.visualize_at(time), id(v.left), id(v.right)))


def output_vertices_at_T(V, T, fh):
    """Output list of vertices as WKT to text file (for QGIS)"""
    fh.write("id;info;wkt;left cw;right ccw\n")
    for v in V:
#         if v.stops_at is not None:
        fh.write("{0};{4};POINT({1[0]} {1[1]});{2};{3}\n".format(id(v), v.visualize_at(T), id(v.left), id(v.right), v.info))


def output_dt(dt):
    """ """
    with open("/tmpfast/vertices.wkt", "w") as fh:
        output_vertices([v for v in dt.vertices], fh)

    it = TriangleIterator(dt)
    with open("/tmpfast/tris.wkt", "w") as fh:
        output_triangles([t for t in it], fh)

    with open("/tmpfast/segments.wkt", "w") as fh:
        output_edges([e for e in FiniteEdgeIterator(dt, True)], fh)


def output_offsets(skel, now=1000, ct=5):
    """ """
    logging.debug("offsets for t={}, ct={}".format(now, ct))
    # now = 10
    # inc = 0.005 # 
    inc = now / float(ct)
    #times = [0.0276]#[0.075] #[0.0375] #[0.15] #[0.075] #
    times = [t*inc for t in range(ct)]
    with open("/tmpfast/offsetsl.wkt", "w") as fh:
        fh.write("wkt;time;from;to\n")
        for t in times:
            for v in skel.vertices:
                if (v.starts_at <= t and v.stops_at > t) or \
                    (v.starts_at <= t and v.stops_at is None): 
                    try:
                        s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{4}".format(v.visualize_at(t), 
                                                                              v.left_at(t).visualize_at(t),
                                                                              t,
                                                                              id(v), id(v.left_at(t)))
                        fh.write(s)
                        fh.write("\n")
                    except AttributeError:
                        #print "*"
                        pass

    with open("/tmpfast/offsetsr.wkt", "w") as fh:
        fh.write("wkt;time;from;to\n")
        for t in times:
            for v in skel.vertices:
                if v.starts_at <= t and v.stops_at > t or \
                    (v.starts_at <= t and v.stops_at is None):
                # finite ranges only (not None is filtered out)
                    try:
                        s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{4}".format(v.visualize_at(t), 
                                                                              v.right_at(t).visualize_at(t),
                                                                              t,
                                                                              id(v), id(v.right_at(t)))
                        fh.write(s)
                        fh.write("\n")
                    except AttributeError:
                        #print "FIXME: investigate"
                        pass


def output_skel(skel, when):
    """ """
    with open("/tmpfast/skel.wkt", "w") as fh:
        fh.write("id;wkt;stopped;length\n")
        for v in skel.vertices:
            fh.write(str(id(v))+";")
            if v.stops_at is not None:
                s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.start_node.pos,
                                                                      v.stop_node.pos
                                                                      )
                fh.write(s)
                fh.write(";True;" + str(dist(v.start_node.pos, v.stop_node.pos)) + "\n")
            else:
                s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(v.visualize_at(v.starts_at), 
                                                                      v.visualize_at(when))
                fh.write(s)
                fh.write(";False;" + str(dist(v.visualize_at(v.starts_at), v.visualize_at(when))) + "\n")

    with open("/tmpfast/skelnodes.wkt", "w") as fh:
        fh.write("wkt\n")
        for n in skel.sk_nodes:
            fh.write("POINT({0[0]} {0[1]})\n".format(n.pos))




# ------------------------------------------------------------------------------
# debugging
_is_hook_qgis_shown = False
def notify_qgis():
    global _is_hook_qgis_shown
    import random
    import time
    import os
    file_nm = "/tmp/signal"
    with open(file_nm, "w") as fh:
        fh.write("{}".format(random.randint(0, 1000)))
    os.system("touch {}".format(file_nm))
    print('Notified QGIS via file: {}'.format(file_nm))
    
    time.sleep(0.01)
    if not _is_hook_qgis_shown:
        enter_in_qgis = """
from PyQt5.QtCore import QFileSystemWatcher
watcher = QFileSystemWatcher()
watcher.addPath('{}')

def onFileChanged():
    print("clearing cache and redrawing" )
    qgis.utils.iface.mapCanvas().setCachingEnabled(False)
    qgis.utils.iface.mapCanvas().resetCachedContent()
    qgis.utils.iface.mapCanvas().refresh()

watcher.fileChanged.connect(onFileChanged)
""".format(file_nm)
        print("To watch in QGIS, enter in the Python console:")
        print(enter_in_qgis)
        _is_hook_qgis_shown = True


def interactive_visualize(queue, skel, step, now):
    visualize(queue, skel, now)
    notify_qgis()
    user_input = raw_input(str(step) + ' {' + str(now) + '} > before event (now time); "r" to rewind, any other key to continue$ ')
    if user_input == 'r':
        visualize(queue, skel, 0)
        notify_qgis()
        user_input = raw_input(str(step) + '  - at start time; "n" to now-0.1, any other key to continue$ ')
        if user_input == 'n':
            visualize(queue, skel, now-0.01)
            notify_qgis()
            user_input = raw_input(str(step) + '  - now time; paused - press a key to continue$ ')


def visualize(queue, skel, NOW):
    """ Visualize progress by writing geometry to WKT files to be viewed with
    QGIS """
    import os
    if not os.path.exists('/tmpfast/support_lines.wkt'):
        with open('/tmpfast/support_lines.wkt', 'w') as fh:
            # from grassfire.line2d import as_wkt
            fh.write("wkt\tlr\toriginal")
            fh.write("\n")
            fh.write("LINESTRING(0 0, 10 0)\tl\tTrue")

    with open('/tmpfast/queue.wkt', 'w') as fh:
        fh.write("pos;wkt;evttype;evttime;tritype;id;n0;n1;n2;finite;info;wavefront_directions\n")
        for i, evt in enumerate(queue):
            fh.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10}\n".format(
                i,
                evt.triangle.visualize_at(NOW),
                evt.tp,
                evt.time,
                evt.triangle.type,
                id(evt.triangle),
                id(evt.triangle.neighbours[0]),
                id(evt.triangle.neighbours[1]),
                id(evt.triangle.neighbours[2]),
                evt.triangle.is_finite,
                evt.triangle.info,
                evt.triangle.wavefront_directions
            )
            )

    with open('/tmpfast/ktri_progress.wkt', 'w') as fh:
        output_triangles_at_T(skel.triangles, NOW, fh)

    with open("/tmpfast/sknodes_progress.wkt", 'w') as fh:
        fh.write("wkt;step;info\n")
        for node in skel.sk_nodes:
            fh.write("POINT({0[0]} {0[1]});{1};{2}\n".format(node.pos, node.step, node.info))

    with open("/tmpfast/bisectors_progress.wkt", "w") as bisector_fh:
        bisector_fh.write("wkt;info;velocity;unitvec_left;unitvec_right;velocity_magnitude;turn\n")
        for kvertex in skel.vertices:
            if kvertex.stops_at is None:
                p1 = kvertex.visualize_at(NOW)
                bi = kvertex.velocity
                if norm(bi) != 0.:
                    end = add(p1, mul(unit(bi), 0.01))
                else:
                    end = p1
                bisector_fh.write(
                    "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{4};{5};{6};{7}\n".format(
                        p1, end, kvertex.info,kvertex.velocity, kvertex.ul, kvertex.ur, norm(kvertex.velocity), kvertex.turn))
    with open("/tmpfast/segments_progress.wkt", "w") as fh:
        fh.write("id;wkt;finished;length;info\n")
        for kvertex in skel.vertices:
            if kvertex.start_node is not None and kvertex.stop_node is not None:
                start, end = kvertex.start_node.pos, kvertex.stop_node.pos
                fh.write(
                    "{4};LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{5}\n".format(
                        start,
                        end,
                        True,
                        dist(
                            start,
                            end),
                        id(kvertex),
                        kvertex.info
                        ))
            elif kvertex.start_node is not None and kvertex.stop_node is None:
                start, end = kvertex.start_node.pos, kvertex.visualize_at(NOW)
                fh.write(
                    "{4};LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]});{2};{3};{5}\n".format(
                        start,
                        end,
                        False,
                        dist(
                            start,
                            end),
                        id(kvertex),
                        kvertex.info
                        ))

    with open("/tmpfast/vertices1_progress.wkt", 'w') as fh1:
        fh1.write("id;wkt;leftid;rightid;info\n")
        for kvertex in skel.vertices:
            #             if kvertex.start_node is not None and kvertex.stop_node is not None:
            #                 fh0.write("{1};POINT({0[0]} {0[1]})\n".format(kvertex.visualize_at(kvertex.starts_at), id(kvertex)))
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
                assert kvertex.stops_at is None
                fh1.write(
                    "{1};POINT({0[0]} {0[1]});{2};{3};{4}\n".format(
                        kvertex.visualize_at(NOW),
                        id(kvertex),
                        left_id,
                        right_id, kvertex.info))

    with open("/tmpfast/wavefront_edges_progress.wkt", "w") as fh:
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

    with open('/tmpfast/signal', 'w') as fh:
        fh.write('{}'.format(NOW))
