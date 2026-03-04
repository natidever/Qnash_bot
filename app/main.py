import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes


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


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is missing in .env")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()


if __name__ == "__main__":
    main()
