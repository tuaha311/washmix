from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.http.request import HttpRequest

from swap_user.admin import BaseUserAdmin
from swap_user.to_named_email.forms import (
    NamedUserEmailOptionalFieldsForm,
    NamedUserEmailRequiredFieldsForm,
)

from billing.choices import InvoiceProvider
from billing.models import Invoice
from billing.utils import add_money_to_balance, remove_money_from_balance
from core.admin import AdminWithSearch
from core.mixins import AdminUpdateFieldsMixin
from deliveries.models import Request
from orders.models import Order
from orders.services.order import OrderService
from subscriptions.models import Package
from subscriptions.services.subscription import SubscriptionService
from users.helpers import remove_user_relation_with_all_info
from users.models import Client, Customer, Employee

User = get_user_model()


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

    change_client_subscription = forms.CharField(
        label="Change Client Subscription",
        required=False,
        widget=forms.Select(choices=[(None, "--------")] + settings.PACKAGE_NAME_CHOICES),
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

    def clean_change_client_subscription(self):
        cleaned_data = self.cleaned_data
        client = self.instance

        change_client_subscription = cleaned_data.get("change_client_subscription", None)

        if change_client_subscription:
            current_subscription = client.subscription.name
            if current_subscription != change_client_subscription:
                package = Package.objects.get(name=change_client_subscription)
                try:
                    subscription_service = SubscriptionService(client)
                    order_container = subscription_service.choose(package)

                    order = Order.objects.get(pk=order_container.pk)
                    order_service = OrderService(client, order)
                    order_container, charge_succesful = order_service.checkout(order)

                except ValidationError:
                    raise forms.ValidationError("Can't bill client's card")

                if not charge_succesful:
                    raise forms.ValidationError("Can't bill client's card")
                else:
                    client.subscription = order_container.subscription
                    client.save()


class ClientAdmin(AdminUpdateFieldsMixin, AdminWithSearch):
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
        "has_card",
    ]
    actions = ["full_delete_action"]

    def save_form(self, request: HttpRequest, form: forms.BaseForm, change):
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

    def full_delete_action(self, request: HttpRequest, client_queryset: QuerySet):
        """
        Method that performs full client's info deletion:
        - Removing all billing related stuff (because this relations are protected).
        - Removing all orders relations (the are also protected).
        - Remove rest of relations by calling default `delete_sected` admin action.
        - Remove all User's information.
        """

        filter_query = {"client__in": client_queryset}
        remove_user_relation_with_all_info(client_queryset, filter_query)

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


class UserAdmin(
    AdminUpdateFieldsMixin,
    AdminWithSearch,
    BaseUserAdmin,
):
    add_form_class = NamedUserEmailRequiredFieldsForm
    change_form_class = NamedUserEmailOptionalFieldsForm


class EmployeeAdmin(AdminWithSearch):
    actions = ["full_delete_action"]

    def full_delete_action(self, request: HttpRequest, employee_queryset: QuerySet):
        """
        Method that performs full employee's info deletion:
        - Remove all User's information.
        """

        filter_query = {"employee__in": employee_queryset}
        remove_user_relation_with_all_info(employee_queryset, filter_query)

        self.message_user(request, "Employees was removed.", messages.SUCCESS)

    full_delete_action.short_description = "Remove all employee's info and notify them."  # type: ignore


models = [
    [Client, ClientAdmin],
    [Employee, EmployeeAdmin],
    [Customer, CustomerAdmin],
]
for item in models:
    admin.site.register(*item)

# here we are trying to override Admin Panel for NamedEmailUser model
# that was provided by 3-rd party library
try:
    admin.site.unregister(User)
except NotRegistered:
    pass
finally:
    admin.site.register(User, UserAdmin)
