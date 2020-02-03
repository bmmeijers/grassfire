from tri.delaunay.helpers import ToPointsAndSegments
from tri.delaunay.insert_kd import triangulate
from tri.delaunay.iter import FiniteEdgeIterator, TriangleIterator
from tri.delaunay.inout import output_triangles

from grassfire.inout import output_offsets, output_skel
from grassfire.initialize import init_skeleton, internal_only_skeleton
from grassfire.events import init_event_list, event_loop
from grassfire.transform import get_transform, get_box

__version__ = '0.1.dev0'
__license__ = 'MIT License'
__author__ = 'Martijn Meijers'
__all__ = ["calc_skel"]
# ------------------------------------------------------------------------------
# main function for calculating skeleton


# FIXME: API -- internal / external calculation
# I E
# t t -- both internal and external (default?)
# t f -- internal only (or should this be default?)
# f t -- external only
# f f -- does not make sense (no skeleton)


def calc_skel(conv, pause=False, output=False, shrink=True,
              internal_only=False):
    """Perform the calculation of the skeleton, given points and segments

    Returns:
        skel -- skeleton structure
    """
    # step 0 -- get transformation parameters
    if shrink:
        box = get_box(conv.points)
        transform = get_transform(box)
        pts = map(transform.forward, conv.points)
    # step 1 -- triangulate
    # FIXME: keep info on points
    # (so that we know after the construction what each node represents)
    else:
        pts = conv.points
    dt = triangulate(pts, None, conv.segments, output)
    if output:
#         with open("/tmp/alltris.wkt", "w") as fh:
#             output_triangles([t for t in TriangleIterator(dt, 
#                                                           finite_only=False)],
#                              fh)
        with open("/tmp/edges.wkt", "w") as fh:
            fh.write("id;wkt\n")
            edgeit = FiniteEdgeIterator(dt, constraints_only=True)
            for j, edge in enumerate(edgeit):
                fh.write(
                    "{0};LINESTRING({1[0][0]} {1[0][1]}, {1[1][0]} {1[1][1]})\n".format(
                        j,
                        edge.segment))
    # step 2a -- copy over triangles and deal with
    # - terminal 1-vertices (add triangle)
    # - infinite triangles
    skel = init_skeleton(dt)
    # step 2b -- do we have a polygon and only internal to its boundaries
    # where do we want to obtain the skeleton?
    if internal_only:
        # keeps internal kinetic triangle/vertices only
        skel = internal_only_skeleton(skel)
    # step 3 -- make initial event list
    el = init_event_list(skel)
    # step 4 -- handle events until finished
    last_evt_time = event_loop(el, skel, pause)
    # step 5 -- output offsets and the skeleton
    if output:
        output_offsets(skel, last_evt_time)
        output_skel(skel, last_evt_time + 10)
    return skel

def calc_offsets(skel, now):
    ct = 100
    inc = now / ct
    for t in range(ct):
        t *= inc
        for v in skel.vertices:
            if (v.starts_at <= t and v.stops_at > t) or \
                (v.starts_at <= t and v.stops_at is None): 
                try:
                    yield (v.position_at(t), 
                            v.left_at(t).position_at(t), 
                            t, 
                            id(v),
                            id(v.left_at(t)))
                except AttributeError:
                    continue