
from gettext import translation
import os
import django


from asgiref.sync import sync_to_async


# Initialize Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'erp.settings')
django.setup()




from django.utils import timezone
from main.models import Profile, Debt, DebtMovement, Company, PriceList, Chats, SupportMessage, Profile, TelegramUser


from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404
from asgiref.sync import sync_to_async
from models import Profile
from text import translations
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
        profile = Profile.objects.get(id_user=user_id)
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
        profile.save()
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

# # Get profile from database
# @sync_to_async
# def get_profile(telegram_id):
#     return Profile.objects.get(telegram_id=str(telegram_id))



@sync_to_async
def get_debt_overview(telegram_id):
    """
    Returns an overview of the debt information for a given profile (identified by telegram_id) as a formatted string.
    The output is in Russian or Uzbek based on the user's language preference.
    """
    try:
        # Fetch the profile using telegram_id
        profile = Profile.objects.get(telegram_id=telegram_id)
        
        if not profile.is_loggined:
            return None
        
        # Get all debts for the given profile
        debts = profile.debts.all()
        
        # Aggregate total amounts in dollars
        total_borrowed = sum(debt.total_borrowed for debt in debts)
        total_paid = sum(debt.total_paid for debt in debts)
        remaining_balance = sum(debt.remaining_balance for debt in debts)
        
        # Get the language preference (if exists, else default to English)
        language = profile.language or "ru"  # default to 'en' (English) if not set
        
        # Get the translation string for the appropriate language
        translation_strings = translations[language]
        
        # Get the formatted debt overview string
        result = translation_strings["debt_overview"].format(
            username=profile.telegram_username or "User",
            total_borrowed=total_borrowed,
            total_paid=total_paid,
            remaining_balance=remaining_balance
        )
        
        return result
    except Profile.DoesNotExist:
        language = "ru"  # Default to Russian for the "profile not found" message
        translation_strings = translations[language]
        return translation_strings["profile_not_found"].format(telegram_id=telegram_id)
    except Exception as e:
        # Handle error when retrieving debt info
        language = "ru"  # Default to Russian for error messages
        translation_strings = translations[language]
        return translation_strings["error_retrieving_debt"].format(error_message=str(e))


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

@sync_to_async
def get_language(telegram_id):
    try:
        # Try to get the Profile with the given telegram_id
        profile = Profile.objects.get(telegram_id=str(telegram_id))
        
        return profile.language
    except ObjectDoesNotExist:
        # If no profile is found with the given telegram_id
        return "standart"  # You can return an appropriate status message here





@sync_to_async
def get_price_list(telegram_id):
    """
    Returns the price list information for a given profile (identified by telegram_id).
    The output is in Russian or Uzbek based on the user's language preference.
    If no profile is found, it defaults to Russian.
    The language can be combined (Russian/Uzbek).
    """
    try:
        # Fetch the profile using telegram_id
        profile = Profile.objects.get(telegram_id=telegram_id)
        
        # Get the language preference (if exists, else default to 'ru')
        language = profile.language or "ru"  # Default to Russian if no language set
        if not profile.is_loggined:
            language = "standart"
        # Fetch the price list
        price_list = PriceList.objects.all()  # Get all price lists
        
        # Get the translation strings for the appropriate language
        translation_strings = translations[language]
        
        # Format the price list as a string (you can modify this to return more details if needed)
        price_list_details = "\n".join([
            f"{price_list_item.name}: {price_list_item.price_plintus_per_pack} ({translation_strings['per_package']}), {price_list_item.price_plintus_per_meter} ({translation_strings['per_meter']}), {price_list_item.price_accessory_per_pack} ({translation_strings['per_accessory_pack']})"
            for price_list_item in price_list
        ])
        
        # Return the formatted price list overview
        result = translation_strings["price_list"].format(price_list_details=price_list_details)
        return result
        
    except Profile.DoesNotExist:
        # If profile does not exist, use default language 'ru'
        language = "standart"
        translation_strings = translations[language]
        
        # Fetch the price list as the default
        price_list = PriceList.objects.all()
        
        # Format the price list as a string
        price_list_details = "\n".join([
            f"<b>{price_list_item.name}</b>: \n"
            f"<i>{translation_strings['per_package']}</i>: <b>{price_list_item.price_plintus_per_pack}</b>\n"
            f"<i>{translation_strings['per_meter']}</i>: <b>{price_list_item.price_plintus_per_meter}</b>\n"
            f"<i>{translation_strings['per_accessory_pack']}</i>: <b>{price_list_item.price_accessory_per_pack}</b>\n"
            "<blockquote>────────────────────────────────────────────</blockquote>"
            for price_list_item in price_list
        ])

        
        # Return the formatted price list overview
        result = translation_strings["price_list"].format(price_list_details=price_list_details)
        return result
        
    except Exception as e:
        # Handle any error when retrieving price list
        language = "ru"  # Default to Russian for error messages
        translation_strings = translations[language]
        return translation_strings["error_retrieving_price_list"].format(error_message=str(e))



@sync_to_async
def get_location(telegram_id):
    try:
        # Try to fetch profile using telegram_id
        profile = Profile.objects.get(telegram_id=telegram_id)
        
        # Get language preference, default to 'standart' (uz / ru combined) if not set
        language = profile.language or "standart"  # Default to 'standart' if no language set
        if not profile.is_loggined:
            language = "standart"
    except Profile.DoesNotExist:
        # If profile doesn't exist, use the default 'standart' language
        language = "standart"
    
    try:
        # Fetch the company info
        company = Company.objects.first()  # Assuming a single company
        
        if company:
            # Get translated labels for location information
            translation_strings = translations.get(language, translations["standart"])  # Fall back to 'standart' if language is not found
            
            # Prepare the location information dictionary
            location_info = {
                "latitude": company.location_latitude,
                "longitude": company.location_longitude,
                "address": company.address,
            }
            
            return location_info
        else:
            return {"error": "Company not found"}
    
    except Exception as e:
        return {"error": str(e)}

@sync_to_async
def get_contact_info(telegram_id):
    """
    Returns the contact information for a given company in a formatted string,
    with the output in Russian, Uzbek, or combined (uz / ru) based on the user's language preference.
    """
    try:
        # Fetch the profile using telegram_id
        profile = Profile.objects.get(telegram_id=telegram_id)
        
        # Get the language preference (if exists, else default to 'standart')
        language = profile.language or "standart"  # Default to 'standart' if no language set
        if not profile.is_loggined:
            language = "standart"
        
        # Fetch the company contact info
        company = Company.objects.first()  # Assuming you only have one company, or you can modify as needed
        
        # Get the translation strings for the appropriate language
        translation_strings = translations[language]
        
        # Create the contact information string by combining fields
        contact_info = "\n".join(filter(None, [
    f"{translation_strings['contact_number']}: {company.contact_number}" if company.contact_number else None,
    f"{translation_strings['additional_contact_number']}: {company.additional_contact_number}" if company.additional_contact_number else None,
    f"{translation_strings['email']}: {company.email}" if company.email else None,
    f"{translation_strings['telegram_username']}: {company.telegram_username}" if company.telegram_username else None,
]))
        print(contact_info)
        # Return the formatted contact info
        return contact_info
    
    except Profile.DoesNotExist:
        # If profile does not exist, use default language 'standart'
        language = "standart"
        translation_strings = translations[language]
        
        # Fetch the company contact info
        company = Company.objects.first()
        
        # Create the contact information string by combining fields
        contact_info = "\n".join(filter(None, [
    f"{translation_strings['contact_number']}: {company.contact_number}" if company.contact_number else None,
    f"{translation_strings['additional_contact_number']}: {company.additional_contact_number}" if company.additional_contact_number else None,
    f"{translation_strings['email']}: {company.email}" if company.email else None,
    f"{translation_strings['telegram_username']}: {company.telegram_username}" if company.telegram_username else None,
]))
        print(contact_info)
        # Return the formatted contact info
        return contact_info
        
    except Exception as e:
        # Handle error when retrieving contact info
        language = "ru"  # Default to Russian for error messages
        translation_strings = translations[language]
        return translation_strings["error_retrieving_contact_info"].format(error_message=str(e))





from django.shortcuts import get_object_or_404


@sync_to_async
def create_support_message_by_telegram_id(telegram_id, message):
    """
    Creates a new support message from the user with the provided telegram_id and message.
    Returns a formatted response with both Russian and Uzbek text, including the user's language preference.
    
    Args:
    - telegram_id: The Telegram ID of the user sending the support message.
    - message: The content of the support message.
    
    Returns:
    - Formatted string with the support message details in ru/uz or None if user doesn't exist.
    """
    try:
        # Fetch the user's profile using the provided telegram_id
        profile = get_object_or_404(Profile, telegram_id=telegram_id)
        
        # Create and save the new support message
        support_message = SupportMessage(profile=profile, message=message)
        support_message.save()
        
        # Get the user's language preference (or default to 'standart')
        language = profile.language or "standart"
        
        # Define the message template in both Russian and Uzbek
        formatted_response = (
            f"Сообщение от пользователя @{profile.telegram_username} ({profile.id_user}): \n "
            f"Xabar foydalanuvchidan @{profile.telegram_username} ({profile.id_user}):\n\n"
            f"Сообщение: {message} \n Xabar: {message}\n\n"
            f"Язык пользователя: {language} \n Foydalanuvchi tili: {language}"
        )
        
        # Return the formatted response
        return formatted_response
    except Profile.DoesNotExist:
        return None  # User not found, return None



@sync_to_async
def get_support_chat_id():
    chat_id = Chats.get_chat_id_by_type("support")
    return chat_id



# Function to save data
@sync_to_async
def save_telegram_user_data(message):
    # Save user and chat information
    TelegramUser.objects.update_or_create(
        user_id=message.from_user.id,
        defaults={
            "is_bot": message.from_user.is_bot,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "username": message.from_user.username,
            "language_code": message.from_user.language_code,
            "is_premium": message.from_user.is_premium,
            "chat_id": message.chat.id,
            "chat_type": message.chat.type,
            "chat_title": message.chat.title,
            "chat_username": message.chat.username,
            "chat_first_name": message.chat.first_name,
            "chat_last_name": message.chat.last_name,
            "chat_is_forum": message.chat.is_forum,
        },
    )
