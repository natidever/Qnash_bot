from telegram import Update
from telegram.ext import ContextTypes

WELCOME_TEXT = (
    "👋 Welcome to Qnash!\n\n"
    "I can help you with:\n"
    "• Products & group deals\n"
    "• Coupon codes\n"
    "• Order confirmation\n\n"
    "Use /start anytime."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(WELCOME_TEXT)
