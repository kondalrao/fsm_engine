__author__ = 'Kondal Rao Komaragiri'

from threading import Timer
from fsm_engine import FSMResource

class FSMTimer(FSMResource):
    """

    """

    def __init__(self):
        FSMResource.__init__(self)
        self.timers = []

    def addTimer(self, tm=1, **kwargs):
        timer = Timer(tm, self.dispatch, kwargs=kwargs)
        self.timers.append(timer)
        return timer

    def startTimer(self, timer):
        timer.start()

    def stopTimer(self, timer):
        timer.cancel()

    def dispatch(self, **kwargs):
        print ('dispatch')
        print (kwargs)
