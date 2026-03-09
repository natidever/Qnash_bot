from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_skip_coupon_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Skip coupon", callback_data="coupon:skip")]]
    )


def build_buy_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Buy", callback_data=f"buy:{product_id}")]]
    )


def build_confirm_order_keyboard(product_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Confirm", callback_data=f"confirm:{product_id}")]]
    )
