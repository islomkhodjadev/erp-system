from aiogram import Router, F

from aiogram.types import CallbackQuery

import markup

import callback_data_classes

import models
from STATUS_CODES import METHOOD_STATUS

callback_handlers = Router(name=__name__)


@callback_handlers.callback_query(callback_data_classes.Language.filter())
async def change_language(query: CallbackQuery, callback_data: callback_data_classes.Language):
    language = callback_data.language
    result = await  models.change_language(query.from_user.id, language)

    if result == METHOOD_STATUS.SUCCESSFUL:
        await query.message.answer("Til muvaffaqiyatli o'zgartirildi / Язык успешно изменен", reply_markup=markup.generate_buttons(language))

    else:
        await query.message.answer("Til o'zgartirilmadi / Язык не был изменен")

    await query.message.delete()
