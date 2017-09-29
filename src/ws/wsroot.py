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
    def queues(self, queue_name, mode='binary'):
        if queue_exists(queue_name):
            cherrypy.request.ws_handler.set(queue_name, mode)
            handler = cherrypy.request.ws_handler
        else:
            cherrypy.response.status = 404
            return "Queue '%s' not found" % queue_name

    @staticmethod
    def config():
        return {
            '/queues': {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls': QueuesWebSocketHandler
            }
        }


class QueuesWebSocketHandler(WebSocketBase):
    """Queues web socket handler"""

    def __init__(self, sock, protocols=None, extensions=None, environ=None, heartbeat_freq=None):
        super().__init__(sock, protocols, extensions, environ, heartbeat_freq)
        self._conn_id = request_id()
        self._logger = Logger("QueuesWSHandler %s" % self._conn_id)
        self._queue = None
        self._mode = None

    def set(self, queue_name, mode):
        if mode not in MODES:
            err_msg = "Invalid QueuesWebSocketHandler mode=%s" % mode
            self._logger.error(err_msg)
            raise Exception(err_msg)

        self._queue = queue_name
        self._mode = mode
        self._logger.debug("Queue '%s' in '%s' mode" % (queue_name, mode))

    def opened(self):
        ip = self.peer_address[0]
        port = self.peer_address[1]
        self._logger.info("Connection from %s:%d" % (ip, port))

    def closed(self, code, reason=None):
        self._logger.info("Connection closed")

    def send_msg(self, message_or_list):
        if isinstance(message_or_list, WsMessage):
            self.send(message_or_list.get_data(), self._mode == MODE_BINARY)
        elif isinstance(message_or_list, list) or isinstance(message_or_list, GeneratorType):
            for bin_msg in message_or_list:
                self.send_msg(bin_msg)
        else:
            raise Exception("Invalid data type to send (%s)" % type(message_or_list))

    def received_message(self, message):
        try:
            request = WsMessageFactory.create_from_message(self._mode, message)
            if request.header not in ALL:
                err_msg = "Unknown message %s" % request.header
                self._logger.warning(err_msg)
                self.send_msg(WsMessageFactory.create(self._mode, ERROR, err_msg, self._conn_id))
            else:
                self._logger.debug("Received message %s from '%s': %s"
                                   % (ALL[request.header], request.application, request.body))

            handler = QueuesRequestHandler(self._mode, self._queue)
            response = handler.get_response(request)
            if response:
                self.send_msg(response)
        except Exception as ex:
            self._logger.error(ex)
            err_msg = WsMessageFactory.create(self._mode, ERROR, "%s" % ex, self._conn_id)
            self.send_msg(err_msg)


