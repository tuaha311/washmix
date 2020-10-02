from django import forms
from django.conf import settings
from django.contrib import admin

from pickups.models import Delivery


class DeliveryForm(forms.ModelForm):
    days = forms.MultipleChoiceField(choices=settings.DELIVERY_DAY_CHOICES,)

    class Meta:
        model = Delivery
        fields = "__all__"


class DeliveryAdmin(admin.ModelAdmin):
    form = DeliveryForm


models = [
    [Delivery, DeliveryAdmin],
]
for item in models:
    if isinstance(item, (list, tuple)):
        admin.site.register(*item)
    else:
        admin.site.register(item)
