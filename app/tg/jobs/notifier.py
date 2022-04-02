import logging
import time

from itertools import groupby

from telegram import ParseMode
from utils import trunc_str_pretty

from db.db_api import Message, User


def notify_users_group_statistics(context):
    msgs = Message.get_statistics_on_day()
    msg_dict = {k:list(items) for k, items in groupby(sorted(msgs, key=lambda x: x.chat__id), lambda x: x.chat__id)}
    usrs = User.prefetch_chats()
    user_sub_dict = {x.user.id:[y.chat for y in sub.subscriptions] for sub in usrs for x in sub.subscriptions}

    for user_id, subs_chat_ids in user_sub_dict.items():
        
        for subs_chat in subs_chat_ids:
            try:
                text_list = [f'Ежедневная сводка по чату {subs_chat.title}']
                for n, msg in enumerate(sorted(msg_dict[subs_chat.id], key=lambda x: x.replies, reverse=True)[:5]):
                    reply_word = 'ответ'
                    if msg.replies >= 2 and msg.replies <= 4:
                        reply_word += 'а'
                    elif msg.replies >= 5 and msg.replies <= 9 or msg.replies == 0:
                        reply_word += 'ов'

                    if msg.text:
                        stat_msg = f'{n+1}. {trunc_str_pretty(msg.text)} - {msg.replies} {reply_word}\n<a href=\'{msg.link}\'>Ссылка</a>'
                    else:
                        stat_msg = f'{n+1}. {msg.replies} {reply_word}\n<a href=\'{msg.link}\'>Ссылка</a>'
                    
                    text_list.append(
                        stat_msg
                    )
                text = '\n\n'.join(text_list)
                context.bot.send_message(chat_id=user_id,
                                    text=text, parse_mode=ParseMode.HTML)
                time.sleep(0.5)
            except Exception as e:
                logging.exception(e)
    pass