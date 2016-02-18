
from math import sqrt 

from operator import add, sub, mul, truediv

orig = (0,0)
dest = (5,0)
apex = (2.5, sqrt(3.)/2. * 5.)

# -- get vectors
dx = orig[0] - dest[0]
dy = orig[1] - dest[1]

a = (dx, dy)

dx = dest[0] - apex[0]
dy = dest[1] - apex[1]

b = (dx,dy)

dx = apex[0] - orig[0]
dy = apex[1] - orig[1]

c = (dx,dy)

print a
print b
print c

def rotate90ccw(v):
    """Rotate 2d vector 90 degrees counter clockwise
    """
    return (-(v[1]), v[0])

def rotate90cw(v):
    """Rotate 2d vector 90 degrees clockwise
    """
    return (v[1], -v[0])

def normalize(v, length):
	"""Normalize vector by a length (e.g. to obtain unit vector)"""
	out = []
	for i in range(len(v)):
		out.append(v[i] / length)
	return out

# get 3 vectors pointing around triangle
down = rotate90ccw(normalize(a, 5.))
right = rotate90ccw(normalize(b, 5.))
left = rotate90ccw(normalize(c, 5.))

# -- first segment
print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format( map(add, down, orig), map(add, down, dest) )

# -- second segment
print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format( map(add, right, dest), map(add, right, apex) )

# -- third segment
print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format( map(add, left, apex), map(add, left, orig))

