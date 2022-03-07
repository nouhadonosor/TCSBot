

import logging
from db.db_api import Message


def delete_old_msgs(context):

    r = Message.delete_all_older_than_today()
    logging.info(f'Cleaned up {r} messages from db.')