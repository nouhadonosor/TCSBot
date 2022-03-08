from telegram.ext import MessageHandler, CommandHandler, CallbackQueryHandler

from tg.private.conv_states import STATE
from tg.filter import FILTER_FALLBACK, FILTER_PRIVATE_ADMIN, FILTER_PRIVATE_SUBS
from db.db_api import User
from tg.private.handlers.admin_handler import admin_handler
from tg.private.handlers.subs_handler import subs_handler
from tg.private.handlers.util_handler import menu_manager_select_handler, menu_manager_switch_page_handler
from tg.private.keyboard import keyboard_reply_main
from tg.private.paginated_menus import SubscriptionMenu


def entrypoint_handler(update, context):
    user_db = User.get_from_tg(update.effective_user)
    m = update.message
    if user_db:
        context.user_data['user_db'] = user_db
        m.reply_text("Привет", reply_markup=keyboard_reply_main(user_db.is_bot_admin))
        return STATE.MENU 
    else:
        m.reply_text("У вас нет доступа")
        return -1
    

ENTRYPOINT_HANDLERS = [
    CommandHandler('start', entrypoint_handler),
]

STATE.MENU = [
    MessageHandler(FILTER_PRIVATE_ADMIN, admin_handler),
    MessageHandler(FILTER_PRIVATE_SUBS, subs_handler),
    CallbackQueryHandler(menu_manager_switch_page_handler, pattern=SubscriptionMenu.get_regex()),
    CallbackQueryHandler(menu_manager_select_handler, pattern=SubscriptionMenu.get_regex_select())
]

FALLBACK_HANDLER = [
    MessageHandler(FILTER_FALLBACK, entrypoint_handler)
]