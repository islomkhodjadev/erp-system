translations = {
    "uz": {
        "order_form": "Plintus buyurtma berish",
        "debts": "Qarzdorliklar",
        "contacts": "Kontaktlar",
        "location": "Joylashuv",
        "support": "Qo'llab-quvvatlash",
        "price": "Narx",
        "see_profile": "Profilni ko'rish",
        "change_language": "Tilni o'zgartirish",
        "logout": "Chiqish",
  "debt_overview": "💰 **{username} uchun qarz haqida ma'lumot**:\n"
                         "📌 **Jami qarz olingan:** ${total_borrowed:,.2f}\n"
                         "✅ **Jami to'langan:** ${total_paid:,.2f}\n"
                         "❗ **Qarz qoldig'i:** ${remaining_balance:,.2f}\n",
        "profile_not_found": "⚠️ Telegram ID {telegram_id} uchun profil topilmadi.",
        "error_retrieving_debt": "⚠️ Qarz ma'lumotlarini olishda xatolik yuz berdi: {error_message}",
           "price_list": "Narxlar ro'yxati:\n{price_list_details}",
        "per_package": "paket uchun",
        "per_meter": "metr uchun",
        "per_accessory_pack": "aksessuarlar paket uchun",
        "error_retrieving_price_list": "Narxlar ro'yxatini olishda xatolik: {error_message}",
          "contact_number": "Aloqa raqami",
        "additional_contact_number": "Qo'shimcha aloqa raqami",
        "email": "Elektron pochta",
        "telegram_username": "Telegram foydalanuvchi nomi",
        "location": "Joylashuv",
        "address": "Manzil",
        "latitude": "Kenglik",
        "longitude": "Uzunlik",
        "write_question": "Iltimos, savolingizni yozing."

    },
    "ru": {
        "order_form": "Заказать плинтус",
        "debts": "Долги",
        "contacts": "Контакты",
        "location": "Местоположение",
        "support": "Поддержка",
        "price": "Цена",
        "see_profile": "Посмотреть профиль",
        "change_language": "Изменить язык",
        "logout": "Выход",
        "debt_overview": "💰 **Обзор задолженности для {username}**:\n"
                         "📌 **Всего взято в долг:** ${total_borrowed:,.2f}\n"
                         "✅ **Всего выплачено:** ${total_paid:,.2f}\n"
                         "❗ **Остаток долга:** ${remaining_balance:,.2f}\n",
        "profile_not_found": "⚠️ Профиль с Telegram ID {telegram_id} не найден.",
        "error_retrieving_debt": "⚠️ Ошибка при получении информации о долге: {error_message}",
          "price_list": "Список цен:\n{price_list_details}",
        "per_package": "за упаковку",
        "per_meter": "за метр",
        "per_accessory_pack": "за комплект аксессуаров",
        "error_retrieving_price_list": "Ошибка при получении списка цен: {error_message}",
          "contact_number": "Контактный номер",
        "additional_contact_number": "Дополнительный контактный номер",
        "email": "Электронная почта",
        "telegram_username": "Телеграм-имя",
        "location": "Местоположение",
        "address": "Адрес",
        "latitude": "Широта",
        "longitude": "Долгота",

        "write_question": "Пожалуйста, напишите ваш вопрос."

  
    },
    "standart": {
        "order_form": "Plintus buyurtma berish",
        "debts": "Qarzdorliklar",
        "support": "Qo'llab-quvvatlash",
        "see_profile": "Profilni ko'rish",
        "change_language": "Tilni o'zgartirish",
        "contacts": "Kontaktlar / Контакты",
        "price": "Narx / Цена",
    "login": "Kirish / Вход",
      "price_list": "Список цен / Narxlar ro'yxati:\n{price_list_details}",
        "per_package": "за упаковку / paket uchun",
        "per_meter": "за метр / metr uchun",
        "per_accessory_pack": "за комплект аксессуаров / aksessuarlar paket uchun",
        "error_retrieving_price_list": "Ошибка при получении списка цен / Narxlar ro'yxatini olishda xatolik: {error_message}",
    "contact_number": "Aloqa raqami / Контактный номер",
        "additional_contact_number": "Qo'shimcha aloqa raqami / Дополнительный контактный номер",
        "email": "Elektron pochta / Электронная почта",
        "telegram_username": "Telegram Foydalanuvchi nomi / Telegram Имя пользователя",
        "location": "Manzil / Местоположение",
        "address": "Manzil / Адрес",
        "latitude": "Kenglik / Широта",
        "longitude": "Uzunlik / Долгота",
        "logout": "Chiqish / Выход",
        "write_question": "Iltimos, savolingizni yozing. / Пожалуйста, напишите ваш вопрос."
}

}


debt_templates = {
    "uz": (
        "💼 *Qarz haqida ma'lumot*\n\n"
        "📅 Sana: {current_date}\n"
        "💰 *Jami qarz summasi:* {total_borrowed}\n"
        "✅ *Jami to'langan summa:* {total_paid}\n"
        "⚠️ *Qolgan qarz:* {remaining_balance}\n\n"
        "🕰️ Qarzlaringizni o'z vaqtida to'lashni unutmang! 🙏\n"
        "Bizning xizmatlarimizdan foydalanganingiz uchun rahmat! 💖"
    ),
    "ru": (
        "💼 *Информация о долге*\n\n"
        "📅 Дата: {current_date}\n"
        "💰 *Общая сумма займа:* {total_borrowed}\n"
        "✅ *Общая сумма погашений:* {total_paid}\n"
        "⚠️ *Оставшаяся задолженность:* {remaining_balance}\n\n"
        "🕰️ Не забудьте вовремя оплатить долг! 🙏\n"
        "Спасибо, что пользуетесь нашими услугами! 💖"
    )
}
