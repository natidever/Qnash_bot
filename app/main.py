import os

from dotenv import load_dotenv
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.handlers.commands import buy_product, confirm_order, receive_coupon, receive_phone, skip_coupon, start


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_TOKEN is missing in .env")

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_product, pattern=r"^buy:\d+$"))
    app.add_handler(CallbackQueryHandler(skip_coupon, pattern=r"^coupon:skip$"))
    app.add_handler(CallbackQueryHandler(confirm_order, pattern=r"^confirm:\d+$"))
    app.add_handler(MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), receive_phone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_coupon))
    app.run_polling()


if __name__ == "__main__":
    main()
