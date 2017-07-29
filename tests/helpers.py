"""Unit tests helpers module"""

import cherrypy
import urllib
from io import BytesIO


# https://stackoverflow.com/questions/33368837/how-to-unittest-a-cherrypy-webapp-in-python-3
class CherryPyClient:
    """CherryPy client"""

    def __init__(self, local, remote):
        self.__local = local
        self.__remote = remote

    def webapp_request(self, path='/', method='GET', **kwargs):
        headers = [('Host', '127.0.0.1')]
        qs = fd = None

        if method in ['POST', 'PUT']:
            qs = urllib.parse.urlencode(kwargs)
            headers.append(('content-type', 'application/x-www-form-urlencoded'))
            headers.append(('content-length', '%d' % len(qs)))
            fd = BytesIO(qs.encode('utf8'))
            qs = None
        elif kwargs:
            qs = urllib.parse.urlencode(kwargs)

        # Get our application and run the request against it
        app = cherrypy.tree.apps['']
        # Let's fake the local and remote addresses
        # Let's also use a non-secure scheme: 'http'
        request, response = app.get_serving(self.__local, self.__remote, 'http', 'HTTP/1.1')
        try:
            response = request.run(method, path, qs, 'HTTP/1.1', headers, fd)
        finally:
            if fd:
                fd.close()

        if response.output_status.startswith(b'500'):
            print(response.body)
            raise AssertionError("Unexpected error")

        # collapse the response into a byte string
        response.collapse_body()
        return response
