from decimal import Decimal

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards.inline import (
    build_buy_keyboard,
    build_confirm_order_keyboard,
    build_skip_coupon_keyboard,
)
from app.utils import (
    confirm_order_in_db,
    fetch_coupon_by_code,
    fetch_product_by_id,
    fetch_products,
    is_valid_phone_number,
)

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
                price = Decimal(str(item.get("price", "0")))
                discounted_price_value = item.get("discounted_price")
                if discounted_price_value is not None:
                    discounted_price = Decimal(str(discounted_price_value))
                    price_text = (
                        f"Price: <s>{price:.2f}</s>\n"
                        f"Discounted price: <b>{discounted_price:.2f}</b>"
                    )
                else:
                    price_text = f"Price: <b>{price:.2f}</b>"

                details = (
                    f"<b>{item['name']}</b>\n"
                    f"{price_text}"
                )
                image_url = item.get("image_url")
                keyboard = build_buy_keyboard(item["id"])
                if image_url:
                    await update.message.reply_photo(
                        photo=image_url,
                        caption=details,
                        parse_mode="HTML",
                        reply_markup=keyboard,
                    )
                else:
                    await update.message.reply_text(details, parse_mode="HTML", reply_markup=keyboard)
        else:
            await update.message.reply_text("No active products found.")


async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    callback_data = query.data or ""
    product_id = int(callback_data.split(":", maxsplit=1)[1])
    product = fetch_product_by_id(product_id)
    if not product:
        await query.answer("Product not found", show_alert=True)
        return

    context.user_data["selected_product"] = product
    context.user_data["awaiting_phone"] = True
    context.user_data["awaiting_coupon"] = False

    await query.answer()
    await query.message.reply_text("Please send your phone number we're going to call you to confirm the deliver .")


async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_phone"):
        await receive_coupon(update, context)
        return

    if not update.message:
        return

    phone_number = None
    if update.message.contact and update.message.contact.phone_number:
        phone_number = update.message.contact.phone_number
    elif update.message.text:
        phone_number = update.message.text.strip()

    if not phone_number:
        await update.message.reply_text("Please send a valid phone number.")
        return

    if not is_valid_phone_number(phone_number):
        await update.message.reply_text("Phone number must start with 09 and contain exactly 10 digits.")
        return

    context.user_data["phone_number"] = phone_number
    context.user_data["awaiting_phone"] = False
    context.user_data["awaiting_coupon"] = True
    await update.message.reply_text(
        "Do you have a coupon code? Send it now or tap Skip.",
        reply_markup=build_skip_coupon_keyboard(),
    )


async def receive_coupon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.user_data.get("awaiting_coupon"):
        return

    if not update.message or not update.message.text:
        return

    coupon_input = update.message.text.strip()
    coupon_code = "None" if coupon_input.lower() in {"skip", "no", "none"} else coupon_input

    if coupon_code != "None" and not fetch_coupon_by_code(coupon_code):
        await update.message.reply_text("Invalid coupon code. Please enter a valid coupon code or type skip.")
        return

    product = context.user_data.get("selected_product") or {}
    price = Decimal(str(product.get("discounted_price") or product.get("price") or "0"))
    product_name = product.get("name", "Unknown")
    group_size_required = product.get("group_size_required", 0)

    summary = (
        "Order summary:\n"
        f"• Product: {product_name}\n"
        f"• Price: {price:.2f}\n"
        f"• Group size to complete: {group_size_required}\n"
        f"• Coupon code: {coupon_code}"
    )

    context.user_data["coupon_code"] = coupon_code
    context.user_data["awaiting_coupon"] = False
    await send_order_summary(update, context, summary, int(product.get("id", 0)))


async def skip_coupon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()
    if not context.user_data.get("awaiting_coupon"):
        return

    product = context.user_data.get("selected_product") or {}
    price = Decimal(str(product.get("discounted_price") or product.get("price") or "0"))
    product_name = product.get("name", "Unknown")
    group_size_required = product.get("group_size_required", 0)

    coupon_code = "None"
    summary = (
        "Order summary:\n"
        f"• Product: {product_name}\n"
        f"• Price: {price:.2f}\n"
        f"• Group size to complete: {group_size_required}\n"
        f"• Coupon code: {coupon_code}"
    )

    context.user_data["coupon_code"] = coupon_code
    context.user_data["awaiting_coupon"] = False
    await send_order_summary(update, context, summary, int(product.get("id", 0)))


async def send_order_summary(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    summary: str,
    product_id: int,
) -> None:
    if update.callback_query and update.callback_query.message:
        await update.callback_query.message.reply_text(
            summary,
            reply_markup=build_confirm_order_keyboard(product_id),
        )
        return

    if update.message:
        await update.message.reply_text(
            summary,
            reply_markup=build_confirm_order_keyboard(product_id),
        )


async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if not query:
        return

    await query.answer()

    product = context.user_data.get("selected_product")
    phone_number = context.user_data.get("phone_number")
    coupon_code = context.user_data.get("coupon_code", "None")
    telegram_id = update.effective_user.id if update.effective_user else None

    if not product or not phone_number or telegram_id is None:
        await query.message.reply_text("Missing order details. Please start again from product selection.")
        return

    username = update.effective_user.username if update.effective_user else None
    result = confirm_order_in_db(product, telegram_id, phone_number, coupon_code, username=username)
    await query.message.reply_text(
        "Order confirmed.\n"
        f"Order ID: {result['order_id']}\n"
        f"Group ID: {result['group_deal_id']}\n"
        f"Participants: {result['current_participants']}/{result['group_size_required']}"
    )
