from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from text import translations
import callback_data_classes
from aiogram.types import WebAppInfo
def generate_choose_language_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="ru", callback_data=callback_data_classes.Language(language="ru").pack()), 
                          InlineKeyboardButton(text="uz", callback_data=callback_data_classes.Language(language="uz").pack())],]
    )
    return keyboard


def generate_open_order_button(language):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=translations[language]["order_form"], web_app=WebAppInfo(url=f"https://winart.uz/erp/order/{language}/"))]]
    )
    return keyboard
