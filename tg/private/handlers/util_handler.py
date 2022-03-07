
#def fallback_handler(update, context):
#    return entrypoint_handler(update, context)

from tg.private.conv_states import STATE


def menu_manager_switch_page_handler(update, context):
    menu = context.user_data['menu_manager']
    menu.change_page(update, context)

    msg_menu = menu.get_keyboard()
    context.user_data['state_m'].edit_text(msg_menu[0], reply_markup=msg_menu[1])
    return STATE.MENU

def menu_manager_select_handler(update, context):
    menu = context.user_data['menu_manager']
    menu.handle_select(update, context)
    menu.rebuild_menu()
    
    msg_menu = menu.get_keyboard()
    context.user_data['state_m'].edit_text(msg_menu[0], reply_markup=msg_menu[1])
    return STATE.MENU