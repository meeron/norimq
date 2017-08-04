"""Queues api module"""

from src.core import storage
from .helpers import *


class Api:
    """Api root class"""

    def __init__(self):
        self.queues = Queues()

    def config(self):
        queues_routes = cherrypy.dispatch.RoutesDispatcher()
        queues_routes.explicit = False
        queues_routes.connect("queues_list", "/queues", self.queues, action='list')
        queues_routes.connect("queues_actions", "/queues/{name}/{action}", self.queues)
        queues_routes.connect("queues_msg_body", "/queues/{name}/{msg_id}/body", self.queues, action='msg_body')

        return {
            '/queues': {
                'request.dispatch': queues_routes
            }
        }


@cherrypy.expose
@cherrypy.tools.json_out()
class Queues:
    """Queues class"""

    def list(self):
        if cherrypy.request.method != 'GET':
            return method_not_allowed()
        return ok(storage.Queues.get_all())

    def details(self, name):
        if cherrypy.request.method != 'GET':
            return method_not_allowed()
        queue = storage.Queues.get(name)
        if queue:
            return ok(queue)
        return not_found()

    def delete(self, name):
        if cherrypy.request.method != 'DELETE':
            return method_not_allowed()
        if storage.Queues.delete(name):
            return ok({})
        return not_found()

    def messages(self, name):
        if cherrypy.request.method != 'GET':
            return method_not_allowed()
        queue = storage.Queues.get(name)
        if queue:
            return ok(storage.Queues.get_msgs(name))
        return not_found()

    def msg_body(self, name, msg_id):
        if cherrypy.request.method != 'GET':
            return method_not_allowed()
        body = storage.Queues.get_msg_body(name, msg_id)
        if body:
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            return body
        return not_found()

    @cherrypy.tools.json_in()
    def put(self, name):
        if cherrypy.request.method != 'PUT':
            return method_not_allowed()
        data = cherrypy.request.json
        if 'application' not in data:
            return bad_request({'code': ErrorCodes.APPLICATION_REQUIRED})
        if 'body' not in data:
            return bad_request({'code': ErrorCodes.BODY_REQUIRED})

        return created(storage.Queues.add_msg(name, data['application'], data['body']))
