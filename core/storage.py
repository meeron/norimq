"""Storage module"""

import time
import norimdb

class Queues:
    """Quesues storage class"""

    @staticmethod
    def getinfo(name):
        """Gets the info about queue"""

        return {
            '_id': norimdb.DocId().to_str(),
            'name': name,
            'created_at': int(time.time()),
            'messages_count': 0,
            'size': 0
        }
