from math import cos, sin, pi

N = 20
inc = 2*pi / N

pts = []
for i in range(N):
	if i %2:
		pt = cos(i * inc), sin(i *inc)
	else:
		pt = 2*cos(i * inc), 2*sin(i *inc)
	pts.append(pt)
for n in range(len(pts)):
	#print n, n+1
	print "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(pts[n], pts[(n+1)%len(pts)])