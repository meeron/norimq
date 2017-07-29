"""Server module"""

import cherrypy
from api import Api
from core import tools
from web import Home
from core import config

if __name__ == '__main__':
    config.init()
    cherrypy.config['tools.json_out.handler'] = tools.json_handler

    home = Home()
    api = Api()

    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())

    cherrypy.engine.start()
    cherrypy.engine.block()
