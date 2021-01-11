from django.contrib.postgres.fields import JSONField
from django.db import models

from billing.choices import Kind, Provider
from core.behaviors import Amountable, Stripeable
from core.common_models import Common


class Transaction(Amountable, Stripeable, Common):
    """
    Service-side and Client-side entity.

    Basic kind of billing operation - we can add money (i.e. "debit"),
    or remove money (i.e. "credit").
    After aggregation stuff we will receive a balance of account.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="transaction_list",
    )
    invoice = models.ForeignKey(
        "billing.Invoice",
        verbose_name="invoice",
        on_delete=models.PROTECT,
        related_name="transaction_list",
    )

    kind = models.CharField(
        verbose_name="kind of transaction",
        max_length=20,
        choices=Kind.CHOICES,
    )
    provider = models.CharField(
        verbose_name="provider of transaction",
        max_length=20,
        choices=Provider.CHOICES,
    )
    source = JSONField(
        verbose_name="source of transaction (Stripe raw data)",
        default=dict,
    )

    class Meta:
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
