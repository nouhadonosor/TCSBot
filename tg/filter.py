from telegram.ext import Filters

MES_CANCEL = 'Отмена'
MES_CLIENT = 'Клиент'
MES_ADMIN = 'Админ'

FILTER_MAIN = Filters.text & (~ Filters.command) & (~ Filters.regex(MES_CANCEL))

FILTER_GROUP = Filters.chat_type.groups & FILTER_MAIN
FILTER_PRIVATE = Filters.chat_type.private & FILTER_MAIN

