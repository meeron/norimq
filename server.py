"""Server module"""

import cherrypy
from web import Home
from api import Api

print(__file__)

if __name__ == '__main__':
    home = Home()
    api = Api()

    cherrypy.tree.mount(home, '/')
    cherrypy.tree.mount(api, '/api', api.config())

    cherrypy.engine.start()
    cherrypy.engine.block()
