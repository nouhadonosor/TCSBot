from telegram.ext import MessageHandler, Filters

from db.db_api import Chat, Message, User
from tg.filter import FILTER_GROUP, FILTER_PRIVATE

def group_handler(update, context):
    #thcnt.add_message(update.message)
    inst = Message.create_from_tg_model(update.message)
    #inst_user = User.add_from_tg(update.message.from_user)
    inst_chat = Chat.add_from_tg(update.message.chat)
    #if hasattr(update.message, 'reply_to_message'):
    #    ent.add_item(update.message.reply_to_message.message_id)

GROUP_HANDLER = MessageHandler(FILTER_GROUP, group_handler)
