from django.contrib.postgres.fields import JSONField
from django.db import models

from core.behaviors import Amountable, Stripeable
from core.common_models import Common


class Transaction(Amountable, Stripeable, Common):
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

    STRIPE = "stripe"
    COUPON = "coupon"
    CREDIT_BACK = "credit_back"
    WASHMIX = "washmix"
    PROVIDER_MAP = {
        STRIPE: "Stripe",
        COUPON: "Coupon",
        CREDIT_BACK: "Credit back",
        WASHMIX: "WashMix",
    }
    PROVIDER_CHOICES = list(PROVIDER_MAP.items())

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="transaction_list",
    )
    invoice = models.OneToOneField(
        "billing.Invoice",
        verbose_name="invoice",
        on_delete=models.PROTECT,
        related_name="transaction",
        null=True,
        blank=True,
    )

    kind = models.CharField(
        verbose_name="kind of transaction",
        max_length=10,
        choices=KIND_CHOICES,
    )
    provider = models.CharField(
        verbose_name="provider of transaction",
        max_length=10,
        choices=PROVIDER_CHOICES,
    )
    source = JSONField(
        verbose_name="source of transaction (Stripe raw data)",
        default=dict,
    )

    class Meta:
        verbose_name = "transaction"
        verbose_name_plural = "transactions"
