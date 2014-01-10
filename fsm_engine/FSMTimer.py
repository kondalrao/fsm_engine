__author__ = 'Kondal Rao Komaragiri'

from threading import Timer
from fsm_engine import FSMResource

class FSMTimer(FSMResource):
    """

    """

    def __init__(self):
        FSMResource.__init__(self, FSMResource.TIMER)
        self.timers = []

    def addTimer(self, tm_sec, func, **kwargs):
        timer = Timer(tm_sec, func, kwargs=kwargs)
        self.timers.append(timer)
        return timer

    def startTimer(self, timer):
        timer.start()

    def stopTimer(self, timer):
        timer.cancel()

    # def dispatch(self, **kwargs):
    #     print ('dispatch')
    #     print (kwargs)
    #
    #     if self.callable(kwargs[func]):
    #         kwargs[func](kwargs[context])
    #     else:
    #         raise FSMException("Cannot find the action: " + str(func))

    def callable(self, func):
        return hasattr(func, "__call__")
