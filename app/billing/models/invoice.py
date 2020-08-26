from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models

from core.behaviors import Amountable
from core.common_models import Common


class Invoice(Amountable, Common):
    """
    Invoice that we generated for buying package or order.

    Most of time, we use `object_id` to point on tables:
        - orders.Order
        - billing.Package
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

    amount = models.BigIntegerField(
        verbose_name="amount in cents",
        blank=True,
        null=True,
    )
    content_type = models.ForeignKey(
        "contenttypes.ContentType",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    object_id = models.PositiveIntegerField(
        verbose_name="ID of related object",
        blank=True,
        null=True,
    )
    # this fields just a wrapper around
    # `content_type` and `object_id` for convenient
    # querying. field doesn't stored inside db.
    object = GenericForeignKey()

    class Meta:
        verbose_name = "invoice"
        verbose_name_plural = "invoices"

    def __str__(self):
        return f"№ {self.pk} {self.amount}"

    @property
    def package(self):
        return None

    @property
    def order(self):
        return None
