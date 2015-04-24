'''
Created on Oct 14, 2012

@author: martijn
'''
from vector import Vector2
from math import sqrt

# px0, py0 = (0., 0.)
# dx0, dy0 = (1., 1.)

track0 = (Vector2(0., 0.), Vector2(1., 1.))
track1 = (Vector2(10., 0.), Vector2(-1, 1.))

def cpatime(track0, track1):
    dv = track0[1]-track1[1]
    print dv
    dv2 = dv.dot(dv)
    if dv2 < 0.00001:
        return 0.0
    w0 = track0[0] - track1[0]
    cpatime = -1 * w0.dot(dv) /dv2
    return cpatime

def cpadistsq(tr1, tr2):
    ctime = cpatime( tr1, tr2)
    p1 = tr1[0] + ctime * tr1[1]
    p2 = tr2[0] + ctime * tr2[1]
    print p1
    print p2
    print p1 == p2
    v = p1 - p2
    print v
    return sqrt(v.dot(v))
#    Point    P1 = Tr1.P0 + (ctime * Tr1.v);
#    Point    P2 = Tr2.P0 + (ctime * Tr2.v);
#
#    return d(P1,P2);           // distance at CPA


print cpatime(track0, track1)
print cpadistsq(track0, track1)

px1, py1 = (0., 5.)
dx1, dy1 = (-0.5, 1.)

#float
#cpa_time( Track Tr1, Track Tr2 )
#{
#    Vector   dv = Tr1.v - Tr2.v;
#
#    float    dv2 = dot(dv,dv);
#    if (dv2 < SMALL_NUM)      // the tracks are almost parallel
#        return 0.0;            // any time is ok.  Use time 0.
#
#    Vector   w0 = Tr1.P0 - Tr2.P0;
#    float    cpatime = -dot(w0,dv) / dv2;
#
#    return cpatime;            // time of CPA
#}
#//===================================================================
#
#// cpa_distance(): compute the distance at CPA for two tracks
#//    Input:  two tracks Tr1 and Tr2
#//    Return: the distance for which the two tracks are closest
#float
#cpa_distance( Track Tr1, Track Tr2 )
#{
#    float    ctime = cpa_time( Tr1, Tr2);
#    Point    P1 = Tr1.P0 + (ctime * Tr1.v);
#    Point    P2 = Tr2.P0 + (ctime * Tr2.v);
#
#    return d(P1,P2);           // distance at CPA
#}