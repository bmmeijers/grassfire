class Transform(object):
    """Transform coordinate systems: scale / translate"""

    def __init__(self, scale, translate):
        """Set up the parameters for the transform"""
        self.scale = scale
        self.translate = translate

    def forward(self, pt):
        """From the original box to (-1,-1),(1,1) box """
        return (pt[0] - self.translate[0]) / self.scale[0], \
            (pt[1] - self.translate[1]) / self.scale[1]

    def backward(self, pt):
        """From the (-1,-1),(1,1) box back to the original box"""
        return (pt[0] * self.scale[0]) + self.translate[0], \
            (pt[1] * self.scale[1]) + self.translate[1]


def get_transform(box):
    """Get a transform object for a bounding box to transform to (-1,-1),(1,1)
    """
    # target = ((-1.,-1.),(1.,1.))
    # tcx, tcy = (0., 0.)
    tdx, tdy = (2., 2.)
    (sxmin, symin), (sxmax, symax) = box
    scx, scy = (sxmin + sxmax) * 0.5, (symin + symax) * 0.5
    sdx, sdy = (sxmax - sxmin), (symax - symin)
    scale = max(sdx / tdx, sdy / tdy)
#    print("scale {}".format(scale))
    return Transform((scale, scale), (scx, scy))


def get_box(pts):
    """Returns tight fitting bounding box (axis aligned) around set of points
    """
    assert len(pts)
    it = iter(pts)
    ll = list(next(it))
    ur = list(ll[:])
    for pt in it:
        if pt[0] < ll[0]:
            ll[0] = pt[0]
        if pt[1] < ll[1]:
            ll[1] = pt[1]
        if pt[0] > ur[0]:
            ur[0] = pt[0]
        if pt[1] > ur[1]:
            ur[1] = pt[1]
    return tuple(ll), tuple(ur)


def _test_transform():
    box = ((70000., 100000.), (75000., 125000.))
    t = get_transform(box)

    assert t.forward(box[0]) == (-0.2, -1)
    assert t.forward((72500., 112500.)) == (0, 0)
    assert t.forward(box[1]) == (0.2, 1)

    assert t.backward((-0.2, -1)) == box[0]
    assert t.backward((0.2, 1)) == box[1]
    assert t.backward((0, 0)) == (72500, 112500)


def _test_box():
    pts = [(78000., 100000.), (75000., 125000.)]
    assert get_box(pts) == ((75000.0, 100000.0), (78000.0, 125000.0))

if __name__ == "__main__":
    _test_transform()
    _test_box()
