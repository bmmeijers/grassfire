'''
Created on Oct 12, 2012

@author: martijn
'''
import sys
from math import sqrt, copysign
from epsilon import near

def solve_linear(a, b):
    """Solves linear equation, defined by a and b
    
    Solves where y = 0.0 for y = a * x + b, if a and b are given
    x = -b / a
    
    Returns tuple with one element
    """
    # assert a != 0.
    if a == 0:
        return None
    else:
        return (-float(b) / float(a), )

def sign(x):
    """Sign function
    """
    if x == 0:
        return 0
    else:
        return copysign(1, x)

def discriminant(a, b, c):
    """Calculate discriminant
    """
    D = b**2 - 4.0*a*c
    # print >> sys.stderr, "D =", D
    return D

def solve_quadratic(a, b, c):
    """Solve quadratic equation, defined by a, b and c
    
    Solves  where y = 0.0 for y = a * x^2 + b * x + c, if a, b and c are given
    
    Returns tuple with two elements
    The result is a:
    (None, None) if imaginary solution
    (None, float) or (float, None) if only one root
    (float, float) if two roots (roots wil    print >> sys.stderr, "a =", a, ", b =", b, ", c =", cl be sorted from small to big)
    """
    x1, x2 = None, None

    a, b, c = float(a), float(b), float(c)
    D = discriminant(a, b, c)
    print >> sys.stderr, "a =", a, ", b =", b, ", c =", c, "D =", D
    #if near(D, 0):
    #    print >> sys.stderr, "making D 0"
    #    D = 0
    if D < 0:
        return (x1, x2)
    else:
        q = -0.5 * (b + sign(b) * D**0.5)
        # print >> sys.stderr, "q =", q
        # prevent division by zero if a == 0 or q == 0
        if a != 0: x1 = q / a
        if q != 0: x2 = c / q
        return tuple(sorted((x1, x2)))

def quadratic(x, a, b, c):
    """Returns y = a * x^2 + b * x + c for given x and a, b, c
    """
    a, b, c, x = float(a), float(b), float(c), float(x)
    return a * x**2 + b * x + c

def linear(x, a, b):
    """Returns y = a * x + b for given x and a, b
    """
    a, b, x = float(a), float(b), float(x)
    return a * x + b

if __name__ == "__main__":
    # some test cases for this module
    assert sign(1) == 1
    assert sign(2) == 1
    assert sign(-0) == 0
    assert sign(0) == 0
    assert sign(-1) == -1
    assert sign(-2) == -1
    
    def assert_almost_equal(a, b):
        digits = 7
        for ia, ib in zip(a, b):
            assert round(ia, digits) == round(ib, digits), "{} vs {}".format(a, b)

    # a = 1, b = 3, c = 2
    assert solve_quadratic(1, 3, 2) == (-2.0, -1.0)
    assert quadratic(-2.0, 1, 3, 2) == 0
    assert quadratic(-1.0, 1, 3, 2) == 0

    # a = 1, b = 4, c = 2
    expected = (-2. - 2 **0.5, -2. + 2 **0.5)
    result = solve_quadratic(1, 4, 2)
    assert_almost_equal(expected, result)
    print quadratic(expected[0], 1, 4, 2)
    print quadratic(expected[1], 1, 4, 2)


    # a = 3, b = 1, c = 6
    assert solve_quadratic(3, 1, 6) == (None, None)
    
    # linear 
    assert solve_linear(1.0, 1.0) == (-1.0, )
    assert solve_linear(0.5, 0.0) == (0.0, )
    
    result = solve_quadratic(1, 2, -7)
    # -1 +/- 2 * sqrt(2)
    expected = (-1. - 2 * sqrt(2), -1. + 2 * sqrt(2))  
    assert_almost_equal(expected, result)
    
    result = solve_quadratic(2, 6, 3)
    # -1 +/- 2 * sqrt(2)
    expected = (-3./2. - sqrt(3) / 2., -3./2. + sqrt(3) / 2.)  
    assert_almost_equal(expected, result)

    result = solve_quadratic(1, -6, 3)
    # -1 +/- 2 * sqrt(2)
    expected = (3. - sqrt(6), 3. + sqrt(6)) 
    assert_almost_equal(expected, result)
