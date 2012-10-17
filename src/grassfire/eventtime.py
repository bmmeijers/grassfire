'''
Created on Oct 12, 2012

@author: martijn
'''

from solver import solve_quadratic, solve_linear, quadratic

class Track(object):
    __slots__ = ["position", "velocity"]
    def __init__(self, position, velocity):
        self.position, self.velocity = position, velocity
    def __str__(self):
        return "<p:{}, v:{}>".format(self.position, self.velocity)

def position(track, t):
    """Obtain resulting position, for given track at time t
    """
    pt, shift = track.position, track.velocity
    result = (float(pt[0]) + shift[0] * t, 
              float(pt[1]) + shift[1] * t)
    print pt, 'with', shift, 'at', t, "=", result
    return result

def collapse_time(tracka, trackb, trackc):
    """Returns time(s) when triangle collapses if vertices are shifted
    in direction of movement vectors shifta, shiftb, shiftc
    """
    pa = tracka.position
    shifta = tracka.velocity
    
    pb = trackb.position
    shiftb = trackb.velocity
    
    pc = trackc.position
    shiftc = trackc.velocity

    xaorig, yaorig = pa[0], pa[1]
    xborig, yborig = pb[0], pb[1]
    xcorig, ycorig = pc[0], pc[1]
    
    dxa, dya = shifta[0], shifta[1]
    dxb, dyb = shiftb[0], shiftb[1]
    dxc, dyc = shiftc[0], shiftc[1]

#    area = .5 *(xaorig + dxa *t) *(yborig + dyb *t) - 0.5 *(xborig + dxb *t) *(yaorig + dya *t)  + 0.5 *(xborig + dxb *t) *(ycorig + dyc *t)  - 0.5 *(xcorig + dxc *t) *(yborig + dyb *t) + 0.5 *(xcorig + dxc *t)* (yaorig + dya *t) - 0.5 *(xaorig + dxa *t)* (ycorig + dyc *t)
#        C                           B               B                               A
#  0.5 * xaorig * yborig + 0.5 * xaorig * dyb * t + 0.5 * dxa * t * yborig + 0.5 * dxa * pow(t,2) * dyb \
#- 0.5 * xborig * yaorig - 0.5 * xborig * dya * t - 0.5 * dxb * t * yaorig - 0.5 * dxb * pow(t,2) * dya \
#+ 0.5 * xborig * ycorig + 0.5 * xborig * dyc * t + 0.5 * dxb * t * ycorig + 0.5 * dxb * pow(t,2) * dyc \
#- 0.5 * xcorig * yborig - 0.5 * xcorig * dyb * t - 0.5 * dxc * t * yborig - 0.5 * dxc * pow(t,2) * dyb \
#+ 0.5 * xcorig * yaorig + 0.5 * xcorig * dya * t + 0.5 * dxc * t * yaorig + 0.5 * dxc * pow(t,2) * dya \
#- 0.5 * xaorig * ycorig - 0.5 * xaorig * dyc * t - 0.5 * dxa * t * ycorig - 0.5 * dxa * pow(t,2) * dyc

    A = 0.5 * dxa * dyb - \
        0.5 * dxb * dya + \
        0.5 * dxb * dyc - \
        0.5 * dxc * dyb + \
        0.5 * dxc * dya - \
        0.5 * dxa * dyc

    B = 0.5 * xaorig * dyb - \
        0.5 * xborig * dya + \
        0.5 * xborig * dyc - \
        0.5 * xcorig * dyb + \
        0.5 * xcorig * dya - \
        0.5 * xaorig * dyc + \
        0.5 * dxa * yborig - \
        0.5 * dxb * yaorig + \
        0.5 * dxb * ycorig - \
        0.5 * dxc * yborig + \
        0.5 * dxc * yaorig - \
        0.5 * dxa * ycorig

    C = 0.5 * xaorig * yborig - \
        0.5 * xborig * yaorig + \
        0.5 * xborig * ycorig - \
        0.5 * xcorig * yborig + \
        0.5 * xcorig * yaorig - \
        0.5 * xaorig * ycorig
    print "coefficients", A, B, C
    if A == 0:
        # special case... 
        # solve linear system
        return solve_linear(B, C)

    return solve_quadratic(A, B, C)


if __name__ == "__main__":
    pa, pb, pc = (0,0), (10,0), (5,10)
    sa, sb, sc = (1,1), (0,0), (0,0)
    
    ta = Track(pa, sa)
    tb = Track(pb, sb)
    tc = Track(pc, sc)
    t = collapse_time(ta, tb, tc)
    print t
    print position(ta, t[0])

#
#    if A == 0.:
#        if B == 0.:
#            print A, B, C
#            raise NotImplementedError("")
#        else:
#            result = solve_linear(B, C)
#    else:
#        result = solve_quadratic(A, B, C)
#
#    if result:
#        if len(result) == 1:
#            t = result[0]
#            print "t =", t
#            print "qp =", quadratic(A, B, C, t)
#            xa = xaorig + dxa * t
#            ya = yaorig + dya * t
#            
#            xb = xborig + dxb * t
#            yb = yborig + dyb * t
#            
#            xc = xcorig + dxc * t
#            yc = ycorig + dyc * t
#            return (xa, ya), (xb, yb), (xc, yc)
#        elif len(result) == 2:
#            print result
#            return None