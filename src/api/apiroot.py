"""Queues api module"""

import cherrypy

from src.core import storage
from .helpers import *


def bad_request(response_dict):
    cherrypy.response.status = 400
    return response_dict


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
        if name:
            queue = storage.Queues.get(name)
            if queue:
                if command is not None:
                    if command == "messages":
                        return storage.Queues.get_msgs(name)
                return storage.Queues.get(name)
            return not_found()

        return storage.Queues.get_all()

    @cherrypy.tools.json_in()
    def PUT(self, name):
        data = cherrypy.request.json
        if 'application' not in data:
            return bad_request({'code': ErrorCodes.APPLICATION_REQUIRED})
        if 'body' not in data:
            return bad_request({'code': ErrorCodes.BODY_REQUIRED})

        cherrypy.response.status = 201
        return storage.Queues.add_msg(name, data['application'], data['body'])

    def DELETE(self, name):
        status = 404
        if storage.Queues.delete(name):
            status = 200
        cherrypy.response.status = status
        return {}
