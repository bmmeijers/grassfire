from tri.delaunay.helpers import ToPointsAndSegments
from tri.delaunay.insert_kd import triangulate
from grassfire.initialize import make_unit_vectors
from tri.delaunay.inout import output_triangles
from tri.delaunay.tds import Edge
from grassfire.vectorops import add


def make_linestring(pt, v):
    wkt = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})"
    return wkt.format(pt, add(pt, v))


def test_make_unit_vectors():
    conv = ToPointsAndSegments()
    polygon = [[(0, 0), (10, 0), (5, 7.5), (0, 0)]]
    conv.add_polygon(polygon)
    dt = triangulate(conv.points, None, conv.segments)

    uvs = make_unit_vectors(dt)
    with open("/tmp/tris.txt", "w") as f, open("/tmp/units.txt", "w") as fhu:
        output_triangles(uvs.keys(), f)
        fhu.write("wkt\n")
        for t in uvs:
            for i, u in enumerate(uvs[t]):
                if u is not None:
                    edge = Edge(t, i)
                    start, end = edge.segment
                    midx, midy = (start.x + end.x) * .5, (start.y + end.y) * .5
                    wkt = make_linestring((midx, midy), u)
                    fhu.write("{}\n".format(wkt))

test_make_unit_vectors()