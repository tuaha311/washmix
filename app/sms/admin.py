from django.contrib import admin
from django.urls import reverse
from users.admin import ClientAdmin
from sms.views import outbound_sms, get_context
from django.utils.html import format_html
from users.models.client import Client

from .models import SMSTemplate, SendSMS


@admin.register(SMSTemplate)
class SMSAdmin(admin.ModelAdmin):
    change_list_template = "assets/sms_change_form.html"
    
@admin.register(SendSMS)
class SendSMSAdmin(ClientAdmin):
    actions = ["send_sms"]

    def get_context(self, request):
        context = get_context()  # Call your get_context function to populate context
        change_list_template = "outbound_send_sms.html"  # Default template

        return {
            **context,
            "change_list_template": change_list_template,
        }

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context.update(self.get_context(request))

        # Set the change_list_template based on the context data
        self.change_list_template = extra_context.get("change_list_template", "outbound_send_sms.html")

        return super().changelist_view(request, extra_context=extra_context)

    def send_sms(self, request, queryset):
        pass
            
    def get_queryset(self, request):
        # Get the queryset of SendSMS instances
        queryset = super().get_queryset(request)
        
        zip_code_param = request.POST.get("zip_code")
        city_param = request.POST.get("city")
        address_param = request.POST.get("address")
        phone_param = request.POST.get("phone")

        # If a zip code parameter is provided, filter the queryset
        if zip_code_param:
           queryset = Client.objects.filter(billing_address__zip_code=zip_code_param)
        elif city_param:
           queryset = Client.objects.filter(billing_address__address_line_1__icontains=city_param)   
        elif address_param:
           queryset = Client.objects.filter(billing_address__address_line_1=address_param)
        elif phone_param:
           queryset = Client.objects.filter(main_phone__number=phone_param)
        else:
            queryset = Client.objects.all()
        return queryset
