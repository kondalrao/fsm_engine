__author__ = 'Kondal'

class FSMException(Exception):
    """
        FSM Exception Class
    """

    def __init__(self, value=None):
        """

        @param value: Error string
        """
        self.value = value

    def __str__(self):
        return repr(self.value)