from telegram.ext import ConversationHandler
from tg.private.conv_states import STATE

PRIVATE_HANDLER = ConversationHandler(
    entry_points=[],
    states=STATE.get_states(),
    fallbacks=[]
)