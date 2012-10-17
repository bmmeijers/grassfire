'''
Created on Oct 12, 2012

@author: martijn
'''
from eventtime import collapse_time, shifted_point

#def shifted_point(pt, shift, t):
#    """Obtain resulting position, for given point at time t, when shift is
#    described by unit vector shift
#    """
#    return (pt[0] + shift[0] * t, pt[1] + shift[1] * t)

pa, shifta = (0., 0.), (0.5, 0.5)
pb, shiftb = (4., 0.), (-0.5, 0.5)
pc, shiftc = (0., 4.), (0.5, -0.5)
print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)

# print "--"
# for t in range(5):
#     print shifted_point(pa, pb, pc, shifta, shiftb, shiftc, t)

pa, shifta = (0., 0.), (-1., -1.)
pb, shiftb = (6., 0.), (1., -1.)
pc, shiftc = (3., 6.), (0., 1.)
print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)

#pa, shifta = (0., 0.), (0.5, 0.5)
#pb, shiftb = (4., 0.), (0.5, 0.5)
#pc, shiftc = (0., 4.), (0.5, -0.5)
#print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)


pa, shifta = (0., 0.), (0., 1.)
pb, shiftb = (4., 0.), (0., 1.)
pc, shiftc = (0., 4.), (0., 0.)
print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)

pa, shifta = (0., 0.), (1., 1.)
pb, shiftb = (10., 0.), (0., 1.)
pc, shiftc = (0., 4.), (1., -1.)
print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)

for t in range(5):
    print "at t =",t
    print shifted_point(pa, shifta, t)
    print shifted_point(pb, shifta, t)
    print shifted_point(pc, shifta, t)


pa, shifta = (0., 0.), (1., 0.)
pb, shiftb = (10., 0.), (1., 0.)
pc, shiftc = (-10., 0.), (1., 1.)
print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
