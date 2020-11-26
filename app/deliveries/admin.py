from django import forms
from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Delivery, Request


class RequestInlineForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = [
            "address",
            "is_rush",
            "comment",
            "schedule",
        ]


class RequestInline(admin.TabularInline):
    model = Request
    form = RequestInlineForm
    extra = 1


class DeliveryAdmin(DefaultAdmin):
    list_display = ["__str__", "employee", "kind", "status", "address", "is_rush", "comment"]
    list_editable = [
        "employee",
        "status",
    ]


models = [
    [Delivery, DeliveryAdmin],
]
for item in models:
    admin.site.register(*item)
