from django import forms
from django.conf import settings
from django.contrib import admin, messages
from django.db.models import QuerySet
from django.db.transaction import atomic
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from billing.choices import InvoicePurpose
from billing.utils import make_refund
from core.admin import AdminWithSearch
from orders.models import Basket, Item, Order, Price, Quantity, Service
from orders.utils import generate_pdf_from_html


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


class BasketAdmin(AdminWithSearch):
    inlines = [QuantityInlineAdmin]


class OrderAdmin(AdminWithSearch):
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
    actions = ["cancel_pos_order"]

    def cancel_pos_order(self, request: HttpRequest, order_queryset: QuerySet):
        """
        This action helps to make refund on unpaid orders with some restrictions:
            - Order should be a POS order
            - Invoice should be unpaid
            - If Invoice was paid only with WashMix credits
        """

        cancelled_order_list = []

        with atomic():
            for order in order_queryset:
                invoice = order.invoice
                basket = order.basket

                if (
                    invoice.is_paid
                    or invoice.has_stripe_transaction
                    or invoice.purpose != InvoicePurpose.ORDER
                ):
                    continue

                make_refund(invoice)

                basket.delete()

                # if we will remove order in place, then it will mutate order_queryset
                # such behavior can lead to unexpected results
                cancelled_order_list.append(order.pk)

            # then we are removing all orders that meet our criteria
            order_queryset.filter(pk__in=cancelled_order_list).delete()

        self.message_user(
            request, f"Orders was cancelled - {cancelled_order_list}", messages.SUCCESS
        )

    cancel_pos_order.short_description = "Cancel unpaid POS order and make refund."  # type: ignore

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
        order_id = order.id
        base_dir = settings.BASE_DIR

        absolute_path = generate_pdf_from_html(order_id)

        # we are looking for path with `media` and using
        # relative path to base dir of project
        relative_to_base_dir = absolute_path.relative_to(base_dir)
        relative_path = str(relative_to_base_dir)

        return f"/{relative_path}"


models = [
    [Order, OrderAdmin],
    [Item, AdminWithSearch],
    [Service, AdminWithSearch],
    [Price, AdminWithSearch],
    [Basket, BasketAdmin],
]
for item in models:
    admin.site.register(*item)
