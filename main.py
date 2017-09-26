"""Server module"""

import cherrypy
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from src.api import Api
from src.ws import WebSocket
from src.web import Home
from src.core import config
from src.core.logging import Logger

if __name__ == '__main__':
    config.init()
    logger = Logger()

    home = Home()
    api = Api()
    ws = WebSocket()

    cherrypy.config.update(config.cherrypy())

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())
    cherrypy.tree.mount(ws, '/ws', ws.config())

    cherrypy.engine.start()

    logger.info("Listening on %s:%d...", config.Network.ip(), config.Network.port())

    cherrypy.engine.block()
