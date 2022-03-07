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

    @property
    def subscribed(self):
        if hasattr(self, '_subscribed'):
            return self._subscribed
        else:
            self._subscribed = False
            return self._subscribed

    @subscribed.setter
    def subscribed(self, v: bool):
        self._subscribed = v

    @classmethod
    def add_from_tg(cls, obj_tg):
        return cls.create_or_replace_pk_safe(
            id=obj_tg.id,
            title=obj_tg.title,
            type=obj_tg.type
        )

    @classmethod
    def prefetch_subscribed_for_user(cls, user):
        """
        q = cls.select(cls, Subscription, User).join(
            Subscription, join_type=JOIN.LEFT_OUTER
        ).join(
            User, join_type=JOIN.LEFT_OUTER
        )
        """
        q = prefetch(cls.select(),Subscription.select())
        for item in q:
            for sub in item.subscriptions:
                if sub.user.id == user.id:
                    item.subscribed = True

        return q

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
    def get_from_tg(cls, obj_tg):
        with db.atomic():
            return cls.get_or_none((cls.id == obj_tg.id) | (cls.username == obj_tg.username))

    @classmethod
    def add_from_tg(cls, obj_tg):
        return cls.create_or_replace_pk_safe(
            id=obj_tg.id,
            username=obj_tg.username,
            first_name=obj_tg.first_name,
            last_name=obj_tg.last_name
        )

    @classmethod
    def prefetch_chats(cls):
        q = prefetch(cls.select(), Subscription.select())
        return q

    @classmethod
    def get_statistics_for_users(cls):
        pass

    def subscribe_to_chat(self, chat: Chat):
        inst = Subscription.create(
            user = self,
            chat = chat
        )
        chat.subscribed = True
        return inst

    def unsubscribe_from_chat(self, chat: Chat):
        inst = Subscription.get_or_none(
            user = self,
            chat = chat
        )
        if inst:
            inst.delete_instance()
            chat.subscribed = False
            return True
        else:
            return False

    def toggle_subscription(self, chat: Chat):
        if chat.subscribed:
            return self.unsubscribe_from_chat(chat)
        else:
            return self.subscribe_to_chat(chat)

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

    @property
    def replies(self):
        if hasattr(self, '_replies'):
            return self._replies
        else:
            self._replies = 0
            return self._replies

    @replies.setter
    def replies(self, v):
        self._replies = v

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
    def get_statistics_on_day(cls, chat: Chat = None, on_date_day=datetime.date.today()):
        s = []
        #thcntr = ThreadCounter()
        thcntr_dict = {}
        where_clause = (fn.date_trunc('day', cls.date) == on_date_day)
        if chat:
            where_clause &= (cls.chat__id == chat.id)
        q = cls.select().where(
             where_clause)
        for message in q:
            if message.chat__id in thcntr_dict:
                thcntr_dict[message.chat__id].add_message(message)
            else:
                thcntr_dict[message.chat__id] = ThreadCounter()
                thcntr_dict[message.chat__id].add_message(message)

        for message in q:
            replies = thcntr_dict[message.chat__id].counters.get(message.message_id, 0)
            if replies > 0:
                message.replies = replies
                s.append(message)
        """
        for x in q: thcntr.add_message(x)
        for x in q:
            replies = thcntr.counters.get(x.message_id, 0)
            if replies > 0:
                x.replies = replies
                s.append(x)
        """
        return s

    @classmethod
    def delete_all_older_than_today(cls):
        with db.atomic():
            return cls.delete().where(fn.date_trunc('day', cls.date) < datetime.date.today()).execute()

class Subscription(BaseThroughModel):
    user = ForeignKeyField(User, backref='subscriptions', on_delete='CASCADE')
    chat = ForeignKeyField(Chat, backref='subscriptions', on_delete='CASCADE')

def setup_db():
    with db.atomic():
        db.create_tables([Chat, User, Message, Subscription])


