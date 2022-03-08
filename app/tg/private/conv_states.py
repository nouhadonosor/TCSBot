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
            if not __name == '__dict__' and __name[0].isupper():
                if __name in self.__dict__:
                    return __name
            return super().__getattribute__(__name)

        def get_states(self):
            self.__initialised = True
            r = self.__dict__.copy()
            del r['_ConvStates__initialised']
            return r

STATE = ConvStates()