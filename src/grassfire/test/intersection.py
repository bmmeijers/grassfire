from geompreds import orient2d
from math import hypot

NOT_INTERSECTING = 0
PARALLEL = 1
COINCIDENT = 2
INTERSECTING_AT_END = 4
INTERSECTING = 8


def intersecting(pa, pb, qa, qb):
    """Returns how two segment defined by p and q are intersecting
    with each other.

    It is assumed that a bounding box check has been performed for
    the two segments and that these boxes *do* overlap!

    Call intersection() to get the location of intersection.
    """
    a = orient2d(pa, pb, qa)
    b = orient2d(pa, pb, qb)
    if (a > 0 and b > 0) or (a < 0 and b < 0):
        return NOT_INTERSECTING

    c = orient2d(qa, qb, pa)
    d = orient2d(qa, qb, pb)
    if (c > 0 and d > 0) or (c < 0 and d < 0):
        return NOT_INTERSECTING

    if a == 0. and b == 0. and c == 0. and d == 0.:
        nume_a = 1.0 * ((qb[0] - qa[0]) * (pa[1] - qa[1])) - \
            ((qb[1] - qa[1]) * (pa[0] - qa[0]))
        nume_b = 1.0 * ((pb[0] - pa[0]) * (pa[1] - qa[1])) - \
            ((pb[1] - pa[1]) * (pa[0] - qa[0]))
        if nume_a == 0.0 and nume_b == 0.0:
            return COINCIDENT
        return PARALLEL

    if a == 0 or b == 0 or c == 0 or d == 0:
        return INTERSECTING_AT_END

    return INTERSECTING


def intersection(pa, pb, qa, qb):
    center = [0., 0.]
    minval = list(pa[:2])
    maxval = list(pa[:2])

    for pt in (pb, qa, qb):
        for i in range(2):
            if pt[i] < minval[i]:
                minval[i] = pt[i]
            if pt[i] > maxval[i]:
                maxval[i] = pt[i]

    for i in range(2):
        center[i] = (maxval[i] + minval[i]) / 2.

    # normalized points, i.e. against center of points
    pa_ = [pa[i] - center[i] for i in range(2)]
    pb_ = [pb[i] - center[i] for i in range(2)]
    qa_ = [qa[i] - center[i] for i in range(2)]
    qb_ = [qb[i] - center[i] for i in range(2)]

    pt = hintersection(pa_, pb_, qa_, qb_)
    for i in range(2):
        pt[i] += center[i]

    # FIXME: should we clamp the coordinates to a box, formed by the segments?
    return tuple(pt)


def hintersection(pa, pb, qa, qb):
    px = pa[1] - pb[1]
    py = pb[0] - pa[0]
    pw = pa[0] * pb[1] - pb[0] * pa[1]
    qx = qa[1] - qb[1]
    qy = qb[0] - qa[0]
    qw = qa[0] * qb[1] - qb[0] * qa[1]
    x = py * qw - qy * pw
    y = qx * pw - px * qw
    w = px * qy - qx * py
    try:
        x_int = x / w
        y_int = y / w
    except ZeroDivisionError:
        raise ValueError('hintersection problem')
    return [x_int, y_int]


def segment_box(segment):
    pa, pb = segment
    minx = min([pa[0], pb[0]])
    miny = min([pa[1], pb[1]])
    maxx = max([pa[0], pb[0]])
    maxy = max([pa[1], pb[1]])
    return ((minx, miny), (maxx, maxy))


def box_box_overlap(ba, bb):
    if bb[0][0] > ba[1][0]:
        return False
    elif bb[0][1] > ba[1][1]:
        return False
    elif bb[1][0] < ba[0][0]:
        return False
    elif bb[1][1] < ba[0][1]:
        return False
    else:
        return True


def segments_intersecting(segments):
    """Are there 'real' intersections inside a set of segments?"""
    annotated = [(segment, segment_box(segment)) for segment in segments]
    for s, sbox in annotated:
        for os, osbox in annotated:
            if id(s) < id(os) and \
                    box_box_overlap(sbox, osbox) and \
                    intersecting(s[0], s[1], os[0], os[1]) == INTERSECTING:
                return True
    return False


def segments_intersection(segments):
    """Return geometry of intersections"""
    annotated = [(segment, segment_box(segment)) for segment in segments]
    pts = []
    for s, sbox in annotated:
        for os, osbox in annotated:
            if id(s) < id(os) and \
                    box_box_overlap(sbox, osbox) and \
                    intersecting(s[0], s[1], os[0], os[1]) == INTERSECTING:
                xpt = intersection(s[0], s[1], os[0], os[1])
                pts.append(xpt)
    return pts


def segment_length(s):
    dx = s[0][0] - s[1][0]
    dy = s[0][1] - s[1][1]
    return hypot(dx, dy)


def test_small():
    test = (0, 0), (10, 10), (5, -10), (5, 10)
    assert intersecting(*test) == INTERSECTING
    assert intersection(*test) == (5, 5)


if __name__ == "__main__":
    test_small()
    segments = [[(0, 0), (10, 10)],
                [(5, -10), (5, 10)]]
    print segments_intersecting(segments)
