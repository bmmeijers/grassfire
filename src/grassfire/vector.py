"""Vector class, originating from pyeuclid

@see: http://code.google.com/p/pyeuclid/
"""
#from simplegeom.geometry import Envelope, Point, Polygon, LinearRing
#from sink import Schema, Field, Index, Layer, dumps

import math
import operator

class Vector2(object):
    __slots__ = ('x', 'y')
    __hash__ = None

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __copy__(self):
        return self.__class__(self.x, self.y)

    copy = __copy__

    def __repr__(self):
        return 'Vector2({}, {})'.format(self.x, self.y)

    def __eq__(self, other):
        if isinstance(other, Vector2):
            return self.x == other.x and \
                   self.y == other.y
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return self.x == other[0] and \
                   self.y == other[1]

    def __ne__(self, other):
        return not self.__eq__(other)

    def __nonzero__(self):
        return self.x != 0 or self.y != 0

    def __len__(self):
        return 2

    def __getitem__(self, key):
        return (self.x, self.y)[key]

    def __setitem__(self, key, value):
        l = [self.x, self.y]
        l[key] = value
        self.x, self.y = l

    def __iter__(self):
        return iter((self.x, self.y))

    def __getattr__(self, name):
        try:
            return tuple([(self.x, self.y)['xy'.index(c)] \
                          for c in name])
        except ValueError:
            raise AttributeError, name

    def __add__(self, other):
        if isinstance(other, Vector2):
            # Vector + Vector -> Vector
            # Vector + Point -> Point
            # Point + Point -> Vector
            return Vector2(self.x + other.x,
                          self.y + other.y)
        else:
#            assert hasattr(other, '__len__') and len(other) == 2, "{}".format(other)
            return tuple([self.x + other[0], self.y + other[1]])
    __radd__ = __add__

    def __iadd__(self, other):
        if isinstance(other, Vector2):
            self.x += other.x
            self.y += other.y
        else:
            self.x += other[0]
            self.y += other[1]
        return self

    def __sub__(self, other):
        if isinstance(other, Vector2):
            # Vector - Vector -> Vector
            # Vector - Point -> Point
            # Point - Point -> Vector
            return Vector2(self.x - other.x,
                          self.y - other.y)
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(self.x - other[0],
                           self.y - other[1])

    def __rsub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(other.x - self.x,
                           other.y - self.y)
        else:
            assert hasattr(other, '__len__') and len(other) == 2
            return Vector2(other.x - self[0],
                           other.y - self[1])

    def __mul__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(self.x * other, self.y * other)
    __rmul__ = __mul__

    def __imul__(self, other):
        assert type(other) in (int, long, float)
        self.x *= other
        self.y *= other
        return self

    def __div__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.div(self.x, other),
                       operator.div(self.y, other))

    def __rdiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.div(other, self.x),
                       operator.div(other, self.y))

    def __floordiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.floordiv(self.x, other),
                       operator.floordiv(self.y, other))


    def __rfloordiv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.floordiv(other, self.x),
                       operator.floordiv(other, self.y))

    def __truediv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.truediv(self.x, other),
                       operator.truediv(self.y, other))

    def __rtruediv__(self, other):
        assert type(other) in (int, long, float)
        return Vector2(operator.truediv(other, self.x),
                       operator.truediv(other, self.y))
    
    def __neg__(self):
        return Vector2(-self.x, -self.y)
    __pos__ = __copy__
    
    def __abs__(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    magnitude = __abs__

    def magnitude_squared(self):
        return self.x ** 2 + self.y ** 2

    def normalize(self):
        d = self.magnitude()
        if d:
            self.x /= d
            self.y /= d
        return self

    def normalized(self):
        d = self.magnitude()
        if d:
            return Vector2(self.x / d, 
                           self.y / d)
        return self.copy()

    def dot(self, other):
        assert isinstance(other, Vector2)
        return self.x * other.x + \
               self.y * other.y

    def cross(self):
        return Vector2(self.y, -self.x)

    def reflect(self, normal):
        # assume normal is normalized
        assert isinstance(normal, Vector2)
        d = 2 * (self.x * normal.x + self.y * normal.y)
        return Vector2(self.x - d * normal.x,
                       self.y - d * normal.y)

    def angle(self, other):
        """Return the angle to the vector other"""
        return math.acos(self.dot(other) / (self.magnitude()*other.magnitude()))

    def project(self, other):
        """Return one vector projected on the vector other"""
        n = other.normalized()
        return self.dot(n)*n

def rotate90ccw(v):
    """
    Rotating a vector 90 degrees is simple.
    (x, y) rotated 90 degrees around (0, 0) is (-y, x).
    """
    return Vector2(-v.y, v.x)

def rotate90cw(v):
    """
    Rotating a vector 90 degrees is simple.
    (x, y) rotated 90 degrees around (0, 0) is (-y, x).
    If you want to rotate clockwise, you simply do it the other way 
    around, getting (y, -x).
    """
    return Vector2(v.y, -v.x)

def lftrgt(pa, pb, pc, scale = 1.):
    """Make two points on left and right of pb, that are on both sides
    on the angular bisection of pb.
    
    It is supposed that pa,pb,pc form two segments:
    
    pa ---- pb ---- pc
    
    We return two points, in the angular bisector of pb, we scale the
    length of the segment lft-pb and rgt-pb with *scale*

    So the result will look like:
    
            lft
             |
    pa ---- pb ---- pc
             |
            rgt
    """
    u = Vector2(pb[0] - pa[0], pb[1] - pa[1])
    v = Vector2(pc[0] - pb[0], pc[1] - pb[1])
    if (abs(u.x) - abs(v.x)) == 0 and (abs(u.y) - abs(v.y)) == 0:
        # if we have two vectors that cancel each other out
        # we just use the vector for the first segment
        u.normalize()
        left = rotate90ccw(u)
        right = rotate90cw(u)
    else:
        # we have 2 vectors as input, for which we get the bisector
        # at their origin, which we normalize and then rotate 90 degrees
        # clockwise / counterclockwise
        u.normalize()
        v.normalize()
        r = u + v
        r.normalize()
        left = rotate90ccw(r)
        right = rotate90cw(r)
    return left * scale + pb, right * scale + pb




#
#def left(pa, pb, pc, scale = 1.):
#    """Make one points on left of pb, that are on both sides
#    on the angular bisection of pb.
#    
#    It is supposed that pa,pb,pc form two segments:
#    
#    pa ---- pb ---- pc
#    
#    We return two points, in the angular bisector of pb, we scale the
#    length of the segment lft-pb and rgt-pb with *scale*
#
#    So the result will look like:
#    
#            lft
#             |
#    pa ---- pb ---- pc
#             |
#            rgt
#    """
#    u = Vector2(pb[0] - pa[0], pb[1] - pa[1])
#    v = Vector2(pc[0] - pb[0], pc[1] - pb[1])
#    if (abs(u.x) - abs(v.x)) == 0 and (abs(u.y) - abs(v.y)) == 0:
#        # if we have two vectors that cancel each other out
#        # we just use the vector for the first segment
#        u.normalize()
#        left = rotate90ccw(u)
#    else:
#        # we have 2 vectors as input, for which we get the bisector
#        # at their origin, which we normalize and then rotate 90 degrees
#        # clockwise / counterclockwise
#        u.normalize()
#        v.normalize()
#        r = u + v
#        r.normalize()
#        left = rotate90ccw(r)
#    return left * scale + pb
#
#
#def right(pa, pb, pc, scale = 1.):
#    """Make two points on left and right of pb, that are on both sides
#    on the angular bisection of pb.
#    
#    It is supposed that pa,pb,pc form two segments:
#    
#    pa ---- pb ---- pc
#    
#    We return two points, in the angular bisector of pb, we scale the
#    length of the segment lft-pb and rgt-pb with *scale*
#
#    So the result will look like:
#    
#            lft
#             |
#    pa ---- pb ---- pc
#             |
#            rgt
#    """
#    u = Vector2(pb[0] - pa[0], pb[1] - pa[1])
#    v = Vector2(pc[0] - pb[0], pc[1] - pb[1])
#    if (abs(u.x) - abs(v.x)) == 0 and (abs(u.y) - abs(v.y)) == 0:
#        # if we have two vectors that cancel each other out
#        # we just use the vector for the first segment
#        u.normalize()
#        right = rotate90cw(u)
#    else:
#        # we have 2 vectors as input, for which we get the bisector
#        # at their origin, which we normalize and then rotate 90 degrees
#        # clockwise / counterclockwise
#        u.normalize()
#        v.normalize()
#        r = u + v
#        r.normalize()
#        right = rotate90cw(r)
#    return right * scale + pb
#
#
#def main():
#    pa = (0,10)
#    pb = (10,10)
#    pc = (10,20)
#    print lftrgt(pa, pb, pc, scale = 10)
#
#    pa = (-10,0)
#    pb = (0,0)
#    pc = (10,0)
#    print lftrgt(pa, pb, pc)
#
#    pa = (0,-10)
#    pb = (0,0)
    pc = (0,10)
    print lftrgt(pa, pb, pc, 10)

fh = open('/tmp/polys', 'w')
fh.write('--geometry;point\n')

WKTPT = "POINT({0[0]} {0[1]})"
WKTBOX = "POLYGON(({0[0]} {0[1]}, {1[0]} {1[1]}, {2[0]} {2[1]}, {3[0]} {3[1]}, {0[0]} {0[1]}))"
if __name__ == "__main__":
    from densify import densify
    
    main()
    from shapefile import Reader
    shprdr = Reader("data/a1_directions")
    print shprdr.bbox
    shapes = shprdr.shapes()
    print shapes

    raster = {}

    STEP = 20
    WIDTH = 120
    
    gid = Field("gid", "numeric")
    envelope = Field("cell", "polygon")
    centroid = Field("centroid", "point")
    
    schema = Schema()
    schema.add_field(gid)
    schema.add_field(envelope)
    schema.add_field(centroid)
    
    schema.add_index( Index(fields = [gid], primary_key = True) )
    schema.add_index( Index(fields = [envelope]) )
    schema.add_index( Index(fields = [centroid]) )
    
    layer = Layer(schema, "rectigrid", srid = 28992)
    
    for item in shapes:
        densed = densify(item.points, small = 80)
#        densed = item.points
        print "***", densed
        size = len(densed)
        for i in range(size):
            raster[i] = {}
            perp = 0
            if i == 0:
                pa, pb, pc, = densed[0], densed[0], densed[1]
                L = left
                R = right
            elif i == size-1:
                pa, pb, pc, = densed[i], densed[i], densed[i-1]
                L = right
                R = left
            else:
                k, l, m, = i-1, i, i+1
                pa, pb, pc, = densed[k], densed[l], densed[m]
                L = left
                R = right
            for j in range(WIDTH, 1, -STEP):
                raster[i][perp] = L(pa, pb, pc, j)
                perp += 1
            raster[i][perp] = pb
            perp += 1
            for j in range(STEP, WIDTH+1, STEP):
                raster[i][perp] = R(pa, pb, pc, j)
                perp += 1
        gid = 0
        for along in range(len(raster)-1):
#            print along, along + 1
            for perp in range(len(raster[along])-1):
                
#                print perp, perp + 1
                tl, bl, br, tr, = raster[along][perp], raster[along][perp+1], raster[along+1][perp+1], raster[along+1][perp]
                avgx = sum([pt[0] for pt in (tl, bl, br, tr)]) / 4.
                avgy = sum([pt[1] for pt in (tl, bl, br, tr)]) / 4.
#                print >>fh, WKTBOX.format(tl, bl, br, tr),";", WKTPT.format((avgx, avgy))
                
                minx = min([pt[0] for pt in (tl, bl, br, tr)]) 
                maxx = max([pt[0] for pt in (tl, bl, br, tr)]) 
                miny = min([pt[1] for pt in (tl, bl, br, tr)]) 
                maxy = max([pt[1] for pt in (tl, bl, br, tr)])
                
                pl = Polygon(srid = 28992)
                ln = LinearRing()
                ln.append(Point(*tl))
                ln.append(Point(*bl))
                ln.append(Point(*br))
                ln.append(Point(*tr))
                ln.append(Point(*tl))
                pl.append(ln)
                box, centroid = Envelope(minx, miny, maxx, maxy, srid=28992), Point(avgx, avgy)
                print box, centroid
                layer.append(gid, pl, centroid) 
                gid += 1
    print >> fh, dumps(layer) 
fh.close()