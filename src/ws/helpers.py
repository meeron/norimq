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

MODE_BINARY = 'binary'
MODES = [MODE_BINARY]


class DocIdEncoder(CustomEncoder):
    """DocId type encoder"""

    def __init__(self):
        super().__init__(DocId, DOCID_TYPE)

    def getbytes(self, value):
        return value.to_bytes()


class WsMessage:
    """WebSocket message"""

    def __init__(self, message=None):
        if message is not None:
            self._msg_dict = self._parse(message)
        else:
            self.set(EMPTY, None)

    def set(self, head, body, reqid=None):
        if head not in ALL:
            raise Exception("Invalid header %s" % head)
        self._msg_dict = {'head': head, 'body': body, 'reqid': reqid}

    def get_data(self):
        raise NotImplementedError()

    @property
    def header(self):
        return self._msg_dict['head']

    @property
    def body(self):
        return self._msg_dict['body']

    @property
    def application(self):
        if 'application' in self._msg_dict:
            return self._msg_dict['application']

        return ""

    @property
    def is_binary(self):
        raise NotImplementedError()

    def _parse(self, message):
        raise NotImplementedError()


class BinaryMessage(WsMessage):
    """BinaryMessage type"""

    def _parse(self, message):
        return loads(message)

    def get_data(self):
        return dumps(self._msg_dict, DocIdEncoder())

    @property
    def is_binary(self):
        return True


class WsMessageFactory:
    """WsMessageFactory class"""

    @staticmethod
    def create(mode, head, body, reqid=None):
        if mode not in MODES:
            raise Exception("Invalid mode=%s" % mode)
        msg_obj = None
        if mode == MODE_BINARY:
            msg_obj = BinaryMessage()

        if msg_obj:
            msg_obj.set(head, body, reqid)
            return msg_obj

        raise Exception("Cannot find message implementation for mode=%s" % mode)

    @staticmethod
    def create_from_message(mode, ws_message):
        if mode == MODE_BINARY and not ws_message.is_binary:
            raise Exception("Cannot create object message for binary mode when web socket message is not binary")

        return BinaryMessage(ws_message.data)


class QueuesRequestHandler:
    """Queues requests handler class"""

    def __init__(self, mode, queue_name):
        self._queue = queue_name
        self._mode = mode

    def _get_all(self):
        result = storage.Queues.get_msgs(self._queue)
        for r in result:
            r['_id'] = str(r['_id'])
            yield WsMessageFactory.create(self._mode, Q_MSG, {'queue': self._queue, 'msg': r})

    def _queue_msg_consumed(self, msg_id):
        return None

    def get_response(self, request: WsMessage):
        if request.header == GET_ALL:
            return self._get_all()
        if request.header == Q_MSG_ACK:
            return self._queue_msg_consumed(request.body['msg_id'])
        return None


def queue_exists(queue_name):
    if storage.Queues.get(queue_name):
        return True

    return False
