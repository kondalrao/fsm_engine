__author__ = 'Kondal Rao Komaragiri'

from multiprocessing import Queue
import xml.etree.ElementTree as ET


# 0 - 15 are predefined queues
# 0 - 4 are high priority queues
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


class FSMObject(object):

    def __init__(self, fd=-1, obj_type=None, fsm=None, context=None, dispatch_func=None):
        self.fd = fd
        self.obj_type = obj_type
        self.fsm = fsm
        self.context = context
        self.dispatch_func = dispatch_func


class FSM(object):

    """
        Finite State Machine

        State:

        Event:
            The event is a tuple of event and data. The data can be None.
            The data is mostly used by the Non FSM queue to pump data into
            FSM.

        Action:
            The action is callback function with two parameter; FSM context and data.
            The data can be None.

        Next_state:

        FSM Functionality:
            The order of state, event matching is done as following.
            (state, event) -> (action, next_state)
            (state, any) -> (action, next_state)
            (any, event) -> (action, next_state)
            (any, any) -> (action, next_state)

            If the pair is not found, an exception is raised.
    """

    def __init__(self, fsm_id=-1, fsm_name=None, xml_file=None):
        """
            Main FSM channel to receive fsm events.
        """
        self.queue = Queue()

        """
            A list of FSMObjects.
            Index 0 has the default fsm object of this fsm.

            Set the default channel.
            This is basically a Queue that picks the events sent through it.
        """
        self.fsm_objects = []
        self.__add_default_fsm_object()

        # General FSM information.
        self.fsm_name = fsm_name
        self.fsm_id = fsm_id
        self.fsm_file = xml_file
        self.fsm_engine = None
        self.fsm_actions = None
        self.import_file = None

        # State, Event and Action tables.
        self.states = {}
        self.events = {}
        self.actions = {}
        self.tables = {}

        # Default states and events.
        self.states['Any'] = 'Any'
        self.states['Same'] = 'Same'
        self.events['Any'] = 'Any'

        # Initial State and Initial Event.
        # NOTE: If the initial event is set, the event is queued into the fsm
        # when the fsm_engine starts.
        self.__init_state = None
        self.__init_event = None
        self.__data = None

        # Current State, Event and Action entries.
        self.__curr_state = None
        self.__curr_event = None
        self.__curr_action = None
        self.__next_state = None

        """
            If the XML is given during initialization then parse the xmlFile
            gathering the states, events, actions and other information.
        """
        if self.fsm_file is not None:
            self.__parse_xml(self.fsm_file)
            self.__import_fsm_actions()

    def __add_default_fsm_object(self):
        q = FSMObject()
        q.obj_type = FSMQ
        q.fsm = self
        q.dispatch_func = self.dispatch
        q.fd = self.queue._reader.fileno()

        self.fsm_objects.append(q)

    def __parse_xml(self, fsm_file=None):
        """
            Parse the xml file gathering states, events, actions and
            other information.
        """
        if fsm_file is not None:
            tree = ET.parse(fsm_file)
        else:
            raise FSMException("FSM file not found: " + str(fsm_file))

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

        tbl_check = [(state, event), (state, 'Any'), ('Any', event), ('Any', 'Any')]

        for chk in tbl_check:
            if chk in self.tables:
                action, next_state = self.tables[chk]
                return action, next_state

        raise FSMException("Invalid event %s in state %s" % (event, state))

    def __pre_dispatch(self):
        """
            The pre dispatch function
        """
        self.__curr_event, self.__data = self.queue.get()
        self.__curr_action, self.__next_state = self.__get_action()

    def __post_dispatch(self):
        """
            The post dispatch function
        """
        if self.__next_state != 'Same':
            self.__curr_state = self.__next_state

    def set_fsm_file(self, fsm_file):
        self.fsm_file = fsm_file
        self.__parse_xml()
        self.__import_fsm_actions()

    def add_fsm_object(self, fsm_object):
        # TODO: Check the type of fsm_object
        self.fsm_objects.append(fsm_object)

    def del_fsm_object(self, id):
        # TODO: Delete the fsm object from the fsm_object list based on ID
        pass

    def get_fsm_object(self):
        return self.fsm_objects[0]

    def get_fsm_objects(self):
        return self.fsm_objects

    def get_context(self):
        return self.fsm_objects[0].context

    def set_context(self, context):
        self.fsm_objects[0].context = context

    def set_id(self, fsm_id):
        self.fsm_id = fsm_id

    def get_id(self):
        return self.fsm_id

    def set_fsm_engine(self, fsm_engine):
        self.fsm_engine = fsm_engine

    def generate_initial_event(self):
        if self.__init_event is not None:
            #self.fsmEngine.generateEvent(self, self.__init_event)
            self.generate_local_event(self.__init_event)

    def generate_local_event(self, event, data=None):
        self.queue.put((event, data))

    def dispatch(self, fsm_object=None):
        """
            The dispatch function.
        """
        self.__pre_dispatch()
        func = getattr(self.fsm_actions, self.__curr_action)

        if callable(func):
            func(self.fsm_objects[0], self.__data)
        else:
            raise FSMException("Cannot find the action: " + str(func))

        self.__post_dispatch()
