from django.contrib import admin
from sms.views import outbound_sms, get_context

from users.models.client import Client

from .models import SMSTemplate, SendSMS


@admin.register(SMSTemplate)
class SMSAdmin(admin.ModelAdmin):
    change_list_template = "assets/sms_change_form.html"
    
@admin.register(SendSMS)
class SendSMSAdmin(admin.ModelAdmin):
    actions = ["printer"]

    def get_context(self, request):
        context = outbound_sms(request)  # Call your get_context function to populate context
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

    def printer(self, request, queryset):
        for sms_instance in queryset:
            print(f"SendSMS Instance ID: {sms_instance.__dict__}")