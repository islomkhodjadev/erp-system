
import os
import django


from asgiref.sync import sync_to_async


# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()




from django.utils import timezone
from main.models import Profile, Debt, DebtMovement


from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from models import Profile

from STATUS_CODES import METHOOD_STATUS


# Function for authenticating user
@sync_to_async
def authenticate_user(user_id, password, telegram_id, telegram_username):
    """
    Authenticate the user using the provided user_id (telegram_id) and password.
    If the user exists and the password matches, a token is generated or regenerated.
    """
    # Return an error if user_id or password is not provided
    if not user_id or not password or not telegram_id:
        return METHOOD_STATUS.LACKS
    
    try:
        # Retrieve profile asynchronously
        profile = get_object_or_404(Profile, id_user=user_id)
    except Profile.DoesNotExist:
        return METHOOD_STATUS.NOTFOUND
    
    # Check if the provided password matches the stored password hash
    if not check_password(password, profile.password):
        return METHOOD_STATUS.INVALID
    
    if profile.is_blocked:
        return METHOOD_STATUS.BLOCKED
    
    profiles = Profile.objects.filter(telegram_id=telegram_id).exists()
    if profiles:
        for user in Profile.objects.filter(telegram_id=telegram_id):
            user.telegram_id = None
            user.save()
    

    # Update the profile with the new telegram_id and username
    profile.telegram_id = telegram_id
    profile.telegram_username = telegram_username
    profile.is_loggined = True
    # Save the updated profile asynchronously
    profile.save()
    
    # Return a success message
    return METHOOD_STATUS.SUCCESSFUL


@sync_to_async
def logout(telegram_id):
    try:
        profile = Profile.objects.get(telegram_id=str(telegram_id))
        profile.is_loggined = False
        return True
    except Profile.DoesNotExist:
        return False


# Check if user is already registered
@sync_to_async
def is_registered(telegram_id):
    try:
        profile = Profile.objects.get(telegram_id=str(telegram_id))
        return profile.is_loggined
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


from django.core.exceptions import ObjectDoesNotExist

@sync_to_async
def change_language(telegram_id, language):
    try:
        # Try to get the Profile with the given telegram_id
        profile = Profile.objects.get(telegram_id=str(telegram_id))
        
        # Update the language
        profile.language = language
        profile.save()

        # Return success status
        return METHOOD_STATUS.SUCCESSFUL  # Or use your constant like METHOD_STATUS.SUCCESSFUL
    except ObjectDoesNotExist:
        # If no profile is found with the given telegram_id
        return METHOOD_STATUS.NOTFOUND  # You can return an appropriate status message here
