'''
Created on Oct 12, 2012

@author: martijn
'''
from math import pi, cos, sin, radians, degrees

def ngon(n, radius = 1.0, direction = 0.0):
    """Returns list of points of a regular n-gon
    
    :param n: the n in n-gon (number of points / sides)
    :type n: integer
    
    :param radius: the radius of the n-gon from the center
    :type radius: float 
    
    :param direction: angle with the x-axes for rotation of the n-gon
    :type direction: float
    """
    assert n > 2
    print degrees(direction)
    ring = []
    for i in range(n):
        t = 2 * pi * (float(i) / float(n)) + direction
        x = cos(t) * radius
        y = sin(t) * radius
        pt = (x, y)
        ring.append(pt)
    return ring

def _test():
    N = 7
    shape = ngon(N, radius = 1., direction = -pi / N)
    print shape
    print len(shape)
    
    fh = open('/tmp/shape.wkt', 'w')
    fh.write('#x,y\n')
    for pt in shape:
        fh.write("{0:.3f},{1:.3f}\n".format(pt[0], pt[1]))
    fh.close()

if __name__ == "__main__":
    _test()