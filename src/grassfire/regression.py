"""2D Euclidean regression using Principal Component Analysis.
"""


# Partly based on code, copyright (c) 2010 Steven D'Aprano.
# MIT license
# https://code.google.com/archive/p/pycalcstats/

import math
from grassfire.calc import near_zero


def _generalised_sum(data, func):
    """_generalised_sum(data, func) -> len(data), sum(func(items of data))

    Return a two-tuple of the length of data and the sum of func() of the
    items of data. If func is None, use just the sum of items of data.
    """
    count = len(data)
    if func is None:
        total = math.fsum(data)
    else:
        total = math.fsum(func(x) for x in data)
    return count, total


def _SS(data, m):
    """SS = sum of square deviations.
    Helper function for calculating variance directly.
    """
    if m is None:
        m = mean(data)
    return _generalised_sum(data, lambda x: (x-m)**2)


def _SP(xdata, mx, ydata, my):
    """SP = sum of product of deviations.
    Helper function for calculating covariance directly.
    """
    if mx is None:
        mx = mean(xdata)
    if my is None:
        my = mean(ydata)
    return _generalised_sum(zip(xdata, ydata), lambda t: (t[0]-mx)*(t[1]-my))


def mean(data):
    """Return the sample arithmetic mean of a sequence of numbers.

    >>> mean([1.0, 2.0, 3.0, 4.0])
    2.5

    The arithmetic mean is the sum of the data divided by the number of data.
    It is commonly called "the average". It is a measure of the central
    location of the data.
    """
    n, total = _generalised_sum(data, None)
    if n == 0:
        raise ValueError('mean of empty sequence is not defined')
    return total/n


def variance(data, m=None):
    """variance(data [, m]) -> sample variance of data.

    >>> variance([0.25, 0.5, 1.25, 1.25,
    ...           1.75, 2.75, 3.5])  #doctest: +ELLIPSIS
    1.37202380952...

    If you know the population mean, or an estimate of it, then you can pass
    the mean as the optional argument m. See also stdev.

    The variance is a measure of the variability (spread or dispersion) of
    data. The sample variance applies when data represents a sample taken
    from the relevant population. If it represents the entire population, you
    should use pvariance instead.
    """
    n, ss = _SS(data, m)
    if n < 2:
        raise ValueError('sample variance or standard deviation'
                         ' requires at least two data points')
    return ss/(n-1)


def pcov(xdata, ydata, mx=None, my=None):
    """Return the population covariance between (x, y) data.

    >>> pcov([0.75, 1.5, 2.5, 2.75, 2.75], [0.25, 1.1, 2.8, 2.95, 3.25])
    ... #doctest: +ELLIPSIS
    0.93399999999...
    >>> pcov([(0.1, 2.3), (0.5, 2.7), (1.2, 3.1), (1.7, 2.9)])
    0.15125

    """
    n, s = _SP(xdata, mx, ydata, my)
    if n > 0:
        return s/n
    else:
        raise ValueError('population covariance requires at least one point')


def split(L):
    """Split list with 2-tuples in 2 lists"""
    xlist = []
    ylist = []
    for x, y in L:
        xlist.append(x)
        ylist.append(y)
    assert len(xlist) == len(ylist)
    return (xlist, ylist)


def cov(xdata, ydata, mx=None, my=None):
    """Return the sample covariance between (x, y) data.

    >>> cov([0.75, 1.5, 2.5, 2.75, 2.75], [0.25, 1.1, 2.8, 2.95, 3.25])
    ... #doctest: +ELLIPSIS
    1.1675

    Covariance reduces down to standard variance when applied to the same
    data as both the x and y values:

    >>> data = [1.2, 0.75, 1.5, 2.45, 1.75]
    >>> cov(data, data)  #doctest: +ELLIPSIS
    0.40325000000...
    >>> variance(data)  #doctest: +ELLIPSIS
    0.40325000000...

    """
    n, s = _SP(xdata, mx, ydata, my)
    if n > 1:
        return s/(n-1)
    else:
        raise ValueError('sample covariance requires at least two points')


def eig_2x2(a, b, c, d):
    """Calculate eigenvalues and vectors of 2x2 matrix A, where:

         | a   b |
    A =  |       |
         | c   d |

     T = a + d
     D = a * d - b * c

     Eigenvalues:

     L1 = T/2 + (T**2/4 - D)**1/2
     L2 = T/2 - (T**2/4 - D)**1/2

     If c is not zero, then the eigenvectors are:

     | L1-d |   | L2-d |
     |      | , |      |
     |   c  |   |   c  |

     If b is not zero, then the eigenvectors are:

     |  b   |   |   b  |
     |      | , |      |
     | L1-a |   | L2-a |

     If both b and c are zero, then the eigenvectors are:

     |  1  |   |  0  |
     |     | , |     |
     |  0  |   |  1  |

     Note, the matrix is row-based!
    """
    T = a + d
    D = a * d - b * c
    tmp = 0.25 * T**2 - D
    tmp = math.sqrt(max(0, tmp))  # prevent negative square root
    L1 = 0.5 * T + tmp
    L2 = 0.5 * T - tmp
    if not near_zero(c):  # != 0
        eig_vecs = (L1 - d, c), (L2 - d, c)
    elif not near_zero(b):  # != 0
        eig_vecs = (b, L1 - a), (b, L2 - a)
    else:
        eig_vecs = (1.0, 0.0), (0.0, 1.0)
    eig_vals = map(abs, [L1, L2])  # is taking the absolute value needed?
    return eig_vals, eig_vecs


def adjust(data):
    """Calculate mean of list of values and subtract the mean of every element
    in the list, making a new list.

    Returns tuple of mean, list of adjusted values
    """
    mu = mean(data)
    return mu, map(lambda x: (x-mu), data)


def regress(pts):
    """Return list of rotated points. The points are rotated in such a way
    that the direction of largest spread after rotation coincides with the
    positive x-axis, and the mean of the points is transformed to (0,0).
    If the original points formed a straight line, then the rotated points
    should have y-values that are all near zero.
    """
    # split points in list of x- and y-values
    xs, ys = split(pts)
    # adjust x- and y-values
    _, xsadj = adjust(xs)
    _, ysadj = adjust(ys)
    # calculate variances (spread) in x- and y-direction
    # If one of the two variances is (nearly) 0,
    # we short circuit our logic
    # -> points then have to be on a straight line
    # (either horizontal or vertical)
    sx = variance(xsadj, m=0)
    if near_zero(sx):  # == 0
        return ysadj, xsadj
    sy = variance(ysadj, m=0)
    if near_zero(sy):  # == 0
        return xsadj, ysadj
    # calculate covariance
    sxy = cov(xsadj, ysadj, 0, 0)
    # get list of eigenvalues and vectors
    # these are sorted based on size of eigenvalues
    eig_sorted = sorted(zip(*eig_2x2(sx, sxy, sxy, sy)), reverse=True)
    vecs = [vec for _, vec in eig_sorted]
    newxs, newys = [], []
    for pt in zip(xsadj, ysadj):
        # no need to transpose the vectors as they are
        xnew = vecs[0][0] * pt[0] + vecs[0][1] * pt[1]
        ynew = vecs[1][0] * pt[0] + vecs[1][1] * pt[1]
        newxs.append(xnew)
        # residuals?!
        # These should be squared distances to regression line that was fitted
        newys.append(ynew)
    return newxs, newys


def are_residuals_near_zero(pts):
    """Returns whether Euclidean regression returns residuals that are
    all near zero (all are very small values).
    """
    y = regress(pts)[1]
    return all(map(near_zero, y))


def _swapxy(data):
    """Swap x and y coordinates"""
    return [(y, x) for (x, y) in data]


def _test1():
    """Create some points on a line that is rotated in n steps around (0, 0)
    Independent from this rotation, the residuals found should be near zero
    """
#     import matplotlib.pyplot as plt
    from math import pi, cos, sin
    n = 800
    PI2 = 2.0*pi
    angle = PI2 / n
    for i in range(n):
        pts = []
        beta = i * angle
        for r in range(1, 10):
            x = r*cos(beta)
            y = r*sin(beta)
            pts.append((x, y))
        are_zero = are_residuals_near_zero(pts)
        # print beta, are_zero
        assert are_zero
#         plt.scatter([pt[0] for pt in pts], [pt[1] for pt in pts], c='red',
#                     marker='s', label = 'input')
#         nxs, nys = residuals(pts)
#         #plt.scatter(xsadj, ysadj, c='green', marker='o', label = 'adjusted')
#         plt.scatter(nxs, nys, label = 'new')
#     #plt.legend()
#     plt.show()


def _test2():
    pts = [(-0.08303192490226027, 0.805999247350045),
           (0.08308419226024952, 0.805999247350045),
           (0.7038322426877964, 0.8059992473500452),
           (-0.7038322426877968, 0.8059992473500452),
           (-0.08303192490226027, 0.805999247350045),
           (0.7038322426877964, 0.8059992473500452),
           (-0.08303192490226027, 0.805999247350045),
           (-0.7038322426877968, 0.8059992473500452),
           (-0.7038322426877968, 0.805999247350045),
           (0.7038322426877964, 0.8059992473500452),
           (0.08308419226024952, 0.805999247350045),
           (0.7038322426877964, 0.805999247350045)]
    # adjustedx, adjustedy = regress(pts)
    assert are_residuals_near_zero(pts) is True

if __name__ == "__main__":
    _test1()
    _test2()
