from functools import partial

from django.db import models

from core.behaviors import Amountable, Discountable, get_dollars
from core.common_models import Common


class Invoice(Amountable, Discountable, Common):
    """
    Invoice that we generated for buying package or order.

    Most of time, we use `object_id` to point on tables:
        - orders.Order
        - billing.Package
    """

    coupon = models.ForeignKey(
        "billing.Coupon",
        verbose_name="coupon",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    card = models.ForeignKey(
        "billing.Card",
        verbose_name="card",
        related_name="invoice_list",
        on_delete=models.SET_NULL,
        null=True,
    )
    transaction = models.OneToOneField(
        "billing.Transaction",
        verbose_name="transaction",
        related_name="invoice",
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def __str__(self):
        return f"№ {self.pk} {self.amount}"

    @property
    def is_filled(self) -> bool:
        required_fields = [self.card, self.amount, self.entity]
        return all(required_fields)

    @property
    def basic(self) -> int:
        if self.is_package:
            return self.package.price
        else:
            return self.order.price

    dollar_basic = property(partial(get_dollars, attribute_name="basic"))
