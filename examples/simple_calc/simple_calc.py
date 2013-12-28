from __future__ import print_function
__author__ = 'Kondal Rao Komaragiri'

import sys
sys.path.append('../..')

from fsm_engine import FSM


fsm_obj = None

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
    global fsm_obj

    fsm_obj = FSM('calc.xml')

def main():
    initialize()

    fd = open('calc.txt')

    for line in fd.readlines():
        print (line.strip('\n'), end=''),

        for ch in line:
            if ch is not '\n':
                ev = get_datatype(ch)
                if ev is not 'WS' or ev is not 'RESULT':
                    fsm_obj.dispatch(event=ev, data=ch)
                else:
                    fsm_obj.dispatch(event=ev)

if __name__ == '__main__':
    main()
