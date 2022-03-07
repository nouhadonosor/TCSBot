from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup

from utils import chunkify

class BaseMenu:
    _regex_swtchl = 'menu_switch_left'
    _regex_swtchr = 'menu_switch_right'
    _regex_select = 'menu_item_'
    _menu_title = 'Меню: '
    def __init__(
        self,
        items: list,
        per_page: int = 5,
        start_page: int = 0,
        callback=None
        ) -> None:
        self._items = items
        self._per_page = per_page
        self._callback = callback
        self._cur_page = start_page
        self._paginate()
        self._make_menu()

    @classmethod
    def get_regex(cls):
        return f'{cls._regex_swtchl}|{cls._regex_swtchr}'

    @classmethod
    def get_regex_select(cls):
        return f'{cls._regex_select}\d+_\d+'

    @classmethod
    def _get_regex_select_callback_data(cls, index, subindex):
        return f'{cls._regex_select}{index}_{subindex}'

    def _paginate(self):
        self._items_paginated = chunkify(self._items, self._per_page)
        self._pages_cnt = len(self._items_paginated)

    def _generate_button(self, item, index, subindex):
        raise NotImplementedError

    def _make_menu(self):
        self._messages_list = []
        l_button = InlineKeyboardButton('<', callback_data=self._regex_swtchl)
        r_button = InlineKeyboardButton('>', callback_data=self._regex_swtchr)
        
        for n, item in enumerate(self._items_paginated):
            mes_page = []
            button_list = []
            for nn, subitem in enumerate(item):
                button_list.append([self._generate_button(subitem, n, nn)])
                #button_list.append(InlineKeyboardButton(f'{item}', callback_data=f'{self._regex_select}{usr.id}'))
            
            if n == 0:
                nav_buttons = [
                    r_button
                ]
            elif n == self._pages_cnt - 1:
                nav_buttons = [
                    l_button
                ]
            else:
                nav_buttons = [
                    l_button, r_button
                ]
            
            kb_buttons = button_list
        

            if self._pages_cnt > 1:
                kb_buttons.append(nav_buttons)

            kb = InlineKeyboardMarkup(kb_buttons)

            mes_page.append(self._menu_title)
            mes_page.append(kb)
            self._messages_list.append(mes_page)
    
    def _get_next_page(self):
        pg = self._cur_page + 1
        if pg < self._pages_cnt:
            self._cur_page = pg
        return self.get_keyboard()
    
    def _get_prev_page(self):
        pg = self._cur_page - 1
        if pg >= 0:
            self._cur_page = pg
        return self.get_keyboard()

    def get_keyboard(self):
        return self._messages_list[self._cur_page]

    def change_page(self, update, context):
        cb_data = update.callback_query.data
        if cb_data == self._regex_swtchl:
            return self._get_prev_page()
        elif cb_data == self._regex_swtchr:
            return self._get_next_page()
        else:
            return self.get_keyboard()

    def select_item(self, update, context):
        cb_data = update.callback_query.data
        splitted = cb_data.split('_')
        subindex = splitted[-1]
        index = splitted[-2]
        return self._items_paginated[int(index)][int(subindex)]

    def handle_select(self, update, context):
        self._callback(self.select_item(update, context))

    def rebuild_menu(self):
        self._make_menu()

class SubscriptionMenu(BaseMenu):
    _menu_title = 'Подписки: '
    def _generate_button(self, item, index, subindex):
        is_sub = item.subscribed
        emoji = '✅' if is_sub else '❌'
        return InlineKeyboardButton(f'{emoji} {item.title} {emoji}', callback_data=self._get_regex_select_callback_data(index, subindex))