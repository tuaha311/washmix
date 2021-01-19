from django import forms
from django.conf import settings
from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

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

    def pdf_path(self, order: Order):
        """
        Shows a relative to media root URL of PDF-report.
        PDF-path only accessible for POS orders.
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
