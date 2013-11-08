import fsm_engine
import termios
import atexit
import sys

fd = sys.stdin.fileno()
f = fsm_engine.FSM(0, 'calc', 'calc.xml')

old_term = termios.tcgetattr(fd)


def set_normal_term():
    termios.tcsetattr(fd, termios.TCSAFLUSH, old_term)


def initialize():
    new_term = termios.tcgetattr(fd)
    #new_term[3] = (new_term[3] & ~termios.ICANON & ~termios.ECHO)
    new_term[3] = (new_term[3] & ~termios.ICANON)

    termios.tcsetattr(fd, termios.TCSAFLUSH, new_term)


def dispatch(fd_type, fd, flags):
    global f

    print "dispatch -> Type: %s fd: %d flags: %d" % (fd_type, fd, flags)

    if type != fsm_engine.STDIN:
        return

    data = sys.stdin.read(1)
    print "Received: " + str(data)

    if data in ['+', '-', '*', '/']:
        f.generateEvent(f, 'OPERATOR', data)
    elif data.isdigit():
        f.generateEvent(f, 'DIGIT', data)
    elif data.isspace():
        f.generateEvent(f, 'WS')
    elif data == '=' or data == '\n':
        f.generateEvent(f, 'RESULT', data)


def main():
    atexit.register(set_normal_term)
    initialize()

    fe = fsm_engine.FsmEngine(dispatch, None)
    fe.addFSM(f)
    fe.addStdin()
    fe.start_engine()

if __name__ == '__main__':
    main()
