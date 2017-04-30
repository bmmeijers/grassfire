import logging

from random import shuffle
from collections import deque

from oseq import OrderedSequence

from grassfire.regression import are_residuals_near_zero
from grassfire.calc import near_zero
from grassfire.collapse import compute_collapse_time, find_gt

from grassfire.events.flip import handle_flip_event
from grassfire.events.edge import handle_edge_event, handle_edge_event_3sides
from grassfire.events.split import handle_split_event

from grassfire.inout import visualize


def choose_next_event(queue):
    """Choose a next event from the queue

    In case there are multiple events happening more or less at the same time
    we pick a non-flipping event first. In case we have all flip events,
    we pick a random event (to break possible flip event loops).
    """
    def sort_key(evt):
        """Key for sorting; first by event type, when these equal by time"""
        types = {'flip': 2, 'split': 0, 'edge': 1}
        x = evt.triangle.vertices[0].position_at(evt.time)[0]
        return (types[evt.tp], -x, evt.time)
    it = iter(queue)
    first = next(it)
    events = [first]
    for e in it:
        if near_zero(e.time - first.time):
            events.append(e)
#         else:
#             break
    logging.debug("Events to pick next event from:\n - " + "\n - ".join(map(str, events)))
    if len(events) == 1:
        # just one event happening now
        item = events[0]
    elif all([_.tp == 'flip' for _ in events]):
        logging.debug("Only flip events, picking randomly an event")
        # only flip events happening, pick random event
        # FIXME: introduce some bias to pick longest flip?
        shuffle(events)
        item = events[0]
    else:
        pts = []
        for evt in events:
            pts.extend([v.position_at(first.time) for v in evt.triangle.vertices])
        on_straight_line = are_residuals_near_zero(pts)
#         print pts
#         for pt in pts:
#             print "POINT({0[0]} {0[1]})".format(pt)
#         metric = r_squared(pts)
#         logging.debug('metric {0}'.format(metric))
#         import numpy as np
#         x = np.array([pt[0] for pt in pts])
#         y = np.array([pt[1] for pt in pts])
#         A = np.vstack([x, np.ones(len(x))]).T
#         res = np.linalg.lstsq(A, y)
#         print res
        if not on_straight_line:
            logging.debug('pick first event')
            # points should be on straight line to exhibit infinite flipping
            # if this is not the case, we return the first event
            item = events[0]
        else:
            logging.debug('pick non-flip event')
            # return the first item, sorted on type (non-flipping events first)
            for item in sorted(events, key=sort_key):
                break
    queue.remove(item)
    return item


def make_frames(now, digits, skel, queue, immediate):
    import random
    import time
    if immediate:
        return
    else:
        scale = pow(10, digits)
        N = round(now, digits)
        try:
            peek = next(iter(queue))
            T = round(peek.time, digits)
        except StopIteration:
            T = N + 0.2
        # print T, N
        delta = T-N
        # print delta
        times = int(delta * scale)
        # print times
        for t in range(1, times):
            print "."
            cur = N + float(t) / float(scale)
#             print N + TIME / scale
            time.sleep(0.25)
            visualize(queue, skel, cur) # N + TIME / scale)
            time.sleep(0.5)
            with open("/tmp/signal", "w") as fh:
                # FIXME -- write a number for the frames to the file
                fh.write("{0}".format(random.randint(0, int(1e6))))
            time.sleep(0.25)


# Main event loop
# -----------------------------------------------------------------------------
def event_loop(queue, skel, pause=False):
    """ The main event loop """
    STOP_AFTER = 1
    VIDEO_DIGITS = 3
    make_video = False
    # -- clean out files for visualization
    if pause:
        for file_nm in [
            "/tmp/sknodes_progress.wkt",
            "/tmp/bisectors_progress.wkt",
            "/tmp/segments_progress.wkt",
            '/tmp/queue.wkt',
            # also contains next triangle to be visualised!
            "/tmp/vertices0_progress.wkt",
            "/tmp/vertices1_progress.wkt",
            '/tmp/ktri_progress.wkt',
        ]:
            with open(file_nm, 'w') as fh:
                pass
    # -- visualize
    NOW = prev_time = 0. #= 5e-6
    if pause:
        visualize(queue, skel, prev_time)
        raw_input('paused at start')
    immediate = deque([])
    logging.debug("=" * 80)
    logging.debug("Immediate / Queue at start of process")
    logging.debug("=" * 80)
    for i, e in enumerate(immediate):
        logging.debug("{0:5d} {1}".format(i, e))
    logging.debug("-" * 80)
    for i, e in enumerate(queue):
        logging.debug("{0:5d} {1}".format(i, e))
    logging.debug("=" * 80)
    ct = 0
    if make_video:
        make_frames(NOW, VIDEO_DIGITS, skel, queue, immediate)
#     step = prev = 0.025
#     FILTER_CT = 220
    while queue or immediate:
        #         if len(queue) < FILTER_CT:
        #             pause = True
        ct += 1
        logging.debug("")
        logging.debug("STEP := " + str(ct))
        logging.debug("")

        logging.debug("=" * 80)
        for i, e in enumerate(immediate):
            logging.debug("{0:5d} {1}".format(i, e))
        logging.debug("-" * 80)
        for i, e in enumerate(queue):
            logging.debug("{0:5d} {1}".format(i, e))
        logging.debug("=" * 80)

        #         if parallel:
        #             evt = parallel.popleft()
        #             # print edge, direction, now
        #             handle_parallel_event(evt, skel, queue, immediate, parallel)
        #             visualize(queue, skel, now)
        #             raise NotImplementedError("stop here")
        #         else:
        if immediate:
            evt = immediate.popleft()
        else:
            evt = choose_next_event(queue)
            NOW = evt.time
#             peek = next(iter(queue))
#             NOW = peek.time
#             if pause and False:  # visualize progressively
#                 #                 if peek.tp == "flip":
#                 #                     ct = 2
#                 #                 else:
#                 ct = 10
#                 # -- use this for getting progress visualization
#                 delta = NOW - prev_time
#                 if near_zero(delta):
#                     ct = 1
#                 step_time = delta / ct
#                 for i in range(ct - 1):  # ct - 2): # stop 1 step before
#                     print "."
#                     prev_time += step_time
#                     visualize(queue, skel, prev_time + step_time)
#                     sleep(0.5)
#             if pause and False:  # and (ct % 10) == 0:
#                 visualize(queue, skel, NOW)
#                 # import random
#                 # with open("/tmp/signal", "w") as fh:
#                 #    fh.write("{}".format(random.randint(0,1000)))
#                 os.system("touch /tmp/signal")
#                 sleep(2.)
# #             if NOW > prev:
# #                 visualize(queue, skel, NOW)
# #                 prev += step
#            ##evt = queue.popleft()
#            #prev_time = NOW
        if pause and ct >= STOP_AFTER: # (ct % STOP_AFTER == 0):
            visualize(queue, skel, NOW - 5e-3)
            raw_input('before event')
        # -- decide what to do based on event type
        logging.debug("Handling event " +
                      str(evt.tp) +
                      " " +
                      str(evt.triangle.type) +
                      " " +
                      str(id(evt.triangle)) +
                      " at time " +
                      "{0:.28g}".format(evt.time))
        # precondition: this triangle has not yet been dealt with before
        if evt.triangle.stops_at is not None:
            logging.warn("Already stopped {}, but queued".format(
                                                             id(evt.triangle)))
            assert evt.triangle.stops_at is None, "already stopped {}".format(id(evt.triangle))
            continue
        if evt.tp == "edge":
            if len(evt.side) == 3:
                handle_edge_event_3sides(evt, skel, queue, immediate)
            else:
                handle_edge_event(evt, skel, queue, immediate)
        elif evt.tp == "flip":
            handle_flip_event(evt, skel, queue, immediate)
        elif evt.tp == "split":
            handle_split_event(evt, skel, queue, immediate)

#         check_ktriangles(skel.triangles, NOW)
        if pause and ct >= STOP_AFTER:
            visualize(queue, skel, NOW)
            raw_input('after event')

        if False:  # len(queue) < FILTER_CT:
            logging.debug("=" * 80)
            logging.debug("Immediate / Queue at end of handling event")
            logging.debug("=" * 80)
            for i, e in enumerate(immediate):
                logging.debug("{0:5d} {1}".format(i, e))
            logging.debug("-" * 80)
            for i, e in enumerate(queue):
                if i > 5 and i < len(queue) - 5:
                    continue
                logging.debug("{0:5d} {1}".format(i, e))
                logging.debug(repr(e.triangle))
                if i == 5 and len(queue) > 5:
                    logging.debug("...")
        logging.debug("=" * 80)
        if make_video:
            make_frames(NOW, VIDEO_DIGITS, skel, queue, immediate)
            # raw_input("paused...")
        if False and not immediate:
            # if we have immediate events, the linked list will not be
            # ok for a while
            try:
                check_wavefront_links(skel.triangles)
            except AssertionError, err:
                print "{}".format(err)
                if False:
                    to_continue = raw_input('continue? [y|n]')
                    if to_continue == 'y':
                        pass
                    else:
                        break
                else:
                    pass
#     if pause:
#         for t in range(3):
#             NOW += t
    if pause:
        visualize(queue, skel, NOW)
    if make_video:
        make_frames(NOW, VIDEO_DIGITS, skel, queue, immediate)
    return NOW



def compare_event_by_time(one, other):
    """ Compare two events, first by time, in case they are equal
    by triangle type (first 2-triangle, then 1-triangle, then 0-triangle),
    as last resort by identifier of triangle.
    """
    # compare by time
    if one.time < other.time:  # lt
        return -1
    elif one.time > other.time:  # gt
        return 1
    # in case times are equal, compare by id of triangle
    # to be able to find the correct triangle back
    else:  # eq
        if -one.triangle_tp < -other.triangle_tp:
            return -1
        elif -one.triangle_tp > -other.triangle_tp:
            return 1
        else:
            if id(one.triangle) < id(other.triangle):
                return -1
            elif id(one.triangle) > id(other.triangle):
                return 1
            else:
                return 0


def init_event_list(skel):
    """Compute for all kinetic triangles when they will collapse and
    put them in an OrderedSequence, so that events are ordered properly
    for further processing
    """
    q = OrderedSequence(cmp=compare_event_by_time)
    logging.debug("Calculate initial events")
    logging.debug("=" * 80)
    for tri in skel.triangles:
        res = compute_collapse_time(tri, 0, find_gt)
        if res is not None:
            q.add(res)
    logging.debug("=" * 80)
    return q
