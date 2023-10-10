import json
from django.contrib import admin
from django.urls import reverse
from users.admin import ClientAdmin
from sms.views import outbound_sms, get_context
from django.utils.html import format_html
from users.models.client import Client
from django.db.models import Q

from .models import SMSTemplate, SendSMS


@admin.register(SMSTemplate)
class SMSAdmin(admin.ModelAdmin):
    change_list_template = "assets/sms_change_form.html"
    
@admin.register(SendSMS)
class SendSMSAdmin(ClientAdmin):
    actions = ["send_sms"]
    
    def get_params(self, request):
        zip_code_param = request.POST.get("zip_code")
        city_param = request.POST.get("city")
        address_param = request.POST.get("address")
        phone_param = request.POST.get("phone")
        selected_customers_json = request.POST.get("selected-customers")  # Get the JSON string
        selected_customers = json.loads(selected_customers_json) if selected_customers_json else []
        selected_customers = list(set(selected_customers))
        data = {}
        # If a zip code parameter is provided, filter the data
        if zip_code_param:
           data = {"queryset": Client.objects.filter(Q(billing_address__zip_code=zip_code_param)), "selected_zip_code": zip_code_param}
        elif city_param:
           data = {"queryset": Client.objects.filter(billing_address__address_line_1__icontains=city_param), "selected_city": city_param}
        elif address_param:
           data = {"queryset": Client.objects.filter(billing_address__address_line_1=address_param), "selected_address": address_param}
        elif phone_param:
           data = {"queryset": Client.objects.filter(main_phone__number=phone_param), "selected_phone": phone_param}
        else:
            data = {"queryset": Client.objects.all()}
        if selected_customers:
            data.update({"selected_customers": json.dumps(selected_customers)})
        return data

    def get_context(self, request):
        context = get_context()  # Call your get_context function to populate context
        context.update(self.get_params(request))
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
        # queryset = super().get_queryset(request)
        
        # Utilize get_params to filter the queryset
        params = self.get_params(request)
        base_queryset = params.get("queryset")

        # Get the selected customers from the request
        selected_customers = params.get("selected_customers")

        # Create a query to filter based on selected customers
        if selected_customers:
            selected_customers_ids = [int(id) for id in selected_customers if id.isdigit()]
            selected_customers_query = Q(id__in=selected_customers_ids)
            selected_customers_queryset = base_queryset + Client.objects.filter()
            
            # Combine the selected customers queryset with the base queryset
            queryset = selected_customers_queryset | base_queryset
        hello = False
        queryset = Client.objects.filter(Q(id=1) | Q(id=2) if hello else None)
        return queryset