"""Storage module"""

import time
import norimdb
from core import config


class Queues:
    """Quesues storage class"""

    @staticmethod
    def getinfo(name):
        """Gets the info about queue"""

        with norimdb.NorimDb(config.Storage.db_path()) as db:
            collection = db.get_collection("queues")
            result = collection.find({'name': name})
            if len(result) == 0:
                return None

            return result[0]
