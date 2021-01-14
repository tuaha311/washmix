from django import forms
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from core.admin import AdminWithSearch
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


class BasketAdmin(AdminWithSearch):
    inlines = [QuantityInlineAdmin]


class OrderAdmin(AdminWithSearch):
    readonly_fields = [
        "pdf_ready",
        "pdf_path",
    ]
    list_display = [
        "__str__",
        "employee",
        "subscription",
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
        """
        Shows a relative to media root URL of PDF-report.
        """

        context = {"instance": instance}

        widget = render_to_string("widgets/href.html", context=context)

        return mark_safe(widget)

    pdf_path.short_description = "PDF path"  # type: ignore

    def pdf_ready(self, instance):
        """
        Simple method that prettifies a boolean field to show in admin.
        """

        ready_status = "Not ready"

        if instance.is_pdf_ready:
            ready_status = "Ready"

        return ready_status

    pdf_ready.short_description = "PDF-report is ready"  # type: ignore


models = [
    [Order, OrderAdmin],
    [Item, AdminWithSearch],
    [Service, AdminWithSearch],
    [Price, AdminWithSearch],
    [Basket, BasketAdmin],
]
for item in models:
    admin.site.register(*item)
