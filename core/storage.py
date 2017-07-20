"""Storage module"""

import time
import norimdb
import pybinn
from core import config


def open_db():
    return norimdb.NorimDb(config.Storage.db_path())


class Queues:
    """Quesues storage class"""

    @staticmethod
    def get(name):
        """Gets the info about queue"""

        with open_db() as db:
            collection = db.get_collection("queues")
            result = collection.find({'name': name})
            if len(result) == 0:
                return None

            result[0]['id'] = str(norimdb.DocId(result[0]['_id']))
            del result[0]['_id']
            return result[0]

    @staticmethod
    def addmsg(queue_name, application, body):
        """Adds message to queue"""

        with open_db() as db:
            queue_messages = db.get_collection("q_{}".format(queue_name))
            queues = db.get_collection("queues")

            queue = {
                'name': queue_name,
                'created_at': time.time(),
                'updated_at': 0,
                'size': 0,
                'messages_count': 0
            }
            queue_result = queues.find({'name': queue_name})
            if len(queue_result) > 0:
                queue = queue_result[0]

            msg_entry = {
                'created_at': time.time(),
                'created_by': application,
                'consumed_at': 0,
                'consumed_by': "",
                'lock_expires_at': 0,
                'size': 0,
                'body': body
            }
            msg_entry['size'] = len(pybinn.dumps(msg_entry))
            queue['size'] += msg_entry['size']
            queue['updated_at'] = time.time()
            queue['messages_count'] += 1

            queue_messages.add(msg_entry)
            if '_id' in queue:
                queues.set(norimdb.DocId(queue['_id']), queue)
            else:
                queues.add(queue)

            return {
                'id': str(msg_entry['_id']),
                'created_at': msg_entry['created_at']
            }

    @staticmethod
    def getall():
        """Gets queues list"""

        with open_db() as db:
            queues_coll = db.get_collection("queues")
            queues = queues_coll.find({})

            for queue in queues:
                queue['id'] = str(norimdb.DocId(queue['_id']))
                del queue['_id']

            return queues

    @staticmethod
    def delete(queue_name):
        """Delete queue by id"""

        with open_db() as db:
            queues_coll = db.get_collection("queues")
            result = queues_coll.find({'name': queue_name})
            if len(result) == 0:
                return False
            count = queues_coll.remove(norimdb.DocId(result[0]['_id']))
            if count == 0:
                raise Exception('queue was not removed.')
            db.remove_collection("q_{}".format(queue_name))
            return True
