from tri import ToPointsAndSegments, triangulate
from tri.delaunay import FiniteEdgeIterator

from grassfire.inout import output_offsets, output_skel
from grassfire.initialize import init_skeleton
from grassfire.events import init_event_list, event_loop
from grassfire.transform import get_transform, get_box


__all__ = ["calc_skel"]
# ------------------------------------------------------------------------------
# main function for calculating skeleton

def calc_skel(conv, pause=False, output=False):
    """Perform the calculation of the skeleton, given points and segments

    Returns:
        skel -- skeleton structure
    """
    # step 0 -- get transformation parameters
#     box = get_box(conv.points)
#     transform = get_transform(box)
#     pts = map(transform.forward, conv.points)
    # step 1 -- triangulate
    # FIXME: keep info on points 
    # (so that we know after the construction what each node represents)
    pts = conv.points
    dt = triangulate(pts, None, conv.segments)
    with open("/tmp/edges.wkt", "w") as fh:
        fh.write("id;wkt\n")
        edgeit = FiniteEdgeIterator(dt, constraints_only=True)
        for j, edge in enumerate(edgeit):
            fh.write("{0};LINESTRING({1[0][0]} {1[0][1]}, {1[1][0]} {1[1][1]})\n".format(j, edge.segment))
    # step 2 -- copy over triangles and deal with 
    # - terminal 1-vertices (add triangle)
    # - infinite triangles
    skel = init_skeleton(dt)
    # step 3 -- make initial event list
    el = init_event_list(skel)
    # step 4 -- handle events until finished
    last_evt_time = event_loop(el, skel, pause)
    # step 5 -- output offsets and the skeleton
    if output:
        output_offsets(skel, last_evt_time)
        output_skel(skel)
    return skel