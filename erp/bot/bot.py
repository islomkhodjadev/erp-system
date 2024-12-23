import os
import django
import sys
from dotenv import load_dotenv

# Initialize Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()


import logging
from aiogram import Bot, Dispatcher, F
import asyncio
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup


from aiogram.filters import CommandStart

from aiogram.fsm.context import FSMContext
from aiogram.types.keyboard_button import KeyboardButton
from aiogram.types import (

    KeyboardButton,

    Message,

    ReplyKeyboardMarkup,

)

from fsm import Login


# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from env file
load_dotenv()

# Use your bot token from env
API_TOKEN = os.getenv("tg_token")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Handle start command
@dp.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Login.username)
    await message.answer(text="Iltimos, foydalanuvchi nomini kiriting 🇺🇿\
        Пожалуйста, напишите имя пользователя 🇷🇺",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                   KeyboardButton(text="Tizimga kirmasdan foydalanish / Использовать без входа"),
                ]
            ],
            resize_keyboard=True,
        ))


# Run the bot
if __name__ == '__main__':
    from handlers import handlers
    from fsm_handlers import fsm_handlers
    from callback_handlers import callback_handlers
    dp.include_routers(fsm_handlers,  callback_handlers, handlers)
    asyncio.run(dp.start_polling(bot))
