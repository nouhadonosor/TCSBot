from telegram import ReplyKeyboardMarkup

from tg.filter import MES_ADMIN, MES_CLIENT



def keyboard_reply_main(is_admin=False):
    #if 'is_admin' in context.user_data:
    #    is_admin = context.user_data['is_admin']
    #else:
    #    is_admin = False

    if is_admin:
        buttons = [
                    [MES_CLIENT, MES_ADMIN]
                ]
    else:
        buttons = [
                    [MES_CLIENT]
                ]

    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    
    return keyboard