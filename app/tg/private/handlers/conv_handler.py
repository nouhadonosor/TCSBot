from telegram.ext import ConversationHandler
from tg.private.handlers.entrypoint_handler import ENTRYPOINT_HANDLERS, FALLBACK_HANDLER
from tg.private.conv_states import STATE

PRIVATE_HANDLER = ConversationHandler(
    entry_points=ENTRYPOINT_HANDLERS,
    states=STATE.get_states(),
    fallbacks=FALLBACK_HANDLER
)