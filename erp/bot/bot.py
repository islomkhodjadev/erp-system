import os
import django
import sys
from dotenv import load_dotenv

# Initialize Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()

# Now you can import your Django models
from main.models import Profile, Debt, DebtMovement

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import asyncio
from asgiref.sync import sync_to_async
from aiogram.types.web_app_info import WebAppInfo
from aiogram.types.reply_keyboard_markup import ReplyKeyboardMarkup
from aiogram.types.keyboard_button import KeyboardButton

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load environment variables from .env file
load_dotenv()

# Use your bot token from .env
API_TOKEN = os.getenv("tg_token")

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# User registration and login state tracking
USER_REGISTRATION = {}

# Sync database functions with sync_to_async
@sync_to_async
def create_profile(user_id, username, language, password):
    return Profile.objects.create(
        id_user=str(user_id),
        telegram_username=username,
        language=language,
        password=password
    )

# Check if user is already registered
@sync_to_async
def is_registered(user_id):
    try:
        Profile.objects.get(id_user=str(user_id))
        return True
    except Profile.DoesNotExist:
        return False

# Get profile from database
@sync_to_async
def get_profile(user_id):
    return Profile.objects.get(id_user=str(user_id))

# Validate user password
@sync_to_async
def validate_user_password(user_id, password):
    try:
        profile = Profile.objects.get(id_user=str(user_id))
        return profile.password == password
    except Profile.DoesNotExist:
        return False

# Get or create a debt record for the user
@sync_to_async
def get_or_create_debt(profile):
    return Debt.objects.get_or_create(profile=profile)

# Create a debt movement (borrow or repay)
@sync_to_async
def create_debt_movement(debt, movement_type, amount):
    DebtMovement.objects.create(debt=debt, movement_type=movement_type, amount=amount, movement_date=timezone.now())

# Save the debt
@sync_to_async
def save_debt(debt):
    debt.save()

# Handle start command
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    markup = ReplyKeyboardMarkup(
        keyboard=[
        
            [KeyboardButton(
                text="Форма заказа Плинтуса",
                web_app=WebAppInfo(url="https://ringai.uz/erp/index.html")
            ), KeyboardButton(text="Долги")],
            [KeyboardButton(text="Контакты"),
             KeyboardButton(text="Местоположение")],
            [KeyboardButton(text="Поддержка")],
        
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите действие:", reply_markup=markup)


# Handle support command
@dp.message(lambda message: message.text == "Поддержка")
async def cmd_support_button(message: types.Message):
    await message.reply("Контакты для поддержки:\nEmail: support@example.com\nТел.: +123456789")

# Handle location command
@dp.message(lambda message: message.text == "Местоположение")
async def cmd_location_button(message: types.Message):
    await message.answer_location(latitude=41.304797, longitude=69.347640)

# Handle contacts command
@dp.message(lambda message: message.text == "Контакты")
async def cmd_contacts_button(message: types.Message):
    await message.reply("Контакты:\nEmail: contact@example.com\nТел.: +987654321")

@dp.message(lambda message: message.text == "Долги")
async def cmd_depts_button(message: types.Message):
    # Dummy data
    current_date = "15.12.2024"
    total_borrowed = "50,000 ₽"
    total_paid = "30,000 ₽"
    remaining_balance = "20,000 ₽"
    
    # Beautifully formatted message
    debt_info = (
        f"💼 *Информация о долге*\n\n"
        f"📅 Дата: {current_date}\n"
        f"💰 *Общая сумма займа:* {total_borrowed}\n"
        f"✅ *Общая сумма погашений:* {total_paid}\n"
        f"⚠️ *Оставшаяся задолженность:* {remaining_balance}\n\n"
        f"🕰️ Не забудьте вовремя оплатить долг! 🙏\n"
        f"Спасибо, что пользуетесь нашими услугами! 💖"
    )
    await message.reply(debt_info)


# Run the bot
if __name__ == '__main__':
    asyncio.run(dp.start_polling(bot))
