from telegram.ext import Filters

from tg.private.keyboard import MES_ADMIN, MES_CANCEL, MES_SUBSCRIPTIONS



FILTER_MAIN = Filters.text & (~ Filters.command) & (~ Filters.regex(MES_CANCEL))

FILTER_GROUP = Filters.chat_type.groups & FILTER_MAIN
FILTER_PRIVATE = Filters.chat_type.private & FILTER_MAIN
FILTER_PRIVATE_ADMIN = Filters.regex(MES_ADMIN)
FILTER_PRIVATE_SUBS = Filters.regex(MES_SUBSCRIPTIONS)

FILTER_FALLBACK = Filters.regex(MES_CANCEL)
