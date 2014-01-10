__author__ = 'Kondal'


class FSMContext(object):
    """
        FSM Context Class
    """

    def __init__(self, fsm):
        object.__init__(self)
        self.data = None
        self.fsm = fsm
