"""Queues api module"""

import cherrypy
from core import storage


def bad_request(message):
    cherrypy.response.status = 400
    return {
        'message': message
    }


def not_found():
    cherrypy.response.status = 404
    return {}


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
 
    def GET(self, name=None, command=None):
        if command is not None:
            if command == "messages":
                return storage.Queues.getmsgs(name)
            return not_found()

        if name:
            queue = storage.Queues.get(name)
            if queue:
                return storage.Queues.get(name)
            return not_found()

        return storage.Queues.getall()

    @cherrypy.tools.json_in()
    def PUT(self, name):
        data = cherrypy.request.json
        if 'application' not in data:
            return bad_request("'application' property is required.")
        if 'body' not in data:
            return bad_request("'body' is required.")

        cherrypy.response.status = 201
        return storage.Queues.addmsg(name, data['application'], data['body'])

    def DELETE(self, name):
        status = 404
        if storage.Queues.delete(name):
            status = 200
        cherrypy.response.status = status
        return {}
