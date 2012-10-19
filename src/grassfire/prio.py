'''
Created on Oct 19, 2012

@author: martijn
'''

class PriorityQueue(object):
    """A PriorityQueue
    
    Objects can be removed directly (this is inefficient though)
    """
    def __init__(self):
        """Constructs a PriorityQueue"""
        self.prio_object = {}
        self.ct = 0
        # FIXME:
        # keep also a dict for object -> prio
        # then searching if an object is there is also fast...
    
    def __contains__(self, val):
        """Returns True when *val* is contained in the PriorityQueue,
        False otherwise"""
        for lst in self.prio_object.itervalues():
            for item in lst:
                if item is val:
                    return True
        else:
            return False
        
    def __len__(self):
        """Returns how many elements are in the PriorityQueue"""
        return self.ct

    def remove(self, obj):
        """Removes *obj* from the PriorityQueue
        
        It is an error when *obj* is not found
        """
        found = False
        for prio, lst in self.prio_object.iteritems():
            for i, item in enumerate(lst):
                if item is obj:
                    self.prio_object[prio].pop(i)
                    self.ct -= 1
                    found = True
                    break
        if not found:
            raise ValueError("Item ({}) not found".format(obj))
        else:
            if not self.prio_object[prio]:
                self.prio_object.pop(prio)
    
    def discard(self, val):
        """Removes *obj* from the PriorityQueue, even if it was not added 
        before
        """
        try:
            self.remove(val)
            return True
        except ValueError:
            return False

    def add(self, prio, obj):
        """Adds the *obj* to the PriorityQueue with given *prio*"""
        if prio in self.prio_object:
            self.prio_object[prio].append(obj)
        else:
            self.prio_object[prio] = [obj]
        self.ct += 1

    def pop(self):
        """Pops the most important object from the PriorityQueue
        """
        return self._pop()
        
    def popleft(self):
        """Pops the least important object from the PriorityQueue
        """
        return self._pop(False)

    def _pop(self, right = True):
        """Low level implementation for pop and popleft"""
        for prio in sorted(self.prio_object.iterkeys(), reverse = right):
            self.ct -= 1
            lst = self.prio_object[prio]
            if len(lst) > 1:
                lst.sort()
                if not right:
                    lst.reverse()
                item = lst.pop()
            else:
                assert len(lst) == 1
                item = self.prio_object.pop(prio)[0]
            return (prio, item) 
        raise ValueError("Empty queue")

def _test():
    pq = PriorityQueue()
    pq.add(1, 2)
    pq.add(1, 3)
    assert 3 in pq
    pq.add(1, 1)
    pq.add(1, 1)
    assert len(pq) == 4
    assert pq.popleft() == (1, 1)
    assert pq.popleft() == (1, 1)
    pq.remove(3)
    pq.discard(4)
    assert len(pq) == 1
    pq.add(2,6)
    pq.add(2,4)
    val = pq.pop()
    assert val == (2,6)
    assert pq.pop() == (2,4)
    assert len(pq)
    pl = pq.popleft()
    assert pl == (1,2)

if __name__ == "__main__":
    _test()