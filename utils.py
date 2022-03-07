from math import trunc


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

def chunkify(a, nn):
    len_a = len(a)
    n = trunc(len_a / nn) + 1
    k, m = divmod(len_a, n)
    return list(a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))