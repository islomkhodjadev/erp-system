from django.contrib import admin
from .models import Profile, Plintus, PlintusComponent, Debt, DebtMovement

# Inline for DebtMovement to be shown in Debt admin page
class DebtMovementInline(admin.TabularInline):
    model = DebtMovement
    extra = 1  # Add one empty row for new movements
    fields = ('movement_type', 'amount', 'movement_date')
    readonly_fields = ('movement_date',)

class DebtAdmin(admin.ModelAdmin):
    list_display = ('profile', 'total_borrowed', 'total_paid', 'remaining_balance', 'status')
    search_fields = ('profile__id_user',)  # Search by user ID (id_user)
    list_filter = ( 'profile__language',)  # Filter by creation date and user language
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
# admin.site.register(Plintus, PlintusAdmin)
admin.site.register(PlintusComponent, PlintusComponentAdmin)
admin.site.register(Debt, DebtAdmin)
admin.site.register(DebtMovement, DebtMovementAdmin)



from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Plintus, PlintusComponent
from .forms import ExcelUploadForm
from .utils import extract_process_and_combine_sheets  # Ensure your function is in utils.py or similar
import pandas as pd

class PlintusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'count_in_packs')
    change_list_template = "admin/plintus_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel, name='upload_excel'),
        ]
        return custom_urls + urls

    def upload_excel(self, request):
        if request.method == "POST":
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['file']
                try:
                    # Process the Excel file
                    sheet_names = ["100мм", "80 мм", "72 мм", "55 мм", "67 мм", "58 мм"]
                    processed_data = extract_process_and_combine_sheets(excel_file, sheet_names)

                    # Save or update data in the database
                    for _, row in processed_data.iterrows():
                        # Convert NaN prices to 0 before processing
                        for i in range(1, 7):  # Loop for price_1 to price_6
                            price_column = f'price_{i}'
                            if pd.isna(row.get(price_column)):
                                row[price_column] = 0  # Replace NaN price with 0

                        # Save or update Plintus
                        plintus, _ = Plintus.objects.update_or_create(
                            code=row['code'],
                            defaults={
                                'name': row['name_1'],
                                'price': row.get('price_1', 0),
                                'count_in_packs': row.get('packages_1', 0),
                            }
                        )

                        # Save or update Plintus Components
                        components = [
                            ('vnutrenniy_ugol', row.get('packages_2'), row.get('price_2')),
                            ('naruzhniy_ugol', row.get('packages_3'), row.get('price_3')),
                            ('zaglushka_levaya', row.get('packages_4'), row.get('price_4')),
                            ('zaglushka_pravaya', row.get('packages_5'), row.get('price_5')),
                            ('soedinitel', row.get('packages_6'), row.get('price_6')),
                        ]

                        for component_type, count, price in components:
                            if component_type and count is not None:  # Ensure we have valid data
                                # Generate a unique code for the component
                                component_code = f"{plintus.code}_{component_type}"  # Ensure the code is unique

                                # Use `update_or_create` to update existing components
                                PlintusComponent.objects.update_or_create(
                                    code=component_code,  # Unique code for the component
                                    defaults={
                                        'plintus': plintus,
                                        'type': component_type,
                                        'count_in_packs': count,
                                        'price': price,
                                    }
                                )

                    self.message_user(request, "Excel data uploaded and database updated successfully.")
                    return HttpResponseRedirect("../")  # Redirect back to the change list

                except Exception as e:
                    self.message_user(request, f"Error processing file: {e}", level="error")

        else:
            form = ExcelUploadForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/upload_excel.html', context)

admin.site.register(Plintus, PlintusAdmin)
