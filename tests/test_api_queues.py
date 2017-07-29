"""Api queues testing module"""

import cherrypy
from .helpers import CherryPyClient, CherryPyTestServer, StatusCodes


class TestApiQueues:

    def setup_class(self):
        self.server = CherryPyTestServer()
        self.client = CherryPyClient('/api')

    def teardown_class(self):
        self.server.close()
        cherrypy.engine.exit()

    def test_get_queues(self):
        response = self.client.webapp_request("/api/queues")
        assert response.status == StatusCodes.OK
