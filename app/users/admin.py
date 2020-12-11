from django import forms
from django.contrib import admin

from core.admin import DefaultAdmin
from deliveries.models import Request
from orders.models import Order
from users.models import Client, Customer, Employee


class OrderInlineForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "basket",
            "employee",
            "request",
            "subscription",
            "coupon",
            "status",
            "payment",
            "note",
        ]


class OrderInlineAdmin(admin.TabularInline):
    model = Order
    form = OrderInlineForm
    extra = 1


class RequestInlineForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = [
            "address",
            "is_rush",
            "comment",
            "schedule",
        ]


class RequestInlineAdmin(admin.TabularInline):
    model = Request
    form = RequestInlineForm
    extra = 1


class ClientAdmin(DefaultAdmin):
    inlines = [RequestInlineAdmin, OrderInlineAdmin]
    list_display = [
        "full_name",
        "email",
        "main_phone",
        "subscription",
        "main_address",
    ]


class CustomerAdmin(DefaultAdmin):
    list_display = [
        "full_name",
        "email",
        "phone",
        "zip_code",
        "address",
        "kind",
    ]
    list_filter = ["kind"]


models = [
    [Client, ClientAdmin],
    [Employee, DefaultAdmin],
    [Customer, DefaultAdmin],
]
for item in models:
    admin.site.register(*item)
