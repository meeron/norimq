"""Tools module"""

import json
from datetime import datetime
from os import urandom
from time import time
from struct import pack
from binascii import hexlify
import cherrypy
from norimdb import DocId


class JsonEncoder(json.JSONEncoder):
    """Custom json encoder class"""

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, DocId):
            return str(o)
        return super().default(o)

    def iterencode(self, value):
        # Adapted from cherrypy/_cpcompat.py
        for chunk in super().iterencode(value):
            yield chunk.encode("utf-8")


def json_handler(*args, **kwargs):
    # Adapted from cherrypy/lib/jsontools.py
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)
    return JsonEncoder().iterencode(value)


def request_id():
    return hexlify(pack('I', int(time())) + urandom(4)).decode('utf8')

