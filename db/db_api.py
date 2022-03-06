import datetime

from peewee import *

from config.global_config import GLOBAL_CONFIG
from utils import ThreadCounter

db = PostgresqlDatabase(
    GLOBAL_CONFIG.DB_NAME,
    user=GLOBAL_CONFIG.DB_USER,
    password=GLOBAL_CONFIG.DB_PASS,
    host=GLOBAL_CONFIG.DB_HOST,
    port=GLOBAL_CONFIG.DB_PORT
)

class BaseModel(Model):
    class Meta:
        database = db

    @classmethod
    def add_from_tg(cls, obj_tg):
        raise NotImplementedError

    @classmethod
    def create_or_replace_pk_safe(cls, **query):
        r = cls.insert(**query).on_conflict(
            conflict_target=(cls._meta.primary_key),
            preserve=[x for x in cls._meta.fields if not cls._meta.primary_key.name == x]
        ).execute()
        return r

class BaseThroughModel(Model):
    class Meta:
        database = db

class Chat(BaseModel):
    CHAT_TYPES = (
        ('channel', 'CHANNEL'),
        ('group', 'GROUP'),
        ('private', 'PRIVATE'),
        ('sender', 'SENDER'),
        ('supergroup', 'SUPERGROUP')
    )

    id = BigIntegerField(primary_key=True)
    title = CharField()
    type = CharField(choices=CHAT_TYPES)

    @classmethod
    def add_from_tg(cls, obj_tg):
        return cls.create_or_replace_pk_safe(
            id=obj_tg.id,
            title=obj_tg.title,
            type=obj_tg.type
        )

class User(BaseModel):
    id = BigIntegerField(primary_key=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)

    is_bot_admin = BooleanField(default=False)

    @property
    def tg_name(self):
        if self.username:
            return '@' + self.username
        return None

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return self.first_name + ' ' + self.last_name
        return None

    @classmethod
    def add_from_tg(cls, obj_tg):
        return cls.create_or_replace_pk_safe(
            id=obj_tg.id,
            username=obj_tg.username,
            first_name=obj_tg.first_name,
            last_name=obj_tg.last_name
        )

class Message(BaseModel):
    message_id = IntegerField()
    chat__id = BigIntegerField(null=True)#ForeignKeyField(Chat, backref='messages', on_delete='CASCADE')
    from_user__id = BigIntegerField(null=True)#ForeignKeyField(User, backref='messages', on_delete='CASCADE')
    date = DateTimeField(default=datetime.datetime.now)
    link = CharField(null=True)
    text = TextField(null=True)
    reply_to_message__id = BigIntegerField(null=True)#ForeignKeyField('self', backref='replies')

    class Meta:
        indexes = (
            (('message_id', 'chat__id'), True),
        )

    def __getattr__(self, __name: str):
        fkm_fields = self.FKEY_FIELDS_MODELS()
        cleared_fkm_fields = [k.split('__')[0] for k in fkm_fields]
        if __name in cleared_fkm_fields:
            return None
        else:
            raise AttributeError(f'{str(self.__class__)} object has no attribute {__name}')

    @classmethod
    def FKEY_FIELDS_MODELS(cls):
        return {
            'chat__id' : Chat.id,
            'from_user__id': User.id,
            'reply_to_message__id': cls.message_id
        }

    @classmethod
    def create_from_tg_model(cls, model):
        rpl_mes_id = model.reply_to_message.message_id if model.reply_to_message else None
        return cls.create(
            message_id=model.message_id,
            chat__id=model.chat.id,
            from_user__id=model.from_user.id,
            date=model.date,
            link=model.link,
            text=model.text,
            reply_to_message__id=rpl_mes_id,
        )

    @classmethod
    def prefetch(cls, *args):
        
        fkm_fields = cls.FKEY_FIELDS_MODELS()
        cleared_fkm_fields = {k.split('__')[0]:v for k, v in fkm_fields.items()}
        fkm_fields_clear_unclear = {k.split('__')[0]:k for k, v in fkm_fields.items()}

        if not args:
            args = [k.split('__')[0] for k in fkm_fields]

        aliases = [cls]
        joins_args = []

        for arg in args:
            if arg in cleared_fkm_fields:
                model_class = cleared_fkm_fields[arg].model
                if model_class == cls:
                    model_class = model_class.alias()
                aliases.append(model_class)
                on = (getattr(cls, fkm_fields_clear_unclear[arg]) == getattr(model_class, cleared_fkm_fields[arg].name))
                join_args = {
                    'dest': model_class,
                    'on': on,
                    'attr': arg,
                    'join_type': JOIN.LEFT_OUTER,
                }
                joins_args.append(join_args)

        q = cls.select(*aliases)

        for join_args in joins_args:
            q = q.join(**join_args).switch(cls)
        """
        al = Message.alias()
        qq = Message.select(Message,  User,al).join(
            User,
            on=(Message.from_user__id == User.id),
            attr='from_user'

        ).switch(Message).join(
            al,
            on=(Message.reply_to_message__id == al.message_id),
            attr='reply_to_message'
        ).switch(Message)
        """

        return (q)

    @classmethod
    def get_statistics_on_day(cls, chat: Chat, on_date_day=datetime.date.today()):
        thcntr = ThreadCounter()
        q = cls.select().where(
            (fn.date_trunc('day', cls.date) == on_date_day) & (cls.chat__id == chat.id))
        for x in q: thcntr.add_message(x)
        for x in q:
            x.replies = thcntr.replies.get(x.id, 0)
        return q

def setup_db():
    with db.atomic():
        db.create_tables([Chat, User, Message])


