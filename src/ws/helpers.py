"""Web socket helpers module"""

from pybinn import dumps, loads, CustomEncoder
from norimdb import DocId

from src.core import storage

DOCID_TYPE = b'\xf6'

EMPTY = 0x00
GET_ALL = 0xa1
Q_MSG = 0xf1
Q_MSG_ACK = 0xf2
ERROR = 0xff
ALL = {
    EMPTY: "EMPTY",
    GET_ALL: "GET_ALL",
    Q_MSG: "Q_MSG",
    Q_MSG_ACK: "Q_MSG_ACK",
    ERROR: "ERROR"
}


class DocIdEncoder(CustomEncoder):
    """DocId type encoder"""

    def __init__(self):
        super().__init__(DocId, DOCID_TYPE)

    def getbytes(self, value):
        return value.to_bytes()


class BinaryMessage:
    """BinaryMessage type"""

    def __init__(self, message=None):
        if message is not None:
            self._msg_dict = loads(message)
        else:
            self.set(EMPTY, None)

    def set(self, head, body, reqid=None):
        if head not in ALL:
            raise Exception("Invalid header %s" % head)
        self._msg_dict = {'head': head, 'body': body, 'reqid': reqid}

    @property
    def bytes(self):
        return dumps(self._msg_dict, DocIdEncoder())

    @property
    def header(self):
        return self._msg_dict['head']

    @property
    def body(self):
        return self._msg_dict['body']

    @staticmethod
    def create(head, body, reqid=None):
        obj = BinaryMessage()
        obj.set(head, body, reqid)
        return obj


class RequestHandler:
    """Request handler class"""

    def __init__(self, request: BinaryMessage):
        self._req = request

    def _get_all(self):
        if not isinstance(self._req.body, dict):
            return BinaryMessage.create(ERROR, "Body should be dictionary type")
        if 'queue' not in self._req.body:
            return BinaryMessage.create(ERROR, "Body doesn't contains 'queue' field")

        queue = self._req.body['queue']
        result = storage.Queues.get_msgs(queue)
        for r in result:
            r['_id'] = str(r['_id'])
            yield BinaryMessage.create(Q_MSG, {'queue': queue, 'msg': r})

    def _queue_msg_consumed(self):
        queue = self._req.body['queue']
        msg_id = self._req.body['msg_id']
        return None

    def response(self):
        if self._req.header == GET_ALL:
            return self._get_all()
        if self._req.header == Q_MSG_ACK:
            return self._queue_msg_consumed()
        return None
