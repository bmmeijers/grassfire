from tri.delaunay.tds import cw, ccw, orient2d

from grassfire.vectorops import add
from grassfire.calc import near_zero
from grassfire.primitives import KineticVertex


def point_to_each_other(triangle, side):
    """Asserts that two kinetic vertices along the wavefront
    point to each other
    """
    v0, v1 = triangle.vertices[cw(side)], triangle.vertices[ccw(side)]
    assert v0.left is v1, "@triangle: {} - v0 := {}, v0.left {} != {}".format(id(triangle), id(v0), id(v0.left), id(v1))
    assert v1.right is v0, "@triangle: {} - v1 := {}, v1.right {} != {}".format(id(triangle), id(v1), id(v1.right), id(v0))

def check_bisectors(skel, now):
    for t in skel.triangles:
        if t.stops_at is None:
            for side, n in enumerate(t.neighbours):
                if n is None:
                    check_bisector_direction(t, side, now)

def check_bisector_direction(triangle, side, time):
    """Asserts that orientation of bisector is straight or turning left wrt unconstrained edge on its left"""
    v0, v1 = triangle.vertices[ccw(side)], triangle.vertices[cw(side)]
    pos2 = add(v1.position_at(time), v1.velocity)
    pos0, pos1 = v0.position_at(time), v1.position_at(time)
    ori = orient2d(pos0, pos1, pos2)
    assert ori > 0 or near_zero(ori), "v0, v1: {}, {} | orientation: {} | positions: {}; {}; {}".format(v0.info, v1.info, orient2d(pos0, pos1, pos2), pos0, pos1, pos2) # left / straight


def check_active_triangles_orientation(tri, now):
    for t in tri:
        if t is None:
            continue
        if t.stops_at is None:
            pos = [t.vertices[side].position_at(now) for side in range(3)]
            ori = orient2d(*pos)
            if all(isinstance(t.vertices[side], KineticVertex) for side in range(3)):
                assert ori >= 0 or near_zero(ori), "triangle ({} [{}]) is not turning CCW @ t={}".format(id(t), t.info, now)
            else:
                assert ori <= 0 or near_zero(ori), "inf-triangle ({} [{}]) is not turning CW @ t={}".format(id(t), t.info, now)

def check_wavefront_links(tri):
    """Check links of the kinetic vertices along the wavefront"""
    for t in tri:
        if t is None:
            continue
        if t.stops_at is None:
            for side in range(3):
                if t.neighbours[side] is None:
                    point_to_each_other(t, side)  # t.neighbours[side]

def check_active_triangles(tri):
    """Check active triangles and their neighbours"""
    for t in tri:
        if t is None:
            continue
        if t.stops_at is None:
            for side in range(3):
                ngb = t.neighbours[side]
                if ngb is not None:
                    assert ngb.stops_at is None, "neighbour {} stopped (not active) @ {} \n {}".format(id(tri), id(ngb), {})



def check_kinetic_vertices(tri):
    """Check kinetic vertices of active triangles"""
    for t in tri:
        if t is None:
            continue
        if t.stops_at is None:
            for side in range(3):
                kv = t.vertices[side]
                if isinstance(kv, KineticVertex):
                    assert kv.stops_at is None,"problemo problemo @ {}".format(id(tri))

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
