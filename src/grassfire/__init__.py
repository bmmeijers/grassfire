from tri import ToPointsAndSegments, triangulate
from grassfire.inout import output_dt, output_offsets, output_skel
from grassfire.initialize import init_skeleton
from grassfire.events import init_event_list, event_loop

__all__ = ["calc_skel"]
# ------------------------------------------------------------------------------
# test cases

def calc_skel(conv, pause=False, output=True):
    """Perform the calculation of the skeleton, given 
    points, info and segments
    """
    from tri.delaunay import Edge
    from grassfire.inout import output_triangles, output_vertices_at_T, output_edges_at_T
    from operator import add

    dt = triangulate(conv.points, None, conv.segments)

    if output:
        output_dt(dt)
    skel = init_skeleton(dt)
    if output:
        # write bisectors to file
        with open("/tmp/bisectors.wkt", "w") as bisector_fh:
            bisector_fh.write("wkt\n")
            for kvertex in skel.vertices:
                p1 = kvertex.origin
                bi = kvertex.velocity
                bisector_fh.write("LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})\n".format(p1, map(add, p1, bi)))
        with open("/tmp/ktris.wkt", "w") as fh:
            output_triangles(skel.triangles, fh)
        with open("/tmp/kvertices.wkt", "w") as fh:
            output_vertices_at_T(skel.vertices, 0,fh)
        with open("/tmp/initial_edges.wkt", "w") as fh:
            edges = []
            for t in skel.triangles:
                for side, n in enumerate(t.neighbours):
                    if n is None:
                        edges.append(Edge(t, side))
            output_edges_at_T(edges, 0, fh)
# #     tmp_events(skel)
    el = init_event_list(skel)
    event_loop(el, skel, pause)
 
#     if output:
    output_offsets(skel)
    output_skel(skel)
    return skel