from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def build_skip_coupon_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(text="Skip coupon", callback_data="coupon:skip")]]
    )
