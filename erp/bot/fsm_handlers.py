from aiogram import Router
from aiogram.types import Message

from aiogram import F

import models
import inlines


from aiogram.fsm.context import FSMContext

from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types import (

    KeyboardButton,

    Message,

    ReplyKeyboardMarkup,

    
)

from fsm import Login, Support
from models import authenticate_user

from STATUS_CODES import METHOOD_STATUS
from text import translations

fsm_handlers = Router(name=__name__)
import markup


@fsm_handlers.message(F.text == "Tizimga kirmasdan foydalanish / Использовать без входа")
async def start_bot_without_login(message: Message):
    
    await message.reply("Bizning xizmatimizdan foydalanganingiz uchun rahmat!\n"
            "Спасибо, что воспользовались нашим сервисом!", reply_markup=markup.generate_buttons_not_registered())





@fsm_handlers.message(Login.username)
async def process_name(message: Message, state: FSMContext) -> None:
    
    if not message.text:
        await message.answer(
            text="Iltimos, foydalanuvchi nomini kiriting 🇺🇿"
            "Пожалуйста, напишите имя пользователя 🇷🇺",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="Tizimga kirmasdan foydalanish / Использовать без входа"),
                    ],
                    [
                        KeyboardButton(text="/login")
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
    
    if not message.text:
        await message.answer(
            "Iltimos, parolingizni kiriting 🔑"
            "Пожалуйста, введите ваш пароль 🔑",
        )
    else:
        await state.update_data(password=message.text)
        
        data = await state.get_data()
        
        
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
        elif (status == METHOOD_STATUS.NOTFOUND):
            await message.answer("Profile mavjud emas."
                     "Профиль не существует.")


        await state.clear()
        await message.delete()


from aiogram.methods.send_message import SendMessage

@fsm_handlers.message(Support.message)
async def process_support_message(message: Message, state: FSMContext) -> None:
    if not message.text:
        language = await models.get_language(message.from_user.id)
        await message.answer(translations[language]["write_question"])
    text = message.text
    await state.clear()

    text = await models.create_support_message_by_telegram_id(message.from_user.id, text)
    chat_id = await models.get_support_chat_id()
    await message.bot(SendMessage(chat_id=chat_id, text=text))
    await message.answer("Наша команда поддержки ответит вам как можно скорее\nBizning qo'llab-quvvatlash jamoamiz imkon qadar tezroq javob beradi.")


