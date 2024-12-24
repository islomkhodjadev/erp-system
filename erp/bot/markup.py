from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo
from text import translations


def generate_buttons(language):
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=translations[language]["order_form"],
                    
                    
                ),
                KeyboardButton(text=translations[language]["debts"])
            ],
            [
                KeyboardButton(text=translations[language]["price"]),
                KeyboardButton(text=translations[language]["contacts"]),
                KeyboardButton(text=translations[language]["location"])
            ],
            [
                KeyboardButton(text=translations[language]["support"])
            ],
            [
              KeyboardButton(text=translations[language]["see_profile"]),
              KeyboardButton(text=translations[language]["change_language"]),
              KeyboardButton(text=translations[language]["logout"])
            ]
        ],
        resize_keyboard=True,
    )
