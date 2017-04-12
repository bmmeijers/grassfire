from tri.delaunay import cw, ccw
from grassfire.calc import near_zero


def point_to_each_other(triangle, side):
    """Asserts that two kinetic vertices along the wavefront
    point to each other
    """
    v0, v1 = triangle.vertices[cw(side)], triangle.vertices[ccw(side)]
    assert v0.left is v1, "@triangle: {} - v0 := {}, v0.left {} != {}".format(id(triangle), id(v0), id(v0.left), id(v1))
    assert v1.right is v0, "@triangle: {} - v1 := {}, v1.right {} != {}".format(id(triangle), id(v1), id(v1.right), id(v0))


def check_wavefront_links(tri):
    """Check links of the kinetic vertices along the wavefront"""
    for t in tri:
        if t is None:
            continue
        if t.stops_at is None:
            for side in range(3):
                if t.neighbours[side] is None:
                    point_to_each_other(t, side)  # t.neighbours[side]


def at_same_location(V, now):
    """Checks whether all vertices are more or less at same location of first
    vertex in the list
    """
    P = [v.position_at(now) for v in V]
    p = P[0]
    for o in P[1:]:
        if not (near_zero(p[0]-o[0]) and near_zero(p[1]-o[1])):
            return False
    return True
