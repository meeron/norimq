"""Queues api module"""

import cherrypy
from core import storage

class Api:
    """Api root class"""

    def __init__(self):
        self.queues = Queues()

    def config(self):
        return {
            '/queues': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher()
            }
        }


@cherrypy.expose
@cherrypy.tools.json_out()
class Queues:
    """Queues class"""
 
    def GET(self, name=None):
        if name:
            queue = storage.Queues.getinfo(name)
            if queue:
                return storage.Queues.getinfo(name)

            cherrypy.response.status = 404
            return {}

        return "Queues list"

    def PUT(self, name):
        cherrypy.response.status = 201
        return "PUT OK"

    def DELETE(self, name):
        return "DEL OK"
