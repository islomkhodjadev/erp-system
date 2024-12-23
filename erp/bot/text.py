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
