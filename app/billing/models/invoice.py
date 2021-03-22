from django.conf import settings
from django.db import models
from django.db.models import Sum

from billing.choices import InvoicePurpose
from core.common_models import CommonAmountDiscountModel
from core.utils import get_dollars


class Invoice(CommonAmountDiscountModel):
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
    card = models.ForeignKey(
        "billing.Card",
        verbose_name="card",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    purpose = models.CharField(
        max_length=20,
        verbose_name="purpose of this invoice",
        default=InvoicePurpose.SUBSCRIPTION,
        choices=InvoicePurpose.CHOICES,
    )

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def __str__(self):
        return f"№ {self.id} {self.amount_with_discount}"

    @property
    def is_paid(self) -> bool:
        paid_amount = self.paid_amount
        amount_with_discount = self.amount_with_discount

        return paid_amount >= amount_with_discount

    @property
    def paid_amount(self):
        transaction_list = self.transaction_list
        paid_amount = transaction_list.aggregate(total=Sum("amount"))["total"] or 0

        return paid_amount

    @property
    def unpaid_amount(self) -> float:
        paid_amount = self.paid_amount
        amount_with_discount = self.amount_with_discount

        unpaid_amount = amount_with_discount - paid_amount

        if unpaid_amount <= 0:
            return settings.DEFAULT_ZERO_AMOUNT

        return unpaid_amount

    @property
    def dollar_unpaid_amount(self) -> float:
        return get_dollars(self, "unpaid_amount")

    @property
    def has_transaction(self) -> bool:
        transaction_list = self.transaction_list

        return transaction_list.exists()
