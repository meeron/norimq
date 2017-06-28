"""Server module"""

import cherrypy
from web import Home
from api import Api

print(__file__)

if __name__ == '__main__':
    cherrypy.tree.mount(Home(), '/')
    cherrypy.tree.mount(Api(), '/api')

    cherrypy.engine.start()
    cherrypy.engine.block()
