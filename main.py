"""Server module"""

import cherrypy
from src.api import Api
from src.core import tools
from src.web import Home
from src.core import config
from src.core.logging import Logger

if __name__ == '__main__':
    config.init()
    logger = Logger()

    server_port = config.Network.port()
    server_ip = config.Network.ip()

    cherrypy.config.update({
        'tools.json_out.handler': tools.json_handler,
        'server.socket_host': server_ip,
        'server.socket_port': server_port,
        'log.screen': False
    })

    home = Home()
    api = Api()

    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())

    cherrypy.engine.start()

    logger.info("Listening on %s:%d...", server_ip, server_port)

    cherrypy.engine.block()
