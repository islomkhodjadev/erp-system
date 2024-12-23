from aiogram import Router
from aiogram.types import Message

from aiogram import F

import inlines


from aiogram.fsm.context import FSMContext

from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types import (

    KeyboardButton,

    Message,

    ReplyKeyboardMarkup,

    
)

from fsm import Login
from models import authenticate_user

from STATUS_CODES import METHOOD_STATUS


fsm_handlers = Router(name=__name__)



@fsm_handlers.message(F.text == "Use without login / Использовать без входа")
async def start_bot_without_login(message: Message):
    
    markup = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Контакты"),
             KeyboardButton(text="Местоположение")],
        
        ],
        resize_keyboard=True
    )
    await message.answer(reply_markup=markup)



@fsm_handlers.message(Login.username)
async def process_name(message: Message, state: FSMContext) -> None:
    print("login")
    if not message.text:
        await message.answer(
            text="Iltimos, foydalanuvchi nomini kiriting 🇺🇿"
            "Пожалуйста, напишите имя пользователя 🇷🇺",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Tizimga kirmasdan foydalanish / Использовать без входа"),
                    ]
                ],
                resize_keyboard=True,
            )
        )
    else:
        await state.update_data(username=message.text)
        await state.set_state(Login.password)
        await message.answer(
            "Iltimos, parolingizni kiriting 🔑"
            "Пожалуйста, введите ваш пароль 🔑",
        )


@fsm_handlers.message(Login.password)
async def process_password(message: Message, state: FSMContext) -> None:
    print("password")
    if not message.text:
        await message.answer(
            "Iltimos, parolingizni kiriting 🔑"
            "Пожалуйста, введите ваш пароль 🔑",
        )
    else:
        await state.update_data(password=message.text)
        
        data = await state.get_data()
        print(data)
        
        status = await authenticate_user(data["username"], data["password"], message.from_user.id, message.from_user.username)
        if (status == METHOOD_STATUS.SUCCESSFUL):
            await message.answer(
            "Iltimos, tilni tanlang\n"
            "Пожалуйста, выберите язык", reply_markup=inlines.generate_choose_language_button())


        elif (status == METHOOD_STATUS.BLOCKED):
            await message.answer(
                "Siz bloklanganingiz uchun kirish mumkin emas. Iltimos, qo'llab-quvvatlash bilan bog'laning. ❌"
                "Вы заблокированы, и вход невозможен. Пожалуйста, свяжитесь с поддержкой. ❌"
            )
        elif (status == METHOOD_STATUS.INVALID):
            await message.answer("Parol noto‘g‘ri."
                "Пароль неверный.")
        await state.clear()
        await message.delete()
