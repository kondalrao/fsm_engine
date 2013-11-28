import multiprocessing
from multiprocessing import Queue
import xml.etree.ElementTree as ET
import select
import logging
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


class FSMObject(object):

    def __init__(self):
        self.fd = -1
        self.obj = None
        self.obj_type = None
        self.dispatch_func = None


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

        self.data = None


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

    def generateInitialEvent(self):
        if self.__init_event is not None:
            self.fsmEngine.generateEvent(self, self.__init_event)

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

    def __init__(self, dispatch=None, flags=None):
        self.q_dict = {}
        self.dispatch = dispatch
        self.flags = flags
        self.poller = select.poll()

        self.__engineStarted = False

        self.__init_log()

    def __init_log(self):
        # multiprocessing.log_to_stderr(logging.DEBUG)
        multiprocessing.log_to_stderr()
        self.logger = multiprocessing.get_logger()
        self.logger.setLevel(logging.DEBUG)

    def __idle(self):
        # self.logger.debug("FsmEngine.__idle")
        pass

    def __collectStats(self):
        # self.logger.debug("FsmEngine.__collectStats")
        pass

    def __getNewFSMId(self):
        self.logger.debug("FsmEngine.__getNewFSMId")
        fsmid = [0]
        for obj in self.q_dict.values():
            if obj.obj_type == FSMQ:
                fsmid.append(obj.obj.getId())

        new_fsmid = max(fsmid) + 1
        self.logger.debug("FsmEngine.__getNewFSMId: new_fsmid: %d" % new_fsmid)

        return new_fsmid

    def __mk_FSMObject(self, obj_type, fd, obj=None, dispatch_func=None):
        fsmObj = FSMObject()
        fsmObj.fd = fd
        fsmObj.obj = obj
        fsmObj.obj_type = obj_type
        fsmObj.dispatch_func = dispatch_func

        return fsmObj

    def __addfd(self, fsmObj):
        self.logger.debug("FsmEngine.__addfd: Adding fd: %s; type: %d, obj: %s" %
                          (fsmObj.fd, fsmObj.obj_type, fsmObj.obj))
        self.q_dict[fsmObj.fd] = fsmObj
        self.poller.register(fsmObj.fd, READ_ONLY)

    def __delfd(self, fd):
        self.logger.debug("FsmEngine.__addfd: Deleting fd: %s" % fd)
        self.q_dict.pop(fd, None)
        self.poller.unregister(fd)

    def addFSM(self, fsm):
        self.logger.info("FsmEngine.addFSM: Adding FSM %s" % fsm.name)

        # Check if the fsm_id is already present in the fsmEngine
        if fsm.getId() == 0:
            fsm.setId(self.__getNewFSMId())

        fsmObj = self.__mk_FSMObject(FSMQ, fsm.getQueueId(), fsm)
        self.__addfd(fsmObj)
        fsm.setFsmEngine(self)
        fsm.generateInitialEvent()

    def removeFSM(self, fsm):
        self.logger.info("FsmEngine.removeFSM: Removing FSM %s" % fsm.name)
        self.__delfd(fsm.getQueueId())

    def addSocket(self, sock, dispatch_func=None):
        self.logger.info("FsmEngine.addSocket: Adding Socket %s" % sock)
        fsmObj = self.__mk_FSMObject(SOCK, sock.fileno(), sock, dispatch_func)
        self.__addfd(fsmObj)

    def removeSocket(self, sock):
        self.logger.info("FsmEngine.removeSocket: Removing Socket %s" % sock)
        self.__delfd(sock)

    def addTimer(self, timer):
        self.logger.info("FsmEngine.addTimer: Adding Timer %d" % timer)
        fsmObj = self.__mk_FSMObject(TMR, timer)
        self.__addfd(fsmObj)

    def removeTimer(self, timer):
        self.logger.info("FsmEngine.removeTimer: Removing Timer %d" % timer)
        self.__delfd(timer)

    def addObject(self, obj):
        self.logger.info("FsmEngine.addObject: Adding Object %s" % obj.name)
        self.__addfd(OBJ, obj)

    def removeObject(self, obj):
        self.logger.info("FsmEngine.removeObject: Removing Object %c" % obj.name)
        self.__delfd(obj.fd)

    def addStdin(self, dispatch_func=None):
        self.logger.info("FsmEngine.addStdin: Adding STDIN")
        fsmObj = self.__mk_FSMObject(STDIN, sys.stdin.fileno(), None, dispatch_func)
        self.__addfd(fsmObj)

    def removeStdin(self):
        self.logger.info("fsmEngine.removeStdin: Removing STDIN")
        self.__delfd(sys.stdin.fileno())

    def generateEvent(self, fsm, event, data=None):
        self.logger.info("FsmEngine.generateEvent: Generating event to FSM: %s; event: %s" % (fsm.name, event))
        fsm.getQueue().put((event, data))

    def broadcaseEvent(self, event, data=None):
        self.logger.info("fsmEngine.broadcaseEvent: Broadcasting event: %d" % event)
        for fsmObj in self.q_dict.values():
            if fsmObj.obj_type == FSMQ:
                self.generateEvent(fsmObj, event, data)

    def start_engine(self):
        self.logger.info("fsmEngine.start_engine")

        self.__engineStarted = True

        while True:
            try:
                events = self.poller.poll(TIMEOUT)
            except KeyboardInterrupt:
                exit()

            self.__collectStats()

            if len(events) == 0:
                self.__idle()
                continue

            # TODO: sort the events based on priority

            for fd, flags in events:
                self.logger.debug("fsmEngine.start_engine: fd: %s; flags: %d" % (fd, flags))
                fsmObj = self.q_dict[fd]

                if callable(fsmObj.dispatch_func):
                    fsmObj.dispatch_func(fsmObj, flags)
                elif callable(self.dispatch):
                    self.dispatch(fsmObj, flags)

                if fsmObj.obj_type == FSMQ:
                    fsmObj.obj.dispatch()
