from django import forms
from django.conf import settings
from django.contrib import admin, messages

from billing.choices import InvoiceProvider
from billing.models import Invoice
from billing.utils import add_money_to_balance, remove_money_from_balance
from core.admin import AdminWithSearch
from deliveries.models import Request
from notifications.tasks import send_email
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
    add_money_amount = forms.IntegerField(
        required=False,
        label="Add credits, in cents (¢)",
        min_value=settings.DEFAULT_ZERO_AMOUNT,
    )
    remove_money_amount = forms.IntegerField(
        required=False,
        label="Remove credits, in cents (¢)",
        min_value=settings.DEFAULT_ZERO_AMOUNT,
    )

    class Meta:
        model = Client
        fields = "__all__"

    def clean_remove_money_amount(self):
        """
        Cleaner method that will check for client's balance is enough.
        """

        cleaned_data = self.cleaned_data

        client = self.instance
        balance = client.balance
        remove_money_amount = cleaned_data.get("remove_money_amount", None)

        if remove_money_amount and balance < remove_money_amount:
            raise forms.ValidationError("Not enough money.", code="not_enough_money")

        return remove_money_amount


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
        add_money_amount = form.cleaned_data.get("add_money_amount", None)
        remove_money_amount = form.cleaned_data.get("remove_money_amount", None)

        if add_money_amount and add_money_amount > 0:
            add_money_to_balance(client, add_money_amount, provider=InvoiceProvider.WASHMIX)

        if remove_money_amount and remove_money_amount > 0:
            remove_money_from_balance(client, remove_money_amount, provider=InvoiceProvider.WASHMIX)

        return super().save_form(request, form, change)

    def full_delete_action(self, request, queryset):
        """
        Method that performs full client's info deletion:
        - Removing all billing related stuff (because this relations are protected).
        - Removing all orders relations (the are also protected).
        - Remove rest of relations by calling default `delete_sected` admin action.
        """

        client_info = [
            {"email": client.email, "full_name": client.full_name} for client in queryset
        ]

        queryset.delete()

        for client in client_info:
            email = client["email"]
            full_name = client["full_name"]
            recipient_list = [email]

            send_email.send(
                event=settings.ACCOUNT_REMOVED,
                recipient_list=recipient_list,
                extra_context={
                    "full_name": full_name,
                },
            )

        self.message_user(request, "Clients was removed.", messages.SUCCESS)

    full_delete_action.short_description = "Remove all client's info and notify them."  # type: ignore


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
