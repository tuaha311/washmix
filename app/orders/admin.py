from typing import Any, List, Tuple

from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.db.models import CharField, F, Q, QuerySet, Value
from django.db.models.functions import Concat, TruncDate
from django.db.transaction import atomic
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from billing.choices import InvoicePurpose
from billing.utils import perform_refund
from core.admin import AdminWithSearch
from orders.models import Basket, Item, Order, Price, Quantity, Service
from orders.utils import generate_pdf_from_html
from users.admin import CustomAutocompleteSelect


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
    extra = 0
    autocomplete_fields = ("price",)


class BasketAdmin(AdminWithSearch):
    inlines = [QuantityInlineAdmin]
    autocomplete_fields = ("client",)

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        if "autocomplete" in request.path:
            queryset = queryset.filter(Q(id__contains=request.GET.get("q", "")))
        return queryset, use_distinct


class OrderAdminForm(forms.ModelForm):
    payment_retry = forms.CharField(
        label="Payment",
        required=False,
        widget=forms.Select(choices=[(None, "--------"), ("retry", "retry")]),
    )

    class Meta:
        model = Order
        fields = "__all__"
        widgets = {
            "client": CustomAutocompleteSelect(
                model._meta.get_field("client").remote_field, "Select a Client", admin.site
            ),
            "employee": CustomAutocompleteSelect(
                model._meta.get_field("employee").remote_field, "Select an Employee", admin.site
            ),
            "basket": CustomAutocompleteSelect(
                model._meta.get_field("basket").remote_field, "Select a Basket", admin.site
            ),
            "request": CustomAutocompleteSelect(
                model._meta.get_field("request").remote_field, "Select a Request", admin.site
            ),
            "subscription": CustomAutocompleteSelect(
                model._meta.get_field("subscription").remote_field,
                "Select a Subscription",
                admin.site,
            ),
            "invoice": CustomAutocompleteSelect(
                model._meta.get_field("invoice").remote_field, "Select an Invoice", admin.site
            ),
            "bought_with_subscription": CustomAutocompleteSelect(
                model._meta.get_field("bought_with_subscription").remote_field,
                "Select a Subscription",
                admin.site,
            ),
        }


class ClientEmailFilter(SimpleListFilter):
    title = "Client Email"
    parameter_name = "client_email"

    def lookups(self, request, model_admin):
        client_emails = (
            model_admin.get_queryset(request)
            .values_list("client__user__email", flat=True)
            .distinct()
        )
        unique_emails = []
        seen_emails = set()
        for email in client_emails:
            if email and email not in seen_emails:
                unique_emails.append((email, email))
                seen_emails.add(email)
        return unique_emails

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(client__user__email=value)
        return queryset


class ClientNameFilter(SimpleListFilter):
    title = "Client Name"
    parameter_name = "client_name"

    def lookups(self, request, model_admin):
        client_names = (
            model_admin.get_queryset(request)
            .annotate(
                full_name=Concat(
                    "client__user__first_name",
                    Value(" "),
                    "client__user__last_name",
                    output_field=CharField(),
                )
            )
            .values_list("full_name", flat=True)
            .distinct()
        )
        unique_names = []
        seen_names = set()
        for name in client_names:
            if name and name not in seen_names:
                unique_names.append((name, name))
                seen_names.add(name)
        return unique_names

    def queryset(self, request, queryset):
        value = self.value()

        if value:
            parts = value.split(" ")
            first_name = parts[0]
            last_name = parts[1] if len(parts) > 1 else ""
            return queryset.filter(
                Q(
                    client__user__first_name__icontains=first_name,
                    client__user__last_name__icontains=last_name,
                )
            )


class BillingPaymentFilter(SimpleListFilter):
    title = "Stripe Payment"
    parameter_name = "stripe_payment"

    def lookups(self, request, model_admin):
        stripe_dates = (
            Order.objects.annotate(date=TruncDate("invoice__transaction_list__created"))
            .values_list("date", flat=True)
            .distinct()
        )
        unique_dates = []
        seen_dates = set()
        for date in stripe_dates:
            if date and date not in seen_dates:
                unique_dates.append((date, date))
                seen_dates.add(date)
        return unique_dates

    def queryset(self, request, queryset):
        value = self.value()
        if value:
            return queryset.filter(invoice__transaction_list__created__date=value)
        return queryset


class OrderAdmin(AdminWithSearch):
    list_filter = [
        "payment",
        "created",
        BillingPaymentFilter,
        ClientEmailFilter,
        ClientNameFilter,
        "id",
    ]

    readonly_fields = [
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
    actions = ["cancel_unpaid_order"]
    form = OrderAdminForm
    # autocomplete_fields = ['client','employee','basket','request','subscription','invoice','bought_with_subscription']

    def get_changelist_form(self, request, **kwargs):
        return OrderAdminForm

    def cancel_unpaid_order(self, request: HttpRequest, order_queryset: QuerySet):
        """
        This action helps to make refund on unpaid orders with some restrictions:
            - Order should be a POS order
            - Invoice should be unpaid
            - If Invoice was paid only with WashMix credits
        """

        cancelled_order_list = []
        allowed_for_refund_purposes = [InvoicePurpose.ORDER, InvoicePurpose.SUBSCRIPTION]

        with atomic():
            for order in order_queryset:
                invoice = order.invoice
                purpose = invoice.purpose
                basket = order.basket
                subscription = order.subscription
                is_refundable = invoice.purpose in allowed_for_refund_purposes

                if invoice.is_paid or invoice.has_stripe_transaction or not is_refundable:
                    continue

                # if we charge some credits for this invoice - let's refund them
                if invoice.paid_amount:
                    perform_refund(invoice)

                if purpose == InvoicePurpose.ORDER:
                    basket.delete()
                elif purpose == InvoicePurpose.SUBSCRIPTION:
                    subscription.delete()

                # if we will remove order in place, then it will mutate order_queryset
                # such behavior can lead to unexpected results - because of it we are forming
                # list of order that will be removed
                cancelled_order_list.append(order.pk)

            # then we are removing all orders that meet our criteria
            order_queryset.filter(pk__in=cancelled_order_list).delete()

        self.message_user(
            request, f"Orders was cancelled - {cancelled_order_list}", messages.SUCCESS
        )

    cancel_unpaid_order.short_description = "Cancel unpaid order and perform refund."  # type: ignore

    def pdf_path(self, order: Order):
        """
        Shows a relative to media root URL of PDF-report.
        PDF-path only accessible for POS orders.

        IMPORTANT: our backend application wrapped in Docker-container.
        Because of it, when container restart all temporary data is wiped out - and we
        are forced to create report every time when user go to Order details view.
        """

        if order.subscription:
            return "-"

        pdf_path = self._generate_pdf_report(order)

        context = {"pdf_path": pdf_path}
        widget = render_to_string("widgets/href.html", context=context)

        return mark_safe(widget)

    pdf_path.short_description = "PDF path"  # type: ignore

    def _generate_pdf_report(self, order: Order):
        """
        PDF-report generator method.
        """

        order_id = order.id
        base_dir = settings.BASE_DIR

        absolute_path = generate_pdf_from_html(order_id)

        # we are looking for path with `media` and using
        # relative path to base dir of project
        relative_to_base_dir = absolute_path.relative_to(base_dir)
        relative_path = str(relative_to_base_dir)

        return f"/{relative_path}"

    def save_form(self, request: HttpRequest, form: forms.BaseForm, change):
        order = form.instance
        payment_retry = form.cleaned_data.get("payment_retry", None)
        if payment_retry == "retry":
            from billing.services.payments import PaymentService

            print("Retrying")
            payment_service = PaymentService(order.client, order.invoice)
            payment_service.charge()

        return super().save_form(request, form, change)


models = [
    [Order, OrderAdmin],
    [Item, AdminWithSearch],
    [Service, AdminWithSearch],
    [Price, AdminWithSearch],
    [Basket, BasketAdmin],
]
for item in models:
    admin.site.register(*item)
