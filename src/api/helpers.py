"""Api helpers module"""

import cherrypy


def bad_request(response_dict):
    cherrypy.response.status = 400
    return response_dict


def not_found():
    cherrypy.response.status = 404
    return {}


def method_not_allowed():
    cherrypy.response.status = 405
    return {}


def ok(data):
    cherrypy.response.status = 200
    return data


def created(data):
    cherrypy.response.status = 201
    return data


class ErrorCodes:
    """Error codes class"""

    APPLICATION_REQUIRED = "application_required"
    BODY_REQUIRED = "body_required"
