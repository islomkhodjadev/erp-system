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
        "plintus_code": "Код плинтуса",
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
        "submit": "Отправить",
        "vnutrenniy_ugol": "Внутренний угол",
        "naruzhniy_ugol": "Наружный угол",
        "zaglushka_levaya": "Заглушка левая",
        "zaglushka_pravaya": "Заглушка правая",
        "soedinitel": "Соединитель"
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
        "submit": "Yuborish",
        "vnutrenniy_ugol": "Ichki burchak",
        "naruzhniy_ugol": "Tashqi burchak",
        "zaglushka_levaya": "Chap zaglushka",
        "zaglushka_pravaya": "O'ng zaglushka",
        "soedinitel": "Birlashtiruvchi"
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


def process_order(forms, language="ru"):
    """
    Function to process multiple orders, validate the stock of Plintus and its components, 
    and calculate the total price for each order.

    Arguments:
    forms (list): A list of OrderForm instances, each representing an individual order.
    language (str): The language code for translation (default is 'ru').

    Returns:
    dict: A dictionary with the processing result (status and message).
    """
    final_message = f"<pre><b>{translate(language, 'order_plintus_form')}:</b>\n"
    total_order_price = 0
    errors = {}

    # Component types
    component_types = ['vnutrenniy_ugol', 'naruzhniy_ugol', 'zaglushka_levaya', 'zaglushka_pravaya', 'soedinitel']

    # Process each form in the list
    for form in forms:
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

            # Get the selected plintus object
            try:
                selected_plintus = Plintus.objects.get(code=plintus_code)
            except Plintus.DoesNotExist:
                errors["plintus_code"] = translate(language, "plintus_not_found")
                continue

            components = selected_plintus.components.all()

            # Check stock for the Plintus
            if number_of_plintus > selected_plintus.count_in_packs:
                errors['plintus_code'] = translate(language, "not_enough_stock", available=selected_plintus.count_in_packs)

            # Validate stock for each component
            for component in components:
                quantity = locals().get(component.type)
                available_component_stock = component.count_in_packs
                if quantity > available_component_stock:
                    errors[component.type] = translate(language, "not_enough_stock", available=available_component_stock)

            if errors:
                continue  # Skip this order if there are errors

            # Initialize the order message with the Plintus price (including count * price breakdown)
            plintus_total_price = number_of_plintus * selected_plintus.price
            order_message = (
                f"<blockquote><b>{translate(language, 'plintus_code')}:</b> {plintus_code}\n"
                f"<b>{translate(language, 'number_of_plintus')}:</b> {number_of_plintus} x {selected_plintus.price} $ = {plintus_total_price} $ 💵\n"
            )

            # Add the Plintus price to the total order price
            total_order_price += plintus_total_price

            # Loop over the component types and add their counts and prices
            for component_type in component_types:
                quantity = locals().get(component_type)  # Get the quantity dynamically
                try:
                    # Get the component object and its price
                    component = components.get(type=component_type)
                    component_price = component.price
                    component_total_price = quantity * component_price  # Calculate total price for the component
                    order_message += f"🧩 <b>{translate(language, component_type)}:</b> {quantity} x {component_price} $ = {component_total_price} $\n"

                    # Add the component's total price to the total order price
                    total_order_price += component_total_price
                except Exception:
                    order_message += f"🧩 <b>{translate(language, component_type)}:</b> {quantity} x N/A = N/A\n"

            order_message += "</blockquote>\n"
            final_message += order_message

        else:
            errors['form_errors'] = form.errors

    # After processing all orders, return the result
    if errors:
        return {"status": "error", "errors": errors}
    
    # Final message with the total order price
    final_message += f"\n<blockquote><b>{translate(language, 'total_price')}:</b> {total_order_price} $ 💸</blockquote></pre>"
    
    return {"status": "success", "message": final_message, "total_order_price": total_order_price}

from django import forms

from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Broadcast


class BroadCastForm(forms.ModelForm):

    class Meta:
        model = Broadcast
        fields = ("content",)
        widgets = {
            "content": CKEditor5Widget(
                attrs={"class": "django_ckeditor_5"}, config_name="comment"
            )
        }
