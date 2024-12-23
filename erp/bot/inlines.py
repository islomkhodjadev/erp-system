from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton

import callback_data_classes

def generate_choose_language_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="ru", callback_data=callback_data_classes.Language(language="ru").pack()), 
                          InlineKeyboardButton(text="uz", callback_data=callback_data_classes.Language(language="uz").pack())],]
    )
    return keyboard
