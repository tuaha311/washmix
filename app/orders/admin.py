from django import forms
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

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


class OrderAdmin(DefaultAdmin):
    readonly_fields = [
        "pdf_path",
    ]
    list_display = [
        "__str__",
        "employee",
        "basket",
        "request",
        "coupon",
        "status",
        "payment",
    ]
    list_editable = [
        "employee",
    ]

    def pdf_path(self, instance):
        context = {"instance": instance}

        widget = render_to_string("widgets/href.html", context=context)

        return mark_safe(widget)

    pdf_path.short_description = "PDF path"


models = [
    [Order, OrderAdmin],
    [Item, DefaultAdmin],
    [Service, DefaultAdmin],
    [Price, DefaultAdmin],
    [Basket, BasketAdmin],
]
for item in models:
    admin.site.register(*item)
