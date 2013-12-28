__author__ = 'Kondal Rao Komaragiri'

from multiprocessing import Process
from fsm_engine import *
import select

class FSMProcess(FSM, Process):
    """

    """

    def __init__(self, xml_file):
        FSM.__init__(self, xml_file)
        Process.__init__(self)

        self.queue = FSMQueue()

    def get_queue(self):
        """

        @return:
        """
        return self.queue

    def run(self):
        """

        """
        while True:
            try:
                rfdl, wfdl, errfdl = select.select([self.queue.fd], [], [], 1000)
            except KeyboardInterrupt:
                exit()

            # TODO: Collect statistics

            if len(rfdl) == 0:
                # TODO: Idle function
                continue

            ev, d = self.queue.get()
            self.dispatch(event=ev, data=d)
