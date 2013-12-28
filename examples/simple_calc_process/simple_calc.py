from __future__ import print_function
__author__ = 'Kondal Rao Komaragiri'

import sys
sys.path.append('../..')

from fsm_engine.FSMProcess import FSMProcess

fsm_obj = None
fsm_queue = None

def get_datatype(data):
    if data in ['+', '-', '*', '/']:
        return 'OPERATOR'
    elif data.isdigit():
        return 'DIGIT'
    elif data.isspace():
        return 'WS'
    elif data == '=' or data == '\n':
        return 'RESULT'

def initialize():
    global fsm_obj, fsm_queue

    fsm_obj = FSMProcess('calc.xml')
    fsm_queue = fsm_obj.get_queue()
    fsm_obj.start()

def main():
    global fsm_obj, fsm_queue

    initialize()

    fd = open('calc.txt')

    for line in fd.readlines():
        print(line.strip('\n'), end='')

        for ch in line:
            if ch is not '\n':
                ev = get_datatype(ch)
                if ev is not 'WS' or ev is not 'RESULT':
                    fsm_queue.put((ev, ch))
                else:
                    fsm_queue.put((ev, None))

if __name__ == '__main__':
    main()
