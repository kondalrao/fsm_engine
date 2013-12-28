__author__ = 'Kondal Rao Komaragiri'

import sys
sys.path.append('../..')

from fsm_engine.FSMProcess import FSMProcess
from simple_calc_actions import calc_context

import termios
#import atexit

fsm_obj = None
fd = sys.stdin.fileno()

old_term = termios.tcgetattr(fd)

def set_normal_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)

def initialize():
    global fsm_obj

    new_term = termios.tcgetattr(fd)
    #new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    new_term[3] = (new_term[3] & ~termios.ICANON)

    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)

    fsm_obj = FSMProcess('calc.xml')
    fsm_obj.set_context(calc_context())
    fsm_obj.start()

def get_datatype(data):
    if data in ['+', '-', '*', '/']:
        return 'OPERATOR'
    elif data.isdigit():
        return 'DIGIT'
    elif data.isspace():
        return 'WS'
    elif data == '=' or data == '\n':
        return 'RESULT'

def main():
    global fsm_obj

    initialize()

    while True:
        try:
            ch = sys.stdin.read(1)
        except KeyboardInterrupt:
            exit()

        ev = get_datatype(ch)
        if ev is not 'WS' or ev is not 'RESULT':
            fsm_obj.get_queue().put((ev, ch))
        else:
            fsm_obj.get_queue().put((ev, None))

if __name__ == '__main__':
    main()
