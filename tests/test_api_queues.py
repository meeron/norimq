"""Api queues testing module"""

import norimdb

from .helpers import *
from src.api.helpers import *


class TestApiQueues:

    def setup_class(self):
        self.server = CherryPyTestServer()
        self.client = CherryPyClient('/api')

    def teardown_class(self):
        self.server.close()
        cherrypy.engine.exit()

    def test_get_queues(self):
        response = self.client.get("/api/queues")
        response_object = parse_response(response)
        assert response.status == StatusCodes.OK
        assert len(response_object) == 0

    def test_add_message_bad_request_application(self):
        response = self.client.put("/api/queues/test/put", {})
        response_object = parse_response(response)
        assert response.status == StatusCodes.BAD_REQUEST
        assert response_object['code'] == ErrorCodes.APPLICATION_REQUIRED

    def test_add_message_bad_request_body(self):
        response = self.client.put("/api/queues/test/put", {'application': "test"})
        response_object = parse_response(response)
        assert response.status == StatusCodes.BAD_REQUEST
        assert response_object['code'] == ErrorCodes.BODY_REQUIRED

    def test_add_message_created(self):
        response = self.client.put("/api/queues/test/put", {'application': "test", 'body': "This is test body"})
        assert response.status == StatusCodes.CREATED
        response_object = parse_response(response)
        assert 'id' in response_object
        assert 'created_at' in response_object

    def test_get_queue_ok(self):
        response = self.client.get("/api/queues/test/details")
        assert response.status == StatusCodes.OK
        response_object = parse_response(response)
        assert '_id' in response_object

    def test_get_queue_messages_ok(self):
        response = self.client.get("/api/queues/test/messages")
        assert response.status == StatusCodes.OK
        response_object = parse_response(response)
        assert len(response_object) == 1
        assert '_id' in response_object[0]

    def test_get_message_body(self):
        response = self.client.get("/api/queues/test/messages")
        msg = parse_response(response)
        response = self.client.get("/api/queues/test/%s/body" % msg[0]['_id'])
        assert response.status == StatusCodes.OK

    def test_get_message_body_invalid_id(self):
        response = self.client.get("/api/queues/test/invalid-id/body")
        assert response.status == StatusCodes.NOT_FOUND

    def test_get_message_body_random_id(self):
        random_id = norimdb.DocId()
        response = self.client.get("/api/queues/test/%s/body" % random_id)
        assert response.status == StatusCodes.NOT_FOUND

    def test_get_queue_delete_ok(self):
        response = self.client.delete("/api/queues/test/delete")
        assert response.status == StatusCodes.OK

    def test_get_message_body_no_queue(self):
        response = self.client.get("/api/queues/test/f2c6a24976598b38/body")
        assert response.status == StatusCodes.NOT_FOUND

    def test_get_queue_delete_not_found(self):
        response = self.client.delete("/api/queues/test123/delete")
        assert response.status == StatusCodes.NOT_FOUND

    def test_get_queue_not_found(self):
        response = self.client.get("/api/queues/test/details")
        assert response.status == StatusCodes.NOT_FOUND

    def test_get_queue_messages_not_found(self):
        response = self.client.get("/api/queues/empty_queue/messages")
        assert response.status == StatusCodes.NOT_FOUND
