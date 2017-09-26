"""Web socket module"""

import cherrypy
from ws4py.websocket import EchoWebSocket


class WebSocket:
    """Web Socket root class"""

    @cherrypy.expose
    def index(self):
        handler = cherrypy.request.ws_handler

    @staticmethod
    def config():
        return {
            '/': {
                'tools.websocket.on': True,
                'tools.websocket.handler_cls': EchoWebSocket
            }
        }
