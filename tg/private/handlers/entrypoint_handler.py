from telegram.ext import MessageHandler

from tg.private.conv_states import STATE
from tg.filter import FILTER_PRIVATE

def entrypoint_handler(update, context):
    pass

STATE.ENTRYPOINT = [
    MessageHandler(FILTER_PRIVATE, entrypoint_handler)
]