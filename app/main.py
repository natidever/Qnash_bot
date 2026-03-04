import os

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler

from app.handlers.commands import start


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
