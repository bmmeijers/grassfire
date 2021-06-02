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
    # adjust x- and y-values (subtract the mean)
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
    """Helper function to swap x and y coordinates"""
    return [(y, x) for (x, y) in data]


def _test1():
    """Create some points on a line that is rotated in n steps around (0, 0)
    Independent from this rotation, the residuals found should be near zero
    """
    import matplotlib.pyplot as plt
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
        plt.scatter([pt[0] for pt in pts], [pt[1] for pt in pts], c='red',
                    marker='s', label = 'input')
        # nxs, nys = residuals(pts)
        #plt.scatter(xsadj, ysadj, c='green', marker='o', label = 'adjusted')
        # plt.scatter(nxs, nys, label = 'new')
    #plt.legend()
    plt.show()


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


def _test3():
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
    result = regress(pts)
    for i in range(2):
        assert len(result[i]) == 12


def _test4():
    pts = [(-0.5773502691896315, -0.3333333333333352), (-0.5773502691896315, -0.3333333333333364), (-0.5773502691896304, -0.3333333333333331), (-0.5773502691896304, -0.3333333333333331), (-0.5773502691896315, -0.3333333333333364), (-0.5773502691896275, -0.33333333333333653), (-0.5773502691896282, -0.3333333333333296), (-0.5773502691896304, -0.3333333333333331), (-0.5773502691896275, -0.33333333333333653), (0.5773502691896237, 0.33333333333333703), (0.5773502691896298, 0.33333333333333404), (0.5773502691896282, 0.33333333333333703), (0.5773502691896298, 0.33333333333333404), (0.5773502691896315, 0.33333333333333715), (0.5773502691896282, 0.33333333333333703), (0.5773502691896265, -0.3333333333333297), (0.5773502691896283, -0.3333333333333328), (0.57735026918963, -0.3333333333333297), (0.5773502691896261, -0.3333333333333369), (0.5773502691896283, -0.3333333333333328), (0.5773502691896265, -0.3333333333333297), (-0.5773502691896315, -0.3333333333333364), (-0.5773502691896297, -0.3333333333333397), (-0.5773502691896275, -0.33333333333333653), (1.1547005383792448, -3.469446951953614e-15), (0.8981004187394133, -2.040548799889688e-16), (0.898100418739415, -3.4416913763379853e-15), (-0.5773502691896304, 0.3333333333333336), (-0.5773502691896284, 0.33333333333333703), (-0.5773502691896322, 0.3333333333333371), (-1.0824674490095276e-15, -0.6666666666666702), (-5.329070518200751e-15, -0.6666666666666701), (-2.9467169445259364e-15, -0.6666666666666736), (-0.8981004187394143, 5.859510407743961e-17), (-1.1547005383792461, -3.2751579226442118e-15), (-0.8981004187394164, -3.2751579226442118e-15), (0.5773502691896276, 0.33333333333333015), (0.5773502691896298, 0.33333333333333404), (0.5773502691896237, 0.33333333333333703), (-0.5773502691896204, 0.9999999999999966), (-0.44905020936970713, 0.7777777777777743), (-0.4490502093697053, 0.7777777777777778), (-0.5773502691896283, 0.33333333333333015), (-0.5773502691896304, 0.3333333333333336), (-0.5773502691896322, 0.33333333333333015), (5.995204332975845e-15, 0.6666666666666701), (2.0261570199409107e-15, 0.6666666666666702), (3.9968028886505635e-15, 0.6666666666666666), (-1.0824674490095276e-15, -0.6666666666666702), (3.2751579226442118e-15, -0.6666666666666698), (1.304512053934559e-15, -0.6666666666666664), (-0.5773502691896284, 0.33333333333333703), (-0.5773502691896304, 0.3333333333333336), (-0.5773502691896283, 0.33333333333333015), (-2.3746436915593783e-16, 0.6666666666666736), (-2.248201624865942e-15, 0.6666666666666702), (2.0261570199409107e-15, 0.6666666666666702), (0.4490502093697072, 0.7777777777777743), (0.5773502691896202, 0.9999999999999964), (0.4490502093697051, 0.7777777777777778), (0.5773502691896237, 0.33333333333333703), (0.38490017945975064, 0.33333333333333703), (0.5773502691896276, 0.33333333333333015), (-0.5773502691896282, -0.3333333333333296), (-0.5773502691896275, -0.33333333333333653), (-0.384900179459754, -0.3333333333333365), (-0.5773502691896283, 0.33333333333333015), (-0.5773502691896242, 0.33333333333333703), (-0.5773502691896284, 0.33333333333333703), (3.9968028886505635e-15, 0.6666666666666666), (2.0261570199409107e-15, 0.6666666666666702), (-2.248201624865942e-15, 0.6666666666666702), (-0.5773502691896324, -0.3333333333333296), (-0.5773502691896304, -0.3333333333333331), (-0.5773502691896282, -0.3333333333333296), (-0.4811252243246915, 0.16666666666666527), (-0.5773502691896242, 0.33333333333333703), (-0.5773502691896283, 0.33333333333333015), (-5.329070518200751e-15, -0.6666666666666701), (-7.382983113757291e-15, -0.6666666666666664), (-9.43689570931383e-15, -0.66666666666667), (-0.5773502691896295, -0.9999999999999933), (-0.577350269189623, -0.9999999999999963), (-0.4490502093697104, -0.7777777777777739), (-1.1547005383792461, 3.858025010572419e-15), (-1.2303526253365504e-15, 1.5655879370690684e-16), (-1.1547005383792461, -3.2751579226442118e-15), (-0.8981004187394143, 5.859510407743961e-17), (-1.1547005383792461, 3.858025010572419e-15), (-1.1547005383792461, -3.2751579226442118e-15), (0.5773502691896276, 0.33333333333333015), (0.5773502691896318, 0.3333333333333304), (0.5773502691896298, 0.33333333333333404), (3.9968028886505635e-15, 0.6666666666666666), (-4.3298697960381105e-15, 0.6666666666666666), (-0.09622504486494107, 0.5000000000000018), (-0.577350269189623, -0.9999999999999963), (-0.5773502691896295, -0.9999999999999933), (-1.2303526253365504e-15, 1.5655879370690684e-16), (-1.2303526253365504e-15, 1.5655879370690684e-16), (1.154700538379245, 3.747002708109903e-15), (1.1547005383792448, -3.469446951953614e-15), (-2.248201624865942e-15, 0.6666666666666702), (-4.3298697960381105e-15, 0.6666666666666666), (3.9968028886505635e-15, 0.6666666666666666), (1.1547005383792448, -3.469446951953614e-15), (1.154700538379245, 3.747002708109903e-15), (0.8981004187394133, -2.040548799889688e-16), (0.5773502691896265, -0.3333333333333297), (0.5773502691896211, -0.33333333333333715), (0.5773502691896261, -0.3333333333333369), (-4.3298697960381105e-15, 0.6666666666666666), (-2.248201624865942e-15, 0.6666666666666702), (-6.494804694057166e-15, 0.6666666666666703), (-0.5773502691896265, 0.3333333333333408), (-0.5773502691896284, 0.33333333333333703), (-0.5773502691896242, 0.33333333333333703), (-7.382983113757291e-15, -0.6666666666666664), (-5.329070518200751e-15, -0.6666666666666701), (-1.0824674490095276e-15, -0.6666666666666702), (1.304512053934559e-15, -0.6666666666666664), (-7.382983113757291e-15, -0.6666666666666664), (-1.0824674490095276e-15, -0.6666666666666702), (-0.4490502093697104, -0.7777777777777739), (-0.577350269189623, -0.9999999999999963), (-0.4490502093697084, -0.7777777777777778), (-0.5773502691896295, -0.9999999999999933), (-0.4490502093697104, -0.7777777777777739), (-0.4490502093697147, -0.777777777777774), (-1.1547005383792461, 3.858025010572419e-15), (-0.8981004187394143, 5.859510407743961e-17), (-0.8981004187394164, 3.83026943495679e-15), (-7.382983113757291e-15, -0.6666666666666664), (1.304512053934559e-15, -0.6666666666666664), (0.09622504486493794, -0.5000000000000018), (0.577350269189626, 0.3333333333333408), (0.5773502691896237, 0.33333333333333703), (0.5773502691896282, 0.33333333333333703), (-0.5773502691896204, 0.9999999999999966), (-0.5773502691896267, 0.9999999999999921), (-0.44905020936970713, 0.7777777777777743), (-1.2303526253365504e-15, 1.5655879370690684e-16), (-0.5773502691896267, 0.9999999999999921), (-0.5773502691896204, 0.9999999999999966), (0.5773502691896162, -0.9999999999999967), (-1.2303526253365504e-15, 1.5655879370690684e-16), (0.5773502691896228, -0.9999999999999929), (0.44905020936970397, -0.7777777777777742), (0.5773502691896162, -0.9999999999999967), (0.5773502691896228, -0.9999999999999929), (0.5773502691896162, -0.9999999999999967), (0.44905020936970397, -0.7777777777777742), (0.4490502093697021, -0.7777777777777782), (0.5773502691896202, 0.9999999999999964), (0.5773502691896271, 0.9999999999999926), (-1.2303526253365504e-15, 1.5655879370690684e-16), (0.8981004187394133, -2.040548799889688e-16), (1.154700538379245, 3.747002708109903e-15), (0.8981004187394155, 3.83026943495679e-15), (0.5773502691896283, -0.3333333333333328), (0.5773502691896261, -0.3333333333333369), (0.5773502691896306, -0.3333333333333367), (0.4490502093697072, 0.7777777777777743), (0.5773502691896271, 0.9999999999999926), (0.5773502691896202, 0.9999999999999964), (-0.44905020936970713, 0.7777777777777743), (-0.5773502691896267, 0.9999999999999921), (-0.44905020936971174, 0.7777777777777745), (0.5773502691896271, 0.9999999999999926), (0.4490502093697072, 0.7777777777777743), (0.44905020936971185, 0.7777777777777745), (0.44905020936970397, -0.7777777777777742), (0.5773502691896228, -0.9999999999999929), (0.44905020936970863, -0.7777777777777743), (0.48112522432469007, -0.16666666666666446), (0.5773502691896211, -0.33333333333333715), (0.5773502691896265, -0.3333333333333297), (0.5773502691896261, -0.3333333333333369), (0.5773502691896211, -0.33333333333333715), (0.5773502691896236, -0.33333333333334136)]
    regress(pts)


def _test5():
    """Create some points on a line that is rotated in n steps around (0, 0)
    Independent from this rotation, the residuals found should be near zero
    """
#     import matplotlib.pyplot as plt
    from math import pi, cos, sin
    n = 800
    PI2 = 2.0*pi
    angle = PI2 / n
    pts = []
    r = 10.0
    for i in range(n):
        beta = i * angle
        x = r*cos(beta)
        y = r*sin(beta)
        pts.append((x, y))
    print (regress(pts))
    are_zero = are_residuals_near_zero(pts)


if __name__ == "__main__":
    _test1()
    _test2()
    _test3()
    _test4()
    _test5()
