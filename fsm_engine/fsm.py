__author__ = 'Kondal Rao Komaragiri'

import xml.etree.ElementTree as Etree
from fsm_engine import *

class FSM_BASE(object):
    def __init__(self):
        """

        """
        self.name = ''
        self.id = None
        self.fd = None

        self.fsm_engine = None
        self.timer = FSMTimer()

        self.context = FSMContext(self)

    def dispatch(self, **kwargs):
        """

        @param fsm_context:
        """
        raise FSMException("Not Implemented: Please override")

    def set_context(self, context):
        """

        @param context:
        """
        self.context = context
        self.context.fsm = self

    def generate_local_event(self, event, data):
        """

        @param event:
        @param data:
        """
        raise FSMException("Not Implemented: Please override")


    def generate_event(self, fsm, event, data):
        """

        @param event:
        @param data:
        """
        raise FSMException("Not Implemented: Please override")


class FSM(FSM_BASE):
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

    def __init__(self, xml_file):

        """

        @param xml_file:
        """
        # super(FSMObject, self).__init__()
        FSM_BASE.__init__(self)

        # General FSM information.
        self.fsm_file = xml_file
        self.fsm_actions = None
        self.import_file = None

        # State, Event and Action tables.
        self.__states = {}
        self.__events = {}
        self.__actions = {}
        self.__tables = {}

        # Default states and events.
        self.__states['Any'] = 'Any'
        self.__states['Same'] = 'Same'
        self.__events['Any'] = 'Any'

        # Initial State and Initial Event.
        # NOTE: If the initial event is set, the event is queued into the fsm
        # when the fsm_engine starts.
        self.__init_state = None
        self.__init_event = None

        # Current State, Event and Action entries.
        self.curr_state = None
        self.curr_event = None
        self.curr_action = None
        self.next_state = None

        """
            If the XML is given during initialization then parse the xmlFile
            gathering the states, events, actions and other information.
        """
        self.__parse_xml(self.fsm_file)
        self.__import_fsm_actions()


    def __parse_xml(self, fsm_file=None):
        """
        Parse the xml file gathering states, events, actions and
        other information.
        @param fsm_file:
        """
        if fsm_file is not None:
            tree = Etree.parse(fsm_file)
        else:
            raise FSMException("FSM file not found: " + str(fsm_file))

        for child in tree.getroot():
            if child.tag == 'states':
                for state in child.getiterator():
                    if state.tag == 'state':
                        self.__states[state.text] = state.text
                    elif state.tag == 'init':
                        self.__init_state = state.text
                        self.curr_state = state.text
            elif child.tag == 'events':
                for event in child.getiterator():
                    if event.tag == 'event':
                        self.__events[event.text] = event.text
                    elif event.tag == 'init':
                        self.__init_event = event.text
            elif child.tag == 'actions':
                for action in child.getiterator():
                    if action.tag == 'action':
                        self.__actions[action.text] = action.text
            elif child.tag == 'tables':
                for table in child.getiterator():
                    if table.tag == 'table':
                        state = table.attrib['state']
                        event = table.attrib['event']
                        action = table.attrib['action']
                        next_state = table.attrib['next_state']
                        self.__tables[tuple([state, event])] = (action, next_state)
            elif child.tag == 'import':
                self.import_file = child.text

    def __import_fsm_actions(self):
        """

        """
        self.fsm_actions = __import__(self.import_file, globals(), locals(), [], -1)

    def __get_action(self):
        """
        Sequence of checks:
        1. [State, Event]
        2. [State, Any]
        3. [Any, Event]
        4. [Any, Any]
        """
        state = self.curr_state
        event = self.curr_event

        tbl_check = [(state, event), (state, 'Any'), ('Any', event), ('Any', 'Any')]

        for chk in tbl_check:
            if chk in self.__tables:
                action, next_state = self.__tables[chk]
                return action, next_state

        raise FSMException("Invalid event %s in state %s" % (event, state))

    def __pre_dispatch(self, **kwargs):
        """
        The pre dispatch function.
        """
        self.curr_event = kwargs['event']
        self.context.data = kwargs['data']
        self.curr_action, self.next_state = self.__get_action()

    def dispatch(self, **kwargs):
        """
        The dispatch function.
        @param fsm_context:
        """
        self.__pre_dispatch(**kwargs)

        func = getattr(self.fsm_actions, self.curr_action)

        if callable(func):
            func(self.context)
        else:
            raise FSMException("Cannot find the action: " + str(func))

        self.__post_dispatch()

    def __post_dispatch(self):
        """
        The post dispatch function
        """
        if self.next_state != 'Same':
            self.curr_state = self.next_state

def callable(func):
    return hasattr(func, "__call__")
