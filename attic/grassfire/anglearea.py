# -*- coding: utf-8 -*-

'''
Created on Oct 17, 2012

@author: martijn
'''
from math import pi, cos, sin, degrees
from predicates import orient2d

center = (0,0)
baseleg = (1,0)

pi2 = 2 * pi
degree_rad = pi2 / 360.

pt = (cos(degree_rad), sin(degree_rad))
area_degree = orient2d(center, baseleg, pt)

ct = int(pi2 / degree_rad)
for i in range(ct):
    angle = i * degree_rad
    pt = (cos(angle), sin(angle))
    
    # area = (base * altitude) * 0.5
    # 2 * area = (base * altitude)
    # 2 * area / base = altitude
    area = orient2d(center, baseleg, pt)
    base = 1. # by definition
    print "{0:5}°".format(degrees(angle)), "->", \
        "{0:8.5f}".format(area), abs(area) / base