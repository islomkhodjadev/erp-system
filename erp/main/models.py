from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid

# User profile model
class Profile(models.Model):
    """
    Represents a user's profile, including information such as:
    - user ID (custom, assigned by admin)
    - Telegram ID and username
    - Password (encrypted)
    - Language preference
    """
    LANGUAGE_CHOICES = [("uz", "uz"), ("ru", "ru")]
    name = models.CharField(max_length=250, blank=True, null=True)
    # Custom user ID
    id_user = models.CharField(max_length=50, unique=True)
    # Unique Telegram user ID
    telegram_id = models.CharField(max_length = 250, unique=True, blank=True, null=True)
    # Telegram username
    telegram_username = models.CharField(max_length=150, blank=True, null=True)
    # Encrypted password
    password = models.CharField(max_length=128)
    # Language preference (Uzbek or Russian)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, blank=True, null=True)
    is_loggined = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)

    def __str__(self):
        """
        String representation of the profile.
        Displays the profile ID and Telegram username if available.
        """
        return f"Profile {self.id} - {self.telegram_username if self.telegram_username else 'No Telegram'}"


    def set_password(self, raw_password):
        """
        Encrypt the password before storing it.
        Uses Django's built-in make_password function to store hashed passwords.
        """
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """
        Checks if the provided password matches the stored hashed password.
        Uses Django's built-in check_password function.
        """
        return check_password(raw_password, self.password)

    def save(self, *args, **kwargs):
        """
        Override the save method to hash the password before saving
        if the password is not already hashed.
        """
        if self.password and not self.password.startswith('pbkdf2_'):
            self.set_password(self.password)
        super().save(*args, **kwargs)

from decimal import Decimal, InvalidOperation

# Debt model to track user borrowings and repayments
class Debt(models.Model):
    """
    Represents the debt of a user. Tracks the total borrowed amount, 
    total paid amount, and remaining balance.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='debts')
    total_borrowed = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)
    remaining_balance = models.DecimalField(max_digits=100, decimal_places=2, default=0.00)

    
    def __str__(self):
        """
        String representation of the debt, showing the profile ID and the remaining balance.
        """
        return f"Debt {self.id} - User {self.profile.id} - Remaining Balance: {self.remaining_balance}"


# DebtMovement model to track debt-related movements (borrowing and repayments)
class DebtMovement(models.Model):
    """
    Represents a movement in the debt: either a 'debt' (borrowing) or 'paid' (repayment).
    Tracks the amount and date of the movement.
    """
    MOVEMENT_CHOICES = [
        ('debt', 'debt'),
        ('paid', 'paid')
    ]

    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=6, choices=MOVEMENT_CHOICES)
    amount = models.DecimalField(max_digits=100,decimal_places=2)
    movement_date = models.DateField(null=True, blank=True)

   
    def __str__(self):
        """
        String representation of the movement, showing the type, amount, and date of the movement.
        """
        return f"{self.get_movement_type_display()} of {self.amount} on {self.movement_date}"


# Plintus model to represent the baseboard items
class Plintus(models.Model):
    """
    Represents a baseboard item (plintus). Tracks the name, unique code, 
    price per pack, and available stock.
    """
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count_in_packs = models.PositiveIntegerField(default=0)

    def __str__(self):
        """
        String representation of the plintus, showing the name, code, and available stock.
        """
        return f"{self.name} ({self.code}) - {self.count_in_packs} packs"


# PlintusComponent model to represent components for the baseboard (plintus)
class PlintusComponent(models.Model):
    """
    Represents components that go along with a plintus (baseboard). 
    Examples include internal and external corners, caps, and connectors.
    """
    COMPONENT_TYPE_CHOICES = [
        ('vnutrenniy_ugol', 'Внутренний угол'),
        ('naruzhniy_ugol', 'Наружный угол'),
        ('zaglushka_levaya', 'Заглушка левая'),
        ('zaglushka_pravaya', 'Заглушка правая'),
        ('soedinitel', 'Соединитель'),
    ]

    plintus = models.ForeignKey(Plintus, on_delete=models.CASCADE, related_name='components')
    type = models.CharField(max_length=50, choices=COMPONENT_TYPE_CHOICES)
    code = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    count_in_packs = models.PositiveIntegerField(default=0)

    def __str__(self):
        """
        String representation of the component, showing the type, code, 
        associated plintus name, and available stock.
        """
        return f"{self.get_type_display()} ({self.code}) for {self.plintus.name} - {self.count_in_packs} packs"







class Company(models.Model):
    name = models.CharField(max_length=255, verbose_name="Company Name")
    contact_number = models.CharField(max_length=20, verbose_name="Contact Number")
    additional_contact_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Additional Contact Number")
    telegram_username = models.CharField(max_length=100, blank=True, null=True, verbose_name="Telegram Username")
    email = models.EmailField(max_length=255, blank=True, null=True, verbose_name="Email")
    location_latitude = models.CharField(max_length=250, verbose_name="Latitude")
    location_longitude = models.CharField(max_length=250, verbose_name="Longitude")
    address = models.TextField(blank=True, null=True, verbose_name="Address")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"



from django.db import models

class PriceList(models.Model):
    name = models.CharField(max_length=250)  # Name of the price list or product
    price_plintus_per_pack = models.CharField(max_length=250)  # Price for plinths per pack
    price_plintus_per_meter = models.CharField(max_length=250)  # Price for plinths per meter
    price_accessory_per_pack = models.CharField(max_length=250)  # Price for accessories per pack

    def __str__(self):
        return self.name





class SupportMessage(models.Model):
    """
    Represents a support message from a user.
    Stores the user profile, the message content, and the timestamp of the message.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='support_messages')
    message = models.TextField()  # The content of the support message
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return f"Support Message from {self.profile.telegram_username if self.profile.telegram_username else 'User'} - {self.created_at}"

    class Meta:
        verbose_name = "Support Message"
        verbose_name_plural = "Support Messages"



from django.db import models

class Chats(models.Model):
    # Define the available chat types
    SUPPORT_CHAT = 'support'
    ORDER_CHAT = 'order'
    
    CHAT_TYPE_CHOICES = [
        (SUPPORT_CHAT, 'Support Chat'),
        (ORDER_CHAT, 'Order Chat'),
    ]
    
    type = models.CharField(
        max_length=20,
        choices=CHAT_TYPE_CHOICES,  # Provide the options for the type field
        unique=True  # Make sure the type is unique
    )
    chat_id = models.CharField(max_length=250)
    @classmethod
    def get_chat_id_by_type(cls, chat_type):
        """
        Retrieve a chat by its type ('support' or 'order').
        
        Args:
        - chat_type (str): The type of the chat ('support' or 'order').
        
        Returns:
        - Chats object if found, or None if no chat is found.
        """
        if chat_type not in [cls.SUPPORT_CHAT, cls.ORDER_CHAT]:
            return None  # Invalid chat type
        
        return cls.objects.filter(type=chat_type).first().chat_id  # Return the first chat of the given type
    
    def __str__(self):
        return f"Chat Type: {self.get_type_display()}"  # Human-readable representation of the type
    
    class Meta:
        verbose_name = "Chat"
        verbose_name_plural = "Chats"






from django.db import models
from asgiref.sync import sync_to_async

# Django Model
class TelegramUser(models.Model):
    user_id = models.BigIntegerField(unique=True)
    is_bot = models.BooleanField()
    first_name = models.CharField(max_length=256)
    last_name = models.CharField(max_length=256, null=True, blank=True)
    username = models.CharField(max_length=256, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    is_premium = models.BooleanField(null=True, blank=True)
    chat_id = models.BigIntegerField()
    chat_type = models.CharField(max_length=50)
    chat_title = models.CharField(max_length=256, null=True, blank=True)
    chat_username = models.CharField(max_length=256, null=True, blank=True)
    chat_first_name = models.CharField(max_length=256, null=True, blank=True)
    chat_last_name = models.CharField(max_length=256, null=True, blank=True)
    chat_is_forum = models.BooleanField(null=True, blank=True)



from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

class Broadcast(models.Model):
    content = CKEditor5Field('Message Content', config_name='broadcast')

    def __str__(self):
        return self.content[:50]  # Display the first 50 characters
