import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters
import uvicorn

from app.handlers.commands import buy_product, confirm_order, receive_coupon, receive_phone, skip_coupon, start


load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_BASE_URL = (os.getenv("WEBHOOK_BASE_URL") or "").strip()

if not TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN is missing in .env")
if not WEBHOOK_BASE_URL:
    raise RuntimeError("WEBHOOK_BASE_URL is missing in .env")
if not WEBHOOK_BASE_URL.startswith("https://"):
    raise RuntimeError("WEBHOOK_BASE_URL must start with https://")


def build_telegram_application() -> Application:
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CallbackQueryHandler(buy_product, pattern=r"^buy:\d+$"))
    telegram_app.add_handler(CallbackQueryHandler(skip_coupon, pattern=r"^coupon:skip$"))
    telegram_app.add_handler(CallbackQueryHandler(confirm_order, pattern=r"^confirm:\d+$"))
    telegram_app.add_handler(MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), receive_phone))
    telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_coupon))
    return telegram_app


telegram_application = build_telegram_application()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await telegram_application.initialize()
    await telegram_application.start()
    await telegram_application.bot.set_webhook(
        url=f"{WEBHOOK_BASE_URL.rstrip('/')}/webhook",
    )
    yield
    await telegram_application.bot.delete_webhook(drop_pending_updates=False)
    await telegram_application.stop()
    await telegram_application.shutdown()


app = FastAPI(lifespan=lifespan)


@app.post("/webhook")
async def telegram_webhook(request: Request) -> dict[str, bool]:
    payload = await request.json()
    update = Update.de_json(payload, telegram_application.bot)
    await telegram_application.process_update(update)
    return {"ok": True}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", "8000")))


if __name__ == "__main__":
    main()
