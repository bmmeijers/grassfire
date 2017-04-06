from tri import ToPointsAndSegments, triangulate
from grassfire.initialize import split_star
from tri.delaunay import output_triangles, Edge, StarEdgeIterator, cw, ccw
from grassfire.vectorops import add


def test_split_star():
    conv = ToPointsAndSegments()
    polygon = [
        [(0, 0), (10, 0), (15, 7), (5, 22), (-7, 28), (3, 11), (-5, 7), (0, 0)]]
    conv.add_polygon(polygon)
#     conv.add_point((0, 0))
#     conv.add_point((0, 5))
#     conv.add_segment((0, 0), (0, 5))
    dt = triangulate(conv.points, None, conv.segments)
#     with open("/tmp/tris.txt", "w") as fh:
#         output_triangles(dt.triangles, fh)

    for v in dt.vertices:
        if v.x == 0 and v.y == 0:
            break
    groups = split_star(v)
    # post condition, the number of triangles in all groups is the
    # same as the number of edges in the star of the vertex
    ct = 0
    for group in groups:
        ct += len(group)
    assert len([v for v in StarEdgeIterator(v)]) == ct

test_split_star()
