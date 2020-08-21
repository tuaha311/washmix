from django.db import models

from core.behaviors import Stripeable
from core.common_models import Common


class Transaction(Stripeable, Common):
    """
    Basic kind of billing operation - we can add money (i.e. "debit"),
    or remove money (i.e. "credit").
    After aggregation stuff we will receive a balance of account.
    """

    DEBIT = "debit"
    CREDIT = "credit"
    KIND_MAP = {
        DEBIT: "Debit",
        CREDIT: "Credit",
    }
    KIND_CHOICES = list(KIND_MAP.items())

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="transaction_list",
    )

    amount = models.DecimalField(
        verbose_name="amount",
        max_digits=9,
        decimal_places=2,
    )
    kind = models.CharField(
        verbose_name="kind of transaction",
        max_length=10,
        choices=KIND_CHOICES,
    )

    class Meta:
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
