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

# class ProfileAdmin(admin.ModelAdmin):
#     list_display = ('id_user', 'telegram_id', 'telegram_username', 'language')
#     search_fields = ('id_user', 'telegram_id', 'telegram_username')
#     list_filter = ('language','telegram_id')

class PlintusComponentAdmin(admin.ModelAdmin):
    list_display = ('plintus', 'get_type_display', 'code', 'price', 'count_in_packs')
    search_fields = ('plintus__name', 'code')
    list_filter = ('type',)

class PlintusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'count_in_packs', 'description')
    search_fields = ('name', 'code')
    list_filter = ('price',)

# Registering the models with their respective admin
# admin.site.register(Profile, ProfileAdmin)
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
from .utils import create_or_update_user_data, extract_process_and_combine_sheets, read_excel_to_dfs, save_price_list_to_model   # Ensure your function is in utils.py or similar
import pandas as pd

class PlintusAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'price', 'count_in_packs')
    change_list_template = "admin/plintus_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.upload_excel, name='plintus_upload_excel'),  # Unique name
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




from django.contrib import admin
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect
from .models import Profile
from .forms import ExcelUploadForm
from .utils import use_debt_save  # Import your Excel processing function
from .excel_worker import usage_debt
        
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id_user', 'telegram_id', 'telegram_username', 'language', 'is_loggined', 'is_blocked')
    search_fields = ('id_user', 'telegram_username', 'telegram_id')
    change_list_template = "admin/profile_changelist.html"  # Custom template for list view

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.admin_site.admin_view(self.upload_excel_view), name='profile_upload_excel'),  # Unique name
        ]
        return custom_urls + urls


    def upload_excel_view(self, request):
        if request.method == "POST":
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    excel_file = request.FILES['file']

                    # Call your import function to process the Excel file
                    create_or_update_user_data(usage_debt(excel_file))

                    self.message_user(request, "Excel file uploaded and processed successfully.")
                    return HttpResponseRedirect("../")  # Redirect back to the list page

                except Exception as e:
                    # Log the error and notify the user
                    self.message_user(request, f"An error occurred while processing the Excel file: {str(e)}", level='error')
        else:
            form = ExcelUploadForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/upload_excel.html', context)

admin.site.register(Profile, ProfileAdmin)



from django.contrib import admin
from .models import Company, PriceList

# Register the Company model
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_number', 'email', 'location_latitude', 'location_longitude', 'address')
    search_fields = ('name', 'contact_number', 'email')
    list_filter = ('location_latitude', 'location_longitude')

    # Optionally, add fields for a more detailed layout in the admin
    fieldsets = (
        (None, {
            'fields': ('name', 'contact_number', 'additional_contact_number', 'telegram_username', 'email')
        }),
        ('Location Info', {
            'fields': ('location_latitude', 'location_longitude', 'address')
        }),
    )

# Register the PriceList model
@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ('name', 'price_plintus_per_pack', 'price_plintus_per_meter', 'price_accessory_per_pack')
    search_fields = ('name',)
    list_filter = ('name',)
    change_list_template = "admin/price_list_changelist.html"  # Custom template for list view

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-excel/', self.admin_site.admin_view(self.upload_excel_view), name='pricelist_upload_excel'),  # Unique name
        ]
        return custom_urls + urls


    def upload_excel_view(self, request):
        if request.method == "POST":
            form = ExcelUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    excel_file = request.FILES['file']
                    save_price_list_to_model(read_excel_to_dfs(excel_file))
                    
                    # Call your import function to process the Excel file
                    # create_or_update_pricelist_data(excel_file)

                    self.message_user(request, "Excel file uploaded and processed successfully.")
                    return HttpResponseRedirect("../")  # Redirect back to the list page

                except Exception as e:
                    # Log the error and notify the user
                    self.message_user(request, f"An error occurred while processing the Excel file: {str(e)}", level='error')
        else:
            form = ExcelUploadForm()

        context = {
            'form': form,
            'opts': self.model._meta,
        }
        return render(request, 'admin/upload_excel.html', context)
    
    # Optionally, define fields to show in the admin form
    fieldsets = (
        (None, {
            'fields': ('name',)
        }),
        ('Pricing Details', {
            'fields': ('price_plintus_per_pack', 'price_plintus_per_meter', 'price_accessory_per_pack')
        }),
    )


from django.contrib import admin
from .models import SupportMessage, Chats, TelegramUser

class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('profile', 'message', 'created_at')  # Display relevant fields in the list
    search_fields = ('profile__telegram_username', 'message')  # Enable search by username or message
    list_filter = ('created_at',)  # Filter messages by timestamp

    def get_queryset(self, request):
        """
        Override to get the list of support messages and show only relevant data.
        """
        queryset = super().get_queryset(request)
        return queryset.select_related('profile')  # This will reduce the number of queries
    
    class Meta:
        model = SupportMessage

admin.site.register(SupportMessage, SupportMessageAdmin)

class ChatsAdmin(admin.ModelAdmin):
    list_display = ('type', 'chat_id')  # Display the chat type and ID
    search_fields = ('chat_id',)  # Enable search by chat ID
    list_filter = ('type',)  # Filter by chat type (support or order)
    ordering = ('type',)  # Order by type to easily distinguish chat types

    def get_queryset(self, request):
        """
        Override to get the list of chats.
        """
        queryset = super().get_queryset(request)
        return queryset
    
    class Meta:
        model = Chats

admin.site.register(Chats, ChatsAdmin)




from django import forms
from django.contrib.admin import ModelAdmin

import requests

from dotenv import load_dotenv

load_dotenv()
import os

TG_API_TOKEN = os.getenv("tg_token")

from .forms import BroadCastForm
# Custom Admin View
class TelegramUserAdmin(ModelAdmin):
    list_display = ("user_id", "first_name", "last_name", "username", "chat_id")
    # change_list_template = "admin/telegram_user_changelist.html"  # Custom template for change list page

    # def get_urls(self):
    #     from django.urls import path
    #     from django.shortcuts import render
    #     from django.http import HttpResponseRedirect

    #     urls = super().get_urls()
    #     custom_urls = [
    #         path("broadcast/", self.admin_site.admin_view(self.broadcast_message_view), name="broadcast_message"),
    #     ]
    #     return custom_urls + urls

    # def broadcast_message_view(self, request):
    #     if request.method == "POST":
    #         form = BroadCastForm(request.POST)
    #         if form.is_valid():
    #             message = form.cleaned_data["content"]
    #             bot_token = TG_API_TOKEN
    #             url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    #             for user in TelegramUser.objects.all():
    #                 payload = {
    #                     "chat_id": user.chat_id,
    #                     "text": message,
    #                     "parse_mode": "HTML"
    #                 }
    #                 try:
    #                     response = requests.post(url, json=payload)
    #                     if not response.ok:
    #                         print(f"Failed to send message to {user.chat_id}: {response.text}")
    #                 except Exception as e:
    #                     print(f"Error sending message to {user.chat_id}: {e}")

    #             self.message_user(request, "Message broadcasted successfully!")
    #             return HttpResponseRedirect("../")
    #     else:
    #         form = BroadCastForm()

    #     context = {
    #         "form": form,
    #         "opts": self.model._meta,
    #         "app_label": self.model._meta.app_label,
    #     }
    #     return render(request, "admin/broadcast_message.html", context)

admin.site.register(TelegramUser, TelegramUserAdmin)

import html
import re

from django.contrib import admin
from .models import Broadcast

class BroadcastAdmin(admin.ModelAdmin):
    list_display = ('id', 'content')  # Display ID and content in the admin list
    search_fields = ('content',)     # Enable search functionality by content
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to send a message to all users when a broadcast is saved.
        """
        obj.content = self.remove_tags_and_decode_entities(obj.content)
        
        super().save_model(request, obj, form, change)  # Save the Broadcast instance
        bot_token = TG_API_TOKEN
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

        for user in TelegramUser.objects.all():
            payload = {
                "chat_id": user.chat_id,
                "text": obj.content,
                "parse_mode": "HTML"
            }
            try:
                response = requests.post(url, json=payload)
                if not response.ok:
                    self.message_user(request, f"Failed to send message to {user.chat_id}: {response.text}", level="error")
            except Exception as e:
                self.message_user(request, f"Error sending message to {user.chat_id}: {e}", level="error")

        self.message_user(request, "Message sent to all users successfully!")
    def remove_tags_and_decode_entities(self, content):
        """Removes <p> and <div> tags and decodes HTML entities to normal characters."""
        # Remove <p> and <div> tags using regex
        content = re.sub(r'<(p|div)[^>]*>', '', content)  # Remove opening <p> and <div>
        content = re.sub(r'</(p|div)>', '', content)     # Remove closing </p> and </div>
        
        # Decode HTML entities (e.g., &nbsp;, &lt;, &gt;, etc.)
        content = html.unescape(content)
        
        return content
# Register the model with the admin site
admin.site.register(Broadcast, BroadcastAdmin)
