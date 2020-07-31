from django.db import models
from django.utils.timezone import localtime

from core.common_models import Common
from modules.enums import CouponType


class Card(Common):
    """
    Credit or debit card.
    We doesn't store anything related to card credentials - only Stripe ID.
    """

    client = models.ForeignKey(
        "users.Client",
        verbose_name="client",
        on_delete=models.CASCADE,
        related_name="card_list",
    )

    stripe_card_id = models.TextField(
        verbose_name="Stripe card ID",
    )
    is_active = models.BooleanField(
        verbose_name="card is active",
        default=False,
    )

    class Meta:
        verbose_name = "card"
        verbose_name_plural = "cards"


class Transaction(Common):
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


class Coupon(Common):
    """
    Coupon (also called "Promocode") that we provide to our clients.
    Coupon can give some discount on our services.
    """

    name = models.CharField(
        verbose_name="name of coupon",
        max_length=30,)
    amount_off = models.DecimalField(
        verbose_name="amount off",
        max_digits=9,
        decimal_places=2,
        default=0,
    )
    percentage_off = models.DecimalField(
        verbose_name="percentage off",
        max_digits=9,
        decimal_places=2,
        default=0,
    )
    end_date = models.DateTimeField(
        verbose_name="end date of coupon",
        default=localtime,
    )
    is_valid = models.BooleanField(
        verbose_name="is coupon valid for apply",
        default=True,
    )
    max_redemptions = models.IntegerField(
        verbose_name="maximum count of redemptions",
        default=1,
    )
    kind = models.CharField(
        verbose_name="coupon type",
        max_length=30,
        choices=[(item, item.value) for item in CouponType],
        null=True,
        default=CouponType.FIRST.value,
    )
