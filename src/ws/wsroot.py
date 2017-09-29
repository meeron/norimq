"""Web socket module"""

import cherrypy
from ws4py.websocket import WebSocket as WebSocketBase
from types import GeneratorType

from src.core.logging import Logger
from src.core.tools import request_id
from src.ws.helpers import *


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

    def send_msg(self, binary_message_or_list):
        if isinstance(binary_message_or_list, BinaryMessage):
            self.send(binary_message_or_list.bytes, True)
        elif isinstance(binary_message_or_list, list) or isinstance(binary_message_or_list, GeneratorType):
            for bin_msg in binary_message_or_list:
                self.send(bin_msg.bytes, True)
        else:
            raise Exception("Invalid data type to send (%s)" % type(binary_message_or_list))

    def received_message(self, message):
        if not message.is_binary:
            return

        try:
            request = BinaryMessage(message.data)
            response = BinaryMessage()

            if request.header not in ALL:
                err_msg = "Unknown message %s" % request.header
                self._logger.warning(err_msg)
                response.set(ERROR, err_msg, self._conn_id)
            else:
                self._logger.debug("Received message %s: %s" % (ALL[request.header], request.body))

            req_handler = RequestHandler(request)
            response = req_handler.response()

            if response is not None:
                self.send_msg(response)
        except Exception as ex:
            self._logger.error(ex)
            self.send_msg(BinaryMessage.create(ERROR, "%s" % ex, self._conn_id))

