from django.db import models

# User profile model
class Profile(models.Model):
    LANGUAGE_CHOICES = [("uz", "uz"), ("ru", "ru")]
    id_user = models.CharField(max_length=50, unique=True)  # Custom ID assigned by admin
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)  # Unique Telegram user ID
    telegram_username = models.CharField(max_length=150, blank=True, null=True)
    password = models.CharField(max_length=128)  # Encrypted password
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, blank=True, null=True)  # Language preference
    
    def __str__(self):
        return f"Profile {self.id} - {self.telegram_username if self.telegram_username else 'No Telegram'}"

# Plintus model (Baseboard itself)
class Plintus(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)  # Unique code for the plintus
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per pack
    count_in_packs = models.PositiveIntegerField(default=0)  # Number of packs available

    def __str__(self):
        return f"{self.name} ({self.code}) - {self.count_in_packs} packs"

# PlintusComponent model
class PlintusComponent(models.Model):
    COMPONENT_TYPE_CHOICES = [
        ('vnutrenniy_ugol', 'Vnutrenniy Ugol'),
        ('naruzhniy_ugol', 'Naruzhniy Ugol'),
        ('zaglushka_levaya', 'Zaglushka Levaya'),
        ('zaglushka_pravaya', 'Zaglushka Pravaya'),
        ('soedinitel', 'Soedinitel'),
    ]

    plintus = models.ForeignKey(Plintus, on_delete=models.CASCADE, related_name='components')
    type = models.CharField(max_length=50, choices=COMPONENT_TYPE_CHOICES)
    code = models.CharField(max_length=50, unique=True)  # Unique code for the component
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per pack
    count_in_packs = models.PositiveIntegerField(default=0)  # Number of packs available

    def __str__(self):
        return f"{self.get_type_display()} ({self.code}) for {self.plintus.name} - {self.count_in_packs} packs"

# Debt model (Modified)
class Debt(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='debts')
    total_borrowed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount borrowed
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Total amount paid
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Remaining balance
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Automatically update the remaining balance
        self.remaining_balance = self.total_borrowed - self.total_paid
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Debt {self.id} - User {self.profile.id} - Remaining Balance: {self.remaining_balance}"

# DebtMovement model (To track borrowing and repayment movements)
class DebtMovement(models.Model):
    MOVEMENT_CHOICES = [
        ('borrow', 'Borrowed'),
        ('repay', 'Repayment')
    ]

    debt = models.ForeignKey(Debt, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=6, choices=MOVEMENT_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    movement_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.movement_type == 'borrow':
            # Add to the total borrowed amount
            self.debt.total_borrowed += self.amount
        elif self.movement_type == 'repay':
            # Add to the total paid amount
            self.debt.total_paid += self.amount

        # Save the movement
        super().save(*args, **kwargs)

        # Save the debt to update the remaining balance
        self.debt.save()

    def __str__(self):
        return f"{self.get_movement_type_display()} of {self.amount} on {self.movement_date}"

