from django import forms
from django.conf import settings
from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Delivery, Request


class RequestInline(admin.TabularInline):
    model = Request
    extra = 1


class DeliveryForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=settings.DELIVERY_DAY_CHOICES,
    )

    class Meta:
        model = Delivery
        fields = "__all__"


class DeliveryAdmin(DefaultAdmin):
    form = DeliveryForm
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
