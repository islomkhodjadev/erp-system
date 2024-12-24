from aiogram import Router

from aiogram import types, F

from aiogram.fsm.context import FSMContext

from text import translations
from aiogram.types.web_app_info import WebAppInfo 
from filters import Registered, CheckCommand
from aiogram.filters import  and_f
import inlines

handlers = Router(name=__name__)
import models

# Handler for order form button.in_(both Russian and Uzbek
@handlers.message(and_f(Registered(), CheckCommand("order_form")))
async def cmd_order_form_button(message: types.Message):
    language = await models.get_language(message.from_user.id)
    await message.reply("order", reply_markup=inlines.generate_open_order_button(language))


# Handle contacts commanddebt
@handlers.message(and_f(Registered(), CheckCommand("debts")))
async def cmd_contacts_button(message: types.Message):
    await message.reply("Контакты:\nEmail: contact@example.com\nТел.: +987654321")


@handlers.message(CheckCommand("price"))
async def cmd_price_button(message: types.Message):
    await message.reply("📊 *Narx*: {price} so'm")  # Example price.in_(Uzbek


# Handle location command
@handlers.message(CheckCommand("location"))
async def cmd_location_button(message: types.Message):
    await message.answer_location(latitude=41.304797, longitude=69.347640)



# Handle contacts command
@handlers.message(and_f(Registered(), CheckCommand("contacts")))
async def cmd_contacts_button(message: types.Message):
    await message.reply("Контакты:\nEmail: contact@example.com\nТел.: +987654321")



@handlers.message(and_f(Registered(), CheckCommand("support")))
async def cmd_support_button(message: types.Message):
    await message.reply("Контакты для поддержки:\nEmail: support@example.com\nТел.: +123456789")

# Handler for see profile.in_(both Russian and Uzbek
@handlers.message(and_f(Registered(), CheckCommand("see_profile")))
async def cmd_see_profile_button(message: types.Message):
    
    await message.reply("🧑‍💻 *Foydalanuvchi profili:*\n" 
                            "👤 *Foydalanuvchi nomi:* {username}\n"
                            "🌍 *Til:* {language}")


# Handler for change language button
@handlers.message(and_f(Registered(), CheckCommand("change_language")))
async def cmd_change_language_button(message: types.Message):
    await message.answer(
            "Iltimos, tilni tanlang"
            "Пожалуйста, выберите язык", reply_markup=inlines.generate_choose_language_button())


# Handler for logout button
@handlers.message(and_f(Registered(), CheckCommand("logout")))
async def cmd_logout_button(message: types.Message):
    await models.logout(message.from_user.id)
    await message.reply("Bizning xizmatimizdan foydalanganingiz uchun rahmat!\n"
                        "Спасибо, что воспользовались нашим сервисом!")
