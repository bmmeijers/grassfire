# README

Grassfire - straight skeleton by means of kinetic triangulation

## Installation

The code in this package depends on a few other packages:

- [tri](https://github.com/bmmeijers/tri/)
- [geompreds](https://github.com/bmmeijers/predicates/)
- [oseq](https://github.com/bmmeijers/oseq/)

You can install them with pip (I'd suggest to make a virtualenv):

```
pip install -e git+https://github.com/bmmeijers/predicates/#egg=geompreds
pip install -e git+https://github.com/bmmeijers/tri/#egg=tri
pip install -e git+https://github.com/bmmeijers/oseq/#egg=oseq
```

After that you should be able to install grassfire:

```
pip install -e git+https://github.com/bmmeijers/grassfire/#egg=grassfire
```


## Examples

See:

- [https://vimeo.com/214460356](https://vimeo.com/214460356)
- [https://vimeo.com/214462766](https://vimeo.com/214462766)


## Usage

Example code for calculating the skeleton of a simple polygon:

```
#!python

from tri.delaunay.helpers import ToPointsAndSegments
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

with open("/tmp/input.wkt", "w") as fh:
    for line in lines:
        start, end = map(tuple, line)
        fh.write(f"LINESTRING({start[0]} {start[1]}, {end[0]} {end[1]})\n")
        conv.add_point(start)
        conv.add_point(end)
        conv.add_segment(start, end)

# produce the skeleton 
# note, this scales input to (-1,1)
skel = calc_skel(conv, internal_only=True)

# segments in the skeleton
print("segments")
with open("/tmp/skeleton.wkt", "w") as fh:
    for segment in skel.segments():
        (start, end), (start_info, end_info), = segment
        fh.write(f"LINESTRING({start[0]} {start[1]}, {end[0]} {end[1]})\n")

# the resulting WKT files can be opened in QGIS (via: Layer > Add Delimited Text Layer)
```


## Changelog

See `CHANGES.txt`.


## Bug reports

If you discover any bugs, feel free to create an issue on Github.

Please add as much information as possible to help us fixing the possible bug.
We also encourage you to help even more by forking and sending us a pull request.

The issue tracker lives [here](https://github.com/bmmeijers/grassfire/issues).


## Maintainers

- [Martijn Meijers](https://github.com/bmmeijers)


## License

[MIT License](https://www.tldrlegal.com/l/mit)
