from django import forms

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label="Upload Excel File")

from django import forms
from .models import Plintus, Profile

class OrderForm(forms.Form):
    user_id = forms.CharField(
        widget=forms.HiddenInput(attrs={
            'id': 'user_id',
        })
    )
    
    plintus_code = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.TextInput(attrs={
            'id': 'plintusCode',
            'name': 'plintusCode',
            'readonly': 'readonly',
            'onclick': 'openCodePopup()',
            'value': ''
        })
    )
    number_of_plintus = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'numberOfPlintus',
            'name': 'numberOfPlintus',
            'min': '0',
            'value': '0',
            'oninput': 'validateInput(this, "plintus"); calculateTotal();'
        })
    )
    vnutrenniy_ugol = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'Внутренний угол',
            'name': 'Внутренний угол',
            'min': '0',
            'value': '0',
            'oninput': 'validateInput(this, "Внутренний угол"); calculateTotal();'
        })
    )
    naruzhniy_ugol = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'Наружный угол',
            'name': 'Наружный угол',
            'min': '0',
            'value': '0',
            'oninput': 'validateInput(this, "Наружный угол"); calculateTotal();'
        })
    )
    zaglushka_levaya = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'Заглушка левая',
            'name': 'Заглушка левая',
            'min': '0',
            'value': '0',
            'oninput': 'validateInput(this, "Заглушка левая"); calculateTotal();'
        })
    )
    zaglushka_pravaya = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'Заглушка правая',
            'name': 'Заглушка правая',
            'min': '0',
            'value': '0',
            'oninput': 'validateInput(this, "Заглушка правая"); calculateTotal();'
        })
    )
    soedinitel = forms.IntegerField(
        min_value=0,
        required=True,
        widget=forms.NumberInput(attrs={
            'id': 'Соединитель',
            'name': 'Соединитель',
            'min': '0',
            'value': '0',
            'oninput': 'validateInput(this, "Соединитель"); calculateTotal();'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch Plintus codes dynamically from the database
        plintus_choices = [(plintus.code, plintus.code) for plintus in Plintus.objects.all()]
        self.fields['plintus_code'].choices = plintus_choices

# Translation dictionary where the language code is the key, and inside it we have the translated terms.
TRANSLATIONS = {
    "ru": {
        "order_plintus_form": "Форма заказа Плинтуса",
        "plintus_code": "Код плинтуса:",
        "order_success": "Ваш заказ был успешно оформлен",
        "number_of_plintus": "Количество плинтусов",
        "plintus_total_price": "Итоговая стоимость плинтуса",
        "components": "Компоненты",
        "total_price": "Общая стоимость (Плинтус + Компоненты)",
        "not_enough_stock": "Недостаточно товара на складе. Доступно: {available} упаковок.",
        "form_invalid": "Форма не является действительной.",
        "choose_plintus": "Выберите тип плинтуса",
        "close": "Закрыть",
        "clean": "Очистить",
        "submit": "Отправить"
    },
    "uz": {
        "order_plintus_form": "Plintus buyurtma formasi",
        "order_success": "Sizning buyurtmangiz muvaffaqiyatli joylandi",
        "plintus_code": "Plyintus kodi",
        "number_of_plintus": "Plyintuslar soni",
        "plintus_total_price": "Plyintusning umumiy narxi",
        "components": "Komponentlar",
        "total_price": "Umumiy narx (Plyintus + Komponentlar)",
        "not_enough_stock": "Omborimizda etarli miqdorda mahsulot yo'q. Mavjud: {available} qadoqlar.",
        "form_invalid": "Forma amal qilmaydi.",
        "choose_plintus": "Plintus turini tanlang",
        "close": "Yopish",
        "clean": "Tozalash",
        "submit": "Yuborish"
    }
}

def translate(language, key, **kwargs):
    """
    Translate a key based on the selected language.
    """
    # Get the translation dictionary for the selected language
    translations = TRANSLATIONS.get(language, {})
    
    # Fetch the translation for the key
    translation = translations.get(key, key)  # If no translation found, return the key itself
    return translation.format(**kwargs) if kwargs else translation

def process_order(form, language="ru"):
    errors = {}
    if form.is_valid():
        # Get cleaned data from the form
        user_id = form.cleaned_data['user_id']
        plintus_code = form.cleaned_data['plintus_code']
        number_of_plintus = form.cleaned_data['number_of_plintus']
        vnutrenniy_ugol = form.cleaned_data['vnutrenniy_ugol']
        naruzhniy_ugol = form.cleaned_data['naruzhniy_ugol']
        zaglushka_levaya = form.cleaned_data['zaglushka_levaya']
        zaglushka_pravaya = form.cleaned_data['zaglushka_pravaya']
        soedinitel = form.cleaned_data['soedinitel']
        
        # Get the selected plintus
        selected_plintus = Plintus.objects.get(code=plintus_code)
        components = selected_plintus.components.all()
        if not user_id:
            errors["user_id"] = "not found"
        # Check if there is enough stock of Plintus
        if number_of_plintus > selected_plintus.count_in_packs:
            errors['plintus_code'] = translate(language, "not_enough_stock", available=selected_plintus.count_in_packs)

        # Validate stock for each component
        for component in components:
            # Get the quantity for the current component
            quantity = locals().get(component.type)
            available_component_stock = component.count_in_packs
            if quantity > available_component_stock:
                errors[component.type] = translate(language, "not_enough_stock", available=available_component_stock)

        if errors:
            return {"status": "error", "errors": errors}

        # Calculate the total price for the plintus and components
        total_price = number_of_plintus * selected_plintus.price  # Price for plintus

        # Initialize the success message with the plintus price
        success_message = f"""
            <b>{translate(language, 'order_success')}</b>:
            <b>{translate(language, 'plintus_code')}:</b> {plintus_code}
            <b>{translate(language, 'number_of_plintus')}:</b> {number_of_plintus}
            <b>{translate(language, 'plintus_total_price')}:</b> {total_price} $

            <b>{translate(language, 'components')}:</b>
            <blockquote>"""

        # Loop over components and add their prices to the success message
        for component in components:
            quantity = locals().get(component.type)
            component_total_price = quantity * component.price  # Calculate price for the component
            success_message += f"{component.type}: {quantity} x {component.price}$ = {component_total_price} $\n"
            total_price += component_total_price  # Add component price to the total

        # Close the preformatted section
        success_message += "</blockquote>"

        # Final total price
        success_message += f"\n<b>{translate(language, 'total_price')}:</b> {total_price} $"

        return {"status": "success", "message": success_message, "user_id": user_id}
    
    return {"status": "error"}
