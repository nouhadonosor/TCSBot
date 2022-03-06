import os

from config.exception import ConfigFieldNotSet

FIELDS = [
    'TELEGRAM_BOT_API_TOKEN',
    'DB_NAME',
    'DB_USER',
    'DB_PASS',
    'DB_HOST',
    'DB_PORT',
]

class GlobalConfig:
    def __init__(self, fields, ignore_missing=False) -> None:
        self.__field_names = fields
        self.__missing_fields = []
        for field in fields:
            fld = os.environ.get(field)
            if not fld:
                self.__missing_fields.append(field)
            else:
                self.__dict__[field] = fld
        
        if not ignore_missing and len(self.__missing_fields)>0:
            raise ConfigFieldNotSet(self.__missing_fields)

GLOBAL_CONFIG = GlobalConfig(FIELDS)