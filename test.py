import datetime
from db.db_api import *
def test():
    test_case_1()

def test_case_1():
    q = Message.prefetch()
    a = list(q)
    chat = Chat.get(type='supergroup')
    q1 = Message.get_statistics(chat, datetime.date(2022, 3, 3))
    #a[0].reply_to_message
    #u = User.create_or_replace_pk_safe(id=12335, username='wwwwww')
    q1 = q.where(Message.date <= datetime.date(2022, 3, 3))
    pass

def test_case_2():
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self

    class ConvStates:
        def __init__(self) -> None:
            self.__initialised = False

        def __setattr__(self, __name: str, __value) -> None:
            if __name[0].isupper():
                if self.__initialised:
                    raise Exception('Tried to set new state after finished initialisation')
                if not __name in self.__dict__:
                    self.__dict__[__name] = __value
                else:
                    raise Exception(f'{__name} already in states!')
            else:
                super().__setattr__(__name, __value)
                #

        def __getattribute__(self, __name: str):
            if not __name == '__dict__':
                if __name in self.__dict__:
                    return __name
            return super().__getattribute__(__name)

        def get_states(self):
            self.__initialised = True
            return self.__dict__
        """
        def __getattribute__(self, __name: str):
            if __name[0].isupper():
                if __name in self.__dict__:
                    return __name
                else:
                    
                    raise Exception(f'State {__name} doesnt exist!')
            else:
                super().__getattribute__(__name)
        """
    c = ConvStates()

    c.STATE_A = 'HELLO'
    
    pass