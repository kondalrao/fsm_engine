from multiprocessing import Queue
#from multiprocessing import Process
import xml.etree.ElementTree as ET
import select
#import random
#import time
import sys

READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
READ_WRITE = READ_ONLY | select.POLLOUT
TIMEOUT = 5000

"""
    0 - 15 are predifined queues
    0 - 4 are high priority queues
"""
PRI0 = 0
PRI1 = 1
PRI2 = 2
PRI3 = 3
PRI4 = 4
TMR = 5
SOCK = 10
STDIN = 15
OBJ = 50
FSMQ = 99


class FSMException(Exception):

    """
        FSM Exception Class
    """

    def __init__(self, value=None):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FSMContext(object):

    """
        FSM Context for the FSM.
    """

    def __init__(self, fsm):
        self.fsm = fsm

        self.curr_state = None
        self.curr_event = None
        self.next_state = None


class FSM(object):

    """
        Finite State Machine

        State:

        Event:
            The event is a tuple of event and data. The data can be None.
            The data is mostly used by the Non FSM queue to pump data into
            FSM.

        Action:
            The action is callback function with two paramenter; FSM context and data.
            The data can be None.

        Next_state:

        FSM Functionality:
            The order of state, event matching is done as following.
            (state, event) -> (action, next_state)
            (state, any) -> (action, next_state)
            (any, event) -> (action, next_state)
            (any, any) -> (action, next_state)

            If the pair is not found, an excpetion is raised.
    """

    def __init__(self, id=0, name=None, file=None):
        """
            A FSM is basically a Queue that picks the events sent through it.
        """
        self.__queue = Queue()
        self.__q_id = self.__queue._reader.fileno()

        """
            General FSM information
        """
        self.name = name
        self.id = id
        self.fsm_file = file
        self.fsmEngine = None
        self.import_file = None
        self.fsm_actions = None

        """
            FSM Context
        """
        self.context = FSMContext(self)

        """
            State, Event and Action tables.
        """
        self.states = {}
        self.events = {}
        self.actions = {}
        self.tables = {}

        """
            Default states and events.
        """
        self.states['Any'] = 'Any'
        self.states['Same'] = 'Same'
        self.events['Any'] = 'Any'

        """
            Initial State and Inital Event.

            If the initial event is set, the event is queued into the fsm
            when the fsm_engine starts.
        """
        self.__init_state = None
        self.__init_event = None

        """
            Current State, Event and Action entries.
        """
        self.__curr_state = None
        self.__curr_event = None
        self.__curr_action = None
        self.__next_state = None

        """
            Temporary data used by the non FSM events.
        """
        self.__data = None

        """
            If the XML is given during initialization then parse the xmlFile
            gathering the states, events, actions and other information.
        """
        if self.fsm_file is not None:
            self.__parseXML()
            self.__import_fsm_actions()

    def __parseXML(self, file=None):
        """
            Parse the xml file gathering states, events, actions and
            other information.
        """
        if file is not None:
            tree = ET.parse(file)
        else:
            tree = ET.parse(self.fsm_file)

        for child in tree.getroot():
            if child.tag == 'states':
                for state in child.iter():
                    if state.tag == 'state':
                        self.states[state.text] = state.text
                    elif state.tag == 'init':
                        self.__init_state = state.text
                        self.__curr_state = state.text
            elif child.tag == 'events':
                for event in child.iter():
                    if event.tag == 'event':
                        self.events[event.text] = event.text
                    elif event.tag == 'init':
                        self.__init_event = event.text
            elif child.tag == 'actions':
                for action in child.iter():
                    if action.tag == 'action':
                        self.actions[action.text] = action.text
            elif child.tag == 'tables':
                for table in child.iter():
                    if table.tag == 'table':
                        state = table.attrib['state']
                        event = table.attrib['event']
                        action = table.attrib['action']
                        next_state = table.attrib['next_state']
                        self.tables[tuple([state, event])] = (action, next_state)
            elif child.tag == 'import':
                self.import_file = child.text

    def __import_fsm_actions(self):
        self.fsm_actions = __import__(self.import_file, globals(), locals(), [], -1)

    def getQueue(self):
        return self.__queue

    def getQueueId(self):
        return self.__q_id

    def getData(self):
        return self.__queue.get()

    def getId(self):
        return self.id

    def setId(self, id):
        self.id = id

    def setFsmEngine(self, fsmEngine):
        self.fsmEngine = fsmEngine

    def setFsmFP(self, file):
        self.fsm_file = file
        self.__parseXML()
        self.__import_fsm_actions()

    def generateEvent(self, fsm, event, data=None):
        self.fsmEngine.generateEvent(fsm, event, data)

    def __get_action(self):
        """
            Sequence of checks:
            1. [State, Event]
            2. [State, Any]
            3. [Any, Event]
            4. [Any, Any]
        """
        state = self.__curr_state
        event = self.__curr_event
        action = None
        next_state = None

        tbl_check = [(state, event), (state, 'Any'), ('Any', event), ('Any', 'Any')]

        for chk in tbl_check:
            if chk in self.tables:
                action, next_state = self.tables[chk]
                return (action, next_state)

        raise FSMException("Invalid event %s in state %s" % (event, state))

    def __pre_dispatch(self):
        """
            The pre dispatch function
        """
        self.__curr_event, self.__data = self.getData()
        self.__curr_action, self.__next_state = self.__get_action()

        self.context.curr_state = self.__curr_state
        self.context.curr_event = self.__curr_event
        self.context.next_state = self.__next_state

    def dispatch(self):
        """
            The dispatch function.
        """
        self.__pre_dispatch()
        func = getattr(self.fsm_actions, self.__curr_action)

        if callable(func):
            func(self.context, self.__data)
        else:
            raise FSMException("Cannot find the action: " + func)

        self.__post_dispatch()

    def __post_dispatch(self):
        """
            The post dispatch function
        """
        if self.__next_state != 'Same':
            self.__curr_state = self.__next_state


class FsmEngine(object):

    def __init__(self, dispatch, flags):
        self.q_dict = {}
        self.dispatch = dispatch
        self.flags = flags
        self.poller = select.poll()

    def __idle(self):
        pass

    def __collectStats(self):
        pass

    def __getNewFSMId(self):
        fsmid = [0]
        for obj_type, obj in self.q_dict.values():
            if obj_type == FSMQ:
                fsmid.append(obj.getId())

        return max(fsmid) + 1

    def __addfd(self, obj_type, fd, obj=None):
        self.q_dict[fd] = (obj_type, obj)
        self.poller.register(fd, READ_ONLY)

    def __delfd(self, fd):
        self.q_dict.pop(fd, None)

    def addFSM(self, fsm):
        # Check if the fsm_id is already present in the fsmEngine
        if fsm.getId() == 0:
            fsm.setId(self.__getNewFSMId())
        self.__addfd(FSMQ, fsm.getQueueId(), fsm)
        fsm.setFsmEngine(self)

    def removeFSM(self, fsm):
        self.__delfd(fsm.getQueueId())

    def addSocket(self, sock):
        self.__addfd(SOCK, sock)

    def removeSocket(self, sock):
        self.__delfd(sock)

    def addTimer(self, timer):
        pass

    def removeTimer(self, timer):
        pass

    def addObject(self, obj):
        self.__addfd(OBJ, obj)

    def removeObject(self, obj):
        self.__delfd(obj)

    def addStdin(self):
        self.__addfd(STDIN, sys.stdin.fileno())

    def removeStdin(self):
        self.__delfd(sys.stdin.fileno())

    def generateEvent(self, fsm, event, data=None):
        fsm.getQueue().put((event, data))

    def broadcaseEvent(self, event, data=None):
        for obj_type, obj in self.q_dict.values():
            if obj_type == FSMQ:
                self.generateEvent(obj, event, data)

    def start_engine(self):

        while True:
            events = self.poller.poll(TIMEOUT)
            self.__collectStats()

            if len(events) == 0:
                self.__idle()
                continue

            # TODO: sort the events based on priority

            for fd, flags in events:
                obj_type, obj = self.q_dict[fd]

                if callable(self.dispatch):
                    self.dispatch(obj_type, fd, flags)

                if obj_type == FSMQ:
                    obj.dispatch(self)

# def Worker(queue, timer):
#    print "Starting Worker with queue: " + str(queue._reader.fileno()) + " with timer: " + str(timer)
#    counter = 10
#    time.sleep(timer)
#
#    while counter > 0:
#        print "Sending data: " + str(counter) + " to Queue: " + str(queue._reader.fileno())
# queue.put(random.randint(1, 5))
#        queue.put(counter)
#        time.sleep(timer)
#        counter = counter - 1
#
#    print "Finished Worker with queue: " + str(queue._reader.fileno())


#
# Test 1
#
# def test1():
#    jobs = []
#    q = [ ]
#    fsms = [ ]
#    fe = FsmEngine(None, None)
#    for idx in range(1, 5):
#        print "idx: " + str(idx)
#        f = FSM(idx)
#        q.append(f.getQueue())
#        fe.addFSM(f)
#
#        for idx in range (0, len(q)):
#            proc = Process(target=Worker, args=(q[idx], random.randint(1, 5),))
#            jobs.append(proc)
#            proc.start()
#
#        fe.start_engine()
#
#        for job in jobs:
# job.terminate()
#            job.join()
#
# End of Test 2
#



#
# Test 2
#
#f = FSM(0, 'calc', 'calc.xml')
#
#
# def dispatch(fsmEngine, obj_type, fd, flags):
#    global fe, f
#
#    print "dispatch -> obj_Type: " + str(obj_type) + " fd: " + str(fd) + " flags: " + str(flags)
#
#    data = raw_input()
#
#    if data in ['+', '-', '*', '/']:
#        fsmEngine.generateEvent(f, 'OPERATOR', data)
#    elif data.isdigit():
#        fsmEngine.generateEvent(f, 'DIGIT', data)
#    elif data == '=':
#        fsmEngine.generateEvent(f, 'RESULT', data)
#
#
# def test2():
#    fe = FsmEngine(dispatch, None)
#    fe.addFSM(f)
#    fe.addStdin()
#    fe.start_engine()
#

# End of Test 2
#

# if __name__ == '__main__':
# test1()
# test2()
#    pass
