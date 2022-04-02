from db.db_api import Chat
from tg.private.conv_states import STATE
from tg.private.keyboard import keyboard_reply_cancel
from tg.private.paginated_menus import SubscriptionMenu

class Dummy:
    def __init__(self, title) -> None:
        self.title = title

def subs_handler(update, context):
    m = update.message
    db_user = context.user_data['user_db']
    menu = SubscriptionMenu(
        Chat.prefetch_subscribed_for_user(db_user),
        callback=db_user.toggle_subscription
    )
    context.user_data['menu_manager'] = menu
    msg_menu = menu.get_keyboard()
    m.reply_text('Нажмите на чат, чтобы подписаться на/отписаться от статистики по нему', reply_markup=keyboard_reply_cancel())
    context.user_data['state_m'] = m.reply_text(msg_menu[0], reply_markup=msg_menu[1])
    return STATE.MENU

