px0, py0 = (0., 0.)

dx0, dy0 = (1., 1.)

px1, py1 = (10., 0.)

dx1, dy1 = (-1, 1.)

# see cpa_time at http://softsurfer.com/Archive/algorithm_0106/algorithm_0106.htm

#P = px0 - px1 + py0 - py1
#D = dx0 - dx1 + dy0 - dy1

#print P / D

def solve(px0, dx0, px1, dx1):
    try:
        print px1 - px0
        print dx0 - dx1
        return (px1 - px0) / (dx0 - dx1)
    except:
        pass

t = solve(px0, dx0, px1, dx1)
print "t =", t
t0 = solve(py0, dy0, py1, dy1)
print "t0 =", t0

def newpt(x, dx, t):
    return x + dx * t

if t is not None:
    x0 = newpt(px0, dx0, t)
    y0 = newpt(py0, dy0, t)
    
    x1 = newpt(px1, dx1, t)
    y1 = newpt(py1, dy1, t)
    
    print x0, y0, ";", x1, y1
    x0 = newpt(px0, dx0, t)
    y0 = newpt(py0, dy0, t)
    
    x1 = newpt(px1, dx1, t)
    y1 = newpt(py1, dy1, t)
    
    print x0, y0, ";", x1, y1


if t0 is not None:
    x0 = newpt(px0, dx0, t0)
    y0 = newpt(py0, dy0, t0)
    
    x1 = newpt(px1, dx1, t0)
    y1 = newpt(py1, dy1, t0)
    
    print x0, y0, ";", x1, y1


#(P_x, P_y)= \bigg(&\frac{(x_1 y_2-y_1 x_2)(x_3-x_4)-(x_1-x_2)(x_3 y_4-y_3 x_4)}{(x_1-x_2)(y_3-y_4)-(y_1-y_2)(x_3-x_4)}, \\
#                  &\frac{(x_1 y_2-y_1 x_2)(y_3-y_4)-(y_1-y_2)(x_3 y_4-y_3 x_4)}{(x_1-x_2)(y_3-y_4)-(y_1-y_2)(x_3-x_4)}\bigg)
x1 = px0
x2 = px0 + dx0
x3 = px1
x4 = px1 + dx1

y1 = py0
y2 = py0 + dy0
y3 = py1
y4 = py1 + dy1


Px = None
num = (x1 * y2-y1 * x2) * (x3-x4)-(x1-x2)* (x3 * y4-y3 * x4)
denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
print num
print denom
Px = num / denom
Py = None
num = (x1 * y2-y1 * x2) * (y3-y4)-(y1-y2) * (x3 * y4-y3 * x4)
denom = (x1-x2)*(y3-y4)-(y1-y2)*(x3-x4)
print num
print denom       
Py = num / denom
print Px, Py
