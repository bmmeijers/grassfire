'''
Created on Oct 13, 2012

@author: martijn
'''
import sys

def near(x, y, epsilon = 0.0001):
    """Returns whether x is near y, considering the 
    epsilon value as threshold
    """
    delta = abs(x - y) 
    threshold = epsilon * max((1.0, abs(x), abs(y),))
    # print >> sys.stderr, delta, threshold
    if delta <= threshold:
        return True
    else:
        return False

a = 4.93038065763e-32
b = 1e-7
print near(a, b)
