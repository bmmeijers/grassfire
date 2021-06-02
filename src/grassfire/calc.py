# turn angle between two vectors... oriented away from same points
#
# atan2(v2.y, v2.x) - atan2(v1.y, v1.x)
# add 2pi until positive

# from itertools import imap
# from operator import add, sub, mul, truediv
# from math import pi, atan2, degrees, hypot, sin, sqrt
# from tri.delaunay import orient2d
# import logging

import math


def get_unique_times(times):
    """Filters out None values and then returns unique event times,
    finding the set of values that are numerically close
    """
    return all_close_clusters(filter(lambda x: x is not None, times))


def all_close_clusters(L, abs_tol=1e-7, rel_tol=0.):
    """Return those values in a list that are 'far enough away'
    from other values in a list.
    """
    if L:
        it = iter(sorted(L))
        first = next(it)
        out = [first]
        for val in it:
            if is_close(first, val, abs_tol, rel_tol, method='average'):
                continue
            else:
                out.append(val)
                first = val
        return out
    else:
        return []


def near_zero(val):
    """returns True if a is close to zero. False otherwise

    :param val: the value to be tested
    """
    return is_close(val, 0.0, rel_tol=1e-12, abs_tol=1e-10, method="weak")


def all_close(iterator, abs_tol=0., rel_tol=1.e-9):
    """
    """
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return False
    return all(is_close(first, other, rel_tol, abs_tol, 'strong')
               for other in iterator)


def is_close(a,
             b,
             rel_tol=1e-9,
             abs_tol=0.0,
             method='weak'):
    """
    returns True if a is close in value to b. False otherwise
    :param a: one of the values to be tested
    :param b: the other value to be tested
    :param rel_tol=1e-9: The relative tolerance -- the amount of error
                         allowed, relative to the magnitude of the input
                         values.
    :param abs_tol=0.0: The minimum absolute tolerance level -- useful for
                        comparisons to zero.
    :param method: The method to use. options are:
                  "asymmetric" : the b value is used for scaling the tolerance
                  "strong" : The tolerance is scaled by the smaller of
                             the two values
                  "weak" : The tolerance is scaled by the larger of
                           the two values
                  "average" : The tolerance is scaled by the average of
                              the two values.
    NOTES:
    -inf, inf and NaN behave similarly to the IEEE 754 Standard. That
    -is, NaN is not close to anything, even itself. inf and -inf are
    -only close to themselves.
    Complex values are compared based on their absolute value.
    The function can be used with Decimal types, if the tolerance(s) are
    specified as Decimals::
      isclose(a, b, rel_tol=Decimal('1e-9'))
    See PEP-0485 for a detailed description

    See also:
    http://www.boost.org/doc/libs/1_34_0/libs/test/doc/components/test_tools/floating_point_comparison.html
    http://floating-point-gui.de/errors/comparison/
    http://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html
    """
    if method not in ("asymmetric", "strong", "weak", "average"):
        raise ValueError('method must be one of: "asymmetric",'
                         ' "strong", "weak", "average"')

    if rel_tol < 0.0 or abs_tol < 0.0:
        raise ValueError('error tolerances must be non-negative')

    if a == b:  # short-circuit exact equality
        return True
    # use cmath so it will work with complex or float
#     print a
#     print b
#     if cmath.isinf(a) or cmath.isinf(b):
#         # This includes the case of two infinities of opposite sign, or
#         # one infinity and one finite number. Two infinities of opposite sign
#         # would otherwise have an infinite relative tolerance.
#         return False
    diff = abs(b - a)
    if method == "asymmetric":
        return (diff <= abs(rel_tol * b)) or (diff <= abs_tol)
    elif method == "strong":
        return (((diff <= abs(rel_tol * b)) and
                 (diff <= abs(rel_tol * a))) or
                (diff <= abs_tol))
    elif method == "weak":
        return (((diff <= abs(rel_tol * b)) or
                 (diff <= abs(rel_tol * a))) or
                (diff <= abs_tol))
    elif method == "average":
        return ((diff <= abs(rel_tol * (a + b) * 0.5) or
                 (diff <= abs_tol)))


def groupby_cluster(L):
    """Groups list of 2-tuples in clusters, based on whether tuples are nearly
    equal

    Assumes sorted list as input
    Returns list with sublists with indices
    """
    it = iter(L)
    prev = next(it)
    clusters = []
    cluster = [0]
    ct = 1
    for item in it:
        if near_zero(prev[0] - item[0]) and near_zero(prev[1] - item[1]):
            cluster.append(ct)
        else:
            clusters.append(cluster)
            cluster = [ct]
            prev = item
        ct += 1
    if cluster:
        clusters.append(cluster)
    return clusters


def r_squared(pts):
    """Calculate R**2 for a set of points

    If value returned == 1, these points are on a straight line
    """
    length = len(pts)
    xs = [pt[0] for pt in pts]
    ys = [pt[1] for pt in pts]
    x = sum(xs)
    y = sum(ys)
    xx = sum(x**2 for x in xs)
    yy = sum(y**2 for y in ys)
    xy = sum(x*y for x, y in zip(xs,ys))
    num = (length * xy - x * y)
    sqt = (length * xx - x * x) * (length * yy - y * y)
    if sqt <= 0:
        corr = 0
    else:
        den = math.sqrt(sqt)
        corr = num / den
    return corr

if __name__ == "__main__":
    L = [(0, 0), (0, 0), (1, 1), (1, 1), (2, 2)]
#    print groupby_cluster(L)
