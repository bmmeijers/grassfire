import unittest

from tri.delaunay.helpers import ToPointsAndSegments

from grassfire import calc_skel, calc_offsets
from grassfire.events import at_same_location
from grassfire.test.intersection import segments_intersecting
from grassfire.vectorops import dist

import fixtures


def all_tests():
    """Find all functions inside the *fixtures* module
    and returns a list with all function objects"""
    import inspect

    all_functions = inspect.getmembers(fixtures, inspect.isfunction)
    return [fn for fn_nm, fn in sorted(all_functions)]


def make_test_cases(fixtures):
    """For all functions in the list, make
    an entry in the cases dictionary, by
    invoking the function.
    """
    cases = {}
    for i, f in enumerate(fixtures):
        data, total, node, infinite, = f()
        assert f.__name__ not in cases, "duplicate test name ({}) found".format(
            f.__name__
        )
        cases[f.__name__] = (
            "* {:>2d}: ".format(i) + str(f.__doc__),
            data,
            total,
            node,
            infinite,
        )
    return cases

EXPENSIVE_POST_CONDITION = True

CASES = make_test_cases(all_tests())
INTERACTIVE = False

# CASES = make_test_cases([all_tests()[48]])
# INTERACTIVE = True

# After: https://stackoverflow.com/a/20870875
class TestSequenceMeta(type):
    """A meta class for all our TestCases"""

    def __new__(mcs, name, bases, dict):
        def gen_test(description, data, total, node, infinite):
            def test(self):
                if INTERACTIVE:
                    skel = calc_skel(
                        data, pause=True, output=True, internal_only=False, shrink=True
#                        data, pause=False, output=False, internal_only=False, shrink=True
                    )
                else:
                    skel = calc_skel(data)
                # check the amount of segments in the skeleton
                self.assertEqual(len(skel.segments()), total)
                # check the amount of skeleton nodes
                self.assertEqual(len(skel.sk_nodes), node)
                # # check the amount of kinetic vertices that are (not) stopped
                not_stopped = [v for v in skel.vertices if v.stops_at is None]
                stopped = [v for v in skel.vertices if v.stops_at is not None and v.start_node is not v.stop_node]
                self.assertEqual(len(not_stopped), infinite)
                self.assertEqual(len(stopped), total - infinite)
                # check cross relationship between kinetic vertices and skeleton nodes
                for v in skel.vertices:
                    # exact same starting location
                    if abs(v.velocity[0]) < 100 and abs(v.velocity[1]) < 100: # check only 'slow' moving vertices
                        self.assertTrue(at_same_location([v.start_node, v], v.starts_at), "{} [{}] {} does not have correct start_node(!) position".format(id(v), v.info, v.velocity))
                    # quite close at the stop node (given the vertex + its direction/speed)
                    if True and v.stops_at is not None and not v.inf_fast and (abs(v.velocity[0]) < 100 and abs(v.velocity[1]) < 100):
                        d = dist(
                                v.stop_node.position_at(v.stops_at),
                                v.position_at(v.stops_at),
                            )
                        self.assertAlmostEqual(
                            d,
                            0.0,
                            2,
                            "{} [{}] velocity '{}' does not have correct stop_node position -- dist: {}".format(id(v), v.info, v.velocity, d)
                        )

                        # self.assertTrue(at_same_location([v.stop_node, v], v.stops_at),
                        #     '{} != {}; {}'.format(v.stop_node.position_at(v.stops_at), v.position_at(v.stops_at),
                        #     dist(v.stop_node.position_at(v.stops_at), v.position_at(v.stops_at)))
                        #     )
                if EXPENSIVE_POST_CONDITION == True:
                    # check that we do not have any self intersections between segments
                    self.assertFalse(
                        segments_intersecting(skel.segments()),
                        "intersection between straight skeleton segments found",
                    )
                    # offset segments should not intersect
                    # (FIXME: these use left_at of kinetic vertices, also check right_at)
                    last_evt_time = max(v.stops_at for v in skel.vertices if v.stops_at is not None)
                    offset_segments = [
                        (line[0], line[1]) for line in calc_offsets(skel, last_evt_time, 25)
                    ]
                    self.assertFalse(
                        segments_intersecting(offset_segments),
                        "Intersection in offsets found",
                    )
                # with open("/tmp/offsets.wkt", "w") as fh:
                #     for segment in offset_segments:
                #         s = "LINESTRING({0[0]} {0[1]}, {1[0]} {1[1]})".format(segment[0], segment[1])
                #         fh.write(s)
                #         fh.write("\n")

            # set the docstring of the test function
            test.__doc__ = description
            return test

        for tname in CASES:
            test_name = "test_%s" % tname
            dict[test_name] = gen_test(*CASES[tname])
        return type.__new__(mcs, name, bases, dict)


class GrassfireTestCase(unittest.TestCase, metaclass=TestSequenceMeta):
    pass


if __name__ == "__main__":
    if INTERACTIVE:
        import logging
        import sys

        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(message)s")
        ch.setFormatter(formatter)
        root.addHandler(ch)

#    import cProfile
#    command = """unittest.main(verbosity=10)"""
#    cProfile.runctx( command, globals(), locals(), filename="/tmp/gf.profile" )

    unittest.main()
