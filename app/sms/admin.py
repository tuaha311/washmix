from django.contrib import admin
from .models import SMSTemplate
from django_nonmodel_admin import NonModelAdmin, register

@admin.register(SMSTemplate)
class SMSAdmin(admin.ModelAdmin):
    pass

@register()
class DashboardAdmin(NonModelAdmin):
    name = 'outbound_sms'
    verbose_name = 'Send SMS'
    change_list_template = "admin/sms/outbound-sms"