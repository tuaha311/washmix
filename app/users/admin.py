from django import forms
from django.contrib import admin

from billing.models import Invoice
from core.admin import DefaultAdmin
from deliveries.models import Request
from orders.models import Order
from users.models import Client, Customer, Employee


#
# Invoice inlines
#
class InvoiceInlineForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            "amount",
            "discount",
            "card",
            "purpose",
        ]


class InvoiceInlineAdmin(admin.TabularInline):
    model = Invoice
    form = InvoiceInlineForm
    extra = 1


#
# Order inlines
#
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


#
# Request inlines
#
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


#
# Client Admin
#
class ClientAdmin(DefaultAdmin):
    inlines = [RequestInlineAdmin, OrderInlineAdmin, InvoiceInlineAdmin]
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
