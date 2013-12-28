__author__ = 'Kondal'

from multiprocessing import queues


class FSMQueue(queues.Queue):
    def __init__(self):
        queues.Queue.__init__(self)

    @property
    def fd(self):
        """


        @return: fd
        """
        return self._reader.fileno()
