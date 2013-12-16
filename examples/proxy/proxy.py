import sys

sys.path.append('../../fsm_engine')

import fsm_engine
import fsm
import socket

fe = fsm_engine.FsmEngine()


def initialize():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serversocket.bind(('localhost', 9999))
    serversocket.listen(5)

    serversocket_fsm_obj = fsm.FSMObject(serversocket, fsm.SOCK, None, None, serversocket_dispatch)

    fe.add_fsm_object(serversocket_fsm_obj)

def client_socket_dispatch(sock_fsm_object):
    sock_fsm_object.fsm.generate_local_event('DataReceived')

def serversocket_dispatch(sock_fsm_object):
    (clientsocket, address) = sock_fsm_object.fd.accept()
    print "Received connection from: %s" % str(address)

    server_fsm = fsm.FSM(xml_file='proxy.xml')
    socket_fsm_obj = fsm.FSMObject(clientsocket, fsm.SOCK, server_fsm, None, client_socket_dispatch)
    server_fsm.add_fsm_object(socket_fsm_obj)

    fe.add_fsm(server_fsm)
    server_fsm.generate_local_event('NewConnection', clientsocket)


def main():
    initialize()

    fe.start_engine()


if __name__ == '__main__':
    main()