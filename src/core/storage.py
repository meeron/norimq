"""Storage module"""

from datetime import datetime

import norimdb
import pybinn

from src.core import config


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

            return result[0]

    @staticmethod
    def add_msg(queue_name, application, body):
        """Adds message to queue"""

        with open_db() as db:
            queue_messages = db.get_collection("q_{}".format(queue_name))
            queues = db.get_collection("queues")

            queue = {
                'name': queue_name,
                'created_at': datetime.utcnow(),
                'updated_at': None,
                'size': 0,
                'messages_count': 0
            }
            queue_result = queues.find({'name': queue_name})
            if len(queue_result) > 0:
                queue = queue_result[0]

            msg_entry = {
                'created_at': datetime.utcnow(),
                'created_by': application,
                'consumed_at': None,
                'consumed_by': None,
                'lock_expires_at': None,
                'size': 0,
                'body': body
            }
            msg_entry['size'] = len(pybinn.dumps(msg_entry))
            queue['size'] += msg_entry['size']
            queue['updated_at'] = datetime.utcnow()
            queue['messages_count'] += 1

            queue_messages.add(msg_entry)
            if '_id' in queue:
                queues.set(queue['_id'], queue)
            else:
                queues.add(queue)

            return {
                'id': msg_entry['_id'],
                'created_at': msg_entry['created_at']
            }

    @staticmethod
    def get_all():
        """Gets queues list"""

        with open_db() as db:
            queues_coll = db.get_collection("queues")
            queues = queues_coll.find({})
            return queues

    @staticmethod
    def delete(queue_name):
        """Delete queue by id"""

        with open_db() as db:
            queues_coll = db.get_collection("queues")
            result = queues_coll.find({'name': queue_name})
            if len(result) == 0:
                return False
            count = queues_coll.remove(result[0]['_id'])
            if count == 0:
                raise Exception('queue was not removed.')
            db.remove_collection("q_{}".format(queue_name))
            return True

    @staticmethod
    def get_msgs(queue_name):
        """Gets messages from queue"""

        with open_db() as db:
            queue_messages = db.get_collection("q_{}".format(queue_name))
            result = queue_messages.find({
                'consumed_at': None
            }, 'created_at')
            for obj in result:
                del obj['body']
            return result

