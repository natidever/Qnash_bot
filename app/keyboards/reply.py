from telegram import KeyboardButton, ReplyKeyboardMarkup


def build_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text="Share phone number", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
