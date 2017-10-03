"""Web socket helpers module"""

from pybinn import dumps, loads

from src.core import storage

EMPTY = 0x00
OK = 0x99
GET = 0xa1
Q_MSG = 0xf1
Q_MSG_ACK = 0xf2
ERROR = 0xff
ALL = {
    EMPTY: "EMPTY",
    OK: "OK",
    GET: "GET",
    Q_MSG: "Q_MSG",
    Q_MSG_ACK: "Q_MSG_ACK",
    ERROR: "ERROR"
}

MODE_BINARY = 'binary'
MODES = [MODE_BINARY]


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
        return dumps(self._msg_dict)

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

    def _get(self):
        result = storage.Queues.get_first_msg(self._queue)
        if result:
            result['_id'] = str(result['_id'])
            return WsMessageFactory.create(self._mode, Q_MSG, {'msg': result})
        return None

    def _queue_msg_consumed(self, msg_id, application):
        storage.Queues.consumed(self._queue, msg_id, application)
        return self._get()

    def get_response(self, request: WsMessage):
        if request.header == GET:
            return self._get()

        if request.header == Q_MSG_ACK:
            next_msg = self._queue_msg_consumed(request.body['msg_id'], request.application)
            msgs = [WsMessageFactory.create(self._mode, OK, {'head': request.header, 'body': request.body})]
            if next_msg:
                msgs.append(next_msg)
            return msgs

        return None


def queue_exists(queue_name):
    if storage.Queues.get(queue_name):
        return True

    return False
