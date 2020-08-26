from django.db import models

from core.behaviors import Amountable
from core.common_models import Common


class Invoice(Amountable, Common):
    """
    Invoice that we generated for buying package or order.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        related_name="invoice_list",
        on_delete=models.CASCADE,
    )
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

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def __str__(self):
        return f"№ {self.pk} {self.amount}"
