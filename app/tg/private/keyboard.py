from telegram import ReplyKeyboardMarkup

MES_CANCEL = 'Отмена'
MES_SUBSCRIPTIONS = 'Подписки'
MES_ADMIN = 'Админ'

def keyboard_reply_main(is_admin=False):
    #if 'is_admin' in context.user_data:
    #    is_admin = context.user_data['is_admin']
    #else:
    #    is_admin = False

    if is_admin:
        buttons = [
                    [MES_SUBSCRIPTIONS, MES_ADMIN]
                ]
    else:
        buttons = [
                    [MES_SUBSCRIPTIONS]
                ]

    keyboard = ReplyKeyboardMarkup(buttons, one_time_keyboard=True)
    
    return keyboard

def keyboard_reply_cancel():
    keyboard = ReplyKeyboardMarkup([
                    [MES_CANCEL]
                ], one_time_keyboard=True)
    
    return keyboard