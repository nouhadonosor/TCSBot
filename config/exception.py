class ConfigFieldNotSet(Exception):
    def __init__(self, field_names) -> None:
        flds = ', '.join(field_names)
        self.__verbose_error = f'{flds} config field(s) not set!'
        super().__init__(self.__verbose_error)