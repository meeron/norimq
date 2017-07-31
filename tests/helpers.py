"""Unit tests helpers module"""

import cherrypy
import urllib
from io import BytesIO
import json
from tempfile import TemporaryDirectory

import src.core.tools
from src.api import Api
from src.core import config



# https://stackoverflow.com/questions/33368837/how-to-unittest-a-cherrypy-webapp-in-python-3
class CherryPyClient:
    """CherryPy client"""

    def __init__(self, app_name):
        self.__local = cherrypy.lib.httputil.Host('127.0.0.1', 50000, "")
        self.__remote = cherrypy.lib.httputil.Host('127.0.0.1', 50001, "")
        self.__app_name = app_name

    def get(self, path):
        return self.__webapp_request(path=path, method='GET')

    def put(self, path, body_dict):
        return self.__webapp_request(path=path, method='PUT', body=json.dumps(body_dict))

    def delete(self, path):
        return self.__webapp_request(path=path, method='DELETE')

    def __webapp_request(self, path='/', method='GET', body=None, content_type='application/json'):
        headers = [('Host', '127.0.0.1')]
        qs = fd = None

        if method in ['POST', 'PUT']:
            headers.append(('content-type', content_type))
            headers.append(('content-length', '%d' % len(body)))
            fd = BytesIO(body.encode('utf8'))

        # Get our application and run the request against it
        app = cherrypy.tree.apps[self.__app_name]
        # Let's fake the local and remote addresses
        # Let's also use a non-secure scheme: 'http'
        request, response = app.get_serving(self.__local, self.__remote, 'http', 'HTTP/1.1')
        try:
            response = request.run(method, path, qs, 'HTTP/1.1', headers, fd)
        finally:
            if fd:
                fd.close()

        # collapse the response into a byte string
        response.collapse_body()
        return response


class CherryPyTestServer:
    """Test server"""

    def __init__(self):
        self.__tempdir = TemporaryDirectory()
        config.current = {'storage': {'dbPath': self.__tempdir.name}}

        cherrypy.config['tools.json_out.handler'] = src.core.tools.json_handler
        cherrypy.config.update({'environment': "test_suite"})

        # prevent the HTTP server from ever starting
        cherrypy.server.unsubscribe()

        api = Api()
        cherrypy.tree.mount(api, '/api', api.config())
        cherrypy.engine.start()

    def close(self):
        self.__tempdir.cleanup()
        cherrypy.engine.exit()


class StatusCodes:

    BAD_REQUEST = "400 Bad Request"
    NOT_FOUND = "404 Not Found"
    OK = "200 OK"
    CREATED = "201 Created"


def parse_response(response):
    return json.loads(response.body[0].decode('utf8'))
