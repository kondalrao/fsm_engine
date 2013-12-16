__author__ = 'Kondal'
import sys
sys.path.append('../../fsm_engine')

import fsm_engine
import fsm
import termios
import atexit

fd = sys.stdin.fileno()


old_term = termios.tcgetattr(fd)


def set_normal_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)


def initialize():
    new_term = termios.tcgetattr(fd)
    #new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    new_term[3] = (new_term[3] & ~termios.ICANON)

    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)


def stdin_dispatch(fsmObj):
    fsm = fsmObj.fsm

    # print "stdin_dispatch -> Type: %s fd: %d flags: %d" % (fsmObj.obj_type, fsmObj.fd, flags)

    data = sys.stdin.read(1)
    # print "Received: " + str(data)

    if data in ['+', '-', '*', '/']:
        fsm.generate_local_event('OPERATOR', data)
    elif data.isdigit():
        fsm.generate_local_event('DIGIT', data)
    elif data.isspace():
        fsm.generate_local_event('WS')
    elif data == '=' or data == '\n':
        fsm.generate_local_event('RESULT', data)


def main():
    atexit.register(set_normal_term)
    initialize()

    f = fsm.FSM(xml_file='calc.xml')
    stdin_fsm_obj = fsm.FSMObject(sys.stdin.fileno(), fsm.STDIN, f, None, stdin_dispatch)
    f.add_fsm_object(stdin_fsm_obj)

    fe = fsm_engine.FsmEngine()

    fe.add_fsm(f)
    fe.start_engine()

if __name__ == '__main__':
    main()
