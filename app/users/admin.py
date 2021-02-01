from django import forms
from django.contrib import admin, messages
from django.contrib.admin import actions
from django.db.transaction import atomic

from billing.choices import InvoiceProvider
from billing.models import Invoice
from billing.utils import add_credits
from core.admin import AdminWithSearch
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
    extra = 0


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
    extra = 0


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
    extra = 0


#
# Client Admin
#
class ClientForm(forms.ModelForm):
    credit_amount = forms.IntegerField(required=False, label="Add credits, in cents (¢)")

    class Meta:
        model = Client
        fields = "__all__"


class ClientAdmin(AdminWithSearch):
    readonly_fields = [
        "balance",
        "stripe_id",
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
    actions = ["full_delete_action"]

    def save_form(self, request, form, change):
        """
        Method that helps to add credits for some client.
        """

        client = form.instance
        credit_amount = form.cleaned_data.get("credit_amount", None)

        if credit_amount and credit_amount > 0:
            add_credits(client, credit_amount, purpose=InvoiceProvider.WASHMIX)

        return super().save_form(request, form, change)

    def full_delete_action(self, request, queryset):
        """
        Method that performs full client's info deletion:
        - Removing all billing related stuff (because this relations are protected).
        - Removing all orders relations (the are also protected).
        - Remove rest of relations by calling default `delete_sected` admin action.
        """

        with atomic():
            # preparation step - we are removing all protected relations
            for client in queryset:
                invoice_list = client.invoice_list.all()
                transaction_list = client.transaction_list.all()
                order_list = client.order_list.all()

                transaction_list.delete()
                invoice_list.delete()
                order_list.delete()

            # and finish step - we are wiping all info
            actions.delete_selected(self, request, queryset)

        self.message_user(request, "Client was removed.", messages.SUCCESS)

    full_delete_action.short_description = "Remove all client's info."  # type: ignore


class CustomerAdmin(AdminWithSearch):
    list_display = [
        "__str__",
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
    [Employee, AdminWithSearch],
    [Customer, CustomerAdmin],
]
for item in models:
    admin.site.register(*item)
