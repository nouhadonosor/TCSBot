import logging

def to_main_on_exception(update, context):
    pass
    logging.info(f'Handled error: ')
    logging.exception(context.error)
    return -1
