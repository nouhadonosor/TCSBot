from telegram.ext import MessageHandler
from telegram.ext import Filters

from tg.filter import MES_CANCEL

def fallback_handler(update, context):
    pass

FALLBACK_HANDLER = [
    MessageHandler(Filters.regex(MES_CANCEL))
]