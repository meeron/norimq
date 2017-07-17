"""Server module"""

import cherrypy
from web import Home
from api import Api
from core import config

print(__file__)

if __name__ == '__main__':
    config.init()

    home = Home()
    api = Api()

    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())

    cherrypy.engine.start()
    cherrypy.engine.block()
