from tri import ToPointsAndSegments, triangulate
from io import output_dt, output_offsets, output_skel
from initialize import init_skeleton
from events import init_event_list, event_loop

__all__ = ["calc_skel"]
# ------------------------------------------------------------------------------
# test cases

def calc_skel(conv):
    """Perform the calulation of the skeleton, given 
    points, info and segments
    """
    dt = triangulate(conv.points, None, conv.segments)
    output_dt(dt)
    skel = init_skeleton(dt)
    el = init_event_list(skel)
    event_loop(el, skel)
    output_offsets(skel)
    output_skel(skel)