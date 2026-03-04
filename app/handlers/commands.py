from telegram import Update
from telegram.ext import ContextTypes

from app.utils import fetch_products

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
        products = fetch_products()
        if products:
            await update.message.reply_text("Available products:")
            for item in products:
                details = f"{item['id']}. {item['name']} - {item['price']}"
                image_url = item.get("image_url")
                if image_url:
                    await update.message.reply_photo(photo=image_url, caption=details)
                else:
                    await update.message.reply_text(details)
        else:
            await update.message.reply_text("No active products found.")
