from django import forms
from django.contrib import admin

from billing.choices import Provider
from billing.models import Invoice
from billing.utils import add_credits
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
class ClientForm(forms.ModelForm):
    credit_amount = forms.IntegerField(required=False, label="Add credits, in cents (¢)")

    class Meta:
        model = Client
        fields = "__all__"


class ClientAdmin(DefaultAdmin):
    readonly_fields = [
        "balance",
    ]
    form = ClientForm
    inlines = [RequestInlineAdmin, OrderInlineAdmin, InvoiceInlineAdmin]
    list_display = [
        "__str__",
        "full_name",
        "main_phone",
        "subscription",
        "main_address",
    ]

    def save_form(self, request, form, change):
        client = form.instance
        credit_amount = form.cleaned_data.get("credit_amount", 0)

        if credit_amount > 0:
            add_credits(client, credit_amount, purpose=Provider.WASHMIX)

        super().save_form(request, form, change)


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
