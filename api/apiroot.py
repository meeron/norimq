"""Queues api module"""

import cherrypy

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
class Queues:
    """Queues class"""

    def GET(self, name=None):
        if name:
            return "Queue {}".format(name)

        return "Queues list"

    def PUT(self, name):
        cherrypy.response.headers["Status"] = "201"
        return "PUT OK"

    def DELETE(self, name):
        return "DEL OK"
