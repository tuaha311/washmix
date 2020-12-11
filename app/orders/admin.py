from django import forms
from django.contrib import admin

from core.admin import DefaultAdmin
from orders.models import Basket, Item, Order, Price, Quantity, Service


class QuantityInlineForm(forms.ModelForm):
    class Meta:
        model = Quantity
        fields = [
            "price",
            "count",
        ]


class QuantityInlineAdmin(admin.TabularInline):
    model = Quantity
    form = QuantityInlineForm
    extra = 1


class BasketAdmin(DefaultAdmin):
    inlines = [QuantityInlineAdmin]


models = [
    [Order, DefaultAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
    [Basket, BasketAdmin],
]
for item in models:
    admin.site.register(*item)
