import argparse
import datetime
import logging

from telegram.ext import Updater

from config.global_config import GLOBAL_CONFIG
from db.db_api import setup_db
from test import test
from tg.group.handlers.entrypoint_handler import GROUP_HANDLER
from tg.jobs.cleanup_routine import delete_old_msgs
from tg.jobs.notifier import notify_users_group_statistics
from tg.private.error_handlers import to_main_on_exception
from tg.private.handlers.conv_handler import PRIVATE_HANDLER

def main():
    #ARGPARSE
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setup_db", help="database init", action="store_true")
    parser.add_argument(
        "--force_post_statistics", help="post statistics", action="store_true")
    parser.add_argument(
        "--test", help="test", action="store_true")    
    parser.add_argument(
        "--log", help='logging level'
    )
    args = parser.parse_args()

    log_level = 'INFO'
    if args.log:
        log_level = args.log

    logging.basicConfig(format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
                    level=log_level)

    if args.setup_db:
        setup_db()
        raise SystemExit

    if args.test:
        test()
        raise SystemExit

    updater = Updater(GLOBAL_CONFIG.TELEGRAM_BOT_API_TOKEN, use_context=True)

    if args.force_post_statistics:
        notify_users_group_statistics(updater)
        raise SystemExit

    dispatcher = updater.dispatcher

    dispatcher.add_handler(GROUP_HANDLER)
    dispatcher.add_handler(PRIVATE_HANDLER)
    
    dispatcher.add_error_handler(to_main_on_exception)

    job_queue = updater.job_queue
    job_queue.run_daily(notify_users_group_statistics, datetime.time(23, 0, 0))
    job_queue.run_daily(delete_old_msgs, datetime.time(23, 0, 0))
    #job_queue.run_repeating(notify_users_group_statistics, 5, 0)

    #POLLING
    print('Polling...')
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()