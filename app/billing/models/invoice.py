from django.db import models
from django.db.models import Sum

from billing.choices import Purpose
from core.behaviors import Amountable, Discountable
from core.common_models import Common
from core.mixins import CalculatedAmountWithDiscount


class Invoice(CalculatedAmountWithDiscount, Amountable, Discountable, Common):
    """
    Service-side and Client-side entity.

    Invoice that we generated for buying package or order.

    Most of time, we use `object_id` to point on tables:
        - orders.Order
        - billing.Package
    """

    # here we store link on client, because we create
    # invoice as first step at Welcome scenario and
    # then we are working based on this.
    # 1. applying coupon
    # 2. finding last active invoice of client
    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="invoice_list",
    )
    order = models.ForeignKey(
        "orders.Order",
        verbose_name="order",
        on_delete=models.PROTECT,
        related_name="invoice_list",
    )
    card = models.ForeignKey(
        "billing.Card",
        verbose_name="card",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        null=True,
    )

    purpose = models.CharField(
        max_length=20,
        verbose_name="purpose of this invoice",
        default=Purpose.SUBSCRIPTION,
        choices=Purpose.CHOICES,
    )

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def __str__(self):
        return f"№ {self.pk} {self.amount}"

    @property
    def is_filled(self) -> bool:
        required_fields = [self.card, self.amount]
        return all(required_fields)

    @property
    def is_paid(self):
        total_amount = self.transaction_list.aggregate(total=Sum('amount'))['total'] or 0

        return total_amount >= self.amount_with_discount
