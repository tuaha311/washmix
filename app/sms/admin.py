from django.contrib import admin
from .models import SMSTemplate

@admin.register(SMSTemplate)
class SMSAdmin(admin.ModelAdmin):
    pass