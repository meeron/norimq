"""Server module"""

import cherrypy
from src.api import Api
from src.core import tools
from src.web import Home
from src.core import config

if __name__ == '__main__':
    config.init()
    cherrypy.config['tools.json_out.handler'] = tools.json_handler

    home = Home()
    api = Api()

    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())

    cherrypy.engine.start()
    cherrypy.engine.block()