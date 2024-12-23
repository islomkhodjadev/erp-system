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

# Debt model to track user borrowings and repayments
class Debt(models.Model):
    """
    Represents the debt of a user. Tracks the total borrowed amount, 
    total paid amount, and remaining balance.
    """
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='debts')
    total_borrowed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        """
        Override the save method to automatically calculate the remaining balance.
        The remaining balance is the difference between total borrowed and total paid amounts.
        """
        self.remaining_balance = self.total_borrowed - self.total_paid
        super().save(*args, **kwargs)

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    movement_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the save method to update the debt amounts based on the movement type.
        - If 'debt', add to the total borrowed.
        - If 'paid', add to the total paid.
        """
        if self.movement_type == 'debt':
            # Add to the total borrowed amount
            self.debt.total_borrowed += self.amount
        elif self.movement_type == 'paid':
            # Add to the total paid amount
            self.debt.total_paid += self.amount

        super().save(*args, **kwargs)

        # Recalculate and save the debt to update the remaining balance
        self.debt.save()

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




