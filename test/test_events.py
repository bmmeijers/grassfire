import unittest

from oseq import OrderedSequence

from grassfire.primitives import Event
from grassfire.events import compare_event_by_time

class TestSplice(unittest.TestCase):

    def test_ordering(self):
        class TriMock(object):
            def __init__(self, id, tp):
                self.id = id
                self.type = tp
        tri1 = TriMock("1", 1)
        tri2 = TriMock("2", 2)
        tri3 = TriMock("3", 3)
        ea = Event(when = 1, tri = tri1)
        eb = Event(when = 1, tri = tri2)
        ec = Event(when = 2, tri = tri3)
        L = [ec, eb, ea]
        #for e in L:
        #    print e
        #print "--"
        #L.sort(cmp=compare_event_by_time)
        #for e in L:
        #    print e
        #print ""
        queue = OrderedSequence(cmp=compare_event_by_time)
        for e in L: queue.add(e)
        queue.remove(ec)
        queue.remove(Event(when=1, tri=tri1))
        while queue:
            e = queue.popleft()
            assert e.triangle is tri2
        assert len(queue) == 0

if __name__ == '__main__':
    unittest.main()