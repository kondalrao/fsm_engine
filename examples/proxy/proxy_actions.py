
from BaseHTTPServer import BaseHTTPRequestHandler
from StringIO import StringIO
from urlparse import urlparse
import select
import socket

httpContext = None


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = StringIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


class HTTPContext(object):
    def __init__(self):
        self.clientsocket = None
        self.proxysocket = None
        self.clientfsm = None
        self.proxyfsm = None

        self.clientdata = None
        self.proxydata = None

        self.request = None
        self.response = None

        self.host = None
        self.port = 80

def log(context, data):
    print "Error Event"

def null(fsm_object):
    pass

def client_socket_dispatch(fsmObj):
    httpContext.clientdata = fsmObj.obj.recv(4096)
    httpContext.clientfsm.generateEvent(httpContext.clientfsm, 'DataReceived')

def newConnection(fsm_object, proxysock):
    fsm_object.context = HTTPContext()

def processRequest(fsm_object, data):
    fsm_object.context.request = HTTPRequest(fsm_object.context.proxysocket.recv(4096))

    print fsm_object.context.request

    if fsm_object.context.request.error_code is not None:
        print fsm_object.context.request.error_code

    url = urlparse(fsm_object.context.request.path)

    fsm_object.context.request.host = url.hostname
    if url.port is not None:
        fsm_object.context.request.port = url.port

    fsm_object.fsm.generate_local_event('CreateProxy')

def createProxy(fsm_object, data):
    print fsm_object.context.host
    print fsm_object.context.port

    fsm_object.context.proxysocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    fsm_object.context.proxysocket.connect((fsm_object.context.host, fsm_object.context.port))
    socket_fsm_obj = fsm.FSMObject(clientsocket, fsm.SOCK, server_fsm, None, client_socket_dispatch)
