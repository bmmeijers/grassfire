from predicates import orient2d

__license__ = "MIT license"

NOT_INTERSECTING = 2
INTERSECTING_AT_END = 4
INTERSECTING = 8
FULL_OVERLAP = 16
PARTLY_OVERLAP = 32

def coincident(a, b):
    if a[0] == b[0] and a[1] == b[1]:
        return True
    else:
        return False

def _envelope_overlap(one, other): 
    if (other[2] < one[0] or \
        other[3] < one[1] or \
        other[0] > one[2] or \
        other[1] > one[3]):
        return False
    else:
        return True
    
def _envelope(pa, pb):
    return (min(pa[0], pb[0]), # xmin
            min(pa[1], pb[1]), # ymin
            max(pa[0], pb[0]), # xmax
            max(pa[1], pb[1])) # ymax

def intersecting(pa, pb, qa, qb):
    """Returns how two segment are intersecting with each other
        
        FULL_OVERLAP
        INTERSECTING_AT_END
        NOT_INTERSECTING
    """
    envp = _envelope(pa, pb)
    envq = _envelope(qa, qb)
    if not _envelope_overlap(envp, envq):
        return NOT_INTERSECTING
    else:
        a = orient2d(pa, pb, qa)
        b = orient2d(pa, pb, qb)
        
        if (a > 0 and b > 0) or (a < 0 and b < 0):
            return NOT_INTERSECTING
        
        c = orient2d(qa, qb, pa)
        d = orient2d(qa, qb, pb)
        
        if (c > 0 and d > 0) or (c < 0 and d < 0):
            return NOT_INTERSECTING
        
        elif a == 0. and b == 0. and c == 0. and d == 0.:

            if envp == envq:
                return FULL_OVERLAP
            elif (envq[0] > envp[0] and envq[0] < envp[2]) or \
                 (envq[2] > envp[0] and envq[2] < envp[2]) or \
                 (envq[1] > envp[1] and envq[1] < envp[3]) or \
                 (envq[3] > envp[1] and envq[3] < envp[3]):
                return PARTLY_OVERLAP
            else:
                return INTERSECTING_AT_END
    
        elif a == 0 or b == 0 or c == 0 or d == 0:
            return INTERSECTING_AT_END
        
        else:
            return INTERSECTING
