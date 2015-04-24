'''
Created on Oct 12, 2012

@author: martijn
'''

from angles import bisector

print bisector(#(5.42, 9.54), (4.5, 0.54), (8.55, 0.54))
    (5.409501243788791, 9.547506218943957),
    (4.5, 0.4524937810560443),
    (8.547506218943955, 0.4524937810560443))

print bisector(#(5.42, 9.54), (4.5, 0.54), (8.55, 0.54))
               

    (0.4524937810560443, 0.4524937810560443),
               (4.5, 0.4524937810560443),    
    (3.590498756211209, 9.547506218943955),
    
    
    )


print bisector(
               (6.90025,   2.09975),
               (6.90024875776, 7.90024875776),
               (6.32020,   2.09975),
               )

print bisector(
                              (2.67980,   2.09975),
               (2.09975124224, 7.90024875776),
               (2.09975, 2.09975),
               
               )
#from eventtime import collapse_time
#
##def shifted_point(pt, shift, t):
##    """Obtain resulting position, for given point at time t, when shift is
##    described by unit vector shift
##    """
##    return (pt[0] + shift[0] * t, pt[1] + shift[1] * t)
#
#pa, shifta = (0., 0.), (0.5, 0.5)
#pb, shiftb = (4., 0.), (-0.5, 0.5)
#pc, shiftc = (0., 4.), (0.5, -0.5)
#print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
#
## print "--"
## for t in range(5):
##     print shifted_point(pa, pb, pc, shifta, shiftb, shiftc, t)
#
#pa, shifta = (0., 0.), (-1., -1.)
#pb, shiftb = (6., 0.), (1., -1.)
#pc, shiftc = (3., 6.), (0., 1.)
#print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
#
##pa, shifta = (0., 0.), (0.5, 0.5)
##pb, shiftb = (4., 0.), (0.5, 0.5)
##pc, shiftc = (0., 4.), (0.5, -0.5)
##print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
#
#
#pa, shifta = (0., 0.), (0., 1.)
#pb, shiftb = (4., 0.), (0., 1.)
#pc, shiftc = (0., 4.), (0., 0.)
#print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
#
#pa, shifta = (0., 0.), (1., 1.)
#pb, shiftb = (10., 0.), (0., 1.)
#pc, shiftc = (0., 4.), (1., -1.)
#print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
#
#for t in range(5):
#    print "at t =",t
#    print shifted_point(pa, shifta, t)
#    print shifted_point(pb, shifta, t)
#    print shifted_point(pc, shifta, t)
#
#
#pa, shifta = (0., 0.), (1., 0.)
#pb, shiftb = (10., 0.), (1., 0.)
#pc, shiftc = (-10., 0.), (1., 1.)
#print collapse_time(pa, pb, pc, shifta, shiftb, shiftc)
