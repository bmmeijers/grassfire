# -*- coding: utf-8 -*-

from operator import sub as _sub, mul as _mul, truediv as _div, add as _add
from math import fsum, sqrt
from grassfire.calc import near_zero

import logging

#_s = 27
#_factor = 2**_s + 1

#def split(a):
#    c = float(_factor * a) # factor= 2**s+ 1
#    x = float(c - (c -a))
#    y = float(a - x)
#    return x, y


#def two_product(a, b):
#    x = a * b
#    a1, a2 = split(a)
#    b1, b2 = split(b)
#    y = a2*b2 -(((x - a1*b1)- a2*b1) - a1 *b2)
#    return x,y


#def two_sum(a, b):
#    x = (a + b)
#    z = (x - a)
#    y = ((a - (x - z)) + (b - z))
#    return x, y


#def accurate_dot(x, y):
#    n = len(x)
##    if 2*n*eps>=1,error('inclusion failed'),end
#    [p, s] = two_product(x[0], y[0])
##    e = abs(s)
#    for i in range(1, n):
#        [h, r] = two_product(x[i], y[i])
#        [p, q] = two_sum(p, h)
#        t = (q + r)
#        s = (s + t)
##        e = (e + abs(t))
#    res = (p + s)
#    return res

# alias accurate dot function
#dot = accurate_dot


def dot(v1, v2):
    """Returns dot product of v1 and v2 """
    assert len(v1) == len(v2), 'Vector dimensions should be equal'
    return fsum(p * q for p, q in zip(v1, v2))


def add(a, b):
    """Add a vector b to a, or add a scalar"""
    if hasattr(b, '__iter__'):
        if len(a) != len(b):
            raise ValueError('Vector dimensions should be equal')
        return tuple(map(_add, a, b))
    else:
        return tuple(ai + b for ai in a)


def mul(a, b):
    """Multiply a vector either element-wise with another vector, or with a
    scalar."""
    if hasattr(b, '__iter__'):
        assert len(a) == len(b), 'Vector dimensions should be equal'
        return tuple(map(_mul, a, b))
    else:
        return tuple(ai * b for ai in a)


def sub(a, b):
    """Subtract a vector b from a, or subtract a scalar"""
    if hasattr(b, '__iter__'):
        assert len(a) == len(b), 'Vector dimensions should be equal'
        return tuple(map(_sub, a, b))
    else:
        return tuple(ai - b for ai in a)


def div(a, b):
    """Element-wise division with another vector, or with a scalar."""
    if hasattr(b, '__iter__'):
        assert len(a) == len(b), 'Vector dimensions should be equal'
        return tuple(map(_div, a, b))
    else:
        return tuple(ai / b for ai in a)


def norm2(v):
    """Returns the norm of v, *squared*."""
    return dot(v, v)


def norm(a):
    """L2 norm ('distance')"""
    return norm2(a) ** 0.5


def unit(v):
    """Returns the unit vector in the direction of v."""
    return div(v, norm(v))


def make_vector(end, start):
    """Creates a vector from the start to the end.
    Vector is made based on two points: end -(minus) start.
    """
    return sub(end, start)


def dist(start, end):
    """Distance between two positons"""
    return norm(make_vector(end, start))


def coefficients_from_points(p, q):
    """ given 2 points p and q, give the coefficients (a,b,c) for the line
    that runs from p to q: ax + by + c = 0

    when a = 0, then the line is horizontal
    when b = 0, then the line is vertical

    see also: 
    https://www.mathcentre.ac.uk/resources/uploaded/mc-ty-strtlines-2009-1.pdf
    """
    (px, py) = p
    (qx, qy) = q
    # horizontal line
    if py == qy:
        a = 0.
        if qx > px:
            b = 1.
            c = -py
        elif qx == px: # q and p at same x, direction unknown
            b = 0.
            c = 0.
        else:
            b = -1.
            c = py
    # vertical line
    elif qx == px:
        b = 0.
        if qy > py: # q above p
            a = -1.
            c = px
        elif qy == py: # q and p at same y, direction unknown
            a = 0.
            c = 0.
        else:
            a = 1.
            c = -px
    # neither horizontal or vertical
    else:
        a = py - qy
        b = qx - px
        c = -px * a - py * b
    return tuple(map(float, (a, b, c)))


def coefficients_perpendicular_through_point(la, lb, px, py):
    a = -lb
    b = la
    c = lb * px - la * py
    return tuple(map(float, (a, b, c)))

def coefficients_bisector_of_lines(pa, pb, pc, qa, qb, qc):
    # see: 
    # https://math.stackexchange.com/questions/38665/equation-of-angle-bisector-given-the-equations-of-two-lines-in-2d
    # https://www.math-only-math.com/equations-of-the-bisectors-of-the-angles-between-two-straight-lines.html
    #
    # normalize
    n1 = sqrt(pa * pa + pb * pb)
    n2 = sqrt(qa * qa + qb * qb)
    # add
    a = n2 * pa + n1 * qa
    b = n2 * pb + n1 * qb
    c = n2 * pc + n1 * qc
    # would this be a degenerate line? handle it
    if (a == 0 and b == 0):
        a = n2 * pa - n1 * qa
        b = n2 * pb - n1 * qb
        c = n2 * pc - n1 * qc
    return tuple(map(float, (a, b, c)))


class Line2:
    def __init__(self, w, b, normalize=True):
        w = tuple(map(float, w))
        b = float(b)
        self.w = w
        self.b = b
        ### print(norm2(w) == 1)
        if normalize:
            self._normalize()

    def __eq__(self, other):
        return self.w == other.w and self.b == other.b

    def _normalize(self):
        nrm = norm(self.w)
#        print(f'norm {nrm}')
        self.b /= nrm
        self.w = unit(self.w)  

    def __repr__(self):
        return "Line2(w={}, b={})".format(self.w, self.b)

    def translated(self, v):
        """ translated line in direction of vector *v*"""
        d = dot(self.w, v)
        return Line2(self.w, self.b - d, normalize=(d != 0.0))

    def perpendicular(self, through):
        """ perp line """
        # line perpendicular to self, passing through pt,
        # the direction of the resulting line is rotated
        # counterclockwise by 90 degrees. 
        coeff = coefficients_perpendicular_through_point(self.w[0], self.w[1],
                                                         through[0], through[1])
        return Line2(coeff[:2], coeff[2])

    def bisector(self, other):
        """ bisector defined by self and other Line2 """
        a, b, c = coefficients_bisector_of_lines(self.w[0], self.w[1], self.b,
                                                 other.w[0], other.w[1], other.b)
        return Line2([a, b], c)

    def signed_distance(self, pt):
        """ signed distance of line *self* to point *pt*

        + = left
        - = right
        0 = on
        """
        return dot(self.w, pt) + self.b

    @property
    def through(self):
        """
        Returns nD-point through which this hyperplane passes
        """
        return mul(self.w, -self.b)

    @classmethod
    def from_points(cls, start, end): # !end! - start
        coeff = coefficients_from_points(start, end)
        ln = cls(coeff[:2], coeff[2])
        assert end != start
#        be = -dot(ln.w, end)
#        bs = -dot(ln.w, start)
#        assert be == bs == ln.b
        #== ln.b
#        print(f'w: {ln.w}')
#        print(f'be: {be}')
#        print(f'bs: {bs}')
#        print(f'b: {ln.b}')
        dist_end = ln.signed_distance(end)
        dist_start = ln.signed_distance(start)
#        assert dist_start == 0
#        assert dist_end == 0
        return ln

    def y_at_x(self, x):
        (a, b), c = self.w, self.b
        return (-a*x-c) / b;

    def ends(self):
        ccw = rotate90ccw(self.w)
        cw = rotate90cw(self.w)
        end = add(mul(cw, 1000.), self.through)
        start = add(mul(ccw, 1000.), self.through)
        return (start, end)

    def visualize(self):
        return "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(*self.ends())

    def at_time(self, now):
        """ Return Line2 at specific time """
        if now == 0.0:
            return Line2(self.w, self.b, normalize=False)
        else:
            logging.debug(' (constructing new line at t= {})'.format(now))
            return self.translated(mul(self.w, now)) # at_time(0) / # at_time(1)
        # should we project the start / end points on the line ??
        #http://www.sunshine2k.de/coding/java/PointOnLine/PointOnLine.html



#        if self.w[0] == 0.0:
#            # a = 0 , horizontal
#            pass
#        elif self.w[1] == 0.0:
#            pass
#        else:
#            xmin = -2000.0
#            xmax = +2000.0
#            ymin = self.y_at_x(xmin)
#            ymax = self.y_at_x(xmax)
#            return (xmin, ymin), (xmax,ymax)



class WaveFront:
    """ A line that remembers start and end point from which it is constructed """
    def __init__(self, start, end, line=None):
        if line is None:
            self.line = Line2.from_points(start, end)
        else:
            assert isinstance(line, Line2) == True
            self.line = line
        self.start = tuple(map(float, start))
        self.end = tuple(map(float, end))

    def __str__(self):
        return "WF start: {0} end: {1} line: {2[0]}·x + {2[1]}·y + {3} = 0.".format(self.start, self.end, self.line.w, self.line.b)


class WaveFrontIntersector:
    """ """
    def __init__(self, wf_left, wf_right):
        self.left = wf_left
        self.right = wf_right
        logging.debug(self.left)
        logging.debug(self.right)

    def get_bisector(self):
        # configuration at time t=0
        intersector = LineLineIntersector(self.left.line, self.right.line)
        if intersector.intersection_type() == LineLineIntersectionResult.LINE:
            # parallel = True; intersect = True
            bi = add(mul(self.left.line.w, 0.5), mul(self.right.line.w, 0.5))
            # the magnitude of the bisector here is either:
            #
            #  a) near 0.0 -> wavefronts moving in opposite direction
            #  b) near 2.0 -> wavefronts moving in same direction
        elif intersector.intersection_type() == LineLineIntersectionResult.POINT:
            # parallel = False; intersect = True
            # configuration at time t = 1 (line.w == unit vector)
            left_translated = self.left.line.translated(self.left.line.w)
            right_translated = self.right.line.translated(self.right.line.w)

            intersector_inner = LineLineIntersector(left_translated, right_translated)
            assert intersector_inner.intersection_type() == LineLineIntersectionResult.POINT
            bi = make_vector(end=intersector_inner.result, start=intersector.result)
        elif intersector.intersection_type() == LineLineIntersectionResult.NO_INTERSECTION:
            # parallel = True; intersect = False
            added = add(self.left.line.w, self.right.line.w)
            bi = added
            # assert near_zero(magn)
        magn = norm(bi)
        logging.debug("magnitude of bisector: {}".format(magn))
        return bi

    def get_intersection(self):
        return self.get_intersection_at_t()

    def get_intersection_at_t(self, t):
        intersector = LineLineIntersector(self.left.line.at_time(t), self.right.line.at_time(t))
        if intersector.intersection_type() == LineLineIntersectionResult.POINT:
            return intersector.result
        else:
            raise ValueError('parallel lines, can not compute point of intersection')


class LineLineIntersectionResult:
    NO_INTERSECTION = 0
    POINT = 1
    LINE = 2


class LineLineIntersector:
    def __init__(self, one, other):
        self.one = one
        self.other = other
        self.result = None

    def intersection_type(self):
        # solve intersection
        #
        one, other = self.one, self.other
        assert len(one.w) == 2
        assert len(other.w) == 2

        # == 3 possible outcomes in 2D:
        #
        # 0. overlapping lines - always intersecting in a line
        # 1. crossing - point2
        # 2. parallel - no intersection
        #
        (a1, b1), c1 = one.w, one.b
        (a2, b2), c2 = other.w, other.b
        denom = a1 * b2 - a2 * b1
#        print(f'denom {denom}')
        # if denom == 0: # ^FIXME: use near_zero ?
        if near_zero(denom) == True:
            x1 = a1 * c2 - a2 * c1
            x2 = b1 * c2 - b2 * c1
#            print(f'cross1 {x1}')
#            print(f'cross2 {x2}')
            # if (x1 == 0) and (x2 == 0): # ^FIXME: use near_zero ?
            if near_zero(x1) == True and near_zero(x2) == True:
                # overlapping lines, always intersecting in this configuration
                self.result = self.one
                return LineLineIntersectionResult.LINE
            else:
                # parallel lines, but not intersecting in this configuration
                self.result = None
                return LineLineIntersectionResult.NO_INTERSECTION
        else:
            # crossing lines
            num1 = b1 * c2 - b2 * c1
            num2 = a2 * c1 - a1 * c2
#            print(denom, num1, num2)
            x, y, w = num1, num2, denom
            xw = x / w
            yw = y / w
#            print(f'point2 {xw}, {yw}')
            self.result = (xw, yw)
            return LineLineIntersectionResult.POINT


def rotate90ccw(v):
    """Rotate 2d vector 90 degrees counter clockwise

    (x, y) -> (-y, x)
    """
    return (-(v[1]), v[0])


def rotate90cw(v):
    """Rotate 2d vector 90 degrees clockwise

    (x, y) -> (y, -x)
    """
    return (v[1], -v[0])


# def as_wkt(p, q):
#     return "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(p, q)


# class MovingLine(Line2):
#     def __init__(self, w, b, kv_start, kv_end, normalize=True):
#         self.kv_start = kv_start
#         self.kv_end = kv_end
#         super().__init__(w, b)

#     def at_time(self, now):
#         return self.translated(mul(self.w, now)) # at_time(0) / # at_time(1)


def main():
    ####l = Line2.from_points( (10, 0), (0, 0) )
    ####print(l)

    ####l = Line2.from_points( (10, 1), (0, 2) ) 
    ####print(l)

    ####lt = l.translate( (1.0, 1.5) )
    ####print(lt)

    ####print(l.intersection(lt))


    ####k = Line2.from_points( (10, 0), (0, 0) ) 
    ####print(l)

    ####l = Line2.from_points( (0, 10), (0, 0) ) 
    ####print(l)

    ####print(k.intersection(l))


    ####la = Line2.from_points( (5, 10), (0, 10) )
    ####lb = Line2.from_points( (150, 10), (10, 10) )

    ####print(la, lb)

    ####print(la.intersection(lb))


    ###k = Line2.from_points( (1, 1), (0, 0) )
    ###print(k)
    ###print(k.through)

    ###l = Line2.from_points( (0,3),  (5,0) )
    ###print(l)
    ###print(l.through)


    ###m = Line2.from_points( (2, 0),  (0, 2) )
    ###print(m)
    ###print(m.through)

    ###print("="*5)
    ###n = Line2.from_points( (0, 100), (100, 0))
    ###print(n)
    ###print(n.through)
    ###print("="*5)
    ####intersection(n, l)
    ####intersection(l, n)
    ####print("="*5)
    ###t = n.translated((0, 0))
    ###print(t.through)
    ###print("="*5)
    ###t = n.translated((-1,+1))
    ###print(t.through)
    ###print('--')
    ###x_axis_positive = Line2.from_points(end=(1, 10), start=(0, 10))
    ###print('dist', x_axis_positive.signed_distance( (0, 10) ))
    ###print('dist', x_axis_positive.signed_distance( (0, 0) ))
    ###print('dist', x_axis_positive.signed_distance( (0, -10) ))
    ###print(x_axis_positive.through)
    ###print('--')
    ###x_axis_negative = Line2.from_points(end=(-1, 0), start=(0, 0))
    ###print('dist', x_axis_negative.signed_distance( (0,  10) ))
    ###print('dist', x_axis_negative.signed_distance( (0,   0) ))
    ###print('dist', x_axis_negative.signed_distance( (0, -10) ))
    ###print(x_axis_negative.through)


    ####y_axis = Line2.from_points( (0, 0), (0, 1) )
    ####print(y_axis.through)

    ####xpp = x_axis.translate( (0, +1) )
    ####assert(xpp.through == (0,1))

    ####xmm = x_axis.translate( (0, -1) )
    ####assert(xmm.through == (0,-1))

    print("")
    #e0 = Line2.from_points(end=(0, 1), start=(-0.25, 0))
    e0 = Line2.from_points( (-0.25, 0), (0, 1) )
    print(e0)
    e0t = e0.translated(mul(e0.w,50.))
    print(e0t)

    print("")
    #e1 = Line2.from_points(end=(+0.25, 0), start=(0, 1))
    e1 = Line2.from_points( (0, 1), (1,0) )
    print(e1)
    e1t = e1.translated(e1.w)
    print(e1t)

    print("")

    pts = []
    intersect = LineLineIntersector(e0, e1)

    if intersect.intersection_type() == 1:
        print(intersect.result)
        pts.append(intersect.result)

    intersect = LineLineIntersector(e0t, e1t)
    if intersect.intersection_type() == 1:
        print(intersect.result)
        pts.append(intersect.result)

    if len(pts) > 1:
        print(pts)
        velocity = make_vector(end=pts[1], start=pts[0])
        print(velocity)

    xaxis = Line2.from_points( (0, 0), (1, 0) )
    yaxis = Line2.from_points( (0, 0), (0, 1) )

    with open('/tmp/lines.wkt', 'w') as fh:
        fh.write("wkt")
        fh.write("\n")

        fh.write(as_wkt(*xaxis.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*yaxis.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*e0.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*e0t.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*(e0t.perpendicular( (10, -10) ).visualize())))
        fh.write("\n")


        fh.write(as_wkt(*e1.visualize()))
        fh.write("\n")
        fh.write(as_wkt(*e1t.visualize()))
        fh.write("\n")

    #coeff = coefficients_from_points((0, 100), (100, 0))
    #print(coeff)

    #ln = Line2(coeff[:2], coeff[2])
    #ln1 = ln.translated((1,1))
    #print(ln)
    #print(ln.signed_distance((51,51)))
    #print(ln1.signed_distance((51,51)))

    #below = (49,49)
    #print(ln.signed_distance(below))
    #print(ln1.signed_distance(below))

    #print(ln1)
    #print(ln1.through)


    pos_xaxis = Line2.from_points( (0, 0), (-1, 0) )
    neg_xaxis_plus1 = Line2.from_points( (-1, -1), (0, 0) )
    # there is 2 bisectors for the line
    bi_p = pos_xaxis.bisector(neg_xaxis_plus1).perpendicular((0, 0))
    bi_n = neg_xaxis_plus1.bisector(pos_xaxis)

    # with open('/tmp/bisect.wkt', 'w') as fh:
    #     fh.write("wkt")
    #     fh.write("\n")

    #     fh.write(as_wkt(*pos_xaxis.visualize()))
    #     fh.write("\n")

    #     fh.write(as_wkt(*neg_xaxis_plus1.visualize()))
    #     fh.write("\n")

    #     fh.write(as_wkt(*bi_p.visualize()))
    #     fh.write("\n")

    #     fh.write(as_wkt(*bi_n.visualize()))
    #     fh.write("\n")

    la = Line2.from_points( (-1, 0), (0, 0) )
    lb = Line2.from_points( (-1, -1), (0,0) )
    bi_ab  = la.bisector(lb)
    bi_ba  = lb.bisector(la)


    with open('/tmp/bisect.wkt', 'w') as fh:
        fh.write("wkt")
        fh.write("\n")

        fh.write(as_wkt(*la.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*lb.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*bi_ab.visualize()))
        fh.write("\n")

        fh.write(as_wkt(*bi_ba.visualize()))
        fh.write("\n")


def create_bevel_wavefront(first, last):
    """
    turning ccw around a vertex that needs to be made into a bevel
    vertex, we start at the first edge, and stop at the last edge
    """
    assert first.start == last.end
    perp = first.line.perpendicular(through=first.start)
    wf_bevel = WaveFront(first.start, first.start, line = perp)
    del perp
    print(wf_bevel)
    wf_intersect = WaveFrontIntersector(first, wf_bevel)
    bisector1 = wf_intersect.get_bisector()
    intersection = wf_intersect.get_intersection()
    print(bisector1)
    print(intersection)
    assert intersection == first.start == last.end
    wf_intersect = WaveFrontIntersector(wf_bevel, last)
    bisector2 = wf_intersect.get_bisector()
    intersection = wf_intersect.get_intersection()
    print(bisector2)
    print(intersection)
    assert intersection == first.start == last.end
    return wf_bevel, bisector1, bisector2


def test_wf():
    # --- 
    left = WaveFront(start=(-1,1), end= (0,0))
    right = WaveFront(start=(0,0), end=(1,1))
    print(left)
    print(right)
    wf_intersect = WaveFrontIntersector(left, right)
    bisector = wf_intersect.get_bisector()
    print(bisector)

    # --- 
    left = WaveFront(start=(0,0), end= (10,0))
    right = WaveFront(start=(10,0), end=(20,0))
    print(left)
    print(right)
    wf_intersect = WaveFrontIntersector(left, right)
    bisector = wf_intersect.get_bisector()
    print(bisector)

    # --- 
    left = WaveFront(start=(0,0), end=(0,10))
    right = WaveFront(start=(0,10), end=(0,0))
    print(left)
    print(right)
    wf_intersect = WaveFrontIntersector(left, right)
    bisector = wf_intersect.get_bisector()
    print(bisector)


def test_create_bevel_wavefront():
    first = WaveFront(start=(10,12.5), end=(0,0))
    last = WaveFront(start=(0,0), end=(10,12.5))
    bevel0, bi1, bi2 = create_bevel_wavefront(first, last)

    bevel1, bi1, bi2 = create_bevel_wavefront(last, first)

    with open('/tmp/lines.wkt', 'w') as fh:
        fh.write("WKT")
        fh.write("\n")

    with open('/tmp/lines.wkt', 'a') as fh:
        for t in range(1, 10):
            for item in [
                    first.line.at_time(t).visualize(),
                    last.line.at_time(t).visualize(),
                    bevel0.line.at_time(t).visualize(),
                    bevel1.line.at_time(t).visualize()]:
                fh.write(item)
                fh.write("\n")


if __name__ == "__main__":
    # main()
    test_wf()
    test_create_bevel_wavefront()
