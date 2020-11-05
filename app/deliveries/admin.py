from django import forms
from django.conf import settings
from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Delivery


class DeliveryForm(forms.ModelForm):
    days = forms.MultipleChoiceField(
        choices=settings.DELIVERY_DAY_CHOICES,
    )

    class Meta:
        model = Delivery
        fields = "__all__"


class DeliveryAdmin(DefaultAdmin):
    form = DeliveryForm


models = [
    [Delivery, DeliveryAdmin],
]
for item in models:
    admin.site.register(*item)
