__author__ = 'Kondal Rao Komaragiri'

from fsm_engine import FSMException

class FSMResource(object):

    NONE = -1
    TMR = 5
    SOCK = 10
    STDIN = 15
    STDOUT = 15
    STDERR = 15
    OBJ = 50
    FSMQ = 99

    def __init__(self):
        self.type = FSMResource.NONE

    def dispatch(self, **kwargs):
        """

        @param kwargs:
        """
        raise FSMException("Not Implemented: Please override")
