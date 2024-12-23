from django.shortcuts import render
from .models import Plintus, PlintusComponent
from .forms import OrderForm, process_order
import decimal, json


# Import necessary modules
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from .models import Profile
from .utils import send_message_to_user


# View to handle order submission, including form validation and price calculation
def order_view(request):
    status = False
    message = ""
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Process the order and get the result
            data = process_order(form, "uz")
            
            if data['status'] == 'success':
                status = True
                
                message = data['message']  # Assuming success message from data

                # Send a success message to Telegram user
                try:
                    # Fetch the user's telegram_id (make sure the user has a telegram_id saved in the Profile)
                    user_id = form.cleaned_data.get('user_id')  # Assuming the form has user_id
                    profile = Profile.objects.get(telegram_id=user_id)
                    telegram_id = profile.telegram_id
                    
                    # Send a success message
                    send_message_to_user(telegram_id, message)
                    status = True
                except Profile.DoesNotExist:
                    # Handle the case where the user doesn't have a Telegram ID
                    return ("Telegram ID not found for user.")
            
            else:
                status = False
                message = "error occured"  # Assuming error message from data

                # Optionally, send an error message to Telegram
                try:
                    user_id = form.cleaned_data.get('user_id')  # Assuming the form has user_id
                    profile = Profile.objects.get(telegram_id=user_id)
                    telegram_id = profile.telegram_id

                    # Send an error message
                    send_message_to_user(telegram_id, message)
                except Profile.DoesNotExist:
                    return ("Telegram ID not found for user.")
        else:
            status = False
            message = 'Form is not valid'

    else:
        form = OrderForm()

    # After processing the form, we return the form again with a status and message
    return render(request, 'order_form.html', {
        'form': form,
        'plintus_list': Plintus.objects.all(),
        'status': status,
        'message': message
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
            "type": component.get_type_display(),  # Human-readable type of the component
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
