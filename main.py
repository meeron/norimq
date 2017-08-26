"""Server module"""

import cherrypy
from src.api import Api
from src.web import Home
from src.core import config
from src.core.logging import Logger

if __name__ == '__main__':
    config.init()
    logger = Logger()

    home = Home()
    api = Api()

    cherrypy.config.update(config.cherrypy())
    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())

    cherrypy.engine.start()

    logger.info("Listening on %s:%d...", config.Network.ip(), config.Network.port())

    cherrypy.engine.block()
