
import sys
sys.path.append('../fsm_engine')

from fsm_engine import *
import time


def Worker(queue, timer):
    print "Starting Worker with queue: " + str(queue._reader.fileno()) + " with timer: " + str(timer)
    counter = 10
    time.sleep(timer)

    while counter > 0:
        print "Sending data: " + str(counter) + " to Queue: " + str(queue._reader.fileno())
        queue.put(random.randint(1, 5))
        queue.put(counter)
        time.sleep(timer)
        counter = counter - 1

    print "Finished Worker with queue: " + str(queue._reader.fileno())


# Test 1


def test1():
    jobs = []
    q = []
    fe = FsmEngine(None, None)
    for idx in range(1, 5):
        print "idx: " + str(idx)
        f = FSM(idx)
        q.append(f.getQueue())
        fe.addFSM(f)

        for idx in range(0, len(q)):
            proc = Process(target=Worker, args=(q[idx], random.randint(1, 5),))
            jobs.append(proc)
            proc.start()

        fe.start_engine()

        for job in jobs:
            job.terminate()
            job.join()

# End of Test 1


# Test 2

f = FSM(0, 'calc', 'calc.xml')


def dispatch(fsmEngine, obj_type, fd, flags):
    global fe, f

    print "dispatch -> obj_Type: " + str(obj_type) + " fd: " + str(fd) + " flags: " + str(flags)

    data = raw_input()

    if data in ['+', '-', '*', '/']:
        fsmEngine.generateEvent(f, 'OPERATOR', data)
    elif data.isdigit():
        fsmEngine.generateEvent(f, 'DIGIT', data)
    elif data == '=':
        fsmEngine.generateEvent(f, 'RESULT', data)


def test2():
    fe = FsmEngine(dispatch, None)
    fe.addFSM(f)
    fe.addStdin()
    fe.start_engine()


# End of Test 2


if __name__ == '__main__':
    # test1()
    # test2()
    pass
