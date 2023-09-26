from datetime import date, datetime
import os
from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.sites import NotRegistered
from django.contrib.admin.views.main import PAGE_VAR, ChangeList
from django.contrib.admin.widgets import AutocompleteSelect
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.paginator import EmptyPage, InvalidPage, Paginator
from django.db.models import Q, QuerySet
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.urls import reverse

from swap_user.admin import BaseUserAdmin
from swap_user.to_named_email.forms import (
    NamedUserEmailOptionalFieldsForm,
    NamedUserEmailRequiredFieldsForm,
)
from deliveries.models.delivery import Delivery

from billing.choices import InvoiceProvider
from billing.models import Invoice
from billing.utils import add_money_to_balance, remove_money_from_balance
from core.admin import AdminWithSearch
from core.mixins import AdminUpdateFieldsMixin
from core.tasks import archive_periodic_promotional_emails
from core.utils import convert_cent_to_dollars
from deliveries.models import Request
from notifications.tasks import send_email
from orders.models import Order
from orders.services.order import OrderService
from settings.base import SEND_ADMIN_STORE_CREDIT
from subscriptions.models import Package
from subscriptions.services.subscription import SubscriptionService
from users.helpers import remove_user_relation_with_all_info
from users.models import Client, Customer, Employee, Log

User = get_user_model()
LIMIT = 10


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__["get_query_string"]

    def __init__(self, request, page_num, paginator):
        self.show_all = "all" in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


class InlineChangeList(object):
    can_show_all = True
    multi_page = True
    get_query_string = ChangeList.__dict__["get_query_string"]

    def __init__(self, request, page_num, paginator):
        self.show_all = "all" in request.GET
        self.page_num = page_num
        self.paginator = paginator
        self.result_count = paginator.count
        self.params = dict(request.GET.items())


#
# Invoice inlines
#
class CustomAutocompleteSelect(AutocompleteSelect):
    def __init__(self, field, prompt="", admin_site=None, attrs=None, choices=(), using=None):
        self.prompt = prompt
        super().__init__(field, admin_site, attrs=attrs, choices=choices, using=using)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.update({"data-placeholder": self.prompt})
        return attrs


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
    readonly_fields = (
        "card",
        "purpose",
    )
    per_page = LIMIT
    template = "admin/edit_inline.html"

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)

        class PaginationFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super(PaginationFormSet, self).__init__(*args, **kwargs)

                qs = self.queryset
                paginator = Paginator(qs, self.per_page)
                try:
                    page_num = int(request.GET.get("page", ["0"])[0])
                except ValueError:
                    page_num = 0

                try:
                    page = paginator.page(page_num + 1)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)

                self.page = page
                self.cl = InlineChangeList(request, page_num, paginator)
                self.paginator = paginator

                if self.cl.show_all:
                    self._queryset = qs
                else:
                    self._queryset = page.object_list

        PaginationFormSet.per_page = self.per_page
        return PaginationFormSet


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
        widgets = {
            "employee": CustomAutocompleteSelect(
                model._meta.get_field("employee").remote_field, "Select an Employee", admin.site
            ),
            "basket": CustomAutocompleteSelect(
                model._meta.get_field("basket").remote_field, "Select a Basket", admin.site
            ),
            "request": CustomAutocompleteSelect(
                model._meta.get_field("request").remote_field, "Select an Request", admin.site
            ),
            "coupon": CustomAutocompleteSelect(
                model._meta.get_field("coupon").remote_field, "Select a Coupon", admin.site
            ),
        }


class OrderInlineAdmin(admin.TabularInline):
    model = Order
    form = OrderInlineForm
    extra = 0
    per_page = LIMIT
    template = "admin/edit_inline.html"

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)

        class PaginationFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super(PaginationFormSet, self).__init__(*args, **kwargs)

                qs = self.queryset
                paginator = Paginator(qs, self.per_page)
                try:
                    page_num = int(request.GET.get("page", ["0"])[0])
                except ValueError:
                    page_num = 0

                try:
                    page = paginator.page(page_num + 1)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)

                self.page = page
                self.cl = InlineChangeList(request, page_num, paginator)
                self.paginator = paginator

                if self.cl.show_all:
                    self._queryset = qs
                else:
                    self._queryset = page.object_list

        PaginationFormSet.per_page = self.per_page
        return PaginationFormSet


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
        widgets = {
            "address": CustomAutocompleteSelect(
                model._meta.get_field("address").remote_field, "Select an Address", admin.site
            ),
            "schedule": CustomAutocompleteSelect(
                model._meta.get_field("schedule").remote_field, "Select a Schedule", admin.site
            ),
        }


class RequestInlineAdmin(admin.TabularInline):
    template = "admin/edit_inline.html"
    model = Request
    form = RequestInlineForm
    extra = 0
    per_page = LIMIT

    def get_formset(self, request, obj=None, **kwargs):
        formset_class = super().get_formset(request, obj, **kwargs)

        class PaginationFormSet(formset_class):
            def __init__(self, *args, **kwargs):
                super(PaginationFormSet, self).__init__(*args, **kwargs)

                qs = self.queryset
                paginator = Paginator(qs, self.per_page)
                try:
                    page_num = int(request.GET.get("page", ["0"])[0])
                except ValueError:
                    page_num = 0

                try:
                    page = paginator.page(page_num + 1)
                except (EmptyPage, InvalidPage):
                    page = paginator.page(paginator.num_pages)

                self.page = page
                self.cl = InlineChangeList(request, page_num, paginator)
                self.paginator = paginator

                if self.cl.show_all:
                    self._queryset = qs
                else:
                    self._queryset = page.object_list

        PaginationFormSet.per_page = self.per_page
        return PaginationFormSet


#
# #
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

    description = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Description appearing on invoice",
        max_length=1000,
    )

    change_client_subscription = forms.CharField(
        label="Change Client Subscription",
        required=False,
        widget=forms.Select(choices=[(None, "--------")] + settings.PACKAGE_NAME_CHOICES),
    )

    private_note = forms.CharField(
        widget=forms.Textarea,
        label="Private Note About Client",
        required=False,
        max_length=300,
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


class ClientAdmin(AdminUpdateFieldsMixin, AdminWithSearch):
    readonly_fields = [
        "additional_phones",
        "balance",
        "stripe_id",
        "full_address",
        "address_line_2",
    ]
    form = ClientForm
    inlines = [RequestInlineAdmin, OrderInlineAdmin, InvoiceInlineAdmin]
    autocomplete_fields = (
        "user",
        "main_card",
        "main_phone",
        "main_address",
    )

    list_display = [
        "full_name",
        "get_main_phone_number",  # Use custom method instead of main_phone
        "__str__",
        "subscription",
        "full_address",
        "has_card",
    ]

    def full_address(self, obj):
        address_line_2 = obj.billing_address.get("address_line_2")
        if address_line_2 is not None:
            return str(obj.main_address) + ", (Apt: " + address_line_2 + " )"
        else:
            return obj.main_address

    def address_line_2(self, obj):
        return obj.billing_address.get("address_line_2")

    def get_main_phone_number(self, obj):
        """
        Returns the phone number portion of the main_phone field, or the main_phone field if it doesn't have a number attribute.
        """
        if hasattr(obj.main_phone, "number"):
            return obj.main_phone.number
        return obj.main_phone

    get_main_phone_number.short_description = "Main Phone Number"  # Set column header in admin

    def save_form(self, request: HttpRequest, form: forms.BaseForm, change):
        """
        Method that helps to add credits for some client.
        """

        client = form.instance
        add_money_amount = form.cleaned_data.get("add_money_amount", None)
        remove_money_amount = form.cleaned_data.get("remove_money_amount", None)
        description = form.cleaned_data.get("description", None)
        added_or_removed = None
        transaction = None
        credit_given = None

        if add_money_amount and add_money_amount > 0:
            transaction = add_money_to_balance(
                client, add_money_amount, provider=InvoiceProvider.WASHMIX, note=description
            )
            added_or_removed = "added"
            credit_given = convert_cent_to_dollars(int(add_money_amount))

        if remove_money_amount and remove_money_amount > 0:
            transaction = remove_money_from_balance(
                client, remove_money_amount, provider=InvoiceProvider.WASHMIX, note=description
            )
            added_or_removed = "removed"
            credit_given = convert_cent_to_dollars(int(remove_money_amount))

        if transaction:
            send_email(
                event=settings.SEND_ADMIN_STORE_CREDIT,
                recipient_list=[*settings.ADMIN_EMAIL_LIST],
                extra_context={
                    "client": client,
                    "added_or_removed": added_or_removed,
                    "credit_given": credit_given,
                    "note": description,
                    "old_balance": convert_cent_to_dollars(
                        int(transaction.invoice.order.balance_before_purchase)
                    ),
                    "new_balance": convert_cent_to_dollars(
                        int(transaction.invoice.order.balance_after_purchase)
                    ),
                },
            )

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

    def delete_model(self, request, obj):
        # Perform the actual deletion
        print("DELETING THE USER       ", obj)
        super().delete_model(request, obj)

        recipient_list = [*settings.ADMIN_EMAIL_LIST, obj.email]

        send_email.send(
            event=settings.ACCOUNT_REMOVED,
            recipient_list=recipient_list,
            extra_context={
                "full_name": obj.full_name,
            },
        )

    full_delete_action.short_description = "Remove all client's info and notify them."  # type: ignore

    def additional_phones(self, obj):
        phones = ""
        for ph in obj.phone_list.all():
            if obj.main_phone != ph:
                phones += ph.number + ", "
        return phones

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(user__email__contains=request.GET.get("q", ""))
        return queryset, use_distinct
    
    change_form_template = "assets/change_list.html"

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


class LogAdmin(AdminWithSearch):
    list_display = [
        "customer",
        "created",
        "action",
    ]


class UserAdmin(
    AdminUpdateFieldsMixin,
    AdminWithSearch,
    BaseUserAdmin,
):
    add_form_class = NamedUserEmailRequiredFieldsForm
    change_form_class = NamedUserEmailOptionalFieldsForm
    search_fields = ["email"]


class EmployeeAdmin(AdminWithSearch):
    actions = ["full_delete_action"]
    change_form_template = 'assets/change_form.html'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        employee = self.get_object(request, object_id)

        if employee and employee.position != 'driver':
            self.change_form_template = None
        else:
            deliveries = Delivery.objects.filter(employee_id=object_id)
            date_list = sorted(list(set([delivery.changed.date() for delivery in deliveries])), reverse=False)
            formatted_date_list = [datetime.strftime(date, '%m/%d/%Y') for date in date_list]
            employee_id = object_id
            extra_context = extra_context or {}
            extra_context['employee_id'] = employee_id
            extra_context['date_list'] = formatted_date_list
            pdf_list = []

            for date in formatted_date_list:
                converted_date = datetime.strptime(date, "%m/%d/%Y").strftime("%Y-%m-%d")
                pdf_filename = f"{converted_date}_driver_{employee_id}.pdf"
                pdf_path = os.path.join(settings.MEDIA_URL, "driver", pdf_filename)
                full_path = os.path.join(settings.MEDIA_ROOT, "driver", pdf_filename)
                if os.path.exists(full_path):
                    pdf_list.append(pdf_path)
                
        
        extra_context['pdf_list'] = pdf_list
        self.change_form_template = 'assets/change_form.html'

        return super().change_view(request, object_id, form_url, extra_context)


    def full_delete_action(self, request: HttpRequest, employee_queryset: QuerySet):
        """
        Method that performs full employee's info deletion:
        - Remove all User's information.
        """

        filter_query = {"employee__in": employee_queryset}
        remove_user_relation_with_all_info(employee_queryset, filter_query)

        self.message_user(request, "Employees was removed.", messages.SUCCESS)

    full_delete_action.short_description = "Remove all employee's info and notify them."  # type: ignore

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(
                Q(user__email__icontains=request.GET.get("q", ""))
                | Q(user__first_name__icontains=request.GET.get("q", ""))
                | Q(user__last_name__icontains=request.GET.get("q", ""))
                | Q(position__icontains=request.GET.get("q", ""))
            )
        return queryset, use_distinct


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

admin.site.register(Log, LogAdmin)
