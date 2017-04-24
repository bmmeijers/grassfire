README
======

Grassfire - straight skeleton by means of kinetic triangulation


Installation
------------

- Download the source
- Run `python setup.py install` (or `python setup.py develop`)

Note, the code in this package depends on a few other packages:

- tri, https://bitbucket.org/bmmeijers/tri/
- geompreds, https://bitbucket.org/bmmeijers/predicates/
- oseq, https://bitbucket.org/bmmeijers/oseq/


Examples
--------
See:

- https://vimeo.com/214460356
- https://vimeo.com/214462766


Usage
-----

Example code for calculating the skeleton of a simple polygon:

```
#!python

from tri import ToPointsAndSegments
from grassfire import calc_skel

# input that will be triangulated and 
# for which a straight skeleton is constructed
conv = ToPointsAndSegments()
lines = [
    [[51046.4, 391515.7], [51046.3, 391516.65]],
    [[51047.95, 391513.05], [51047.55, 391515.85]],
    [[51047.55, 391515.85], [51046.4, 391515.7]],
    [[51047.45, 391516.8], [51046.9, 391520.8]],
    [[51046.3, 391516.65], [51047.45, 391516.8]],
    [[51055, 391521], [51057, 391514]],
    [[51046.9, 391520.8, ], [51055, 391521]],
    [[51047.95, 391513.05], [51057, 391514]]]
for line in lines:
    start, end = map(tuple, line)
    conv.add_point(start)
    conv.add_point(end)
    conv.add_segment(start, end)

# produce the skeleton 
# note, this scales input to (-1,1)
skel = calc_skel(conv)

# nodes produced
print "nodes"
for node in skel.sk_nodes:
    print node.pos

# segments in the skeleton
print "segments"
for segment in skel.segments():
    print segment
```



Changelog
---------
See `CHANGES.txt`.


Bug reports
-----------
If you discover any bugs, feel free to create an issue on Bitbucket.

Please add as much information as possible to help us fixing the possible bug.
We also encourage you to help even more by forking and sending us a pull
request.

The issue tracker lives `here <https://bitbucket.org/bmmeijers/grassfire/issues>`_.


Maintainers
-----------

- `Martijn Meijers <https://bitbucket.org/bmmeijers>`_


License
-------

`MIT License <https://www.tldrlegal.com/l/mit>`_
