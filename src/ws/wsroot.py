"""Web socket module"""

import cherrypy
from ws4py.websocket import WebSocket as WebSocketBase
from pybinn import dumps
from pybinn import loads

from src.core.logging import Logger
from src.core.tools import request_id

HEAD_EMPTY = b'\x00'
HEAD_GET_ALL = b'\xa1'
HEAD_ERROR = b'\xff'
HEAD_ALL = {
    HEAD_EMPTY: "HEAD_EMPTY",
    HEAD_GET_ALL: "HEAD_GET_ALL",
    HEAD_ERROR: "HEAD_ERROR"
}


class WebSocket:
    """Web Socket root class"""

    @cherrypy.expose
    def queuesb(self):
        handler = cherrypy.request.ws_handler

    @staticmethod
    def config():
        return {
            '/queuesb': {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls': QueuesBinaryWebSocketHandler
            }
        }


class QueuesBinaryWebSocketHandler(WebSocketBase):
    """Queue web socket handler"""

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        super().__init__(sock, protocols, extensions, environ, heartbeat_freq)
        self._conn_id = request_id()
        self._logger = Logger("QueuesBinaryWebSocket %s" % self._conn_id)

    def opened(self):
        ip = self.peer_address[0]
        port = self.peer_address[1]
        self._logger.info("Connection from %s:%d" % (ip, port))

    def closed(self, code, reason=None):
        self._logger.info("Connection closed")

    def send_msg(self, binary_message):
        self.send(binary_message.bytes, True)

    def received_message(self, message):
        if not message.is_binary:
            return

        try:
            request = BinaryMessage(message.data)
            response = BinaryMessage()

            if request.header not in HEAD_ALL:
                err_msg = "Unknown message %s" % request.header
                self._logger.warning(err_msg)
                response.set(HEAD_ERROR, err_msg)
            else:
                self._logger.debug("Received message %s" % HEAD_ALL[request.header])

            self.send_msg(response)
        except Exception as ex:
            self._logger.error(ex)
            self.send_msg(BinaryMessage.create(HEAD_ERROR, "ServerBinaryMessage error: %s" % ex))


class BinaryMessage:
    def __init__(self, message=None):
        if message is not None:
            self._msg_dict = loads(message)
        else:
            self._msg_dict = {'head': HEAD_EMPTY, 'body': None}

    def set(self, head, body):
        if head not in HEAD_ALL:
            raise Exception("Invalid header %s" % head)
        self._msg_dict = {'head': head, 'body': body}

    @property
    def bytes(self):
        return dumps(self._msg_dict)

    @property
    def header(self):
        return self._msg_dict['head']

    @property
    def body(self):
        return self._msg_dict['body']

    @staticmethod
    def create(head, body):
        obj = BinaryMessage()
        obj.set(head, body)
        return obj
