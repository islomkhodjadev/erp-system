from aiogram import Router

from aiogram import types, F

from aiogram.fsm.context import FSMContext

from text import translations
from aiogram.types.web_app_info import WebAppInfo 
from filters import Registered, CheckCommand
from aiogram.filters import  and_f
import inlines
from fsm import Support

handlers = Router(name=__name__)
import models
import markup
# Handler for order form button.in_(both Russian and Uzbek
@handlers.message(and_f(Registered(), CheckCommand("order_form")))
async def cmd_order_form_button(message: types.Message):
    language = await models.get_language(message.from_user.id)
    await message.reply("order", reply_markup=inlines.generate_open_order_button(language))


# Handle contacts commanddebt
@handlers.message(and_f(Registered(), CheckCommand("debts")))
async def cmd_contacts_button(message: types.Message):
    text = await models.get_debt_overview(message.from_user.id)
    await message.reply(text)


@handlers.message(CheckCommand("price"))
async def cmd_price_button(message: types.Message):
    text  = await models.get_price_list(message.from_user.id)
    await message.reply(text)  # Example price.in_(Uzbek


# Handle location command
@handlers.message(CheckCommand("location"))
async def cmd_location_button(message: types.Message):
    location = await models.get_location(message.from_user.id)
    await message.answer(location["address"])
    await message.answer_location(latitude=location["latitude"], longitude=location["longitude"])



# Handle contacts command
@handlers.message(and_f(CheckCommand("contacts")))
async def cmd_contacts_button(message: types.Message):
    text = await models.get_contact_info(message.from_user.id)
    await message.reply(text)



@handlers.message(and_f(Registered(), CheckCommand("support")))
async def command_start(message: types.Message, state: FSMContext) -> None:
    await state.set_state(Support.message)
    language = await models.get_language(message.from_user.id)
    await message.answer(translations[language]["write_question"])


# # Handler for see profile.in_(both Russian and Uzbek
# @handlers.message(and_f(Registered(), CheckCommand("see_profile")))
# async def cmd_see_profile_button(message: types.Message):
    
#     await message.reply("🧑‍💻 *Foydalanuvchi profili:*\n" 
#                             "👤 *Foydalanuvchi nomi:* {username}\n"
#                             "🌍 *Til:* {language}")


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
                        "Спасибо, что воспользовались нашим сервисом!", reply_markup=markup.generate_buttons_not_registered())
