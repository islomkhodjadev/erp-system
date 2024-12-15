from django.contrib import admin
from .models import Profile, Plintus, PlintusComponent, Debt, DebtMovement

# Inline for DebtMovement to be shown in Debt admin page
class DebtMovementInline(admin.TabularInline):
    model = DebtMovement
    extra = 1  # Add one empty row for new movements
    fields = ('movement_type', 'amount', 'movement_date')
    readonly_fields = ('movement_date',)

class DebtAdmin(admin.ModelAdmin):
    list_display = ('profile', 'total_borrowed', 'total_paid', 'remaining_balance', 'created_at', 'status')
    search_fields = ('profile__id_user',)  # Search by user ID (id_user)
    list_filter = ('created_at', 'profile__language')  # Filter by creation date and user language
    inlines = [DebtMovementInline]

    def status(self, obj):
        # Add a custom field for displaying the debt status (remaining balance)
        if obj.remaining_balance > 0:
            return f"Outstanding: {obj.remaining_balance}"
        return "Paid off"
    status.short_description = "Debt Status"

class DebtMovementAdmin(admin.ModelAdmin):
    list_display = ('debt', 'movement_type', 'amount', 'movement_date')
    search_fields = ('debt__profile__id_user', 'debt__profile__telegram_username')  # Search by user ID (id_user) and Telegram username
    list_filter = ('movement_type', 'movement_date')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'telegram_id', 'telegram_username', 'language')
    search_fields = ('id_user', 'telegram_id', 'telegram_username')
    list_filter = ('language','telegram_id')

class PlintusComponentAdmin(admin.ModelAdmin):
    list_display = ('plintus', 'get_type_display', 'code', 'price', 'count_in_packs')
    search_fields = ('plintus__name', 'code')
    list_filter = ('type',)

class PlintusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'count_in_packs', 'description')
    search_fields = ('name', 'code')
    list_filter = ('price',)

# Registering the models with their respective admin
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Plintus, PlintusAdmin)
admin.site.register(PlintusComponent, PlintusComponentAdmin)
admin.site.register(Debt, DebtAdmin)
admin.site.register(DebtMovement, DebtMovementAdmin)
