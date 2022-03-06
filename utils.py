class ThreadCounter:
    def __init__(self) -> None:
        self.counters = {}
        self.pointers = {}

    def add_message(self, message):
        mes_id = message.message_id
        repl_mes_id = message.reply_to_message__id
        if not mes_id in self.counters and not repl_mes_id:
            self.counters[mes_id] = 0
        if repl_mes_id in self.counters:
            self.counters[repl_mes_id] += 1
            self.pointers[mes_id] = repl_mes_id
        if repl_mes_id in self.pointers:
            self.counters[self.pointers[repl_mes_id]] += 1
            self.pointers[mes_id] = self.pointers[repl_mes_id]

class ThreadMessage:
    def __init__(self, message):
        #self.message = message
        #self.replies = []
        self.replies_ids = []
        self.replies_count = 0

    def __add_new_message_to_replies(self, message):
        self.replies.append(message)
        self.replies_ids.append(message.message_id)
        self.replies_count += 1

    def add_reply(self, reply_message):
        if reply_message.reply_to_message:
            origin_id = reply_message.reply_to_message.message_id
            if origin_id in self.replies_ids or origin_id == self.message.message_id:
                self.__add_new_message_to_replies(reply_message)
                return True
        return False