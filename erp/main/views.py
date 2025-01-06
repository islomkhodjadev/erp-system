from django.shortcuts import render
from .models import Plintus, PlintusComponent
from .forms import OrderForm, process_order
import decimal, json

from .forms import translate

# Import necessary modules
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from .models import Profile
from .utils import inform_order_user_gorup, send_message_to_telegram


# View to handle order submission, including form validation and price calculation

# View to handle order submission, including form validation and price calculation
def order_view(request, language):
    """
    Handles order submissions via POST requests, validates and processes them, and sends a response.

    Arguments:
    request: Django HttpRequest object.
    language: Language code for translations.
    """
    status = False
    message = ""

    if request.method == 'POST':
        # Read JSON data from the request body
        data = json.loads(request.body)
        user_id = data.get('user_id')
        order_data = data.get('order_data', [])
        
        # if not user_id:
        #     return JsonResponse({"status": "error", "message": "User ID is required."}, status=400)

        # Initialize the final message and total price for the order
        errors = {}
        forms = []

        # Loop through all the orders and process each one
        for order in order_data:
            # Create the form data for each order
            form_data = {
                'user_id': user_id,
                'plintus_code': order.get('plintus_code'),
                'number_of_plintus': order.get('number_of_plintus', 0),
                'vnutrenniy_ugol': order.get('vnutrenniy_ugol', 0),
                'naruzhniy_ugol': order.get('naruzhniy_ugol', 0),
                'zaglushka_levaya': order.get('zaglushka_levaya', 0),
                'zaglushka_pravaya': order.get('zaglushka_pravaya', 0),
                'soedinitel': order.get('soedinitel', 0)
            }

            # Instantiate the form
            form = OrderForm(form_data)
            forms.append(form)

        # Process the order using the `process_order` function
        result = process_order(forms, language)

        if result['status'] == 'error':
            status = False
            message = f"Errors occurred while processing the orders: {json.dumps(result['errors'])}"
            return JsonResponse({"status": "error", "message": message}, status=400)

        else:
            status = True
            final_message = result['message']
            total_order_price = result['total_order_price']
            message = f"Total order price: {total_order_price} $"

            # Send the final message to the user (via Telegram or another method)
            try:
                print(final_message)
                # Replace '1099766821' with user_id or profile.telegram_id as needed
                send_message_to_telegram("1099766821", final_message)  # Send the message to the user
            except Profile.DoesNotExist:
                return JsonResponse({"status": "error", "message": "Telegram ID not found for the user."}, status=400)

            return JsonResponse({"status": "success", "message": message}, status=200)

    else:
        form = OrderForm()

    # For GET requests, render the order form template
    plintus_queryset = Plintus.objects.all()
    # Convert the queryset to a list of dictionaries
    plintus_list = list(plintus_queryset.values('code'))
    
    return render(request, 'order_form.html', {
        'form': form,
        'plintus_list': json.dumps(plintus_list),
        'status': status,
        'message': message,
        "choose_plintus": translate(language, "choose_plintus"),
        "close": translate(language, "close"),
        "total_price": translate(language, "total_price"),
        "clean": translate(language, "clean"),
        "submit": translate(language, "submit"),
        "order_plintus_form": translate(language, "order_plintus_form"),
        "plintus_code": translate(language, "plintus_code"),
        "number_of_plintus": translate(language, "number_of_plintus"),
        "vnutrenniy_ugol": translate(language, "vnutrenniy_ugol"),
        "naruzhniy_ugol": translate(language, "naruzhniy_ugol"),
        "zaglushka_levaya": translate(language, "zaglushka_levaya"),
        "zaglushka_pravaya": translate(language, "zaglushka_pravaya"),
        "soedinitel": translate(language, "soedinitel"),
    })

# View to fetch the components related to a specific Plintus by its code
def get_components_by_plintus_code(request, plintus_code):
    """
    View that returns a list of components related to a specific Plintus identified by its code.
    Returns the data in JSON format, including the Plintus details and its components.
    """
    # Get the Plintus object by its unique code
    plintus = get_object_or_404(Plintus, code=plintus_code)
    
    # Retrieve all components related to this Plintus
    components = plintus.components.all()
    
    # Prepare the components data in JSON-friendly format
    components_data = [
        {
            "id": component.id,
            "type": component.type,  # Human-readable type of the component
            "code": component.code,
            "price": float(component.price),  # Convert Decimal to float for JSON
            "count_in_packs": component.count_in_packs,  # Stock of the component
        }
        for component in components
    ]
    
    # Return a JSON response with the Plintus and its components data
    return JsonResponse({
        "plintus": {
            "id": plintus.id,
            "name": plintus.name,
            "code": plintus.code,
            "price": float(plintus.price),  # Convert Decimal to float for JSON
            "count_in_packs": plintus.count_in_packs,  # Stock of the Plintus
        },
        "components": components_data,  # List of components for the Plintus
    }, safe=False)
