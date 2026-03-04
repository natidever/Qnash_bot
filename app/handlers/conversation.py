from telegram.ext import ConversationHandler

from app.states import ASK_COUPON, ASK_PHONE, CONFIRM_ORDER


def build_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[],
        states={
            ASK_COUPON: [],
            ASK_PHONE: [],
            CONFIRM_ORDER: [],
        },
        fallbacks=[],
    )
